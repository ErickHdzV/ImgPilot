"""Module for image optimization and compression."""
import io
from PIL import Image
from typing import Optional, Tuple


def optimize_image_quality(
    image: Image.Image,
    target_size_bytes: Optional[int] = None,
    quality_range: Tuple[int, int] = (50, 95),
    format_type: str = 'WEBP'
) -> Tuple[Image.Image, int]:
    """
    Optimizes image quality to reach a target size.
    Uses binary search to find the best quality.
    
    Args:
        image: PIL image to optimize
        target_size_bytes: Target size in bytes (None to use maximum quality)
        quality_range: Quality range to test (min, max)
        format_type: Output format ('WEBP' or 'AVIF')
    
    Returns:
        Tuple (optimized image, final quality used)
    """
    if target_size_bytes is None:
        # No target size, use maximum quality
        return image.copy(), quality_range[1]
    
    min_quality, max_quality = quality_range
    best_quality = max_quality
    best_image = image.copy()
    
    # Binary search to find the best quality
    while min_quality <= max_quality:
        mid_quality = (min_quality + max_quality) // 2
        
        # Test this quality
        test_image = _compress_image(image, mid_quality, format_type)
        test_size = _get_image_size_bytes(test_image, format_type)
        
        if test_size <= target_size_bytes:
            # Acceptable size, try higher quality
            best_quality = mid_quality
            best_image = test_image
            min_quality = mid_quality + 1
        else:
            # Size too large, reduce quality
            max_quality = mid_quality - 1
    
    return best_image, best_quality


def _compress_image(image: Image.Image, quality: int, format_type: str) -> Image.Image:
    """
    Compresses an image with a specific quality in memory.
    
    Args:
        image: Image to compress
        quality: Compression quality (0-100)
        format_type: Output format
    
    Returns:
        Compressed image (copy)
    """
    buffer = io.BytesIO()
    
    # Convert to RGB if necessary
    img_copy = image.copy()
    if img_copy.mode not in ('RGB', 'RGBA'):
        if format_type == 'AVIF' and img_copy.mode in ('RGBA', 'LA', 'P'):
            # Keep transparency for AVIF
            if img_copy.mode == 'P' and 'transparency' not in img_copy.info:
                img_copy = img_copy.convert('RGB')
            else:
                if img_copy.mode == 'RGBA':
                    pass  # Keep RGBA
                else:
                    img_copy = img_copy.convert('RGB')
    
    save_kwargs = {
        'format': format_type,
        'quality': quality,
    }
    
    if format_type == 'WEBP':
        save_kwargs['method'] = 6  # Best compression
    
    img_copy.save(buffer, **save_kwargs)
    buffer.seek(0)
    
    return Image.open(buffer)


def _get_image_size_bytes(image: Image.Image, format_type: str) -> int:
    """
    Gets the size in bytes of an image in memory.
    
    Args:
        image: PIL image
        format_type: Output format
    
    Returns:
        Size in bytes
    """
    buffer = io.BytesIO()
    
    save_kwargs = {
        'format': format_type,
        'quality': 80,  # Calidad por defecto para medir
    }
    
    if format_type == 'WEBP':
        save_kwargs['method'] = 6
    
    image.save(buffer, **save_kwargs)
    return len(buffer.getvalue())


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculates compression ratio.
    
    Args:
        original_size: Original size in bytes
        compressed_size: Compressed size in bytes
    
    Returns:
        Compression ratio (0.0 to 1.0, where lower is better)
    """
    if original_size == 0:
        return 0.0
    return compressed_size / original_size


def estimate_quality_for_size(
    image: Image.Image,
    target_size_bytes: int,
    format_type: str = 'WEBP'
) -> int:
    """
    Estimates quality needed to reach a target size.
    
    Args:
        image: Image to analyze
        target_size_bytes: Target size in bytes
        format_type: Output format
    
    Returns:
        Estimated quality (0-100)
    """
    # Test some qualities to estimate
    test_qualities = [95, 80, 65, 50, 35, 20]
    sizes = []
    
    for quality in test_qualities:
        test_img = _compress_image(image, quality, format_type)
        size = _get_image_size_bytes(test_img, format_type)
        sizes.append((quality, size))
    
    # Simple linear interpolation
    for i in range(len(sizes) - 1):
        q1, s1 = sizes[i]
        q2, s2 = sizes[i + 1]
        
        if s1 >= target_size_bytes >= s2:
            # Interpolate between these two points
            ratio = (target_size_bytes - s2) / (s1 - s2) if s1 != s2 else 0
            estimated_quality = int(q2 + ratio * (q1 - q2))
            return max(20, min(95, estimated_quality))
    
    # If target size is too large or too small
    if target_size_bytes >= sizes[0][1]:
        return 95
    else:
        return 20

