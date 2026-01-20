"""
Configuration management for Easy Bulk GIF Optimizer.
Handles saving and loading user settings.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages application configuration."""

    DEFAULT_SETTINGS = {
        'quality': 70,          # Overall quality (1-100)
        'width': 320,           # Output width in pixels (0 = original) - NEW DEFAULT
        'height': 0,            # Output height in pixels (0 = original)
        'fps': 20,              # Frames per second (5-60) - NEW DEFAULT
        'lossy_quality': 80,    # Compression level (1-100)
        'motion_quality': 80,   # Motion handling quality (1-100)
        'keep_temp_files': True,  # Keep extracted video frames (Mode 1)
        'last_input_folder': '',  # Last used input folder path
        'last_output_folder': ''  # Last used output folder path
    }

    def __init__(self, config_path: Path = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file. Defaults to config.json in app directory.
        """
        if config_path is None:
            # Store config in same directory as application
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller exe - use directory where exe is located
                app_dir = Path(sys.executable).parent
            else:
                # Running in development mode - files are in root
                app_dir = Path(__file__).parent.parent
            self.config_path = app_dir / 'config.json'
        else:
            self.config_path = Path(config_path)

        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load settings from config file.

        Returns:
            Dictionary of settings (uses defaults if file doesn't exist)
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded_settings}
            else:
                # Use defaults if no config file exists, and create the file
                self.settings = self.DEFAULT_SETTINGS.copy()
                self.save(self.settings)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()

        return self.settings

    def save(self, settings: Dict[str, Any]) -> bool:
        """Save settings to config file.

        Args:
            settings: Dictionary of settings to save

        Returns:
            True if successful, False otherwise
        """
        try:
            self.settings = settings
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
            return False

    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset settings to defaults and save.

        Returns:
            Dictionary of default settings
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save(self.settings)
        return self.settings

    def get(self, key: str, default=None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if key doesn't exist

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
