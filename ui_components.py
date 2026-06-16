"""
Reusable UI components for the Azure Document Intelligence Streamlit demo.
Contains functions for generating dynamic UI elements based on model selection.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import json

from config import (
    AZURE_DI_MODELS, API_PARAMETERS, AVAILABLE_FEATURES, OUTPUT_OPTIONS,
    MODEL_CATEGORIES, QUERY_FIELDS_MAX, get_model_features, get_models_by_category,
    is_feature_available, get_model_display_name,
    get_output_options_for_model, supports_query_fields
)


class ModelSelector:
    """Component for model selection and configuration."""
    
    @staticmethod
    def render_model_dropdown() -> Optional[str]:
        """
        Render the model selection dropdown.
        
        Returns:
            Selected model ID or None
        """
        st.sidebar.header("🤖 Model Selection")
        
        # Organize models by category
        categorized_models = get_models_by_category()
        
        # Create options list with categories
        options = []
        option_to_model = {}
        
        for category in MODEL_CATEGORIES:
            if category in categorized_models:
                options.append(f"━━━ {category} ━━━")
                for model_id in categorized_models[category]:
                    display_name = get_model_display_name(model_id)
                    options.append(f"  {display_name}")
                    option_to_model[f"  {display_name}"] = model_id
        
        # Find default model (prebuilt-layout) index
        default_index = 0
        layout_display_name = get_model_display_name("prebuilt-layout")
        layout_option = f"  {layout_display_name}"
        if layout_option in options:
            default_index = options.index(layout_option)
        
        # Model selection
        selected_option = st.sidebar.selectbox(
            "Choose a Document Intelligence model:",
            options,
            index=default_index,
            help="Select the Azure Document Intelligence model to use for analysis"
        )
        
        # Return model ID if valid selection
        if selected_option in option_to_model:
            return option_to_model[selected_option]
        
        return None
    
    @staticmethod
    def render_model_info(model_id: str):
        """
        Display information about the selected model.
        
        Args:
            model_id: Selected model ID
        """
        if not model_id or model_id not in AZURE_DI_MODELS:
            return
        
        model_info = AZURE_DI_MODELS[model_id]
        
        with st.sidebar.expander("ℹ️ Model Information", expanded=False):
            st.write(f"**Name:** {model_info['name']}")
            st.write(f"**Description:** {model_info['description']}")
            st.write(f"**Category:** {model_info['category']}")
            st.write(f"**Max Pages:** {model_info['max_pages']}")
            st.write(f"**Supported Formats:** {', '.join(model_info['supported_formats'])}")


class ParameterConfiguration:
    """Component for dynamic parameter configuration."""
    
    @staticmethod
    def render_basic_parameters() -> Dict[str, Any]:
        """
        Render basic API parameters.
        
        Returns:
            Dictionary of parameter values
        """
        st.sidebar.header("⚙️ Basic Parameters")
        
        params = {}
        
        # Pages parameter
        pages_config = API_PARAMETERS["pages"]
        params["pages"] = st.sidebar.text_input(
            pages_config["label"],
            value=pages_config["default"],
            placeholder=pages_config["placeholder"],
            help=pages_config["help"]
        )
        
        # Locale parameter
        locale_config = API_PARAMETERS["locale"]
        locale_options = [(label, value) for label, value in locale_config["options"]]
        selected_locale = st.sidebar.selectbox(
            locale_config["label"],
            options=locale_options,
            format_func=lambda x: x[0],
            help=locale_config["help"]
        )
        params["locale"] = selected_locale[1] if selected_locale else ""
        
        # String index type
        string_index_config = API_PARAMETERS["stringIndexType"]
        string_index_options = [(label, value) for label, value in string_index_config["options"]]
        selected_string_index = st.sidebar.selectbox(
            string_index_config["label"],
            options=string_index_options,
            format_func=lambda x: x[0],
            help=string_index_config["help"]
        )
        params["stringIndexType"] = selected_string_index[1] if selected_string_index else "textElements"
        
        # Output content format
        output_format_config = API_PARAMETERS["outputContentFormat"]
        output_format_options = [(label, value) for label, value in output_format_config["options"]]
        selected_output_format = st.sidebar.selectbox(
            output_format_config["label"],
            options=output_format_options,
            format_func=lambda x: x[0],
            help=output_format_config["help"]
        )
        params["outputContentFormat"] = selected_output_format[1] if selected_output_format else "text"
        
        return params
    
    @staticmethod
    def render_features_selection(model_id: str) -> List[str]:
        """
        Render feature selection checkboxes for the selected model.
        
        Args:
            model_id: Selected model ID
            
        Returns:
            List of selected features
        """
        if not model_id:
            return []
        
        available_features = get_model_features(model_id)
        if not available_features:
            return []
        
        st.sidebar.header("🔧 Features")
        
        selected_features = []
        
        for feature in available_features:
            if feature in AVAILABLE_FEATURES:
                feature_info = AVAILABLE_FEATURES[feature]
                is_selected = st.sidebar.checkbox(
                    feature_info["label"],
                    help=feature_info["description"]
                )
                if is_selected:
                    selected_features.append(feature)
        
        return selected_features
    
    @staticmethod
    def render_output_options(model_id: str) -> List[str]:
        """
        Render additional output options valid for the selected model.

        Args:
            model_id: Selected model ID

        Returns:
            List of selected output options
        """
        available_outputs = get_output_options_for_model(model_id)
        if not available_outputs:
            return []

        st.sidebar.header("📤 Additional Output")

        selected_outputs = []

        for output_key, output_info in available_outputs.items():
            is_selected = st.sidebar.checkbox(
                output_info["label"],
                help=output_info["description"],
                key=f"output_{output_key}"
            )
            if is_selected:
                selected_outputs.append(output_key)

        return selected_outputs

    @staticmethod
    def render_query_fields(model_id: str) -> List[str]:
        """
        Render the query fields add-on input for the selected model.

        Args:
            model_id: Selected model ID

        Returns:
            List of query field names (empty if unused or unsupported)
        """
        if not supports_query_fields(model_id):
            return []

        st.sidebar.header("🔎 Query Fields")

        raw = st.sidebar.text_input(
            "Custom fields to extract",
            value="",
            placeholder="e.g., InvoiceNumber, BillingAddress",
            help=(
                "Add-on capability: comma-separated field names to extract beyond the "
                f"model's schema (max {QUERY_FIELDS_MAX}). Use camelCase or PascalCase for "
                "multi-word names. Premium add-on; not supported on tax W-2/1098/1099."
            )
        )

        # Parse, trim, drop blanks, de-duplicate while preserving order.
        fields = []
        for name in raw.split(","):
            name = name.strip()
            if name and name not in fields:
                fields.append(name)

        if len(fields) > QUERY_FIELDS_MAX:
            st.sidebar.warning(
                f"Only the first {QUERY_FIELDS_MAX} query fields are sent; "
                f"{len(fields) - QUERY_FIELDS_MAX} extra ignored."
            )
            fields = fields[:QUERY_FIELDS_MAX]

        return fields


class FileUploadSection:
    """Component for file upload and sample documents."""
    
    @staticmethod
    def render_upload_section():
        """
        Render the file upload section with multiple options.
        
        Returns:
            Tuple of (uploaded_file, file_source_type)
        """
        st.header("📁 Document Upload")
        
        # Upload method selection
        upload_method = st.radio(
            "Choose upload method:",
            ["File Upload", "URL", "Sample Documents"],
            horizontal=True
        )
        
        uploaded_file = None
        source_type = None
        
        if upload_method == "File Upload":
            uploaded_file = st.file_uploader(
                "Choose a document file",
                type=['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'],
                help="Upload a document in supported format (PDF, JPG, PNG, BMP, TIFF)"
            )
            source_type = "upload"
            
        elif upload_method == "URL":
            url = st.text_input(
                "Enter document URL:",
                placeholder="https://example.com/document.pdf",
                help="Enter a direct URL to a document file"
            )
            
            if url:
                if st.button("Load from URL"):
                    with st.spinner("Downloading document..."):
                        from document_processor import DocumentProcessor
                        file_data = DocumentProcessor.download_sample_document(url)
                        
                        if file_data:
                            # Create a mock uploaded file object
                            import io
                            uploaded_file = io.BytesIO(file_data)
                            uploaded_file.name = url.split('/')[-1]
                            source_type = "url"
                        else:
                            st.error("Failed to download document from URL")
        
        elif upload_method == "Sample Documents":
            from document_processor import DocumentProcessor
            samples = DocumentProcessor.create_sample_documents()
            
            sample_names = list(samples.keys())
            selected_sample = st.selectbox(
                "Choose a sample document:",
                options=sample_names,
                help="Select a sample document for testing"
            )
            
            if selected_sample and st.button("Load Sample"):
                with st.spinner("Loading sample document..."):
                    sample_info = samples[selected_sample]
                    file_data = DocumentProcessor.download_sample_document(sample_info["url"])
                    
                    if file_data:
                        # Create a mock uploaded file object
                        import io
                        uploaded_file = io.BytesIO(file_data)
                        uploaded_file.name = f"{selected_sample}.{sample_info['url'].split('.')[-1]}"
                        source_type = "sample"
                        
                        # Store recommended model in session state
                        st.session_state.recommended_model = sample_info["model"]
                    else:
                        st.error("Failed to load sample document")
        
        return uploaded_file, source_type


class ResultsDisplay:
    """Component for displaying analysis results in multiple formats."""
    
    @staticmethod
    def render_results_tabs(analysis_result: Dict[str, Any], raw_result: Dict[str, Any]):
        """
        Render results in tabbed interface.
        
        Args:
            analysis_result: Processed analysis result
            raw_result: Raw API response
        """
        tab1, tab2, tab3 = st.tabs(["📋 Fields", "📝 Markdown", "🔧 Raw JSON"])
        
        with tab1:
            ResultsDisplay._render_fields_view(analysis_result)
        
        with tab2:
            ResultsDisplay._render_markdown_view(analysis_result)
        
        with tab3:
            ResultsDisplay._render_json_view(raw_result)
    
    @staticmethod
    def _render_fields_view(analysis_result: Dict[str, Any]):
        """Render the fields view similar to Azure DI Studio."""
        from document_processor import ResultsFormatter
        from azure_di_client import DocumentAnalysisResult
        
        result = DocumentAnalysisResult(analysis_result)
        formatted_fields = result.get_formatted_fields()
        
        if formatted_fields:
            # Create expandable sections for each document type
            for doc_type, fields in formatted_fields.items():
                with st.expander(f"📄 {doc_type.title()}", expanded=True):
                    # Display fields in a nice format
                    for field_name, field_info in fields.items():
                        col1, col2, col3 = st.columns([2, 3, 1])
                        
                        with col1:
                            st.write(f"**{field_name}**")
                        
                        with col2:
                            content = field_info.get('content', '')
                            if len(str(content)) > 100:
                                st.write(f"{str(content)[:97]}...")
                            else:
                                st.write(str(content))
                        
                        with col3:
                            confidence = field_info.get('confidence', 0) * 100
                            if confidence >= 90:
                                st.success(f"{confidence:.1f}%")
                            elif confidence >= 70:
                                st.warning(f"{confidence:.1f}%")
                            else:
                                st.error(f"{confidence:.1f}%")
        else:
            st.info("No structured fields extracted. Try using a more specific model for your document type.")
    
    @staticmethod
    def _render_markdown_view(analysis_result: Dict[str, Any]):
        """Render the markdown view."""
        from azure_di_client import DocumentAnalysisResult
        
        result = DocumentAnalysisResult(analysis_result)
        markdown_content = result.to_markdown()
        
        if markdown_content.strip():
            # Add copy button
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📋 Copy", key="copy_markdown"):
                    st.write("Content copied to clipboard!")
            
            # Display markdown
            st.markdown("### Extracted Content")
            
            # Check the outputContentFormat parameter used in the analysis
            analysis_params = st.session_state.get('analysis_params', {})
            output_format = analysis_params.get('outputContentFormat', 'text')
            
            if output_format == 'text':
                # For text format, wrap in code block to preserve formatting and line breaks
                st.markdown(f"```\n{markdown_content}\n```")
            else:
                # For markdown format, render as normal markdown
                st.markdown(markdown_content)
        else:
            st.info("No markdown content available.")
    
    @staticmethod
    def _render_json_view(raw_result: Dict[str, Any]):
        """Render the raw JSON view."""
        # Add download and copy buttons
        col1, col2, col3 = st.columns([2, 1, 1])

        json_str = json.dumps(raw_result, indent=2, ensure_ascii=False)

        with col2:
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name="analysis_result.json",
                mime="application/json"
            )

        with col3:
            # Copy to clipboard button using JavaScript
            copy_button_html = f"""
            <button onclick="copyToClipboard()" style="
                background-color: #0e1117;
                color: #ffffff;
                border: 1px solid #ffffff33;
                border-radius: 0.5rem;
                padding: 0.25rem 0.75rem;
                cursor: pointer;
                font-size: 14px;
                height: 38px;
                width: 100%;
                margin-top: 0px;
            ">
                📋 Copy JSON
            </button>
            <script>
            function copyToClipboard() {{
                const jsonText = {json.dumps(json_str)};
                navigator.clipboard.writeText(jsonText).then(function() {{
                    const btn = event.target;
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '✅ Copied!';
                    btn.style.backgroundColor = '#00cc00';
                    setTimeout(function() {{
                        btn.innerHTML = originalText;
                        btn.style.backgroundColor = '#0e1117';
                    }}, 2000);
                }}, function(err) {{
                    alert('Failed to copy: ' + err);
                }});
            }}
            </script>
            """
            st.components.v1.html(copy_button_html, height=50)

        # Display JSON with syntax highlighting
        st.markdown("### Raw Analysis Result")
        st.json(raw_result)


class StatusDisplay:
    """Component for displaying analysis status and progress."""
    
    @staticmethod
    def show_progress(message: str):
        """Show progress message."""
        st.info(f"⏳ {message}")
    
    @staticmethod
    def show_success(message: str):
        """Show success message."""
        st.success(f"✅ {message}")
    
    @staticmethod
    def show_error(message: str):
        """Show error message."""
        st.error(f"❌ {message}")
    
    @staticmethod
    def show_warning(message: str):
        """Show warning message."""
        st.warning(f"⚠️ {message}")


class DocumentViewer:
    """Component for displaying documents with annotations."""
    
    @staticmethod
    def render_document_viewer(images: List[str], bounding_boxes: Dict = None):
        """
        Render document viewer with navigation and annotations.
        
        Args:
            images: List of base64 encoded images
            bounding_boxes: Optional bounding boxes data
        """
        if not images:
            st.warning("No document to display")
            return
        
        st.header("📄 Document Viewer")
        
        # Page navigation
        if len(images) > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                current_page = st.selectbox(
                    "Page:",
                    range(len(images)),
                    format_func=lambda x: f"Page {x + 1} of {len(images)}"
                )
        else:
            current_page = 0
        
        # Display options
        col1, col2 = st.columns([3, 1])
        with col2:
            show_annotations = st.checkbox("Show Annotations", value=True)
            zoom_level = st.slider("Zoom", 0.5, 2.0, 1.0, 0.1)
        
        # Display image
        if current_page < len(images):
            image_html = f"""
            <div style="text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 10px;">
                <img src="{images[current_page]}" 
                     style="max-width: 100%; height: auto; transform: scale({zoom_level});" 
                     alt="Document page {current_page + 1}" />
            </div>
            """
            st.markdown(image_html, unsafe_allow_html=True)


def render_connection_status(client):
    """
    Render connection status indicator.
    
    Args:
        client: Azure Document Intelligence client
    """
    with st.sidebar.expander("🔌 Connection Status", expanded=False):
        if client:
            success, message = client.test_connection()
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.error("No Azure DI client configured. Please check your environment variables or Streamlit secrets.")


def render_auto_mode_placeholder():
    """Render placeholder for future auto mode feature."""
    st.sidebar.header("🤖 Future: Auto Mode")
    
    with st.sidebar.expander("Coming Soon", expanded=False):
        st.info(
            "**Auto Mode** will automatically:\n"
            "- Detect document type\n"
            "- Select optimal model\n"
            "- Configure best parameters\n"
            "- Powered by LLM analysis"
        )
        
        auto_enabled = st.checkbox("Enable Auto Mode", disabled=True)
        if auto_enabled:
            st.warning("Auto mode is not yet implemented.")