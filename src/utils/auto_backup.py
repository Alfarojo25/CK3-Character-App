#!/usr/bin/env python3
"""
Auto Backup Manager
Handles automatic database backups at configurable intervals.
"""

import os
import shutil
import zipfile
import threading
import time
from datetime import datetime
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class AutoBackupManager:
    """Manages automatic database backups."""
    
    # Backup intervals in minutes
    INTERVALS = {
        "disabled": 0,
        "1min": 1,
        "5min": 5,
        "10min": 10,
        "30min": 30
    }
    
    def __init__(self, db_directory: str, backup_directory: str, 
                 interval: str = "disabled", max_backups: int = 10):
        """
        Initialize auto backup manager.
        
        Args:
            db_directory: Path to database directory
            backup_directory: Path to backup storage directory
            interval: Backup interval ("disabled", "1min", "5min", "10min", "30min")
            max_backups: Maximum number of backups to keep
        """
        self.db_directory = db_directory
        self.backup_directory = backup_directory
        self.interval = interval
        self.max_backups = max_backups
        
        self.is_running = False
        self.backup_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callback for backup completion
        self.on_backup_complete: Optional[Callable[[str], None]] = None
        
        # Ensure backup directory exists
        os.makedirs(backup_directory, exist_ok=True)
        
        logger.info(f"AutoBackupManager initialized: interval={interval}, max_backups={max_backups}")
    
    def start(self):
        """Start automatic backups."""
        if self.interval == "disabled" or self.INTERVALS[self.interval] == 0:
            logger.info("Auto backup is disabled")
            return
        
        if self.is_running:
            logger.warning("Auto backup already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()
        
        logger.info(f"Auto backup started with {self.interval} interval")
    
    def stop(self):
        """Stop automatic backups."""
        if not self.is_running:
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        
        logger.info("Auto backup stopped")
    
    def set_interval(self, interval: str):
        """
        Change backup interval.
        
        Args:
            interval: New backup interval
        """
        if interval not in self.INTERVALS:
            logger.error(f"Invalid interval: {interval}")
            return
        
        was_running = self.is_running
        
        if was_running:
            self.stop()
        
        self.interval = interval
        logger.info(f"Backup interval changed to: {interval}")
        
        if was_running and interval != "disabled":
            self.start()
    
    def _backup_loop(self):
        """Main backup loop (runs in separate thread)."""
        interval_minutes = self.INTERVALS[self.interval]
        interval_seconds = interval_minutes * 60
        
        while self.is_running and not self.stop_event.is_set():
            # Wait for interval or stop event
            if self.stop_event.wait(timeout=interval_seconds):
                break
            
            # Perform backup
            try:
                backup_path = self.create_backup()
                logger.info(f"Auto backup created: {backup_path}")
                
                # Call callback if set
                if self.on_backup_complete:
                    self.on_backup_complete(backup_path)
                
                # Clean old backups
                self.cleanup_old_backups()
                
            except Exception as e:
                logger.error(f"Auto backup failed: {e}")
    
    def create_backup(self) -> str:
        """
        Create a backup of the database.
        
        Returns:
            Path to created backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_directory, backup_name)
        
        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through database directory
            for root, dirs, files in os.walk(self.db_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.db_directory)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    
    def cleanup_old_backups(self):
        """Remove old backups exceeding max_backups limit."""
        try:
            # Get all backup files
            backups = []
            for file in os.listdir(self.backup_directory):
                if file.startswith("auto_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(self.backup_directory, file)
                    backups.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            if len(backups) > self.max_backups:
                for file_path, _ in backups[self.max_backups:]:
                    try:
                        os.remove(file_path)
                        logger.info(f"Removed old backup: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove backup {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_backup_list(self) -> list:
        """
        Get list of available backups.
        
        Returns:
            List of tuples (filename, size, date)
        """
        backups = []
        
        try:
            for file in os.listdir(self.backup_directory):
                if file.startswith("auto_backup_") and file.endswith(".zip"):
                    file_path = os.path.join(self.backup_directory, file)
                    size = os.path.getsize(file_path)
                    mtime = os.path.getmtime(file_path)
                    date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                    backups.append((file, size, date, file_path))
            
            # Sort by date (newest first)
            backups.sort(key=lambda x: x[2], reverse=True)
        
        except Exception as e:
            logger.error(f"Failed to get backup list: {e}")
        
        return backups
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup of current database before restoring
            current_backup = os.path.join(
                self.backup_directory,
                f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )
            
            with zipfile.ZipFile(current_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.db_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.db_directory)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Created backup before restore: {current_backup}")
            
            # Clear current database directory
            for item in os.listdir(self.db_directory):
                item_path = os.path.join(self.db_directory, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.db_directory)
            
            logger.info(f"Database restored from: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
