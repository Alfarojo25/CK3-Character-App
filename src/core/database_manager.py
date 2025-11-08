"""
Database Manager
Handles multiple databases for characters and CoAs (Coat of Arms).
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Manages multiple databases (characters and CoAs)."""
    
    def __init__(self, base_dir: str = "databases"):
        """
        Initialize database manager.
        
        Args:
            base_dir: Base directory for all databases
        """
        self.base_dir = base_dir
        self.config_file = os.path.join(base_dir, "db_config.json")
        self._ensure_directories()
        self._load_config()
    
    def _ensure_directories(self):
        """Ensure database directories exist."""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "backups"), exist_ok=True)
    
    def _load_config(self):
        """Load database configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "current_character_db": "default",
                "current_coa_db": "default",
                "databases": {
                    "default": {
                        "name": "default",
                        "type": "both",  # both, character, coa
                        "created": datetime.now().isoformat(),
                        "description": "Default database"
                    }
                }
            }
            self._save_config()
    
    def _save_config(self):
        """Save database configuration."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_database_list(self) -> List[Dict[str, str]]:
        """
        Get list of all databases.
        
        Returns:
            List of database info dictionaries
        """
        return [
            {
                "name": name,
                "type": info["type"],
                "created": info.get("created", ""),
                "description": info.get("description", "")
            }
            for name, info in self.config["databases"].items()
        ]
    
    def create_database(self, name: str, db_type: str = "both", description: str = "") -> bool:
        """
        Create a new database.
        
        Args:
            name: Database name
            db_type: Type of database (both, character, coa)
            description: Optional description
            
        Returns:
            True if created successfully
        """
        if name in self.config["databases"]:
            return False
        
        self.config["databases"][name] = {
            "name": name,
            "type": db_type,
            "created": datetime.now().isoformat(),
            "description": description
        }
        self._save_config()
        
        # Create database directory structure
        db_path = os.path.join(self.base_dir, name)
        os.makedirs(db_path, exist_ok=True)
        
        if db_type in ["both", "character"]:
            os.makedirs(os.path.join(db_path, "character_data"), exist_ok=True)
            os.makedirs(os.path.join(db_path, "portraits"), exist_ok=True)
        
        if db_type in ["both", "coa"]:
            os.makedirs(os.path.join(db_path, "coa_data"), exist_ok=True)
            os.makedirs(os.path.join(db_path, "coa_images"), exist_ok=True)
        
        return True
    
    def delete_database(self, name: str) -> bool:
        """
        Delete a database.
        
        Args:
            name: Database name
            
        Returns:
            True if deleted successfully
        """
        if name not in self.config["databases"] or name == "default":
            return False
        
        # Remove from config
        del self.config["databases"][name]
        self._save_config()
        
        # Remove directory
        db_path = os.path.join(self.base_dir, name)
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        
        # Update current database if needed
        if self.config["current_character_db"] == name:
            self.config["current_character_db"] = "default"
        if self.config["current_coa_db"] == name:
            self.config["current_coa_db"] = "default"
        self._save_config()
        
        return True
    
    def backup_database(self, name: str) -> Optional[str]:
        """
        Create a backup of a database.
        
        Args:
            name: Database name
            
        Returns:
            Path to backup file or None if failed
        """
        if name not in self.config["databases"]:
            return None
        
        db_path = os.path.join(self.base_dir, name)
        if not os.path.exists(db_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{name}_backup_{timestamp}.zip"
        backup_path = os.path.join(self.base_dir, "backups", backup_name)
        
        # Create zip archive
        shutil.make_archive(
            backup_path.replace('.zip', ''),
            'zip',
            db_path
        )
        
        return backup_path
    
    def get_current_database(self, db_type: str = "character") -> str:
        """
        Get current active database name.
        
        Args:
            db_type: Type of database (character or coa)
            
        Returns:
            Database name
        """
        if db_type == "character":
            return self.config["current_character_db"]
        else:
            return self.config["current_coa_db"]
    
    def set_current_database(self, name: str, db_type: str = "character") -> bool:
        """
        Set current active database.
        
        Args:
            name: Database name
            db_type: Type of database (character or coa)
            
        Returns:
            True if set successfully
        """
        if name not in self.config["databases"]:
            return False
        
        db_info = self.config["databases"][name]
        if db_type == "character" and db_info["type"] not in ["both", "character"]:
            return False
        if db_type == "coa" and db_info["type"] not in ["both", "coa"]:
            return False
        
        if db_type == "character":
            self.config["current_character_db"] = name
        else:
            self.config["current_coa_db"] = name
        
        self._save_config()
        return True
    
    def get_database_path(self, name: str, db_type: str = "character") -> str:
        """
        Get path to database directory.
        
        Args:
            name: Database name
            db_type: Type (character or coa)
            
        Returns:
            Path to database directory
        """
        base_path = os.path.join(self.base_dir, name)
        
        if db_type == "character":
            return os.path.join(base_path, "character_data")
        else:
            return os.path.join(base_path, "coa_data")
    
    def move_item(self, item_id: str, from_db: str, to_db: str, item_type: str = "character") -> bool:
        """
        Move an item from one database to another.
        
        Args:
            item_id: Item identifier (character name or coa id)
            from_db: Source database name
            to_db: Destination database name
            item_type: Type of item (character or coa)
            
        Returns:
            True if moved successfully
        """
        if from_db not in self.config["databases"] or to_db not in self.config["databases"]:
            return False
        
        from_path = self.get_database_path(from_db, item_type)
        to_path = self.get_database_path(to_db, item_type)
        
        # For characters, move data and portraits
        if item_type == "character":
            # Move character data file
            char_file = os.path.join(from_path, f"{item_id}.json")
            if os.path.exists(char_file):
                shutil.move(char_file, os.path.join(to_path, f"{item_id}.json"))
            
            # Move portrait
            from_portraits = os.path.join(self.base_dir, from_db, "portraits")
            to_portraits = os.path.join(self.base_dir, to_db, "portraits")
            portrait_file = os.path.join(from_portraits, f"{item_id}.png")
            if os.path.exists(portrait_file):
                shutil.move(portrait_file, os.path.join(to_portraits, f"{item_id}.png"))
        
        # For CoAs, move data and images
        else:
            coa_file = os.path.join(from_path, f"{item_id}.json")
            if os.path.exists(coa_file):
                shutil.move(coa_file, os.path.join(to_path, f"{item_id}.json"))
            
            from_images = os.path.join(self.base_dir, from_db, "coa_images")
            to_images = os.path.join(self.base_dir, to_db, "coa_images")
            image_file = os.path.join(from_images, f"{item_id}.png")
            if os.path.exists(image_file):
                shutil.move(image_file, os.path.join(to_images, f"{item_id}.png"))
        
        return True
    
    def get_database_stats(self, name: str) -> Dict[str, int]:
        """
        Get statistics for a database.
        
        Args:
            name: Database name
            
        Returns:
            Dictionary with character_count and coa_count
        """
        stats = {"character_count": 0, "coa_count": 0}
        
        if name not in self.config["databases"]:
            return stats
        
        db_path = os.path.join(self.base_dir, name)
        
        # Count characters
        char_path = os.path.join(db_path, "character_data")
        if os.path.exists(char_path):
            stats["character_count"] = len([f for f in os.listdir(char_path) if f.endswith('.json')])
        
        # Count CoAs
        coa_path = os.path.join(db_path, "coa_data")
        if os.path.exists(coa_path):
            stats["coa_count"] = len([f for f in os.listdir(coa_path) if f.endswith('.json')])
        
        return stats
