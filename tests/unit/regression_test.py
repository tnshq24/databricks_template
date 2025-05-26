import unittest
import tempfile
import os
import shutil

from UnnamedSlug.jobs.regression.entrypoint import RegressionJob
from pyspark.sql import SparkSession
from unittest.mock import MagicMock


class RegressionJobUnitTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory().name
        self.spark = SparkSession.builder.master("local[1]").getOrCreate()
        self.test_config = {
            "output_format": "parquet",
            "output_path": os.path.join(self.test_dir, "regression_output"),
        }
        self.job = RegressionJob(spark=self.spark, init_conf=self.test_config)

    def test_create_sample_data(self):
        """Test sample data creation"""
        # Mock dbutils if needed
        self.job.dbutils = MagicMock()
        
        # Test data creation
        df = self.job._create_sample_data()
        
        # Verify data structure
        self.assertIsNotNone(df)
        expected_columns = ["id", "feature1", "feature2", "feature3", "target"]
        self.assertEqual(df.columns, expected_columns)
        
        # Verify data count
        self.assertEqual(df.count(), 10000)

    def test_regression_model_training(self):
        """Test the full regression pipeline"""
        # Mock dbutils and MLflow
        self.job.dbutils = MagicMock()
        
        # Mock MLflow to avoid actual logging in tests
        import mlflow
        with unittest.mock.patch.object(mlflow, 'start_run'), \
             unittest.mock.patch.object(mlflow, 'log_metric'), \
             unittest.mock.patch.object(mlflow.spark, 'log_model'):
            
            result = self.job.launch()
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("rmse", result)
            self.assertIn("r2", result)
            self.assertIn("model_path", result)
            
            # Verify metrics are reasonable
            self.assertGreater(result["rmse"], 0)
            self.assertLessEqual(result["r2"], 1.0)

    def test_model_output_exists(self):
        """Test that model output files are created"""
        # Mock dbutils and MLflow
        self.job.dbutils = MagicMock()
        
        # Mock MLflow to avoid actual logging in tests
        import mlflow
        with unittest.mock.patch.object(mlflow, 'start_run'), \
             unittest.mock.patch.object(mlflow, 'log_metric'), \
             unittest.mock.patch.object(mlflow.spark, 'log_model'):
            
            result = self.job.launch()
            
            # Check that predictions were saved
            predictions_path = f"{self.test_config['output_path']}/predictions"
            
            # Verify the predictions directory exists and has data
            prediction_files = [f for f in os.listdir(predictions_path) 
                              if f.endswith('.parquet')]
            self.assertGreater(len(prediction_files), 0)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    unittest.main() 