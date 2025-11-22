"""Utilities for file handling and directory selection."""
import os
import tkinter.filedialog as filedialog
from pathlib import Path
from typing import List, Optional, Tuple


def select_images() -> List[str]:
    """
    Opens a dialog to select one or multiple images.
    
    Returns:
        List of selected file paths. Empty list if cancelled.
    """
    filetypes = [
        ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp *.avif *.ico"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
        ("ICO", "*.ico"),
        ("Todos los archivos", "*.*")
    ]
    
    files = filedialog.askopenfilenames(
        title="Seleccionar imágenes",
        filetypes=filetypes
    )
    
    return list(files) if files else []


def select_output_folder() -> Optional[str]:
    """
    Opens a dialog to select an output folder.
    
    Returns:
        Path of selected folder. None if cancelled.
    """
    folder = filedialog.askdirectory(
        title="Seleccionar carpeta de salida"
    )
    
    return folder if folder else None


def generate_output_filename(
    original_path: str,
    format_ext: str,
    output_folder: Optional[str] = None,
    custom_name: Optional[str] = None
) -> str:
    """
    Generates output filename based on original file.
    
    Args:
        original_path: Path of original file
        format_ext: Output format extension (e.g.: 'webp', 'avif')
        output_folder: Output folder. If None, uses same folder as original.
        custom_name: Custom name for file (without extension). If None, uses original name.
    
    Returns:
        Complete output file path
    """
    original_path_obj = Path(original_path)
    
    # Use custom name if provided, otherwise use original name
    if custom_name and custom_name.strip():
        # Clean custom name (remove invalid characters)
        custom_name = custom_name.strip()
        # Remove characters not allowed in filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            custom_name = custom_name.replace(char, '_')
        stem = custom_name
    else:
        stem = original_path_obj.stem
    
    extension = f".{format_ext}"
    
    if output_folder:
        output_path = Path(output_folder) / f"{stem}{extension}"
    else:
        output_path = original_path_obj.parent / f"{stem}{extension}"
    
    # If file already exists, add a number
    counter = 1
    base_output = output_path
    while output_path.exists():
        output_path = base_output.parent / f"{base_output.stem}_{counter}{base_output.suffix}"
        counter += 1
    
    return str(output_path)


def get_file_size(file_path: str) -> int:
    """
    Gets file size in bytes.
    
    Args:
        file_path: File path
    
    Returns:
        Size in bytes
    """
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """
    Formats file size into a readable string.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g.: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def is_valid_image(file_path: str) -> bool:
    """
    Verifies if a file is a valid image.
    
    Args:
        file_path: Path of file to verify
    
    Returns:
        True if it's a valid image, False otherwise
    """
    # Verify file exists
    if not os.path.exists(file_path):
        return False
    
    # Verify it's a file (not directory)
    if not os.path.isfile(file_path):
        return False
    
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.avif', '.ico'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in valid_extensions:
        return False
    
    # Try to open with Pillow to verify it's a valid image
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def check_write_permissions(folder_path: str) -> Tuple[bool, Optional[str]]:
    """
    Verifies if write permissions exist in a folder.
    
    Args:
        folder_path: Path of folder to verify
    
    Returns:
        Tuple (has_permissions, error_message)
    """
    try:
        # Verify folder exists
        if not os.path.exists(folder_path):
            return False, f"Folder does not exist: {folder_path}"
        
        # Verify it's a directory
        if not os.path.isdir(folder_path):
            return False, f"Path is not a directory: {folder_path}"
        
        # Try to create a test file
        test_file = os.path.join(folder_path, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True, None
        except PermissionError:
            return False, f"No write permissions in: {folder_path}"
        except Exception as e:
            return False, f"Error verifying permissions: {str(e)}"
    
    except Exception as e:
        return False, f"Error verifying folder: {str(e)}"

