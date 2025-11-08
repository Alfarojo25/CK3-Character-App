"""
Welcome Dialog
First-run configuration dialog for language and database location.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Tuple


class WelcomeDialog(tk.Toplevel):
    """Welcome dialog for first-time setup."""
    
    def __init__(self, parent, available_languages: list, default_lang: str = "en"):
        """
        Initialize welcome dialog.
        
        Args:
            parent: Parent window
            available_languages: List of dicts with 'code', 'name', 'native' keys
            default_lang: Default language code
        """
        super().__init__(parent)
        
        self.title("Welcome / Bienvenido - CK3 Character Manager")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Center on screen
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.available_languages = available_languages
        self.selected_lang = tk.StringVar(value=default_lang)
        # Default to Documents/CK3-Character-Manager
        default_db_path = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "CK3-Character-Manager"
        )
        self.selected_db_dir = tk.StringVar(value=default_db_path)
        self.result: Optional[Tuple[str, str]] = None
        self.dir_entry = None  # Will be set in setup_ui
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Welcome to CK3 Character Manager\nBienvenido a CK3 Character Manager",
            font=("Segoe UI", 14, "bold"),
            justify=tk.CENTER
        )
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = (
            "Please configure your preferences for first use.\n"
            "Por favor configure sus preferencias para el primer uso."
        )
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            justify=tk.CENTER,
            wraplength=500
        )
        desc_label.pack(pady=(0, 30))
        
        # Language section
        lang_frame = ttk.LabelFrame(main_frame, text="Language / Idioma", padding="15")
        lang_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            lang_frame,
            text="Select your preferred language / Seleccione su idioma:"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Language dropdown
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.selected_lang,
            state="readonly",
            width=40
        )
        
        # Populate languages
        lang_options = []
        lang_values = []
        for lang in self.available_languages:
            display = f"{lang['native']} - {lang['name']}"
            lang_options.append(display)
            lang_values.append(lang['code'])
        
        lang_combo['values'] = lang_options
        
        # Set default selection
        try:
            default_index = lang_values.index(self.selected_lang.get())
            lang_combo.current(default_index)
        except ValueError:
            lang_combo.current(0)
        
        # Update selected_lang when combo changes
        self.lang_values = lang_values
        lang_combo.bind('<<ComboboxSelected>>', 
                       lambda e: self.selected_lang.set(self.lang_values[lang_combo.current()]))
        
        lang_combo.pack(fill=tk.X)
        
        # Database directory section
        db_frame = ttk.LabelFrame(
            main_frame,
            text="Database Location / Ubicación de Base de Datos",
            padding="15"
        )
        db_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            db_frame,
            text="Select where to store your databases / Seleccione dónde guardar sus bases de datos:"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Directory selector
        dir_entry_frame = ttk.Frame(db_frame)
        dir_entry_frame.pack(fill=tk.X)
        
        self.dir_entry = ttk.Entry(dir_entry_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        # Set initial value from variable
        self.dir_entry.insert(0, self.selected_db_dir.get())
        
        browse_btn = ttk.Button(
            dir_entry_frame,
            text="Browse / Explorar...",
            command=self.browse_directory
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        continue_btn = ttk.Button(
            button_frame,
            text="Continue / Continuar",
            command=self.on_continue,
            style="Accent.TButton"
        )
        continue_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel / Cancelar",
            command=self.on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.on_continue())
        self.bind('<Escape>', lambda e: self.on_cancel())
    
    def browse_directory(self):
        """Open directory browser."""
        current_dir = self.dir_entry.get()
        if not current_dir or not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")  # Use home directory as fallback
        
        selected = filedialog.askdirectory(
            title="Select Database Directory / Seleccionar Carpeta de Base de Datos",
            initialdir=current_dir,
            mustexist=False
        )
        
        if selected:
            abs_path = os.path.abspath(selected)
            self.selected_db_dir.set(abs_path)
            # Update entry field
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, abs_path)
    
    def on_continue(self):
        """Handle continue button."""
        # Get directory from entry field
        db_dir = self.dir_entry.get().strip()
        
        # Validate selections
        if not self.selected_lang.get():
            messagebox.showwarning(
                "Warning / Advertencia",
                "Please select a language.\nPor favor seleccione un idioma."
            )
            return
        
        if not db_dir:
            messagebox.showwarning(
                "Warning / Advertencia",
                "Please select a database directory.\nPor favor seleccione una carpeta para la base de datos."
            )
            return
        
        # Store results
        self.result = (self.selected_lang.get(), db_dir)
        self.destroy()
    
    def on_cancel(self):
        """Handle cancel button."""
        if messagebox.askyesno(
            "Confirm Exit / Confirmar Salida",
            "Are you sure you want to exit?\n¿Está seguro que desea salir?"
        ):
            self.result = None
            self.destroy()
    
    def show(self) -> Optional[Tuple[str, str]]:
        """
        Show dialog and wait for result.
        
        Returns:
            Tuple of (language_code, database_directory) or None if cancelled
        """
        self.wait_window()
        return self.result
