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

