"""
Gallery Manager Module
Handles character galleries, data persistence, and character management.
"""

import json
import os
import shutil
import uuid
import time
import re
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class GalleryManager:
    """Manages character galleries and their persistence."""
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a character name to be used as a filename."""
        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        # Limit length to 100 characters
        sanitized = sanitized[:100]
        # If empty after sanitization, use 'character'
        return sanitized if sanitized else 'character'
    
    def __init__(self, data_dir: str = "character_data", base_dir: str = "databases", db_name: str = "Default"):
        """
        Initialize the gallery manager.
        
        Args:
            data_dir: Directory to store gallery data and images (relative to database folder)
            base_dir: Base directory for all databases
            db_name: Database name
        """
        self.base_dir = base_dir
        self.db_name = db_name
        self.db_folder = os.path.join(base_dir, f"Database_{db_name}")
        self.data_dir = os.path.join(self.db_folder, data_dir)
        self.data_file = os.path.join(self.data_dir, "characters.json")
        self.images_dir = os.path.join(self.data_dir, "images")
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Load or initialize galleries
        self.galleries = self._load_galleries()
    
    def _load_galleries(self) -> List[Dict[str, Any]]:
        """Load galleries from JSON file or create default."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return [{"name": "Default", "characters": []}]
        else:
            return [{"name": "Default", "characters": []}]
    
    def save_galleries(self) -> None:
        """Save galleries to JSON file."""
        try:
            logger.info(f"Saving galleries to {self.data_file}")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.galleries, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved {len(self.galleries)} galleries")
        except Exception as e:
            logger.error(f"Error saving galleries to {self.data_file}: {str(e)}", exc_info=True)
            raise
    
    def reload_from_disk(self) -> None:
        """Reload galleries data from disk."""
        self.galleries = self._load_galleries()
    
    def get_gallery_names(self) -> List[str]:
        """Get list of all gallery names."""
        return [g["name"] for g in self.galleries]
    
    def get_gallery(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a gallery by name."""
        for gallery in self.galleries:
            if gallery["name"] == name:
                return gallery
        return None
    
    def create_gallery(self, name: str) -> bool:
        """
        Create a new gallery.
        
        Args:
            name: Name for the new gallery
            
        Returns:
            True if created successfully, False if name already exists
        """
        try:
            logger.info(f"Creating gallery: {name}")
            if any(g["name"] == name for g in self.galleries):
                logger.warning(f"Gallery '{name}' already exists")
                return False
            
            self.galleries.append({
                "name": name,
                "characters": [],
                "created": time.time(),
                "modified": time.time()
            })
            self.save_galleries()
            logger.info(f"Successfully created gallery: {name}")
            return True
        except Exception as e:
            logger.error(f"Error creating gallery '{name}': {str(e)}", exc_info=True)
            return False
    
    def rename_gallery(self, old_name: str, new_name: str) -> bool:
        """Rename a gallery."""
        if any(g["name"] == new_name for g in self.galleries):
            return False
        
        gallery = self.get_gallery(old_name)
        if gallery:
            gallery["name"] = new_name
            gallery["modified"] = time.time()
            self.save_galleries()
            return True
        return False
    
    def delete_gallery(self, name: str) -> bool:
        """Delete a gallery and all its character images."""
        if len(self.galleries) <= 1:
            return False  # Don't delete the last gallery
        
        gallery = self.get_gallery(name)
        if not gallery:
            return False
        
        # Remove all character images
        for char in gallery["characters"]:
            img_path = char.get("image")
            if img_path and os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except OSError:
                    pass
        
        self.galleries.remove(gallery)
        self.save_galleries()
        return True
    
    def add_character(self, gallery_name: str, name: str, dna: str = "", 
                     tags: List[str] = None, image_path: Optional[str] = None) -> Optional[str]:
        """
        Add a new character to a gallery.
        
        Args:
            gallery_name: Name of the gallery
            name: Character name
            dna: Character DNA string
            tags: List of tags
            image_path: Path to character portrait image
            
        Returns:
            Character ID if successful, None otherwise
        """
        try:
            logger.info(f"Adding character '{name}' to gallery '{gallery_name}'")
            gallery = self.get_gallery(gallery_name)
            if not gallery:
                logger.warning(f"Gallery '{gallery_name}' not found")
                return None
            
            char_id = str(uuid.uuid4())
            character = {
                'id': char_id,
                'name': name,
                'dna': dna,
                'tags': tags or [],
                'image': None,
                'created': time.time(),
                'modified': time.time()
            }
            
            # Copy image if provided
            if image_path and os.path.exists(image_path):
                # Use character name for filename, with UUID as fallback
                safe_name = self._sanitize_filename(name) or char_id
                base_name = safe_name
                counter = 1
                dest_path = os.path.join(self.images_dir, f"{base_name}.png")
                
                # If file exists, append counter
                while os.path.exists(dest_path) and dest_path != image_path:
                    dest_path = os.path.join(self.images_dir, f"{base_name}_{counter}.png")
                    counter += 1
                
                try:
                    shutil.copy2(image_path, dest_path)
                    character['image'] = dest_path
                    logger.info(f"Copied character image to {dest_path}")
                except IOError as e:
                    logger.warning(f"Failed to copy image for '{name}': {str(e)}")
            
            gallery["characters"].append(character)
            gallery["modified"] = time.time()
            self.save_galleries()
            logger.info(f"Successfully added character '{name}' with ID {char_id}")
            return char_id
        except Exception as e:
            logger.error(f"Error adding character '{name}' to gallery '{gallery_name}': {str(e)}", exc_info=True)
            return None
    
    def update_character(self, gallery_name: str, char_id: str, 
                        name: Optional[str] = None, dna: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> bool:
        """Update a character's information."""
        gallery = self.get_gallery(gallery_name)
        if not gallery:
            return False
        
        for char in gallery["characters"]:
            if char["id"] == char_id:
                # If name is changing and character has an image, rename the image file
                if name is not None and name != char.get("name") and char.get("image"):
                    old_image = char["image"]
                    if os.path.exists(old_image):
                        safe_name = self._sanitize_filename(name) or char_id
                        base_name = safe_name
                        counter = 1
                        new_image = os.path.join(self.images_dir, f"{base_name}.png")
                        
                        # Find available filename
                        while os.path.exists(new_image) and new_image != old_image:
                            new_image = os.path.join(self.images_dir, f"{base_name}_{counter}.png")
                            counter += 1
                        
                        # Rename the image file
                        if new_image != old_image:
                            try:
                                os.rename(old_image, new_image)
                                char["image"] = new_image
                            except OSError:
                                pass  # Keep old image path if rename fails
                
                if name is not None:
                    char["name"] = name
                if dna is not None:
                    char["dna"] = dna
                if tags is not None:
                    char["tags"] = tags
                char["modified"] = time.time()
                gallery["modified"] = time.time()
                self.save_galleries()
                return True
        return False
    
    def delete_character(self, gallery_name: str, char_id: str) -> bool:
        """Delete a character and its image."""
        try:
            logger.info(f"Deleting character {char_id} from gallery '{gallery_name}'")
            gallery = self.get_gallery(gallery_name)
            if not gallery:
                logger.warning(f"Gallery '{gallery_name}' not found")
                return False
            
            for i, char in enumerate(gallery["characters"]):
                if char["id"] == char_id:
                    char_name = char.get('name', 'Unknown')
                    # Remove image
                    img_path = char.get("image")
                    if img_path and os.path.exists(img_path):
                        try:
                            os.remove(img_path)
                            logger.info(f"Deleted image: {img_path}")
                        except OSError as e:
                            logger.warning(f"Failed to delete image {img_path}: {str(e)}")
                    
                    gallery["characters"].pop(i)
                    gallery["modified"] = time.time()
                    self.save_galleries()
                    logger.info(f"Successfully deleted character '{char_name}' ({char_id})")
                    return True
            
            logger.warning(f"Character {char_id} not found in gallery '{gallery_name}'")
            return False
        except Exception as e:
            logger.error(f"Error deleting character {char_id} from '{gallery_name}': {str(e)}", exc_info=True)
            return False
    
    def set_character_image(self, gallery_name: str, char_id: str, image_path: str) -> bool:
        """Set or update a character's portrait image."""
        gallery = self.get_gallery(gallery_name)
        if not gallery:
            return False
        
        for char in gallery["characters"]:
            if char["id"] == char_id:
                # Use character name for filename
                safe_name = self._sanitize_filename(char.get('name', '')) or char_id
                base_name = safe_name
                counter = 1
                dest_path = os.path.join(self.images_dir, f"{base_name}.png")
                
                # If file exists and is not the current character's image, append counter
                while os.path.exists(dest_path) and dest_path != char.get('image') and dest_path != image_path:
                    dest_path = os.path.join(self.images_dir, f"{base_name}_{counter}.png")
                    counter += 1
                
                try:
                    # Remove old image if it exists and is different
                    old_image = char.get('image')
                    if old_image and os.path.exists(old_image) and old_image != dest_path:
                        try:
                            os.remove(old_image)
                        except OSError:
                            pass
                    
                    shutil.copy2(image_path, dest_path)
                    char["image"] = dest_path
                    char["modified"] = time.time()
                    gallery["modified"] = time.time()
                    self.save_galleries()
                    return True
                except IOError:
                    return False
        return False
    
    def export_gallery(self, gallery_name: str, export_dir: str) -> bool:
        """Export a gallery to a directory."""
        gallery = self.get_gallery(gallery_name)
        if not gallery:
            return False
        
        out_dir = os.path.join(export_dir, gallery_name)
        os.makedirs(out_dir, exist_ok=True)
        
        # Save characters JSON
        with open(os.path.join(out_dir, "characters.json"), "w", encoding="utf-8") as f:
            json.dump(gallery["characters"], f, indent=2, ensure_ascii=False)
        
        # Copy images
        images_out = os.path.join(out_dir, "images")
        os.makedirs(images_out, exist_ok=True)
        for char in gallery["characters"]:
            img_path = char.get("image")
            if img_path and os.path.exists(img_path):
                shutil.copy2(img_path, os.path.join(images_out, os.path.basename(img_path)))
        
        return True
    
    def import_gallery(self, import_dir: str, gallery_name: str) -> bool:
        """Import a gallery from a directory."""
        json_file = os.path.join(import_dir, "characters.json")
        images_folder = os.path.join(import_dir, "images")
        
        if not os.path.exists(json_file):
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                chars = json.load(f)
        except (json.JSONDecodeError, IOError):
            return False
        
        new_gallery = {
            "name": gallery_name,
            "characters": [],
            "created": time.time(),
            "modified": time.time()
        }
        
        for char in chars:
            char_id = char.get("id", str(uuid.uuid4()))
            char['id'] = char_id
            
            src_img = os.path.join(images_folder, f"{char_id}.png")
            if os.path.exists(src_img):
                dest_img = os.path.join(self.images_dir, f"{char_id}.png")
                try:
                    shutil.copy2(src_img, dest_img)
                    char['image'] = dest_img
                except IOError:
                    char['image'] = None
            else:
                char['image'] = None
            
            new_gallery["characters"].append(char)
        
        self.galleries.append(new_gallery)
        self.save_galleries()
        return True
