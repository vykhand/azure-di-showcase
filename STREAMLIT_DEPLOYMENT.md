# Deploying Azure Document Intelligence Demo to Streamlit Community Cloud

This guide provides step-by-step instructions for deploying your Azure Document Intelligence demo application to Streamlit Community Cloud.

## Prerequisites

Before you begin, ensure you have:

1. **GitHub Account**: A GitHub account to host your repository
2. **Streamlit Community Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Azure Document Intelligence Resource**:
   - Azure subscription with Document Intelligence resource created
   - Endpoint URL (e.g., `https://your-resource.cognitiveservices.azure.com`)
   - API Key from your Azure portal

## Step 1: Prepare Your Repository

### 1.1 Create/Update `.gitignore`

Ensure your `.gitignore` file includes:

```gitignore
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml
```

### 1.2 Verify `requirements.txt`

Your `requirements.txt` should contain all necessary dependencies:

```txt
streamlit>=1.28.0
aiohttp>=3.8.5
asyncio
Pillow>=10.0.0
pandas>=2.0.3
plotly>=5.15.0
streamlit-ace>=0.1.1
streamlit-aggrid>=0.3.4
python-dotenv>=1.0.0
requests>=2.31.0
typing-extensions>=4.5.0
pdf2image>=1.16.3
```

### 1.3 Create `packages.txt` for System Dependencies

Streamlit Community Cloud needs system-level packages for PDF processing. Create `packages.txt`:

```txt
poppler-utils
```

This file tells Streamlit to install poppler-utils (required for pdf2image) during deployment.

### 1.4 Remove Sensitive Data

**IMPORTANT**: Never commit your `.env` file or any files containing API keys!

```bash
# If .env was accidentally committed, remove it from git history
git rm --cached .env

# Or create a clean .env.example instead
cp .env .env.example
# Edit .env.example to replace actual values with placeholders
```

Create `.env.example`:

```bash
# Azure Document Intelligence Configuration
# Copy this file to .env and fill in your actual values

# Your Azure Document Intelligence endpoint URL
AZURE_DI_ENDPOINT="https://your-resource.cognitiveservices.azure.com"

# Your Azure Document Intelligence API key
AZURE_DI_API_KEY="your-api-key-here"
```

## Step 2: Push to GitHub

### 2.1 Initialize Git (if not already done)

```bash
git init
git add .
git commit -m "Initial commit: Azure DI demo app"
```

### 2.2 Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name your repository (e.g., `azure-di-showcase`)
4. Choose "Public" visibility (required for free Streamlit Community Cloud)
5. Don't initialize with README (you already have one)
6. Click "Create repository"

### 2.3 Push Your Code

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/vykhand/azure-di-showcase.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Streamlit Community Cloud

### 3.1 Sign In to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub repositories

### 3.2 Create New App

1. Click "New app" button
2. Fill in the deployment settings:

   **Repository**: Select your repository (e.g., `vykhand/azure-di-showcase`)

   **Branch**: `main` (or your default branch)

   **Main file path**: `app.py`

   **App URL**: Choose a custom URL (e.g., `azure-di-demo`) or use the auto-generated one

3. Click "Advanced settings" (Optional but recommended):

   **Python version**: `3.9` or higher (recommended: `3.11`)

### 3.3 Configure Secrets

This is the most important step for security!

1. Before clicking "Deploy", scroll to "Advanced settings"
2. Click on "Secrets" section
3. Add your Azure credentials in TOML format:

```toml
# .streamlit/secrets.toml format
AZURE_DI_ENDPOINT = "https://your-resource.cognitiveservices.azure.com"
AZURE_DI_API_KEY = "your-actual-api-key-here"
```

**Important Notes**:
- Replace `your-resource` with your actual Azure resource name
- Replace `your-actual-api-key-here` with your actual API key from Azure portal
- Make sure there are no trailing slashes in the endpoint URL
- Keep the quotes around the values

### 3.4 Deploy

1. Click "Deploy!" button
2. Wait for the app to build (usually 2-5 minutes)
3. Watch the build logs for any errors

## Step 4: Verify Deployment

### 4.1 Test the Application

Once deployed, your app will open automatically. Test the following:

1. **Connection Status**:
   - Open the sidebar
   - Expand "🔌 Connection Status"
   - Should show "Connection successful!"

2. **Model Selection**:
   - Select a model from the dropdown
   - Verify model information displays correctly

3. **Document Upload**:
   - Try uploading a test document
   - Verify analysis works correctly

4. **New Features**:
   - Test the "Copy JSON" button in the Raw JSON tab
   - Works without requiring .env file

### 4.2 Troubleshooting Common Issues

#### Build Fails

**Error**: `ModuleNotFoundError`
- **Solution**: Check `requirements.txt` has all dependencies
- Verify package names and versions are correct

**Error**: `pdf2image` related errors or "Unable to get page count. Is poppler installed?"
- **Solution**: Make sure you have `packages.txt` file in your repository root with:
  ```txt
  poppler-utils
  ```
- This file should already be included in your repository
- If missing, create it and push to GitHub, then redeploy

#### Connection Issues

**Error**: "Connection failed" or "401 Unauthorized"
- **Solution**:
  - Verify secrets are correctly formatted in TOML
  - Check Azure endpoint URL is correct
  - Ensure API key is valid and not expired
  - Verify Azure resource is in "Running" state

**Error**: "Resource not found"
- **Solution**:
  - Double-check endpoint URL format
  - Ensure no trailing slashes
  - Verify API version compatibility

#### Runtime Errors

**Error**: App crashes or times out
- **Solution**:
  - Check app logs in Streamlit Cloud dashboard
  - Reduce document size for testing
  - Verify sufficient resources (free tier has limits)

## Step 5: Manage Your Deployment

### 5.1 Update the App

To update your deployed app:

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Community Cloud will automatically redeploy your app within a few minutes.

### 5.2 View Logs

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click "Manage app" → "Logs"
4. View real-time logs for debugging

### 5.3 Update Secrets

1. Go to your app settings in Streamlit Cloud
2. Click "⚙️ Settings" → "Secrets"
3. Update the TOML configuration
4. Click "Save"
5. App will automatically restart

## Step 6: Share Your App

### 6.1 Get Your App URL

Your app will be available at:
```
https://YOUR-APP-NAME.streamlit.app
```

Or if you chose a custom subdomain:
```
https://YOUR-CUSTOM-NAME.streamlit.app
```

### 6.2 Add to README

Update your repository's README.md with a link to the live app:

```markdown
# Azure Document Intelligence Demo

🚀 **[Try the Live Demo](https://your-app-name.streamlit.app)**

[Rest of your README content...]
```

### 6.3 Share on Social Media

Streamlit Community Cloud provides a built-in sharing button with social media options.

## Additional Resources

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Managing Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

### Azure Documentation
- [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Get API Keys](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/create-document-intelligence-resource)

### Support
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/vykhand/azure-di-showcase/issues)

## Security Best Practices

1. **Never commit secrets**: Always use Streamlit secrets or environment variables
2. **Use .gitignore**: Ensure `.env` and `secrets.toml` are ignored
3. **Rotate keys**: Regularly rotate your Azure API keys
4. **Monitor usage**: Check Azure portal for unusual API usage
5. **Repository visibility**: Consider making repository private if it contains sensitive logic
6. **Rate limiting**: Implement rate limiting in production apps

## Cost Considerations

### Streamlit Community Cloud (Free Tier)
- 1 private app OR unlimited public apps
- Limited resources (1 GB RAM per app)
- May sleep after inactivity
- No custom domain on free tier

### Azure Document Intelligence
- Pay-per-use pricing
- Free tier: 500 pages/month
- Check [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/) for details
- Monitor usage in Azure portal

## Alternative: Using Credentials via UI

If you don't want to use secrets (not recommended for production):

1. Users can enter credentials directly in the sidebar
2. Credentials are not persisted between sessions
3. Good for demos but not ideal for shared apps
4. Consider this for personal use only

The app now supports this method - if no `.env` or secrets are found, input boxes will appear in the sidebar.

## Conclusion

Your Azure Document Intelligence demo is now live and accessible to anyone with the URL!

For any issues or questions, refer to the troubleshooting section or reach out via GitHub Issues.

Happy deploying! 🚀