"""
Azure Document Intelligence 4.0 Streamlit Demo Application.

This application provides a comprehensive interface for testing all Azure Document Intelligence 4.0
capabilities through REST API integration. Features include dynamic model selection, parameter
configuration, document upload, analysis, and multi-format result visualization.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import logging configuration
from logging_config import setup_logging, get_logger

# Set up logging for the entire application
setup_logging()
logger = get_logger(__name__)

# Import our custom modules
from config import AZURE_DI_MODELS, get_model_display_name
from azure_di_client import AzureDocumentIntelligenceClient, DocumentAnalysisResult, create_client_from_env
from document_processor import DocumentProcessor, ResultsFormatter, create_document_viewer_html
from ui_components import (
    ModelSelector, ParameterConfiguration, FileUploadSection, 
    ResultsDisplay, StatusDisplay, DocumentViewer, 
    render_connection_status, render_auto_mode_placeholder
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Azure Document Intelligence 4.0 Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0078d4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'raw_result' not in st.session_state:
        st.session_state.raw_result = None
    if 'analysis_params' not in st.session_state:
        st.session_state.analysis_params = None
    if 'document_images' not in st.session_state:
        st.session_state.document_images = None
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'current_file_id' not in st.session_state:
        st.session_state.current_file_id = None
    if 'current_page_idx' not in st.session_state:
        st.session_state.current_page_idx = 0
    if 'searchable_pdf' not in st.session_state:
        st.session_state.searchable_pdf = None
    if 'extracted_figures' not in st.session_state:
        st.session_state.extracted_figures = {}
    if 'batch_result' not in st.session_state:
        st.session_state.batch_result = None
    if 'operation_location' not in st.session_state:
        st.session_state.operation_location = None


def create_azure_client() -> Optional[AzureDocumentIntelligenceClient]:
    """Create and return Azure Document Intelligence client."""
    client = create_client_from_env()

    if not client:
        st.sidebar.warning("⚠️ **Azure DI credentials not found in environment**")
        st.sidebar.markdown("### 🔐 Enter Credentials")

        # Add input boxes for endpoint and API key
        endpoint = st.sidebar.text_input(
            "Azure DI Endpoint",
            placeholder="https://your-resource.cognitiveservices.azure.com",
            help="Your Azure Document Intelligence endpoint URL",
            key="azure_di_endpoint_input"
        )

        api_key = st.sidebar.text_input(
            "Azure DI API Key",
            type="password",
            placeholder="Enter your API key",
            help="Your Azure Document Intelligence API key",
            key="azure_di_api_key_input"
        )

        # If both fields are filled, create client
        if endpoint and api_key:
            try:
                client = AzureDocumentIntelligenceClient(endpoint.strip(), api_key.strip())
                st.sidebar.success("✅ Credentials provided!")
                return client
            except Exception as e:
                st.sidebar.error(f"Failed to create client: {str(e)}")
                return None

        # Show help message
        with st.sidebar.expander("💡 Alternative Setup Methods", expanded=False):
            st.markdown(
                "**Option 1: Environment Variables**\n"
                "```bash\n"
                "export AZURE_DI_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'\n"
                "export AZURE_DI_API_KEY='your-api-key-here'\n"
                "```\n\n"
                "**Option 2: Streamlit Secrets**\n"
                "Add to `.streamlit/secrets.toml`:\n"
                "```toml\n"
                "AZURE_DI_ENDPOINT = \"https://your-resource.cognitiveservices.azure.com/\"\n"
                "AZURE_DI_API_KEY = \"your-api-key-here\"\n"
                "```"
            )
        return None

    return client


def render_main_header():
    """Render the main application header."""
    st.markdown('<h1 class="main-header">🤖 Azure Document Intelligence 4.0 Demo</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Comprehensive showcase of all Azure Document Intelligence capabilities via REST API</p>',
        unsafe_allow_html=True
    )

    # Attribution and license notice
    st.info(
        "👤 **Author:** Andrey Vykhodtsev | "
        "📜 **License:** MIT License | "
        "⚖️ Attribution required when using or modifying this code | "
        "[View License](https://github.com/vykhand/azure-di-showcase/blob/main/LICENSE)"
    )


def fetch_output_artifacts(client: AzureDocumentIntelligenceClient, analysis: DocumentAnalysisResult, requested_output):
    """Fetch generated artifacts (searchable PDF, figure images) into session state.

    Args:
        client: Azure DI client (holds the last Operation-Location).
        analysis: Parsed analysis result.
        requested_output: List of output options requested (e.g. ['pdf', 'figures']).
    """
    # Always reset so stale artifacts from a previous run aren't shown.
    st.session_state.searchable_pdf = None
    st.session_state.extracted_figures = {}

    requested_output = requested_output or []
    operation_location = getattr(client, 'last_operation_location', None)
    if not operation_location:
        return

    if 'pdf' in requested_output:
        ok, pdf = client.get_pdf_result(operation_location)
        if ok:
            st.session_state.searchable_pdf = pdf
        else:
            logger.warning(f"Could not retrieve searchable PDF: {pdf}")

    if 'figures' in requested_output:
        figures = analysis.analyze_result.get('figures', [])
        for figure in figures:
            figure_id = figure.get('id')
            if not figure_id:
                continue
            ok, image = client.get_figure(operation_location, figure_id)
            if ok:
                st.session_state.extracted_figures[figure_id] = image
            else:
                logger.warning(f"Could not retrieve figure '{figure_id}': {image}")


def handle_document_analysis(client: AzureDocumentIntelligenceClient, model_id: str, file_data: bytes, params: Dict[str, Any]):
    """
    Handle document analysis process.
    
    Args:
        client: Azure DI client
        model_id: Selected model ID
        file_data: Document file data
        params: Analysis parameters
    """
    logger.info(f"Starting document analysis with model: {model_id}")
    logger.debug(f"Document size: {len(file_data)} bytes, Parameters: {params}")
    
    # Progress indicator
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    def progress_callback(message: str):
        logger.debug(f"Progress: {message}")
        progress_placeholder.info(f"⏳ {message}")
    
    # Start analysis
    with st.spinner("Starting document analysis..."):
        progress_callback("Uploading document and starting analysis...")
        
        # Filter out empty parameters
        filtered_params = {k: v for k, v in params.items() if v}
        logger.debug(f"Filtered parameters: {filtered_params}")
        
        success, result = client.analyze_document_with_polling(
            model_id=model_id,
            document_data=file_data,
            progress_callback=progress_callback,
            **filtered_params
        )
    
    # Clear progress indicators
    progress_placeholder.empty()
    
    if success:
        logger.info("Document analysis completed successfully")
        st.session_state.raw_result = result
        st.session_state.analysis_result = result
        st.session_state.analysis_params = filtered_params  # Store the analysis parameters
        st.session_state.operation_location = getattr(client, 'last_operation_location', None)
        status_placeholder.success("✅ Document analysis completed successfully!")

        try:
            # Create analysis result object for easier data access
            analysis = DocumentAnalysisResult(result)

            # Retrieve generated artifacts (searchable PDF, figures) when requested.
            fetch_output_artifacts(client, analysis, filtered_params.get('output', []))
            
            # Display summary stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pages = analysis.get_pages()
                st.metric("Pages Analyzed", len(pages))
            
            with col2:
                tables = analysis.get_tables()
                st.metric("Tables Found", len(tables))
            
            with col3:
                kvps = analysis.get_key_value_pairs()
                st.metric("Key-Value Pairs", len(kvps))
            
            with col4:
                documents = analysis.get_documents()
                st.metric("Documents", len(documents))
                
        except Exception as e:
            logger.warning(f"Issue processing analysis results: {str(e)}")
            st.warning(f"⚠️ Analysis completed but there was an issue processing the results: {str(e)}")
        
    else:
        error_msg = result.get('error', 'Unknown error occurred')
        if isinstance(error_msg, dict):
            error_details = error_msg.get('message', str(error_msg))
        else:
            error_details = str(error_msg)
        
        logger.error(f"Document analysis failed: {error_details}")
        logger.debug(f"Full error result: {result}")
        
        status_placeholder.error(f"❌ Analysis failed: {error_details}")
        st.session_state.analysis_result = None
        st.session_state.raw_result = None
        st.session_state.analysis_params = None
        st.session_state.searchable_pdf = None
        st.session_state.extracted_figures = {}
        st.session_state.operation_location = None
        
        # Show detailed debugging information
        st.subheader("🔍 Debugging Information")
        
        # Display the full error result for debugging
        with st.expander("View Full Error Details", expanded=True):
            st.json(result)
        
        # Show traceback if available
        if "traceback" in result:
            with st.expander("View Stack Trace", expanded=False):
                st.code(result["traceback"], language="python")
        
        # Add instructions for viewing console logs
        st.info("""
        📋 **To see detailed debug logs:**
        1. Open your terminal where you ran `streamlit run app.py`
        2. Look for DEBUG messages in the console output
        3. The logs will show the exact URL, headers, and response details
        """)
        
        # Provide helpful suggestions based on error type
        if "timeout" in error_details.lower():
            st.info("💡 **Tip**: Large documents may take longer to process. Try analyzing fewer pages or a smaller file.")
        elif "unauthorized" in error_details.lower() or "403" in error_details or "401" in error_details:
            st.info("💡 **Tip**: Check your API key and endpoint URL in the connection status section.")
        elif "network" in error_details.lower() or "connection" in error_details.lower():
            st.info("💡 **Tip**: Check your internet connection and try again.")
        elif "unsupported" in error_details.lower():
            st.info("💡 **Tip**: Make sure your document is in a supported format (PDF, JPG, PNG, BMP, TIFF).")
        elif "resource not found" in error_details.lower():
            st.error("🚨 **Resource not found** usually means:")
            st.markdown("""
            - **Wrong endpoint URL**: Check if your endpoint URL is correct
            - **Wrong API version**: Using unsupported API version
            - **Model not available**: The model might not be available in your region
            - **Malformed URL**: Check the URL construction in debug logs
            """)
            st.info("💡 **Next steps**: Check the debug logs in your terminal console for the exact URL being used.")


def _show_annotation_legend(image_width: int, zoom_level: float):
    """Display the annotation legend at the top with collapsible functionality."""
    
    # Calculate actual display width
    display_width = int(image_width * zoom_level)
    
    # Create collapsible expander for legend
    with st.expander("📍 Document Annotations Legend", expanded=False):
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; 
                    width: {display_width}px; max-width: 100%;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 12px; background-color: #007ACC; 
                                margin-right: 8px; border: 1px solid #ccc; border-radius: 2px;"></div>
                    <span style="font-size: 14px; color: #333;">📝 Text Lines</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 12px; background-color: #00B04F; 
                                margin-right: 8px; border: 1px solid #ccc; border-radius: 2px;"></div>
                    <span style="font-size: 14px; color: #333;">📊 Tables</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 12px; background-color: #9932CC; 
                                margin-right: 8px; border: 1px solid #ccc; border-radius: 2px;"></div>
                    <span style="font-size: 14px; color: #333;">📄 Paragraphs</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 12px; background-color: #DC143C; 
                                margin-right: 8px; border: 1px solid #ccc; border-radius: 2px;"></div>
                    <span style="font-size: 14px; color: #333;">🖼️ Figures</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 12px; background-color: #FF8C00; 
                                margin-right: 8px; border: 1px solid #ccc; border-radius: 2px;"></div>
                    <span style="font-size: 14px; color: #333;">🔗 Key-Value Pairs</span>
                </div>
            </div>
            <div style="font-size: 12px; color: #6c757d; margin-top: 10px; font-style: italic;">
                💡 Hover over highlighted areas to see detailed information
            </div>
        </div>
        """, unsafe_allow_html=True)


def _create_interactive_annotations(image, bounding_boxes, page_idx, scale_x, scale_y, zoom_level=1.0):
    """Create HTML with interactive annotations and rich tooltips."""
    import base64
    from io import BytesIO
    import html
    
    # Encode image
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = base64.b64encode(buffer.getvalue()).decode()
    
    # Filter boxes for current page
    page_boxes = {}
    for box_type, boxes in bounding_boxes.items():
        page_boxes[box_type] = [box for box in boxes if box.get('page', 0) == page_idx]
    
    # Element colors and names
    element_info = {
        'text': {'color': '#007ACC', 'name': '📝 Text Line', 'icon': '📝'},
        'tables': {'color': '#00B04F', 'name': '📊 Table', 'icon': '📊'},
        'paragraphs': {'color': '#9932CC', 'name': '📄 Paragraph', 'icon': '📄'},
        'figures': {'color': '#DC143C', 'name': '🖼️ Figure', 'icon': '🖼️'},
        'keyValuePairs': {'color': '#FF8C00', 'name': '🔗 Key-Value Pair', 'icon': '🔗'}
    }
    
    # Create overlays with rich tooltips
    overlays_html = ""
    container_id = f"doc-viewer-{page_idx}"
    
    overlay_count = 0
    for box_type, boxes in page_boxes.items():
        info = element_info.get(box_type, {'color': '#FF0000', 'name': box_type.title(), 'icon': '📋'})
        color = info['color']
        type_name = info['name']
        icon = info['icon']
        
        for i, box in enumerate(boxes):
            polygon = box.get('polygon', [])
            if len(polygon) != 8:
                continue
                
            # Calculate bounding rectangle with zoom
            x_coords = [polygon[j] * scale_x * zoom_level for j in range(0, 8, 2)]
            y_coords = [polygon[j] * scale_y * zoom_level for j in range(1, 8, 2)]
            
            x_min = max(0, int(min(x_coords)))
            y_min = max(0, int(min(y_coords)))
            x_max = min(int(image.width * zoom_level), int(max(x_coords)))
            y_max = min(int(image.height * zoom_level), int(max(y_coords)))
            
            width = x_max - x_min
            height = y_max - y_min
            
            # Debug logging for first few boxes
            if overlay_count < 3:
                from logging_config import get_logger
                logger = get_logger(__name__)
                logger.debug(f"Box {overlay_count} ({box_type}): raw_polygon={polygon[:4]}")
                logger.debug(f"Box {overlay_count}: scaled_coords=({x_min},{y_min},{x_max},{y_max})")
                logger.debug(f"Box {overlay_count}: size={width}x{height}px")
            
            if width <= 2 or height <= 2:
                continue
            
            # Create detailed tooltip content
            content = box.get('content', '').strip()
            confidence = box.get('confidence', 1.0)
            
            tooltip_lines = [f"<div style='font-weight:bold;color:{color};'>{icon} {type_name}</div>"]
            
            if content:
                # Truncate long content for display
                display_content = content[:100] + '...' if len(content) > 100 else content
                tooltip_lines.append(f"<div style='margin:5px 0;'><strong>Content:</strong><br>{html.escape(display_content)}</div>")
            
            if confidence < 1.0:
                tooltip_lines.append(f"<div style='font-size:0.9em;color:#666;'><strong>Confidence:</strong> {confidence:.1%}</div>")
            
            # Add type-specific details
            if box.get('details'):
                details = box['details']
                if box_type == 'tables':
                    rows = details.get('rowCount', 0)
                    cols = details.get('columnCount', 0)
                    tooltip_lines.append(f"<div style='font-size:0.9em;color:#666;'><strong>Size:</strong> {rows} rows × {cols} columns</div>")
                elif box_type == 'keyValuePairs':
                    role = details.get('role', '').title()
                    if role:
                        tooltip_lines.append(f"<div style='font-size:0.9em;color:#666;'><strong>Role:</strong> {role}</div>")
                elif box_type == 'figures':
                    fig_id = details.get('id', '')
                    if fig_id:
                        tooltip_lines.append(f"<div style='font-size:0.9em;color:#666;'><strong>ID:</strong> {fig_id}</div>")
            
            tooltip_content = ''.join(tooltip_lines)
            overlay_id = f"overlay-{overlay_count}"
            overlay_count += 1
            
            overlays_html += f'''
            <div class="annotation-overlay" 
                 id="{overlay_id}"
                 data-tooltip="{html.escape(tooltip_content)}"
                 style="position:absolute;left:{x_min}px;top:{y_min}px;width:{width}px;height:{height}px;
                        border:2px solid {color};background:rgba(0,0,0,0.05);cursor:help;
                        transition:all 0.2s ease;">
            </div>'''
    
    # Create complete HTML with advanced tooltips
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
        body {{
            margin: 0;
            padding: 10px;
            font-family: 'Source Sans Pro', sans-serif;
        }}
        
        .annotation-overlay {{
            transition: all 0.2s ease;
        }}
        
        .annotation-overlay:hover {{
            background: rgba(255,255,255,0.3) !important;
            border-width: 3px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
        }}
        
        .custom-tooltip {{
            word-wrap: break-word;
            white-space: normal;
        }}
        
        #{container_id} {{
            margin: 0 auto;
            display: block;
        }}
        </style>
    </head>
    <body>
        <div id="{container_id}" style="position:relative;display:inline-block;">
            <img src="data:image/png;base64,{image_data}" 
                 style="display:block;width:{int(image.width * zoom_level)}px;height:{int(image.height * zoom_level)}px;border:1px solid #ddd;border-radius:5px;" 
                 alt="Document page {page_idx + 1}" />
            {overlays_html}
            
            <!-- Tooltip container -->
            <div id="tooltip-{container_id}" class="custom-tooltip" 
                 style="position:absolute;background:rgba(0,0,0,0.9);color:white;padding:12px;
                        border-radius:8px;font-size:13px;line-height:1.4;max-width:300px;
                        pointer-events:none;z-index:1000;display:none;
                        box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            </div>
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const container = document.getElementById('{container_id}');
            const tooltip = document.getElementById('tooltip-{container_id}');
            
            if (!container || !tooltip) return;
            
            const overlays = container.querySelectorAll('.annotation-overlay');
            
            overlays.forEach(overlay => {{
                overlay.addEventListener('mouseenter', function(e) {{
                    const tooltipContent = this.getAttribute('data-tooltip');
                    if (tooltipContent) {{
                        tooltip.innerHTML = tooltipContent;
                        tooltip.style.display = 'block';
                    }}
                }});
                
                overlay.addEventListener('mousemove', function(e) {{
                    const rect = container.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    // Position tooltip
                    let tooltipX = x + 10;
                    let tooltipY = y - 10;
                    
                    // Keep tooltip in bounds
                    const tooltipRect = tooltip.getBoundingClientRect();
                    const containerRect = container.getBoundingClientRect();
                    
                    if (tooltipX + tooltipRect.width > containerRect.width) {{
                        tooltipX = x - tooltipRect.width - 10;
                    }}
                    if (tooltipY < 0) {{
                        tooltipY = y + 20;
                    }}
                    
                    tooltip.style.left = tooltipX + 'px';
                    tooltip.style.top = tooltipY + 'px';
                }});
                
                overlay.addEventListener('mouseleave', function() {{
                    tooltip.style.display = 'none';
                }});
            }});
        }});
        </script>
    </body>
    </html>
    '''
    
    return html_content


def render_document_preview(uploaded_file, file_source: str):
    """
    Render document preview section with annotations if analysis results are available.
    
    Args:
        uploaded_file: Uploaded file object
        file_source: Source of the file (upload/url/sample)
    """
    if not uploaded_file:
        return
    
    st.header("📄 Document Viewer")
    
    # Get file data with proper handling
    try:
        if hasattr(uploaded_file, 'read'):
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            file_data = uploaded_file.read()
        elif hasattr(uploaded_file, 'getvalue'):
            file_data = uploaded_file.getvalue()
        else:
            st.error("Unable to read file data")
            return
        
        # Validate file data
        if not file_data or len(file_data) == 0:
            st.error("File appears to be empty or corrupted")
            return
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return
    
    # Get file info
    file_info = DocumentProcessor.get_file_info(uploaded_file) if hasattr(uploaded_file, 'name') else {}
    
    # Display file information
    if file_info:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("File Name", file_info.get('name', 'Unknown')[:20] + "..." if len(file_info.get('name', '')) > 20 else file_info.get('name', 'Unknown'))
        with col2:
            st.metric("File Size", f"{file_info.get('size_mb', 0)} MB")
        with col3:
            st.metric("File Type", file_info.get('extension', 'Unknown').upper())
        with col4:
            st.metric("Source", file_source.title())
    
    # Convert to images for preview
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower() if hasattr(uploaded_file, 'name') else 'pdf'
        images = DocumentProcessor.convert_to_images(file_data, file_extension)
        
        if images:
            st.session_state.document_images = images
            
            # Viewer controls
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                # Page navigation for multi-page documents
                if len(images) > 1:
                    # Initialize page index in session state
                    if 'current_page_idx' not in st.session_state:
                        st.session_state.current_page_idx = 0
                    
                    # Ensure page index is within bounds
                    st.session_state.current_page_idx = max(0, min(st.session_state.current_page_idx, len(images) - 1))
                    
                    # Navigation controls
                    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                    
                    with nav_col1:
                        if st.button("◀ Prev", disabled=st.session_state.current_page_idx == 0):
                            st.session_state.current_page_idx -= 1
                            st.rerun()
                    
                    with nav_col2:
                        # Page selector dropdown
                        page_idx = st.selectbox(
                            "Page:",
                            range(len(images)),
                            index=st.session_state.current_page_idx,
                            format_func=lambda x: f"Page {x + 1} of {len(images)}",
                            key="page_selector"
                        )
                        # Update session state if dropdown changed
                        if page_idx != st.session_state.current_page_idx:
                            st.session_state.current_page_idx = page_idx
                    
                    with nav_col3:
                        if st.button("Next ▶", disabled=st.session_state.current_page_idx == len(images) - 1):
                            st.session_state.current_page_idx += 1
                            st.rerun()
                    
                    page_idx = st.session_state.current_page_idx
                else:
                    page_idx = 0
                    st.write(f"📄 Page 1 of 1")
            
            with col2:
                # Annotation toggle
                show_annotations = st.checkbox("Show Annotations", value=True, disabled=not st.session_state.analysis_result)
                if not st.session_state.analysis_result:
                    st.caption("Annotations available after analysis")
            
            with col3:
                st.write("**Display Options**")
                show_tooltips = st.checkbox("Show labels", value=True, 
                                          help="Show text labels on bounding boxes")
                
                # Zoom control
                zoom_level = st.slider("Zoom", 
                                     min_value=0.25, 
                                     max_value=2.0, 
                                     value=1.0, 
                                     step=0.25,
                                     format="%.2fx",
                                     help="Scale the document display size")
            
            # Display document with or without annotations
            if page_idx < len(images):
                display_image = images[page_idx]
                
                # Show annotations with interactive tooltips
                if show_annotations and st.session_state.analysis_result:
                    try:
                        from azure_di_client import DocumentAnalysisResult
                        
                        # Get bounding boxes
                        analysis = DocumentAnalysisResult(st.session_state.analysis_result)
                        bounding_boxes = analysis.get_bounding_boxes()
                        
                        # Show legend first
                        if show_tooltips:
                            _show_annotation_legend(display_image.width, zoom_level)
                        
                        # Calculate scaling factors
                        pages = st.session_state.analysis_result.get('analyzeResult', {}).get('pages', [])
                        if pages and page_idx < len(pages):
                            page_info = pages[page_idx]
                            page_width_inches = page_info.get('width', 8.5)
                            page_height_inches = page_info.get('height', 11)
                            
                            # Log debug info
                            from logging_config import get_logger
                            logger = get_logger(__name__)
                            logger.debug(f"Page {page_idx}: size {page_width_inches}\" x {page_height_inches}\"")
                            logger.debug(f"Image size: {display_image.width} x {display_image.height} pixels")
                            
                            scale_x = display_image.width / page_width_inches
                            scale_y = display_image.height / page_height_inches
                            
                            logger.debug(f"Scale factors: X={scale_x:.2f}, Y={scale_y:.2f}")
                        else:
                            scale_x = scale_y = 150.0 / 72.0  # Default 150 DPI
                        
                        # Create HTML with interactive annotations
                        if show_tooltips:
                            html = _create_interactive_annotations(
                                display_image, bounding_boxes, page_idx, scale_x, scale_y, zoom_level
                            )
                            # Use components.html for complex HTML with JavaScript
                            # Set height to match zoomed image height plus padding
                            component_height = int(display_image.height * zoom_level) + 40  # Add padding for borders
                            components.html(html, height=component_height, scrolling=False)
                        else:
                            # Use simple annotator for labels without tooltips
                            from simple_annotator import SimpleDocumentAnnotator
                            annotator = SimpleDocumentAnnotator()
                            annotated_image = annotator.annotate_image(
                                display_image, bounding_boxes, page_idx, scale_x, scale_y, True
                            )
                            st.image(annotated_image, caption=f"Page {page_idx + 1} (with annotations)", use_container_width=True)
                    
                    except Exception as e:
                        st.error(f"Could not create annotations: {str(e)}")
                        st.image(display_image, caption=f"Page {page_idx + 1}", use_container_width=True)
                else:
                    # Show plain image
                    st.image(display_image, caption=f"Page {page_idx + 1}", use_container_width=True)
        else:
            st.warning("Could not generate preview for this document type.")
            
    except Exception as e:
        st.error(f"Error generating document preview: {str(e)}")


def render_analysis_results(client=None):
    """Render analysis results section."""
    if not st.session_state.analysis_result:
        return
    
    st.header("📊 Analysis Results")

    # Generated artifacts (searchable PDF / figures), when requested and available.
    render_output_artifacts()

    # Results display with tabs
    ResultsDisplay.render_results_tabs(
        st.session_state.analysis_result,
        st.session_state.raw_result or st.session_state.analysis_result
    )

    # GDPR / privacy: delete the stored analyze response early (otherwise kept 24h).
    operation_location = st.session_state.get('operation_location')
    if client and operation_location:
        with st.expander("🗑️ Privacy: delete stored response", expanded=False):
            st.caption(
                "Analyze responses are retained by Azure for 24 hours. "
                "Delete the stored response now if you don't need to re-fetch it."
            )
            if st.button("Delete analyze result", key="delete_analyze_result"):
                ok, msg = client.delete_analyze_result(operation_location)
                if ok:
                    st.session_state.operation_location = None
                    st.success(msg)
                else:
                    st.error(msg)


def render_output_artifacts():
    """Render download buttons and previews for generated artifacts."""
    pdf_bytes = st.session_state.get('searchable_pdf')
    figures = st.session_state.get('extracted_figures') or {}

    if not pdf_bytes and not figures:
        return

    st.subheader("📦 Generated Output")

    if pdf_bytes:
        st.download_button(
            label="💾 Download Searchable PDF",
            data=pdf_bytes,
            file_name="searchable.pdf",
            mime="application/pdf",
            key="download_searchable_pdf"
        )

    if figures:
        st.write(f"**Extracted Figures ({len(figures)})**")
        figure_items = list(figures.items())
        cols = st.columns(min(3, len(figure_items)))
        for idx, (figure_id, image_bytes) in enumerate(figure_items):
            with cols[idx % len(cols)]:
                st.image(image_bytes, caption=f"Figure {figure_id}")
                st.download_button(
                    label="💾 Download",
                    data=image_bytes,
                    file_name=f"figure_{figure_id}.png",
                    mime="image/png",
                    key=f"download_figure_{figure_id}"
                )



def render_single_document_tab(client, selected_model, all_params):
    """Render the single-document upload, preview, and results workflow."""
    # Main content area
    col1, col2 = st.columns([2, 3])

    with col1:
        # File upload section
        uploaded_file, file_source = FileUploadSection.render_upload_section()

        # Clear state when no file is uploaded
        if not uploaded_file:
            if st.session_state.get('current_file_id') is not None:
                # File was removed - clear analysis
                st.session_state.analysis_result = None
                st.session_state.raw_result = None
                st.session_state.analysis_params = None
                st.session_state.document_images = None
                st.session_state.current_page_idx = 0
                st.session_state.current_file_id = None
                st.session_state.uploaded_file = None

        if uploaded_file:
            # Check if this is a different document than before
            current_file_id = None
            if hasattr(uploaded_file, 'name') and hasattr(uploaded_file, 'getvalue'):
                # For file uploads, use name + size as identifier
                try:
                    file_size = len(uploaded_file.getvalue())
                    current_file_id = f"{uploaded_file.name}_{file_size}_{file_source}"
                except:
                    current_file_id = f"{uploaded_file.name}_{file_source}"
            elif hasattr(uploaded_file, 'name'):
                # For URL/sample docs, use the name + source
                current_file_id = f"{uploaded_file.name}_{file_source}"
            else:
                # Fallback identifier
                current_file_id = f"unknown_{file_source}"

            # Clear analysis results if document changed
            if 'current_file_id' not in st.session_state:
                st.session_state.current_file_id = None

            if current_file_id != st.session_state.current_file_id:
                # Document changed - clear previous analysis
                st.session_state.analysis_result = None
                st.session_state.raw_result = None
                st.session_state.analysis_params = None
                st.session_state.document_images = None
                st.session_state.current_page_idx = 0  # Reset to first page
                st.session_state.current_file_id = current_file_id

            # Validate file
            is_valid, validation_msg = DocumentProcessor.validate_file(uploaded_file)

            if is_valid:
                st.success(f"✅ {validation_msg}")

                # Store file in session state
                st.session_state.uploaded_file = uploaded_file

                # Analysis button
                if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
                    try:
                        # Get file data with proper handling
                        if hasattr(uploaded_file, 'read'):
                            uploaded_file.seek(0)  # Reset file pointer
                            file_data = uploaded_file.read()
                        elif hasattr(uploaded_file, 'getvalue'):
                            file_data = uploaded_file.getvalue()
                        else:
                            st.error("Unable to read file data for analysis")
                            st.stop()

                        # Validate file data before analysis
                        if not file_data or len(file_data) == 0:
                            st.error("File data is empty. Please try uploading the file again.")
                            st.stop()

                        handle_document_analysis(client, selected_model, file_data, all_params)

                    except Exception as e:
                        st.error(f"Error preparing file for analysis: {str(e)}")
                        st.info("💡 **Tip**: Try re-uploading the file or use a different document.")
            else:
                st.error(f"❌ {validation_msg}")

    with col2:
        # Document preview
        if st.session_state.uploaded_file:
            render_document_preview(st.session_state.uploaded_file, file_source or 'upload')

    # Analysis results (full width)
    render_analysis_results(client)


def render_batch_analysis_tab(client, selected_model, all_params):
    """Render the batch analysis workflow over an Azure Blob container."""
    st.header("🗂️ Batch Analysis")
    st.caption(
        f"Analyze every document in an Azure Blob container with **{selected_model}** "
        "in a single job. Results are written to your result container as JSON "
        "(plus any requested PDF/figures)."
    )
    st.info(
        "ℹ️ Provide **SAS URLs** with the right permissions: the source container needs "
        "**Read + List**, the result container needs **Write + List**. The current sidebar "
        "model and parameters are applied to the whole batch."
    )

    with st.form("batch_form"):
        container_url = st.text_input(
            "Source container SAS URL",
            placeholder="https://acct.blob.core.windows.net/source?sv=...&sig=...",
            help="Blob container holding the documents to analyze (Read + List)."
        )
        prefix = st.text_input(
            "Source prefix (optional)",
            placeholder="invoices/2025/",
            help="Only analyze blobs whose names start with this prefix."
        )
        result_container_url = st.text_input(
            "Result container SAS URL",
            placeholder="https://acct.blob.core.windows.net/results?sv=...&sig=...",
            help="Destination container for result JSON (Write + List)."
        )
        result_prefix = st.text_input(
            "Result prefix (optional)",
            placeholder="output/",
            help="Prefix for result blobs. Required if results share the source container."
        )
        overwrite_existing = st.checkbox("Overwrite existing result blobs", value=True)
        submitted = st.form_submit_button("🚀 Run Batch Analysis", type="primary")

    if submitted:
        if not container_url or not result_container_url:
            st.error("Both the source and result container SAS URLs are required.")
        else:
            # Reuse the sidebar analysis parameters, dropping empties.
            batch_kwargs = {k: v for k, v in all_params.items() if v}
            progress = st.empty()

            def progress_callback(message: str):
                progress.info(f"⏳ {message}")

            with st.spinner("Running batch analysis..."):
                ok, result = client.analyze_batch_with_polling(
                    model_id=selected_model,
                    container_url=container_url,
                    result_container_url=result_container_url,
                    prefix=prefix,
                    result_prefix=result_prefix,
                    overwrite_existing=overwrite_existing,
                    progress_callback=progress_callback,
                    **batch_kwargs
                )
            progress.empty()

            if ok:
                st.session_state.batch_result = result
                st.success("✅ Batch analysis completed!")
            else:
                st.session_state.batch_result = None
                error_msg = result.get('error', result) if isinstance(result, dict) else result
                st.error(f"❌ Batch analysis failed: {error_msg}")
                with st.expander("View error details", expanded=True):
                    st.json(result)

    # Show the most recent batch result.
    if st.session_state.get('batch_result'):
        render_batch_result(st.session_state.batch_result)

    # Recent batch jobs (past 7 days) with delete.
    render_batch_jobs(client, selected_model)


def render_batch_result(result):
    """Render the summary and per-file details of a completed batch job."""
    batch = result.get('result', {}) if isinstance(result, dict) else {}
    details = batch.get('details', [])

    st.subheader("📦 Batch Result")
    col1, col2, col3 = st.columns(3)
    col1.metric("Succeeded", batch.get('succeededCount', 0))
    col2.metric("Failed", batch.get('failedCount', 0))
    col3.metric("Skipped", batch.get('skippedCount', 0))

    if details:
        rows = [
            {
                "Source": d.get('sourceUrl', '').split('?')[0],
                "Status": d.get('status', ''),
                "Result": d.get('resultUrl', '').split('?')[0],
            }
            for d in details
        ]
        st.dataframe(rows, use_container_width=True)


def render_batch_jobs(client, selected_model):
    """List batch jobs from the past seven days and allow deletion."""
    with st.expander("🕘 Recent batch jobs (past 7 days)", expanded=False):
        if st.button("Refresh batch job list", key="refresh_batch_jobs"):
            ok, result = client.list_batch_results(selected_model)
            if ok:
                st.session_state.batch_jobs = result.get('value', result)
            else:
                st.error(f"Could not list batch jobs: {result}")

        jobs = st.session_state.get('batch_jobs')
        if jobs:
            for job in jobs:
                result_id = job.get('resultId') or job.get('operationId') or ''
                status = job.get('status', 'unknown')
                col1, col2 = st.columns([4, 1])
                col1.write(f"`{result_id}` — {status}")
                if result_id and col2.button("Delete", key=f"del_batch_{result_id}"):
                    ok, msg = client.delete_batch_result(selected_model, result_id)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def main():
    """Main application function."""
    logger.info("Starting Azure Document Intelligence Streamlit Demo")
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_main_header()
    
    # Create Azure client
    client = create_azure_client()
    
    if not client:
        logger.error("Failed to create Azure DI client - stopping application")
        st.stop()
    
    # Sidebar: Connection status
    render_connection_status(client)
    
    # Sidebar: Model selection
    selected_model = ModelSelector.render_model_dropdown()
    st.session_state.selected_model = selected_model
    
    if selected_model:
        # Show model information
        ModelSelector.render_model_info(selected_model)
        
        # Parameter configuration
        basic_params = ParameterConfiguration.render_basic_parameters()
        selected_features = ParameterConfiguration.render_features_selection(selected_model)
        output_options = ParameterConfiguration.render_output_options(selected_model)
        query_fields = ParameterConfiguration.render_query_fields(selected_model)

        # Combine all parameters
        all_params = basic_params.copy()
        if query_fields:
            # queryFields requires both the feature flag and the field list.
            selected_features = list(selected_features)
            if 'queryFields' not in selected_features:
                selected_features.append('queryFields')
            all_params['queryFields'] = query_fields
        if selected_features:
            all_params['features'] = selected_features
        if output_options:
            all_params['output'] = output_options
        
        # Auto mode placeholder
        render_auto_mode_placeholder()
        
        # Workflow tabs: single document vs batch analysis
        single_tab, batch_tab = st.tabs(["📄 Single Document", "🗂️ Batch Analysis"])

        with single_tab:
            render_single_document_tab(client, selected_model, all_params)

        with batch_tab:
            render_batch_analysis_tab(client, selected_model, all_params)
    
    else:
        st.info("👆 Please select a Document Intelligence model from the sidebar to begin.")
    
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using [Streamlit](https://streamlit.io/) and "
        "[Azure Document Intelligence 4.0](https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/) REST API"
    )


if __name__ == "__main__":
    main()