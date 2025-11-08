#!/usr/bin/env python3
"""
Tests for GalleryManager.
"""

import pytest
import json
import os
import tempfile
import shutil
from src.core.gallery_manager import GalleryManager


class TestGalleryManager:
    """Test cases for GalleryManager class."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def gallery_manager(self, temp_data_dir):
        """Create GalleryManager instance with temp directory."""
        manager = GalleryManager(data_dir="test_data", base_dir=temp_data_dir)
        return manager
    
    def test_initialization(self, gallery_manager):
        """Test GalleryManager initialization."""
        assert gallery_manager is not None
        assert len(gallery_manager.galleries) > 0
        assert gallery_manager.galleries[0]["name"] == "Default"
    
    def test_get_gallery_names(self, gallery_manager):
        """Test getting gallery names."""
        names = gallery_manager.get_gallery_names()
        
        assert "Default" in names
        assert isinstance(names, list)
    
    def test_create_gallery(self, gallery_manager):
        """Test creating new gallery."""
        result = gallery_manager.create_gallery("Test Gallery")
        
        assert result is True
        assert "Test Gallery" in gallery_manager.get_gallery_names()
    
    def test_create_duplicate_gallery(self, gallery_manager):
        """Test creating gallery with duplicate name."""
        gallery_manager.create_gallery("Test Gallery")
        result = gallery_manager.create_gallery("Test Gallery")
        
        assert result is False
    
    def test_get_gallery(self, gallery_manager):
        """Test getting gallery by name."""
        gallery_manager.create_gallery("Test Gallery")
        gallery = gallery_manager.get_gallery("Test Gallery")
        
        assert gallery is not None
        assert gallery["name"] == "Test Gallery"
        assert "characters" in gallery
    
    def test_get_nonexistent_gallery(self, gallery_manager):
        """Test getting nonexistent gallery."""
        gallery = gallery_manager.get_gallery("Nonexistent")
        
        assert gallery is None
    
    def test_rename_gallery(self, gallery_manager):
        """Test renaming gallery."""
        gallery_manager.create_gallery("Old Name")
        result = gallery_manager.rename_gallery("Old Name", "New Name")
        
        assert result is True
        assert "New Name" in gallery_manager.get_gallery_names()
        assert "Old Name" not in gallery_manager.get_gallery_names()
    
    def test_rename_gallery_duplicate_name(self, gallery_manager):
        """Test renaming gallery to existing name."""
        gallery_manager.create_gallery("Gallery 1")
        gallery_manager.create_gallery("Gallery 2")
        result = gallery_manager.rename_gallery("Gallery 1", "Gallery 2")
        
        assert result is False
    
    def test_delete_gallery(self, gallery_manager):
        """Test deleting gallery."""
        gallery_manager.create_gallery("Test Gallery")
        result = gallery_manager.delete_gallery("Test Gallery")
        
        assert result is True
        assert "Test Gallery" not in gallery_manager.get_gallery_names()
    
    def test_cannot_delete_last_gallery(self, gallery_manager):
        """Test that last gallery cannot be deleted."""
        # Only Default gallery exists
        result = gallery_manager.delete_gallery("Default")
        
        assert result is False
        assert "Default" in gallery_manager.get_gallery_names()
    
    def test_add_character(self, gallery_manager):
        """Test adding character to gallery."""
        char_id = gallery_manager.add_character(
            gallery_name="Default",
            name="Test Character",
            dna="abc123xyz789",
            tags=["warrior", "brave"]
        )
        
        assert char_id is not None
        
        # Verify character was added
        gallery = gallery_manager.get_gallery("Default")
        assert len(gallery["characters"]) == 1
        assert gallery["characters"][0]["name"] == "Test Character"
    
    def test_add_character_to_nonexistent_gallery(self, gallery_manager):
        """Test adding character to nonexistent gallery."""
        char_id = gallery_manager.add_character(
            gallery_name="Nonexistent",
            name="Test Character"
        )
        
        assert char_id is None
    
    def test_update_character(self, gallery_manager):
        """Test updating character information."""
        # Add character
        char_id = gallery_manager.add_character(
            gallery_name="Default",
            name="Original Name",
            dna="abc123"
        )
        
        # Update character
        result = gallery_manager.update_character(
            gallery_name="Default",
            char_id=char_id,
            name="Updated Name",
            dna="xyz789"
        )
        
        assert result is True
        
        # Verify update
        gallery = gallery_manager.get_gallery("Default")
        char = gallery["characters"][0]
        assert char["name"] == "Updated Name"
        assert char["dna"] == "xyz789"
    
    def test_update_character_tags(self, gallery_manager):
        """Test updating character tags."""
        # Add character
        char_id = gallery_manager.add_character(
            gallery_name="Default",
            name="Test Character",
            tags=["old_tag"]
        )
        
        # Update tags
        result = gallery_manager.update_character(
            gallery_name="Default",
            char_id=char_id,
            tags=["new_tag_1", "new_tag_2"]
        )
        
        assert result is True
        
        # Verify tags
        gallery = gallery_manager.get_gallery("Default")
        char = gallery["characters"][0]
        assert "new_tag_1" in char["tags"]
        assert "new_tag_2" in char["tags"]
        assert "old_tag" not in char["tags"]
    
    def test_update_nonexistent_character(self, gallery_manager):
        """Test updating nonexistent character."""
        result = gallery_manager.update_character(
            gallery_name="Default",
            char_id="nonexistent-id",
            name="New Name"
        )
        
        assert result is False
    
    def test_delete_character(self, gallery_manager):
        """Test deleting character."""
        # Add character
        char_id = gallery_manager.add_character(
            gallery_name="Default",
            name="Test Character"
        )
        
        # Delete character
        result = gallery_manager.delete_character(
            gallery_name="Default",
            char_id=char_id
        )
        
        assert result is True
        
        # Verify deletion
        gallery = gallery_manager.get_gallery("Default")
        assert len(gallery["characters"]) == 0
    
    def test_delete_nonexistent_character(self, gallery_manager):
        """Test deleting nonexistent character."""
        result = gallery_manager.delete_character(
            gallery_name="Default",
            char_id="nonexistent-id"
        )
        
        assert result is False
    
    def test_save_and_load_galleries(self, temp_data_dir):
        """Test saving and loading galleries."""
        # Create manager and add data
        manager1 = GalleryManager(data_dir="test_data", base_dir=temp_data_dir)
        manager1.create_gallery("Test Gallery")
        manager1.add_character("Test Gallery", "Test Character", "abc123", ["tag1"])
        manager1.save_galleries()
        
        # Create new manager instance to load saved data
        manager2 = GalleryManager(data_dir="test_data", base_dir=temp_data_dir)
        
        assert "Test Gallery" in manager2.get_gallery_names()
        gallery = manager2.get_gallery("Test Gallery")
        assert len(gallery["characters"]) == 1
        assert gallery["characters"][0]["name"] == "Test Character"
    
    def test_character_has_timestamps(self, gallery_manager):
        """Test that characters have created and modified timestamps."""
        char_id = gallery_manager.add_character(
            gallery_name="Default",
            name="Test Character"
        )
        
        gallery = gallery_manager.get_gallery("Default")
        char = gallery["characters"][0]
        
        assert "created" in char
        assert "modified" in char
        assert char["created"] > 0
        assert char["modified"] > 0
