#!/usr/bin/env python3
"""
Settings Dialog
Application settings and preferences.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os


class SettingsDialog(tk.Toplevel):
    """Dialog for application settings."""
    
    def __init__(self, parent, app_config, auto_backup_manager, i18n):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent window
            app_config: ConfigManager instance
            auto_backup_manager: AutoBackupManager instance
            i18n: Internationalization instance
        """
        super().__init__(parent)
        
        self.app_config = app_config
        self.auto_backup_manager = auto_backup_manager
        self.i18n = i18n
        self.parent = parent
        
        self.title(self.i18n.t("settings_title"))
        self.geometry("600x500")
        self.configure(bg="#2e2e2e")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        # Main container
        main_frame = tk.Frame(self, bg="#2e2e2e", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=self.i18n.t("settings_title"),
            font=("Arial", 16, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # General tab
        general_tab = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(general_tab, text=self.i18n.t("settings_tab_general"))
        self.setup_general_tab(general_tab)
        
        # Backup tab
        backup_tab = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(backup_tab, text=self.i18n.t("settings_tab_backup"))
        self.setup_backup_tab(backup_tab)
        
        # Sorting tab
        sorting_tab = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(sorting_tab, text=self.i18n.t("settings_tab_sorting"))
        self.setup_sorting_tab(sorting_tab)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2e2e2e")
        btn_frame.pack(pady=(15, 0))
        
        ttk.Button(
            btn_frame,
            text=self.i18n.t("settings_save"),
            command=self.save_settings,
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text=self.i18n.t("settings_cancel"),
            command=self.destroy,
            width=15
        ).pack(side="left", padx=5)
    
    def setup_general_tab(self, parent):
        """Setup general settings tab."""
        container = tk.Frame(parent, bg="#2e2e2e", padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Database directory
        tk.Label(
            container,
            text=self.i18n.t("settings_database_directory"),
            font=("Arial", 11, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        ).pack(anchor="w", pady=(0, 5))
        
        dir_frame = tk.Frame(container, bg="#2e2e2e")
        dir_frame.pack(fill="x", pady=(0, 15))
        
        self.db_dir_var = tk.StringVar()
        tk.Entry(
            dir_frame,
            textvariable=self.db_dir_var,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#eeeeee",
            insertbackground="white",
            state="readonly"
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(
            dir_frame,
            text=self.i18n.t("settings_browse"),
            command=self.browse_db_directory,
            width=10
        ).pack(side="right")
        
        # Theme
        tk.Label(
            container,
            text=self.i18n.t("settings_theme"),
            font=("Arial", 11, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        ).pack(anchor="w", pady=(0, 5))
        
        self.theme_var = tk.StringVar()
        theme_frame = tk.Frame(container, bg="#2e2e2e")
        theme_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Radiobutton(
            theme_frame,
            text=self.i18n.t("menu_view_theme_dark"),
            variable=self.theme_var,
            value="dark"
        ).pack(side="left", padx=(0, 15))
        
        ttk.Radiobutton(
            theme_frame,
            text=self.i18n.t("menu_view_theme_light"),
            variable=self.theme_var,
            value="light"
        ).pack(side="left")
    
    def setup_backup_tab(self, parent):
        """Setup backup settings tab."""
        container = tk.Frame(parent, bg="#2e2e2e", padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Auto backup enabled
        self.auto_backup_var = tk.BooleanVar()
        tk.Checkbutton(
            container,
            text=self.i18n.t("settings_auto_backup_enabled"),
            variable=self.auto_backup_var,
            font=("Arial", 11, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee",
            selectcolor="#1e1e1e",
            activebackground="#2e2e2e",
            activeforeground="#eeeeee",
            command=self.toggle_backup_options
        ).pack(anchor="w", pady=(0, 15))
        
        # Backup interval
        interval_frame = tk.Frame(container, bg="#2e2e2e")
        interval_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            interval_frame,
            text=self.i18n.t("settings_backup_interval"),
            font=("Arial", 10),
            bg="#2e2e2e",
            fg="#cccccc"
        ).pack(side="left", padx=(0, 10))
        
        self.interval_var = tk.StringVar()
        self.interval_combo = ttk.Combobox(
            interval_frame,
            textvariable=self.interval_var,
            state="readonly",
            width=15,
            values=["1min", "5min", "10min", "30min"]
        )
        self.interval_combo.pack(side="left")
        
        # Max backups
        max_frame = tk.Frame(container, bg="#2e2e2e")
        max_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            max_frame,
            text=self.i18n.t("settings_max_backups"),
            font=("Arial", 10),
            bg="#2e2e2e",
            fg="#cccccc"
        ).pack(side="left", padx=(0, 10))
        
        self.max_backups_var = tk.IntVar()
        tk.Spinbox(
            max_frame,
            from_=5,
            to=50,
            textvariable=self.max_backups_var,
            width=10,
            font=("Arial", 10),
            bg="#1e1e1e",
            fg="#eeeeee",
            insertbackground="white",
            buttonbackground="#2e2e2e"
        ).pack(side="left")
        
        # Backup info
        info_frame = tk.Frame(container, bg="#1e1e1e", relief="ridge", borderwidth=1)
        info_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        tk.Label(
            info_frame,
            text=self.i18n.t("settings_backup_info"),
            font=("Arial", 9),
            bg="#1e1e1e",
            fg="#cccccc",
            justify="left",
            anchor="w",
            wraplength=500
        ).pack(padx=15, pady=15)
    
    def setup_sorting_tab(self, parent):
        """Setup sorting settings tab."""
        container = tk.Frame(parent, bg="#2e2e2e", padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Sort by
        tk.Label(
            container,
            text=self.i18n.t("settings_sort_by"),
            font=("Arial", 11, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        ).pack(anchor="w", pady=(0, 10))
        
        self.sort_by_var = tk.StringVar()
        
        sort_options = [
            ("name", self.i18n.t("settings_sort_name")),
            ("created", self.i18n.t("settings_sort_created")),
            ("modified", self.i18n.t("settings_sort_modified")),
            ("tags", self.i18n.t("settings_sort_tags"))
        ]
        
        for value, label in sort_options:
            ttk.Radiobutton(
                container,
                text=label,
                variable=self.sort_by_var,
                value=value
            ).pack(anchor="w", pady=2)
        
        # Sort order
        tk.Label(
            container,
            text=self.i18n.t("settings_sort_order"),
            font=("Arial", 11, "bold"),
            bg="#2e2e2e",
            fg="#eeeeee"
        ).pack(anchor="w", pady=(20, 10))
        
        self.sort_order_var = tk.StringVar()
        
        ttk.Radiobutton(
            container,
            text=self.i18n.t("settings_sort_ascending"),
            variable=self.sort_order_var,
            value="asc"
        ).pack(anchor="w", pady=2)
        
        ttk.Radiobutton(
            container,
            text=self.i18n.t("settings_sort_descending"),
            variable=self.sort_order_var,
            value="desc"
        ).pack(anchor="w", pady=2)
    
    def load_settings(self):
        """Load current settings."""
        # General
        self.db_dir_var.set(self.app_config.get("database_directory", ""))
        self.theme_var.set(self.app_config.get("theme", "dark"))
        
        # Backup
        self.auto_backup_var.set(self.app_config.get("auto_backup_enabled", True))
        self.interval_var.set(self.app_config.get("auto_backup_interval", "10min"))
        self.max_backups_var.set(self.app_config.get("auto_backup_max_count", 10))
        
        # Sorting
        self.sort_by_var.set(self.app_config.get("sort_by", "name"))
        self.sort_order_var.set(self.app_config.get("sort_order", "asc"))
        
        self.toggle_backup_options()
    
    def toggle_backup_options(self):
        """Enable/disable backup options based on checkbox."""
        state = "normal" if self.auto_backup_var.get() else "disabled"
        self.interval_combo.config(state="readonly" if state == "normal" else "disabled")
    
    def browse_db_directory(self):
        """Browse for database directory."""
        directory = filedialog.askdirectory(
            title=self.i18n.t("settings_select_db_directory"),
            initialdir=self.db_dir_var.get()
        )
        
        if directory:
            self.db_dir_var.set(directory)
    
    def save_settings(self):
        """Save settings and close dialog."""
        # Check if any settings changed that require restart
        restart_needed = False
        
        # Check theme change
        if self.theme_var.get() != self.app_config.get("theme"):
            restart_needed = True
        
        # Check database directory change
        if self.db_dir_var.get() != self.app_config.get("database_directory"):
            restart_needed = True
        
        # Save all settings
        self.app_config.set("database_directory", self.db_dir_var.get())
        self.app_config.set("theme", self.theme_var.get())
        self.app_config.set("auto_backup_enabled", self.auto_backup_var.get())
        self.app_config.set("auto_backup_interval", self.interval_var.get())
        self.app_config.set("auto_backup_max_count", self.max_backups_var.get())
        self.app_config.set("sort_by", self.sort_by_var.get())
        self.app_config.set("sort_order", self.sort_order_var.get())
        self.app_config.save()
        
        # Update auto backup settings
        if self.auto_backup_var.get():
            self.auto_backup_manager.max_backups = self.max_backups_var.get()
            self.auto_backup_manager.set_interval(self.interval_var.get())
            if not self.auto_backup_manager.is_running:
                self.auto_backup_manager.start()
        else:
            self.auto_backup_manager.stop()
        
        # Show restart message if needed
        if restart_needed:
            response = messagebox.askyesno(
                self.i18n.t("settings_saved"),
                self.i18n.t("settings_restart_required"),
                icon='question'
            )
            
            if response:
                self.destroy()
                self.parent.restart_application()
            else:
                self.destroy()
        else:
            messagebox.showinfo(
                self.i18n.t("settings_saved"),
                self.i18n.t("settings_saved_message")
            )
            self.destroy()
