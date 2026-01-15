"""
Configuration manager.
Handles app settings and credential paths.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """
    Simple configuration manager with JSON storage.
    """
    
    DEFAULT_CONFIG = {
        "start_with_windows": False,
        "hotkey": "ctrl+shift+p",
        "theme": "dark",
        "default_tasklist": None,
        "show_notifications": True,
        "overlay_width_percent": 30,
    }
    
    def __init__(self, config_dir: Path):
        """
        Initialize configuration.
        
        Args:
            config_dir: Directory for config files
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "settings.json"
        self._config = {}
        self._load()
        
    def _load(self):
        """Load configuration from file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                self._config = {}
                
        # Merge with defaults
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value
                
    def _save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self._save()
        
    def delete(self, key: str):
        """
        Delete a configuration key.
        
        Args:
            key: Configuration key to delete
        """
        if key in self._config:
            del self._config[key]
            self._save()
            
    def reset(self):
        """Reset configuration to defaults."""
        self._config = dict(self.DEFAULT_CONFIG)
        self._save()
        
    @property
    def all(self) -> dict:
        """Get all configuration values."""
        return dict(self._config)
