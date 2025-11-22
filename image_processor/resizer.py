"""Module for image resizing."""
from PIL import Image
from typing import Optional, Tuple


# Available resize methods
RESIZE_METHODS = {
    'LANCZOS': Image.Resampling.LANCZOS,  # Best quality, slower
    'BICUBIC': Image.Resampling.BICUBIC,  # Good quality
    'BILINEAR': Image.Resampling.BILINEAR,  # Faster
    'NEAREST': Image.Resampling.NEAREST,  # Faster, lower quality
}


def resize_image(
    image: Image.Image,
    width: Optional[int] = None,
    height: Optional[int] = None,
    maintain_aspect: bool = True,
    method: str = 'LANCZOS'
) -> Image.Image:
    """
    Resizes an image according to specified parameters.
    
    Args:
        image: PIL image to resize
        width: Desired width (None to maintain proportion)
        height: Desired height (None to maintain proportion)
        maintain_aspect: Whether to maintain aspect ratio
        method: Resize method ('LANCZOS', 'BICUBIC', 'BILINEAR', 'NEAREST')
    
    Returns:
        Resized image
    
    Raises:
        ValueError: If parameters are invalid
    """
    if width is None and height is None:
        return image.copy()
    
    # Get resize method
    resize_method = RESIZE_METHODS.get(method.upper(), Image.Resampling.LANCZOS)
    
    original_width, original_height = image.size
    
    # Calculate final dimensions
    if maintain_aspect:
        if width is not None and height is not None:
            # Calculate scale factor to maintain proportion
            width_ratio = width / original_width
            height_ratio = height / original_height
            ratio = min(width_ratio, height_ratio)
            final_width = int(original_width * ratio)
            final_height = int(original_height * ratio)
        elif width is not None:
            # Maintain proportion based on width
            ratio = width / original_width
            final_width = width
            final_height = int(original_height * ratio)
        elif height is not None:
            # Maintain proportion based on height
            ratio = height / original_height
            final_width = int(original_width * ratio)
            final_height = height
        else:
            return image.copy()
    else:
        # Don't maintain proportion - use exact dimensions
        final_width = width if width is not None else original_width
        final_height = height if height is not None else original_height
    
    # Validate dimensions
    if final_width <= 0 or final_height <= 0:
        raise ValueError("Dimensions must be greater than 0")
    
    # Resize
    resized_image = image.resize((final_width, final_height), resize_method)
    
    return resized_image


def resize_image_from_path(
    image_path: str,
    output_path: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    maintain_aspect: bool = True,
    method: str = 'LANCZOS'
) -> Image.Image:
    """
    Resizes an image from a file path.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save resized image (optional)
        width: Desired width
        height: Desired height
        maintain_aspect: Whether to maintain proportion
        method: Resize method
    
    Returns:
        Resized image
    """
    with Image.open(image_path) as img:
        resized = resize_image(img, width, height, maintain_aspect, method)
        
        if output_path:
            resized.save(output_path)
        
        return resized


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Gets image dimensions.
    
    Args:
        image_path: Image path
    
    Returns:
        Tuple (width, height)
    """
    with Image.open(image_path) as img:
        return img.size

