"""
Document processing utilities for Azure Document Intelligence Streamlit demo.
Handles file uploads, validation, conversion, and basic document operations.
"""

import io
import base64
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw
import pdf2image
import streamlit as st

from config import SUPPORTED_FORMATS, ELEMENT_COLORS
from logging_config import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Handles document processing and validation."""
    
    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file format and size.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file extension
        file_extension = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else ''
        
        supported_extensions = []
        for format_info in SUPPORTED_FORMATS.values():
            supported_extensions.extend([ext.lower().lstrip('.') for ext in format_info['extensions']])
        
        if file_extension not in supported_extensions:
            return False, f"Unsupported file format: .{file_extension}. Supported formats: {', '.join(supported_extensions)}"
        
        # Check file size (in MB)
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        max_size = 500  # MB for paid tier
        
        if file_size_mb > max_size:
            return False, f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({max_size} MB)"
        
        return True, "File is valid"
    
    @staticmethod
    def get_file_info(uploaded_file) -> Dict[str, Any]:
        """
        Get information about the uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Dictionary with file information
        """
        if not uploaded_file:
            return {}
        
        file_size_bytes = len(uploaded_file.getvalue())
        file_size_mb = file_size_bytes / (1024 * 1024)
        file_extension = uploaded_file.name.lower().split('.')[-1] if '.' in uploaded_file.name else 'unknown'
        
        return {
            'name': uploaded_file.name,
            'size_bytes': file_size_bytes,
            'size_mb': round(file_size_mb, 2),
            'type': uploaded_file.type,
            'extension': file_extension
        }
    
    @staticmethod
    def convert_to_images(file_data: bytes, file_type: str) -> List[Image.Image]:
        """
        Convert document to PIL Images for display.
        
        Args:
            file_data: Raw file bytes
            file_type: File extension or MIME type
            
        Returns:
            List of PIL Images (one per page)
        """
        images = []
        
        # Validate input data
        if not file_data or len(file_data) == 0:
            st.error("Document data is empty or corrupted")
            return images
        
        try:
            if file_type.lower() in ['pdf', 'application/pdf']:
                # Check if file_data is valid PDF
                if not file_data.startswith(b'%PDF'):
                    st.error("File does not appear to be a valid PDF document")
                    return images
                
                # Convert PDF to images with better error handling
                try:
                    images = pdf2image.convert_from_bytes(
                        file_data,
                        dpi=150,
                        first_page=1,
                        last_page=10,  # Limit to first 10 pages for display
                        fmt='RGB',
                        thread_count=1,  # Reduce thread count for stability
                        use_pdftocairo=False  # Use poppler instead of cairo
                    )
                except Exception as pdf_error:
                    # Try alternative approach with different settings
                    try:
                        images = pdf2image.convert_from_bytes(
                            file_data,
                            dpi=100,  # Lower DPI
                            first_page=1,
                            last_page=5,   # Even fewer pages
                            fmt='RGB',
                            thread_count=1
                        )
                        if not images:
                            raise Exception("No pages could be converted")
                    except Exception as fallback_error:
                        st.error(f"PDF conversion failed: {str(pdf_error)}. Fallback also failed: {str(fallback_error)}")
                        st.info("💡 **Tip**: The PDF might be corrupted, password-protected, or in an unsupported format. Try a different PDF file.")
                        return images
                        
            elif file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'] or file_type.startswith('image/'):
                # Open image file with better error handling
                try:
                    # Create a BytesIO object for the image data
                    image_stream = io.BytesIO(file_data)
                    image = Image.open(image_stream)
                    
                    # Verify the image is valid
                    image.verify()
                    
                    # Reopen for actual use (verify() closes the file)
                    image_stream.seek(0)
                    image = Image.open(image_stream)
                    
                    # Convert to RGB if needed
                    if image.mode not in ['RGB', 'RGBA']:
                        image = image.convert('RGB')
                    elif image.mode == 'RGBA':
                        # Convert RGBA to RGB with white background
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                        
                    images = [image]
                    
                except Exception as img_error:
                    st.error(f"Image processing failed: {str(img_error)}")
                    st.info("💡 **Tip**: The image might be corrupted or in an unsupported format. Try a different image file.")
                    return images
            else:
                st.error(f"Unsupported file type for preview: {file_type}")
                st.info("💡 **Tip**: Supported formats are PDF, JPG, PNG, BMP, and TIFF")
                
        except Exception as e:
            st.error(f"Error converting document to images: {str(e)}")
            st.info("💡 **Tip**: Try a different document or check if the file is corrupted.")
            
        return images
    
    @staticmethod
    def draw_bounding_boxes(image: Image.Image, bounding_boxes: List[Dict[str, Any]], element_type: str = 'text', scale_x: float = None, scale_y: float = None) -> Image.Image:
        """
        Draw bounding boxes on an image.
        
        Args:
            image: PIL Image
            bounding_boxes: List of bounding box data
            element_type: Type of elements (affects color)
            scale_x: Factor to scale X coordinates from inches to image pixels
            scale_y: Factor to scale Y coordinates from inches to image pixels
            
        Returns:
            PIL Image with bounding boxes drawn
        """
        if not bounding_boxes:
            logger.debug(f"No bounding boxes provided for element_type: {element_type}")
            return image
        
        logger.debug(f"Drawing {len(bounding_boxes)} bounding boxes for element_type: {element_type}")
        logger.debug(f"Image size: {image.width}x{image.height}, scale_x: {scale_x:.2f}, scale_y: {scale_y:.2f}")
        
        # Create a copy of the image to draw on
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)
        
        # Calculate scale factors if not provided
        if scale_x is None:
            scale_x = 150.0 / 72.0  # Default scale factor
        if scale_y is None:
            scale_y = scale_x  # Use same scale for Y if not specified
        
        # Get color for this element type
        color = ELEMENT_COLORS.get(element_type, '#FF0000')
        logger.debug(f"Using color {color} for element_type: {element_type}")
        
        # Try to load a font, fallback to default
        try:
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 12)
                except:
                    font = ImageFont.load_default()
        except:
            font = None
        
        for bbox in bounding_boxes:
            polygon = bbox.get('polygon', [])
            if len(polygon) >= 6:  # At least 3 points (x,y pairs)
                # Convert polygon to list of tuples and scale coordinates
                points = []
                for i in range(0, len(polygon), 2):
                    if i + 1 < len(polygon):
                        # Apply scale factors to convert from inches to image pixels
                        x = max(0, min(int(polygon[i] * scale_x), image.width))
                        y = max(0, min(int(polygon[i + 1] * scale_y), image.height))
                        points.append((x, y))
                
                logger.debug(f"Original polygon: {polygon[:8]}... -> Scaled points: {points[:4]}...")
                
                # Additional debug for coordinate issues
                if len(points) >= 2:
                    logger.debug(f"First point: ({polygon[0]:.3f}, {polygon[1]:.3f}) -> ({points[0][0]}, {points[0][1]}) [scale: {scale_x:.2f}, {scale_y:.2f}]")
                
                if len(points) >= 3:
                    # Draw polygon outline with transparency
                    draw.polygon(points, outline=color, width=2)
                    
                    # Fill with semi-transparent color
                    if len(points) == 4:  # Rectangle
                        # Create a semi-transparent overlay
                        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
                        overlay_draw = ImageDraw.Draw(overlay)
                        
                        # Convert hex color to RGB with alpha
                        rgb_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                        rgba_color = rgb_color + (30,)  # Low alpha for transparency
                        
                        overlay_draw.polygon(points, fill=rgba_color)
                        annotated_image = Image.alpha_composite(annotated_image.convert('RGBA'), overlay).convert('RGB')
                        draw = ImageDraw.Draw(annotated_image)
                    
                    # Draw confidence score and content preview
                    confidence = bbox.get('confidence', 0)
                    content = bbox.get('content', '')
                    
                    if len(points) > 0:
                        x, y = points[0]
                        
                        # Draw confidence score
                        if confidence > 0:
                            conf_text = f"{confidence:.2f}"
                            if font:
                                draw.text((x, y - 20), conf_text, fill=color, font=font)
                            else:
                                draw.text((x, y - 15), conf_text, fill=color)
                        
                        # Draw content preview (first few characters)
                        if content and len(content) > 0:
                            preview = content[:20] + "..." if len(content) > 20 else content
                            preview = preview.replace('\n', ' ').replace('\r', ' ')
                            
                            if font:
                                draw.text((x, y + 5), preview, fill=color, font=font)
                            else:
                                draw.text((x, y + 5), preview, fill=color)
        
        return annotated_image
    
    @staticmethod
    def create_annotated_images(images: List[Image.Image], bounding_boxes_data: Dict[str, List], scale_x: float = None, scale_y: float = None, scale_factor: float = None) -> List[Image.Image]:
        """
        Create annotated images with all bounding box types.
        
        Args:
            images: List of original PIL Images
            bounding_boxes_data: Dictionary with bounding boxes by type
            scale_x: Factor to scale X coordinates from inches to image pixels
            scale_y: Factor to scale Y coordinates from inches to image pixels
            
        Returns:
            List of annotated PIL Images
        """
        # Handle backward compatibility for single scale_factor
        if scale_factor is not None and scale_x is None and scale_y is None:
            scale_x = scale_factor
            scale_y = scale_factor
        
        annotated_images = []
        
        for page_idx, image in enumerate(images):
            annotated_image = image.copy()
            
            # Draw different types of bounding boxes
            for element_type, boxes in bounding_boxes_data.items():
                # Filter boxes for current page
                page_boxes = [box for box in boxes if box.get('page', 0) == page_idx]
                
                logger.debug(f"Page {page_idx}: Found {len(page_boxes)} boxes of type {element_type}")
                
                if page_boxes:
                    annotated_image = DocumentProcessor.draw_bounding_boxes(
                        annotated_image, page_boxes, element_type, scale_x, scale_y
                    )
            
            annotated_images.append(annotated_image)
        
        return annotated_images
    
    @staticmethod
    def encode_image_for_display(image: Image.Image, format: str = 'PNG') -> str:
        """
        Encode PIL Image as base64 string for HTML display.
        
        Args:
            image: PIL Image
            format: Image format (PNG, JPEG)
            
        Returns:
            Base64 encoded image string
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_str}"
    
    @staticmethod
    def create_sample_documents() -> Dict[str, Dict[str, Any]]:
        """
        Create a dictionary of sample documents for demo purposes.
        
        Returns:
            Dictionary with sample document information
        """
        samples = {
            "Receipt Sample": {
                "description": "Sample receipt for testing receipt model",
                "model": "prebuilt-receipt",
                "url": "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-receipt.jpg"
            },
            "Invoice Sample": {
                "description": "Sample invoice for testing invoice model", 
                "model": "prebuilt-invoice",
                "url": "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"
            },
            "Business Card Sample": {
                "description": "Sample business card for testing business card model",
                "model": "prebuilt-businessCard",
                "url": "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-business-card.jpg"
            },
            "ID Document Sample": {
                "description": "Sample ID document for testing ID document model",
                "model": "prebuilt-idDocument", 
                "url": "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-id.jpg"
            }
        }
        return samples
    
    @staticmethod
    def download_sample_document(url: str) -> Optional[bytes]:
        """
        Download a sample document from URL.
        
        Args:
            url: Document URL
            
        Returns:
            Document bytes or None if failed
        """
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except requests.exceptions.Timeout:
            st.error("Sample document download timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to sample document URL. Please check your internet connection.")
        except Exception as e:
            st.error(f"Error downloading sample document: {str(e)}")
        
        return None


class ResultsFormatter:
    """Formats Document Intelligence analysis results for display."""
    
    @staticmethod
    def format_confidence_score(confidence: float) -> str:
        """
        Format confidence score with color coding.
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            HTML formatted confidence score
        """
        percentage = confidence * 100
        
        if percentage >= 90:
            color = "green"
        elif percentage >= 70:
            color = "orange"
        else:
            color = "red"
        
        return f'<span style="color: {color}; font-weight: bold">{percentage:.1f}%</span>'
    
    @staticmethod
    def create_fields_table(fields_data: Dict[str, Any]) -> str:
        """
        Create HTML table for fields display.
        
        Args:
            fields_data: Formatted fields data
            
        Returns:
            HTML table string
        """
        if not fields_data:
            return "<p>No fields extracted</p>"
        
        html = "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<tr style='background-color: #f0f0f0;'><th style='border: 1px solid #ddd; padding: 8px;'>Field</th><th style='border: 1px solid #ddd; padding: 8px;'>Content</th><th style='border: 1px solid #ddd; padding: 8px;'>Confidence</th></tr>"
        
        for doc_type, fields in fields_data.items():
            html += f"<tr style='background-color: #e8f4f8;'><td colspan='3' style='border: 1px solid #ddd; padding: 8px; font-weight: bold;'>{doc_type}</td></tr>"
            
            for field_name, field_info in fields.items():
                content = str(field_info.get('content', ''))
                confidence = field_info.get('confidence', 0)
                
                # Truncate long content
                if len(content) > 100:
                    content = content[:97] + "..."
                
                confidence_html = ResultsFormatter.format_confidence_score(confidence)
                
                html += f"<tr>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{field_name}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{content}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{confidence_html}</td>"
                html += f"</tr>"
        
        html += "</table>"
        return html
    
    @staticmethod
    def format_json_with_syntax_highlighting(json_data: Dict[str, Any]) -> str:
        """
        Format JSON with basic syntax highlighting.
        
        Args:
            json_data: JSON data to format
            
        Returns:
            HTML formatted JSON string
        """
        import json
        
        try:
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            # Basic syntax highlighting (could be enhanced with a proper library)
            json_str = json_str.replace('"', '<span style="color: #d73a49;">"</span>')
            json_str = json_str.replace(':', '<span style="color: #005cc5;">:</span>')
            json_str = json_str.replace(',', '<span style="color: #005cc5;">,</span>')
            
            return f"<pre style='background-color: #f6f8fa; padding: 10px; border-radius: 5px; overflow-x: auto;'><code>{json_str}</code></pre>"
        
        except Exception:
            return f"<pre>{str(json_data)}</pre>"


def create_document_viewer_html(images: List[str], current_page: int = 0) -> str:
    """
    Create HTML for document viewer with navigation.
    
    Args:
        images: List of base64 encoded image strings
        current_page: Current page index
        
    Returns:
        HTML string for document viewer
    """
    if not images:
        return "<p>No document to display</p>"
    
    html = f"""
    <div style="text-align: center; border: 1px solid #ddd; border-radius: 5px; padding: 10px;">
        <div style="margin-bottom: 10px;">
            <span style="font-weight: bold;">Page {current_page + 1} of {len(images)}</span>
        </div>
        <div style="max-height: 600px; overflow: auto;">
            <img src="{images[current_page]}" style="max-width: 100%; height: auto;" />
        </div>
    </div>
    """
    
    return html