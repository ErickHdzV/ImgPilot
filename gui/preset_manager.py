"""Preset manager for optimization configurations."""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class PresetManager:
    """Manages loading and saving of configuration presets."""
    
    def __init__(self):
        """Initializes the preset manager."""
        # Configuration directory in user's home directory
        self.config_dir = Path.home() / ".imgpilot"
        self.presets_file = self.config_dir / "presets.json"
        
        # Create directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing presets
        self.presets = self._load_presets()
        
        # Create default presets if they don't exist
        if not self.presets:
            self._create_default_presets()
    
    def _load_presets(self) -> Dict[str, Dict[str, Any]]:
        """Loads presets from JSON file."""
        if not self.presets_file.exists():
            return {}
        
        try:
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Silent error - default presets will be created
            return {}
    
    def _save_presets(self) -> bool:
        """Saves presets to JSON file."""
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            # Silent error - presets won't be saved but app will continue working
            return False
    
    def _create_default_presets(self):
        """Creates default presets."""
        default_presets = {
            "Web - Balanceado": {
                "formats": {"webp": True, "avif": False, "png": False, "jpg": False, "ico": False},
                "quality": 80,
                "resize_enabled": False,
                "width": None,
                "height": None,
                "maintain_aspect": True,
                "resize_method": "LANCZOS",
                "preserve_exif": True
            },
            "Web - Alta Calidad": {
                "formats": {"webp": True, "avif": False, "png": False, "jpg": False, "ico": False},
                "quality": 95,
                "resize_enabled": False,
                "width": None,
                "height": None,
                "maintain_aspect": True,
                "resize_method": "LANCZOS",
                "preserve_exif": True
            },
            "Web - Máxima Compresión": {
                "formats": {"webp": True, "avif": False, "png": False, "jpg": False, "ico": False},
                "quality": 60,
                "resize_enabled": False,
                "width": None,
                "height": None,
                "maintain_aspect": True,
                "resize_method": "LANCZOS",
                "preserve_exif": False
            },
            "PNG - Sin Pérdida": {
                "formats": {"webp": False, "avif": False, "png": True, "jpg": False, "ico": False},
                "quality": 80,
                "resize_enabled": False,
                "width": None,
                "height": None,
                "maintain_aspect": True,
                "resize_method": "LANCZOS",
                "preserve_exif": True
            },
            "JPEG - Alta Calidad": {
                "formats": {"webp": False, "avif": False, "png": False, "jpg": True, "ico": False},
                "quality": 90,
                "resize_enabled": False,
                "width": None,
                "height": None,
                "maintain_aspect": True,
                "resize_method": "LANCZOS",
                "preserve_exif": True
            }
        }
        
        self.presets = default_presets
        self._save_presets()
    
    def save_preset(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Saves a preset with the specified name.
        
        Args:
            name: Preset name
            config: Dictionary with configuration
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not name or not name.strip():
            return False
        
        name = name.strip()
        self.presets[name] = config
        return self._save_presets()
    
    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Loads a preset by name.
        
        Args:
            name: Preset name
        
        Returns:
            Dictionary with configuration or None if it doesn't exist
        """
        return self.presets.get(name)
    
    def delete_preset(self, name: str) -> bool:
        """
        Deletes a preset.
        
        Args:
            name: Name of preset to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if name in self.presets:
            del self.presets[name]
            return self._save_presets()
        return False
    
    def list_presets(self) -> List[str]:
        """
        Gets the list of available preset names.
        
        Returns:
            List of preset names
        """
        return sorted(self.presets.keys())
    
    def preset_exists(self, name: str) -> bool:
        """
        Checks if a preset exists.
        
        Args:
            name: Preset name
        
        Returns:
            True if it exists, False otherwise
        """
        return name in self.presets
    
    def get_preset_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Gets the complete configuration of a preset.
        
        Args:
            name: Preset name
        
        Returns:
            Dictionary with configuration or None if it doesn't exist
        """
        return self.presets.get(name)

