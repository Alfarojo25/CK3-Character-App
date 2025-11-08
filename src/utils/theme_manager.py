#!/usr/bin/env python3
"""
Theme Manager for CK3 Character Manager
Handles dark/light theme switching and persistence
"""

from typing import Dict, Any


class Theme:
    """Base theme class."""
    
    def __init__(self):
        self.colors = {}
    
    def get_color(self, key: str) -> str:
        """Get color value by key."""
        return self.colors.get(key, "#000000")


class DarkTheme(Theme):
    """Dark theme color scheme."""
    
    def __init__(self):
        super().__init__()
        self.colors = {
            # Main backgrounds
            "bg_primary": "#1e1e1e",
            "bg_secondary": "#2e2e2e",
            "bg_tertiary": "#3e3e3e",
            
            # Text colors
            "fg_primary": "#eeeeee",
            "fg_secondary": "#cccccc",
            "fg_tertiary": "#aaaaaa",
            "fg_disabled": "#666666",
            
            # Accent colors
            "accent_primary": "#0d7377",
            "accent_secondary": "#14ffec",
            "accent_hover": "#0a5c5f",
            
            # Status colors
            "success": "#00FF00",
            "error": "#FF0000",
            "warning": "#FFA500",
            "info": "#00BFFF",
            
            # UI elements
            "border": "#555555",
            "selection": "#264f78",
            "highlight": "#094771",
            "canvas_bg": "#252526",
            
            # Button colors
            "button_bg": "#2e2e2e",
            "button_fg": "#eeeeee",
            "button_hover": "#3e3e3e",
            "button_active": "#094771",
            
            # Entry/Input colors
            "entry_bg": "#1e1e1e",
            "entry_fg": "#eeeeee",
            "entry_border": "#555555",
            "entry_focus": "#0d7377",
            
            # Listbox colors
            "listbox_bg": "#1e1e1e",
            "listbox_fg": "#eeeeee",
            "listbox_select_bg": "#264f78",
            "listbox_select_fg": "#ffffff",
            
            # Menu colors
            "menu_bg": "#2e2e2e",
            "menu_fg": "#eeeeee",
            "menu_select_bg": "#094771",
            "menu_select_fg": "#ffffff",
            
            # Scrollbar colors
            "scrollbar_bg": "#2e2e2e",
            "scrollbar_fg": "#555555",
            "scrollbar_active": "#666666",
        }


class LightTheme(Theme):
    """Light theme color scheme."""
    
    def __init__(self):
        super().__init__()
        self.colors = {
            # Main backgrounds
            "bg_primary": "#ffffff",
            "bg_secondary": "#f5f5f5",
            "bg_tertiary": "#e0e0e0",
            
            # Text colors
            "fg_primary": "#000000",
            "fg_secondary": "#333333",
            "fg_tertiary": "#666666",
            "fg_disabled": "#999999",
            
            # Accent colors
            "accent_primary": "#0078d4",
            "accent_secondary": "#106ebe",
            "accent_hover": "#005a9e",
            
            # Status colors
            "success": "#107c10",
            "error": "#e81123",
            "warning": "#ff8c00",
            "info": "#0078d4",
            
            # UI elements
            "border": "#cccccc",
            "selection": "#cce8ff",
            "highlight": "#b3d9ff",
            "canvas_bg": "#fafafa",
            
            # Button colors
            "button_bg": "#f0f0f0",
            "button_fg": "#000000",
            "button_hover": "#e0e0e0",
            "button_active": "#cce8ff",
            
            # Entry/Input colors
            "entry_bg": "#ffffff",
            "entry_fg": "#000000",
            "entry_border": "#cccccc",
            "entry_focus": "#0078d4",
            
            # Listbox colors
            "listbox_bg": "#ffffff",
            "listbox_fg": "#000000",
            "listbox_select_bg": "#cce8ff",
            "listbox_select_fg": "#000000",
            
            # Menu colors
            "menu_bg": "#f0f0f0",
            "menu_fg": "#000000",
            "menu_select_bg": "#cce8ff",
            "menu_select_fg": "#000000",
            
            # Scrollbar colors
            "scrollbar_bg": "#f0f0f0",
            "scrollbar_fg": "#cccccc",
            "scrollbar_active": "#999999",
        }


class ThemeManager:
    """Manages application themes."""
    
    THEMES = {
        "dark": DarkTheme(),
        "light": LightTheme()
    }
    
    def __init__(self, theme_name: str = "dark"):
        """Initialize theme manager with specified theme."""
        self.current_theme_name = theme_name
        self.current_theme = self.THEMES.get(theme_name, self.THEMES["dark"])
    
    def get_theme(self) -> Theme:
        """Get current theme."""
        return self.current_theme
    
    def get_theme_name(self) -> str:
        """Get current theme name."""
        return self.current_theme_name
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set theme by name.
        
        Args:
            theme_name: Name of theme ("dark" or "light")
            
        Returns:
            True if theme was changed, False otherwise
        """
        if theme_name not in self.THEMES:
            return False
        
        if theme_name == self.current_theme_name:
            return False
        
        self.current_theme_name = theme_name
        self.current_theme = self.THEMES[theme_name]
        return True
    
    def get_available_themes(self) -> list:
        """Get list of available theme names."""
        return list(self.THEMES.keys())
    
    def get_color(self, key: str) -> str:
        """Get color from current theme."""
        return self.current_theme.get_color(key)
    
    def get_style_config(self) -> Dict[str, Any]:
        """Get ttk style configuration for current theme."""
        theme = self.current_theme
        return {
            "TFrame": {
                "configure": {
                    "background": theme.get_color("bg_secondary")
                }
            },
            "TLabel": {
                "configure": {
                    "background": theme.get_color("bg_secondary"),
                    "foreground": theme.get_color("fg_primary")
                }
            },
            "TButton": {
                "configure": {
                    "background": theme.get_color("button_bg"),
                    "foreground": theme.get_color("button_fg"),
                    "borderwidth": 1,
                    "relief": "raised"
                },
                "map": {
                    "background": [
                        ("active", theme.get_color("button_hover")),
                        ("pressed", theme.get_color("button_active"))
                    ]
                }
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": theme.get_color("entry_bg"),
                    "foreground": theme.get_color("entry_fg"),
                    "bordercolor": theme.get_color("entry_border"),
                    "insertcolor": theme.get_color("fg_primary")
                },
                "map": {
                    "bordercolor": [("focus", theme.get_color("entry_focus"))]
                }
            },
            "TCombobox": {
                "configure": {
                    "fieldbackground": theme.get_color("entry_bg"),
                    "background": theme.get_color("button_bg"),
                    "foreground": theme.get_color("entry_fg"),
                    "arrowcolor": theme.get_color("fg_primary"),
                    "bordercolor": theme.get_color("entry_border")
                },
                "map": {
                    "fieldbackground": [("readonly", theme.get_color("entry_bg"))],
                    "foreground": [("readonly", theme.get_color("entry_fg"))],
                    "bordercolor": [("focus", theme.get_color("entry_focus"))]
                }
            },
            "Vertical.TScrollbar": {
                "configure": {
                    "background": theme.get_color("scrollbar_bg"),
                    "troughcolor": theme.get_color("scrollbar_bg"),
                    "bordercolor": theme.get_color("border"),
                    "arrowcolor": theme.get_color("fg_primary")
                },
                "map": {
                    "background": [
                        ("active", theme.get_color("scrollbar_active")),
                        ("pressed", theme.get_color("scrollbar_fg"))
                    ]
                }
            }
        }
