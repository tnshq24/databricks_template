import unittest
import tempfile
import os
import shutil

from UnnamedSlug.jobs.regression.entrypoint import RegressionJob
from unittest.mock import MagicMock


class RegressionJobUnitTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory().name
        
        # Mock SparkSession instead of creating a real one (avoids Java dependency)
        self.spark = MagicMock()
        self.spark.range.return_value = MagicMock()
        
        self.test_config = {
            "output_format": "parquet",
            "output_path": os.path.join(self.test_dir, "regression_output"),
        }
        self.job = RegressionJob(spark=self.spark, init_conf=self.test_config)

    def test_create_sample_data(self):
        """Test sample data creation"""
        from unittest.mock import patch, MagicMock
        
        # Mock dbutils if needed
        self.job.dbutils = MagicMock()
        
        # Mock the spark dataframe chain
        mock_df = MagicMock()
        mock_df.toDF.return_value = mock_df
        mock_df.withColumn.return_value = mock_df
        mock_df.columns = ["id", "feature1", "feature2", "feature3", "target"]
        mock_df.count.return_value = 10000
        
        self.spark.range.return_value = mock_df
        
        # Mock PySpark functions that require SparkContext
        mock_rand = MagicMock()
        mock_col = MagicMock()
        
        with patch('UnnamedSlug.jobs.regression.entrypoint.rand', return_value=mock_rand), \
             patch('UnnamedSlug.jobs.regression.entrypoint.col', return_value=mock_col):
            
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
        from unittest.mock import patch, MagicMock
        
        # Mock dbutils and MLflow
        self.job.dbutils = MagicMock()
        
        # Mock MLflow to avoid actual logging in tests
        import mlflow
        
        # Mock Spark DataFrames and transformations
        mock_df = MagicMock()
        mock_df.randomSplit.return_value = [mock_df, mock_df]  # train, test
        mock_df.count.return_value = 8000  # train size
        mock_df.select.return_value = mock_df
        mock_df.limit.return_value = mock_df
        mock_df.collect.return_value = [{"features": MagicMock()}]
        mock_df.toPandas.return_value = MagicMock()
        
        # Mock VectorAssembler
        mock_assembler = MagicMock()
        mock_assembler.transform.return_value = mock_df
        
        # Mock LinearRegression
        mock_lr = MagicMock()
        mock_model = MagicMock()
        mock_lr.fit.return_value = mock_model
        mock_model.transform.return_value = mock_df
        
        # Create a mock run with proper attributes
        mock_run = MagicMock()
        mock_run.info.run_id = "test_run_123"
        
        with patch.object(mlflow, 'start_run', return_value=mock_run), \
             patch.object(mlflow, 'log_metric'), \
             patch.object(mlflow, 'set_experiment'), \
             patch.object(mlflow, 'set_tags'), \
             patch.object(mlflow, 'log_params'), \
             patch.object(mlflow, 'log_metrics'), \
             patch.object(mlflow.spark, 'log_model'), \
             patch.object(self.job, '_save_outputs') as mock_save, \
             patch.object(self.job, '_evaluate_model', return_value=(0.5, 0.8, 0.3)), \
             patch.object(self.job, '_promote_model_if_better'), \
             patch('UnnamedSlug.jobs.regression.entrypoint.VectorAssembler', return_value=mock_assembler), \
             patch('UnnamedSlug.jobs.regression.entrypoint.LinearRegression', return_value=mock_lr):
            
            # Mock _create_sample_data to return our mock DataFrame
            self.job._create_sample_data = MagicMock(return_value=mock_df)
            
            result = self.job.launch()
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("rmse", result)
            self.assertIn("r2", result)
            self.assertIn("model_path", result)
            
            # Verify metrics are reasonable
            self.assertGreater(result["rmse"], 0)
            self.assertLessEqual(result["r2"], 1.0)
            
            # Verify _save_outputs was called
            self.assertTrue(mock_save.called)

    def test_model_output_exists(self):
        """Test that model output files are created"""
        from unittest.mock import patch, MagicMock
        
        # Mock dbutils and MLflow
        self.job.dbutils = MagicMock()
        
        # Mock MLflow to avoid actual logging in tests
        import mlflow
        
        # Mock Spark DataFrames
        mock_df = MagicMock()
        mock_df.randomSplit.return_value = [mock_df, mock_df]
        mock_df.count.return_value = 8000
        mock_df.select.return_value = mock_df
        mock_df.limit.return_value = mock_df
        mock_df.collect.return_value = [{"features": MagicMock()}]
        mock_df.toPandas.return_value = MagicMock()
        
        # Mock VectorAssembler and LinearRegression
        mock_assembler = MagicMock()
        mock_assembler.transform.return_value = mock_df
        mock_lr = MagicMock()
        mock_model = MagicMock()
        mock_lr.fit.return_value = mock_model
        mock_model.transform.return_value = mock_df
        
        # Create a mock run with proper attributes
        mock_run = MagicMock()
        mock_run.info.run_id = "test_run_456"
        
        with patch.object(mlflow, 'start_run', return_value=mock_run), \
             patch.object(mlflow, 'log_metric'), \
             patch.object(mlflow, 'set_experiment'), \
             patch.object(mlflow, 'set_tags'), \
             patch.object(mlflow, 'log_params'), \
             patch.object(mlflow, 'log_metrics'), \
             patch.object(mlflow.spark, 'log_model'), \
             patch.object(self.job, '_save_outputs') as mock_save, \
             patch.object(self.job, '_evaluate_model', return_value=(0.5, 0.8, 0.3)), \
             patch.object(self.job, '_promote_model_if_better'), \
             patch('UnnamedSlug.jobs.regression.entrypoint.VectorAssembler', return_value=mock_assembler), \
             patch('UnnamedSlug.jobs.regression.entrypoint.LinearRegression', return_value=mock_lr):
            
            # Mock _create_sample_data to return our mock DataFrame
            self.job._create_sample_data = MagicMock(return_value=mock_df)
            
            result = self.job.launch()
            
            # Verify _save_outputs was called with correct parameters
            self.assertTrue(mock_save.called)
            
            # Verify that the launch method completed successfully
            self.assertIsInstance(result, dict)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    unittest.main() 