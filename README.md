# 🚀 MLOps Pipeline with GitHub Actions & Databricks

[![MLOps Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/mlops-pipeline.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/mlops-pipeline.yml)

A **production-ready MLOps pipeline** using **GitHub Actions** for CI/CD and **Databricks** for model training, serving, and monitoring.

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

## 🏗️ **Architecture**

```
GitHub Repository
├── Code Changes → GitHub Actions
├── Unit Tests → Validation
├── Model Training → Databricks Jobs
├── Model Registry → MLflow
├── Model Serving → Databricks Endpoints
└── Monitoring → Auto-Retraining
```

## 🚀 **Quick Start**

### **1. Setup GitHub Secrets**

1. Go to your **GitHub repository**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add this secret:
   ```
   Name: DATABRICKS_TOKEN
   Value: dapi8177f62e4c349554eca732a116742bc9
   ```

### **2. Deploy the Pipeline**

```bash
# Push to main branch to trigger the pipeline
git add .
git commit -m "Deploy MLOps pipeline"
git push origin main
```

### **3. Monitor the Pipeline**

1. Go to **Actions** tab in your GitHub repository
2. Watch the live logs for each job:
   - 🧪 **Run Unit Tests**
   - 🚀 **Train and Deploy Model**
   - 🌐 **Deploy Model to Serving Endpoint**
   - 🔄 **Setup Auto-Retraining Pipeline**

## 📊 **Model Serving Endpoint**

After deployment, your model is available at:

```
https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations
```

### **Make Predictions:**

```python
import requests

url = "https://adb-1244961191947049.9.azuredatabricks.net/serving-endpoints/regression-model-endpoint/invocations"
headers = {
    "Authorization": "Bearer dapi8177f62e4c349554eca732a116742bc9",
    "Content-Type": "application/json"
}

data = {
    "dataframe_records": [
        {
            "feature1": 50.0,
            "feature2": 25.0, 
            "feature3": 12.5
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
prediction = response.json()
print(f"Prediction: {prediction}")
```

## 🔄 **Auto-Retraining**

The pipeline automatically retrains when:

1. **📅 Scheduled**: Daily at 2 AM UTC
2. **📈 Data Drift**: Input data changes significantly  
3. **📉 Performance Drop**: Model accuracy decreases
4. **💾 New Data**: Fresh training data becomes available

## 📁 **Project Structure**

```
databricks-cicd-template/
├── .github/workflows/
│   ├── mlops-pipeline.yml          # Main MLOps pipeline
│   ├── data-retrain.yml           # Data-driven retraining
│   └── test-pr.yml                # PR validation
├── UnnamedSlug/
│   ├── jobs/
│   │   ├── regression/
│   │   │   └── entrypoint.py       # Model training
│   │   └── auto_retrain/
│   │       └── data_monitor.py     # Auto-retraining logic
│   └── common.py                   # Shared utilities
├── tests/
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
├── conf/
│   └── test/
│       └── regression.json         # Configuration
├── scripts/
│   └── github_actions_setup.py    # Setup script
└── requirements/
    ├── unit-requirements-fixed.txt # Dependencies
    └── requirements.txt
```

## 🛠️ **Technologies Used**

- **🔄 CI/CD**: GitHub Actions
- **🧠 ML Platform**: Databricks
- **📊 Experiment Tracking**: MLflow
- **🌐 Model Serving**: Databricks Model Serving
- **📈 Monitoring**: Data drift detection
- **🐍 Language**: Python
- **⚡ Compute**: Apache Spark

## 🎯 **Features**

### **✅ Continuous Integration**
- Automated testing on every commit
- Pull request validation
- Code quality gates

### **✅ Continuous Deployment**
- Automatic model training and registration
- Seamless production deployment
- Multi-environment support

### **✅ Model Serving**
- Real-time prediction endpoint
- Auto-scaling and cost optimization
- Request logging and monitoring

### **✅ Monitoring & Observability**
- Data drift detection
- Performance monitoring
- GitHub Actions integration

### **✅ Continuous Learning**
- Automatic retraining on new data
- Model performance comparison
- Intelligent model promotion

## 📈 **Monitoring & Dashboards**

### **GitHub Actions**
- Pipeline status and logs
- Build history and artifacts
- Email notifications on failures

### **Databricks**
- **Jobs**: `https://adb-1244961191947049.9.azuredatabricks.net/#job/list`
- **MLflow**: `https://adb-1244961191947049.9.azuredatabricks.net/#mlflow`
- **Serving**: `https://adb-1244961191947049.9.azuredatabricks.net/#/serving-endpoints`

## 🔧 **Configuration**

### **Model Configuration** (`conf/test/regression.json`)
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

### **Workflow Triggers**
- **Push to main/develop**: Full pipeline
- **Pull requests**: Testing only
- **Schedule**: Data monitoring every 6 hours
- **Manual**: On-demand execution

## 🚨 **Alerts & Notifications**

The pipeline monitors:
- ✅ **Pipeline Status** (GitHub Actions notifications)
- ✅ **Model Performance** (RMSE, R², MAE)
- ✅ **Data Drift** (feature distribution changes)
- ✅ **Prediction Volume** (requests per minute)
- ✅ **Response Times** (latency monitoring)
- ✅ **Error Rates** (failed predictions)

## 🔥 **Why GitHub Actions?**

### **Advantages over Azure DevOps:**
1. **🆓 Free for Public Repos** - 2,000 minutes/month for private
2. **🔧 Simpler Setup** - No variable groups, just repository secrets
3. **📱 Better Integration** - Native GitHub ecosystem
4. **🚀 Faster Iteration** - Edit workflows directly in GitHub
5. **🌐 Community Actions** - Vast marketplace of pre-built actions
6. **📊 Better Visibility** - Status badges, PR checks, notifications

## 📚 **Documentation**

- **[GitHub Actions Deployment Guide](GITHUB_ACTIONS_DEPLOYMENT_GUIDE.md)** - Complete setup instructions
- **[Testing Guide](TESTING_GUIDE.md)** - Testing procedures and options

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

**🚀 Your enterprise-grade MLOps pipeline with GitHub Actions is ready for production!**
