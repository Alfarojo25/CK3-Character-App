#!/usr/bin/env python3
"""
Statistics Dialog
Shows gallery statistics and analytics.
"""

import tkinter as tk
from tkinter import ttk
from collections import Counter
from typing import Optional


class StatisticsDialog(tk.Toplevel):
    """Dialog for displaying gallery statistics."""
    
    def __init__(self, parent, gallery_manager, gallery_name: Optional[str], i18n):
        """
        Initialize statistics dialog.
        
        Args:
            parent: Parent window
            gallery_manager: GalleryManager instance
            gallery_name: Name of current gallery
            i18n: Internationalization instance
        """
        super().__init__(parent)
        
        self.gallery_manager = gallery_manager
        self.gallery_name = gallery_name
        self.i18n = i18n
        
        self.title(self.i18n.t("statistics_title"))
        self.geometry("600x700")
        self.configure(bg="#2e2e2e")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.calculate_statistics()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        # Main container
        main_frame = tk.Frame(self, bg="#2e2e2e", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=self.i18n.t("statistics_title"),
            font=("Arial", 16, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        )
        title_label.pack(pady=(0, 20))
        
        # Gallery info
        if self.gallery_name:
            gallery_label = tk.Label(
                main_frame,
                text=f"{self.i18n.t('statistics_gallery')} {self.gallery_name}",
                font=("Arial", 12),
                bg="#2e2e2e",
                fg="#eeeeee"
            )
            gallery_label.pack(pady=(0, 15))
        
        # Statistics frame
        stats_frame = tk.Frame(main_frame, bg="#1e1e1e", relief="ridge", borderwidth=2)
        stats_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Statistics labels (will be populated later)
        self.stats_labels = {}
        
        # Create stat rows
        stat_keys = [
            "total_characters",
            "total_tags",
            "avg_tags_per_char",
            "characters_with_portraits",
            "characters_with_dna"
        ]
        
        for key in stat_keys:
            row = tk.Frame(stats_frame, bg="#1e1e1e")
            row.pack(fill="x", padx=15, pady=8)
            
            label = tk.Label(
                row,
                text=self.i18n.t(f"statistics_{key}"),
                font=("Arial", 11),
                bg="#1e1e1e",
                fg="#cccccc",
                anchor="w"
            )
            label.pack(side="left")
            
            value = tk.Label(
                row,
                text="0",
                font=("Arial", 11, "bold"),
                bg="#1e1e1e",
                fg="#14ffec",
                anchor="e"
            )
            value.pack(side="right")
            
            self.stats_labels[key] = value
        
        # Top tags section
        tags_label = tk.Label(
            main_frame,
            text=self.i18n.t("statistics_top_tags"),
            font=("Arial", 12, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        )
        tags_label.pack(pady=(10, 5))
        
        # Tags listbox with scrollbar
        tags_container = tk.Frame(main_frame, bg="#2e2e2e")
        tags_container.pack(fill="both", expand=True)
        
        tags_scroll = tk.Scrollbar(tags_container)
        tags_scroll.pack(side="right", fill="y")
        
        self.tags_listbox = tk.Listbox(
            tags_container,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#eeeeee",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            yscrollcommand=tags_scroll.set,
            height=10
        )
        self.tags_listbox.pack(side="left", fill="both", expand=True)
        tags_scroll.config(command=self.tags_listbox.yview)
        
        # Close button
        btn_frame = tk.Frame(main_frame, bg="#2e2e2e")
        btn_frame.pack(pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text=self.i18n.t("statistics_close"),
            command=self.destroy,
            width=15
        ).pack()
    
    def calculate_statistics(self):
        """Calculate and display statistics."""
        if not self.gallery_name:
            return
        
        # Get all characters
        characters = self.gallery_manager.get_characters(self.gallery_name)
        
        if not characters:
            return
        
        # Calculate statistics
        total_chars = len(characters)
        
        # Count tags
        all_tags = []
        chars_with_portraits = 0
        chars_with_dna = 0
        
        for char in characters:
            # Tags
            tags = char.get("tags", [])
            all_tags.extend(tags)
            
            # Portraits
            if char.get("image"):
                chars_with_portraits += 1
            
            # DNA
            if char.get("dna"):
                chars_with_dna += 1
        
        # Unique tags
        unique_tags = len(set(all_tags))
        
        # Average tags per character
        avg_tags = len(all_tags) / total_chars if total_chars > 0 else 0
        
        # Update statistics labels
        self.stats_labels["total_characters"].config(text=str(total_chars))
        self.stats_labels["total_tags"].config(text=str(unique_tags))
        self.stats_labels["avg_tags_per_char"].config(text=f"{avg_tags:.2f}")
        self.stats_labels["characters_with_portraits"].config(
            text=f"{chars_with_portraits} ({chars_with_portraits*100//total_chars if total_chars > 0 else 0}%)"
        )
        self.stats_labels["characters_with_dna"].config(
            text=f"{chars_with_dna} ({chars_with_dna*100//total_chars if total_chars > 0 else 0}%)"
        )
        
        # Top tags
        tag_counter = Counter(all_tags)
        top_tags = tag_counter.most_common(10)
        
        # Display top tags
        self.tags_listbox.delete(0, tk.END)
        
        if top_tags:
            # Add header
            header = f"{'#':<4} {self.i18n.t('statistics_tag'):<30} {self.i18n.t('statistics_count'):>10}"
            self.tags_listbox.insert(tk.END, header)
            self.tags_listbox.insert(tk.END, "-" * 50)
            
            # Add tags
            for i, (tag, count) in enumerate(top_tags, 1):
                percentage = (count * 100) / total_chars if total_chars > 0 else 0
                line = f"{i:<4} {tag:<30} {count:>5} ({percentage:>5.1f}%)"
                self.tags_listbox.insert(tk.END, line)
        else:
            self.tags_listbox.insert(tk.END, "No tags found")
