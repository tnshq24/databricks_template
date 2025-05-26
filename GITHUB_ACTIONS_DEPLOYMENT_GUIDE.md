# 🚀 Complete MLOps Pipeline with GitHub Actions

This guide will help you deploy a **full production MLOps pipeline** using **GitHub Actions** with automatic retraining and model serving.

## 🎯 **What This Pipeline Does**

### **Complete Automated Workflow:**
1. **Code Changes** → Triggers GitHub Actions workflow
2. **Unit Testing** → Validates code quality
3. **Model Training** → Trains on latest data
4. **Model Registration** → Saves to MLflow registry
5. **Performance Evaluation** → Compares with production model
6. **Auto-Promotion** → Promotes better models to production
7. **Model Serving** → Deploys to real-time endpoint
8. **Monitoring** → Watches for data drift and performance
9. **Auto-Retraining** → Triggers when needed

## 📋 **Prerequisites**

✅ **GitHub Repository** (this repository)  
✅ **Databricks Workspace**: `https://adb-1244961191947049.9.azuredatabricks.net`  
✅ **Databricks Token**: `<YOUR_DATABRICKS_TOKEN>`  
✅ **GitHub Actions enabled** (enabled by default)  

## 🔧 **Step 1: GitHub Repository Setup**

### 1.1 **Add GitHub Secrets**

1. Go to your **GitHub repository**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add this secret:

```
Name: DATABRICKS_TOKEN
Value: <YOUR_DATABRICKS_TOKEN>
```

⚠️ **Make sure to mark it as a secret** - never commit tokens to your code!

### 1.2 **Verify Workflow File**

The workflow file is already created at `.github/workflows/mlops-pipeline.yml`. This handles:
- ✅ **Unit Testing**
- ✅ **Model Training** 
- ✅ **Model Serving**
- ✅ **Auto-Retraining Setup**

## 🚀 **Step 2: Deploy the Pipeline**

### **Trigger the Workflow**

You can trigger the pipeline in multiple ways:

#### **Option A: Push to Main Branch** (Automatic)
```bash
git add .
git commit -m "Deploy MLOps pipeline"
git push origin main
```

#### **Option B: Manual Trigger**
1. Go to **Actions** tab in your GitHub repository
2. Click **MLOps Pipeline**
3. Click **Run workflow**
4. Select branch and click **Run workflow**

#### **Option C: Create Pull Request**
```bash
git checkout -b feature/mlops-update
git add .
git commit -m "Update MLOps pipeline"
git push origin feature/mlops-update
# Create PR in GitHub UI
```

### **Monitor the Pipeline**

1. Go to **Actions** tab
2. Click on your running workflow
3. Watch the live logs for each job:
   - 🧪 **Run Unit Tests**
   - 🚀 **Train and Deploy Model**
   - 🌐 **Deploy Model to Serving Endpoint**
   - 🔄 **Setup Auto-Retraining Pipeline**

## 📊 **Step 3: Model Serving Endpoint**

After successful deployment, your model will be available at:

```
Endpoint URL: https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations
```

### **How to Use the Endpoint**

#### **Python Client Example:**
```python
import requests
import json

# Endpoint configuration
url = "https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations"
headers = {
         "Authorization": "Bearer <YOUR_DATABRICKS_TOKEN>",
    "Content-Type": "application/json"
}

# Sample prediction request
data = {
    "dataframe_records": [
        {
            "feature1": 50.0,
            "feature2": 25.0, 
            "feature3": 12.5
        }
    ]
}

# Make prediction
response = requests.post(url, headers=headers, json=data)
prediction = response.json()
print(f"Prediction: {prediction}")
```

#### **curl Example:**
```bash
curl -X POST \
  https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations \
  -H "Authorization: Bearer <YOUR_DATABRICKS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_records": [
      {
        "feature1": 50.0,
        "feature2": 25.0,
        "feature3": 12.5
      }
    ]
  }'
```

## 🔄 **Step 4: Automatic Retraining**

### **Triggers for Retraining:**

1. **📅 Scheduled**: Daily at 2 AM UTC (configurable)
2. **📈 Data Drift**: When input data changes significantly
3. **📉 Performance Drop**: When model accuracy decreases
4. **💾 New Data**: When fresh training data becomes available

### **Configure Auto-Retraining**

Update `conf/test/regression.json` with monitoring configuration:

```json
{
  "output_format": "delta",
  "output_path": "dbfs:/dbx/tmp/test/UnnamedSlug/regression_model",
  "new_data_path": "dbfs:/mnt/data/incoming/",
  "reference_data_path": "dbfs:/tmp/regression_model/reference_data",
  "retrain_interval_days": 1,
  "drift_threshold": 0.1,
  "performance_threshold": 0.05
}
```

### **Manual Retraining Trigger**

You can manually trigger retraining:

1. **Via GitHub Actions:**
   - Go to **Actions** → **MLOps Pipeline**
   - Click **Run workflow**
   - This will retrain if conditions are met

2. **Via Databricks:**
   ```python
   # Run in Databricks notebook
   from UnnamedSlug.jobs.auto_retrain.data_monitor import DataMonitorJob
   
   job = DataMonitorJob()
   result = job.launch()
   ```

## 📈 **Step 5: Data Pipeline Integration**

### **For New Data Integration:**

1. **Upload new data** to: `dbfs:/mnt/data/incoming/`
2. **Data format** should include:
   ```
   - feature1: numeric
   - feature2: numeric  
   - feature3: numeric
   - target: numeric (for training)
   - timestamp: datetime
   ```

3. **Auto-detection** will trigger retraining automatically

### **GitHub Actions + Data Updates**

Set up data-driven retraining:

```yaml
# Add to .github/workflows/data-retrain.yml
name: Data-Driven Retraining

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  repository_dispatch:
    types: [new-data-available]

jobs:
  check-and-retrain:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Trigger Retraining Check
      run: |
        # Trigger data monitoring job in Databricks
        databricks jobs run-now --job-id $AUTO_RETRAIN_JOB_ID
```

## 🎯 **Step 6: Production Usage**

### **Real-Time Predictions**

Your endpoint automatically:
- ✅ **Scales to zero** when not in use (cost-effective)
- ✅ **Auto-scales up** when requests increase  
- ✅ **Uses latest model** automatically
- ✅ **Logs all requests** for monitoring
- ✅ **Tracks performance** metrics

### **Model Monitoring Dashboard**

Access in Databricks:
1. Go to **Machine Learning** → **Model Serving**
2. Click on `regression-model-endpoint`
3. View **metrics, logs, and performance**

### **MLflow Tracking**

Monitor experiments:
1. Go to **Machine Learning** → **Experiments**
2. Find `/Shared/mlops-regression-experiment`
3. View **runs, metrics, and model versions**

## 🔧 **Step 7: Advanced GitHub Actions**

### **Environment-Specific Workflows**

Create separate workflows for different environments:

```
.github/workflows/
├── mlops-pipeline.yml          # Production (main branch)
├── mlops-dev.yml              # Development (dev branch)
├── mlops-staging.yml          # Staging (staging branch)
└── data-retrain.yml           # Data-driven retraining
```

### **Pull Request Validation**

The workflow automatically runs on PRs:
- ✅ **Unit tests** for code validation
- ✅ **Model training** in dev environment
- ✅ **Performance benchmarks**
- ✅ **Code quality checks**

### **Slack/Teams Notifications**

Add notifications to your workflow:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'MLOps Pipeline: ${{ job.status }}'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## 🚨 **Monitoring & Alerts**

### **What Gets Monitored:**
- ✅ **Pipeline Status** (GitHub Actions notifications)
- ✅ **Model Performance** (RMSE, R², MAE)
- ✅ **Data Drift** (feature distribution changes)
- ✅ **Prediction Volume** (requests per minute)
- ✅ **Response Times** (latency monitoring)
- ✅ **Error Rates** (failed predictions)

### **GitHub Actions Notifications:**

1. **Email notifications** for failed workflows
2. **GitHub UI** shows workflow status
3. **Status badges** for README
4. **Custom webhooks** for external systems

### **Add Status Badge to README:**

```markdown
[![MLOps Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/mlops-pipeline.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/mlops-pipeline.yml)
```

## 🎉 **What You've Built**

### **A Production-Ready MLOps Pipeline with GitHub Actions:**

1. **🔄 Continuous Integration**
   - Automated testing on every commit
   - Pull request validation
   - Code quality gates

2. **🚀 Continuous Deployment** 
   - Automatic model training and registration
   - Seamless production deployment
   - Multi-environment support

3. **📊 Model Serving**
   - Real-time prediction endpoint
   - Auto-scaling and cost optimization
   - Request logging and monitoring

4. **🔍 Monitoring & Observability**
   - Data drift detection
   - Performance monitoring
   - GitHub Actions integration

5. **🔄 Continuous Learning**
   - Automatic retraining on new data
   - Model performance comparison
   - Intelligent model promotion

## 🚀 **Next Steps**

### **Your Pipeline is Ready! 🎯**

1. **✅ Pipeline Deployed** - GitHub Actions running your MLOps workflow
2. **✅ Model Serving** - Real-time predictions available
3. **✅ Auto-Retraining** - Handles new data automatically
4. **✅ Monitoring** - Watches performance and drift

### **Quick Test:**

```bash
# Test the endpoint immediately
curl -X POST \
  https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations \
  -H "Authorization: Bearer <YOUR_DATABRICKS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"dataframe_records": [{"feature1": 50.0, "feature2": 25.0, "feature3": 12.5}]}'
```

### **Monitor Your Pipeline:**

1. **GitHub Actions**: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
2. **Model Serving**: `https://adb-1244961191947049.9.azuredatabricks.net/#/serving-endpoints`
3. **MLflow**: `https://adb-1244961191947049.9.azuredatabricks.net/#mlflow`

## 🔥 **Key Advantages of GitHub Actions vs Azure DevOps**

### **✅ Why GitHub Actions is Better for This Use Case:**

1. **🆓 Free for Public Repos** - 2,000 minutes/month for private repos
2. **🔧 Simpler Setup** - No variable groups, just repository secrets
3. **📱 Better Integration** - Native GitHub ecosystem
4. **🚀 Faster Iteration** - Edit workflows directly in GitHub
5. **🌐 Community Actions** - Vast marketplace of pre-built actions
6. **📊 Better Visibility** - Status badges, PR checks, notifications
7. **🔄 Git-Centric** - Everything in your repository

### **🎯 No Azure DevOps Approval Needed!**

Your MLOps pipeline runs entirely within:
- ✅ **Your GitHub repository** (code and workflows)
- ✅ **GitHub Actions** (CI/CD execution)  
- ✅ **Your Databricks workspace** (model training and serving)

**🚀 Your enterprise-grade MLOps pipeline is now running with GitHub Actions!** 