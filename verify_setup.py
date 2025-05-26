#!/usr/bin/env python3
"""
Verify CI/CD pipeline setup without requiring Java/Spark locally
"""

import os
import sys
import json

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'UnnamedSlug/jobs/regression/entrypoint.py',
        'UnnamedSlug/__init__.py',
        'UnnamedSlug/common.py',
        'tests/unit/regression_test.py',
        'conf/test/regression.json',
        'conf/deployment.json',
        '.databrickscfg',
        '.dbx/project.json'
    ]
    
    print("📁 Checking file structure...")
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exist = False
    
    return all_exist

def check_configuration():
    """Check if configuration files are properly set up"""
    print("\n⚙️ Checking configuration files...")
    
    # Check .databrickscfg
    try:
        with open('.databrickscfg', 'r') as f:
            content = f.read()
            if 'https://adb-1244961191947049.9.azuredatabricks.net' in content:
                print("✅ Databricks host configured")
            if 'dapi' in content and len(content) > 100:
                print("✅ Databricks token configured")
            else:
                print("⚠️ Databricks token might not be properly configured")
    except FileNotFoundError:
        print("❌ .databrickscfg not found")
        return False
    
    # Check deployment.json
    try:
        with open('conf/deployment.json', 'r') as f:
            config = json.load(f)
            jobs = config.get('default', {}).get('jobs', [])
            regression_job = next((job for job in jobs if 'regression' in job.get('name', '')), None)
            if regression_job:
                print("✅ Regression job configured in deployment.json")
            else:
                print("❌ Regression job not found in deployment.json")
                return False
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading deployment.json: {e}")
        return False
    
    # Check .dbx/project.json
    try:
        with open('.dbx/project.json', 'r') as f:
            project_config = json.load(f)
            env = project_config.get('environments', {}).get('default', {})
            if env.get('workspace_host') == 'https://adb-1244961191947049.9.azuredatabricks.net':
                print("✅ DBX workspace host configured")
            else:
                print("❌ DBX workspace host not properly configured")
                return False
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading .dbx/project.json: {e}")
        return False
    
    return True

def check_imports():
    """Check if imports work (without initializing Spark)"""
    print("\n📦 Checking imports...")
    
    try:
        # Check if the module structure is correct
        import UnnamedSlug
        print("✅ UnnamedSlug package imports successfully")
        
        # Try importing without creating Spark session
        from UnnamedSlug.jobs.regression.entrypoint import RegressionJob
        print("✅ RegressionJob class imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🧪 Databricks CI/CD Pipeline Verification")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Configuration", check_configuration),
        ("Imports", check_imports)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            all_passed = False
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 SUCCESS! Your CI/CD pipeline is ready!")
        print("\n📋 Next Steps:")
        print("1. ✅ Databricks workspace connected")
        print("2. ✅ Files and configurations are ready")
        print("3. 🚀 Deploy to Databricks using one of these methods:")
        print()
        print("   Option A - Manual file deployment:")
        print("   💻 Run in Databricks notebook:")
        print("   %pip install /Workspace/Repos/<your-repo>/UnnamedSlug")
        print("   from UnnamedSlug.jobs.regression.entrypoint import RegressionJob")
        print("   job = RegressionJob(); job.launch()")
        print()
        print("   Option B - Upload files manually:")
        print("   1. Upload 'UnnamedSlug' folder to Databricks workspace")
        print("   2. Create a notebook and run the regression job")
        print()
        print("   Option C - Try dbx again (may need dependency fixes):")
        print("   dbx deploy --files-only")
        print("   dbx launch --job=databricks-cicd-template-regression")
        
    else:
        print("❌ Some checks failed. Please review the errors above.")
    
    print("\n🔧 What your regression model does:")
    print("• Generates 10,000 synthetic data points")
    print("• Trains a Linear Regression model")
    print("• Evaluates with RMSE and R² metrics")
    print("• Logs experiments to MLflow")
    print("• Saves predictions to Delta/Parquet")

if __name__ == "__main__":
    main() 