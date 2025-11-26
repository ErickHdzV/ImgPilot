"""Reusable components for the graphical interface."""
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional, Callable
import os
from pathlib import Path


class ImagePreview(ctk.CTkFrame):
    """Component for displaying an image preview."""
    
    def __init__(self, parent, width=400, height=300, **kwargs):
        super().__init__(parent, **kwargs)
        self.width = width
        self.height = height
        self.current_image = None
        self.current_photo = None
        
        # Label to display the image
        self.image_label = ctk.CTkLabel(
            self,
            text="Sin imagen seleccionada",
            width=width,
            height=height
        )
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Label for image information
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=(0, 10))
    
    def display_image(self, image_path: str):
        """
        Displays an image in the preview.
        
        Args:
            image_path: Path of the image to display
        """
        try:
            # Load image
            img = Image.open(image_path)
            original_size = img.size
            
            # Resize to fit preview while maintaining aspect ratio
            img.thumbnail((self.width - 20, self.height - 60), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.current_photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.current_photo, text="")
            
            # Display information
            info_text = f"Dimensiones: {original_size[0]}x{original_size[1]} px"
            self.info_label.configure(text=info_text)
            
            self.current_image = img
            
        except Exception as e:
            self.image_label.configure(image="", text=f"Error al cargar imagen:\n{str(e)}")
            self.info_label.configure(text="")
            self.current_image = None
    
    def clear(self):
        """Clears the preview."""
        self.image_label.configure(image="", text="Sin imagen seleccionada")
        self.info_label.configure(text="")
        self.current_image = None
        self.current_photo = None


class QualitySlider(ctk.CTkFrame):
    """Slider component for quality control."""
    
    def __init__(self, parent, label="Calidad", default_value=80, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.label_text = ctk.CTkLabel(self, text=f"{label}:", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_text.pack(side="left", padx=(0, 10))
        
        self.slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_slider_change
        )
        self.slider.set(default_value)
        self.slider.pack(side="left", expand=True, fill="x", padx=10)
        
        self.value_label = ctk.CTkLabel(self, text=str(default_value), width=50)
        self.value_label.pack(side="right", padx=(10, 0))
        
        self._on_slider_change(default_value)
    
    def _on_slider_change(self, value):
        """Updates the label when the slider changes."""
        self.value_label.configure(text=str(int(value)))
    
    def get(self) -> int:
        """Gets the current slider value."""
        return int(self.slider.get())
    
    def set(self, value: int):
        """Sets the slider value."""
        self.slider.set(value)
        self.value_label.configure(text=str(int(value)))


class ImageThumbnail(ctk.CTkFrame):
    """Component for displaying an image thumbnail in the gallery."""
    
    def __init__(self, parent, image_path: str, on_click: Optional[Callable] = None, on_delete: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.image_path = image_path
        self.on_click = on_click
        self.on_delete = on_delete
        self.is_selected = False
        self.current_photo = None
        
        # Configure style
        self.configure(cursor="hand2", corner_radius=8)
        
        # Frame for the image with relative positioning for delete button
        self.image_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.image_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Container for image and delete button
        self.image_container = ctk.CTkFrame(self.image_frame, fg_color="transparent")
        self.image_container.pack(fill="both", expand=True)
        
        # Label for the image
        self.image_label = ctk.CTkLabel(
            self.image_container,
            text="",
            width=120,
            height=120
        )
        self.image_label.pack(expand=True, fill="both")
        
        # Delete button (only show on hover)
        self.delete_button = ctk.CTkButton(
            self.image_container,
            text="✕",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            command=self._on_delete_click,
            corner_radius=12,
            cursor="hand2"
        )
        # Prevent click propagation
        self.delete_button.bind("<Button-1>", lambda e: "break")
        # Position delete button in top-right corner using place
        self.delete_button.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)
        self.delete_button.lower()  # Put it behind initially
        self.delete_button_visible = False
        self._hide_button_id = None  # Store after() call ID to cancel if needed
        
        # Label for the filename
        filename = os.path.basename(image_path)
        if len(filename) > 20:
            filename = filename[:17] + "..."
        
        self.name_label = ctk.CTkLabel(
            self,
            text=filename,
            font=ctk.CTkFont(size=10),
            wraplength=130
        )
        self.name_label.pack(pady=(0, 5))
        
        # Load thumbnail
        self._load_thumbnail()
        
        # Bind eventos
        self.bind("<Button-1>", self._on_click)
        self.image_label.bind("<Button-1>", self._on_click)
        self.name_label.bind("<Button-1>", self._on_click)
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.image_frame.bind("<Enter>", self._on_enter)
        self.image_frame.bind("<Leave>", self._on_leave)
        self.image_container.bind("<Enter>", self._on_enter)
        self.image_container.bind("<Leave>", self._on_leave)
        # Also bind hover events to delete button to keep it visible when hovering over it
        self.delete_button.bind("<Enter>", self._on_enter)
        self.delete_button.bind("<Leave>", self._on_leave)
    
    def _on_delete_click(self, event=None):
        """Handles delete button click."""
        # Stop event propagation
        if event:
            event.stop = True
        if self.on_delete:
            self.on_delete(self.image_path)
    
    def _load_thumbnail(self):
        """Loads the image thumbnail."""
        try:
            img = Image.open(self.image_path)
            img.thumbnail((120, 120), Image.Resampling.LANCZOS)
            self.current_photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.current_photo)
        except Exception as e:
            self.image_label.configure(text="Error", image="")
    
    def _on_click(self, event):
        """Handles click on thumbnail."""
        if self.on_click:
            self.on_click(self.image_path)
    
    def _on_enter(self, event):
        """Hover effect on enter."""
        # Cancel any pending hide operation
        if self._hide_button_id is not None:
            self.after_cancel(self._hide_button_id)
            self._hide_button_id = None
        
        if not self.is_selected:
            self.configure(fg_color=("gray80", "gray30"))
        # Show delete button on hover
        if self.on_delete and not self.delete_button_visible:
            self.delete_button.lift()
            self.delete_button_visible = True
    
    def _on_leave(self, event):
        """Hover effect on leave."""
        if not self.is_selected:
            self.configure(fg_color=("gray90", "gray20"))
        # Hide delete button with a small delay to allow mouse to move to button
        # This prevents the button from disappearing when moving mouse to click it
        if self.on_delete and self.delete_button_visible:
            # Cancel any previous hide operation
            if self._hide_button_id is not None:
                self.after_cancel(self._hide_button_id)
            # Schedule hide after a short delay
            self._hide_button_id = self.after(150, self._hide_delete_button)
    
    def _hide_delete_button(self):
        """Actually hides the delete button."""
        # Double-check mouse is not over component or button before hiding
        x, y = self.winfo_pointerxy()
        widget_under_mouse = self.winfo_containing(x, y)
        
        # If mouse is still over this component or delete button, don't hide
        if widget_under_mouse:
            # Check if it's this component or any of its children
            current = widget_under_mouse
            while current:
                if current == self or current == self.delete_button:
                    # Mouse is still over component or button, reschedule check
                    self._hide_button_id = self.after(100, self._hide_delete_button)
                    return
                try:
                    current = current.master
                except:
                    break
        
        # Mouse is really gone, hide the button
        if self.delete_button_visible:
            self.delete_button.lower()
            self.delete_button_visible = False
        self._hide_button_id = None
    
    def set_selected(self, selected: bool):
        """Marks the thumbnail as selected."""
        self.is_selected = selected
        if selected:
            self.configure(fg_color=("#3B8ED0", "#1F6AA5"), border_width=2, border_color=("#1F6AA5", "#3B8ED0"))
        else:
            self.configure(fg_color=("gray90", "gray20"), border_width=0)


class BeforeAfterView(ctk.CTkFrame):
    """Component for before/after comparison."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.original_image_path = None
        self.optimized_image_path = None
        self.original_photo = None
        self.optimized_photo = None
        self.split_position = 0.5  # 0.0 to 1.0
        
        # Main frame with panels
        self.panels_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.panels_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel (original)
        self.original_frame = ctk.CTkFrame(self.panels_frame)
        self.original_frame.pack(side="left", fill="both", expand=True, padx=(0, 2))
        
        self.original_label = ctk.CTkLabel(
            self.original_frame,
            text="Original",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.original_label.pack(pady=5)
        
        self.original_image_label = ctk.CTkLabel(
            self.original_frame,
            text="Sin imagen",
            width=300,
            height=300
        )
        self.original_image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.original_info_label = ctk.CTkLabel(
            self.original_frame,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.original_info_label.pack(pady=(0, 10))
        
        # Right panel (optimized)
        self.optimized_frame = ctk.CTkFrame(self.panels_frame)
        self.optimized_frame.pack(side="right", fill="both", expand=True, padx=(2, 0))
        
        self.optimized_label = ctk.CTkLabel(
            self.optimized_frame,
            text="Optimizada",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.optimized_label.pack(pady=5)
        
        self.optimized_image_label = ctk.CTkLabel(
            self.optimized_frame,
            text="Sin imagen",
            width=300,
            height=300
        )
        self.optimized_image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.optimized_info_label = ctk.CTkLabel(
            self.optimized_frame,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.optimized_info_label.pack(pady=(0, 10))
    
    def display_original(self, image_path: str, info: Optional[str] = None):
        """Displays the original image."""
        self.original_image_path = image_path
        try:
            img = Image.open(image_path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            self.original_photo = ImageTk.PhotoImage(img)
            self.original_image_label.configure(image=self.original_photo, text="")
            
            if info:
                self.original_info_label.configure(text=info)
            else:
                size = img.size
                file_size = os.path.getsize(image_path)
                size_mb = file_size / (1024 * 1024)
                self.original_info_label.configure(
                    text=f"{size[0]}x{size[1]} px | {size_mb:.2f} MB"
                )
        except Exception as e:
            self.original_image_label.configure(image="", text=f"Error: {str(e)}")
    
    def display_optimized(self, image_path: Optional[str], info: Optional[str] = None):
        """Displays the optimized image."""
        if image_path is None:
            self.optimized_image_label.configure(image="", text="Sin imagen optimizada")
            self.optimized_info_label.configure(text="")
            return
        
        self.optimized_image_path = image_path
        try:
            img = Image.open(image_path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            self.optimized_photo = ImageTk.PhotoImage(img)
            self.optimized_image_label.configure(image=self.optimized_photo, text="")
            
            if info:
                self.optimized_info_label.configure(text=info)
            else:
                size = img.size
                file_size = os.path.getsize(image_path)
                size_mb = file_size / (1024 * 1024)
                self.optimized_info_label.configure(
                    text=f"{size[0]}x{size[1]} px | {size_mb:.2f} MB"
                )
        except Exception as e:
            self.optimized_image_label.configure(image="", text=f"Error: {str(e)}")
    
    def clear(self):
        """Clears both views."""
        self.original_image_label.configure(image="", text="Sin imagen")
        self.optimized_image_label.configure(image="", text="Sin imagen")
        self.original_info_label.configure(text="")
        self.optimized_info_label.configure(text="")


class CollapsibleFrame(ctk.CTkFrame):
    """Collapsible frame for options."""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.is_expanded = True
        self.title = title
        
        # Toggle button
        self.toggle_button = ctk.CTkButton(
            self,
            text=f"▼ {title}",
            command=self.toggle,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            text_color=("black", "white"),  # Black in light mode, white in dark mode
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.toggle_button.pack(fill="x", padx=5, pady=5)
        
        # Frame for content
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def toggle(self):
        """Toggles between expanded and collapsed."""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            self.toggle_button.configure(text=f"▼ {self.title}")
        else:
            self.content_frame.pack_forget()
            self.toggle_button.configure(text=f"▶ {self.title}")
    
    def get_content_frame(self):
        """Returns the content frame for adding widgets."""
        return self.content_frame


class DropZone(ctk.CTkFrame):
    """Drag & drop zone for files."""
    
    def __init__(self, parent, on_drop: Optional[Callable] = None, on_click: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_drop = on_drop
        self.on_click = on_click
        self.is_dragging = False
        
        self.configure(border_width=2, border_color=("gray60", "gray40"), corner_radius=10, cursor="hand2")
        
        # Main label
        self.label = ctk.CTkLabel(
            self,
            text="Arrastra imágenes aquí\no haz clic para seleccionar",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray50"),
            cursor="hand2"
        )
        self.label.pack(expand=True, fill="both", pady=20)
        
        # Bind click events
        if on_click:
            self.bind("<Button-1>", lambda e: on_click())
            self.label.bind("<Button-1>", lambda e: on_click())
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Visual effect on enter."""
        if not self.is_dragging:
            self.configure(border_color=("#3B8ED0", "#1F6AA5"))
            self.label.configure(text_color=("#3B8ED0", "#1F6AA5"))
    
    def _on_leave(self, event):
        """Visual effect on leave."""
        if not self.is_dragging:
            self.configure(border_color=("gray60", "gray40"))
            self.label.configure(text_color=("gray50", "gray50"))
    
    def set_dragging(self, dragging: bool):
        """Updates the dragging state."""
        self.is_dragging = dragging
        if dragging:
            self.configure(border_color=("#3B8ED0", "#1F6AA5"), border_width=3)
            self.label.configure(text="Suelta aquí", text_color=("#3B8ED0", "#1F6AA5"))
        else:
            self.configure(border_color=("gray60", "gray40"), border_width=2)
            self.label.configure(text="Arrastra imágenes aquí\no haz clic para seleccionar", text_color=("gray50", "gray50"))

