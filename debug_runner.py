#!/usr/bin/env python3
"""
Debug runner for testing Azure DI client with full debug output.
This script helps identify exactly where the "Resource not found" error occurs.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from azure_di_client import AzureDocumentIntelligenceClient

from logging_config import setup_logging, get_logger

# Configure logging for maximum debug output
setup_logging('DEBUG')
logger = get_logger(__name__)

def debug_test():
    """Run a comprehensive debug test."""
    
    logger.info("Azure Document Intelligence Debug Test")
    logger.info("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    endpoint = os.getenv("AZURE_DI_ENDPOINT")
    api_key = os.getenv("AZURE_DI_API_KEY")
    
    logger.info("Configuration:")
    logger.info(f"   Endpoint: {endpoint}")
    logger.info(f"   API Key: {'*' * (len(api_key) - 8) + api_key[-8:] if api_key and len(api_key) > 8 else 'NOT SET'}")
    
    if not endpoint or not api_key:
        logger.error("Missing credentials!")
        logger.error("Please set AZURE_DI_ENDPOINT and AZURE_DI_API_KEY in your environment or .env file")
        return False
    
    # Create client
    logger.info("Creating client...")
    client = AzureDocumentIntelligenceClient(endpoint, api_key)
    
    # Test 1: Connection test
    logger.info("Test 1: Connection Test")
    logger.info("-" * 30)
    success, message = client.test_connection()
    logger.info(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    logger.info(f"Message: {message}")
    
    if not success:
        logger.error("Connection test failed. Check the debug output above for details.")
        return False
    
    # Test 2: Simple analysis with minimal data
    logger.info("Test 2: Minimal Document Analysis")
    logger.info("-" * 40)
    
    # Create a minimal PDF for testing
    minimal_pdf = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n189\n%%EOF'
    
    logger.info(f"   Using minimal test PDF ({len(minimal_pdf)} bytes)")
    logger.info("   Model: prebuilt-layout")
    
    success, result = client.analyze_document_sync(
        model_id="prebuilt-layout",
        document_data=minimal_pdf
    )
    
    logger.info(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    if success:
        logger.info(f"Operation ID: {result}")
    else:
        logger.error(f"Error: {result}")
    
    if not success:
        logger.error("Analysis request failed. Check the debug output above.")
        return False
    
    logger.info("All tests passed!")
    logger.info("If the Streamlit app still fails:")
    logger.info("   1. Compare the debug output from the app with this script")
    logger.info("   2. Look for differences in URLs, headers, or parameters")
    logger.info("   3. Check that file reading in the app works correctly")
    
    return True

if __name__ == "__main__":
    try:
        debug_test()
    except Exception as e:
        logger.error(f"Debug test crashed: {e}")
        import traceback
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        sys.exit(1)