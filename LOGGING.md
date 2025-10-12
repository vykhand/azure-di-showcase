# Logging System Documentation

## Overview
The Azure Document Intelligence demo now uses a comprehensive logging system that provides detailed debugging information with timestamps, module names, function names, and line numbers.

## Log Levels

### DEBUG
Shows all debug messages including:
- URL construction details
- Request/response headers  
- API parameters and responses
- File processing steps
- Internal function flow

### INFO (Default)
Shows important operational information:
- Analysis start/completion
- Connection status
- File uploads
- Major processing steps

### WARNING
Shows potential issues that don't stop execution:
- JSON parsing failures
- File format issues
- Recoverable errors

### ERROR
Shows serious errors:
- API failures
- Authentication issues
- Network problems
- Unrecoverable errors

## Configuration

### Method 1: Environment Variable
```bash
export AZURE_DI_LOG_LEVEL=DEBUG
streamlit run app.py
```

### Method 2: .env File
Add to your `.env` file:
```
AZURE_DI_LOG_LEVEL=DEBUG
```

### Method 3: Script-specific
Each script can set its own level:
```python
from logging_config import setup_logging
setup_logging('DEBUG')
```

## Log Format

All logs follow this format:
```
2024-08-26 17:45:23 - azure_di_client - DEBUG - [azure_di_client.py:analyze_document_sync:84] - Analyze URL: https://...
```

Components:
- **Timestamp**: `2024-08-26 17:45:23`
- **Logger Name**: `azure_di_client`  
- **Level**: `DEBUG`
- **Location**: `[azure_di_client.py:analyze_document_sync:84]`
  - File: `azure_di_client.py`
  - Function: `analyze_document_sync`
  - Line: `84`
- **Message**: The actual log message

## Debugging Workflow

### 1. For General Issues
```bash
export AZURE_DI_LOG_LEVEL=INFO
streamlit run app.py
```
Check for connection and analysis completion messages.

### 2. For API Issues  
```bash
export AZURE_DI_LOG_LEVEL=DEBUG
streamlit run app.py
```
Look for:
- Request URLs and headers
- Response status codes
- Error messages

### 3. For Testing
```bash
export AZURE_DI_LOG_LEVEL=DEBUG
python debug_runner.py
```

### 4. For Quick Tests
```bash
python test_client.py  # Uses INFO level by default
```

## Common Log Messages

### Successful Analysis
```
2024-08-26 17:45:23 - app - INFO - [app.py:handle_document_analysis:141] - Starting document analysis with model: prebuilt-layout
2024-08-26 17:45:24 - azure_di_client - DEBUG - [azure_di_client.py:analyze_document_sync:84] - Analyze URL: https://...
2024-08-26 17:45:24 - azure_di_client - DEBUG - [azure_di_client.py:analyze_document_sync:111] - Response status code: 202
2024-08-26 17:45:25 - azure_di_client - DEBUG - [azure_di_client.py:get_analysis_result_sync:183] - Polling response status: 200
2024-08-26 17:45:26 - app - INFO - [app.py:handle_document_analysis:171] - Document analysis completed successfully
```

### Connection Issues
```
2024-08-26 17:45:23 - azure_di_client - ERROR - [azure_di_client.py:analyze_document_sync:149] - CONNECTION ERROR - Failed to connect to Azure Document Intelligence service
2024-08-26 17:45:23 - azure_di_client - DEBUG - [azure_di_client.py:analyze_document_sync:150] - Connection traceback: ...
```

### API Errors
```
2024-08-26 17:45:24 - azure_di_client - ERROR - [azure_di_client.py:analyze_document_sync:130] - Request failed with status 404
2024-08-26 17:45:24 - azure_di_client - ERROR - [azure_di_client.py:analyze_document_sync:131] - Response text: {"error": "Resource not found"}
```

## File-Specific Logging

### azure_di_client.py
- API request/response details
- URL construction
- Polling status
- Error handling

### app.py  
- Application flow
- User interactions
- Analysis results
- Error display

### test_client.py
- Test execution
- Connection verification
- Analysis testing

### debug_runner.py
- Comprehensive debugging
- Step-by-step analysis
- Full error traces

## Tips for Debugging

1. **Start with INFO level** to see the big picture
2. **Use DEBUG level** when you need details about API calls
3. **Check timestamps** to see where delays occur
4. **Look for ERROR level messages** first when troubleshooting
5. **Use function and line numbers** to pinpoint issues in code
6. **Compare successful vs failed runs** to identify differences

## Production Recommendations

For production or demo environments:
- Use **INFO** level for normal operation
- Use **WARNING** level to reduce noise
- Use **DEBUG** level only for troubleshooting
- Consider log file output instead of console for permanent deployments

## Customization

To add logging to new modules:
```python
from logging_config import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Starting my function")
    logger.debug(f"Processing data: {data}")
    logger.error("Something went wrong")
```

The logging system automatically handles formatting, timestamps, and location information.