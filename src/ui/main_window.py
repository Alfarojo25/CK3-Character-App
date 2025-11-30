"""
Main Application Window
Unified CK3 Character Manager with Gallery and DNA Duplicator.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageGrab
import os
import sys
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import GalleryManager, duplicate_dna, validate_dna, DatabaseManager, CoAManager
from utils import (
    copy_to_clipboard, crop_image,
    get_config, get_i18n, t, 
    setup_logging, get_logger
)
from utils.theme_manager import ThemeManager
from utils.auto_backup import AutoBackupManager
from ui.image_cropper import ImageCropper
from ui.database_dialogs import (
    CreateDatabaseDialog, SelectDatabaseDialog, 
    MoveItemsDialog, DatabaseInfoDialog
)
from ui.credits_dialog import CreditsDialog

# Setup logging
setup_logging()
logger = get_logger(__name__)


class CK3CharacterApp(tk.Tk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Initializing CK3 Character Manager")
        
        # Setup Tkinter error reporting
        self.report_callback_exception = self.handle_tk_exception
        
        # Initialize configuration and i18n first
        self.app_config = get_config()
        self.i18n = get_i18n()
        
        # Initialize theme manager
        theme_name = self.app_config.get("theme", "dark")
        self.theme_manager = ThemeManager(theme_name)
        logger.info(f"Theme set to: {theme_name}")
        
        # Set language from config
        lang_code = self.app_config.get("language", "en")
        if lang_code in [lang['code'] for lang in self.i18n.get_available_languages()]:
            self.i18n.set_language(lang_code)
            logger.info(f"Language set to: {lang_code}")
        else:
            logger.warning(f"Language {lang_code} not available, using default")
        
        # Set window title using translation
        self.title(self.i18n.t("app_title"))
        self.geometry("1600x900")
        
        # Apply theme colors
        theme = self.theme_manager.get_theme()
        self.configure(bg=theme.get_color("bg_secondary"))
        
        # Configure ttk styles
        style = ttk.Style(self)
        style_config = self.theme_manager.get_style_config()
        for widget_style, config in style_config.items():
            if "configure" in config:
                style.configure(widget_style, **config["configure"])
            if "map" in config:
                style.map(widget_style, **config["map"])
        
        # Get database directory from config or ask
        db_dir = self.app_config.get("database_directory", "databases")
        if not os.path.exists(db_dir):
            db_dir = self.ask_database_directory()
            self.app_config.set("database_directory", db_dir)
        
        logger.info(f"Using database directory: {db_dir}")
        
        # Initialize database manager first
        self.db_manager = DatabaseManager(base_dir=db_dir)
        
        # Get current database name from config or use db_manager's current
        db_name = self.app_config.get("current_database_name")
        if not db_name:
            # Fallback to db_manager's current database
            db_name = self.db_manager.get_current_database("character")
        
        # Initialize managers with current database name
        self.current_db_name = db_name
        self.gallery_manager = GalleryManager(base_dir=db_dir, db_name=db_name)
        self.coa_manager = CoAManager(base_dir=db_dir, db_name=db_name)
        
        # Save current database name to config
        self.app_config.set("current_database_name", db_name)
        
        # Initialize auto backup manager
        backup_dir = os.path.join(db_dir, "backups")
        auto_backup_enabled = self.app_config.get("auto_backup_enabled", True)
        auto_backup_interval = self.app_config.get("auto_backup_interval", "10min")
        auto_backup_max = self.app_config.get("auto_backup_max_count", 10)
        
        # Backup the entire database folder (Database_Default) which contains both character_data and coa_data
        backup_source_dir = self.gallery_manager.db_folder
        
        self.auto_backup_manager = AutoBackupManager(
            db_directory=backup_source_dir,
            backup_directory=backup_dir,
            interval=auto_backup_interval if auto_backup_enabled else "disabled",
            max_backups=auto_backup_max,
            db_name=db_name
        )
        
        # Start auto backup if enabled
        if auto_backup_enabled:
            self.auto_backup_manager.start()
            logger.info("Auto backup started")
        
        # Current state
        self.current_mode = "character"  # "character" or "coa"
        self.current_gallery_name = None
        self.current_character = None
        self.current_coa = None
        self.dirty = False
        
        # UI components
        self.portrait_photo = None
        self.portrait_image_id = None
        
        # Setup menu bar first
        self.setup_menu_bar()
        
        # Setup UI
        self.setup_ui()
        
        # Update window title with active database
        mode_name = "Character" if self.current_mode == "character" else "CoA"
        self.title(f"CK3 Manager - {mode_name} - Database: {self.current_db_name}")
        
        # Load first gallery
        galleries = self.gallery_manager.get_gallery_names()
        if galleries:
            self.current_gallery_name = galleries[0]
            self.gallery_var.set(galleries[0])
            self.load_gallery(galleries[0])
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def handle_tk_exception(self, exc_type, exc_value, exc_traceback):
        """Handle Tkinter exceptions and log them."""
        import traceback
        logger.error("Tkinter exception occurred:")
        logger.error(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        
        # Show error to user
        error_msg = f"{exc_type.__name__}: {exc_value}"
        messagebox.showerror("Error", f"An error occurred:\n\n{error_msg}\n\nCheck log/log.txt for details.")
    
    def ask_database_directory(self) -> str:
        """
        Ask user to select or confirm database directory.
        
        Returns:
            Path to database directory
        """
        default_dir = "databases"
        
        # Check if default directory exists with data
        if os.path.exists(default_dir):
            config_path = os.path.join(default_dir, "db_config.json")
            if os.path.exists(config_path):
                # Database exists, ask if user wants to keep it or change
                response = messagebox.askyesnocancel(
                    "Directorio de Base de Datos",
                    f"Se encontró una base de datos existente en:\n{os.path.abspath(default_dir)}\n\n"
                    "¿Desea usar esta ubicación?\n\n"
                    "Sí = Usar esta ubicación\n"
                    "No = Seleccionar otra ubicación\n"
                    "Cancelar = Salir",
                    icon='question'
                )
                
                if response is None:  # Cancel
                    self.quit()
                    sys.exit(0)
                elif response:  # Yes
                    return default_dir
                # else: No, continue to directory selection
        
        # Ask user to select directory
        selected_dir = filedialog.askdirectory(
            title="Seleccionar carpeta para bases de datos",
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            mustexist=False
        )
        
        if not selected_dir:
            # User cancelled, use default
            messagebox.showinfo(
                "Ubicación por defecto",
                f"Se usará la ubicación por defecto:\n{os.path.abspath(default_dir)}"
            )
            return default_dir
        
        return selected_dir
    
    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Database Menu
        db_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("menu_database"), menu=db_menu)
        
        db_menu.add_command(label=self.i18n.t("menu_database_create"), command=self.create_database)
        db_menu.add_command(label=self.i18n.t("menu_database_switch"), command=self.switch_database)
        db_menu.add_separator()
        db_menu.add_command(label=self.i18n.t("menu_database_backup"), command=self.backup_database)
        db_menu.add_command(label=self.i18n.t("menu_database_manage"), command=self.manage_databases)
        db_menu.add_separator()
        db_menu.add_command(label=self.i18n.t("menu_database_move"), command=self.move_items)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("menu_view"), menu=view_menu)
        
        self.view_mode_var = tk.StringVar(value="character")
        view_menu.add_radiobutton(
            label=self.i18n.t("menu_view_character"), 
            variable=self.view_mode_var, 
            value="character",
            command=lambda: self.switch_mode("character")
        )
        view_menu.add_radiobutton(
            label=self.i18n.t("menu_view_coa"), 
            variable=self.view_mode_var, 
            value="coa",
            command=lambda: self.switch_mode("coa")
        )
        
        view_menu.add_separator()
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=self.i18n.t("menu_view_theme"), menu=theme_menu)
        
        self.theme_var = tk.StringVar(value=self.app_config.get("theme", "dark"))
        theme_menu.add_radiobutton(
            label=self.i18n.t("menu_view_theme_dark"),
            variable=self.theme_var,
            value="dark",
            command=lambda: self.change_theme("dark")
        )
        theme_menu.add_radiobutton(
            label=self.i18n.t("menu_view_theme_light"),
            variable=self.theme_var,
            value="light",
            command=lambda: self.change_theme("light")
        )
        
        view_menu.add_separator()
        view_menu.add_command(label=self.i18n.t("menu_view_statistics"), command=self.show_statistics)
        view_menu.add_command(label=self.i18n.t("menu_view_compare"), command=self.compare_characters)
        
        # Language Menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("menu_language"), menu=lang_menu)
        
        # Add languages dynamically
        self.current_lang_var = tk.StringVar(value=self.i18n.current_lang)
        for lang in self.i18n.get_available_languages():
            lang_menu.add_radiobutton(
                label=f"{lang['native']} - {lang['name']}",
                variable=self.current_lang_var,
                value=lang['code'],
                command=lambda code=lang['code']: self.change_language(code)
            )
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("menu_help"), menu=help_menu)
        
        help_menu.add_command(label=self.i18n.t("menu_help_shortcuts"), command=self.show_shortcuts)
        help_menu.add_command(label=self.i18n.t("menu_help_settings"), command=self.show_settings)
        help_menu.add_separator()
        help_menu.add_command(label=self.i18n.t("menu_help_credits"), command=self.show_credits)
        help_menu.add_command(label=self.i18n.t("menu_help_about"), command=self.show_about)
    
    def setup_ui(self):
        """Setup the user interface."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", foreground="#ffffff", background="#555555")
        style.configure("TLabel", foreground="#dddddd", background="#2e2e2e")
        
        main_frame = tk.Frame(self, bg="#2e2e2e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # LEFT PANEL: Gallery List
        self.setup_left_panel(main_frame)
        
        # MIDDLE PANEL: Portrait and Tags
        self.setup_middle_panel(main_frame)
        
        # RIGHT PANEL: DNA Editor
        self.setup_right_panel(main_frame)
        
        # Status bar at bottom
        self.status_label = tk.Label(
            self, text=self.i18n.t("status_ready"), bg="#2e2e2e", fg="#888888",
            font=("TkDefaultFont", 8)
        )
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=1)
    
    def setup_left_panel(self, parent):
        """Setup left panel with gallery selection and character list."""
        list_frame = tk.Frame(parent, bg="#3a3a3a", width=250)
        list_frame.pack(side="left", fill="y", padx=(0, 10))
        list_frame.pack_propagate(False)
        
        # Gallery selector with menu
        top_frame = tk.Frame(list_frame, bg="#3a3a3a")
        top_frame.pack(fill="x", pady=(5, 2))
        
        self.gallery_var = tk.StringVar()
        self.gallery_box = ttk.Combobox(
            top_frame, textvariable=self.gallery_var,
            values=self.gallery_manager.get_gallery_names() + [f"➕ {self.i18n.t('new_gallery')}"],
            state="readonly"
        )
        self.gallery_box.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.gallery_box.bind("<<ComboboxSelected>>", self.on_gallery_change)
        
        # Gallery menu button
        menu_btn = ttk.Menubutton(top_frame, text="⋮", width=3)
        menu = tk.Menu(menu_btn, tearoff=False)
        menu.add_command(label=self.i18n.t("rename_gallery"), command=self.rename_gallery)
        menu.add_command(label=self.i18n.t("delete_gallery"), command=self.delete_gallery)
        menu.add_separator()
        menu.add_command(label=self.i18n.t("export_gallery"), command=self.export_gallery)
        menu.add_command(label=self.i18n.t("import_gallery"), command=self.import_gallery)
        menu_btn["menu"] = menu
        menu_btn.pack(side="left", padx=(2, 5))
        
        # Search section
        search_section = tk.Frame(list_frame, bg="#3a3a3a")
        search_section.pack(fill="x", padx=5, pady=(5, 5))
        
        # Search label and clear button
        search_header = tk.Frame(search_section, bg="#3a3a3a")
        search_header.pack(fill="x")
        ttk.Label(search_header, text=f"{self.i18n.t('search')}:", background="#3a3a3a").pack(side="left")
        ttk.Button(search_header, text=f"✕ {self.i18n.t('clear')}", command=self.clear_search, width=8).pack(side="right")
        
        # Search type selector
        self.search_type_var = tk.StringVar(value="name")
        search_type_frame = tk.Frame(search_section, bg="#3a3a3a")
        search_type_frame.pack(fill="x", pady=(5, 5))
        ttk.Radiobutton(search_type_frame, text=self.i18n.t("by_name"), variable=self.search_type_var, 
                       value="name", command=self.on_search_type_change).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(search_type_frame, text=self.i18n.t("by_tag"), variable=self.search_type_var, 
                       value="tag", command=self.on_search_type_change).pack(side="left")
        
        # Search box with autocomplete
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_characters())
        self.search_combobox = ttk.Combobox(search_section, textvariable=self.search_var)
        self.search_combobox.pack(fill="x")
        self.search_combobox.bind('<Return>', lambda e: self.filter_characters())
        self.search_entry = self.search_combobox  # Mantener compatibilidad con código existente
        
        # Character listbox
        list_container = tk.Frame(list_frame, bg="#3a3a3a")
        list_container.pack(fill="both", expand=True, padx=5)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.char_listbox = tk.Listbox(
            list_container, bg="#1e1e1e", fg="#eeeeee",
            font=("Arial", 10), selectmode="single",
            yscrollcommand=scrollbar.set, highlightthickness=0
        )
        self.char_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.char_listbox.yview)
        self.char_listbox.bind("<<ListboxSelect>>", self.on_character_select)
        
        # Character buttons
        btn_frame = tk.Frame(list_frame, bg="#3a3a3a")
        btn_frame.pack(fill="x", pady=10, padx=5)
        
        # Actions in a 2x2 grid
        btn_grid = tk.Frame(btn_frame, bg="#3a3a3a")
        btn_grid.pack(fill="x")
        
        # Row 1
        btn_row1 = tk.Frame(btn_grid, bg="#3a3a3a")
        btn_row1.pack(fill="x", pady=(0, 5))
        ttk.Button(btn_row1, text=f"➕ {self.i18n.t('new')}", command=self.new_character, width=10).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_row1, text=f"📋 {self.i18n.t('copy')}", command=self.copy_character, width=10).pack(side="left", fill="x", expand=True)
        
        # Row 2
        btn_row2 = tk.Frame(btn_grid, bg="#3a3a3a")
        btn_row2.pack(fill="x", pady=(0, 5))
        ttk.Button(btn_row2, text=f"✏️ {self.i18n.t('edit')}", command=self.edit_character, width=10).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_row2, text=f"🗑️ {self.i18n.t('delete')}", command=self.delete_character, width=10).pack(side="left", fill="x", expand=True)
        
        # Row 3 - Refresh button
        btn_row3 = tk.Frame(btn_grid, bg="#3a3a3a")
        btn_row3.pack(fill="x")
        ttk.Button(btn_row3, text=f"🔄 {self.i18n.t('refresh')}", command=self.refresh_current_view).pack(fill="x", expand=True)
    
    def setup_middle_panel(self, parent):
        """Setup middle panel with portrait and tags."""
        portrait_frame = tk.Frame(parent, bg="#2e2e2e", width=525)
        portrait_frame.pack(side="left", fill="y", padx=10)
        portrait_frame.pack_propagate(False)
        
        ttk.Label(portrait_frame, text=self.i18n.t("character_portrait"), font=("Arial", 12, "bold")).pack(pady=5)
        
        # Portrait canvas
        self.portrait_canvas = tk.Canvas(
            portrait_frame, width=450, height=450,
            bg="#1e1e1e", highlightthickness=2, highlightbackground="#666666"
        )
        self.portrait_canvas.pack(pady=(0, 10))
        self.portrait_canvas.bind("<Button-1>", lambda e: self.change_portrait())
        
        # Portrait buttons
        portrait_btn_frame = tk.Frame(portrait_frame, bg="#2e2e2e")
        portrait_btn_frame.pack(pady=5)
        ttk.Button(portrait_btn_frame, text=f"📁 {self.i18n.t('change_portrait')}", command=self.change_portrait).pack(side="left", padx=2)
        ttk.Button(portrait_btn_frame, text=f"📋 {self.i18n.t('paste_from_clipboard')}", command=self.paste_portrait).pack(side="left", padx=2)
        
        # Character name
        ttk.Label(portrait_frame, text=self.i18n.t("character_name"), font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(portrait_frame, textvariable=self.name_var, font=("Arial", 11))
        self.name_entry.pack(fill="x", padx=10)
        self.name_var.trace_add("write", lambda *args: self.on_data_change())
        
        # Tags section
        ttk.Label(portrait_frame, text=self.i18n.t("tags_comma_separated"), font=("Arial", 10, "bold")).pack(pady=(15, 5))
        self.tags_text = tk.Text(
            portrait_frame, wrap="word", bg="#1e1e1e", fg="#eeeeee",
            font=("Arial", 10), insertbackground="white", height=3
        )
        self.tags_text.pack(fill="x", padx=10, pady=5)
        self.tags_text.bind("<KeyRelease>", lambda e: self.on_data_change())
    
    def setup_right_panel(self, parent):
        """Setup right panel with DNA editor and duplicator."""
        dna_frame = tk.Frame(parent, bg="#2e2e2e")
        dna_frame.pack(side="right", fill="both", expand=True)
        
        ttk.Label(dna_frame, text=self.i18n.t("character_dna"), font=("Arial", 12, "bold")).pack(pady=5)
        
        # DNA text editor
        text_container = tk.Frame(dna_frame, bg="#2e2e2e")
        text_container.pack(fill="both", expand=True)
        
        self.dna_text = tk.Text(
            text_container, wrap="none", bg="#1e1e1e", fg="#eeeeee",
            font=("Consolas", 10), insertbackground="white",
            undo=True, maxundo=-1
        )
        self.dna_text.pack(side="left", fill="both", expand=True)
        
        dna_scroll_y = ttk.Scrollbar(text_container, orient="vertical", command=self.dna_text.yview)
        dna_scroll_y.pack(side="right", fill="y")
        self.dna_text.config(yscrollcommand=dna_scroll_y.set)
        self.dna_text.bind("<KeyRelease>", lambda e: self.on_data_change())
        
        # DNA action buttons
        btn_frame = tk.Frame(dna_frame, bg="#2e2e2e")
        btn_frame.pack(fill="x", pady=10, padx=5)
        
        # First row - Main actions
        btn_row1 = tk.Frame(btn_frame, bg="#2e2e2e")
        btn_row1.pack(fill="x", pady=(0, 5))
        ttk.Button(btn_row1, text=f"🧬 {self.i18n.t('duplicate_dna')}", command=self.duplicate_dna_action).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(btn_row1, text=f"✓ {self.i18n.t('validate_dna')}", command=self.validate_dna_action).pack(side="left", fill="x", expand=True, padx=3)
        ttk.Button(btn_row1, text=f"🗑️ {self.i18n.t('clear')}", command=lambda: self.dna_text.delete("1.0", tk.END)).pack(side="left", fill="x", expand=True, padx=(3, 0))
        
        # Second row - Save and Copy
        btn_row2 = tk.Frame(btn_frame, bg="#2e2e2e")
        btn_row2.pack(fill="x")
        ttk.Button(btn_row2, text=f"📋 {self.i18n.t('copy_dna')}", command=self.copy_dna).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(btn_row2, text=f"💾 {self.i18n.t('save')}", command=self.save_character).pack(side="left", fill="x", expand=True, padx=(3, 0))
    
    def setup_hotkeys(self):
        """Setup keyboard shortcuts."""
        self.bind_all("<Control-s>", lambda e: self.save_character())
        self.bind_all("<Control-n>", lambda e: self.new_character())
        self.bind_all("<Control-d>", lambda e: self.duplicate_dna_action())
        self.bind_all("<Control-v>", lambda e: self.paste_portrait())
        self.bind_all("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind_all("<Control-c>", lambda e: self.copy_character())
        self.bind_all("<Delete>", lambda e: self.delete_character())
    
    def set_status(self, message: str, color: str = "#00FF00"):
        """Set status bar message."""
        self.status_label.config(text=message, fg=color)
        self.after(5000, lambda: self.status_label.config(text="Ready", fg="#888888"))
    
    def on_close(self):
        """Handle window close event."""
        if self.dirty:
            response = messagebox.askyesnocancel(
                self.i18n.t("unsaved_changes"),
                self.i18n.t("unsaved_changes_message")
            )
            if response is None:  # Cancel
                return
            if response:  # Yes
                self.save_character()
        
        # Stop auto backup
        if hasattr(self, 'auto_backup_manager'):
            self.auto_backup_manager.stop()
            logger.info("Auto backup stopped")
        
        self.destroy()
    
    # Gallery Management Methods
    
    def on_gallery_change(self, event=None):
        """Handle gallery selection change."""
        name = self.gallery_var.get()
        if name == "➕ New Gallery...":
            self.create_new_gallery()
        else:
            self.load_gallery(name)
    
    def create_new_gallery(self):
        """Create a new gallery."""
        name = simpledialog.askstring("New Gallery", "Enter gallery name:", parent=self)
        if name:
            if self.gallery_manager.create_gallery(name):
                self.gallery_box["values"] = self.gallery_manager.get_gallery_names() + ["➕ New Gallery..."]
                self.gallery_var.set(name)
                self.load_gallery(name)
                self.set_status(self.i18n.t("gallery_created", name=name))
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("gallery_name_exists"))
        else:
            # Reset to current gallery if cancelled
            if self.current_gallery_name:
                self.gallery_var.set(self.current_gallery_name)
    
    def rename_gallery(self):
        """Rename current gallery."""
        if not self.current_gallery_name:
            return
        new_name = simpledialog.askstring(self.i18n.t("rename_gallery"), 
                                         self.i18n.t("enter_new_name", name=self.current_gallery_name), 
                                         parent=self)
        if new_name:
            if self.gallery_manager.rename_gallery(self.current_gallery_name, new_name):
                self.current_gallery_name = new_name
                self.gallery_box["values"] = self.gallery_manager.get_gallery_names() + ["➕ New Gallery..."]
                self.gallery_var.set(new_name)
                self.set_status(self.i18n.t("gallery_renamed", name=new_name))
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("gallery_name_exists"))
    
    def delete_gallery(self):
        """Delete current gallery."""
        if not self.current_gallery_name:
            return
        if messagebox.askyesno(self.i18n.t("delete_gallery"), 
                              self.i18n.t("delete_gallery_confirm", name=self.current_gallery_name)):
            if self.gallery_manager.delete_gallery(self.current_gallery_name):
                galleries = self.gallery_manager.get_gallery_names()
                self.gallery_box["values"] = galleries + ["➕ New Gallery..."]
                if galleries:
                    self.current_gallery_name = galleries[0]
                    self.gallery_var.set(galleries[0])
                    self.load_gallery(galleries[0])
                self.set_status(self.i18n.t("gallery_deleted"))
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("cannot_delete_last_gallery"))
    
    def export_gallery(self):
        """Export current gallery."""
        if not self.current_gallery_name:
            return
        folder = filedialog.askdirectory(title=self.i18n.t("select_export_folder"))
        if folder:
            if self.gallery_manager.export_gallery(self.current_gallery_name, folder):
                messagebox.showinfo(self.i18n.t("success"), self.i18n.t("gallery_exported_to", folder=folder))
                self.set_status(self.i18n.t("gallery_exported"))
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_export_gallery"))
    
    def import_gallery(self):
        """Import a gallery."""
        folder = filedialog.askdirectory(title=self.i18n.t("select_gallery_folder"))
        if folder:
            name = simpledialog.askstring(self.i18n.t("import_gallery"), self.i18n.t("enter_gallery_name"), parent=self)
            if name:
                if self.gallery_manager.import_gallery(folder, name):
                    self.gallery_box["values"] = self.gallery_manager.get_gallery_names() + ["➕ New Gallery..."]
                    self.gallery_var.set(name)
                    self.load_gallery(name)
                    messagebox.showinfo(self.i18n.t("success"), self.i18n.t("gallery_imported", name=name))
                    self.set_status(self.i18n.t("gallery_imported_status"))
                else:
                    messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_import_gallery"))
    
    def load_gallery(self, name: str):
        """Load a gallery and refresh character list."""
        self.current_gallery_name = name
        self.current_character = None
        self.current_coa = None
        self.update_tag_autocomplete()
        self.filter_characters()
        self.clear_character_display()
    
    def update_tag_autocomplete(self):
        """Update the autocomplete list based on search type."""
        if not self.current_gallery_name:
            return
        
        if self.current_mode == "character":
            gallery = self.gallery_manager.get_gallery(self.current_gallery_name)
            if not gallery:
                return
            
            if self.search_type_var.get() == "tag":
                # Collect all unique tags
                all_tags = set()
                for char in gallery["characters"]:
                    tags = char.get("tags", [])
                    for tag in tags:
                        if tag.strip():
                            all_tags.add(tag.strip())
                
                # Update combobox values with sorted tags
                tag_list = sorted(list(all_tags))
                self.search_combobox["values"] = tag_list
            else:
                # For name search, show all character names
                names = sorted([char.get("name", "") for char in gallery["characters"]])
                self.search_combobox["values"] = names
        else:
            # CoA mode
            gallery = self.coa_manager.load_gallery(self.current_gallery_name)
            if not gallery:
                return
            
            if self.search_type_var.get() == "tag":
                # Collect all unique tags from CoAs
                all_tags = set()
                for coa in gallery.get("coats_of_arms", []):
                    tags = coa.get("tags", [])
                    for tag in tags:
                        if tag.strip():
                            all_tags.add(tag.strip())
                
                tag_list = sorted(list(all_tags))
                self.search_combobox["values"] = tag_list
            else:
                # For name search, show all CoA names/IDs
                names = sorted([coa.get("id", "") for coa in gallery.get("coats_of_arms", [])])
                self.search_combobox["values"] = names
    
    def clear_search(self):
        """Clear the search box and show all characters."""
        self.search_var.set("")
        self.filter_characters()
    
    def on_search_type_change(self):
        """Handle search type change (name/tag)."""
        # Update autocomplete based on search type
        self.update_tag_autocomplete()
        
        # Clear current search and refilter
        self.search_var.set("")
        self.filter_characters()
    
    def filter_characters(self):
        """Filter and display characters based on search term and search type."""
        if not self.current_gallery_name:
            return
        
        gallery = self.gallery_manager.get_gallery(self.current_gallery_name)
        if not gallery:
            return
        
        self.char_listbox.delete(0, tk.END)
        search_term = self.search_var.get().lower().strip()
        search_type = self.search_type_var.get()
        
        # Get sort preferences
        sort_by = self.app_config.get("sort_by", "name")
        sort_order = self.app_config.get("sort_order", "asc")
        
        # Filter characters
        filtered_chars = []
        
        for char in gallery["characters"]:
            name = char.get("name", "")
            tags = char.get("tags", [])
            
            # If no search term, show all
            if not search_term:
                filtered_chars.append(char)
                continue
            
            # Search based on selected type
            if search_type == "name":
                # Search only in name
                if search_term in name.lower():
                    filtered_chars.append(char)
            else:  # search_type == "tag"
                # Search only in tags
                if any(search_term in tag.lower() for tag in tags):
                    filtered_chars.append(char)
        
        # Sort characters
        filtered_chars = self.sort_characters(filtered_chars, sort_by, sort_order)
        
        # Display sorted characters
        for char in filtered_chars:
            self.char_listbox.insert(tk.END, char.get("name", ""))
    
    def sort_characters(self, characters: list, sort_by: str, sort_order: str) -> list:
        """
        Sort characters based on criteria.
        
        Args:
            characters: List of character dictionaries
            sort_by: Sort criteria ("name", "created", "modified", "tags")
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            Sorted list of characters
        """
        reverse = (sort_order == "desc")
        
        if sort_by == "name":
            return sorted(characters, key=lambda c: c.get("name", "").lower(), reverse=reverse)
        elif sort_by == "created":
            return sorted(characters, key=lambda c: c.get("created", 0), reverse=reverse)
        elif sort_by == "modified":
            return sorted(characters, key=lambda c: c.get("modified", 0), reverse=reverse)
        elif sort_by == "tags":
            return sorted(characters, key=lambda c: len(c.get("tags", [])), reverse=reverse)
        else:
            return characters
    
    # Character Management Methods
    
    def on_character_select(self, event=None):
        """Handle character selection from list."""
        selection = self.char_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        char_name = self.char_listbox.get(idx)
        
        gallery = self.gallery_manager.get_gallery(self.current_gallery_name)
        if gallery:
            for char in gallery["characters"]:
                if char["name"] == char_name:
                    self.current_character = char
                    self.load_character(char)
                    break
    
    def load_character(self, char: dict):
        """Load character data into UI."""
        # Load name
        self.name_var.set(char.get("name", ""))
        
        # Load portrait
        img_path = char.get("image")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img = img.resize((450, 450), Image.Resampling.LANCZOS)
                self.portrait_photo = ImageTk.PhotoImage(img)
                
                if self.portrait_image_id:
                    self.portrait_canvas.delete(self.portrait_image_id)
                self.portrait_image_id = self.portrait_canvas.create_image(225, 225, image=self.portrait_photo)
            except Exception:
                self.clear_portrait()
        else:
            self.clear_portrait()
        
        # Load DNA
        self.dna_text.delete("1.0", tk.END)
        self.dna_text.insert("1.0", char.get("dna", ""))
        
        # Load tags
        self.tags_text.delete("1.0", tk.END)
        tags = char.get("tags", [])
        self.tags_text.insert("1.0", ", ".join(tags))
        
        self.dirty = False
    
    def clear_character_display(self):
        """Clear all character data from UI."""
        self.name_var.set("")
        self.clear_portrait()
        self.dna_text.delete("1.0", tk.END)
        self.tags_text.delete("1.0", tk.END)
        self.dirty = False
    
    def clear_portrait(self):
        """Clear the portrait display."""
        if self.portrait_image_id:
            self.portrait_canvas.delete(self.portrait_image_id)
        self.portrait_image_id = None
        self.portrait_photo = None
    
    def new_character(self):
        """Create a new character."""
        if not self.current_gallery_name:
            messagebox.showwarning(self.i18n.t("warning"), self.i18n.t("select_gallery_first"))
            return
        
        name = simpledialog.askstring(self.i18n.t("new_character"), self.i18n.t("enter_character_name"), parent=self)
        if name:
            logger.info(f"Creating new character: {name} in gallery: {self.current_gallery_name}")
            char_id = self.gallery_manager.add_character(self.current_gallery_name, name)
            if char_id:
                self.update_tag_autocomplete()
                self.filter_characters()
                # Select the new character
                for i in range(self.char_listbox.size()):
                    if self.char_listbox.get(i) == name:
                        self.char_listbox.selection_clear(0, tk.END)
                        self.char_listbox.selection_set(i)
                        self.char_listbox.see(i)
                        self.on_character_select()
                        break
                self.set_status(self.i18n.t("character_created", name=name))
                logger.info(f"Character created successfully: {name} (ID: {char_id})")
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_create_character"))
                logger.error(f"Failed to create character: {name}")
    
    def delete_character(self):
        """Delete current character."""
        if not self.current_character:
            return
        
        name = self.current_character.get("name", "")
        if messagebox.askyesno(self.i18n.t("delete_character"), self.i18n.t("delete_character_confirm", name=name)):
            char_id = self.current_character.get("id")
            logger.info(f"Deleting character: {name} (ID: {char_id}) from gallery: {self.current_gallery_name}")
            if self.gallery_manager.delete_character(self.current_gallery_name, char_id):
                self.update_tag_autocomplete()
                self.filter_characters()
                self.clear_character_display()
                self.current_character = None
                self.set_status(self.i18n.t("character_deleted", name=name))
                logger.info(f"Character deleted successfully: {name}")
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_delete_character"))
                logger.error(f"Failed to delete character: {name}")
    
    def copy_character(self):
        """Duplicate/Copy current character."""
        if not self.current_character:
            messagebox.showwarning(self.i18n.t("warning"), self.i18n.t("select_character_to_copy"))
            return
        
        original_name = self.current_character.get("name", "")
        new_name = simpledialog.askstring(self.i18n.t("copy_character"), 
                                          self.i18n.t("enter_copy_name", name=original_name),
                                          initialvalue=self.i18n.t("copy_name_default", name=original_name),
                                          parent=self)
        
        if not new_name:
            return
        
        # Get current character data
        dna = self.current_character.get("dna", "")
        tags = self.current_character.get("tags", []).copy()
        image_path = self.current_character.get("image")
        
        # Create new character with copied data
        char_id = self.gallery_manager.add_character(
            self.current_gallery_name,
            new_name,
            dna,
            tags,
            image_path
        )
        
        if char_id:
            self.update_tag_autocomplete()
            self.filter_characters()
            # Select the new character
            for i in range(self.char_listbox.size()):
                if self.char_listbox.get(i) == new_name:
                    self.char_listbox.selection_clear(0, tk.END)
                    self.char_listbox.selection_set(i)
                    self.char_listbox.see(i)
                    self.on_character_select()
                    break
            self.set_status(self.i18n.t("character_copied", original=original_name, new=new_name))
        else:
            messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_copy_character"))
    
    def save_character(self):
        """Save current character data."""
        if not self.current_character:
            return
        
        name = self.name_var.get().strip()
        dna = self.dna_text.get("1.0", tk.END).strip()
        tags_str = self.tags_text.get("1.0", tk.END).strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        if not name:
            messagebox.showwarning(self.i18n.t("warning"), self.i18n.t("character_name_empty"))
            logger.warning("Attempted to save character without name")
            return
        
        char_id = self.current_character.get("id")
        logger.info(f"Saving character: {name} (ID: {char_id}) in gallery: {self.current_gallery_name}")
        if self.gallery_manager.update_character(self.current_gallery_name, char_id, name, dna, tags):
            self.current_character["name"] = name
            self.current_character["dna"] = dna
            self.current_character["tags"] = tags
            self.update_tag_autocomplete()  # Actualizar autocompletado con nuevos tags
            self.filter_characters()
            self.dirty = False
            self.set_status(self.i18n.t("character_saved"))
            logger.info(f"Character saved successfully: {name}")
        else:
            messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_save_character"))
            logger.error(f"Failed to save character: {name}")
    
    def on_data_change(self):
        """Mark data as dirty when changed."""
        self.dirty = True
    
    # Portrait Management Methods
    
    def change_portrait(self):
        """Change character portrait from file."""
        if not self.current_character:
            messagebox.showwarning(self.i18n.t("warning"), self.i18n.t("select_character_first"))
            return
        
        file_path = filedialog.askopenfilename(
            title=self.i18n.t("select_portrait_image"),
            filetypes=[(self.i18n.t("image_files"), "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), (self.i18n.t("all_files"), "*.*")]
        )
        
        if file_path:
            self._process_portrait_image(file_path)
    
    def paste_portrait(self):
        """Paste portrait from clipboard."""
        if not self.current_character:
            messagebox.showwarning(self.i18n.t("warning"), self.i18n.t("select_character_first"))
            return
        
        try:
            result = ImageGrab.grabclipboard()
            temp_path = None
            
            if isinstance(result, Image.Image):
                temp_path = os.path.join(self.gallery_manager.data_dir, "temp_clipboard.png")
                result.save(temp_path)
            elif isinstance(result, list) and result:
                file_path = result[0]
                ext = os.path.splitext(file_path)[1].lower()
                if ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
                    temp_path = file_path
            
            if temp_path:
                self._process_portrait_image(temp_path)
                # Clean up temp file
                if temp_path.endswith("temp_clipboard.png"):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            else:
                messagebox.showinfo("Info", "No image found in clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {str(e)}")
    
    def _process_portrait_image(self, image_path: str):
        """Process and save portrait image with cropping."""
        cropper = ImageCropper(self, image_path)
        self.wait_window(cropper)
        
        if cropper.result:
            char_id = self.current_character.get("id")
            char_name = self.current_character.get("name", "")
            
            # Use character name for filename
            safe_name = self.gallery_manager._sanitize_filename(char_name) or char_id
            base_name = safe_name
            counter = 1
            dest_path = os.path.join(self.gallery_manager.images_dir, f"{base_name}.png")
            
            # If file exists and is not the current character's image, append counter
            old_image = self.current_character.get("image")
            while os.path.exists(dest_path) and dest_path != old_image:
                dest_path = os.path.join(self.gallery_manager.images_dir, f"{base_name}_{counter}.png")
                counter += 1
            
            if crop_image(image_path, dest_path, cropper.result, (450, 450)):
                # Remove old image if different
                if old_image and os.path.exists(old_image) and old_image != dest_path:
                    try:
                        os.remove(old_image)
                    except OSError:
                        pass
                
                self.current_character["image"] = dest_path
                self.gallery_manager.save_galleries()
                self.load_character(self.current_character)
                self.set_status(self.i18n.t("portrait_updated"))
            else:
                messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_process_image"))
    
    # DNA Operations
    
    def duplicate_dna_action(self):
        """Duplicate DNA values for consistent inheritance."""
        dna = self.dna_text.get("1.0", tk.END).strip()
        
        if not dna:
            messagebox.showinfo(self.i18n.t("info"), self.i18n.t("no_dna_to_duplicate"))
            return
        
        result = duplicate_dna(dna)
        
        if result.startswith("Error:"):
            messagebox.showerror(self.i18n.t("error"), result)
        else:
            self.dna_text.delete("1.0", tk.END)
            self.dna_text.insert("1.0", result)
            self.dirty = True
            self.set_status(self.i18n.t("dna_duplicated_successfully"))
    
    def validate_dna_action(self):
        """Validate DNA format."""
        dna = self.dna_text.get("1.0", tk.END).strip()
        
        if not dna:
            messagebox.showinfo(self.i18n.t("info"), self.i18n.t("no_dna_to_validate"))
            return
        
        is_valid, error_msg = validate_dna(dna)
        
        if is_valid:
            messagebox.showinfo(self.i18n.t("validation"), self.i18n.t("dna_valid"))
            self.set_status(self.i18n.t("dna_is_valid"))
        else:
            messagebox.showerror(self.i18n.t("validation_error"), f"✗ {error_msg}")
            self.set_status(self.i18n.t("dna_validation_failed"), "#FF0000")
    
    def copy_dna(self):
        """Copy DNA to clipboard."""
        dna = self.dna_text.get("1.0", tk.END).strip()
        
        if not dna:
            messagebox.showinfo(self.i18n.t("info"), self.i18n.t("no_dna_to_copy"))
            return
        
        if copy_to_clipboard(dna):
            self.set_status(self.i18n.t("dna_copied_to_clipboard"))
        else:
            messagebox.showerror(self.i18n.t("error"), self.i18n.t("failed_copy_to_clipboard"))
    
    # Database Management Methods
    
    def create_database(self):
        """Create a new database."""
        existing = [db["name"] for db in self.db_manager.get_database_list()]
        dialog = CreateDatabaseDialog(self, existing)
        self.wait_window(dialog)
        
        if dialog.result:
            if self.db_manager.create_database(**dialog.result):
                messagebox.showinfo("Success", f"Database '{dialog.result['name']}' created successfully!")
                self.set_status(f"Created database: {dialog.result['name']}")
            else:
                messagebox.showerror("Error", "Failed to create database.")
    
    def switch_database(self):
        """Switch to a different database."""
        databases = self.db_manager.get_database_list()
        current_db = self.db_manager.get_current_database(
            "character" if self.current_mode == "character" else "coa"
        )
        
        dialog = SelectDatabaseDialog(self, databases, current_db, 
                                      "character" if self.current_mode == "character" else "coa")
        self.wait_window(dialog)
        
        if dialog.result and dialog.result != current_db:
            logger.info(f"Switching database from '{current_db}' to '{dialog.result}' (mode: {self.current_mode})")
            if self.db_manager.set_current_database(dialog.result, 
                                                     "character" if self.current_mode == "character" else "coa"):
                # Update current database name
                self.current_db_name = dialog.result
                self.app_config.set("current_database_name", dialog.result)
                
                # Reinitialize managers with new database
                db_dir = self.app_config.get("database_directory", "databases")
                self.gallery_manager = GalleryManager(base_dir=db_dir, db_name=dialog.result)
                self.coa_manager = CoAManager(base_dir=db_dir, db_name=dialog.result)
                
                # Reinitialize auto backup manager with new database
                backup_dir = os.path.join(db_dir, "backups")
                auto_backup_enabled = self.app_config.get("auto_backup_enabled", True)
                auto_backup_interval = self.app_config.get("auto_backup_interval", "10min")
                auto_backup_max = self.app_config.get("auto_backup_max_count", 10)
                
                # Stop old backup manager
                if hasattr(self, 'auto_backup_manager'):
                    self.auto_backup_manager.stop()
                
                # Create new backup manager for new database
                backup_source_dir = self.gallery_manager.db_folder
                self.auto_backup_manager = AutoBackupManager(
                    db_directory=backup_source_dir,
                    backup_directory=backup_dir,
                    interval=auto_backup_interval if auto_backup_enabled else "disabled",
                    max_backups=auto_backup_max,
                    db_name=dialog.result
                )
                
                # Start auto backup if enabled
                if auto_backup_enabled:
                    self.auto_backup_manager.start()
                
                # Clear current view
                self.char_listbox.delete(0, tk.END)
                self.clear_character_display()
                self.current_character = None
                self.current_gallery_name = None
                
                # Update window title to show active database
                mode_name = "Character" if self.current_mode == "character" else "CoA"
                self.title(f"CK3 Manager - {mode_name} - Database: {dialog.result}")
                
                # Reload UI with new database
                self.refresh_gallery_list()
                messagebox.showinfo("Success", f"Switched to database '{dialog.result}'")
                self.set_status(f"Active database: {dialog.result}")
                logger.info(f"Database switched successfully to '{dialog.result}'")
            else:
                messagebox.showerror("Error", "Failed to switch database.")
                logger.error(f"Failed to switch database to '{dialog.result}'")
    
    def backup_database(self):
        """Backup the current database with file location selector."""
        # Ask user to select backup location
        from datetime import datetime
        import zipfile
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = self.current_db_name
        # New format: Database_YYYYMMDD_HHMMSS_CK3_Character_App_NombreDB.zip
        default_filename = f"Database_{timestamp}_CK3_Character_App_{db_name}.zip"
        
        backup_path = filedialog.asksaveasfilename(
            title="Select Backup Location",
            defaultextension=".zip",
            initialfile=default_filename,
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if backup_path:
            try:
                # Backup the entire database folder (Database_Default)
                source_dir = self.gallery_manager.db_folder  # databases/Database_Default
                
                # Folder name inside the ZIP (same as filename without .zip)
                zip_folder_name = os.path.basename(backup_path).replace(".zip", "")
                
                # Create zip file
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Calculate relative path from source_dir
                            arcname = os.path.relpath(file_path, source_dir)
                            # Add to ZIP inside the folder structure
                            zipf.write(file_path, os.path.join(zip_folder_name, arcname))
                
                backup_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                messagebox.showinfo("Success", f"Backup created:\n{backup_path}\n\nSize: {backup_size:.2f} MB")
                self.set_status(f"Backup created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create backup:\n{str(e)}")
    
    def manage_databases(self):
        """Open database management dialog."""
        dialog = DatabaseInfoDialog(self, self.db_manager, self.on_database_deleted)
        self.wait_window(dialog)
        
        # Check if user selected a database to switch to
        if dialog.result:
            self.switch_database(dialog.result)
    
    def on_database_deleted(self):
        """Callback when a database is deleted."""
        # Reload current database info
        self.refresh_gallery_list()
    
    def move_items(self):
        """Move items between databases."""
        if self.current_mode == "character":
            # Get all characters from current gallery
            gallery = self.gallery_manager.load_gallery(self.current_gallery_name)
            if not gallery or not gallery.get("characters"):
                messagebox.showinfo("Info", "No characters in current gallery to move.")
                return
            
            items = [char["name"] for char in gallery["characters"]]
        else:
            # Get all CoAs from current gallery
            gallery = self.coa_manager.load_gallery(self.coa_manager.current_gallery)
            if not gallery or not gallery.get("coats_of_arms"):
                messagebox.showinfo("Info", "No coats of arms in current gallery to move.")
                return
            
            items = [coa["id"] for coa in gallery["coats_of_arms"]]
        
        current_db = self.db_manager.get_current_database(
            "character" if self.current_mode == "character" else "coa"
        )
        databases = self.db_manager.get_database_list()
        
        dialog = MoveItemsDialog(self, items, databases, current_db,
                                "character" if self.current_mode == "character" else "coa")
        self.wait_window(dialog)
        
        if dialog.result:
            success_count = 0
            for item in dialog.result["items"]:
                if self.db_manager.move_item(
                    item, current_db, dialog.result["target"],
                    "character" if self.current_mode == "character" else "coa"
                ):
                    success_count += 1
            
            messagebox.showinfo("Success", f"Moved {success_count} item(s) successfully!")
            self.load_gallery(self.current_gallery_name)  # Reload current gallery
            self.set_status(f"Moved {success_count} items")
    
    def switch_mode(self, mode: str):
        """Switch between character and CoA mode."""
        if mode == self.current_mode:
            return
        
        # Check for unsaved changes
        if self.dirty:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before switching modes?"
            )
            if response is None:  # Cancel
                self.view_mode_var.set(self.current_mode)
                return
            elif response:  # Yes
                self.save_character()
        
        self.current_mode = mode
        
        # Update title with database name
        mode_name = "Characters" if mode == "character" else "Coats of Arms"
        self.title(f"CK3 Manager - {mode_name} - Database: {self.current_db_name}")
        
        # Hide/Show DNA panel
        if mode == "coa":
            # Hide DNA editor in CoA mode
            if hasattr(self, 'dna_panel'):
                self.dna_panel.pack_forget()
        else:
            # Show DNA editor in character mode
            if hasattr(self, 'dna_panel'):
                self.dna_panel.pack(side="right", fill="both", expand=True)
        
        # Reload galleries for the current mode
        self.refresh_gallery_list()
        self.set_status(f"Switched to {mode_name} mode")
    
    def refresh_gallery_list(self):
        """Refresh the gallery list based on current mode."""
        if self.current_mode == "character":
            galleries = self.gallery_manager.get_gallery_names()
        else:
            galleries = self.coa_manager.get_gallery_names()
        
        self.gallery_box['values'] = galleries + ["➕ New Gallery..."]
        
        if galleries:
            self.gallery_var.set(galleries[0])
            self.load_gallery(galleries[0])
        else:
            self.char_listbox.delete(0, tk.END)
            self.clear_character_data()
    
    def refresh_current_view(self):
        """Refresh the current gallery view and reload data from database."""
        # Reload data from disk based on current mode
        if self.current_mode == "character":
            self.gallery_manager.reload_from_disk()
            # Rename images to match character names
            self._update_image_names()
        else:
            self.coa_manager.reload_from_disk()
        
        # Refresh the view
        if self.current_gallery_name:
            self.load_gallery(self.current_gallery_name)
            self.set_status(self.i18n.t("view_refreshed"))
        else:
            self.refresh_gallery_list()
            self.set_status(self.i18n.t("view_refreshed"))
    
    def _update_image_names(self):
        """Update image filenames to match character names."""
        try:
            for gallery in self.gallery_manager.galleries:
                for char in gallery.get("characters", []):
                    old_image = char.get("image")
                    if old_image and os.path.exists(old_image):
                        # Check if image has UUID name
                        old_filename = os.path.basename(old_image)
                        if len(old_filename) == 40:  # UUID format (36 chars + .png = 40)
                            # Generate new name based on character name
                            char_name = char.get("name", "")
                            if char_name:
                                safe_name = self.gallery_manager._sanitize_filename(char_name)
                                base_name = safe_name
                                counter = 1
                                new_image_path = os.path.join(self.gallery_manager.images_dir, f"{base_name}.png")
                                
                                # Find available filename
                                while os.path.exists(new_image_path) and new_image_path != old_image:
                                    new_image_path = os.path.join(self.gallery_manager.images_dir, f"{base_name}_{counter}.png")
                                    counter += 1
                                
                                # Rename file
                                if new_image_path != old_image:
                                    try:
                                        os.rename(old_image, new_image_path)
                                        char["image"] = new_image_path
                                    except OSError as e:
                                        logger.warning(f"Failed to rename {old_image}: {e}")
            
            # Save updated galleries
            self.gallery_manager.save_galleries()
        except Exception as e:
            logger.error(f"Error updating image names: {e}")
    
    def edit_character(self):
        """Edit the currently selected character/CoA."""
        selection = self.char_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select an item to edit.")
            return
        
        # Focus on the name entry field
        self.name_entry.focus_set()
        self.name_entry.select_range(0, tk.END)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts help."""
        shortcuts = """
Keyboard Shortcuts:

Ctrl+S - Save current character/CoA
Ctrl+N - Create new character/CoA
Ctrl+C - Copy character/CoA
Ctrl+D - Duplicate DNA (Character mode only)
Ctrl+V - Paste portrait from clipboard
Ctrl+F - Focus search box
Delete - Delete selected character/CoA
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_settings(self):
        """Show settings dialog."""
        from ui.settings_dialog import SettingsDialog
        SettingsDialog(self, self.app_config, self.auto_backup_manager, self.i18n)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
CK3 Character & CoA Manager
Version 2.0

A unified tool for managing Crusader Kings III characters and coats of arms.

Features:
• Character DNA management with duplication
• Coat of Arms gallery system
• Multiple database support
• Import/Export capabilities
• Cross-database item movement
• Multi-language support

Created for the CK3 modding community.
        """
        messagebox.showinfo("About", about_text)
    
    def show_credits(self):
        """Show credits dialog with links."""
        dialog = CreditsDialog(self)
        self.wait_window(dialog)
    
    def change_language(self, lang_code: str):
        """
        Change application language.
        
        Args:
            lang_code: Language code (e.g., 'en', 'es')
        """
        if self.i18n.set_language(lang_code):
            self.app_config.set("language", lang_code)
            self.current_lang_var.set(lang_code)
            logger.info(f"Language changed to: {lang_code}")
            
            # Ask user if they want to restart now
            response = messagebox.askyesno(
                "Language Changed / Idioma Cambiado",
                "Language preference saved. Restart application now?\n\n"
                "Idioma guardado. ¿Reiniciar la aplicación ahora?",
                icon='question'
            )
            
            if response:
                # Restart application
                self.restart_application()
    
    def restart_application(self):
        """Restart the application."""
        logger.info("Restarting application...")
        
        # Save current state
        self.app_config.save()
        
        # Close current window
        self.destroy()
        
        # Restart using subprocess
        subprocess.Popen([sys.executable] + sys.argv)
        
        # Exit current process
        sys.exit(0)
    
    def change_theme(self, theme_name: str):
        """
        Change application theme.
        
        Args:
            theme_name: Theme name ("dark" or "light")
        """
        if self.theme_manager.set_theme(theme_name):
            self.app_config.set("theme", theme_name)
            self.theme_var.set(theme_name)
            logger.info(f"Theme changed to: {theme_name}")
            
            # Ask user if they want to restart now
            response = messagebox.askyesno(
                self.i18n.t("theme_changed"),
                self.i18n.t("theme_changed_restart"),
                icon='question'
            )
            
            if response:
                # Restart application
                self.restart_application()
    
    def show_statistics(self):
        """Show gallery statistics dialog."""
        from ui.statistics_dialog import StatisticsDialog
        StatisticsDialog(self, self.gallery_manager, self.current_gallery_name, self.i18n)
    
    def compare_characters(self):
        """Show character comparison dialog."""
        if not self.current_gallery_name:
            messagebox.showwarning(
                self.i18n.t("warning"),
                self.i18n.t("select_gallery_first")
            )
            return
        
        from ui.compare_dialog import CompareCharactersDialog
        CompareCharactersDialog(self, self.gallery_manager, self.current_gallery_name, self.i18n)


def main():
    """Main entry point."""
    app = CK3CharacterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
