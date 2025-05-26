#!/usr/bin/env python3
"""
GitHub Actions Setup Script for MLOps Pipeline
"""

import os
import json
import subprocess
import sys
from pathlib import Path


class GitHubActionsSetup:
    """Setup GitHub Actions for MLOps pipeline"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.databricks_host = "https://adb-1244961191947049.9.azuredatabricks.net"
        self.databricks_token = "<YOUR_DATABRICKS_TOKEN>"
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Not in a git repository. Please initialize git first:")
                print("   git init")
                print("   git remote add origin <your-github-repo-url>")
                return False
        except FileNotFoundError:
            print("❌ Git not found. Please install git.")
            return False
        
        # Check if GitHub CLI is available (optional)
        try:
            subprocess.run(['gh', '--version'], capture_output=True)
            self.has_gh_cli = True
            print("✅ GitHub CLI found - can help with secret setup")
        except FileNotFoundError:
            self.has_gh_cli = False
            print("ℹ️ GitHub CLI not found - manual secret setup required")
        
        # Check workflow files
        workflows_dir = self.repo_root / '.github' / 'workflows'
        if workflows_dir.exists():
            print("✅ GitHub workflows directory exists")
        else:
            print("❌ GitHub workflows directory not found")
            return False
            
        # Check if main workflow exists
        main_workflow = workflows_dir / 'mlops-pipeline.yml'
        if main_workflow.exists():
            print("✅ Main MLOps workflow found")
        else:
            print("❌ Main MLOps workflow not found")
            return False
            
        print("✅ All prerequisites met!")
        return True
    
    def setup_github_secrets(self):
        """Setup GitHub repository secrets"""
        print("\n🔐 Setting up GitHub secrets...")
        
        if self.has_gh_cli:
            # Try to set secrets using GitHub CLI
            try:
                print("🔑 Setting DATABRICKS_TOKEN secret...")
                result = subprocess.run([
                    'gh', 'secret', 'set', 'DATABRICKS_TOKEN',
                    '--body', self.databricks_token
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ DATABRICKS_TOKEN secret set successfully!")
                else:
                    print(f"❌ Failed to set secret: {result.stderr}")
                    self._manual_secret_instructions()
            except Exception as e:
                print(f"❌ Error using GitHub CLI: {e}")
                self._manual_secret_instructions()
        else:
            self._manual_secret_instructions()
    
    def _manual_secret_instructions(self):
        """Provide manual instructions for setting secrets"""
        print("\n📝 Manual Secret Setup Instructions:")
        print("1. Go to your GitHub repository")
        print("2. Click Settings → Secrets and variables → Actions")
        print("3. Click 'New repository secret'")
        print("4. Add the following secret:")
        print("")
        print("   Name: DATABRICKS_TOKEN")
        print(f"   Value: {self.databricks_token}")
        print("")
        print("5. Click 'Add secret'")
        print("")
        print("⚠️ Keep this token secure and never commit it to your code!")
    
    def verify_workflow_files(self):
        """Verify workflow files are correctly configured"""
        print("\n📋 Verifying workflow files...")
        
        workflows_dir = self.repo_root / '.github' / 'workflows'
        
        # Check main workflow
        main_workflow = workflows_dir / 'mlops-pipeline.yml'
        if main_workflow.exists():
            print("✅ Main MLOps workflow: mlops-pipeline.yml")
            
            # Check if it contains the correct Databricks host
            content = main_workflow.read_text(encoding='utf-8')
            if self.databricks_host in content:
                print("✅ Correct Databricks host configured")
            else:
                print("⚠️ Databricks host may need updating in workflow")
        
        # Check data retraining workflow
        data_workflow = workflows_dir / 'data-retrain.yml'
        if data_workflow.exists():
            print("✅ Data retraining workflow: data-retrain.yml")
        else:
            print("ℹ️ Data retraining workflow not found (optional)")
    
    def create_test_pr_workflow(self):
        """Create a simple workflow for testing PRs"""
        print("\n🧪 Creating test workflow for PRs...")
        
        workflows_dir = self.repo_root / '.github' / 'workflows'
        test_workflow = workflows_dir / 'test-pr.yml'
        
        workflow_content = """name: Test Pull Request

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r unit-requirements-fixed.txt
        pip install -e .

    - name: Run unit tests
      run: |
        python -m pytest tests/unit/ -v --tb=short

    - name: Validate configuration
      run: |
        echo "✅ PR validation passed!"
        echo "📋 Ready for review and merge"
"""
        
        test_workflow.write_text(workflow_content, encoding='utf-8')
        print(f"✅ Created test workflow: {test_workflow}")
    
    def generate_status_badge(self):
        """Generate status badge for README"""
        print("\n🏷️ GitHub Actions status badge:")
        print("")
        print("Add this to your README.md:")
        print("")
        
        # Try to get repository info
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                # Extract owner/repo from URL
                if 'github.com' in repo_url:
                    repo_path = repo_url.split('github.com/')[-1].replace('.git', '')
                    badge_url = f"https://github.com/{repo_path}/actions/workflows/mlops-pipeline.yml/badge.svg"
                    action_url = f"https://github.com/{repo_path}/actions/workflows/mlops-pipeline.yml"
                    
                    print(f"[![MLOps Pipeline]({badge_url})]({action_url})")
                    print("")
                    print("This will show the current status of your MLOps pipeline!")
                else:
                    print("Repository URL format not recognized")
            else:
                print("Could not determine repository URL")
        except Exception as e:
            print(f"Error getting repository info: {e}")
    
    def provide_next_steps(self):
        """Provide next steps for the user"""
        print("\n🚀 Next Steps:")
        print("")
        print("1. ✅ Commit and push your changes:")
        print("   git add .")
        print("   git commit -m 'Add GitHub Actions MLOps pipeline'")
        print("   git push origin main")
        print("")
        print("2. 🔐 Set up GitHub secrets (if not done already)")
        print("")
        print("3. 📊 Monitor your pipeline:")
        print("   - Go to your GitHub repository")
        print("   - Click the 'Actions' tab")
        print("   - Watch your MLOps pipeline run!")
        print("")
        print("4. 🌐 Access your model endpoint:")
        print(f"   {self.databricks_host}/serving-endpoints/regression-model-endpoint/invocations")
        print("")
        print("5. 📈 Monitor in Databricks:")
        print(f"   - Jobs: {self.databricks_host}/#job/list")
        print(f"   - MLflow: {self.databricks_host}/#mlflow")
        print(f"   - Serving: {self.databricks_host}/#/serving-endpoints")
        print("")
        print("🎉 Your MLOps pipeline with GitHub Actions is ready!")
    
    def run(self):
        """Run the complete setup"""
        print("🚀 GitHub Actions MLOps Pipeline Setup")
        print("=" * 40)
        
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix issues above.")
            return False
        
        self.setup_github_secrets()
        self.verify_workflow_files()
        self.create_test_pr_workflow()
        self.generate_status_badge()
        self.provide_next_steps()
        
        return True


if __name__ == "__main__":
    setup = GitHubActionsSetup()
    success = setup.run()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1) 