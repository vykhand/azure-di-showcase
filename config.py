"""
Configuration for Azure Document Intelligence 4.0 models and parameters.
"""

from typing import Dict, List, Any

# Azure Document Intelligence API Configuration
AZURE_DI_API_VERSION = "2024-11-30"

# All supported Azure Document Intelligence 4.0 models
AZURE_DI_MODELS = {
    "prebuilt-read": {
        "name": "Read OCR",
        "description": "Extract text and layout information from documents",
        "category": "Core Models",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 2000,
        "icon": "📖"
    },
    "prebuilt-layout": {
        "name": "Layout Analysis",
        "description": "Extract text, tables, selection marks, and document structure",
        "category": "Core Models",
        "features": ["ocrHighResolution", "languages", "barcodes", "formulas", "keyValuePairs", "styleFont"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 2000,
        "icon": "📋"
    },
    "prebuilt-receipt": {
        "name": "Receipt",
        "description": "Extract key information from sales receipts",
        "category": "Document Types",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "🧾"
    },
    "prebuilt-invoice": {
        "name": "Invoice",
        "description": "Extract key information from invoices",
        "category": "Document Types",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 50,
        "icon": "📄"
    },
    "prebuilt-businessCard": {
        "name": "Business Card",
        "description": "Extract contact information from business cards",
        "category": "Document Types",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "💳"
    },
    "prebuilt-idDocument": {
        "name": "ID Document",
        "description": "Extract information from identity documents",
        "category": "Document Types",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "🆔"
    },
    "prebuilt-contract": {
        "name": "Contract",
        "description": "Extract key information from contracts",
        "category": "Document Types",
        "features": ["ocrHighResolution", "languages", "keyValuePairs"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 2000,
        "icon": "📜"
    },
    "prebuilt-bankCheck": {
        "name": "Bank Check",
        "description": "Extract information from bank checks",
        "category": "Financial Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "🏦"
    },
    "prebuilt-bankStatement": {
        "name": "Bank Statement",
        "description": "Extract information from bank statements",
        "category": "Financial Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 2000,
        "icon": "📊"
    },
    "prebuilt-payStub": {
        "name": "Pay Stub",
        "description": "Extract information from pay stubs",
        "category": "Financial Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "💰"
    },
    "prebuilt-marriageCertificate": {
        "name": "Marriage Certificate",
        "description": "Extract information from marriage certificates",
        "category": "Legal Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "💒"
    },
    "prebuilt-creditCard": {
        "name": "Credit Card",
        "description": "Extract information from credit cards",
        "category": "Financial Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "💳"
    },
    "prebuilt-healthInsuranceCard.us": {
        "name": "US Health Insurance Card",
        "description": "Extract information from US health insurance cards",
        "category": "Healthcare Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 1,
        "icon": "🏥"
    },
    # US Tax Documents
    "prebuilt-tax.us.w2": {
        "name": "US W-2",
        "description": "Extract information from W-2 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "📋"
    },
    "prebuilt-tax.us.w4": {
        "name": "US W-4",
        "description": "Extract information from W-4 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "📋"
    },
    "prebuilt-tax.us.1040": {
        "name": "US 1040",
        "description": "Extract information from 1040 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 50,
        "icon": "📋"
    },
    "prebuilt-tax.us.1098": {
        "name": "US 1098",
        "description": "Extract information from 1098 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "📋"
    },
    "prebuilt-tax.us.1099": {
        "name": "US 1099",
        "description": "Extract information from 1099 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "📋"
    },
    "prebuilt-tax.us.1095": {
        "name": "US 1095",
        "description": "Extract information from 1095 tax forms",
        "category": "US Tax Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "📋"
    },
    # US Mortgage Documents
    "prebuilt-mortgage.us.1003": {
        "name": "US 1003 (Loan Application)",
        "description": "Extract information from Uniform Residential Loan Application",
        "category": "US Mortgage Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 50,
        "icon": "🏠"
    },
    "prebuilt-mortgage.us.1004": {
        "name": "US 1004 (Appraisal Report)",
        "description": "Extract information from Uniform Residential Appraisal Report",
        "category": "US Mortgage Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 50,
        "icon": "🏠"
    },
    "prebuilt-mortgage.us.1005": {
        "name": "US 1005 (Employment Verification)",
        "description": "Extract information from Verification of Employment",
        "category": "US Mortgage Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "🏠"
    },
    "prebuilt-mortgage.us.1008": {
        "name": "US 1008 (Summary Document)",
        "description": "Extract information from Summary Document",
        "category": "US Mortgage Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "🏠"
    },
    "prebuilt-mortgage.us.closingDisclosure": {
        "name": "US Closing Disclosure",
        "description": "Extract information from Closing Disclosure forms",
        "category": "US Mortgage Documents",
        "features": ["ocrHighResolution", "languages"],
        "supported_formats": ["pdf", "jpg", "png", "bmp", "tiff"],
        "max_pages": 10,
        "icon": "🏠"
    }
}

# API Parameters configuration
API_PARAMETERS = {
    "pages": {
        "type": "text_input",
        "label": "Pages",
        "help": "Page range to analyze (e.g., '1-3,5,7-9' or '1,3,5'). Leave empty to analyze all pages.",
        "default": "",
        "placeholder": "e.g., 1-3,5,7-9"
    },
    "locale": {
        "type": "selectbox",
        "label": "Locale",
        "help": "Language hint for text recognition and analysis",
        "options": [
            ("Auto-detect", ""),
            ("English (US)", "en-US"),
            ("English (GB)", "en-GB"),
            ("French", "fr-FR"),
            ("German", "de-DE"),
            ("Spanish", "es-ES"),
            ("Italian", "it-IT"),
            ("Portuguese", "pt-PT"),
            ("Dutch", "nl-NL"),
            ("Japanese", "ja-JP"),
            ("Korean", "ko-KR"),
            ("Chinese (Simplified)", "zh-Hans"),
            ("Chinese (Traditional)", "zh-Hant")
        ],
        "default": ""
    },
    "stringIndexType": {
        "type": "selectbox",
        "label": "String Index Type",
        "help": "Method for computing string offsets and lengths",
        "options": [
            ("Text Elements (Default)", "textElements"),
            ("Unicode Code Points", "unicodeCodePoint"),
            ("UTF-16 Code Units", "utf16CodeUnit")
        ],
        "default": "textElements"
    },
    "outputContentFormat": {
        "type": "selectbox",
        "label": "Output Content Format",
        "help": "Format of the content in the analysis result",
        "options": [
            ("Text", "text"),
            ("Markdown", "markdown")
        ],
        "default": "text"
    }
}

# Available features for different models
AVAILABLE_FEATURES = {
    "ocrHighResolution": {
        "label": "OCR High Resolution",
        "description": "Enable high-resolution OCR for better text extraction",
        "models": ["prebuilt-read", "prebuilt-layout", "prebuilt-receipt", "prebuilt-invoice", 
                  "prebuilt-businessCard", "prebuilt-idDocument", "prebuilt-contract",
                  "prebuilt-bankCheck", "prebuilt-bankStatement", "prebuilt-payStub",
                  "prebuilt-marriageCertificate", "prebuilt-creditCard", "prebuilt-healthInsuranceCard.us",
                  "prebuilt-tax.us.w2", "prebuilt-tax.us.w4", "prebuilt-tax.us.1040",
                  "prebuilt-tax.us.1098", "prebuilt-tax.us.1099", "prebuilt-tax.us.1095",
                  "prebuilt-mortgage.us.1003", "prebuilt-mortgage.us.1004", "prebuilt-mortgage.us.1005",
                  "prebuilt-mortgage.us.1008", "prebuilt-mortgage.us.closingDisclosure"]
    },
    "languages": {
        "label": "Language Detection",
        "description": "Detect and identify languages in the document",
        "models": ["prebuilt-read", "prebuilt-layout", "prebuilt-receipt", "prebuilt-invoice",
                  "prebuilt-businessCard", "prebuilt-idDocument", "prebuilt-contract",
                  "prebuilt-bankCheck", "prebuilt-bankStatement", "prebuilt-payStub",
                  "prebuilt-marriageCertificate", "prebuilt-creditCard", "prebuilt-healthInsuranceCard.us",
                  "prebuilt-tax.us.w2", "prebuilt-tax.us.w4", "prebuilt-tax.us.1040",
                  "prebuilt-tax.us.1098", "prebuilt-tax.us.1099", "prebuilt-tax.us.1095",
                  "prebuilt-mortgage.us.1003", "prebuilt-mortgage.us.1004", "prebuilt-mortgage.us.1005",
                  "prebuilt-mortgage.us.1008", "prebuilt-mortgage.us.closingDisclosure"]
    },
    "barcodes": {
        "label": "Barcode Detection",
        "description": "Detect and extract barcode information",
        "models": ["prebuilt-layout"]
    },
    "formulas": {
        "label": "Formula Recognition",
        "description": "Recognize and extract mathematical formulas",
        "models": ["prebuilt-layout"]
    },
    "keyValuePairs": {
        "label": "Key-Value Pairs",
        "description": "Extract key-value pairs from documents",
        "models": ["prebuilt-layout", "prebuilt-contract"]
    },
    "styleFont": {
        "label": "Font Style Detection",
        "description": "Detect font styles and formatting",
        "models": ["prebuilt-layout"]
    }
}

# Additional output options
OUTPUT_OPTIONS = {
    "pdf": {
        "label": "PDF Output",
        "description": "Generate annotated PDF with bounding boxes"
    },
    "figures": {
        "label": "Extract Figures",
        "description": "Extract figures and images from the document"
    },
    "cropped": {
        "label": "Cropped Images",
        "description": "Generate cropped images of detected elements"
    }
}

# Model categories for organization
MODEL_CATEGORIES = [
    "Core Models",
    "Document Types", 
    "Financial Documents",
    "Legal Documents",
    "Healthcare Documents",
    "US Tax Documents",
    "US Mortgage Documents"
]

# Color coding for visualization
ELEMENT_COLORS = {
    "text": "#007ACC",          # Blue
    "tables": "#00B04F",      # Green  
    "table": "#00B04F",       # Green (alias)
    "paragraphs": "#9932CC",  # Dark Orchid
    "paragraph": "#9932CC",   # Dark Orchid (alias)
    "figures": "#DC143C",     # Crimson Red
    "figure": "#DC143C",      # Crimson Red (alias)
    "keyValuePairs": "#FF8C00", # Orange
    "keyValuePair": "#FF8C00", # Orange (alias)
    "selectionMarks": "#8A2BE2", # Purple
    "selectionMark": "#8A2BE2", # Purple (alias)
    "header": "#000080",     # Dark Blue
    "title": "#4B0082",      # Indigo
    "sectionHeader": "#2F4F4F", # Dark Slate Gray
    "pageNumber": "#A0A0A0",  # Gray
    "footnote": "#808080"     # Gray
}

# File format support
SUPPORTED_FORMATS = {
    "pdf": {
        "extensions": [".pdf"],
        "mime_types": ["application/pdf"],
        "max_size_mb": 500,
        "description": "Portable Document Format"
    },
    "jpg": {
        "extensions": [".jpg", ".jpeg"],
        "mime_types": ["image/jpeg"],
        "max_size_mb": 500,
        "description": "JPEG Image"
    },
    "png": {
        "extensions": [".png"],
        "mime_types": ["image/png"],
        "max_size_mb": 500,
        "description": "PNG Image"
    },
    "bmp": {
        "extensions": [".bmp"],
        "mime_types": ["image/bmp"],
        "max_size_mb": 500,
        "description": "Bitmap Image"
    },
    "tiff": {
        "extensions": [".tiff", ".tif"],
        "mime_types": ["image/tiff"],
        "max_size_mb": 500,
        "description": "TIFF Image"
    }
}

def get_model_features(model_id: str) -> List[str]:
    """Get available features for a specific model."""
    if model_id not in AZURE_DI_MODELS:
        return []
    return AZURE_DI_MODELS[model_id].get("features", [])

def get_models_by_category() -> Dict[str, List[str]]:
    """Get models organized by category."""
    categorized = {}
    for model_id, model_info in AZURE_DI_MODELS.items():
        category = model_info.get("category", "Other")
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(model_id)
    return categorized

def is_feature_available(model_id: str, feature: str) -> bool:
    """Check if a feature is available for a specific model."""
    if feature not in AVAILABLE_FEATURES:
        return False
    return model_id in AVAILABLE_FEATURES[feature]["models"]

def get_model_display_name(model_id: str) -> str:
    """Get the display name for a model."""
    if model_id in AZURE_DI_MODELS:
        icon = AZURE_DI_MODELS[model_id].get("icon", "")
        name = AZURE_DI_MODELS[model_id]["name"]
        return f"{icon} {name}" if icon else name
    return model_id