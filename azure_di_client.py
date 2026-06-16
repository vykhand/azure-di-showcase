"""
Azure Document Intelligence REST API Client for version 4.0.
Handles all API interactions including document analysis, polling, and error handling.
"""

import asyncio
import base64
import json
import time
import traceback
import logging
import inspect
from collections import Counter
from typing import Dict, Any, Optional, Union, Tuple
from io import BytesIO

import aiohttp
import requests
import streamlit as st

from config import AZURE_DI_API_VERSION

from logging_config import get_logger

logger = get_logger(__name__)


class AzureDocumentIntelligenceClient:
    """Client for Azure Document Intelligence REST API v4.0."""
    
    def __init__(self, endpoint: str, api_key: str):
        """
        Initialize the Azure Document Intelligence client.
        
        Args:
            endpoint: Azure Document Intelligence endpoint URL
            api_key: API key for authentication
        """
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.api_version = AZURE_DI_API_VERSION
        self.base_url = f"{self.endpoint}/documentintelligence"
        # Operation-Location of the most recent analyze request, used to fetch
        # generated artifacts (searchable PDF, figure images) by resultId.
        self.last_operation_location: Optional[str] = None
        
    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": content_type
        }
    
    def _build_analyze_url(self, model_id: str, **params) -> str:
        """Build the analyze document URL with parameters."""
        base_url = f"{self.base_url}/documentModels/{model_id}:analyze"
        query_params = [f"api-version={self.api_version}"]
        
        # Add optional parameters
        for param, value in params.items():
            if value:  # Only add non-empty values
                if isinstance(value, list):
                    # Handle list parameters (like features)
                    if value:
                        query_params.append(f"{param}={','.join(value)}")
                else:
                    query_params.append(f"{param}={value}")
        
        if query_params:
            return f"{base_url}?{'&'.join(query_params)}"
        return base_url
    
    def analyze_document_sync(
        self, 
        model_id: str, 
        document_data: bytes,
        **kwargs
    ) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        """
        Start document analysis (synchronous version).
        
        Args:
            model_id: Azure DI model ID
            document_data: Document bytes
            **kwargs: Additional API parameters
            
        Returns:
            Tuple of (success: bool, result: operation_id or error_dict)
        """
        try:
            url = self._build_analyze_url(model_id, **kwargs)
            
            # Debug logging
            logger.debug(f"Analyze URL: {url}")
            logger.debug(f"Model ID: {model_id}")
            logger.debug(f"Document size: {len(document_data)} bytes")
            logger.debug(f"Endpoint: {self.endpoint}")
            logger.debug(f"API Version: {self.api_version}")
            logger.debug(f"Parameters: {kwargs}")
            
            # Determine content type based on document data
            content_type = "application/octet-stream"  # Default for binary data
            if document_data.startswith(b'%PDF'):
                content_type = "application/pdf"
            elif document_data.startswith(b'\xff\xd8\xff'):
                content_type = "image/jpeg"
            elif document_data.startswith(b'\x89PNG'):
                content_type = "image/png"
            elif document_data.startswith(b'BM'):
                content_type = "image/bmp"
            elif document_data.startswith(b'II*\x00') or document_data.startswith(b'MM\x00*'):
                content_type = "image/tiff"
            
            logger.debug(f"Detected content type: {content_type}")
            
            # Use the same approach as the working example - send raw binary data
            headers = self._get_headers(content_type)
            logger.debug(f"Request headers: {headers}")
            
            logger.debug("Sending POST request...")
            response = requests.post(url, headers=headers, data=document_data, timeout=60)
            
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 202:
                # Extract operation ID from the Operation-Location header
                operation_location = response.headers.get('Operation-Location')
                logger.debug(f"Operation-Location header: {operation_location}")
                
                if operation_location:
                    # Store the complete operation location URL for polling
                    # We should use this exact URL for polling, not construct our own
                    logger.debug(f"Will use Operation-Location URL for polling: {operation_location}")
                    self.last_operation_location = operation_location
                    return True, operation_location
                else:
                    error_msg = "No Operation-Location header in response"
                    logger.error(f"No Operation-Location header: {error_msg}")
                    return False, {"error": error_msg}
            else:
                logger.error(f"Request failed with status {response.status_code}")
                logger.error(f"Response text: {response.text}")
                
                try:
                    error_data = response.json()
                    logger.debug(f"Parsed error data: {error_data}")
                    return False, error_data
                except Exception as json_error:
                    logger.warning(f"Failed to parse error JSON: {json_error}")
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"Final error message: {error_msg}")
                    return False, {"error": error_msg}
                    
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out: {str(e)}"
            logger.error(f"TIMEOUT ERROR - {error_msg}")
            logger.debug(f"Timeout traceback:\n{traceback.format_exc()}")
            return False, {"error": error_msg}
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(f"CONNECTION ERROR - {error_msg}")
            logger.debug(f"Connection traceback:\n{traceback.format_exc()}")
            return False, {"error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Request exception: {str(e)}"
            logger.error(f"REQUEST ERROR - {error_msg}")
            logger.debug(f"Request traceback:\n{traceback.format_exc()}")
            return False, {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in analyze_document_sync: {str(e)}"
            logger.error(f"UNEXPECTED ERROR - {error_msg}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            return False, {"error": error_msg, "traceback": traceback.format_exc()}
    
    def get_analysis_result_sync(self, operation_location: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get analysis result (synchronous version).
        
        Args:
            operation_location: Complete operation location URL from analyze request
            
        Returns:
            Tuple of (success: bool, result: analysis_result or error_dict)
        """
        try:
            # Use the exact URL provided in Operation-Location header
            url = operation_location
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            
            logger.debug(f"Polling URL: {url}")
            logger.debug(f"Operation Location: {operation_location}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            logger.debug(f"Polling response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Polling result status: {result.get('status', 'unknown')}")
                return True, result
            else:
                logger.error(f"Polling failed with status {response.status_code}")
                logger.error(f"Polling response text: {response.text}")
                
                try:
                    error_data = response.json()
                    logger.debug(f"Polling error data: {error_data}")
                    return False, error_data
                except Exception as json_error:
                    logger.warning(f"Failed to parse polling error JSON: {json_error}")
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    return False, {"error": error_msg}
                    
        except requests.exceptions.Timeout:
            return False, {"error": "Request timed out. Please try again or check your internet connection."}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Failed to connect to Azure Document Intelligence service. Please check your endpoint URL and internet connection."}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def _split_operation_location(operation_location: str) -> Tuple[str, str]:
        """Split an Operation-Location URL into its base (no query) and query string.

        The base looks like
        ``{endpoint}/documentintelligence/documentModels/{modelId}/analyzeResults/{resultId}``
        which is the prefix used to fetch generated artifacts (pdf, figures).
        """
        if '?' in operation_location:
            base, query = operation_location.split('?', 1)
        else:
            base, query = operation_location, f"api-version={AZURE_DI_API_VERSION}"
        return base.rstrip('/'), query

    def get_pdf_result(self, operation_location: str) -> Tuple[bool, Union[bytes, Dict[str, Any]]]:
        """Retrieve the generated searchable PDF for a completed analysis.

        Only available when the analyze request was made with ``output=pdf``
        (Read model). Returns the raw PDF bytes on success.
        """
        try:
            base, query = self._split_operation_location(operation_location)
            url = f"{base}/pdf?{query}"
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Accept": "application/pdf"
            }

            logger.debug(f"Fetching searchable PDF: {url}")
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == 200:
                return True, response.content
            else:
                logger.error(f"PDF retrieval failed with status {response.status_code}: {response.text}")
                try:
                    return False, response.json()
                except Exception:
                    return False, {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"PDF retrieval network error: {str(e)}")
            return False, {"error": f"Network error retrieving PDF: {str(e)}"}
        except Exception as e:
            logger.error(f"PDF retrieval unexpected error: {str(e)}")
            return False, {"error": f"Unexpected error retrieving PDF: {str(e)}"}

    def get_figure(self, operation_location: str, figure_id: str) -> Tuple[bool, Union[bytes, Dict[str, Any]]]:
        """Retrieve a detected figure image for a completed analysis.

        Only available when the analyze request was made with ``output=figures``
        (Layout model). Returns the raw image bytes on success.
        """
        try:
            base, query = self._split_operation_location(operation_location)
            url = f"{base}/figures/{figure_id}?{query}"
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Accept": "image/png"
            }

            logger.debug(f"Fetching figure '{figure_id}': {url}")
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == 200:
                return True, response.content
            else:
                logger.error(f"Figure retrieval failed with status {response.status_code}: {response.text}")
                try:
                    return False, response.json()
                except Exception:
                    return False, {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Figure retrieval network error: {str(e)}")
            return False, {"error": f"Network error retrieving figure: {str(e)}"}
        except Exception as e:
            logger.error(f"Figure retrieval unexpected error: {str(e)}")
            return False, {"error": f"Unexpected error retrieving figure: {str(e)}"}

    def analyze_document_with_polling(
        self,
        model_id: str,
        document_data: bytes,
        progress_callback=None,
        **kwargs
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Analyze document and poll for results.
        
        Args:
            model_id: Azure DI model ID
            document_data: Document bytes
            progress_callback: Optional callback for progress updates
            **kwargs: Additional API parameters
            
        Returns:
            Tuple of (success: bool, result: analysis_result or error_dict)
        """
        # Start analysis
        success, result = self.analyze_document_sync(model_id, document_data, **kwargs)
        
        if not success:
            return False, result
        
        operation_location = result
        
        if progress_callback:
            progress_callback("Analysis started, waiting for results...")
        
        # Poll for results
        max_attempts = 120  # 2 minutes with 1-second intervals
        attempt = 0
        
        while attempt < max_attempts:
            success, result = self.get_analysis_result_sync(operation_location)
            
            if not success:
                return False, result
            
            status = result.get('status', '').lower()
            
            if status == 'succeeded':
                if progress_callback:
                    progress_callback("Analysis completed successfully!")
                return True, result
            elif status == 'failed':
                error_info = result.get('error', {})
                return False, {"error": f"Analysis failed: {error_info}"}
            elif status in ['running', 'notstarted']:
                if progress_callback:
                    progress_callback(f"Analysis in progress... ({attempt + 1}/{max_attempts})")
                time.sleep(1)
                attempt += 1
            else:
                if progress_callback:
                    progress_callback(f"Unknown status: {status}")
                time.sleep(1)
                attempt += 1
        
        return False, {"error": "Analysis timed out after 2 minutes"}

    def delete_analyze_result(self, operation_location: str) -> Tuple[bool, str]:
        """Delete the stored analyze response early (GDPR / privacy).

        Analyze responses are otherwise retained for 24 hours. Deletes the
        result identified by the analyze Operation-Location URL.
        """
        try:
            base, query = self._split_operation_location(operation_location)
            url = f"{base}?{query}"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}

            logger.debug(f"Deleting analyze result: {url}")
            response = requests.delete(url, headers=headers, timeout=30)

            if response.status_code in (200, 204):
                return True, "Analyze result deleted."
            return False, f"Delete failed (HTTP {response.status_code}): {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Network error deleting result: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error deleting result: {str(e)}"

    def _build_batch_url(self, model_id: str, **params) -> str:
        """Build the analyzeBatch URL with optional analysis query parameters."""
        base_url = f"{self.base_url}/documentModels/{model_id}:analyzeBatch"
        query_params = [f"api-version={self.api_version}"]

        for param, value in params.items():
            if value:
                if isinstance(value, list):
                    query_params.append(f"{param}={','.join(value)}")
                else:
                    query_params.append(f"{param}={value}")

        return f"{base_url}?{'&'.join(query_params)}"

    def analyze_batch_sync(
        self,
        model_id: str,
        container_url: str,
        result_container_url: str,
        prefix: str = "",
        result_prefix: str = "",
        overwrite_existing: bool = True,
        **kwargs
    ) -> Tuple[bool, Union[str, Dict[str, Any]]]:
        """Start a batch analysis over documents in an Azure Blob container.

        Args:
            model_id: Azure DI model ID.
            container_url: Source blob container SAS URL (read+list).
            result_container_url: Destination blob container SAS URL (write+list).
            prefix: Optional blob name prefix to filter the source documents.
            result_prefix: Optional prefix for result blobs.
            overwrite_existing: Overwrite existing result blobs.
            **kwargs: Optional analysis query parameters (pages, features, etc.).

        Returns:
            Tuple of (success, operation_location URL or error dict).
        """
        try:
            url = self._build_batch_url(model_id, **kwargs)

            azure_blob_source = {"containerUrl": container_url}
            if prefix:
                azure_blob_source["prefix"] = prefix

            body: Dict[str, Any] = {
                "azureBlobSource": azure_blob_source,
                "resultContainerUrl": result_container_url,
                "overwriteExisting": overwrite_existing,
            }
            if result_prefix:
                body["resultPrefix"] = result_prefix

            headers = self._get_headers("application/json")
            logger.debug(f"Batch analyze URL: {url}")
            logger.debug(f"Batch body (containers redacted): model={model_id}, prefix='{prefix}', result_prefix='{result_prefix}'")

            response = requests.post(url, headers=headers, json=body, timeout=60)
            logger.debug(f"Batch submit status: {response.status_code}")

            if response.status_code == 202:
                operation_location = response.headers.get('Operation-Location')
                if operation_location:
                    return True, operation_location
                return False, {"error": "No Operation-Location header in batch response"}
            else:
                try:
                    return False, response.json()
                except Exception:
                    return False, {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Batch submit network error: {str(e)}")
            return False, {"error": f"Network error starting batch: {str(e)}"}
        except Exception as e:
            logger.error(f"Batch submit unexpected error: {str(e)}")
            return False, {"error": f"Unexpected error starting batch: {str(e)}"}

    def analyze_batch_with_polling(
        self,
        model_id: str,
        container_url: str,
        result_container_url: str,
        prefix: str = "",
        result_prefix: str = "",
        overwrite_existing: bool = True,
        progress_callback=None,
        max_attempts: int = 600,
        **kwargs
    ) -> Tuple[bool, Dict[str, Any]]:
        """Start a batch analysis and poll until completion.

        Batch jobs can take much longer than single documents, so this polls
        with a longer ceiling (default ~10 minutes at 1s intervals).
        """
        success, result = self.analyze_batch_sync(
            model_id, container_url, result_container_url,
            prefix=prefix, result_prefix=result_prefix,
            overwrite_existing=overwrite_existing, **kwargs
        )
        if not success:
            return False, result

        operation_location = result
        if progress_callback:
            progress_callback("Batch job submitted, waiting for results...")

        attempt = 0
        while attempt < max_attempts:
            ok, poll = self.get_analysis_result_sync(operation_location)
            if not ok:
                return False, poll

            status = poll.get('status', '').lower()
            # The overall batch job terminates as 'completed' (or 'succeeded' in some responses).
            if status in ('succeeded', 'completed'):
                if progress_callback:
                    progress_callback("Batch analysis completed!")
                return True, poll
            elif status == 'failed':
                return False, {"error": f"Batch analysis failed: {poll.get('error', {})}"}
            else:
                if progress_callback:
                    percent = poll.get('percentCompleted')
                    suffix = f" ({percent}%)" if percent is not None else f" ({attempt + 1})"
                    progress_callback(f"Batch in progress...{suffix}")
                time.sleep(1)
                attempt += 1

        return False, {"error": "Batch analysis timed out"}

    def list_batch_results(self, model_id: str) -> Tuple[bool, Dict[str, Any]]:
        """List batch analysis jobs from the past seven days for a model."""
        try:
            url = f"{self.base_url}/documentModels/{model_id}/analyzeBatchResults?api-version={self.api_version}"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return True, response.json()
            try:
                return False, response.json()
            except Exception:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error listing batch jobs: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error listing batch jobs: {str(e)}"}

    def delete_batch_result(self, model_id: str, result_id: str) -> Tuple[bool, str]:
        """Delete a batch analysis job result (GDPR / privacy compliance)."""
        try:
            url = f"{self.base_url}/documentModels/{model_id}/analyzeBatchResults/{result_id}?api-version={self.api_version}"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            response = requests.delete(url, headers=headers, timeout=30)
            if response.status_code in (200, 204):
                return True, f"Batch job '{result_id}' deleted."
            return False, f"Delete failed (HTTP {response.status_code}): {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Network error deleting batch job: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error deleting batch job: {str(e)}"

    def get_model_info(self, model_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get information about a specific model.
        
        Args:
            model_id: Azure DI model ID
            
        Returns:
            Tuple of (success: bool, result: model_info or error_dict)
        """
        try:
            url = f"{self.base_url}/documentModels/{model_id}?api-version={self.api_version}"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                try:
                    error_data = response.json()
                    return False, error_data
                except:
                    return False, {"error": f"HTTP {response.status_code}: {response.text}"}
                    
        except requests.exceptions.Timeout:
            return False, {"error": "Request timed out. Please try again or check your internet connection."}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Failed to connect to Azure Document Intelligence service. Please check your endpoint URL and internet connection."}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def list_models(self) -> Tuple[bool, Dict[str, Any]]:
        """
        List available models.
        
        Returns:
            Tuple of (success: bool, result: models_list or error_dict)
        """
        try:
            url = f"{self.base_url}/documentModels?api-version={self.api_version}"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                try:
                    error_data = response.json()
                    return False, error_data
                except:
                    return False, {"error": f"HTTP {response.status_code}: {response.text}"}
                    
        except requests.exceptions.Timeout:
            return False, {"error": "Request timed out. Please try again or check your internet connection."}
        except requests.exceptions.ConnectionError:
            return False, {"error": "Failed to connect to Azure Document Intelligence service. Please check your endpoint URL and internet connection."}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the connection to Azure Document Intelligence service.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.debug(f"Testing connection to endpoint: {self.endpoint}")
        logger.debug(f"Using API version: {self.api_version}")
        logger.debug(f"API key length: {len(self.api_key)} characters")
        
        success, result = self.list_models()
        
        if success:
            model_count = len(result.get('value', []))
            logger.info(f"Connection test successful, found {model_count} models")
            return True, f"Connection successful! Found {model_count} available models."
        else:
            error_msg = result.get('error', 'Unknown error')
            if isinstance(error_msg, dict):
                error_msg = error_msg.get('message', str(error_msg))
            logger.error(f"Connection test failed: {error_msg}")
            return False, f"Connection failed: {error_msg}"


class DocumentAnalysisResult:
    """Helper class to parse and format Document Intelligence results."""
    
    def __init__(self, result_data: Dict[str, Any]):
        """Initialize with analysis result data."""
        self.raw_data = result_data
        self.analyze_result = result_data.get('analyzeResult', {})
        
    def get_pages(self) -> list:
        """Get all pages from the analysis result."""
        return self.analyze_result.get('pages', [])
    
    def get_tables(self) -> list:
        """Get all tables from the analysis result."""
        return self.analyze_result.get('tables', [])
    
    def get_key_value_pairs(self) -> list:
        """Get all key-value pairs from the analysis result."""
        return self.analyze_result.get('keyValuePairs', [])
    
    def get_documents(self) -> list:
        """Get all documents from the analysis result."""
        return self.analyze_result.get('documents', [])
    
    def get_content(self) -> str:
        """Get the full text content."""
        return self.analyze_result.get('content', '')
    
    def get_formatted_fields(self) -> Dict[str, Any]:
        """Get formatted fields for display.

        A single analysis can return multiple documents of the same docType
        (e.g. multi-copy tax extraction returns several W-2s). Label each copy
        uniquely so later copies don't overwrite earlier ones.
        """
        formatted_fields = {}

        documents = self.get_documents()
        doc_type_counts = Counter(doc.get('docType', 'unknown') for doc in documents)
        seen_counts = {}

        for doc in documents:
            doc_type = doc.get('docType', 'unknown')
            if doc_type_counts[doc_type] > 1:
                seen_counts[doc_type] = seen_counts.get(doc_type, 0) + 1
                label = f"{doc_type} #{seen_counts[doc_type]}"
            else:
                label = doc_type
            fields = doc.get('fields', {})

            formatted_fields[label] = {}
            for field_name, field_data in fields.items():
                formatted_fields[label][field_name] = {
                    'content': field_data.get('content', field_data.get('valueString', field_data.get('value', ''))),
                    'confidence': field_data.get('confidence', 0),
                    'boundingRegions': field_data.get('boundingRegions', []),
                    'type': field_data.get('type', 'string')
                }

        return formatted_fields
    
    def to_markdown(self) -> str:
        """Convert analysis result to markdown format."""
        content = self.get_content()
        
        if not content:
            # Fallback to constructing markdown from pages
            pages = self.get_pages()
            content_parts = []
            
            for page in pages:
                page_content = []
                for line in page.get('lines', []):
                    page_content.append(line.get('content', ''))
                content_parts.append('\n'.join(page_content))
            
            content = '\n\n---\n\n'.join(content_parts)
        
        return content
    
    def get_bounding_boxes(self) -> Dict[str, list]:
        """
        Extract bounding boxes from Azure DI 4.0 API response.
        
        Schema notes:
        - Pages are 1-indexed in API response
        - Bounding regions contain pageNumber (1-based) and polygon (4-vertex quadrilateral)
        - Coordinates are in inches for PDFs, pixels for images
        - Polygons are clockwise: top-left, top-right, bottom-right, bottom-left
        """
        bounding_boxes = {
            'text': [],
            'tables': [],
            'paragraphs': [],
            'figures': [],
            'keyValuePairs': []
        }
        
        analyze_result = self.analyze_result
        
        # 1. Text lines from pages collection
        pages = analyze_result.get('pages', [])
        for page in pages:
            page_number = page.get('pageNumber', 1)  # API uses 1-based page numbers
            
            for line in page.get('lines', []):
                polygon = line.get('polygon', [])
                if len(polygon) == 8:  # Exactly 4 vertices (x,y pairs)
                    bounding_boxes['text'].append({
                        'page': page_number - 1,  # Convert to 0-based for internal use
                        'polygon': polygon,
                        'content': line.get('content', ''),
                        'type': 'text',
                        'confidence': 1.0
                    })
        
        # 2. Tables collection
        for table in analyze_result.get('tables', []):
            for region in table.get('boundingRegions', []):
                polygon = region.get('polygon', [])
                page_number = region.get('pageNumber', 1)
                
                if len(polygon) == 8:
                    bounding_boxes['tables'].append({
                        'page': page_number - 1,
                        'polygon': polygon,
                        'content': f"Table ({table.get('rowCount', 0)} rows × {table.get('columnCount', 0)} cols)",
                        'type': 'table',
                        'confidence': 1.0,
                        'details': {
                            'rowCount': table.get('rowCount', 0),
                            'columnCount': table.get('columnCount', 0),
                            'cellCount': len(table.get('cells', []))
                        }
                    })
        
        # 3. Paragraphs collection  
        for paragraph in analyze_result.get('paragraphs', []):
            for region in paragraph.get('boundingRegions', []):
                polygon = region.get('polygon', [])
                page_number = region.get('pageNumber', 1)
                
                if len(polygon) == 8:
                    content = paragraph.get('content', '')
                    bounding_boxes['paragraphs'].append({
                        'page': page_number - 1,
                        'polygon': polygon,
                        'content': content[:100] + ('...' if len(content) > 100 else ''),
                        'type': 'paragraph',
                        'confidence': 1.0,
                        'details': {
                            'fullContent': content,
                            'length': len(content)
                        }
                    })
        
        # 4. Figures collection
        for figure in analyze_result.get('figures', []):
            for region in figure.get('boundingRegions', []):
                polygon = region.get('polygon', [])
                page_number = region.get('pageNumber', 1)
                
                if len(polygon) == 8:
                    caption = figure.get('caption', {}).get('content', '')
                    bounding_boxes['figures'].append({
                        'page': page_number - 1,
                        'polygon': polygon,
                        'content': f"Figure: {caption}" if caption else "Figure",
                        'type': 'figure',
                        'confidence': 1.0,
                        'details': {
                            'id': figure.get('id', ''),
                            'caption': caption
                        }
                    })
        
        # 5. Key-value pairs (if present)
        for kvp in analyze_result.get('keyValuePairs', []):
            key_obj = kvp.get('key', {})
            value_obj = kvp.get('value', {})
            
            # Process key regions
            for region in key_obj.get('boundingRegions', []):
                polygon = region.get('polygon', [])
                page_number = region.get('pageNumber', 1)
                
                if len(polygon) == 8:
                    bounding_boxes['keyValuePairs'].append({
                        'page': page_number - 1,
                        'polygon': polygon,
                        'content': f"Key: {key_obj.get('content', '')}",
                        'type': 'key',
                        'confidence': kvp.get('confidence', 1.0),
                        'details': {
                            'role': 'key',
                            'keyContent': key_obj.get('content', ''),
                            'valueContent': value_obj.get('content', '')
                        }
                    })
            
            # Process value regions  
            for region in value_obj.get('boundingRegions', []):
                polygon = region.get('polygon', [])
                page_number = region.get('pageNumber', 1)
                
                if len(polygon) == 8:
                    bounding_boxes['keyValuePairs'].append({
                        'page': page_number - 1,
                        'polygon': polygon,
                        'content': f"Value: {value_obj.get('content', '')}",
                        'type': 'value',
                        'confidence': kvp.get('confidence', 1.0),
                        'details': {
                            'role': 'value',
                            'keyContent': key_obj.get('content', ''),
                            'valueContent': value_obj.get('content', '')
                        }
                    })
        
        return bounding_boxes


def create_client_from_env() -> Optional[AzureDocumentIntelligenceClient]:
    """Create client from environment variables or Streamlit secrets."""
    endpoint = None
    api_key = None
    
    # Try to get from Streamlit secrets first
    try:
        endpoint = st.secrets["AZURE_DI_ENDPOINT"]
        api_key = st.secrets["AZURE_DI_API_KEY"]
    except:
        # Try environment variables
        import os
        endpoint = os.getenv("AZURE_DI_ENDPOINT")
        api_key = os.getenv("AZURE_DI_API_KEY")
    
    if endpoint and api_key:
        return AzureDocumentIntelligenceClient(endpoint, api_key)
    
    return None