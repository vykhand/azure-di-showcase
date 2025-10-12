"""
Simple but effective annotation system that draws directly on the image.
This avoids HTML complexity and works reliably in Streamlit.
"""

from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import streamlit as st


class SimpleDocumentAnnotator:
    """Creates image-based annotations with overlaid bounding boxes."""
    
    def __init__(self):
        self.element_styles = {
            'text': {'color': '#007ACC', 'width': 2},
            'tables': {'color': '#00B04F', 'width': 3},  
            'paragraphs': {'color': '#9932CC', 'width': 2},
            'figures': {'color': '#DC143C', 'width': 3},
            'keyValuePairs': {'color': '#FF8C00', 'width': 2}
        }
    
    def annotate_image(
        self, 
        image: Image.Image, 
        bounding_boxes: Dict[str, List[Dict]], 
        page_idx: int,
        scale_x: float, 
        scale_y: float,
        show_labels: bool = True
    ) -> Image.Image:
        """
        Create annotated image with bounding boxes drawn directly on it.
        
        Args:
            image: PIL Image to annotate
            bounding_boxes: Dictionary of bounding box data by type
            page_idx: Current page index (0-based)
            scale_x: Scaling factor for X coordinates 
            scale_y: Scaling factor for Y coordinates
            show_labels: Whether to show text labels
            
        Returns:
            Annotated PIL Image
        """
        # Create a copy to draw on
        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 14)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                small_font = font
        
        # Filter boxes for current page
        page_boxes = self._filter_boxes_for_page(bounding_boxes, page_idx)
        
        # Draw annotations by type (in order of priority)
        draw_order = ['paragraphs', 'figures', 'tables', 'keyValuePairs', 'text']
        
        for box_type in draw_order:
            boxes = page_boxes.get(box_type, [])
            if not boxes:
                continue
                
            style = self.element_styles.get(box_type, {'color': '#FF0000', 'width': 2})
            
            for i, box in enumerate(boxes):
                self._draw_single_box(
                    draw, box, box_type, style, scale_x, scale_y, 
                    image.width, image.height, font, small_font, show_labels
                )
        
        return annotated
    
    def _filter_boxes_for_page(self, bounding_boxes: Dict[str, List], page_idx: int) -> Dict[str, List]:
        """Filter bounding boxes for specific page."""
        page_boxes = {}
        for box_type, boxes in bounding_boxes.items():
            page_boxes[box_type] = [box for box in boxes if box.get('page', 0) == page_idx]
        return page_boxes
    
    def _draw_single_box(
        self, 
        draw: ImageDraw.Draw, 
        box: Dict, 
        box_type: str, 
        style: Dict,
        scale_x: float, 
        scale_y: float, 
        img_width: int, 
        img_height: int,
        font, 
        small_font,
        show_labels: bool
    ):
        """Draw a single bounding box."""
        polygon = box.get('polygon', [])
        if len(polygon) != 8:  # Must be exactly 4 vertices
            return
        
        # Convert and scale coordinates
        points = []
        for i in range(0, 8, 2):
            x = max(0, min(int(polygon[i] * scale_x), img_width))
            y = max(0, min(int(polygon[i + 1] * scale_y), img_height))
            points.append((x, y))
        
        if len(points) < 3:
            return
        
        color = style['color']
        width = style['width']
        
        # Draw the polygon outline
        draw.polygon(points, outline=color, width=width)
        
        # Add semi-transparent fill for better visibility
        if box_type in ['tables', 'figures']:
            # Convert hex color to RGB with alpha
            rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            fill_color = rgb_color + (30,)  # Low alpha for transparency
            draw.polygon(points, fill=fill_color, outline=color, width=width)
        
        # Add labels if requested
        if show_labels and points:
            self._add_label(draw, box, box_type, points[0], color, font, small_font)
    
    def _add_label(self, draw, box, box_type, position, color, font, small_font):
        """Add text label to the bounding box."""
        x, y = position
        
        # Create label text
        if box_type == 'text':
            content = box.get('content', '').strip()
            if len(content) > 30:
                label = content[:27] + '...'
            else:
                label = content
        elif box_type == 'tables':
            details = box.get('details', {})
            label = f"Table {details.get('rowCount', 0)}×{details.get('columnCount', 0)}"
        elif box_type == 'figures':
            details = box.get('details', {})
            label = f"Fig {details.get('id', '')}"
        elif box_type == 'paragraphs':
            label = f"¶ Paragraph"
        elif box_type == 'keyValuePairs':
            details = box.get('details', {})
            role = details.get('role', '').title()
            label = f"KV {role}" if role else "Key-Value"
        else:
            label = box_type.title()
        
        if not label:
            return
        
        # Position label above the box
        label_y = max(0, y - 20)
        
        # Draw label background
        bbox = draw.textbbox((x, label_y), label, font=small_font)
        bg_padding = 2
        bg_rect = [
            bbox[0] - bg_padding, 
            bbox[1] - bg_padding,
            bbox[2] + bg_padding, 
            bbox[3] + bg_padding
        ]
        
        draw.rectangle(bg_rect, fill='white', outline=color, width=1)
        
        # Draw label text
        draw.text((x, label_y), label, fill=color, font=small_font)
        
        # Add confidence if available and < 1.0
        confidence = box.get('confidence', 1.0)
        if confidence < 1.0:
            conf_text = f"{confidence:.0%}"
            conf_y = label_y + 15
            draw.text((x, conf_y), conf_text, fill=color, font=small_font)
    
    def create_legend_html(self) -> str:
        """Create legend showing annotation types and colors."""
        legend_items = []
        
        type_names = {
            'text': '📝 Text Lines',
            'tables': '📊 Tables', 
            'paragraphs': '📄 Paragraphs',
            'figures': '🖼️ Figures',
            'keyValuePairs': '🔗 Key-Value Pairs'
        }
        
        for box_type, style in self.element_styles.items():
            name = type_names.get(box_type, box_type)
            legend_items.append(f"""
                <div style="display: flex; align-items: center; margin-bottom: 6px;">
                    <div style="width: 24px; height: 14px; background-color: {style['color']}; 
                                margin-right: 10px; border: 1px solid #ccc; border-radius: 2px; opacity: 0.7;"></div>
                    <span style="font-size: 14px; color: #333;">{name}</span>
                </div>
            """)
        
        return f"""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #dee2e6; margin: 10px 0;">
            <div style="font-weight: bold; margin-bottom: 10px; color: #495057; font-size: 15px;">
                📍 Document Annotations
            </div>
            {''.join(legend_items)}
            <div style="font-size: 12px; color: #6c757d; margin-top: 10px; font-style: italic;">
                💡 Bounding boxes show detected document elements with labels
            </div>
        </div>
        """