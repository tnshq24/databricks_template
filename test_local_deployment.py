#!/usr/bin/env python3
"""
Local Databricks Connectivity and Deployment Test
Run this script while connected to your company VPN to test the MLOps pipeline
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path

# Configuration
DATABRICKS_HOST = "https://adb-1244961191947049.9.azuredatabricks.net"
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")

def test_connection():
    """Test basic Databricks API connectivity"""
    print("🔐 Testing Databricks connection...")
    
    if not DATABRICKS_TOKEN:
        print("❌ DATABRICKS_TOKEN environment variable not set!")
        print("💡 Run: export DATABRICKS_TOKEN='your_token_here'")
        return False
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test clusters API
        response = requests.get(f"{DATABRICKS_HOST}/api/2.0/clusters/list", headers=headers)
        if response.status_code == 200:
            print("✅ Databricks API connection successful!")
            clusters = response.json().get("clusters", [])
            print(f"📊 Found {len(clusters)} clusters in workspace")
            return True
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_workspace_access():
    """Test workspace API access"""
    print("\n📁 Testing workspace access...")
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{DATABRICKS_HOST}/api/2.0/workspace/list?path=/Shared", headers=headers)
        if response.status_code == 200:
            print("✅ Workspace access successful!")
            return True
        else:
            print(f"❌ Workspace access failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Workspace access error: {e}")
        return False

def install_databricks_cli():
    """Install Databricks CLI if not present"""
    print("\n🔧 Checking Databricks CLI...")
    
    try:
        result = subprocess.run(["databricks", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Databricks CLI already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("📥 Installing Databricks CLI...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "databricks-cli"], check=True)
        print("✅ Databricks CLI installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Databricks CLI: {e}")
        return False

def configure_databricks_cli():
    """Configure Databricks CLI"""
    print("\n⚙️ Configuring Databricks CLI...")
    
    config_content = f"""[DEFAULT]
host = {DATABRICKS_HOST}
token = {DATABRICKS_TOKEN}
"""
    
    # Write config file
    config_path = Path.home() / ".databrickscfg"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print("✅ Databricks CLI configured!")
    
    # Test CLI connection
    try:
        result = subprocess.run(["databricks", "workspace", "list", "/Shared"], 
                              capture_output=True, text=True, check=True)
        print("✅ CLI connection test successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI connection test failed: {e}")
        return False

def deploy_code():
    """Deploy UnnamedSlug package to Databricks workspace"""
    print("\n🚀 Deploying code to Databricks workspace...")
    
    try:
        # Create workspace directories
        subprocess.run(["databricks", "workspace", "mkdirs", "/Workspace/Shared/UnnamedSlug"], check=True)
        print("✅ Created workspace directory")
        
        # Upload Python files
        unnamed_slug_path = Path("UnnamedSlug")
        if not unnamed_slug_path.exists():
            print("❌ UnnamedSlug directory not found!")
            return False
        
        uploaded_files = 0
        for py_file in unnamed_slug_path.rglob("*.py"):
            target_path = f"/Workspace/Shared/{py_file}"
            try:
                subprocess.run([
                    "databricks", "workspace", "import", 
                    str(py_file), target_path,
                    "--language", "PYTHON", "--overwrite"
                ], check=True)
                uploaded_files += 1
                print(f"📤 Uploaded: {py_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to upload {py_file}: {e}")
        
        print(f"✅ Uploaded {uploaded_files} Python files")
        
        # Upload config file
        config_file = Path("conf/test/regression.json")
        if config_file.exists():
            subprocess.run(["databricks", "workspace", "mkdirs", "/Workspace/Shared/conf"], check=True)
            subprocess.run([
                "databricks", "workspace", "import",
                str(config_file), "/Workspace/Shared/conf/regression.json",
                "--overwrite"
            ], check=True)
            print("✅ Uploaded configuration file")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def create_test_notebook():
    """Create a test notebook in Databricks"""
    print("\n📓 Creating test notebook...")
    
    notebook_content = """# MLOps Pipeline Test Notebook

## Import the UnnamedSlug package
%run /Workspace/Shared/UnnamedSlug/jobs/regression/entrypoint

## Create and run the regression job
job = RegressionJob()
print("🚀 Starting MLOps regression training...")

# Run the job
try:
    result = job.launch()
    print("✅ MLOps pipeline completed successfully!")
    print(f"📊 Result: {result}")
except Exception as e:
    print(f"❌ Pipeline failed: {e}")
    raise
"""
    
    # Create temp notebook file
    notebook_path = Path("test_mlops_notebook.py")
    with open(notebook_path, "w") as f:
        f.write(notebook_content)
    
    try:
        subprocess.run([
            "databricks", "workspace", "import",
            str(notebook_path), "/Workspace/Shared/test_mlops_pipeline",
            "--language", "PYTHON", "--overwrite"
        ], check=True)
        print("✅ Test notebook created: /Workspace/Shared/test_mlops_pipeline")
        
        # Clean up temp file
        notebook_path.unlink()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create notebook: {e}")
        notebook_path.unlink(missing_ok=True)
        return False

def main():
    """Main test function"""
    print("🧪 Local Databricks MLOps Pipeline Test")
    print("=" * 60)
    print(f"🌐 Workspace: {DATABRICKS_HOST}")
    print("=" * 60)
    
    # Check VPN connection first
    print("🔍 Testing if you're connected to the private network...")
    if not test_connection():
        print("\n❌ Cannot connect to Databricks workspace!")
        print("💡 Please ensure:")
        print("   1. You're connected to your company VPN")
        print("   2. DATABRICKS_TOKEN environment variable is set")
        print("   3. Token has the necessary permissions")
        return False
    
    # Run all tests
    tests = [
        ("Workspace Access", test_workspace_access),
        ("Install Databricks CLI", install_databricks_cli),
        ("Configure Databricks CLI", configure_databricks_cli),
        ("Deploy Code", deploy_code),
        ("Create Test Notebook", create_test_notebook),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS! Local MLOps deployment completed!")
        print("\n📋 Next Steps:")
        print("1. ✅ Code deployed to Databricks workspace")
        print("2. 🔗 Go to your workspace: https://adb-1244961191947049.9.azuredatabricks.net")
        print("3. 📓 Open: /Workspace/Shared/test_mlops_pipeline")
        print("4. ▶️ Run the notebook to test your MLOps pipeline")
        print("5. 📊 Check MLflow experiments for results")
        print("\n🚀 Your MLOps pipeline is ready for production!")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 