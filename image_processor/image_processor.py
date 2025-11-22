"""Main image processor."""
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image

from image_processor.converter import (
    convert_to_webp, convert_to_avif, convert_to_png,
    convert_to_jpg, convert_to_ico, convert_to_svg
)
from image_processor.resizer import resize_image
from utils.file_handler import get_file_size, format_file_size


class ImageProcessor:
    """Class for processing and converting images."""
    
    # Format mapping to conversion functions
    CONVERTERS = {
        'webp': convert_to_webp,
        'avif': convert_to_avif,
        'png': convert_to_png,
        'jpg': convert_to_jpg,
        'ico': convert_to_ico,
        'svg': convert_to_svg,
    }
    
    @staticmethod
    def process_image(
        image_path: str,
        output_path: str,
        format_type: str,
        quality: int = 80,
        preserve_exif: bool = True,
        resize_config: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Processes an image: resizes (if necessary) and converts to specified format.
        
        Args:
            image_path: Path of original image
            output_path: Path where to save processed image
            format_type: Output format ('webp', 'avif', 'png', 'jpg', 'ico')
            quality: Compression quality (0-100)
            preserve_exif: Whether to preserve EXIF metadata
            resize_config: Dictionary with resize configuration (optional)
                - width: Width in pixels
                - height: Height in pixels
                - maintain_aspect: Whether to maintain aspect ratio
                - method: Resize method
        
        Returns:
            Tuple (success, error_message)
        """
        temp_resized_path = None
        
        try:
            # If there's resizing, process first
            source_path = image_path
            if resize_config and (resize_config.get('width') or resize_config.get('height')):
                try:
                    with Image.open(image_path) as img:
                        resized_img = resize_image(
                            img,
                            resize_config.get('width'),
                            resize_config.get('height'),
                            resize_config.get('maintain_aspect', True),
                            resize_config.get('method', 'LANCZOS')
                        )
                        # Create temporary file for resized image
                        temp_fd, temp_resized_path = tempfile.mkstemp(suffix='.png')
                        os.close(temp_fd)
                        resized_img.save(temp_resized_path, format='PNG')
                        source_path = temp_resized_path
                except Exception as e:
                    return False, f"Error resizing: {str(e)}"
            
            # Convert to specified format
            converter = ImageProcessor.CONVERTERS.get(format_type)
            if not converter:
                return False, f"Formato no soportado: {format_type}"
            
            success = converter(
                source_path,
                output_path,
                quality=quality,
                preserve_exif=preserve_exif
            )
            
            if not success:
                return False, f"Error converting to {format_type.upper()}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error: {str(e)}"
        
        finally:
            # Clean up temporary file if it exists
            if temp_resized_path and os.path.exists(temp_resized_path):
                try:
                    os.unlink(temp_resized_path)
                except Exception:
                    pass
    
    @staticmethod
    def calculate_compression_stats(
        original_path: str,
        optimized_path: str
    ) -> Dict[str, any]:
        """
        Calculates compression statistics between original and optimized image.
        
        Args:
            original_path: Path of original image
            optimized_path: Path of optimized image
        
        Returns:
            Dictionary with statistics:
                - original_size: Original size in bytes
                - optimized_size: Optimized size in bytes
                - saved_bytes: Bytes saved
                - compression_ratio: Compression percentage
        """
        original_size = get_file_size(original_path)
        optimized_size = get_file_size(optimized_path)
        saved_bytes = original_size - optimized_size
        compression_ratio = (saved_bytes / original_size * 100) if original_size > 0 else 0
        
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'saved_bytes': saved_bytes,
            'compression_ratio': compression_ratio,
            'original_size_formatted': format_file_size(original_size),
            'optimized_size_formatted': format_file_size(optimized_size),
            'saved_bytes_formatted': format_file_size(saved_bytes),
        }

