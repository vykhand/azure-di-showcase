# Azure Document Intelligence 4.0 Streamlit Demo

A comprehensive Streamlit application that showcases all Azure Document Intelligence 4.0 capabilities through REST API integration. This demo provides an intuitive interface similar to Azure DI Studio for document analysis, extraction, and visualization.

## Features

### 🤖 Model Selection
- Support for 20+ prebuilt models including:
  - Core models: Read OCR, Layout Analysis
  - Document types: Receipts, Invoices, Business Cards, ID Documents
  - Financial documents: Bank Checks, Statements, Pay Stubs
  - US Tax documents: W-2, W-4, 1040, 1098, 1099, 1099-SSA, 1095-A, 1095-C
  - US Mortgage documents: 1003, 1004, 1005, 1008, Closing Disclosure
  - Healthcare: US Health Insurance Cards

### ⚙️ Dynamic Parameter Configuration
- Automatic UI generation based on selected model
- Support for all API parameters:
  - Page ranges (e.g., "1-3,5,7-9")
  - Locale selection (multiple languages)
  - String index types
  - Output content formats
  - Feature toggles (OCR high-res, languages, barcodes, formulas, etc.)
  - Additional output options

### 📁 Flexible Document Upload
- **File Upload**: Drag & drop or browse for local files
- **URL Input**: Analyze documents from web URLs
- **Sample Documents**: Pre-loaded samples for testing different models

### 📄 Document Visualization
- Annotated document viewer similar to Azure DI Studio
- Color-coded bounding boxes for different element types
- Interactive page navigation for multi-page documents
- Zoom and pan functionality
- Confidence scores and content previews

### 📊 Multi-Format Results Display
- **Fields View**: Structured data extraction with confidence scores
- **Markdown Output**: Clean, copyable text representation
- **Raw JSON**: Complete API response with syntax highlighting
- **Download JSON**: Export analysis results to JSON file
- **Copy to Clipboard**: One-click copy of JSON results

### 🔧 Advanced Features
- **Query Fields**: extract custom, ad-hoc fields from any supported model with no training (add-on; not available on tax W-2/1098/1099)
- **Searchable PDF**: download a text-embedded PDF from the Read model (`output=pdf`)
- **Figure Extraction**: download detected figures as images from the Layout model (`output=figures`)
- **Batch Analysis**: analyze a whole Azure Blob container in one job, with a recent-jobs list and delete
- **Privacy**: delete a stored analyze response early (otherwise retained 24h)
- Real-time progress indicators
- Comprehensive error handling
- Connection status monitoring
- Future: Auto-mode for intelligent model selection

## Prerequisites

- Python 3.8+
- Azure Document Intelligence resource
- API key and endpoint URL

## Setup

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd azure-di-streamlit-demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure Document Intelligence credentials**

   **Option 1: In-App Configuration (Easiest)**
   - Start the app without credentials
   - Enter your endpoint and API key in the sidebar input boxes
   - Credentials are session-only (not saved)

   **Option 2: Environment Variables**
   ```bash
   export AZURE_DI_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'
   export AZURE_DI_API_KEY='your-api-key-here'
   ```

   **Option 3: .env file**
   ```bash
   cp .env .env.example  # Create example from your .env
   # Edit .env with your actual credentials
   ```

   **Option 4: Streamlit Secrets (for deployment)**
   ```toml
   # .streamlit/secrets.toml
   AZURE_DI_ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"
   AZURE_DI_API_KEY = "your-api-key-here"
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Select a model** from the sidebar dropdown

4. **Configure parameters** based on your needs

5. **Upload a document** using one of three methods:
   - File upload (drag & drop)
   - URL input
   - Sample documents

6. **Analyze the document** by clicking the "🚀 Analyze Document" button

7. **View results** in multiple formats:
   - Fields view with confidence scores
   - Markdown text output
   - Raw JSON response

## Supported File Formats

- **PDF**: Up to 2000 pages, 500MB max
- **Images**: JPG, PNG, BMP, TIFF
- **Size limit**: 500MB (paid tier), 4MB (free tier)
- **Resolution**: 50x50 to 10,000x10,000 pixels

## API Models Overview

| Category | Models | Description |
|----------|--------|-------------|
| **Core Models** | Read OCR, Layout Analysis | Text extraction and document structure |
| **Document Types** | Receipt, Invoice, Business Card, ID Document, Contract | Common business documents |
| **Financial** | Bank Check, Bank Statement, Pay Stub, Credit Card | Financial document processing |
| **Legal** | Marriage Certificate | Legal document extraction |
| **Healthcare** | US Health Insurance Card | Healthcare document processing |
| **US Tax** | W-2, W-4, 1040, 1098, 1099, 1099-SSA, 1095-A, 1095-C | Tax form processing |
| **US Mortgage** | 1003, 1004, 1005, 1008, Closing Disclosure | Mortgage document processing |

## Architecture

```
azure-di-streamlit-demo/
├── app.py                 # Main Streamlit application
├── config.py             # Models and parameters configuration
├── azure_di_client.py    # REST API client
├── ui_components.py      # Reusable UI components
├── document_processor.py # Document handling utilities
├── logging_config.py     # Centralized logging configuration
├── test_client.py        # Client testing script
├── debug_runner.py       # Debug testing with full logging
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── SPEC.md              # Technical specification
├── LOGGING.md           # Logging system documentation
├── CODE_QUALITY.md      # Code quality standards
└── .env.template        # Environment variables template
```

## Configuration Details

### Model Features
Each model supports different features that can be toggled:
- **OCR High Resolution**: Enhanced text extraction
- **Languages**: Language detection
- **Barcodes**: Barcode detection (Layout model)
- **Formulas**: Mathematical formula recognition (Layout model)
- **Key-Value Pairs**: Extract key-value pairs (Layout, Contract models)
- **Style Font**: Font style detection (Layout model)

### API Parameters
- **Pages**: Specify page ranges (e.g., "1-3,5", "1,3,5", "1-")
- **Locale**: Language hints (en-US, fr-FR, de-DE, etc.)
- **String Index Type**: Text element indexing method
- **Output Content Format**: Text or Markdown output
- **Additional Output**: Searchable PDF (Read model) and figure images (Layout model)
- **Query Fields**: comma-separated custom field names to extract (max 20)

## Troubleshooting

### Logging and Debugging

The application includes comprehensive logging with timestamps, module names, function names, and line numbers.

**Enable DEBUG logging:**
```bash
export AZURE_DI_LOG_LEVEL=DEBUG
streamlit run app.py
```

**Or add to .env file:**
```
AZURE_DI_LOG_LEVEL=DEBUG
```

**Debug logging shows:**
- Complete API request/response details
- URL construction and parameters  
- File processing steps
- Error stack traces with exact locations

See [LOGGING.md](LOGGING.md) for complete documentation.

### Connection Issues
- Verify your endpoint URL includes the full path
- Check that your API key is correct and active
- Ensure your Azure resource is in the correct region
- **Check DEBUG logs for exact error details**

### File Upload Issues
- Check file size limits (500MB for paid tier)
- Verify file format is supported
- Ensure good image quality for optimal results

### Analysis Errors
- Try different models for different document types
- Check page range syntax (e.g., "1-3,5")
- Verify document is not corrupted or password-protected
- **Enable DEBUG logging to see API response details**

### "Resource not found" Errors
- Check DEBUG logs for the exact URL being used
- Verify API version compatibility
- Ensure model is available in your region

## Performance Tips

1. **Use appropriate models**: Choose specific models (e.g., receipt model for receipts) for best results
2. **Optimize page selection**: Analyze only necessary pages for large documents
3. **Image quality**: Use high-resolution, clear images for better accuracy
4. **Network**: Ensure stable internet connection for large file uploads

## Future Enhancements

- **Auto Mode**: Intelligent model selection using LLM analysis
- **Custom Models**: Support for custom trained and classification models
- **Enhanced Visualization**: Render barcodes, formulas, and selection marks as bounding boxes
- **Export Options**: Additional output formats (Excel, CSV)

> ✅ **Batch Processing** is now implemented — see the **Batch Analysis** tab.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for demonstration purposes. Please ensure compliance with Azure Document Intelligence terms of service.

## Deployment

### Deploy to Streamlit Community Cloud

Want to share this app with others? Deploy it for free on Streamlit Community Cloud!

See the comprehensive deployment guide: [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)

**Quick Deploy Steps:**
1. Push your code to GitHub (without .env file!)
2. Sign in to [share.streamlit.io](https://share.streamlit.io)
3. Create new app and select your repository
4. Add Azure credentials to Streamlit secrets
5. Deploy and share your app URL!

### What's New

**Version 1.1 Features:**
- ✨ In-app credential configuration (no .env required)
- 📋 Copy JSON to clipboard button
- 🚀 Ready for Streamlit Community Cloud deployment
- 📚 Comprehensive deployment documentation

## Support

For issues related to:
- **Azure Document Intelligence**: Check [Azure documentation](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/)
- **This demo**: Create an issue in the repository
- **Streamlit**: Visit [Streamlit documentation](https://docs.streamlit.io/)
- **Deployment**: See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)

---

Built with ❤️ using [Streamlit](https://streamlit.io/) and [Azure Document Intelligence 4.0](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/) REST API