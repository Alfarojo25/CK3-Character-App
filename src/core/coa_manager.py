"""
Coat of Arms (CoA) Manager
Manages CK3 coat of arms without DNA duplication functionality.
"""

import json
import logging
import os
import re
import time
import uuid
from typing import Dict, List, Optional, Any
from PIL import Image

logger = logging.getLogger(__name__)


class CoAManager:
    """Manages coat of arms galleries and data."""
    
    def __init__(self, data_dir: str = "coa_data", base_dir: str = "databases", db_name: str = "Default"):
        """
        Initialize CoA manager.
        
        Args:
            data_dir: Directory for CoA data storage (relative to database folder)
            base_dir: Base directory for all databases
            db_name: Database name
        """
        self.base_dir = base_dir
        self.db_name = db_name
        self.db_folder = os.path.join(base_dir, f"Database_{db_name}")
        self.data_dir = os.path.join(self.db_folder, data_dir)
        self.data_file = os.path.join(self.data_dir, "coats_of_arms.json")
        self.images_dir = os.path.join(self.data_dir, "images")
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Load or initialize galleries
        self.galleries = self._load_galleries()
        self.current_gallery = "Default"
    
    def _load_galleries(self) -> List[Dict[str, Any]]:
        """Load galleries from JSON file or create default."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8-sig') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return [{"name": "Default", "coats_of_arms": []}]
        else:
            return [{"name": "Default", "coats_of_arms": []}]
    
    def save_galleries(self) -> None:
        """Save galleries to JSON file."""
        try:
            logger.info(f"Saving CoA galleries to {self.data_file}")
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.galleries, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved {len(self.galleries)} CoA galleries")
        except Exception as e:
            logger.error(f"Error saving CoA galleries to {self.data_file}: {str(e)}", exc_info=True)
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
    
    def create_gallery(self, name: str, description: str = "") -> bool:
        """
        Create a new CoA gallery.
        
        Args:
            name: Gallery name
            description: Gallery description
            
        Returns:
            True if created successfully
        """
        try:
            logger.info(f"Creating CoA gallery: {name}")
            if any(g["name"] == name for g in self.galleries):
                logger.warning(f"CoA gallery '{name}' already exists")
                return False
            
            self.galleries.append({
                "name": name,
                "description": description,
                "coats_of_arms": [],
                "created": time.time(),
                "modified": time.time()
            })
            self.save_galleries()
            logger.info(f"Successfully created CoA gallery: {name}")
            return True
        except Exception as e:
            logger.error(f"Error creating CoA gallery '{name}': {str(e)}", exc_info=True)
            return False
    
    def load_gallery(self, name: str) -> Optional[Dict]:
        """Load a gallery by name."""
        return self.get_gallery(name)
    
    def save_gallery(self, name: str, gallery_data: Dict) -> bool:
        """Save gallery data (compatibility method)."""
        self.save_galleries()
        return True
    
    def get_image_file(self, coa_id: str) -> str:
        """Get path to CoA image file."""
        return os.path.join(self.images_dir, f"{coa_id}.png")
    
    def add_coa(self, gallery_name: str, coa_id: str, coa_code: str, 
                tags: List[str] = None, image_path: str = None) -> bool:
        """
        Add a coat of arms to a gallery.
        
        Args:
            gallery_name: Gallery name
            coa_id: Unique identifier for the CoA
            coa_code: CK3 coat of arms code
            tags: Optional tags for categorization
            image_path: Optional path to CoA image
            
        Returns:
            True if added successfully
        """
        try:
            logger.info(f"Adding CoA '{coa_id}' to gallery '{gallery_name}'")
            gallery = self.get_gallery(gallery_name)
            if not gallery:
                logger.warning(f"CoA gallery '{gallery_name}' not found")
                return False
            
            # Check if CoA already exists
            for coa in gallery["coats_of_arms"]:
                if coa["id"] == coa_id:
                    logger.warning(f"CoA '{coa_id}' already exists in '{gallery_name}'")
                    return False
            
            coa_data = {
                "id": coa_id,
                "code": coa_code,
                "tags": tags or [],
                "has_image": False,
                "created": time.time(),
                "modified": time.time()
            }
            
            # Copy image if provided
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    dest_path = self.get_image_file(coa_id)
                    image.save(dest_path)
                    coa_data["has_image"] = True
                    logger.info(f"Saved CoA image to {dest_path}")
                except Exception as e:
                    logger.warning(f"Failed to save CoA image for '{coa_id}': {str(e)}")
            
            gallery["coats_of_arms"].append(coa_data)
            gallery["modified"] = time.time()
            self.save_galleries()
            logger.info(f"Successfully added CoA '{coa_id}' to gallery '{gallery_name}'")
            return True
        except Exception as e:
            logger.error(f"Error adding CoA '{coa_id}' to gallery '{gallery_name}': {str(e)}", exc_info=True)
            return False
    
    def update_coa(self, gallery_name: str, coa_id: str, coa_code: str = None,
                   tags: List[str] = None, image_path: str = None) -> bool:
        """
        Update a coat of arms.
        
        Args:
            gallery_name: Gallery name
            coa_id: CoA identifier
            coa_code: Updated CK3 code (optional)
            tags: Updated tags (optional)
            image_path: Updated image path (optional)
            
        Returns:
            True if updated successfully
        """
        gallery = self.load_gallery(gallery_name)
        if gallery is None:
            return False
        
        for coa in gallery["coats_of_arms"]:
            if coa["id"] == coa_id:
                if coa_code is not None:
                    coa["code"] = coa_code
                if tags is not None:
                    coa["tags"] = tags
                if image_path and os.path.exists(image_path):
                    try:
                        image = Image.open(image_path)
                        image.save(self.get_image_file(coa_id))
                        coa["has_image"] = True
                    except Exception:
                        pass
                
                return self.save_gallery(gallery_name, gallery)
        
        return False
    
    def delete_coa(self, gallery_name: str, coa_id: str) -> bool:
        """
        Delete a coat of arms.
        
        Args:
            gallery_name: Gallery name
            coa_id: CoA identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"Deleting CoA '{coa_id}' from gallery '{gallery_name}'")
            gallery = self.load_gallery(gallery_name)
            if gallery is None:
                logger.warning(f"CoA gallery '{gallery_name}' not found")
                return False
            
            original_count = len(gallery["coats_of_arms"])
            gallery["coats_of_arms"] = [
                coa for coa in gallery["coats_of_arms"] if coa["id"] != coa_id
            ]
            
            if len(gallery["coats_of_arms"]) < original_count:
                # Delete image file
                image_file = self.get_image_file(coa_id)
                if os.path.exists(image_file):
                    try:
                        os.remove(image_file)
                        logger.info(f"Deleted CoA image: {image_file}")
                    except OSError as e:
                        logger.warning(f"Failed to delete CoA image {image_file}: {str(e)}")
                
                result = self.save_gallery(gallery_name, gallery)
                if result:
                    logger.info(f"Successfully deleted CoA '{coa_id}' from gallery '{gallery_name}'")
                return result
            
            logger.warning(f"CoA '{coa_id}' not found in gallery '{gallery_name}'")
            return False
        except Exception as e:
            logger.error(f"Error deleting CoA '{coa_id}' from gallery '{gallery_name}': {str(e)}", exc_info=True)
            return False
        return False
    
    def get_coa(self, gallery_name: str, coa_id: str) -> Optional[Dict]:
        """
        Get a specific coat of arms.
        
        Args:
            gallery_name: Gallery name
            coa_id: CoA identifier
            
        Returns:
            CoA data dictionary or None if not found
        """
        gallery = self.load_gallery(gallery_name)
        if gallery is None:
            return None
        
        for coa in gallery["coats_of_arms"]:
            if coa["id"] == coa_id:
                return coa
        
        return None
    
    def parse_coa_name(self, coa_code: str) -> str:
        """
        Parse CoA name from code.
        
        Args:
            coa_code: CK3 CoA code
            
        Returns:
            Parsed name or "Unnamed CoA"
        """
        # Try to extract name from coa_rd_* pattern
        match = re.search(r'coa_rd_(\w+)_(\d+)', coa_code)
        if match:
            type_name = match.group(1)
            number = match.group(2)
            return f"{type_name.replace('_', ' ').title()} #{number}"
        
        return "Unnamed CoA"
    
    def get_all_tags(self, gallery_name: str) -> List[str]:
        """
        Get all unique tags from a gallery.
        
        Args:
            gallery_name: Gallery name
            
        Returns:
            List of unique tags
        """
        gallery = self.load_gallery(gallery_name)
        if gallery is None:
            return []
        
        tags = set()
        for coa in gallery["coats_of_arms"]:
            tags.update(coa.get("tags", []))
        
        return sorted(list(tags))
    
    def rename_gallery(self, old_name: str, new_name: str) -> bool:
        """
        Rename a gallery.
        
        Args:
            old_name: Current gallery name
            new_name: New gallery name
            
        Returns:
            True if renamed successfully
        """
        old_file = self.get_gallery_file(old_name)
        new_file = self.get_gallery_file(new_name)
        
        if not os.path.exists(old_file) or os.path.exists(new_file):
            return False
        
        # Load, update, and save with new name
        gallery = self.load_gallery(old_name)
        if gallery is None:
            return False
        
        gallery["name"] = new_name
        self.save_gallery(new_name, gallery)
        
        # Remove old file
        os.remove(old_file)
        
        return True
    
    def delete_gallery(self, name: str) -> bool:
        """
        Delete a gallery and all its CoA images.
        
        Args:
            name: Gallery name
            
        Returns:
            True if deleted successfully
        """
        gallery = self.load_gallery(name)
        if gallery is None:
            return False
        
        # Delete all CoA images
        for coa in gallery["coats_of_arms"]:
            image_file = self.get_image_file(coa["id"])
            if os.path.exists(image_file):
                os.remove(image_file)
        
        # Delete gallery file
        gallery_file = self.get_gallery_file(name)
        if os.path.exists(gallery_file):
            os.remove(gallery_file)
        
        return True
    
    def export_gallery(self, name: str, export_path: str) -> bool:
        """
        Export gallery to a file.
        
        Args:
            name: Gallery name
            export_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        gallery = self.load_gallery(name)
        if gallery is None:
            return False
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(gallery, f, indent=2, ensure_ascii=False)
        
        return True
    
    def import_gallery(self, import_path: str) -> Optional[str]:
        """
        Import gallery from a file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            Gallery name if imported successfully, None otherwise
        """
        try:
            with open(import_path, 'r', encoding='utf-8-sig') as f:
                gallery = json.load(f)
            
            name = gallery.get("name", "imported_coa")
            
            # Ensure unique name
            counter = 1
            original_name = name
            while os.path.exists(self.get_gallery_file(name)):
                name = f"{original_name}_{counter}"
                counter += 1
            
            gallery["name"] = name
            self.save_gallery(name, gallery)
            
            return name
        except Exception:
            return None
