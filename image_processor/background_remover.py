"""Module for removing background from images."""
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import numpy as np

# Try to import rembg
REM_BG_AVAILABLE = False
try:
    from rembg import remove
    REM_BG_AVAILABLE = True
except ImportError:
    REM_BG_AVAILABLE = False
except Exception:
    REM_BG_AVAILABLE = False


def remove_background(
    image_path: str,
    output_path: str,
    model_name: str = "u2net"
) -> Tuple[bool, Optional[str]]:
    """
    Removes background from an image using rembg.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save image without background
        model_name: Model to use for background removal (default: "u2net")
    
    Returns:
        Tuple (success, error_message)
    """
    if not REM_BG_AVAILABLE:
        return False, "rembg no está disponible. Instala con: pip install rembg"
    
    try:
        # Read input image
        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background
        output_data = remove(input_data, model_name=model_name)
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save output image
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        return True, None
        
    except Exception as e:
        return False, f"Error removiendo background: {str(e)}"


def check_rembg_available() -> bool:
    """
    Checks if rembg is available.
    
    Returns:
        True if rembg is available, False otherwise
    """
    return REM_BG_AVAILABLE

