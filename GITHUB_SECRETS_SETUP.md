# 🔐 GitHub Secrets Setup Guide

## Required Secret Configuration

Your GitHub Actions workflows require the following secret to be configured:

### 🔑 **DATABRICKS_TOKEN**

**Value**: `[YOUR_DATABRICKS_TOKEN_HERE]`  
**Description**: Your Databricks personal access token for API authentication

> ⚠️ **Security Note**: Get your token from Databricks workspace → Settings → User Settings → Access Tokens

## 📋 **Step-by-Step Setup Instructions**

### 1. Navigate to Your GitHub Repository
Go to: `https://github.com/tnshq24/databricks_template`

### 2. Access Repository Settings
- Click on the **Settings** tab (in the top menu bar)
- In the left sidebar, click on **Secrets and variables** 
- Select **Actions**

### 3. Add New Repository Secret
- Click **New repository secret**
- Set **Name**: `DATABRICKS_TOKEN`
- Set **Secret**: `[PASTE_YOUR_DATABRICKS_TOKEN_HERE]`
- Click **Add secret**

> 📝 **How to get your token**:
> 1. Go to your Databricks workspace: `https://adb-1244961191947049.9.azuredatabricks.net`
> 2. Click Settings → User Settings → Access Tokens
> 3. Click "Generate New Token"
> 4. Copy the token value and paste it in the GitHub secret

## ✅ **Verification Steps**

After adding the secret, verify it's working:

1. **Go to Actions tab** in your GitHub repository
2. **Manually trigger** the "Complete MLOps Deployment" workflow:
   - Click on **Actions** → **Complete MLOps Deployment**
   - Click **Run workflow** → **Run workflow**
3. **Monitor the execution** to ensure authentication works

## 🔧 **Troubleshooting**

### If you see "Authorization failed" errors:

1. **Check token validity**: 
   - Go to Databricks workspace: `https://adb-1244961191947049.9.azuredatabricks.net`
   - Settings → User Settings → Access Tokens
   - Verify your token is still active

2. **Regenerate token if needed**:
   - Create a new personal access token in Databricks
   - Update the GitHub secret with the new token

3. **Verify secret name**: Ensure it's exactly `DATABRICKS_TOKEN` (case-sensitive)

## 🚀 **Ready to Deploy!**

Once the secret is configured, your workflows will:
- ✅ Connect to Databricks successfully
- ✅ Run unit tests
- ✅ Train and deploy ML models
- ✅ Set up model serving endpoints
- ✅ Configure auto-retraining pipelines

## 📞 **Need Help?**

If you continue to see authentication errors:
1. Double-check the token value in Databricks
2. Ensure the token has proper permissions
3. Verify the GitHub secret is saved correctly 