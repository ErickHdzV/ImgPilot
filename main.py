"""Main entry point for the ImgPilot application."""
import sys
import argparse

# Fix for Python 3.14 compatibility with CustomTkinter
# CustomTkinter tries to use block_update_dimensions_event which doesn't exist in Python 3.14
try:
    import tkinter as tk
    
    # Add missing methods to Tk class for Python 3.14 compatibility
    if not hasattr(tk.Tk, 'block_update_dimensions_event'):
        def block_update_dimensions_event(self):
            """Dummy method for Python 3.14 compatibility."""
            pass
        
        def unblock_update_dimensions_event(self):
            """Dummy method for Python 3.14 compatibility."""
            pass
        
        tk.Tk.block_update_dimensions_event = block_update_dimensions_event
        tk.Tk.unblock_update_dimensions_event = unblock_update_dimensions_event
        
        # Also patch the base class
        if hasattr(tk.Tk, '__init__'):
            # Ensure the methods are available on instances
            pass
except Exception:
    # If patching fails, continue anyway
    pass

# Additional fix: Patch CustomTkinter's scaling tracker to handle the error gracefully
try:
    import customtkinter.windows.widgets.scaling.scaling_tracker as scaling_tracker
    
    # Save original function
    if hasattr(scaling_tracker, 'check_dpi_scaling'):
        original_check = scaling_tracker.check_dpi_scaling
        
        def patched_check_dpi_scaling(*args, **kwargs):
            try:
                return original_check(*args, **kwargs)
            except AttributeError as e:
                if 'block_update_dimensions_event' in str(e):
                    # Silently ignore this error for Python 3.14
                    return
                raise
        
        scaling_tracker.check_dpi_scaling = patched_check_dpi_scaling
except Exception:
    # If patching fails, continue anyway
    pass

from gui.main_window import MainWindow
import customtkinter as ctk
import config

# Try to import TkinterDnD for drag & drop from outside
try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = None


def set_window_icon(window):
    """
    Sets the window icon for both taskbar and window title bar.
    Uses the PNG without background if available for better appearance.
    """
    try:
        from PIL import Image, ImageTk
        
        # Try to use the removebg version first (better for taskbar)
        icon_path = config.get_logo_path('png', removebg=True)
        if not icon_path.exists():
            icon_path = config.get_logo_path('png')
        
        if icon_path.exists():
            # Load icon image
            icon_img = Image.open(str(icon_path))
            icon_photo = ImageTk.PhotoImage(icon_img)
            # iconphoto(True) sets icon for all windows and taskbar
            window.iconphoto(True, icon_photo)
        
        # Also set iconbitmap for .ico file (Windows compatibility)
        ico_path = config.get_icon_path()
        if ico_path.exists():
            window.iconbitmap(str(ico_path))
    except Exception:
        # If icon fails to load, continue without it
        pass


def main():
    """Main application function."""
    parser = argparse.ArgumentParser(
        description="ImgPilot - Image optimizer and format converter"
    )
    parser.add_argument(
        '--theme',
        choices=['dark', 'light', 'system'],
        default='light',
        help='Interface theme (default: light)'
    )
    parser.add_argument(
        '--color-theme',
        choices=['blue', 'green', 'dark-blue'],
        default='blue',
        help='Color theme (default: blue)'
    )
    
    args = parser.parse_args()
    
    # Configure theme
    ctk.set_appearance_mode(args.theme)
    ctk.set_default_color_theme(args.color_theme)
    
    # Create and run application
    try:
        # If TkinterDnD is available, create window with drag & drop support
        if DND_AVAILABLE:
            # Create TkinterDnD window as base
            root = TkinterDnD.Tk()
            root.title("ImgPilot")
            root.geometry("1400x900")
            root.minsize(1200, 700)
            
            # Set window icon (for taskbar and window)
            set_window_icon(root)
            
            # Configure theme on root window as well
            # (although CustomTkinter will handle most of the theme)
            
            # Create MainWindow as a frame inside the TkinterDnD window
            app = MainWindow(root)
            app.pack(fill="both", expand=True, padx=0, pady=0)
            
            root.mainloop()
        else:
            # Use normal method without drag & drop from outside
            app = MainWindow()
            # Set window icon (for taskbar and window)
            set_window_icon(app)
            app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

