# 🔒 Private Network Databricks Deployment Guide

## ⚠️ Issue: Private Network Access Required

Your Databricks workspace is in a private network requiring VPN access. GitHub Actions public runners **cannot** access it directly.

**Error**: `Unauthorized network access to workspace: 1244961191947049`

## 🛠️ Deployment Solutions

### **Option 1: Self-Hosted GitHub Runners (Recommended)**

#### **Setup Steps:**

1. **Set up a runner inside your private network:**
   ```bash
   # On a machine with VPN access to Databricks
   mkdir actions-runner && cd actions-runner
   curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
   tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
   ```

2. **Configure the runner:**
   ```bash
   # Get token from: https://github.com/tnshq24/databricks_template/settings/actions/runners
   ./config.sh --url https://github.com/tnshq24/databricks_template --token [RUNNER_TOKEN]
   ```

3. **Start the runner:**
   ```bash
   ./run.sh
   ```

4. **Use the workflow:** `.github/workflows/mlops-pipeline-private.yml`

#### **Benefits:**
- ✅ Full access to private Databricks workspace
- ✅ Can run all CI/CD operations
- ✅ Secure within your network perimeter

---

### **Option 2: Manual Deployment via Local Development**

#### **For Development/Testing:**

1. **Connect to VPN** on your local machine

2. **Run deployment script locally:**
   ```bash
   # Set environment variables
   export DATABRICKS_HOST="https://adb-1244961191947049.9.azuredatabricks.net"
   export DATABRICKS_TOKEN="your_token_here"
   
   # Install Databricks CLI
   pip install databricks-cli
   
   # Configure CLI
   databricks configure --token
   
   # Deploy code
   databricks workspace mkdirs /Workspace/Shared/UnnamedSlug
   find UnnamedSlug -name "*.py" -type f | while read file; do
     workspace_path="/Workspace/Shared/${file}"
     echo "Uploading $file to $workspace_path"
     databricks workspace import "$file" "$workspace_path" --language PYTHON --overwrite
   done
   ```

3. **Test in Databricks notebook:**
   ```python
   %run /Workspace/Shared/UnnamedSlug/jobs/regression/entrypoint
   
   # Create and run the job
   job = RegressionJob()
   job.launch()
   ```

---

### **Option 3: Azure DevOps with Private Agents**

#### **If you have Azure DevOps access:**

1. **Set up Azure DevOps private agent** in your network
2. **Create Azure pipeline** that can access Databricks
3. **Use Azure Repos** or GitHub integration

---

### **Option 4: Databricks Asset Bundles (DABs)**

#### **Modern approach with private workspace:**

1. **Install Databricks CLI locally** (on VPN-connected machine)
2. **Initialize bundle:**
   ```bash
   databricks bundle init
   ```
3. **Configure bundle** for your workspace
4. **Deploy:**
   ```bash
   databricks bundle deploy
   ```

---

## 🔧 **Immediate Testing Solution**

### **Test Locally (While Connected to VPN):**

1. **Connect to your company VPN**

2. **Test connection:**
   ```bash
   curl -H "Authorization: Bearer your_token" \
        "https://adb-1244961191947049.9.azuredatabricks.net/api/2.0/clusters/list"
   ```

3. **If successful**, deploy using any of the above methods

---

## 📋 **Recommended Architecture**

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│ Self-Hosted  │───▶│   Private       │
│                 │    │   Runner     │    │   Databricks    │
│                 │    │ (Inside VPN) │    │   Workspace     │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

---

## ⚡ **Quick Start**

**For immediate testing:**
1. Connect to company VPN
2. Run local deployment script above
3. Test MLOps pipeline in Databricks

**For production CI/CD:**
1. Set up self-hosted GitHub runner
2. Use `.github/workflows/mlops-pipeline-private.yml`
3. Enjoy automated deployments! 🚀

## 🆘 **Need Help?**

- **GitHub Runner Setup**: https://docs.github.com/en/actions/hosting-your-own-runners
- **Databricks CLI**: https://docs.databricks.com/en/dev-tools/cli/index.html
- **Private Network**: Contact your network admin for VPN access details 