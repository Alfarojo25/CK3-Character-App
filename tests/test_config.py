#!/usr/bin/env python3
"""
Tests for ConfigManager.
"""

import pytest
import json
import os
import tempfile
from src.utils.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        yield config_path
        
        # Cleanup
        if os.path.exists(config_path):
            os.remove(config_path)
    
    def test_initialization_new_config(self, temp_config_file):
        """Test initialization with new config file."""
        config = ConfigManager(config_file=temp_config_file)
        
        assert config is not None
        assert config.get("language") == "en"
        assert config.get("theme") == "dark"
    
    def test_get_default_value(self, temp_config_file):
        """Test getting default values."""
        config = ConfigManager(config_file=temp_config_file)
        
        assert config.get("language") == "en"
        assert config.get("auto_backup_enabled") is True
        assert config.get("auto_backup_interval") == "10min"
    
    def test_get_with_custom_default(self, temp_config_file):
        """Test getting value with custom default."""
        config = ConfigManager(config_file=temp_config_file)
        
        value = config.get("nonexistent_key", "custom_default")
        assert value == "custom_default"
    
    def test_set_and_get(self, temp_config_file):
        """Test setting and getting values."""
        config = ConfigManager(config_file=temp_config_file)
        
        config.set("language", "es")
        assert config.get("language") == "es"
        
        config.set("theme", "light")
        assert config.get("theme") == "light"
    
    def test_save_and_load(self, temp_config_file):
        """Test saving and loading config."""
        config1 = ConfigManager(config_file=temp_config_file)
        config1.set("language", "es")
        config1.set("theme", "light")
        config1.save()
        
        # Create new instance to load saved config
        config2 = ConfigManager(config_file=temp_config_file)
        assert config2.get("language") == "es"
        assert config2.get("theme") == "light"
    
    def test_add_recent_database(self, temp_config_file):
        """Test adding recent databases."""
        config = ConfigManager(config_file=temp_config_file)
        
        config.add_recent_database("db1")
        config.add_recent_database("db2")
        config.add_recent_database("db3")
        
        recent = config.get("recent_databases")
        assert "db1" in recent
        assert "db2" in recent
        assert "db3" in recent
    
    def test_recent_database_limit(self, temp_config_file):
        """Test recent databases limit."""
        config = ConfigManager(config_file=temp_config_file)
        max_recent = config.get("max_recent", 5)
        
        # Add more than max
        for i in range(max_recent + 3):
            config.add_recent_database(f"db{i}")
        
        recent = config.get("recent_databases")
        assert len(recent) <= max_recent
    
    def test_recent_database_duplicates(self, temp_config_file):
        """Test that duplicates move to front."""
        config = ConfigManager(config_file=temp_config_file)
        
        config.add_recent_database("db1")
        config.add_recent_database("db2")
        config.add_recent_database("db3")
        config.add_recent_database("db1")  # Duplicate
        
        recent = config.get("recent_databases")
        assert recent[0] == "db1"  # Should be at front
        assert recent.count("db1") == 1  # Should appear only once
