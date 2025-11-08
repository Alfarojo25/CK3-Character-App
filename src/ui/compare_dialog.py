#!/usr/bin/env python3
"""
Compare Characters Dialog
Compare two characters side by side.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os


class CompareCharactersDialog(tk.Toplevel):
    """Dialog for comparing two characters."""
    
    def __init__(self, parent, gallery_manager, gallery_name: str, i18n):
        """
        Initialize compare dialog.
        
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
        
        self.title(self.i18n.t("compare_title"))
        self.geometry("1000x800")
        self.configure(bg="#2e2e2e")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Character data
        self.char1 = None
        self.char2 = None
        self.photo1 = None
        self.photo2 = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        # Main container
        main_frame = tk.Frame(self, bg="#2e2e2e", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=self.i18n.t("compare_title"),
            font=("Arial", 16, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        )
        title_label.pack(pady=(0, 15))
        
        # Selection frame
        selection_frame = tk.Frame(main_frame, bg="#2e2e2e")
        selection_frame.pack(fill="x", pady=(0, 15))
        
        # Instructions
        tk.Label(
            selection_frame,
            text=self.i18n.t("compare_select_characters"),
            font=("Arial", 11),
            bg="#2e2e2e",
            fg="#eeeeee"
        ).pack(pady=(0, 10))
        
        # Character selectors
        selector_row = tk.Frame(selection_frame, bg="#2e2e2e")
        selector_row.pack(fill="x")
        
        # Character 1 selector
        char1_frame = tk.Frame(selector_row, bg="#2e2e2e")
        char1_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Label(
            char1_frame,
            text=self.i18n.t("compare_character_1"),
            font=("Arial", 10),
            bg="#2e2e2e",
            fg="#cccccc"
        ).pack(anchor="w")
        
        self.char1_var = tk.StringVar()
        self.char1_combo = ttk.Combobox(
            char1_frame,
            textvariable=self.char1_var,
            state="readonly",
            font=("Arial", 10)
        )
        self.char1_combo.pack(fill="x")
        
        # Character 2 selector
        char2_frame = tk.Frame(selector_row, bg="#2e2e2e")
        char2_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        tk.Label(
            char2_frame,
            text=self.i18n.t("compare_character_2"),
            font=("Arial", 10),
            bg="#2e2e2e",
            fg="#cccccc"
        ).pack(anchor="w")
        
        self.char2_var = tk.StringVar()
        self.char2_combo = ttk.Combobox(
            char2_frame,
            textvariable=self.char2_var,
            state="readonly",
            font=("Arial", 10)
        )
        self.char2_combo.pack(fill="x")
        
        # Load character names
        self.load_character_names()
        
        # Compare button
        ttk.Button(
            selection_frame,
            text=self.i18n.t("compare_button"),
            command=self.compare_characters,
            width=20
        ).pack(pady=(10, 0))
        
        # Comparison frame (will be populated after comparison)
        self.comparison_frame = tk.Frame(main_frame, bg="#2e2e2e")
        self.comparison_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        # Close button
        btn_frame = tk.Frame(main_frame, bg="#2e2e2e")
        btn_frame.pack(pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text=self.i18n.t("compare_close"),
            command=self.destroy,
            width=15
        ).pack()
    
    def load_character_names(self):
        """Load character names into comboboxes."""
        characters = self.gallery_manager.get_characters(self.gallery_name)
        names = [char.get("name", "") for char in characters]
        
        self.char1_combo["values"] = names
        self.char2_combo["values"] = names
        
        if names:
            self.char1_combo.current(0)
            if len(names) > 1:
                self.char2_combo.current(1)
            else:
                self.char2_combo.current(0)
    
    def compare_characters(self):
        """Compare the selected characters."""
        name1 = self.char1_var.get()
        name2 = self.char2_var.get()
        
        if not name1 or not name2:
            return
        
        if name1 == name2:
            messagebox.showwarning(
                self.i18n.t("warning"),
                self.i18n.t("compare_select_two")
            )
            return
        
        # Get character data
        characters = self.gallery_manager.get_characters(self.gallery_name)
        self.char1 = next((c for c in characters if c.get("name") == name1), None)
        self.char2 = next((c for c in characters if c.get("name") == name2), None)
        
        if not self.char1 or not self.char2:
            return
        
        # Clear previous comparison
        for widget in self.comparison_frame.winfo_children():
            widget.destroy()
        
        # Create comparison view
        self.create_comparison_view()
    
    def create_comparison_view(self):
        """Create the comparison view."""
        # Create two columns
        col1 = tk.Frame(self.comparison_frame, bg="#1e1e1e", relief="ridge", borderwidth=2)
        col1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        col2 = tk.Frame(self.comparison_frame, bg="#1e1e1e", relief="ridge", borderwidth=2)
        col2.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Populate columns
        self.populate_character_column(col1, self.char1)
        self.populate_character_column(col2, self.char2)
    
    def populate_character_column(self, parent, character):
        """
        Populate a column with character data.
        
        Args:
            parent: Parent frame
            character: Character data dictionary
        """
        # Character name header
        name = character.get("name", "Unknown")
        name_label = tk.Label(
            parent,
            text=name,
            font=("Arial", 14, "bold"),
            bg="#1e1e1e",
            fg="#14ffec",
            pady=10
        )
        name_label.pack()
        
        # Portrait
        portrait_frame = tk.Frame(parent, bg="#1e1e1e")
        portrait_frame.pack(pady=10)
        
        image_path = character.get("image")
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Store reference to prevent garbage collection
                if character == self.char1:
                    self.photo1 = photo
                else:
                    self.photo2 = photo
                
                canvas = tk.Canvas(
                    portrait_frame,
                    width=200,
                    height=200,
                    bg="#252526",
                    highlightthickness=0
                )
                canvas.pack()
                canvas.create_image(100, 100, image=photo)
            except Exception as e:
                tk.Label(
                    portrait_frame,
                    text="[No Portrait]",
                    font=("Arial", 10),
                    bg="#1e1e1e",
                    fg="#666666"
                ).pack()
        else:
            tk.Label(
                portrait_frame,
                text="[No Portrait]",
                font=("Arial", 10),
                bg="#1e1e1e",
                fg="#666666"
            ).pack()
        
        # Info container
        info_frame = tk.Frame(parent, bg="#1e1e1e")
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Tags
        self.add_info_row(info_frame, self.i18n.t("compare_tags"), 
                         ", ".join(character.get("tags", [])) or "None")
        
        # DNA info
        dna = character.get("dna", "")
        has_dna = self.i18n.t("compare_yes") if dna else self.i18n.t("compare_no")
        self.add_info_row(info_frame, self.i18n.t("compare_has_portrait"),
                         self.i18n.t("compare_yes") if image_path else self.i18n.t("compare_no"))
        
        self.add_info_row(info_frame, "DNA", has_dna)
        
        if dna:
            self.add_info_row(info_frame, self.i18n.t("compare_dna_length"), str(len(dna)))
            
            # DNA preview
            dna_frame = tk.Frame(info_frame, bg="#1e1e1e")
            dna_frame.pack(fill="both", expand=True, pady=(5, 0))
            
            tk.Label(
                dna_frame,
                text=self.i18n.t("compare_dna") + ":",
                font=("Arial", 9, "bold"),
                bg="#1e1e1e",
                fg="#cccccc",
                anchor="w"
            ).pack(fill="x")
            
            dna_text = tk.Text(
                dna_frame,
                height=6,
                width=40,
                wrap="word",
                bg="#252526",
                fg="#eeeeee",
                font=("Consolas", 8),
                relief="sunken",
                borderwidth=1
            )
            dna_text.pack(fill="both", expand=True)
            dna_text.insert("1.0", dna[:500] + ("..." if len(dna) > 500 else ""))
            dna_text.config(state="disabled")
    
    def add_info_row(self, parent, label: str, value: str):
        """
        Add an info row to the parent frame.
        
        Args:
            parent: Parent frame
            label: Label text
            value: Value text
        """
        row = tk.Frame(parent, bg="#1e1e1e")
        row.pack(fill="x", pady=3)
        
        tk.Label(
            row,
            text=f"{label}:",
            font=("Arial", 9, "bold"),
            bg="#1e1e1e",
            fg="#cccccc",
            anchor="w",
            width=15
        ).pack(side="left")
        
        tk.Label(
            row,
            text=value,
            font=("Arial", 9),
            bg="#1e1e1e",
            fg="#eeeeee",
            anchor="w",
            wraplength=250
        ).pack(side="left", fill="x", expand=True)
