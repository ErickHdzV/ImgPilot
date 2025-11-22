"""Main application window."""
import customtkinter as ctk
import threading
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Try to import TkinterDnD for drag & drop from outside the application
try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = None

# Local imports
from gui.components import (
    ImagePreview, QualitySlider, ImageThumbnail,
    BeforeAfterView, CollapsibleFrame, DropZone
)
from gui.preset_manager import PresetManager
from gui.drag_drop import setup_drag_drop, is_valid_image_file
from gui.app_state import AppState, ProcessingConfig
from utils.file_handler import (
    select_images, select_output_folder, generate_output_filename,
    get_file_size, format_file_size, is_valid_image, check_write_permissions
)
from image_processor.converter import check_avif_support
from image_processor.image_processor import ImageProcessor
from image_processor.background_remover import remove_background, check_rembg_available
import config


class MainWindow(ctk.CTkFrame if DND_AVAILABLE else ctk.CTk):
    """Main window for the image optimization application."""
    
    def __init__(self, parent=None):
        if DND_AVAILABLE and parent is not None:
            # If there's a parent (TkinterDnD window), create as frame
            super().__init__(parent)
            self._parent_window = parent
        else:
            # If no parent, create as main window
            super().__init__()
            self._parent_window = None
        
        # Window configuration (only if it's main window, not frame)
        if self._parent_window is None:
            self.title(config.APP_NAME)
            self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
            self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        
        # Configure theme
        self.current_theme = config.DEFAULT_THEME
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme(config.DEFAULT_COLOR_THEME)
        
        # Application state
        self.app_state = AppState()
        self.thumbnail_widgets: List[ImageThumbnail] = []
        
        # Preset manager
        self.preset_manager = PresetManager()
        
        # Image processor
        self.image_processor = ImageProcessor()
        
        # Check AVIF support
        try:
            from image_processor.converter import AVIF_AVAILABLE
            self.avif_supported = check_avif_support()
            if AVIF_AVAILABLE and not self.avif_supported:
                self.avif_supported = True
        except Exception:
            try:
                from image_processor.converter import AVIF_AVAILABLE
                self.avif_supported = AVIF_AVAILABLE
            except:
                self.avif_supported = False
        
        # Create interface
        self._create_widgets()
        self._update_avif_status()
        
        # Set up drag & drop on main window to drag from outside
        self._setup_window_drag_drop()
    
    def _create_widgets(self):
        """Creates all interface widgets with the new design."""
        
        # === TOP TOOLBAR ===
        toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        toolbar.pack(fill="x", padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            toolbar,
            text="🌓",
            width=50,
            height=40,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=18)
        )
        self.theme_button.pack(side="left", padx=10, pady=5)
        
        # Presets
        preset_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        preset_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(preset_frame, text="Preset:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
        
        self.preset_combo = ctk.CTkComboBox(
            preset_frame,
            values=["Ninguno"] + self.preset_manager.list_presets(),
            width=200,
            command=self._on_preset_selected,
            state="readonly"
        )
        self.preset_combo.set("Ninguno")
        self.preset_combo.pack(side="left", padx=5)
        
        self.save_preset_button = ctk.CTkButton(
            preset_frame,
            text="💾 Guardar",
            width=100,
            height=30,
            command=self._on_save_preset,
            font=ctk.CTkFont(size=11)
        )
        self.save_preset_button.pack(side="left", padx=5)
        
        self.manage_preset_button = ctk.CTkButton(
            preset_frame,
            text="⚙️ Gestionar",
            width=100,
            height=30,
            command=self._on_manage_presets,
            font=ctk.CTkFont(size=11)
        )
        self.manage_preset_button.pack(side="left", padx=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=5)
        
        self.select_button = ctk.CTkButton(
            action_frame,
            text="📁 Seleccionar Imágenes",
            command=self._on_select_images,
            width=150,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.select_button.pack(side="left", padx=5)
        
        self.output_folder_button = ctk.CTkButton(
            action_frame,
            text="📂 Carpeta Salida",
            command=self._on_select_output_folder,
            width=130,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.output_folder_button.pack(side="left", padx=5)
        
        self.remove_bg_button = ctk.CTkButton(
            action_frame,
            text="✂️ Quitar Background",
            command=self._on_remove_background,
            width=150,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.remove_bg_button.pack(side="left", padx=5)
        
        # === MAIN AREA ===
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel: Gallery
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 5))
        left_panel.configure(width=250)
        
        gallery_label = ctk.CTkLabel(
            left_panel,
            text="Galería",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        gallery_label.pack(pady=10)
        
        # Scrollable frame for gallery
        self.gallery_scroll = ctk.CTkScrollableFrame(left_panel)
        self.gallery_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initial drop zone
        self.drop_zone = DropZone(
            self.gallery_scroll,
            on_drop=self._on_drop_files,
            on_click=self._on_select_images
        )
        self.drop_zone.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set up drag & drop on drop zone and also on scrollable frame
        # These are optional since the main window also handles drag & drop
        try:
            setup_drag_drop(self.drop_zone, self._on_drop_files, is_valid_image_file)
        except:
            pass
        try:
            setup_drag_drop(self.gallery_scroll, self._on_drop_files, is_valid_image_file)
        except:
            pass
        try:
            setup_drag_drop(left_panel, self._on_drop_files, is_valid_image_file)
        except:
            pass
        
        # Center panel: Before/after comparison
        center_panel = ctk.CTkFrame(main_container)
        center_panel.pack(side="left", fill="both", expand=True, padx=5)
        
        comparison_label = ctk.CTkLabel(
            center_panel,
            text="Comparación",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        comparison_label.pack(pady=10)
        
        self.comparison_view = BeforeAfterView(center_panel)
        self.comparison_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right panel: Options
        right_panel = ctk.CTkScrollableFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=False, padx=(5, 0))
        right_panel.configure(width=350)
        
        # === OPTIONS (Collapsible) ===
        
        # Formats
        formats_frame = CollapsibleFrame(right_panel, "Formatos de Salida")
        formats_frame.pack(fill="x", padx=10, pady=5)
        formats_content = formats_frame.get_content_frame()
        
        self.format_vars = {
            'webp': ctk.BooleanVar(value=True),
            'avif': ctk.BooleanVar(value=False),
            'png': ctk.BooleanVar(value=False),
            'jpg': ctk.BooleanVar(value=False),
            'ico': ctk.BooleanVar(value=False),
            'svg': ctk.BooleanVar(value=False)
        }
        
        self.format_checkboxes = {}
        for fmt, var in self.format_vars.items():
            checkbox = ctk.CTkCheckBox(
                formats_content,
                text=fmt.upper(),
                variable=var,
            font=ctk.CTkFont(size=12)
        )
            checkbox.pack(anchor="w", padx=20, pady=3)
            self.format_checkboxes[fmt] = checkbox
        
        # Quality
        quality_frame = CollapsibleFrame(right_panel, "Calidad")
        quality_frame.pack(fill="x", padx=10, pady=5)
        quality_content = quality_frame.get_content_frame()
        
        self.quality_slider = QualitySlider(
            quality_content,
            label="Calidad",
            default_value=80
        )
        self.quality_slider.pack(fill="x", padx=15, pady=15)
        
        # Resize
        resize_frame = CollapsibleFrame(right_panel, "Redimensionamiento")
        resize_frame.pack(fill="x", padx=10, pady=5)
        resize_content = resize_frame.get_content_frame()
        
        self.resize_enabled_var = ctk.BooleanVar(value=False)
        resize_checkbox = ctk.CTkCheckBox(
            resize_content,
            text="Redimensionar imagen",
            variable=self.resize_enabled_var,
            command=self._on_resize_toggle,
            font=ctk.CTkFont(size=12)
        )
        resize_checkbox.pack(anchor="w", padx=20, pady=5)
        
        dimensions_frame = ctk.CTkFrame(resize_content)
        dimensions_frame.pack(fill="x", padx=20, pady=5)
        
        width_frame = ctk.CTkFrame(dimensions_frame)
        width_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(width_frame, text="Ancho:", width=60).pack(side="left", padx=5)
        self.width_entry = ctk.CTkEntry(width_frame, width=100, placeholder_text="px")
        self.width_entry.pack(side="left", padx=5)
        
        height_frame = ctk.CTkFrame(dimensions_frame)
        height_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(height_frame, text="Alto:", width=60).pack(side="left", padx=5)
        self.height_entry = ctk.CTkEntry(height_frame, width=100, placeholder_text="px")
        self.height_entry.pack(side="left", padx=5)
        
        self.maintain_aspect_var = ctk.BooleanVar(value=True)
        aspect_checkbox = ctk.CTkCheckBox(
            dimensions_frame,
            text="Mantener proporción",
            variable=self.maintain_aspect_var,
            font=ctk.CTkFont(size=11)
        )
        aspect_checkbox.pack(anchor="w", padx=5, pady=5)
        
        # Resize method
        method_frame = ctk.CTkFrame(resize_content)
        method_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(method_frame, text="Método:", width=80).pack(side="left", padx=5)
        self.resize_method_combo = ctk.CTkComboBox(
            method_frame,
            values=["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],
            width=120,
            state="readonly"
        )
        self.resize_method_combo.set("LANCZOS")
        self.resize_method_combo.pack(side="left", padx=5)
        
        self._update_resize_widgets_state()
        
        # Advanced options
        advanced_frame = CollapsibleFrame(right_panel, "Opciones Avanzadas")
        advanced_frame.pack(fill="x", padx=10, pady=5)
        advanced_content = advanced_frame.get_content_frame()
        
        self.preserve_exif_var = ctk.BooleanVar(value=True)
        exif_checkbox = ctk.CTkCheckBox(
            advanced_content,
            text="Preservar metadatos EXIF",
            variable=self.preserve_exif_var,
            font=ctk.CTkFont(size=12)
        )
        exif_checkbox.pack(anchor="w", padx=20, pady=5)
        
        # Filename
        filename_frame = CollapsibleFrame(right_panel, "Nombre de Archivo")
        filename_frame.pack(fill="x", padx=10, pady=5)
        filename_content = filename_frame.get_content_frame()
        
        filename_help = ctk.CTkLabel(
            filename_content,
            text="Opcional: deja vacío para usar el nombre original",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        filename_help.pack(anchor="w", padx=20, pady=(5, 0))
        
        self.custom_filename_entry = ctk.CTkEntry(
            filename_content,
            placeholder_text="Ej: imagen_optimizada",
            font=ctk.CTkFont(size=12)
        )
        self.custom_filename_entry.pack(fill="x", padx=20, pady=10)
        
        # Optimize button
        self.optimize_button = ctk.CTkButton(
            right_panel,
            text="🚀 Optimizar Imágenes",
            command=self._on_optimize,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=("#3B8ED0", "#1F6AA5")
        )
        self.optimize_button.pack(fill="x", padx=15, pady=15)
        
        # Progress
        progress_frame = ctk.CTkFrame(right_panel)
        progress_frame.pack(fill="x", padx=15, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(pady=(0, 10))
        
        # Results
        results_frame = CollapsibleFrame(right_panel, "Resultados")
        results_frame.pack(fill="x", padx=10, pady=5)
        results_content = results_frame.get_content_frame()
        
        self.results_text = ctk.CTkTextbox(
            results_content,
            height=150,
            font=ctk.CTkFont(size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _setup_window_drag_drop(self):
        """Sets up drag & drop on main window to drag from outside."""
        if DND_AVAILABLE and self._parent_window is not None:
            try:
                from tkinterdnd2 import DND_FILES
                from gui.drag_drop import parse_dropped_files
                
                # Usar la ventana padre (TkinterDnD.Tk) directamente
                def handle_window_drop(event):
                    """Handles files dropped on main window."""
                    try:
                        data = event.data if hasattr(event, 'data') else str(event)
                        file_list = parse_dropped_files(data)
                        
                        # Filter only valid images
                        valid_files = [f for f in file_list if is_valid_image_file(f)]
                        
                        if valid_files:
                            self._on_drop_files(valid_files)
                    except Exception as e:
                        # Silent error - user can try again
                        pass
                
                # Register parent window as drop target
                self._parent_window.drop_target_register(DND_FILES)
                self._parent_window.dnd_bind('<<Drop>>', handle_window_drop)
                
                # Silent message - only show if there are problems
                
            except Exception as e:
                # Silent error - drag & drop may not work on this window
                # but will work on specific zones
                pass
        # Don't show message if tkinterdnd2 is not available (it's optional)
    
    def _toggle_theme(self):
        """Toggles between light and dark theme."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
    
    def _update_avif_status(self):
        """Updates AVIF checkbox status."""
        if not self.avif_supported:
            self.format_checkboxes['avif'].configure(text="AVIF (requiere pillow-heif)")
        else:
            self.format_checkboxes['avif'].configure(text="AVIF")
    
    def _on_drop_files(self, files: List[str]):
        """Handles dropped files."""
        valid_files = [f for f in files if is_valid_image_file(f)]
        if valid_files:
            self._add_images(valid_files)
    
    def _add_images(self, files: List[str]):
        """Adds images to the list."""
        # Hide drop zone if there are images
        if self.drop_zone.winfo_viewable():
            self.drop_zone.pack_forget()
        
        # Add new images to state
        self.app_state.add_images(files)
        
        # Update gallery
        self._update_gallery()
        
        # Show first image if none is selected
        if self.app_state.selected_images and not self.app_state.current_preview_image:
            self._select_image(0)
    
    def _update_gallery(self):
        """Updates the thumbnail gallery."""
        # Clear existing thumbnails
        for widget in self.thumbnail_widgets:
            widget.destroy()
        self.thumbnail_widgets.clear()
        
        # Create new thumbnails
        for idx, image_path in enumerate(self.app_state.selected_images):
            thumbnail = ImageThumbnail(
                self.gallery_scroll,
                image_path,
                on_click=lambda path, i=idx: self._select_image(i)
            )
            thumbnail.pack(fill="x", padx=5, pady=5)
            self.thumbnail_widgets.append(thumbnail)
        
        # Update selection
        if self.thumbnail_widgets:
            self._update_thumbnail_selection()
    
    def _select_image(self, index: int):
        """Selects an image from the gallery."""
        if 0 <= index < len(self.app_state.selected_images):
            self.app_state.set_active_image(index)
            
            # Update comparison
            self.comparison_view.display_original(
                self.app_state.current_preview_image,
                f"Original: {format_file_size(get_file_size(self.app_state.current_preview_image))}"
            )
            
            # If there's an optimized result, show it
            if self.app_state.current_preview_image in self.app_state.optimized_results:
                optimized_path = self.app_state.optimized_results[self.app_state.current_preview_image]
                if os.path.exists(optimized_path):
                    stats = ImageProcessor.calculate_compression_stats(
                        self.app_state.current_preview_image,
                        optimized_path
                    )
                    self.comparison_view.display_optimized(
                        optimized_path,
                        f"Optimizada: {stats['optimized_size_formatted']} ({stats['compression_ratio']:.1f}% reducción)"
                    )
            else:
                self.comparison_view.display_optimized(None, "")
            
            # Update visual selection
            self._update_thumbnail_selection()
    
    def _update_thumbnail_selection(self):
        """Updates visual selection in gallery."""
        for idx, thumbnail in enumerate(self.thumbnail_widgets):
            thumbnail.set_selected(idx == self.app_state.active_image_index)
    
    def _on_select_images(self):
        """Handles image selection."""
        files = select_images()
        if files:
            valid_files = [f for f in files if is_valid_image(f)]
            if valid_files:
                self._add_images(valid_files)
    
    def _on_select_output_folder(self):
        """Handles output folder selection."""
        folder = select_output_folder()
        if folder:
            self.app_state.output_folder = folder
    
    def _on_resize_toggle(self):
        """Handles resize toggle."""
        self._update_resize_widgets_state()
    
    def _update_resize_widgets_state(self):
        """Updates resize widgets state."""
        enabled = self.resize_enabled_var.get()
        state = "normal" if enabled else "disabled"
        
        self.width_entry.configure(state=state)
        self.height_entry.configure(state=state)
        self.maintain_aspect_var.set(True)  # Reset
        self.resize_method_combo.configure(state=state if enabled else "disabled")
    
    def _on_preset_selected(self, preset_name: str):
        """Loads a selected preset."""
        if preset_name == "Ninguno":
            return
        
        preset = self.preset_manager.load_preset(preset_name)
        if preset:
            # Apply preset configuration
            if 'formats' in preset:
                for fmt, enabled in preset['formats'].items():
                    if fmt in self.format_vars:
                        self.format_vars[fmt].set(enabled)
            
            if 'quality' in preset:
                self.quality_slider.set(preset['quality'])
            
            if 'resize_enabled' in preset:
                self.resize_enabled_var.set(preset['resize_enabled'])
                self._update_resize_widgets_state()
            
            if 'width' in preset and preset['width']:
                self.width_entry.delete(0, "end")
                self.width_entry.insert(0, str(preset['width']))
            
            if 'height' in preset and preset['height']:
                self.height_entry.delete(0, "end")
                self.height_entry.insert(0, str(preset['height']))
            
            if 'maintain_aspect' in preset:
                self.maintain_aspect_var.set(preset['maintain_aspect'])
            
            if 'resize_method' in preset:
                self.resize_method_combo.set(preset['resize_method'])
            
            if 'preserve_exif' in preset:
                self.preserve_exif_var.set(preset['preserve_exif'])
    
    def _on_save_preset(self):
        """Saves current configuration as preset."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Guardar Preset")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Nombre del preset:", font=ctk.CTkFont(size=12)).pack(pady=10)
        
        name_entry = ctk.CTkEntry(dialog, width=300, font=ctk.CTkFont(size=12))
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def save():
            name = name_entry.get().strip()
            if name:
                config = self._get_current_config()
                if self.preset_manager.save_preset(name, config):
                    # Update combo
                    self.preset_combo.configure(
                        values=["Ninguno"] + self.preset_manager.list_presets()
                    )
                    dialog.destroy()
                else:
                    self._show_message("Error al guardar el preset.")
            else:
                self._show_message("Por favor, ingresa un nombre para el preset.")
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Guardar", command=save).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=5)
        
        name_entry.bind("<Return>", lambda e: save())
    
    def _on_manage_presets(self):
        """Opens dialog to manage presets."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Gestionar Presets")
        dialog.geometry("500x400")
        dialog.transient(self)
        
        ctk.CTkLabel(
            dialog,
            text="Presets guardados:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        presets_list = ctk.CTkScrollableFrame(dialog)
        presets_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        for preset_name in self.preset_manager.list_presets():
            preset_frame = ctk.CTkFrame(presets_list)
            preset_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                preset_frame,
                text=preset_name,
                font=ctk.CTkFont(size=12)
            ).pack(side="left", padx=10, pady=5)
            
            def delete_preset(name=preset_name):
                if self.preset_manager.delete_preset(name):
                    # Update combo and list
                    self.preset_combo.configure(
                        values=["Ninguno"] + self.preset_manager.list_presets()
                    )
                    dialog.destroy()
                    self._on_manage_presets()  # Refresh
                else:
                    self._show_message("Error al eliminar el preset.")
            
            ctk.CTkButton(
                preset_frame,
                text="Eliminar",
                width=80,
                command=delete_preset,
                fg_color=("red", "darkred")
            ).pack(side="right", padx=10, pady=5)
        
        ctk.CTkButton(dialog, text="Cerrar", command=dialog.destroy).pack(pady=10)
    
    def _get_current_config(self) -> Dict[str, Any]:
        """Gets current configuration."""
        formats = {}
        for fmt, var in self.format_vars.items():
            formats[fmt] = var.get()
        
        width = None
        height = None
        try:
            if self.width_entry.get():
                width = int(self.width_entry.get())
        except ValueError:
            pass
        
        try:
            if self.height_entry.get():
                height = int(self.height_entry.get())
        except ValueError:
            pass
        
        return {
            'formats': formats,
            'quality': self.quality_slider.get(),
            'resize_enabled': self.resize_enabled_var.get(),
            'width': width,
            'height': height,
            'maintain_aspect': self.maintain_aspect_var.get(),
            'resize_method': self.resize_method_combo.get(),
            'preserve_exif': self.preserve_exif_var.get()
        }
    
    def _validate_optimization(self) -> Optional[str]:
        """
        Validates that images can be processed.
        
        Returns:
            Error message if there's a problem, None if everything is OK.
        """
        if not self.app_state.selected_images:
            return config.MESSAGES['no_images']
        
        # Verify that at least one format is selected
        formats_selected = [fmt for fmt, var in self.format_vars.items() if var.get()]
        if not formats_selected:
            return config.MESSAGES['no_formats']
        
        # Validate permissions
        output_folder = self.app_state.output_folder
        if output_folder:
            has_permission, error_msg = check_write_permissions(output_folder)
            if not has_permission:
                return f"Error de permisos: {error_msg}"
        else:
            if self.app_state.selected_images:
                first_file_folder = os.path.dirname(self.app_state.selected_images[0])
                has_permission, error_msg = check_write_permissions(first_file_folder)
                if not has_permission:
                    return f"Error de permisos en carpeta de origen: {error_msg}"
        
        # Validate resize
        if self.resize_enabled_var.get():
            try:
                width = int(self.width_entry.get()) if self.width_entry.get() else None
                height = int(self.height_entry.get()) if self.height_entry.get() else None
                
                if width is None and height is None:
                    return config.MESSAGES['no_resize_dimensions']
                
                if width is not None and width <= 0:
                    return config.MESSAGES['invalid_width']
                
                if height is not None and height <= 0:
                    return config.MESSAGES['invalid_height']
            except ValueError:
                return config.MESSAGES['invalid_dimensions']
        
        return None
    
    def _on_optimize(self):
        """Starts the optimization process."""
        # Validate
        error_msg = self._validate_optimization()
        if error_msg:
            self._show_message(error_msg)
            return
        
        # Get current configuration
        formats_selected = [fmt for fmt, var in self.format_vars.items() if var.get()]
        current_config = self._get_current_config()
        
        # Update processing state
        self.app_state.processing_config = ProcessingConfig(
            formats=formats_selected,
            quality=current_config['quality'],
            preserve_exif=current_config['preserve_exif'],
            resize_enabled=current_config['resize_enabled'],
            width=current_config.get('width'),
            height=current_config.get('height'),
            maintain_aspect=current_config['maintain_aspect'],
            resize_method=current_config['resize_method'],
            custom_filename=self.custom_filename_entry.get().strip() or None
        )
        
        # Disable button and clear results
        self.optimize_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Iniciando...")
        self.results_text.delete("1.0", "end")
        self.app_state.optimized_results.clear()
        
        # Start processing in separate thread
        thread = threading.Thread(
            target=self._process_images,
            daemon=True
        )
        thread.start()
    
    def _process_images(self):
        """Processes images in a separate thread."""
        proc_config = self.app_state.processing_config
        total_images = len(self.app_state.selected_images)
        total_tasks = total_images * len(proc_config.formats)
        completed = 0
        results = []
        
        try:
            for idx, image_path in enumerate(self.app_state.selected_images):
                progress = completed / total_tasks if total_tasks > 0 else 0
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda i=idx+1, t=total_images: 
                    self.progress_label.configure(text=f"Procesando {i}/{t}..."))
                
                try:
                    original_size = get_file_size(image_path)
                    resize_config = proc_config.get_resize_config()
                    
                    # Process each format
                    for format_type in proc_config.formats:
                        # Generate output filename
                        custom_name = proc_config.custom_filename
                        if custom_name and len(proc_config.formats) > 1:
                            custom_name_with_format = f"{custom_name}_{format_type}"
                        else:
                            custom_name_with_format = custom_name
                        
                        output_path = generate_output_filename(
                            image_path,
                            format_type,
                            self.app_state.output_folder,
                            custom_name_with_format
                        )
                        
                        # Process image using ImageProcessor
                        success, error_msg = ImageProcessor.process_image(
                            image_path,
                                    output_path,
                            format_type,
                            quality=proc_config.quality,
                            preserve_exif=proc_config.preserve_exif,
                            resize_config=resize_config
                        )
                        
                        if success:
                            # Calculate statistics
                            stats = ImageProcessor.calculate_compression_stats(
                                image_path,
                                output_path
                            )
                            
                            results.append({
                                'original': os.path.basename(image_path),
                                'format': format_type.upper(),
                                'output': os.path.basename(output_path),
                                'original_size': stats['original_size'],
                                'new_size': stats['optimized_size'],
                                'compression': stats['compression_ratio'],
                                'path': output_path
                            })
                            
                            # Save result for comparison (only first format)
                            if image_path not in self.app_state.optimized_results or format_type == proc_config.formats[0]:
                                self.app_state.optimized_results[image_path] = output_path
                        elif error_msg:
                            self.after(0, lambda msg=error_msg, img=os.path.basename(image_path), fmt=format_type: 
                                self._append_result(f"✗ {img} ({fmt}): {msg}"))
                        
                        completed += 1
                        progress = completed / total_tasks if total_tasks > 0 else 0
                        self.after(0, lambda p=progress: self.progress_bar.set(p))
                
                except Exception as e:
                    error_msg = f"Error procesando {os.path.basename(image_path)}: {str(e)}"
                    self.after(0, lambda msg=error_msg: self._append_result(msg))
                    completed += len(proc_config.formats)
            
            self.after(0, lambda: self._show_results(results))
            
        except Exception as e:
            self.after(0, lambda: self._show_message(f"Error durante el procesamiento: {str(e)}"))
        finally:
            self.after(0, lambda: self.optimize_button.configure(state="normal"))
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.progress_label.configure(text="Completado"))
            
            # Update comparison if there's an active image
            if self.app_state.current_preview_image and self.app_state.current_preview_image in self.app_state.optimized_results:
                self.after(0, lambda: self._select_image(self.app_state.active_image_index))
    
    def _show_results(self, results: List[dict]):
        """Shows processing results."""
        if not results:
            self.results_text.insert("end", "No se generaron archivos.\n")
            return
        
        total_original = sum(r['original_size'] for r in results)
        total_new = sum(r['new_size'] for r in results)
        total_saved = total_original - total_new
        total_compression = (total_saved / total_original * 100) if total_original > 0 else 0
        
        self.results_text.insert("end", f"✓ Procesamiento completado\n\n")
        self.results_text.insert("end", f"Archivos generados: {len(results)}\n")
        self.results_text.insert("end", f"Tamaño original: {format_file_size(total_original)}\n")
        self.results_text.insert("end", f"Tamaño optimizado: {format_file_size(total_new)}\n")
        self.results_text.insert("end", f"Espacio ahorrado: {format_file_size(total_saved)} ({total_compression:.1f}%)\n\n")
        self.results_text.insert("end", "Archivos:\n")
        self.results_text.insert("end", "-" * 50 + "\n")
        
        for result in results:
            self.results_text.insert("end", f"\n{result['original']} → {result['output']}\n")
            self.results_text.insert("end", f"  {format_file_size(result['original_size'])} → {format_file_size(result['new_size'])} ({result['compression']:.1f}%)\n")
    
    def _append_result(self, message: str):
        """Adds a message to the results area."""
        self.results_text.insert("end", message + "\n")
    
    def _on_remove_background(self):
        """Handles background removal for the selected image."""
        # Check if rembg is available
        if not check_rembg_available():
            self._show_message(
                "rembg no está disponible.\n\n"
                "Instala con: pip install rembg\n\n"
                "Nota: La primera vez que uses rembg, descargará un modelo "
                "que puede tardar unos minutos."
            )
            return
        
        # Check if there's a selected image
        if not self.app_state.current_preview_image:
            self._show_message("Por favor, selecciona una imagen primero.")
            return
        
        image_path = self.app_state.current_preview_image
        
        # Generate output filename
        output_path = generate_output_filename(
            image_path,
            'png',
            self.app_state.output_folder,
            None  # Use original name with suffix
        )
        # Modify to add _no_bg suffix
        path_obj = Path(output_path)
        output_path = str(path_obj.parent / f"{path_obj.stem}_no_bg{path_obj.suffix}")
        
        # Disable button during processing
        self.remove_bg_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Quitando background...")
        
        # Process in separate thread
        def process_bg_removal():
            try:
                success, error_msg = remove_background(image_path, output_path)
                
                if success:
                    # Update comparison view
                    self.after(0, lambda: self.comparison_view.display_optimized(
                        output_path,
                        f"Sin background: {format_file_size(get_file_size(output_path))}"
                    ))
                    
                    # Show success message
                    self.after(0, lambda: self._append_result(
                        f"✓ Background removido: {os.path.basename(output_path)}"
                    ))
                    
                    # Update results
                    stats = ImageProcessor.calculate_compression_stats(
                        image_path,
                        output_path
                    )
                    self.after(0, lambda: self._append_result(
                        f"  Original: {stats['original_size_formatted']} → "
                        f"Resultado: {stats['optimized_size_formatted']}"
                    ))
                else:
                    self.after(0, lambda: self._show_message(
                        f"Error al quitar el background:\n{error_msg or 'Error desconocido'}"
                    ))
            except Exception as e:
                self.after(0, lambda: self._show_message(
                    f"Error al quitar el background:\n{str(e)}"
                ))
            finally:
                self.after(0, lambda: self.remove_bg_button.configure(state="normal"))
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.after(0, lambda: self.progress_label.configure(text="Completado"))
        
        thread = threading.Thread(target=process_bg_removal, daemon=True)
        thread.start()
    
    def _show_message(self, message: str):
        """Shows a message to the user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Mensaje")
        dialog.geometry("400x150")
        dialog.transient(self)
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=30, padx=20)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)
