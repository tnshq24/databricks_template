# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Regression Model CI/CD Pipeline Test
# MAGIC 
# MAGIC This notebook tests our regression model in the Databricks environment

# COMMAND ----------

# Install MLflow if not available
%pip install mlflow

# COMMAND ----------

# Define the regression job code directly in the notebook for testing
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, rand
import mlflow
import mlflow.spark

class RegressionJob:
    def __init__(self):
        self.spark = spark  # Use the existing Databricks Spark session
        self.logger = None  # We'll use print instead
        self.conf = {
            "output_format": "delta",
            "output_path": "dbfs:/tmp/regression_test_output"
        }
    
    def launch(self):
        print("Starting Regression Model Training")
        
        # Start MLflow run
        with mlflow.start_run():
            # Generate sample dataset
            print("Generating sample dataset...")
            df = self._create_sample_data()
            
            # Split data
            train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
            
            # Prepare features
            assembler = VectorAssembler(
                inputCols=["feature1", "feature2", "feature3"],
                outputCol="features"
            )
            
            train_df = assembler.transform(train_df)
            test_df = assembler.transform(test_df)
            
            # Train model
            print("Training Linear Regression model...")
            lr = LinearRegression(
                featuresCol="features",
                labelCol="target",
                predictionCol="prediction"
            )
            
            model = lr.fit(train_df)
            
            # Make predictions
            predictions = model.transform(test_df)
            
            # Evaluate model
            evaluator = RegressionEvaluator(
                labelCol="target",
                predictionCol="prediction",
                metricName="rmse"
            )
            
            rmse = evaluator.evaluate(predictions)
            r2_evaluator = RegressionEvaluator(
                labelCol="target",
                predictionCol="prediction",
                metricName="r2"
            )
            r2 = r2_evaluator.evaluate(predictions)
            
            # Log metrics
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            
            print(f"Model RMSE: {rmse:.4f}")
            print(f"Model R2: {r2:.4f}")
            
            # Save model and predictions
            output_path = self.conf.get("output_path")
            
            print(f"Saving model to {output_path}")
            mlflow.spark.log_model(model, "linear_regression_model")
            
            # Save predictions
            predictions.select("features", "target", "prediction").write \
                .format(self.conf.get("output_format", "delta")) \
                .mode("overwrite") \
                .save(f"{output_path}/predictions")
            
            print("Regression job completed successfully!")
            
            return {"rmse": rmse, "r2": r2, "model_path": output_path}

    def _create_sample_data(self):
        """Create sample data for regression"""
        print("Creating sample regression dataset...")
        
        # Create sample data with 3 features and a target variable
        df = self.spark.range(0, 10000).toDF("id")
        
        # Add random features
        df = df.withColumn("feature1", rand(seed=42) * 100) \
              .withColumn("feature2", rand(seed=123) * 50) \
              .withColumn("feature3", rand(seed=456) * 25)
        
        # Create a target variable with some relationship to features + noise
        df = df.withColumn("target", 
                          col("feature1") * 0.5 + 
                          col("feature2") * 0.3 + 
                          col("feature3") * 0.2 + 
                          (rand(seed=789) * 10))  # Add some noise
        
        return df

# COMMAND ----------

# Test the regression model
print("🧪 Testing Regression Model...")
job = RegressionJob()
result = job.launch()

print(f"\n🎉 SUCCESS! Results: {result}")

# COMMAND ----------

# Verify the output data
print("📊 Checking saved predictions...")
predictions_df = spark.read.format("delta").load("dbfs:/tmp/regression_test_output/predictions")
print(f"Number of predictions saved: {predictions_df.count()}")
predictions_df.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ CI/CD Pipeline Test Complete!
# MAGIC 
# MAGIC Your regression model:
# MAGIC - ✅ Generated synthetic data successfully
# MAGIC - ✅ Trained a Linear Regression model  
# MAGIC - ✅ Evaluated with RMSE and R² metrics
# MAGIC - ✅ Logged experiments to MLflow
# MAGIC - ✅ Saved predictions to Delta format
# MAGIC 
# MAGIC This confirms your CI/CD pipeline is working! 🎯 