from UnnamedSlug.common import Job
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, rand
import mlflow
import mlflow.spark
from mlflow.tracking import MlflowClient
import json
from datetime import datetime


class RegressionJob(Job):
    """
    MLOps-ready Linear Regression job with model registration and serving
    """

    def __init__(self, spark=None, init_conf=None):
        super().__init__(spark, init_conf)
        self.model_name = "mlops-regression-model"
        self.experiment_name = "/Shared/mlops-regression-experiment"
        
    def launch(self):
        self.logger.info("Starting MLOps Regression Model Training")
        
        # Set MLflow experiment
        mlflow.set_experiment(self.experiment_name)
        
        # Start MLflow run with tags
        with mlflow.start_run() as run:
            # Log run metadata
            mlflow.set_tags({
                "model_type": "linear_regression",
                "data_source": "synthetic",
                "environment": "production",
                "training_date": datetime.now().isoformat()
            })
            
            # Generate sample dataset
            self.logger.info("Generating sample dataset...")
            df = self._create_sample_data()
            
            # Log dataset info
            mlflow.log_metric("dataset_size", df.count())
            
            # Split data
            train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
            mlflow.log_metric("train_size", train_df.count())
            mlflow.log_metric("test_size", test_df.count())
            
            # Prepare features
            assembler = VectorAssembler(
                inputCols=["feature1", "feature2", "feature3"],
                outputCol="features"
            )
            
            train_df = assembler.transform(train_df)
            test_df = assembler.transform(test_df)
            
            # Train model
            self.logger.info("Training Linear Regression model...")
            lr = LinearRegression(
                featuresCol="features",
                labelCol="target",
                predictionCol="prediction",
                regParam=0.1,  # Add regularization for better generalization
                elasticNetParam=0.1
            )
            
            # Log hyperparameters
            mlflow.log_params({
                "regParam": lr.getRegParam(),
                "elasticNetParam": lr.getElasticNetParam(),
                "maxIter": lr.getMaxIter()
            })
            
            model = lr.fit(train_df)
            
            # Make predictions
            predictions = model.transform(test_df)
            
            # Evaluate model
            rmse, r2, mae = self._evaluate_model(predictions)
            
            # Log metrics
            mlflow.log_metrics({
                "rmse": rmse,
                "r2": r2,
                "mae": mae
            })
            
            self.logger.info(f"Model RMSE: {rmse:.4f}")
            self.logger.info(f"Model R2: {r2:.4f}")
            self.logger.info(f"Model MAE: {mae:.4f}")
            
            # Save model with signature
            self.logger.info("Registering model with MLflow...")
            input_example = train_df.select("features").limit(1).collect()[0]["features"]
            
            # Log model to MLflow
            mlflow.spark.log_model(
                spark_model=model,
                artifact_path="model",
                registered_model_name=self.model_name,
                input_example=[input_example.toArray().tolist()],
                signature=mlflow.models.infer_signature(
                    model_input=train_df.select("features").limit(100).toPandas(),
                    model_output=predictions.select("prediction").limit(100).toPandas()
                )
            )
            
            # Save feature transformer
            mlflow.spark.log_model(
                spark_model=assembler,
                artifact_path="feature_transformer"
            )
            
            # Save predictions and model artifacts
            output_path = self.conf.get("output_path", "dbfs:/tmp/regression_model")
            self._save_outputs(predictions, output_path, run.info.run_id)
            
            # Promote model to production if it meets criteria
            self._promote_model_if_better(rmse, r2)
            
            self.logger.info("MLOps Regression job completed successfully!")
            
            return {
                "rmse": rmse, 
                "r2": r2, 
                "mae": mae,
                "model_path": output_path,
                "run_id": run.info.run_id,
                "model_name": self.model_name
            }

    def _evaluate_model(self, predictions):
        """Comprehensive model evaluation"""
        rmse_evaluator = RegressionEvaluator(
            labelCol="target",
            predictionCol="prediction",
            metricName="rmse"
        )
        
        r2_evaluator = RegressionEvaluator(
            labelCol="target",
            predictionCol="prediction",
            metricName="r2"
        )
        
        mae_evaluator = RegressionEvaluator(
            labelCol="target",
            predictionCol="prediction",
            metricName="mae"
        )
        
        rmse = rmse_evaluator.evaluate(predictions)
        r2 = r2_evaluator.evaluate(predictions)
        mae = mae_evaluator.evaluate(predictions)
        
        return rmse, r2, mae

    def _save_outputs(self, predictions, output_path, run_id):
        """Save model outputs and metadata"""
        # Save predictions
        predictions.select("features", "target", "prediction").write \
            .format(self.conf.get("output_format", "delta")) \
            .mode("overwrite") \
            .save(f"{output_path}/predictions")
        
        # Save model metadata (ensure all values are JSON serializable)
        metadata = {
            "run_id": str(run_id),  # Ensure it's a string
            "model_name": str(self.model_name),  # Ensure it's a string
            "training_timestamp": datetime.now().isoformat(),
            "model_type": "linear_regression",
            "features": ["feature1", "feature2", "feature3"]
        }
        
        # Convert to JSON string and validate it's serializable
        try:
            metadata_json = json.dumps(metadata)
            # Save metadata as JSON
            self.spark.sparkContext.parallelize([metadata_json]) \
                .saveAsTextFile(f"{output_path}/metadata")
        except (TypeError, ValueError) as e:
            self.logger.warning(f"Failed to serialize metadata: {e}")
            # Save a simplified version instead
            simple_metadata = {
                "run_id": "unknown" if run_id is None else str(run_id),
                "model_name": "mlops-regression-model", 
                "training_timestamp": datetime.now().isoformat(),
                "model_type": "linear_regression"
            }
            metadata_json = json.dumps(simple_metadata)
            self.spark.sparkContext.parallelize([metadata_json]) \
                .saveAsTextFile(f"{output_path}/metadata")

    def _promote_model_if_better(self, rmse, r2):
        """Promote model to production if it performs better"""
        client = MlflowClient()
        
        try:
            # Get current production model
            current_production_models = client.get_latest_versions(
                self.model_name, 
                stages=["Production"]
            )
            
            if not current_production_models:
                # No production model exists, promote this one
                self._promote_to_production(client)
            else:
                # Compare with current production model
                current_model = current_production_models[0]
                current_run = client.get_run(current_model.run_id)
                current_rmse = current_run.data.metrics.get("rmse", float('inf'))
                
                if rmse < current_rmse:
                    self.logger.info(f"New model (RMSE: {rmse:.4f}) is better than current production model (RMSE: {current_rmse:.4f})")
                    self._promote_to_production(client)
                else:
                    self.logger.info(f"Current production model (RMSE: {current_rmse:.4f}) is still better than new model (RMSE: {rmse:.4f})")
                    
        except Exception as e:
            self.logger.warning(f"Error in model promotion: {e}")

    def _promote_to_production(self, client):
        """Promote latest model version to production"""
        try:
            latest_version = client.get_latest_versions(self.model_name, stages=["None"])[0]
            
            # Transition to production
            client.transition_model_version_stage(
                name=self.model_name,
                version=latest_version.version,
                stage="Production",
                archive_existing_versions=True
            )
            
            self.logger.info(f"Model version {latest_version.version} promoted to Production")
            
        except Exception as e:
            self.logger.error(f"Failed to promote model to production: {e}")

    def _create_sample_data(self):
        """Create sample data for regression"""
        self.logger.info("Creating sample regression dataset...")
        
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


# Entry point for automated retraining
def retrain_on_new_data(new_data_path, config_path):
    """
    Function to retrain model when new data arrives
    """
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.appName("AutoRetraining").getOrCreate()
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create job instance
    job = RegressionJob(spark=spark, init_conf=config)
    
    # If new data path is provided, load and use it
    if new_data_path:
        # Load new data (implement based on your data format)
        new_df = spark.read.format("delta").load(new_data_path)
        # Add logic to incorporate new data into training
        
    # Train model
    result = job.launch()
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run regression model training')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--new-data', help='New data path for retraining')
    
    args = parser.parse_args()
    
    if args.new_data:
        # Retraining mode
        result = retrain_on_new_data(args.new_data, args.config)
    else:
        # Regular training mode
        job = RegressionJob()
        result = job.launch()
    
    print(f"Job completed with results: {result}") 