#!/usr/bin/env python3
"""
Tests for DNA utilities.
"""

import pytest
from src.core.dna_duplicator import duplicate_dna, validate_dna


class TestDuplicateDna:
    """Test cases for duplicate_dna function."""
    
    def test_duplicate_simple_dna(self):
        """Test duplicating simple DNA string."""
        dna = "abc123"
        duplicated = duplicate_dna(dna)
        
        assert duplicated == "abc123abc123"
    
    def test_duplicate_empty_dna(self):
        """Test duplicating empty DNA string."""
        dna = ""
        duplicated = duplicate_dna(dna)
        
        assert duplicated == ""
    
    def test_duplicate_dna_with_spaces(self):
        """Test that spaces are preserved."""
        dna = "abc 123"
        duplicated = duplicate_dna(dna)
        
        assert duplicated == "abc 123abc 123"
    
    def test_duplicate_special_characters(self):
        """Test duplicating DNA with special characters."""
        dna = "abc!@#$%"
        duplicated = duplicate_dna(dna)
        
        assert duplicated == "abc!@#$%abc!@#$%"


class TestValidateDna:
    """Test cases for validate_dna function."""
    
    def test_valid_dna_basic(self):
        """Test validation of basic DNA."""
        dna = "abc123xyz789"
        is_valid, message = validate_dna(dna)
        
        assert is_valid is True
        assert message == ""
    
    def test_valid_empty_dna(self):
        """Test that empty DNA is valid (no DNA is acceptable)."""
        dna = ""
        is_valid, message = validate_dna(dna)
        
        assert is_valid is True
    
    def test_valid_dna_alphanumeric(self):
        """Test DNA with alphanumeric characters."""
        dna = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        is_valid, message = validate_dna(dna)
        
        assert is_valid is True
    
    def test_valid_dna_with_allowed_chars(self):
        """Test DNA with allowed special characters."""
        # CK3 DNA typically uses alphanumeric and some special chars
        dna = "abc123_-"
        is_valid, message = validate_dna(dna)
        
        assert is_valid is True
    
    def test_invalid_dna_too_short(self):
        """Test DNA that is too short."""
        dna = "abc"
        is_valid, message = validate_dna(dna, min_length=10)
        
        assert is_valid is False
        assert "too short" in message.lower()
    
    def test_invalid_dna_too_long(self):
        """Test DNA that is too long."""
        dna = "a" * 1000
        is_valid, message = validate_dna(dna, max_length=500)
        
        assert is_valid is False
        assert "too long" in message.lower()
    
    def test_invalid_dna_forbidden_chars(self):
        """Test DNA with forbidden characters."""
        dna = "abc<>123"
        is_valid, message = validate_dna(dna)
        
        assert is_valid is False
        assert "invalid character" in message.lower() or "forbidden" in message.lower()
    
    def test_dna_validation_with_spaces(self):
        """Test DNA with spaces (might be invalid depending on implementation)."""
        dna = "abc 123"
        is_valid, message = validate_dna(dna)
        
        # This test depends on your validation rules
        # Adjust based on whether spaces are allowed
        assert isinstance(is_valid, bool)
    
    def test_dna_validation_length_bounds(self):
        """Test DNA at exact length boundaries."""
        # Minimum length
        dna_min = "a" * 10
        is_valid, _ = validate_dna(dna_min, min_length=10, max_length=100)
        assert is_valid is True
        
        # Maximum length
        dna_max = "a" * 100
        is_valid, _ = validate_dna(dna_max, min_length=10, max_length=100)
        assert is_valid is True
        
        # Just below minimum
        dna_below = "a" * 9
        is_valid, _ = validate_dna(dna_below, min_length=10, max_length=100)
        assert is_valid is False
        
        # Just above maximum
        dna_above = "a" * 101
        is_valid, _ = validate_dna(dna_above, min_length=10, max_length=100)
        assert is_valid is False
