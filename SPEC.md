# Azure Document Intelligence 4.0 Streamlit Demo - Technical Specification

## Overview
A comprehensive Streamlit application demonstrating all capabilities of Azure Document Intelligence 4.0 through REST API integration. The application provides an intuitive interface similar to Azure DI Studio for document analysis, extraction, and visualization.

## Architecture

### Core Components
```
azure-di-streamlit-demo/
├── app.py                 # Main Streamlit application
├── config.py             # Azure DI models and parameters configuration
├── azure_di_client.py    # REST API client for Azure Document Intelligence
├── ui_components.py      # Reusable Streamlit UI components
├── document_processor.py # Document handling and processing utilities
├── requirements.txt      # Python dependencies
└── SPEC.md              # This specification document
```

## Functional Requirements

### 1. Model Selection and Configuration

#### 1.1 Supported Models
The application must support all Azure Document Intelligence 4.0 prebuilt models:

**Core Models:**
- `prebuilt-read` - OCR and text extraction
- `prebuilt-layout` - Document structure analysis with tables, paragraphs, headers

**Document Type Models:**
- `prebuilt-receipt` - Receipt processing
- `prebuilt-invoice` - Invoice processing
- `prebuilt-businessCard` - Business card extraction
- `prebuilt-idDocument` - ID document processing
- `prebuilt-contract` - Contract analysis
- `prebuilt-bankCheck` - Bank check processing
- `prebuilt-bankStatement` - Bank statement analysis
- `prebuilt-payStub` - Pay stub extraction
- `prebuilt-marriageCertificate` - Marriage certificate processing
- `prebuilt-creditCard` - Credit card information extraction

**US Tax Documents:**
- `prebuilt-tax.us.w2` - W-2 tax forms
- `prebuilt-tax.us.w4` - W-4 tax forms
- `prebuilt-tax.us.1040` - 1040 tax forms
- `prebuilt-tax.us.1098` - 1098 tax forms
- `prebuilt-tax.us.1099` - 1099 tax forms (base form and variations)
- `prebuilt-tax.us.1099SSA` - 1099-SSA Social Security benefit statements
- `prebuilt-tax.us.1095A` - 1095-A Health Insurance Marketplace statements
- `prebuilt-tax.us.1095C` - 1095-C employer-provided health insurance forms

**US Mortgage Documents:**
- `prebuilt-mortgage.us.1003` - Uniform Residential Loan Application
- `prebuilt-mortgage.us.1004` - Uniform Residential Appraisal Report
- `prebuilt-mortgage.us.1005` - Verification of Employment
- `prebuilt-mortgage.us.1008` - Summary Document
- `prebuilt-mortgage.us.closingDisclosure` - Closing Disclosure

**Healthcare:**
- `prebuilt-healthInsuranceCard.us` - US Health Insurance Cards

#### 1.2 Dynamic Parameter Configuration
For each selected model, the sidebar must dynamically generate UI controls for all applicable API parameters:

**Universal Parameters:**
- `pages` (text input) - Page range specification (e.g., "1-3,5,7-9")
- `locale` (selectbox) - Language locale (en-US, fr-FR, de-DE, etc.)
- `stringIndexType` (selectbox) - textElements, unicodeCodePoint, utf16CodeUnit
- `outputContentFormat` (selectbox) - text, markdown

**Feature Toggles:**
- `features` (multiselect) - Available features based on model:
  - ocrHighResolution
  - languages
  - barcodes
  - formulas
  - keyValuePairs (layout model)
  - styleFont (layout model)
  - queryFields

**Output Options:** (the API `output` parameter only accepts `pdf` and `figures`, each valid for specific models)
- `output` (multiselect) - Additional outputs:
  - pdf — searchable PDF, Read model only; retrieved via `analyzeResults/{resultId}/pdf`
  - figures — figure images, Layout model only; retrieved via `analyzeResults/{resultId}/figures/{figureId}`

**Query Fields:** (add-on; supported by Layout and prebuilt models except tax W-2/1098/1099)
- `queryFields` (text input) — comma-separated custom field names (max 20); also sets `features=queryFields`

### 2. Document Upload and Processing

#### 2.1 File Support
Support all Azure DI compatible formats:
- **Images**: PNG, JPG, JPEG, BMP, TIFF
- **Documents**: PDF (up to 2000 pages)
- **Size limits**: 500 MB (paid tier), 4 MB (free tier)
- **Resolution**: 50x50 to 10,000x10,000 pixels

#### 2.2 Upload Methods
- File uploader widget for local files
- URL input for remote documents
- Drag & drop interface
- Sample document gallery

### 3. User Interface Layout

#### 3.1 Sidebar Configuration
```
┌─────────────────────────┐
│ Model Selection         │
│ ┌─────────────────────┐ │
│ │ [Dropdown Menu]     │ │
│ └─────────────────────┘ │
│                         │
│ Model Parameters        │
│ ┌─────────────────────┐ │
│ │ Pages: [_________]  │ │
│ │ Locale: [_______]   │ │
│ │ Features:           │ │
│ │ □ OCR High Res      │ │
│ │ □ Languages         │ │
│ │ □ Barcodes         │ │
│ │ └─────────────────┘ │ │
│                         │
│ Advanced Options        │
│ ┌─────────────────────┐ │
│ │ String Index Type   │ │
│ │ Output Format       │ │
│ │ Additional Output   │ │
│ └─────────────────────┘ │
│                         │
│ Future: Auto Mode       │
│ ┌─────────────────────┐ │
│ │ □ Auto Model Select │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

#### 3.2 Main Area Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Document Upload                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Drag & Drop     │ │ Browse Files    │ │ Enter URL       │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Document Viewer (Annotated)                             │ │
│ │                                                         │ │
│ │ [Document with bounding boxes and highlights]           │ │
│ │                                                         │ │
│ │ Navigation: ◀ Page 1 of 3 ▶                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Results Tabs                                                │
│ ┌─────────────────┬─────────────────┬─────────────────────┐ │
│ │ Fields | Result │ Markdown        │ Raw JSON            │ │
│ └─────────────────┴─────────────────┴─────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Results Content Area                                    │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 4. Document Visualization

#### 4.1 Annotated Document Display
- **Overlay System**: Bounding boxes for detected elements
- **Color Coding**: Different colors for different field types
- **Interactive Elements**: Click to highlight corresponding results
- **Zoom Controls**: Pan and zoom functionality
- **Multi-page Support**: Navigation for multi-page documents

#### 4.2 Element Types and Colors
- **Text Lines**: Blue (#007ACC)
- **Tables**: Green (#00B04F)
- **Key-Value Pairs**: Orange (#FF8C00)
- **Selection Marks**: Purple (#8A2BE2)
- **Figures**: Red (#DC143C)
- **Headers/Titles**: Dark Blue (#000080)

### 5. Results Display

#### 5.1 Fields View (Similar to Azure DI Studio)
- **Hierarchical Display**: Expandable tree structure
- **Confidence Scores**: Visual indicators (color-coded bars)
- **Field Details**: Content, bounding box coordinates, confidence
- **Search/Filter**: Find specific fields quickly

#### 5.2 Markdown Output
- **Formatted Text**: Clean markdown representation
- **Table Preservation**: Maintain table structure
- **Copy Functionality**: One-click copy to clipboard

#### 5.3 Raw JSON View
- **Syntax Highlighting**: Colored JSON display
- **Collapsible Sections**: Expand/collapse JSON objects
- **Copy/Download**: Export JSON results
- **Search**: Find specific keys or values

### 6. Azure Document Intelligence REST API Integration

#### 6.1 API Client Implementation
```python
class AzureDocumentIntelligenceClient:
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = "2024-11-30"
        
    async def analyze_document(
        self, 
        model_id: str,
        document: Union[bytes, str],
        **kwargs
    ) -> dict:
        """Analyze document using specified model"""
        
    async def get_analysis_result(self, operation_id: str) -> dict:
        """Poll for analysis results"""
        
    def get_model_info(self, model_id: str) -> dict:
        """Get model capabilities and supported features"""
```

#### 6.2 API Endpoints
- **Analyze Document**: `POST {endpoint}/documentintelligence/documentModels/{modelId}:analyze`
- **Get Result**: `GET {endpoint}/documentintelligence/documentModels/{modelId}/analyzeResults/{resultId}`
- **Delete Result** (GDPR): `DELETE {endpoint}/documentintelligence/documentModels/{modelId}/analyzeResults/{resultId}`
- **Searchable PDF**: `GET .../analyzeResults/{resultId}/pdf`
- **Figure image**: `GET .../analyzeResults/{resultId}/figures/{figureId}`
- **List Models**: `GET {endpoint}/documentintelligence/documentModels`
- **Batch Analyze**: `POST {endpoint}/documentintelligence/documentModels/{modelId}:analyzeBatch` (body: `azureBlobSource`, `resultContainerUrl`, `resultPrefix`, `overwriteExisting`)
- **List Batch Jobs** (past 7 days): `GET .../documentModels/{modelId}/analyzeBatchResults`
- **Delete Batch Job**: `DELETE .../documentModels/{modelId}/analyzeBatchResults/{resultId}`

#### 6.3 Error Handling
- **Authentication Errors**: Invalid API key handling
- **Rate Limiting**: Exponential backoff retry logic
- **Document Errors**: Invalid format, size exceeded
- **Model Errors**: Unsupported model, invalid parameters

### 7. Configuration Management

#### 7.1 Model Definitions
```python
AZURE_DI_MODELS = {
    "prebuilt-layout": {
        "name": "Layout Analysis",
        "description": "Extract text, tables, and document structure",
        "features": ["ocrHighResolution", "languages", "barcodes", "formulas", "keyValuePairs", "styleFont"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 2000
    },
    "prebuilt-receipt": {
        "name": "Receipt Processing",
        "description": "Extract key information from receipts",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1
    },
    # ... additional models
}
```

#### 7.2 Parameter Definitions
```python
API_PARAMETERS = {
    "pages": {
        "type": "text_input",
        "label": "Pages",
        "help": "Page range (e.g., 1-3,5,7-9)",
        "default": ""
    },
    "locale": {
        "type": "selectbox",
        "label": "Locale",
        "options": ["", "en-US", "fr-FR", "de-DE", "es-ES"],
        "default": ""
    },
    # ... additional parameters
}
```

### 8. Advanced Features

#### 8.1 Future Auto Mode
- **LLM Integration**: Placeholder for automatic model selection
- **Document Classification**: Analyze document type automatically
- **Optimal Parameters**: Suggest best parameters for document type

#### 8.2 Performance Optimization
- **Async Processing**: Non-blocking document analysis
- **Caching**: Cache model information and results
- **Progress Indicators**: Real-time processing status

#### 8.3 Export Capabilities
- **Download Results**: JSON, CSV, Markdown formats
- **Print View**: Optimized document display for printing
- **Share Results**: Generate shareable links (future)

## Technical Requirements

### 8.1 Dependencies
```txt
streamlit>=1.28.0
aiohttp>=3.8.5
asyncio>=3.4.3
Pillow>=10.0.0
pandas>=2.0.3
plotly>=5.15.0
streamlit-ace>=0.1.1
streamlit-aggrid>=0.3.4
python-dotenv>=1.0.0
requests>=2.31.0
base64
json
io
typing
```

### 8.2 Environment Configuration
```bash
# Required environment variables
AZURE_DI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DI_API_KEY=your-api-key-here
```

### 8.3 Deployment
- **Local Development**: `streamlit run app.py`
- **Container Support**: Docker configuration
- **Cloud Deployment**: Azure Container Instances, Streamlit Cloud

## Security Considerations

### 9.1 API Key Management
- Environment variables for sensitive data
- No hardcoded credentials
- Key rotation support

### 9.2 Document Handling
- Secure file upload validation
- Temporary file cleanup
- No persistent document storage

### 9.3 Error Information
- Sanitized error messages
- No credential leakage in logs
- User-friendly error display

## Testing Strategy

### 10.1 Document Types
- Various receipt formats
- Multi-page PDFs
- Different image qualities
- Non-English documents
- Edge cases (corrupted files, unsupported formats)

### 10.2 Model Coverage
- Test all prebuilt models
- Parameter combinations
- Feature toggle validation
- Error scenarios

### 10.3 UI Testing
- Responsive design validation
- Cross-browser compatibility
- Accessibility compliance
- Performance under load

## Success Metrics

### 11.1 Functionality
- All Azure DI 4.0 models supported
- Parameter configuration working correctly
- Results display accurate and complete
- Error handling graceful

### 11.2 User Experience
- Intuitive interface similar to Azure DI Studio
- Fast response times (<3 seconds for UI updates)
- Clear progress indicators
- Helpful error messages

### 11.3 Code Quality
- Modular architecture
- Comprehensive error handling
- Clear documentation
- Maintainable codebase

This specification provides a comprehensive blueprint for building a production-ready Azure Document Intelligence 4.0 Streamlit demo that showcases all platform capabilities through an intuitive, Studio-like interface.