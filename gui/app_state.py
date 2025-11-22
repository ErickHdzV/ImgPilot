"""Application state management."""
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ProcessingConfig:
    """Configuration for image processing."""
    formats: List[str] = field(default_factory=lambda: ['webp'])
    quality: int = 80
    preserve_exif: bool = True
    resize_enabled: bool = False
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect: bool = True
    resize_method: str = 'LANCZOS'
    custom_filename: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Converts configuration to dictionary."""
        return {
            'formats': self.formats,
            'quality': self.quality,
            'preserve_exif': self.preserve_exif,
            'resize_enabled': self.resize_enabled,
            'width': self.width,
            'height': self.height,
            'maintain_aspect': self.maintain_aspect,
            'resize_method': self.resize_method,
            'custom_filename': self.custom_filename,
        }
    
    def get_resize_config(self) -> Optional[Dict]:
        """Returns resize configuration if enabled."""
        if not self.resize_enabled:
            return None
        
        return {
            'width': self.width,
            'height': self.height,
            'maintain_aspect': self.maintain_aspect,
            'method': self.resize_method,
        }


@dataclass
class AppState:
    """Global application state."""
    selected_images: List[str] = field(default_factory=list)
    output_folder: Optional[str] = None
    current_preview_image: Optional[str] = None
    active_image_index: int = 0
    optimized_results: Dict[str, str] = field(default_factory=dict)  # original_path -> optimized_path
    processing_config: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    def clear(self):
        """Clears application state."""
        self.selected_images.clear()
        self.output_folder = None
        self.current_preview_image = None
        self.active_image_index = 0
        self.optimized_results.clear()
        self.processing_config = ProcessingConfig()
    
    def add_images(self, image_paths: List[str]):
        """Adds images to the selected list."""
        for path in image_paths:
            if path not in self.selected_images:
                self.selected_images.append(path)
    
    def set_active_image(self, index: int):
        """Sets the active image by index."""
        if 0 <= index < len(self.selected_images):
            self.active_image_index = index
            self.current_preview_image = self.selected_images[index]

