"""Module for converting images to SVG format through vectorization."""
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import numpy as np

# Try to import required libraries
SVG_LIBS_AVAILABLE = False
try:
    import cv2
    import svgwrite
    SVG_LIBS_AVAILABLE = True
except ImportError:
    SVG_LIBS_AVAILABLE = False
except Exception:
    SVG_LIBS_AVAILABLE = False


def vectorize_to_svg(
    image_path: str,
    output_path: str,
    simplify_paths: bool = True,
    simplify_tolerance: float = 1.0,
    edge_threshold_low: int = 50,
    edge_threshold_high: int = 150,
    max_paths: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Converts a raster image to SVG by vectorizing it.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save SVG file
        simplify_paths: Whether to simplify paths to reduce file size
        simplify_tolerance: Tolerance for path simplification (higher = more simplification)
        edge_threshold_low: Lower threshold for Canny edge detection
        edge_threshold_high: Upper threshold for Canny edge detection
        max_paths: Maximum number of paths to include (None = no limit)
    
    Returns:
        Tuple (success, error_message)
    """
    if not SVG_LIBS_AVAILABLE:
        return False, "Librerías requeridas no disponibles. Instala: pip install opencv-python svgwrite"
    
    try:
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get image dimensions
            width, height = img.size
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect edges using Canny
            edges = cv2.Canny(blurred, edge_threshold_low, edge_threshold_high)
            
            # Find contours using OpenCV
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create SVG drawing
            dwg = svgwrite.Drawing(output_path, size=(f"{width}px", f"{height}px"))
            dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='white'))
            
            # Convert contours to SVG paths
            path_count = 0
            for contour in contours:
                if max_paths is not None and path_count >= max_paths:
                    break
                
                # Simplify contour if requested
                if simplify_paths:
                    # Use Douglas-Peucker algorithm via OpenCV
                    epsilon = simplify_tolerance * cv2.arcLength(contour, False)
                    if epsilon > 0:
                        contour = cv2.approxPolyDP(contour, epsilon, False)
                
                # Convert contour to path string
                if len(contour) < 2:
                    continue
                
                # Create path
                path_data = []
                for i, point in enumerate(contour):
                    # OpenCV contours are in (x, y) format
                    x, y = point[0][0], point[0][1]
                    if i == 0:
                        path_data.append(f"M {x:.2f} {y:.2f}")
                    else:
                        path_data.append(f"L {x:.2f} {y:.2f}")
                
                # Close path
                path_data.append("Z")
                path_string = " ".join(path_data)
                
                # Add path to SVG
                dwg.add(dwg.path(d=path_string, fill='black', stroke='none'))
                path_count += 1
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save SVG
            dwg.save()
            
            return True, None
            
    except Exception as e:
        return False, f"Error vectorizando a SVG: {str(e)}"


def convert_raster_to_svg_embedded(
    image_path: str,
    output_path: str,
    quality: int = 80
) -> Tuple[bool, Optional[str]]:
    """
    Converts an image to SVG by embedding it as base64 (alternative method).
    This preserves the original image quality but doesn't truly vectorize.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save SVG file
        quality: JPEG quality if converting to JPEG for embedding (0-100)
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        import base64
        import svgwrite
        
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            
            # Save image to bytes
            import io
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
            
            # Create SVG with embedded image
            dwg = svgwrite.Drawing(output_path, size=(f"{width}px", f"{height}px"))
            dwg.add(dwg.image(
                href=f"data:image/png;base64,{img_base64}",
                insert=(0, 0),
                size=(width, height)
            ))
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save SVG
            dwg.save()
            
            return True, None
            
    except Exception as e:
        return False, f"Error convirtiendo a SVG embebido: {str(e)}"


def check_svg_libs_available() -> bool:
    """
    Checks if required libraries for SVG conversion are available.
    
    Returns:
        True if libraries are available, False otherwise
    """
    return SVG_LIBS_AVAILABLE

