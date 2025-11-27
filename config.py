"""Application configuration and constants."""
from pathlib import Path
from typing import Dict, Tuple

# Application information
APP_NAME = "ImgPilot"
APP_VERSION = "1.0.0"

# Window configuration
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

# Theme configuration
DEFAULT_THEME = "light"
DEFAULT_COLOR_THEME = "blue"
THEMES = ["light", "dark", "system"]
COLOR_THEMES = ["blue", "green", "dark-blue"]

# Quality configuration
DEFAULT_QUALITY = 80
MIN_QUALITY = 0
MAX_QUALITY = 100

# Resize configuration
DEFAULT_RESIZE_METHOD = "LANCZOS"
RESIZE_METHODS = ["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"]

# Supported formats
SUPPORTED_INPUT_FORMATS = {
    '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', 
    '.webp', '.avif', '.ico'
}

SUPPORTED_OUTPUT_FORMATS = {
    'webp': 'WebP',
    'avif': 'AVIF',
    'png': 'PNG',
    'jpg': 'JPEG',
    'ico': 'ICO'
}

# File configuration
CONFIG_DIR_NAME = ".imgpilot"
PRESETS_FILENAME = "presets.json"

# Configuration paths
def get_config_dir() -> Path:
    """Returns the user configuration directory."""
    return Path.home() / CONFIG_DIR_NAME

def get_presets_file() -> Path:
    """Returns the presets file path."""
    return get_config_dir() / PRESETS_FILENAME

# Logo paths
def get_logo_path(format: str = 'png', removebg: bool = False) -> Path:
    """
    Returns the path to the logo image.
    Works both in development and in PyInstaller executable.
    
    Args:
        format: Image format ('png', 'ico', 'jpg', 'webp', 'svg', 'avif')
        removebg: If True, try to get the version without background
    
    Returns:
        Path to the logo file
    """
    import sys
    import os
    
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent
    
    logo_dir = base_path / 'image' / 'logo'
    
    # If removebg is requested and format is png, try removebg version first
    if removebg and format == 'png':
        removebg_path = logo_dir / 'ImgPilot-removebg.png'
        if removebg_path.exists():
            return removebg_path
    
    logo_path = logo_dir / f'ImgPilot.{format}'
    
    # If the requested format doesn't exist, try PNG as fallback
    if not logo_path.exists() and format != 'png':
        logo_path = logo_dir / 'ImgPilot.png'
    
    return logo_path

def get_icon_path() -> Path:
    """Returns the path to the .ico icon file."""
    return get_logo_path('ico')

# UI configuration
TOOLBAR_HEIGHT = 50
GALLERY_PANEL_WIDTH = 250
OPTIONS_PANEL_WIDTH = 350
THUMBNAIL_SIZE = 120

# Colors (light mode, dark mode)
COLORS = {
    'primary': ("#3B8ED0", "#1F6AA5"),
    'text_title': ("black", "white"),
    'border': ("gray60", "gray40"),
    'hover': ("gray70", "gray30"),
}

# Messages
MESSAGES = {
    'no_images': "Por favor, selecciona al menos una imagen.",
    'no_formats': "Por favor, selecciona al menos un formato de salida.",
    'no_resize_dimensions': "Por favor, especifica al menos ancho o alto para redimensionar.",
    'invalid_width': "El ancho debe ser mayor que 0.",
    'invalid_height': "El alto debe ser mayor que 0.",
    'invalid_dimensions': "Por favor, ingresa valores numéricos válidos para las dimensiones.",
}

