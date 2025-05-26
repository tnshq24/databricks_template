#!/usr/bin/env python3
"""
Script to set up and manage model serving endpoint for real-time predictions
"""

import requests
import json
import time
import logging
from typing import Dict, Any
import os


class ModelServingManager:
    """Manages Databricks model serving endpoints"""
    
    def __init__(self, databricks_host: str, token: str):
        self.base_url = databricks_host.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
        
    def create_serving_endpoint(self, endpoint_name: str, model_name: str) -> Dict[str, Any]:
        """Create a new model serving endpoint"""
        
        endpoint_config = {
            "name": endpoint_name,
            "config": {
                "served_models": [
                    {
                        "name": f"{model_name}-latest",
                        "model_name": model_name,
                        "model_version": "latest",
                        "workload_size": "Small",
                        "scale_to_zero_enabled": True,
                        "environment_vars": {
                            "ENABLE_MLFLOW_TRACING": "true"
                        }
                    }
                ],
                "auto_capture_config": {
                    "catalog_name": "main",
                    "schema_name": "model_inference_logs", 
                    "table_name_prefix": model_name.replace("-", "_")
                },
                "traffic_config": {
                    "routes": [
                        {
                            "served_model_name": f"{model_name}-latest",
                            "traffic_percentage": 100
                        }
                    ]
                }
            }
        }
        
        # Check if endpoint already exists
        response = self.get_endpoint(endpoint_name)
        
        if response.status_code == 404:
            # Create new endpoint
            self.logger.info(f"Creating new serving endpoint: {endpoint_name}")
            response = requests.post(
                f"{self.base_url}/api/2.0/serving-endpoints",
                headers=self.headers,
                json=endpoint_config
            )
        else:
            # Update existing endpoint
            self.logger.info(f"Updating existing serving endpoint: {endpoint_name}")
            response = requests.put(
                f"{self.base_url}/api/2.0/serving-endpoints/{endpoint_name}/config",
                headers=self.headers,
                json=endpoint_config["config"]
            )
        
        if response.status_code in [200, 201]:
            self.logger.info(f"Endpoint {endpoint_name} configured successfully")
            return response.json()
        else:
            self.logger.error(f"Failed to configure endpoint: {response.text}")
            response.raise_for_status()
    
    def get_endpoint(self, endpoint_name: str) -> requests.Response:
        """Get endpoint details"""
        return requests.get(
            f"{self.base_url}/api/2.0/serving-endpoints/{endpoint_name}",
            headers=self.headers
        )
    
    def wait_for_endpoint_ready(self, endpoint_name: str, timeout: int = 1800) -> bool:
        """Wait for endpoint to be ready"""
        self.logger.info(f"Waiting for endpoint {endpoint_name} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.get_endpoint(endpoint_name)
            
            if response.status_code == 200:
                endpoint_data = response.json()
                state = endpoint_data.get("state", {}).get("ready", "NOT_READY")
                
                self.logger.info(f"Endpoint state: {state}")
                
                if state == "READY":
                    self.logger.info(f"Endpoint {endpoint_name} is ready!")
                    return True
                elif state == "CONFIG_UPDATE_IN_PROGRESS":
                    self.logger.info("Config update in progress...")
                elif "FAILED" in state:
                    self.logger.error(f"Endpoint failed to start: {state}")
                    return False
            
            time.sleep(30)  # Wait 30 seconds before checking again
        
        self.logger.error(f"Timeout waiting for endpoint {endpoint_name} to be ready")
        return False
    
    def update_endpoint_model(self, endpoint_name: str, model_name: str, model_version: str = "latest") -> bool:
        """Update endpoint to use a new model version"""
        try:
            # Get current endpoint config
            response = self.get_endpoint(endpoint_name)
            if response.status_code != 200:
                self.logger.error(f"Failed to get endpoint {endpoint_name}")
                return False
            
            current_config = response.json()["config"]
            
            # Update the model version
            for served_model in current_config["served_models"]:
                if served_model["model_name"] == model_name:
                    served_model["model_version"] = model_version
                    self.logger.info(f"Updating {model_name} to version {model_version}")
            
            # Update endpoint
            response = requests.put(
                f"{self.base_url}/api/2.0/serving-endpoints/{endpoint_name}/config",
                headers=self.headers,
                json=current_config
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully updated endpoint {endpoint_name}")
                return True
            else:
                self.logger.error(f"Failed to update endpoint: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating endpoint: {e}")
            return False
    
    def test_endpoint(self, endpoint_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the serving endpoint with sample data"""
        try:
            response = requests.post(
                f"{self.base_url}/serving-endpoints/{endpoint_name}/invocations",
                headers=self.headers,
                json=test_data
            )
            
            if response.status_code == 200:
                self.logger.info("Endpoint test successful")
                return response.json()
            else:
                self.logger.error(f"Endpoint test failed: {response.text}")
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Error testing endpoint: {e}")
            raise
    
    def get_endpoint_metrics(self, endpoint_name: str) -> Dict[str, Any]:
        """Get endpoint performance metrics"""
        try:
            response = requests.get(
                f"{self.base_url}/api/2.0/serving-endpoints/{endpoint_name}/metrics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Could not get metrics: {response.text}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {}


def setup_model_serving(databricks_host: str, token: str, model_name: str, endpoint_name: str):
    """Main function to set up model serving"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize serving manager
        serving_manager = ModelServingManager(databricks_host, token)
        
        # Create/update serving endpoint
        logger.info("Setting up model serving endpoint...")
        endpoint_result = serving_manager.create_serving_endpoint(endpoint_name, model_name)
        
        # Wait for endpoint to be ready
        if serving_manager.wait_for_endpoint_ready(endpoint_name):
            logger.info("Endpoint is ready for serving!")
            
            # Test the endpoint
            test_data = {
                "dataframe_records": [
                    {
                        "feature1": 50.0,
                        "feature2": 25.0,
                        "feature3": 12.5
                    }
                ]
            }
            
            logger.info("Testing endpoint with sample data...")
            test_result = serving_manager.test_endpoint(endpoint_name, test_data)
            logger.info(f"Test result: {test_result}")
            
            # Get endpoint URL for client applications
            endpoint_url = f"{databricks_host}/serving-endpoints/{endpoint_name}/invocations"
            logger.info(f"🎉 Model serving endpoint ready at: {endpoint_url}")
            
            return {
                "status": "success",
                "endpoint_name": endpoint_name,
                "endpoint_url": endpoint_url,
                "test_result": test_result
            }
        else:
            logger.error("Failed to get endpoint ready")
            return {"status": "failed", "reason": "endpoint_not_ready"}
            
    except Exception as e:
        logger.error(f"Error setting up model serving: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup model serving endpoint')
    parser.add_argument('--host', required=True, help='Databricks workspace URL')
    parser.add_argument('--token', required=True, help='Databricks access token')
    parser.add_argument('--model-name', default='mlops-regression-model', help='Model name')
    parser.add_argument('--endpoint-name', default='regression-model-endpoint', help='Endpoint name')
    
    args = parser.parse_args()
    
    result = setup_model_serving(
        databricks_host=args.host,
        token=args.token,
        model_name=args.model_name,
        endpoint_name=args.endpoint_name
    )
    
    print(f"Setup result: {json.dumps(result, indent=2)}") 