# Azure Document Intelligence 4.0 Demo - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Azure Credentials
Choose one of these options:

**Option A: In-App Configuration (Easiest)**
- Skip this step and go directly to Step 3
- Enter credentials in the sidebar when the app starts
- Perfect for quick testing and demos

**Option B: Environment Variables**
```bash
export AZURE_DI_ENDPOINT='https://your-resource-name.cognitiveservices.azure.com/'
export AZURE_DI_API_KEY='your-api-key-here'
```

**Option C: Create .env file**
```bash
# Create .env file with your credentials
echo "AZURE_DI_ENDPOINT=https://your-resource.cognitiveservices.azure.com" > .env
echo "AZURE_DI_API_KEY=your-api-key-here" >> .env
```

### Step 3: Run the Application
```bash
streamlit run app.py
```

### Step 4: Open in Browser
Navigate to: http://localhost:8501

## 🎯 Quick Demo Flow

1. **Select a Model**: Choose "Receipt" from the sidebar dropdown
2. **Load Sample**: Click "Sample Documents" → Select "Receipt Sample" → Click "Load Sample"
3. **Analyze**: Click the "🚀 Analyze Document" button
4. **View Results**: Explore the three result tabs (Fields, Markdown, Raw JSON)
5. **Try Annotations**: Toggle "Show Annotations" to see bounding boxes

## 🏥 Azure Resource Setup

If you don't have an Azure Document Intelligence resource:

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Document Intelligence" resource
3. Get the endpoint URL and API key from the resource page
4. Use these credentials in the app

## 📋 Supported Features

### Models Available
- **Core**: Read OCR, Layout Analysis
- **Business**: Receipts, Invoices, Business Cards, Contracts
- **Financial**: Bank Checks, Statements, Pay Stubs
- **Government**: Tax forms (W-2, 1040, etc.), Mortgage documents
- **Healthcare**: Insurance cards

### File Formats
- PDF (up to 2000 pages)
- Images: JPG, PNG, BMP, TIFF
- Size limit: 500MB

### Analysis Features
- Text extraction with OCR
- Table detection and extraction
- Key-value pair identification
- Form field recognition
- Document structure analysis
- Multi-language support

## 🔧 Troubleshooting

### Common Issues

**"No module named 'streamlit'"**
```bash
pip install -r requirements.txt
```

**"Connection failed"**
- Check your endpoint URL (should start with https://)
- Verify API key is correct
- Ensure resource is active in Azure

**"Analysis failed"**
- Try a smaller file size
- Check file format is supported
- Verify internet connection

**"Could not generate preview"**
- Install pdf2image dependencies:
  ```bash
  # On macOS
  brew install poppler
  
  # On Ubuntu/Debian
  sudo apt-get install poppler-utils
  
  # On Windows
  # Download poppler binaries and add to PATH
  ```

### Getting Help

1. Check the [SPEC.md](SPEC.md) for technical details
2. Review [README.md](README.md) for comprehensive documentation
3. Test connection in the sidebar "Connection Status" section
4. Try sample documents first before using your own files

## 🎨 Demo Tips

### Best Results
- Use clear, high-resolution images
- Try model-specific samples (receipt model with receipts)
- Experiment with different parameters
- Use page ranges for large documents

### Cool Features to Try
- **In-app credentials**: Enter Azure credentials directly in the sidebar
- **Multi-page navigation**: Upload a multi-page PDF
- **Feature toggles**: Enable/disable OCR high resolution
- **Annotation viewer**: Toggle annotations on/off
- **Export options**: Download JSON results or copy to clipboard
- **Zoom controls**: Zoom in on document details

## 📊 What to Expect

### Analysis Time
- Single page: 5-15 seconds
- Multi-page PDF: 30-60 seconds
- Large documents: 1-2 minutes

### Accuracy
- High-quality scans: 95%+ accuracy
- Mobile photos: 85-95% accuracy
- Low quality images: 70-85% accuracy

Ready to explore Azure Document Intelligence? Start the app and try the sample documents! 🎉