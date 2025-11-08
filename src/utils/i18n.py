"""
Internationalization (i18n) module for multi-language support.
Automatically detects and loads any JSON language file in locales/ directory.
"""

import json
import os
from typing import Dict, Optional, List
import logging


class I18n:
    """Internationalization manager with automatic language detection."""
    
    def __init__(self, lang_dir: str = "locales", default_lang: str = "en"):
        """
        Initialize i18n manager.
        
        Args:
            lang_dir: Directory containing language files
            default_lang: Default language code
        """
        self.lang_dir = lang_dir
        self.default_lang = default_lang
        self.current_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self.available_languages: List[Dict[str, str]] = []
        
        # Create directory if needed
        os.makedirs(lang_dir, exist_ok=True)
        
        # Load all languages
        self._load_all_languages()
        
        # Set current language
        if default_lang in self.translations:
            self.current_lang = default_lang
        elif self.available_languages:
            self.current_lang = self.available_languages[0]['code']
    
    def _load_all_languages(self):
        """Automatically load all JSON language files from locales directory."""
        if not os.path.exists(self.lang_dir):
            return
        
        # Scan for JSON files
        for filename in os.listdir(self.lang_dir):
            if filename.endswith('.json'):
                lang_code = filename[:-5]  # Remove .json
                file_path = os.path.join(self.lang_dir, filename)
                
                try:
                    # Try UTF-8 with BOM first, then regular UTF-8
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            data = json.load(f)
                    except:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    # Validate metadata
                    if 'language' not in data or 'language_code' not in data:
                        continue
                    
                    # Store translations (exclude metadata keys)
                    self.translations[lang_code] = {
                        k: v for k, v in data.items() 
                        if k not in ['language', 'language_code', 'language_native']
                    }
                    
                    # Store language info
                    self.available_languages.append({
                        'code': lang_code,
                        'name': data.get('language', lang_code),
                        'native': data.get('language_native', data.get('language', lang_code))
                    })
                        
                except Exception as e:
                    logging.error(f"Error loading {filename}: {e}")
        
        # Sort by name
        self.available_languages.sort(key=lambda x: x['name'])
    
    def set_language(self, lang_code: str) -> bool:
        """
        Set current language.
        
        Args:
            lang_code: Language code (e.g., 'en', 'es', 'zh')
            
        Returns:
            True if successful
        """
        if lang_code in self.translations:
            self.current_lang = lang_code
            return True
        return False
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Get list of available languages.
        
        Returns:
            List of dicts with 'code', 'name', and 'native' keys
        """
        return self.available_languages.copy()
    
    def t(self, key: str, **kwargs) -> str:
        """
        Get translated string (alias for get).
        
        Args:
            key: Translation key
            **kwargs: Variables for interpolation
            
        Returns:
            Translated string or key if not found
        """
        # Get from current language
        if self.current_lang in self.translations:
            translation = self.translations[self.current_lang].get(key)
            if translation:
                # Interpolate variables
                if kwargs:
                    try:
                        return translation.format(**kwargs)
                    except KeyError:
                        pass
                return translation
        
        # Fallback to default language
        if self.current_lang != self.default_lang and self.default_lang in self.translations:
            translation = self.translations[self.default_lang].get(key)
            if translation:
                if kwargs:
                    try:
                        return translation.format(**kwargs)
                    except KeyError:
                        pass
                return translation
        
        return key
    
    def get(self, key: str, fallback: Optional[str] = None) -> str:
        """
        Get translated string (deprecated, use t() instead).
        
        Args:
            key: Translation key
            fallback: Fallback text if translation not found
            
        Returns:
            Translated string or fallback or key
        """
        result = self.t(key)
        return result if result != key else (fallback if fallback else key)


# Global instance
_i18n_instance: Optional[I18n] = None


def get_i18n(lang_dir: str = "locales", default_lang: str = "en") -> I18n:
    """Get or create global i18n instance."""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(lang_dir, default_lang)
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """
    Shorthand function for translation.
    
    Args:
        key: Translation key
        **kwargs: Variables for interpolation
        
    Returns:
        Translated string
    """
    return get_i18n().t(key, **kwargs)
