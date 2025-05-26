from UnnamedSlug.common import Job
from pyspark.sql.functions import col, count, when, isnan, isnull, mean, stddev
from pyspark.sql import functions as F
import mlflow
from mlflow.tracking import MlflowClient
import json
from datetime import datetime, timedelta
import logging


class DataMonitorJob(Job):
    """
    Data monitoring and auto-retraining job
    Monitors data drift and triggers retraining when needed
    """
    
    def __init__(self, spark=None, init_conf=None):
        super().__init__(spark, init_conf)
        self.model_name = "mlops-regression-model"
        self.drift_threshold = 0.1  # 10% drift threshold
        self.performance_threshold = 0.05  # 5% performance degradation threshold
        
    def launch(self):
        self.logger.info("Starting Data Monitoring and Auto-Retraining Job")
        
        try:
            # Check for new data
            new_data_available = self._check_for_new_data()
            
            if new_data_available:
                self.logger.info("New data detected. Checking for drift...")
                
                # Check data drift
                drift_detected = self._detect_data_drift()
                
                # Check model performance
                performance_degraded = self._check_model_performance()
                
                # Determine if retraining is needed
                should_retrain = (
                    drift_detected or 
                    performance_degraded or 
                    self._scheduled_retrain_due()
                )
                
                if should_retrain:
                    self.logger.info("Triggering automatic model retraining...")
                    self._trigger_retraining()
                else:
                    self.logger.info("No retraining needed at this time.")
            else:
                self.logger.info("No new data available. Monitoring completed.")
                
        except Exception as e:
            self.logger.error(f"Error in data monitoring job: {e}")
            raise
            
        return {"status": "completed", "timestamp": datetime.now().isoformat()}
    
    def _check_for_new_data(self):
        """Check if new data is available since last training"""
        try:
            # Get the path for new data (configure in your setup)
            new_data_path = self.conf.get("new_data_path", "dbfs:/mnt/data/incoming/")
            
            # Check if new data exists
            try:
                new_data_df = self.spark.read.format("delta").load(new_data_path)
                
                # Get the latest training timestamp
                last_training_time = self._get_last_training_timestamp()
                
                # Filter for data newer than last training
                if last_training_time:
                    new_records = new_data_df.filter(
                        col("timestamp") > last_training_time
                    ).count()
                else:
                    new_records = new_data_df.count()
                
                self.logger.info(f"Found {new_records} new records")
                return new_records > 0
                
            except Exception as e:
                self.logger.warning(f"No new data found or error reading: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking for new data: {e}")
            return False
    
    def _detect_data_drift(self):
        """Detect data drift by comparing distributions"""
        try:
            # Load reference data (from last training)
            reference_data_path = self.conf.get(
                "reference_data_path", 
                "dbfs:/tmp/regression_model/reference_data"
            )
            
            # Load new data
            new_data_path = self.conf.get("new_data_path", "dbfs:/mnt/data/incoming/")
            
            reference_df = self.spark.read.format("delta").load(reference_data_path)
            new_df = self.spark.read.format("delta").load(new_data_path)
            
            # Compare statistical properties
            drift_score = self._calculate_drift_score(reference_df, new_df)
            
            # Log drift metrics
            mlflow.log_metric("data_drift_score", drift_score)
            
            drift_detected = drift_score > self.drift_threshold
            
            if drift_detected:
                self.logger.warning(f"Data drift detected! Score: {drift_score:.4f}")
            else:
                self.logger.info(f"No significant data drift. Score: {drift_score:.4f}")
                
            return drift_detected
            
        except Exception as e:
            self.logger.error(f"Error in drift detection: {e}")
            return False
    
    def _calculate_drift_score(self, reference_df, new_df):
        """Calculate drift score based on statistical differences"""
        try:
            feature_columns = ["feature1", "feature2", "feature3"]
            drift_scores = []
            
            for feature in feature_columns:
                # Calculate statistics for reference data
                ref_stats = reference_df.select(
                    mean(col(feature)).alias("mean"),
                    stddev(col(feature)).alias("stddev")
                ).collect()[0]
                
                # Calculate statistics for new data
                new_stats = new_df.select(
                    mean(col(feature)).alias("mean"),
                    stddev(col(feature)).alias("stddev")
                ).collect()[0]
                
                # Calculate drift score (normalized difference)
                if ref_stats["stddev"] and ref_stats["stddev"] > 0:
                    mean_drift = abs(new_stats["mean"] - ref_stats["mean"]) / ref_stats["stddev"]
                    std_drift = abs(new_stats["stddev"] - ref_stats["stddev"]) / ref_stats["stddev"]
                    
                    feature_drift = (mean_drift + std_drift) / 2
                    drift_scores.append(feature_drift)
            
            # Return average drift score
            return sum(drift_scores) / len(drift_scores) if drift_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating drift score: {e}")
            return 0.0
    
    def _check_model_performance(self):
        """Check if current model performance has degraded"""
        try:
            # Get current production model
            client = MlflowClient()
            production_models = client.get_latest_versions(
                self.model_name, 
                stages=["Production"]
            )
            
            if not production_models:
                self.logger.warning("No production model found")
                return True  # Trigger retraining if no production model
            
            # Get model metrics
            current_model = production_models[0]
            current_run = client.get_run(current_model.run_id)
            baseline_rmse = current_run.data.metrics.get("rmse", 0)
            
            # Evaluate current model on recent data (if available)
            recent_performance = self._evaluate_on_recent_data(current_model)
            
            if recent_performance:
                performance_degradation = (recent_performance - baseline_rmse) / baseline_rmse
                
                mlflow.log_metric("performance_degradation", performance_degradation)
                
                if performance_degradation > self.performance_threshold:
                    self.logger.warning(f"Performance degradation detected: {performance_degradation:.4f}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking model performance: {e}")
            return False
    
    def _evaluate_on_recent_data(self, model_version):
        """Evaluate model on recent data"""
        try:
            # This would implement evaluation logic on recent data
            # For now, return None (would need actual evaluation data)
            self.logger.info("Performance evaluation on recent data not implemented yet")
            return None
            
        except Exception as e:
            self.logger.error(f"Error evaluating recent performance: {e}")
            return None
    
    def _scheduled_retrain_due(self):
        """Check if scheduled retraining is due"""
        try:
            # Get last training timestamp
            last_training_time = self._get_last_training_timestamp()
            
            if not last_training_time:
                return True  # No previous training found
            
            # Check if it's been more than the configured interval
            retrain_interval_days = self.conf.get("retrain_interval_days", 7)  # Weekly by default
            
            days_since_training = (datetime.now() - last_training_time).days
            
            self.logger.info(f"Days since last training: {days_since_training}")
            
            return days_since_training >= retrain_interval_days
            
        except Exception as e:
            self.logger.error(f"Error checking scheduled retrain: {e}")
            return False
    
    def _get_last_training_timestamp(self):
        """Get timestamp of last training run"""
        try:
            client = MlflowClient()
            
            # Get the latest production model
            production_models = client.get_latest_versions(
                self.model_name, 
                stages=["Production"]
            )
            
            if production_models:
                model = production_models[0]
                run = client.get_run(model.run_id)
                
                # Get training timestamp from run tags
                training_date_str = run.data.tags.get("training_date")
                if training_date_str:
                    return datetime.fromisoformat(training_date_str.replace('Z', '+00:00'))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last training timestamp: {e}")
            return None
    
    def _trigger_retraining(self):
        """Trigger automatic model retraining"""
        try:
            self.logger.info("Triggering automatic model retraining...")
            
            # Import and run the regression job
            from UnnamedSlug.jobs.regression.entrypoint import RegressionJob
            
            # Create retraining job with updated configuration
            retrain_config = self.conf.copy()
            retrain_config.update({
                "output_path": f"dbfs:/tmp/regression_model/retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "triggered_by": "auto_retrain",
                "trigger_reason": "data_drift_or_performance_degradation"
            })
            
            # Run retraining
            retrain_job = RegressionJob(spark=self.spark, init_conf=retrain_config)
            result = retrain_job.launch()
            
            self.logger.info(f"Retraining completed with result: {result}")
            
            # Log retraining event
            mlflow.log_event(
                event="model_retrained",
                data={
                    "trigger": "automatic",
                    "timestamp": datetime.now().isoformat(),
                    "new_model_rmse": result.get("rmse"),
                    "new_model_r2": result.get("r2")
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in automatic retraining: {e}")
            raise


if __name__ == "__main__":
    job = DataMonitorJob()
    result = job.launch()
    print(f"Data monitoring job completed: {result}") 