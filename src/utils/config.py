"""
Configuration Manager
Handles application settings persistence.
"""

import json
import os
from typing import Any, Optional
import logging


class ConfigManager:
    """Manages application configuration."""
    
    # Default database location in Documents folder
    _default_db_dir = os.path.join(
        os.path.expanduser("~"),
        "Documents",
        "CK3-Character-Manager"
    )
    
    DEFAULT_CONFIG = {
        "language": "en",
        "database_directory": _default_db_dir,
        "last_database": "default",
        "last_gallery": None,
        "window_geometry": "1600x900",
        "theme": "dark",
        "auto_backup_enabled": True,
        "auto_backup_interval": "10min",  # "disabled", "1min", "5min", "10min", "30min"
        "auto_backup_max_count": 10,
        "show_welcome": True,
        "recent_databases": [],
        "max_recent": 5,
        "sort_by": "name",  # "name", "created", "modified", "tags"
        "sort_order": "asc"  # "asc", "desc"
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new keys were added)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                logging.error(f"Error loading config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        else:
            logging.info("No config file found, creating default")
            return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.debug("Configuration saved")
        except IOError as e:
            logging.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            save: Whether to save immediately
        """
        self.config[key] = value
        if save:
            self.save()
        logging.debug(f"Config updated: {key} = {value}")
    
    def add_recent_database(self, db_name: str):
        """
        Add database to recent list.
        
        Args:
            db_name: Database name
        """
        recent = self.config.get("recent_databases", [])
        
        # Remove if already exists
        if db_name in recent:
            recent.remove(db_name)
        
        # Add to front
        recent.insert(0, db_name)
        
        # Trim to max
        max_recent = self.config.get("max_recent", 5)
        recent = recent[:max_recent]
        
        self.set("recent_databases", recent)
    
    def get_recent_databases(self) -> list:
        """Get list of recent databases."""
        return self.config.get("recent_databases", [])
    
    def is_first_run(self) -> bool:
        """Check if this is the first run (show welcome dialog)."""
        return self.config.get("show_welcome", True)
    
    def mark_welcome_shown(self):
        """Mark that welcome dialog has been shown."""
        self.set("show_welcome", False)


# Global config instance
_config_instance: Optional[ConfigManager] = None


def get_config(config_file: str = "config.json") -> ConfigManager:
    """
    Get or create global config instance.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Global ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_file)
    return _config_instance
