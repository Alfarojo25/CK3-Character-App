#!/usr/bin/env python3
"""
Tests for i18n module.
"""

import pytest
import json
import os
import tempfile
from src.utils.i18n import I18n


class TestI18n:
    """Test cases for I18n class."""
    
    @pytest.fixture
    def temp_locales_dir(self):
        """Create temporary locales directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            locales_dir = os.path.join(tmpdir, "locales")
            os.makedirs(locales_dir)
            
            # Create English locale
            en_data = {
                "language": "English",
                "language_code": "en",
                "language_native": "English",
                "hello": "Hello",
                "greeting": "Hello, {name}!",
                "items_count": "You have {count} items"
            }
            
            with open(os.path.join(locales_dir, "en.json"), "w", encoding="utf-8") as f:
                json.dump(en_data, f, ensure_ascii=False, indent=2)
            
            # Create Spanish locale
            es_data = {
                "language": "Spanish",
                "language_code": "es",
                "language_native": "Español",
                "hello": "Hola",
                "greeting": "¡Hola, {name}!",
                "items_count": "Tienes {count} artículos"
            }
            
            with open(os.path.join(locales_dir, "es.json"), "w", encoding="utf-8") as f:
                json.dump(es_data, f, ensure_ascii=False, indent=2)
            
            yield locales_dir
    
    def test_initialization(self, temp_locales_dir):
        """Test I18n initialization."""
        i18n = I18n(locales_dir=temp_locales_dir)
        assert i18n is not None
        assert i18n.current_lang == "en"
    
    def test_get_available_languages(self, temp_locales_dir):
        """Test getting available languages."""
        i18n = I18n(locales_dir=temp_locales_dir)
        languages = i18n.get_available_languages()
        
        assert len(languages) == 2
        assert any(lang["code"] == "en" for lang in languages)
        assert any(lang["code"] == "es" for lang in languages)
    
    def test_set_language(self, temp_locales_dir):
        """Test setting language."""
        i18n = I18n(locales_dir=temp_locales_dir)
        
        # Set to Spanish
        result = i18n.set_language("es")
        assert result is True
        assert i18n.current_lang == "es"
        
        # Try invalid language
        result = i18n.set_language("fr")
        assert result is False
        assert i18n.current_lang == "es"  # Should remain unchanged
    
    def test_translation(self, temp_locales_dir):
        """Test basic translation."""
        i18n = I18n(locales_dir=temp_locales_dir)
        
        # English translation
        assert i18n.t("hello") == "Hello"
        
        # Switch to Spanish
        i18n.set_language("es")
        assert i18n.t("hello") == "Hola"
    
    def test_translation_with_params(self, temp_locales_dir):
        """Test translation with parameters."""
        i18n = I18n(locales_dir=temp_locales_dir)
        
        result = i18n.t("greeting", name="John")
        assert result == "Hello, John!"
        
        result = i18n.t("items_count", count=5)
        assert result == "You have 5 items"
    
    def test_missing_key(self, temp_locales_dir):
        """Test missing translation key."""
        i18n = I18n(locales_dir=temp_locales_dir)
        
        result = i18n.t("nonexistent_key")
        assert result == "nonexistent_key"  # Should return key itself
    
    def test_missing_parameter(self, temp_locales_dir):
        """Test translation with missing parameter."""
        i18n = I18n(locales_dir=temp_locales_dir)
        
        # Missing 'name' parameter
        result = i18n.t("greeting")
        assert "{name}" in result  # Should keep placeholder
