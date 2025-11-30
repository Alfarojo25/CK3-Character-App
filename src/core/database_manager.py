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
    
    def scan_databases(self) -> List[str]:
        """Scan for all Database_* folders in base directory.
        
        Returns:
            List of database names (without Database_ prefix)
        """
        databases = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                if item.startswith("Database_"):
                    item_path = os.path.join(self.base_dir, item)
                    if os.path.isdir(item_path):
                        # Extract name without Database_ prefix
                        db_name = item[9:]  # len("Database_") = 9
                        
                        # Skip backup folders (format: YYYYMMDD_HHMMSS_CK3_Character_App_*)
                        # These start with a date pattern
                        if len(db_name) > 8 and db_name[8] == '_' and db_name[:8].isdigit():
                            continue
                        
                        databases.append(db_name)
        return sorted(databases)
    
    def _load_config(self):
        """Load database configuration and sync with existing folders."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8-sig') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "current_character_db": "Default",
                "current_coa_db": "Default",
                "databases": {}
            }
        
        # Scan for existing Database_* folders and add to config if not present
        existing_dbs = self.scan_databases()
        for db_name in existing_dbs:
            if db_name not in self.config["databases"]:
                # Auto-detect type based on folders
                db_path = os.path.join(self.base_dir, f"Database_{db_name}")
                has_character = os.path.exists(os.path.join(db_path, "character_data"))
                has_coa = os.path.exists(os.path.join(db_path, "coa_data"))
                
                if has_character and has_coa:
                    db_type = "both"
                elif has_character:
                    db_type = "character"
                elif has_coa:
                    db_type = "coa"
                else:
                    db_type = "both"
                
                self.config["databases"][db_name] = {
                    "name": db_name,
                    "type": db_type,
                    "created": datetime.now().isoformat(),
                    "description": f"Database {db_name}"
                }
        
        # Remove databases from config that don't have folders or are backups
        config_dbs = list(self.config["databases"].keys())
        for db_name in config_dbs:
            # Skip backup entries (format: YYYYMMDD_HHMMSS_CK3_Character_App_*)
            if len(db_name) > 8 and db_name[8] == '_' and db_name[:8].isdigit():
                del self.config["databases"][db_name]
                continue
            
            db_path = os.path.join(self.base_dir, f"Database_{db_name}")
            if not os.path.exists(db_path):
                del self.config["databases"][db_name]
        
        # Ensure Default exists
        if "Default" not in self.config["databases"]:
            self.config["databases"]["Default"] = {
                "name": "Default",
                "type": "both",
                "created": datetime.now().isoformat(),
                "description": "Default database"
            }
            # Create Default folder if it doesn't exist
            self.create_database("Default", "both", "Default database")
        
        # Ensure current databases are valid
        if self.config.get("current_character_db") not in self.config["databases"]:
            self.config["current_character_db"] = "Default"
        if self.config.get("current_coa_db") not in self.config["databases"]:
            self.config["current_coa_db"] = "Default"
        
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
        
        # Create database directory structure with Database_ prefix
        db_path = os.path.join(self.base_dir, f"Database_{name}")
        os.makedirs(db_path, exist_ok=True)
        
        if db_type in ["both", "character"]:
            os.makedirs(os.path.join(db_path, "character_data"), exist_ok=True)
            os.makedirs(os.path.join(db_path, "character_data", "images"), exist_ok=True)
        
        if db_type in ["both", "coa"]:
            os.makedirs(os.path.join(db_path, "coa_data"), exist_ok=True)
            os.makedirs(os.path.join(db_path, "coa_data", "images"), exist_ok=True)
        
        return True
    
    def delete_database(self, name: str) -> bool:
        """
        Delete a database.
        
        Args:
            name: Database name
            
        Returns:
            True if deleted successfully
        """
        if name not in self.config["databases"] or name == "Default":
            return False
        
        # Remove from config
        del self.config["databases"][name]
        self._save_config()
        
        # Remove directory (with Database_ prefix)
        db_path = os.path.join(self.base_dir, f"Database_{name}")
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        
        # Update current database if needed
        if self.config["current_character_db"] == name:
            self.config["current_character_db"] = "Default"
        if self.config["current_coa_db"] == name:
            self.config["current_coa_db"] = "Default"
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
        
        db_path = os.path.join(self.base_dir, f"Database_{name}")
        if not os.path.exists(db_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # New format: Database_YYYYMMDD_HHMMSS_CK3_Character_App_NombreDB.zip
        backup_name = f"Database_{timestamp}_CK3_Character_App_{name}.zip"
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
        base_path = os.path.join(self.base_dir, f"Database_{name}")
        
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
            from_images = os.path.join(self.base_dir, f"Database_{from_db}", "character_data", "images")
            to_images = os.path.join(self.base_dir, f"Database_{to_db}", "character_data", "images")
            portrait_file = os.path.join(from_images, f"{item_id}.png")
            if os.path.exists(portrait_file):
                shutil.move(portrait_file, os.path.join(to_images, f"{item_id}.png"))
        
        # For CoAs, move data and images
        else:
            coa_file = os.path.join(from_path, f"{item_id}.json")
            if os.path.exists(coa_file):
                shutil.move(coa_file, os.path.join(to_path, f"{item_id}.json"))
            
            from_images = os.path.join(self.base_dir, f"Database_{from_db}", "coa_data", "images")
            to_images = os.path.join(self.base_dir, f"Database_{to_db}", "coa_data", "images")
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
        
        db_path = os.path.join(self.base_dir, f"Database_{name}")
        
        # Count characters from characters.json
        char_file = os.path.join(db_path, "character_data", "characters.json")
        if os.path.exists(char_file):
            try:
                with open(char_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    # Count total characters across all galleries
                    if isinstance(data, list):
                        for gallery in data:
                            if isinstance(gallery, dict) and "characters" in gallery:
                                stats["character_count"] += len(gallery["characters"])
            except:
                pass
        
        # Count CoAs from coats_of_arms.json
        coa_file = os.path.join(db_path, "coa_data", "coats_of_arms.json")
        if os.path.exists(coa_file):
            try:
                with open(coa_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    # Count total CoAs across all galleries
                    for gallery_data in data.values():
                        if isinstance(gallery_data, dict) and "coas" in gallery_data:
                            stats["coa_count"] += len(gallery_data["coas"])
            except:
                pass
        
        return stats
