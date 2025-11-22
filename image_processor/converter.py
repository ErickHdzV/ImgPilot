"""Module for converting images to WebP and AVIF formats."""
import os
from pathlib import Path
from typing import Optional
from PIL import Image

# Try to register AVIF support with pillow-heif
AVIF_AVAILABLE = False
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    AVIF_AVAILABLE = True
except ImportError:
    # pillow-heif is not installed
    AVIF_AVAILABLE = False
except Exception as e:
    # If there's any other error registering, consider as not available
    # Debug: uncomment the following line if there are problems
    # print(f"Error registering pillow_heif: {e}")
    AVIF_AVAILABLE = False


def convert_to_webp(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True
) -> bool:
    """
    Converts an image to WebP format.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save WebP image
        quality: Compression quality (0-100)
        preserve_exif: Whether to preserve EXIF metadata
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (WebP doesn't support all modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Keep transparency if it exists
                if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
                    pass  # WebP soporta transparencia
                else:
                    img = img.convert('RGB')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Prepare save parameters
            save_kwargs = {
                'format': 'WEBP',
                'quality': quality,
                'method': 6  # Compression method (0-6, 6 is slower but better compression)
            }
            
            # Preserve EXIF if requested
            if preserve_exif and hasattr(img, 'getexif'):
                try:
                    exif = img.getexif()
                    if exif:
                        save_kwargs['exif'] = exif.tobytes()
                except Exception:
                    pass  # If EXIF can't be preserved, continue without it
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            img.save(output_path, **save_kwargs)
            return True
            
    except Exception as e:
        print(f"Error converting to WebP: {e}")
        return False


def convert_to_avif(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True
) -> bool:
    """
    Converts an image to AVIF format.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save AVIF image
        quality: Compression quality (0-100)
        preserve_exif: Whether to preserve EXIF metadata
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
                    pass  # AVIF soporta transparencia
                else:
                    img = img.convert('RGB')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Prepare save parameters
            save_kwargs = {
                'format': 'AVIF',
                'quality': quality,
            }
            
            # Preserve EXIF if requested
            if preserve_exif and hasattr(img, 'getexif'):
                try:
                    exif = img.getexif()
                    if exif:
                        save_kwargs['exif'] = exif.tobytes()
                except Exception:
                    pass
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to save with AVIF support
            # Check if pillow-heif is available
            if not AVIF_AVAILABLE:
                raise Exception(
                    "AVIF support not available. "
                    "Install pillow-heif: pip install pillow-heif"
                )
            
            img.save(output_path, **save_kwargs)
            return True
                
    except Exception as e:
        print(f"Error converting to AVIF: {e}")
        return False


def convert_to_png(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True,
    compression_level: int = 6
) -> bool:
    """
    Converts an image to PNG format.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save PNG image
        quality: Quality (0-100) - used for lossy format conversion
        preserve_exif: Whether to preserve EXIF metadata
        compression_level: PNG compression level (0-9, 9 is maximum compression)
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # PNG supports transparency, keep RGBA if it exists
            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
            elif img.mode not in ('RGB', 'RGBA', 'LA', 'L'):
                # Convert to RGB if it doesn't have transparency
                if img.mode == 'RGBA':
                    pass  # Keep RGBA
                else:
                    img = img.convert('RGB')
            
            # Prepare save parameters
            save_kwargs = {
                'format': 'PNG',
                'compress_level': min(9, max(0, compression_level))  # 0-9
            }
            
            # Preserve EXIF if requested
            if preserve_exif and hasattr(img, 'getexif'):
                try:
                    exif = img.getexif()
                    if exif:
                        save_kwargs['exif'] = exif.tobytes()
                except Exception:
                    pass
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            img.save(output_path, **save_kwargs)
            return True
            
    except Exception as e:
        print(f"Error converting to PNG: {e}")
        return False


def convert_to_jpg(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True
) -> bool:
    """
    Converts an image to JPEG format.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save JPEG image
        quality: Compression quality (0-100)
        preserve_exif: Whether to preserve EXIF metadata
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # JPEG doesn't support transparency, convert to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                elif img.mode == 'LA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img.convert('RGB'), mask=img.split()[1])
                    img = background
                else:
                    img = img.convert('RGB')
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Prepare save parameters
            save_kwargs = {
                'format': 'JPEG',
                'quality': min(100, max(1, quality)),  # 1-100
                'optimize': True  # Additional optimization
            }
            
            # Preserve EXIF if requested
            if preserve_exif and hasattr(img, 'getexif'):
                try:
                    exif = img.getexif()
                    if exif:
                        save_kwargs['exif'] = exif.tobytes()
                except Exception:
                    pass
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            img.save(output_path, **save_kwargs)
            return True
            
    except Exception as e:
        print(f"Error converting to JPEG: {e}")
        return False


def convert_to_ico(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True,
    sizes: Optional[list] = None
) -> bool:
    """
    Converts an image to ICO (icon) format.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save ICO image
        quality: Quality (0-100) - used for optimization
        preserve_exif: Whether to preserve EXIF metadata (usually doesn't apply to ICO)
        sizes: List of sizes in pixels [(16,16), (32,32), etc.]. If None, uses standard sizes.
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            # ICO typically uses standard sizes
            if sizes is None:
                sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
            
            # Create list of images in different sizes
            ico_images = []
            for size in sizes:
                # Resize maintaining aspect ratio
                resized = img.copy()
                resized.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Create image of exact size with transparent background if necessary
                if resized.mode == 'RGBA':
                    ico_img = Image.new('RGBA', size, (0, 0, 0, 0))
                    # Center the resized image
                    x = (size[0] - resized.size[0]) // 2
                    y = (size[1] - resized.size[1]) // 2
                    ico_img.paste(resized, (x, y))
                else:
                    ico_img = Image.new('RGBA', size, (0, 0, 0, 0))
                    rgb_img = resized.convert('RGB')
                    x = (size[0] - rgb_img.size[0]) // 2
                    y = (size[1] - rgb_img.size[1]) // 2
                    ico_img.paste(rgb_img, (x, y))
                
                ico_images.append(ico_img)
            
            # Create output directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save as ICO with multiple sizes
            ico_images[0].save(
                output_path,
                format='ICO',
                sizes=[(img.size[0], img.size[1]) for img in ico_images]
            )
            return True
            
    except Exception as e:
        print(f"Error converting to ICO: {e}")
        return False


def convert_to_svg(
    image_path: str,
    output_path: str,
    quality: int = 80,
    preserve_exif: bool = True
) -> bool:
    """
    Converts an image to SVG format through vectorization.
    
    Args:
        image_path: Path of original image
        output_path: Path where to save SVG image
        quality: Quality parameter (0-100) - affects simplification level
        preserve_exif: Whether to preserve EXIF metadata (not applicable to SVG)
    
    Returns:
        True if conversion was successful, False otherwise
    """
    try:
        from image_processor.svg_converter import vectorize_to_svg, check_svg_libs_available
        
        if not check_svg_libs_available():
            raise Exception(
                "Librerías requeridas no disponibles. "
                "Instala: pip install opencv-python svgwrite"
            )
        
        # Calculate simplify tolerance based on quality
        # Higher quality = less simplification (lower tolerance)
        # Lower quality = more simplification (higher tolerance)
        simplify_tolerance = (100 - quality) / 50.0  # Range: 0.0 to 2.0
        
        success, error_msg = vectorize_to_svg(
            image_path,
            output_path,
            simplify_paths=True,
            simplify_tolerance=max(0.5, min(2.0, simplify_tolerance)),
            edge_threshold_low=50,
            edge_threshold_high=150
        )
        
        if not success:
            raise Exception(error_msg or "Error desconocido al convertir a SVG")
        
        return True
        
    except Exception as e:
        print(f"Error converting to SVG: {e}")
        return False


def check_avif_support() -> bool:
    """
    Checks if AVIF support is available.
    
    Returns:
        True if AVIF is available, False otherwise
    """
    # First check the global variable
    if not AVIF_AVAILABLE:
        return False
    
    # Do a practical check to ensure it really works
    try:
        import pillow_heif
        # Ensure it's registered
        pillow_heif.register_heif_opener()
        
        # Verify that Pillow can save AVIF
        from PIL import Image
        test_img = Image.new('RGB', (1, 1))
        import tempfile
        import os
        
        tmp_file = tempfile.NamedTemporaryFile(suffix='.avif', delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        try:
            test_img.save(tmp_path, format='AVIF', quality=80)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return True
        except Exception:
            # Clean up on error
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except:
                pass
            return False
    except Exception:
        return False

