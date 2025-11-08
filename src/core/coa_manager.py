"""
Coat of Arms (CoA) Manager
Manages CK3 coat of arms without DNA duplication functionality.
"""

import json
import os
import re
from typing import Dict, List, Optional
from PIL import Image


class CoAManager:
    """Manages coat of arms galleries and data."""
    
    def __init__(self, data_dir: str = "coa_data", base_dir: str = "databases"):
        """
        Initialize CoA manager.
        
        Args:
            data_dir: Directory for CoA data storage (relative to base_dir)
            base_dir: Base directory for all databases
        """
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "default", data_dir)
        self.images_dir = os.path.join(base_dir, "default", "coa_images")
        self._ensure_directories()
        self.current_gallery = "default_coa"
        self._ensure_default_gallery()
    
    def _ensure_directories(self):
        """Ensure data directories exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
    
    def _ensure_default_gallery(self):
        """Ensure default gallery exists."""
        gallery_file = os.path.join(self.data_dir, f"{self.current_gallery}.json")
        if not os.path.exists(gallery_file):
            self.create_gallery("default_coa", "Default CoA Gallery")
    
    def get_gallery_file(self, gallery_name: str) -> str:
        """Get path to gallery file."""
        return os.path.join(self.data_dir, f"{gallery_name}.json")
    
    def get_image_file(self, coa_id: str) -> str:
        """Get path to CoA image file."""
        return os.path.join(self.images_dir, f"{coa_id}.png")
    
    def create_gallery(self, name: str, description: str = "") -> bool:
        """
        Create a new CoA gallery.
        
        Args:
            name: Gallery name
            description: Gallery description
            
        Returns:
            True if created successfully
        """
        gallery_file = self.get_gallery_file(name)
        if os.path.exists(gallery_file):
            return False
        
        gallery_data = {
            "name": name,
            "description": description,
            "coats_of_arms": []
        }
        
        with open(gallery_file, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_gallery_names(self) -> List[str]:
        """
        Get list of all gallery names.
        
        Returns:
            List of gallery names
        """
        if not os.path.exists(self.data_dir):
            return []
        
        galleries = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.json'):
                galleries.append(file[:-5])
        
        return sorted(galleries)
    
    def load_gallery(self, name: str) -> Optional[Dict]:
        """
        Load a gallery.
        
        Args:
            name: Gallery name
            
        Returns:
            Gallery data dictionary or None if not found
        """
        gallery_file = self.get_gallery_file(name)
        if not os.path.exists(gallery_file):
            return None
        
        with open(gallery_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_gallery(self, name: str, gallery_data: Dict) -> bool:
        """
        Save gallery data.
        
        Args:
            name: Gallery name
            gallery_data: Gallery data dictionary
            
        Returns:
            True if saved successfully
        """
        gallery_file = self.get_gallery_file(name)
        
        with open(gallery_file, 'w', encoding='utf-8') as f:
            json.dump(gallery_data, f, indent=2, ensure_ascii=False)
        
        return True
    
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
        gallery = self.load_gallery(gallery_name)
        if gallery is None:
            return False
        
        # Check if CoA already exists
        for coa in gallery["coats_of_arms"]:
            if coa["id"] == coa_id:
                return False
        
        coa_data = {
            "id": coa_id,
            "code": coa_code,
            "tags": tags or [],
            "has_image": False
        }
        
        # Copy image if provided
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                image.save(self.get_image_file(coa_id))
                coa_data["has_image"] = True
            except Exception:
                pass
        
        gallery["coats_of_arms"].append(coa_data)
        return self.save_gallery(gallery_name, gallery)
    
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
        gallery = self.load_gallery(gallery_name)
        if gallery is None:
            return False
        
        original_count = len(gallery["coats_of_arms"])
        gallery["coats_of_arms"] = [
            coa for coa in gallery["coats_of_arms"] if coa["id"] != coa_id
        ]
        
        if len(gallery["coats_of_arms"]) < original_count:
            # Delete image file
            image_file = self.get_image_file(coa_id)
            if os.path.exists(image_file):
                os.remove(image_file)
            
            return self.save_gallery(gallery_name, gallery)
        
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
            with open(import_path, 'r', encoding='utf-8') as f:
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
