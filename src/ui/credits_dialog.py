"""
Credits Dialog
Shows credits and links to original projects and authors.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser


class CreditsDialog(tk.Toplevel):
    """Dialog showing credits and project links."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Credits")
        self.geometry("700x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        self.bind('<Escape>', lambda e: self.destroy())
    
    def setup_ui(self):
        """Setup UI components."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#2e5c8a", relief="raised", bd=2)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            header_frame, 
            text="CK3 Character & CoA Manager",
            font=("TkDefaultFont", 16, "bold"),
            background="#2e5c8a",
            foreground="white"
        ).pack(pady=15)
        
        ttk.Label(
            header_frame,
            text="Version 2.0",
            font=("TkDefaultFont", 10),
            background="#2e5c8a",
            foreground="white"
        ).pack(pady=(0, 15))
        
        # Scrollable content
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content = scrollable_frame
        
        # Developed by section
        ttk.Label(
            content,
            text="Developed by",
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(10, 5))
        
        ttk.Label(
            content,
            text="Alfarojo",
            font=("TkDefaultFont", 11)
        ).pack()
        
        self.create_link(content, "GitHub: https://github.com/Alfarojo25", 
                        "https://github.com/Alfarojo25")
        
        # Separator
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=20)
        
        # Based on section
        ttk.Label(
            content,
            text="Based on Original Projects",
            font=("TkDefaultFont", 12, "bold")
        ).pack(pady=(0, 15))
        
        # CK3-Character-Gallery
        gallery_frame = ttk.LabelFrame(content, text="CK3-Character-Gallery", padding=15)
        gallery_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            gallery_frame,
            text="by huangfanglong",
            font=("TkDefaultFont", 10, "italic")
        ).pack(anchor="w")
        
        ttk.Label(
            gallery_frame,
            text="Character gallery management system and portrait handling",
            wraplength=600
        ).pack(anchor="w", pady=(5, 10))
        
        self.create_link(gallery_frame, "GitHub: https://github.com/huangfanglong/CK3-Character-Gallery",
                        "https://github.com/huangfanglong/CK3-Character-Gallery")
        self.create_link(gallery_frame, "Reddit: CK3 local character warehouse",
                        "https://www.reddit.com/r/CKTinder/comments/1offc3u/ck3_local_character_warehouse/")
        
        # CK3-DNA-Duplicator
        dna_frame = ttk.LabelFrame(content, text="CK3-DNA-Duplicator", padding=15)
        dna_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            dna_frame,
            text="by Deticaru",
            font=("TkDefaultFont", 10, "italic")
        ).pack(anchor="w")
        
        ttk.Label(
            dna_frame,
            text="DNA duplication functionality and validation system",
            wraplength=600
        ).pack(anchor="w", pady=(5, 10))
        
        self.create_link(dna_frame, "GitHub: https://github.com/Deticaru/CK3-DNA-Duplicator",
                        "https://github.com/Deticaru/CK3-DNA-Duplicator")
        self.create_link(dna_frame, "Reddit: For DNA enthusiasts",
                        "https://www.reddit.com/r/CKTinder/comments/1ob8yzr/for_dna_enthusiasts/")
        
        # Separator
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=20)
        
        # Features section
        ttk.Label(
            content,
            text="This Project Adds",
            font=("TkDefaultFont", 11, "bold")
        ).pack(pady=(0, 10))
        
        features = [
            "✓ Unified application combining both tools",
            "✓ Multiple database system",
            "✓ Coat of Arms support",
            "✓ Cross-database item movement",
            "✓ Enhanced UI/UX with menu system",
            "✓ Multi-language support (12 languages)",
            "✓ Improved workflows and features"
        ]
        
        for feature in features:
            ttk.Label(content, text=feature).pack(anchor="w", padx=20, pady=2)
        
        # Thanks message
        ttk.Label(
            content,
            text="\nSpecial thanks to the original creators\nand the CK3 modding community!",
            font=("TkDefaultFont", 9, "italic"),
            justify="center"
        ).pack(pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="right")
    
    def create_link(self, parent, text, url):
        """Create a clickeable link label."""
        link = tk.Label(
            parent,
            text=text,
            foreground="blue",
            cursor="hand2",
            font=("TkDefaultFont", 9, "underline")
        )
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda e: webbrowser.open(url))
        link.bind("<Enter>", lambda e: link.config(foreground="darkblue"))
        link.bind("<Leave>", lambda e: link.config(foreground="blue"))
