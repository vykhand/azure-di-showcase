#!/usr/bin/env python3
"""
Simple test script to verify the Azure DI client works correctly.
Run this to test your credentials and API connection.
"""

import os
import logging
from dotenv import load_dotenv
from azure_di_client import AzureDocumentIntelligenceClient

from logging_config import setup_logging, get_logger

# Set up logging for the test
setup_logging('INFO')  # Set to DEBUG to see all debug messages
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

def test_client():
    """Test the Azure DI client with your credentials."""
    
    # Get credentials
    endpoint = os.getenv("AZURE_DI_ENDPOINT")
    api_key = os.getenv("AZURE_DI_API_KEY")
    
    if not endpoint or not api_key:
        logger.error("Missing credentials. Please check your .env file or environment variables:")
        logger.error("   AZURE_DI_ENDPOINT")
        logger.error("   AZURE_DI_API_KEY")
        return False
    
    logger.info(f"Testing connection to: {endpoint}")
    
    # Create client
    client = AzureDocumentIntelligenceClient(endpoint, api_key)
    
    # Test connection
    success, message = client.test_connection()
    
    if success:
        logger.info(f"✅ {message}")
        return True
    else:
        logger.error(f"❌ {message}")
        return False

def test_with_pdf(pdf_path: str):
    """Test analysis with a specific PDF file."""
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return False
    
    # Get credentials
    endpoint = os.getenv("AZURE_DI_ENDPOINT")
    api_key = os.getenv("AZURE_DI_API_KEY")
    
    client = AzureDocumentIntelligenceClient(endpoint, api_key)
    
    logger.info(f"Testing analysis with: {pdf_path}")
    
    # Read PDF file
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    
    logger.debug(f"File size: {len(pdf_data)} bytes")
    
    # Test analysis
    success, result = client.analyze_document_with_polling(
        model_id="prebuilt-layout",
        document_data=pdf_data,
        outputContentFormat="markdown",
        progress_callback=lambda msg: logger.debug(f"Progress: {msg}")
    )
    
    if success:
        logger.info("Analysis successful!")
        
        # Show some results
        analyze_result = result.get("analyzeResult", {})
        content = analyze_result.get("content", "")
        pages = analyze_result.get("pages", [])
        
        logger.info(f"Extracted {len(pages)} pages")
        logger.info(f"Content length: {len(content)} characters")
        
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            logger.debug(f"Content preview:\n{preview}")
            
        return True
    else:
        logger.error(f"Analysis failed: {result}")
        return False

if __name__ == "__main__":
    logger.info("Azure Document Intelligence Client Test")
    
    # Test 1: Connection test
    logger.info("=" * 50)
    logger.info("Test 1: Connection Test")
    logger.info("=" * 50)
    
    if not test_client():
        logger.error("Connection test failed. Please check your credentials.")
        exit(1)
    
    # Test 2: PDF analysis (if PDF path is provided)
    pdf_path = "/Users/vykhand/DEV/av-ai-demos/data/Document_20160111_0001_travel_list.pdf"
    
    if os.path.exists(pdf_path):
        logger.info("=" * 50)
        logger.info("Test 2: PDF Analysis Test")
        logger.info("=" * 50)
        
        if test_with_pdf(pdf_path):
            logger.info("All tests passed! Your client is working correctly.")
        else:
            logger.error("PDF analysis test failed.")
    else:
        logger.warning(f"PDF test skipped (file not found: {pdf_path})")
        logger.info("Connection test passed! Your client should work in the Streamlit app.")