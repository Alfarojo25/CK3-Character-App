#!/usr/bin/env python3
"""
Tests for ThemeManager.
"""

import pytest
from src.utils.theme_manager import ThemeManager, DarkTheme, LightTheme


class TestTheme:
    """Test cases for Theme classes."""
    
    def test_dark_theme_colors(self):
        """Test dark theme color definitions."""
        theme = DarkTheme()
        
        # Primary colors
        assert theme.get_color("bg_primary") == "#1e1e1e"
        assert theme.get_color("fg_primary") == "#eeeeee"
        assert theme.get_color("accent_primary") == "#0078d4"
        
        # Menu colors
        assert theme.get_color("menu_bg") == "#252526"
        assert theme.get_color("menu_fg") == "#cccccc"
        
        # Button colors
        assert theme.get_color("button_bg") == "#2d2d30"
        assert theme.get_color("button_fg") == "#e0e0e0"
    
    def test_light_theme_colors(self):
        """Test light theme color definitions."""
        theme = LightTheme()
        
        # Primary colors
        assert theme.get_color("bg_primary") == "#ffffff"
        assert theme.get_color("fg_primary") == "#000000"
        assert theme.get_color("accent_primary") == "#0078d4"
        
        # Menu colors
        assert theme.get_color("menu_bg") == "#f0f0f0"
        assert theme.get_color("menu_fg") == "#1e1e1e"
        
        # Button colors
        assert theme.get_color("button_bg") == "#e0e0e0"
        assert theme.get_color("button_fg") == "#1e1e1e"
    
    def test_theme_missing_color(self):
        """Test getting nonexistent color."""
        theme = DarkTheme()
        
        color = theme.get_color("nonexistent_color")
        assert color == "#000000"  # Default fallback


class TestThemeManager:
    """Test cases for ThemeManager class."""
    
    def test_initialization(self):
        """Test ThemeManager initialization."""
        manager = ThemeManager()
        
        assert manager is not None
        assert manager.current_theme == "dark"
    
    def test_initialization_with_theme(self):
        """Test initialization with specific theme."""
        manager = ThemeManager(theme_name="light")
        
        assert manager.current_theme == "light"
    
    def test_get_theme_dark(self):
        """Test getting dark theme."""
        manager = ThemeManager(theme_name="dark")
        theme = manager.get_theme()
        
        assert isinstance(theme, DarkTheme)
        assert theme.get_color("bg_primary") == "#1e1e1e"
    
    def test_get_theme_light(self):
        """Test getting light theme."""
        manager = ThemeManager(theme_name="light")
        theme = manager.get_theme()
        
        assert isinstance(theme, LightTheme)
        assert theme.get_color("bg_primary") == "#ffffff"
    
    def test_set_theme(self):
        """Test setting theme."""
        manager = ThemeManager(theme_name="dark")
        
        manager.set_theme("light")
        assert manager.current_theme == "light"
        
        theme = manager.get_theme()
        assert isinstance(theme, LightTheme)
    
    def test_set_invalid_theme(self):
        """Test setting invalid theme."""
        manager = ThemeManager(theme_name="dark")
        
        manager.set_theme("invalid")
        assert manager.current_theme == "dark"  # Should fallback to dark
    
    def test_get_style_config_dark(self):
        """Test getting ttk style config for dark theme."""
        manager = ThemeManager(theme_name="dark")
        styles = manager.get_style_config()
        
        assert "TButton" in styles
        assert "TFrame" in styles
        assert "TLabel" in styles
        
        # Check button config
        button_config = styles["TButton"]
        assert button_config["background"] == "#2d2d30"
        assert button_config["foreground"] == "#e0e0e0"
    
    def test_get_style_config_light(self):
        """Test getting ttk style config for light theme."""
        manager = ThemeManager(theme_name="light")
        styles = manager.get_style_config()
        
        assert "TButton" in styles
        assert "TFrame" in styles
        assert "TLabel" in styles
        
        # Check button config
        button_config = styles["TButton"]
        assert button_config["background"] == "#e0e0e0"
        assert button_config["foreground"] == "#1e1e1e"
    
    def test_theme_consistency(self):
        """Test that both themes have same color keys."""
        dark = DarkTheme()
        light = LightTheme()
        
        dark_keys = set(dark.colors.keys())
        light_keys = set(light.colors.keys())
        
        assert dark_keys == light_keys
