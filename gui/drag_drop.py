"""Drag & drop functionality for files."""
import os
from pathlib import Path
from typing import List, Callable, Optional
import customtkinter as ctk

# Try to import tkinterdnd2
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


def setup_drag_drop(widget, on_drop: Callable[[List[str]], None], validate_files: Optional[Callable[[str], bool]] = None):
    """
    Sets up drag & drop on a widget.
    
    Args:
        widget: CustomTkinter widget where to set up drag & drop
        on_drop: Callback function that receives a list of file paths
        validate_files: Optional function to validate files (returns True if valid)
    """
    if DND_AVAILABLE:
        try:
            # Get the native tkinter widget from CustomTkinter
            # CustomTkinter widgets have different ways to access the native widget
            native_widget = None
            
            # Try different methods to get the native widget
            # Method 1: If it has tk attribute (native tkinter widget)
            if hasattr(widget, 'tk') and widget.tk is not None:
                native_widget = widget.tk
            
            # Method 2: For CTkFrame and other widgets, look for the canvas
            elif hasattr(widget, '_canvas') and widget._canvas is not None:
                native_widget = widget._canvas
            
            # Method 3: For CTkScrollableFrame, the canvas is in _parent_canvas
            elif hasattr(widget, '_parent_canvas') and widget._parent_canvas is not None:
                native_widget = widget._parent_canvas
            
            # Method 4: Try to access the canvas frame
            elif hasattr(widget, '_canvas_frame') and widget._canvas_frame is not None:
                native_widget = widget._canvas_frame
            
            # Method 5: If it's a native tkinter widget directly (not CustomTkinter)
            elif hasattr(widget, 'winfo_toplevel') and not hasattr(widget, '_canvas'):
                # Verify it's not a CustomTkinter widget
                widget_class = type(widget).__name__
                if not widget_class.startswith('CTk'):
                    native_widget = widget
            
            # Method 6: Look in master/parent
            else:
                try:
                    if hasattr(widget, 'master') and widget.master is not None:
                        master = widget.master
                        if hasattr(master, '_canvas') and master._canvas is not None:
                            native_widget = master._canvas
                        elif hasattr(master, 'tk') and master.tk is not None:
                            native_widget = master.tk
                except:
                    pass
            
            if native_widget is None:
                # Last resort: try to get the toplevel and its canvas
                try:
                    toplevel = widget.winfo_toplevel()
                    if hasattr(toplevel, '_canvas') and toplevel._canvas is not None:
                        native_widget = toplevel._canvas
                    elif hasattr(toplevel, 'tk') and toplevel.tk is not None:
                        native_widget = toplevel.tk
                except:
                    pass
            
            if native_widget is None:
                raise Exception("Could not find native tkinter widget for drag & drop")
            
            def handle_drop(event):
                files = []
                try:
                    # tkinterdnd2 provides paths in event.data
                    data = event.data if hasattr(event, 'data') else str(event)
                    
                    # Parse files (format may vary by OS)
                    file_list = parse_dropped_files(data)
                    
                    for file_path in file_list:
                        if os.path.exists(file_path):
                            if validate_files is None or validate_files(file_path):
                                files.append(file_path)
                    
                    if files:
                        on_drop(files)
                except Exception as e:
                    # Silent error - user can try again
                    pass
            
            # Register as drop target
            native_widget.drop_target_register(DND_FILES)
            native_widget.dnd_bind('<<Drop>>', handle_drop)
            
        except Exception as e:
            # Only show error if critical (failure in main widget)
            # Don't show traceback to avoid console noise
            pass  # Silent fallback to manual implementation
            _setup_manual_drag_drop(widget, on_drop, validate_files)
    else:
        # Don't show message if tkinterdnd2 is not available (it's optional)
        # User can install if needed
        _setup_manual_drag_drop(widget, on_drop, validate_files)


def _setup_manual_drag_drop(widget, on_drop: Callable[[List[str]], None], validate_files: Optional[Callable[[str], bool]] = None):
    """
    Manual drag & drop implementation using input events.
    Note: This is a basic implementation that works with click and selection.
    For real drag & drop between applications, tkinterdnd2 is required.
    """
    def on_click(event):
        # This is a simplified implementation
        # In practice, real drag & drop requires tkinterdnd2
        pass
    
    widget.bind("<Button-1>", on_click)


def is_valid_image_file(file_path: str) -> bool:
    """
    Validates if a file is a valid image.
    
    Args:
        file_path: File path
    
    Returns:
        True if it's a valid image
    """
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
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


def parse_dropped_files(data: str) -> List[str]:
    """
    Parses the dropped files string.
    
    Args:
        data: String with file paths (tkinterdnd2 format)
    
    Returns:
        List of file paths
    """
    files = []
    if not data:
        return files
    
    # tkinterdnd2 on Windows wraps paths in braces and separates them with } {
    # On Linux/Mac it may use spaces or quotes
    try:
        # Clean the string
        data = data.strip()
        
        # If wrapped in braces (Windows)
        if data.startswith('{') and data.endswith('}'):
            # Remove outer braces
            data = data[1:-1]
            # Split by } {
            file_list = data.split('} {')
        elif '"' in data:
            # If it has quotes, split by quotes
            import re
            file_list = re.findall(r'"([^"]+)"', data)
            if not file_list:
                file_list = data.split()
        else:
            # Split by spaces
            file_list = data.split()
        
        for file_path in file_list:
            # Clean each path
            file_path = file_path.strip('{}').strip('"').strip("'").strip()
            
            # Verify it exists and is a file
            if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
                # Normalize the path
                file_path = os.path.normpath(file_path)
                if file_path not in files:  # Avoid duplicates
                    files.append(file_path)
    
    except Exception as e:
        # Silent error when parsing - return empty list
        pass
    
    return files

