"""
Database Management Dialogs
UI dialogs for managing databases, moving characters, and backups.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Callable


class CreateDatabaseDialog(tk.Toplevel):
    """Dialog for creating a new database."""
    
    def __init__(self, parent, existing_names: List[str]):
        super().__init__(parent)
        
        self.result = None
        self.existing_names = existing_names
        
        self.title("Create New Database")
        self.geometry("450x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup UI components."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Name
        ttk.Label(main_frame, text="Database Name:").pack(anchor="w", pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.focus()
        
        # Type
        ttk.Label(main_frame, text="Database Type:").pack(anchor="w", pady=(0, 5))
        self.type_var = tk.StringVar(value="both")
        
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Radiobutton(type_frame, text="Both (Characters & CoAs)", 
                       variable=self.type_var, value="both").pack(anchor="w")
        ttk.Radiobutton(type_frame, text="Characters Only", 
                       variable=self.type_var, value="character").pack(anchor="w")
        ttk.Radiobutton(type_frame, text="Coats of Arms Only", 
                       variable=self.type_var, value="coa").pack(anchor="w")
        
        # Description
        ttk.Label(main_frame, text="Description (optional):").pack(anchor="w", pady=(0, 5))
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=40)
        desc_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Create", command=self.on_create).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")
        
        self.bind('<Return>', lambda e: self.on_create())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def on_create(self):
        """Handle create button."""
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a database name.", parent=self)
            return
        
        if name in self.existing_names:
            messagebox.showerror("Error", "A database with this name already exists.", parent=self)
            return
        
        # Validate name (alphanumeric and underscores only)
        if not name.replace('_', '').replace('-', '').isalnum():
            messagebox.showerror("Error", "Database name can only contain letters, numbers, hyphens, and underscores.", parent=self)
            return
        
        self.result = {
            "name": name,
            "type": self.type_var.get(),
            "description": self.desc_var.get().strip()
        }
        
        self.destroy()


class SelectDatabaseDialog(tk.Toplevel):
    """Dialog for selecting a database."""
    
    def __init__(self, parent, databases: List[dict], current_db: str, db_type: str = "character"):
        super().__init__(parent)
        
        self.result = None
        self.databases = databases
        self.current_db = current_db
        self.db_type = db_type
        
        type_name = "Character" if db_type == "character" else "CoA"
        self.title(f"Select {type_name} Database")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup UI components."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Info label
        ttk.Label(main_frame, text=f"Select a database (Current: {self.current_db}):").pack(anchor="w", pady=(0, 10))
        
        # Database list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.db_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=12)
        self.db_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.db_listbox.yview)
        
        # Populate list
        for db in self.databases:
            # Skip backups folder and backup entries (format: YYYYMMDD_HHMMSS_*)
            db_name = db["name"]
            if db_name.lower() == "backups" or "backup" in db_name.lower():
                continue
            # Skip backup database entries (date pattern at start)
            if len(db_name) > 8 and db_name[8] == '_' and db_name[:8].isdigit():
                continue
            
            # Filter by type
            if self.db_type == "character" and db["type"] not in ["both", "character"]:
                continue
            if self.db_type == "coa" and db["type"] not in ["both", "coa"]:
                continue
            
            display = f"{db['name']} ({db['type']})"
            if db.get("description"):
                display += f" - {db['description']}"
            
            self.db_listbox.insert("end", display)
            
            if db["name"] == self.current_db:
                self.db_listbox.selection_set("end")
                self.db_listbox.see("end")
        
        self.db_listbox.bind('<Double-Button-1>', lambda e: self.on_select())
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Browse...", command=self.browse_folder).pack(side="left")
        ttk.Button(btn_frame, text="Select", command=self.on_select).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")
        
        self.bind('<Return>', lambda e: self.on_select())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def browse_folder(self):
        """Browse for a database folder."""
        folder = filedialog.askdirectory(
            parent=self,
            title="Select Database Folder",
            mustexist=True
        )
        
        if folder:
            # Extract folder name from path
            folder_name = os.path.basename(folder)
            
            # Check if it's the backups folder
            if folder_name.lower() == "backups" or "backup" in folder_name.lower():
                messagebox.showwarning(
                    "Invalid Selection",
                    "Cannot use the backups folder as a database.",
                    parent=self
                )
                return
            
            # Extract database name from folder name (remove "Database_" prefix if present)
            if folder_name.startswith("Database_"):
                db_name = folder_name[9:]  # Remove "Database_" (9 characters)
            else:
                db_name = folder_name
            
            self.result = db_name
            self.destroy()
    
    def on_select(self):
        """Handle select button."""
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database.", parent=self)
            return
        
        selected_text = self.db_listbox.get(selection[0])
        db_name = selected_text.split(" (")[0]
        
        self.result = db_name
        self.destroy()


class MoveItemsDialog(tk.Toplevel):
    """Dialog for moving items between databases."""
    
    def __init__(self, parent, items: List[str], databases: List[dict], 
                 current_db: str, item_type: str = "character"):
        super().__init__(parent)
        
        self.result = None
        self.items = items
        self.databases = databases
        self.current_db = current_db
        self.item_type = item_type
        
        type_name = "Characters" if item_type == "character" else "Coats of Arms"
        self.title(f"Move {type_name}")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup UI components."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Info
        info_text = f"Move selected items from '{self.current_db}' to another database:"
        ttk.Label(main_frame, text=info_text).pack(anchor="w", pady=(0, 10))
        
        # Two-column layout
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Left: Items to move
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Select items to move:").pack(anchor="w", pady=(0, 5))
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.items_listbox = tk.Listbox(list_frame, selectmode="multiple", yscrollcommand=scrollbar.set)
        self.items_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.items_listbox.yview)
        
        for item in self.items:
            self.items_listbox.insert("end", item)
        
        # Select all button
        ttk.Button(left_frame, text="Select All", command=self.select_all).pack(fill="x", pady=(5, 0))
        
        # Right: Target database
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="left", fill="both", expand=True)
        
        ttk.Label(right_frame, text="Destination database:").pack(anchor="w", pady=(0, 5))
        
        # Filter databases by type
        valid_databases = []
        for db in self.databases:
            # Skip backups folder and backup entries (format: YYYYMMDD_HHMMSS_*)
            db_name = db["name"]
            if db_name.lower() == "backups" or "backup" in db_name.lower():
                continue
            # Skip backup database entries (date pattern at start)
            if len(db_name) > 8 and db_name[8] == '_' and db_name[:8].isdigit():
                continue
            
            if db["name"] == self.current_db:
                continue
            if self.item_type == "character" and db["type"] not in ["both", "character"]:
                continue
            if self.item_type == "coa" and db["type"] not in ["both", "coa"]:
                continue
            valid_databases.append(db["name"])
        
        self.target_var = tk.StringVar()
        if valid_databases:
            self.target_var.set(valid_databases[0])
        
        target_combo = ttk.Combobox(right_frame, textvariable=self.target_var, 
                                    values=valid_databases, state="readonly")
        target_combo.pack(fill="x")
        
        # Info about target
        info_frame = ttk.LabelFrame(right_frame, text="Target Database Info", padding=10)
        info_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="", justify="left")
        self.info_label.pack(fill="both", expand=True)
        
        self.target_var.trace_add("write", lambda *args: self.update_info())
        self.update_info()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Move", command=self.on_move).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")
        
        self.bind('<Escape>', lambda e: self.destroy())
    
    def select_all(self):
        """Select all items."""
        self.items_listbox.selection_set(0, "end")
    
    def update_info(self):
        """Update target database info."""
        target = self.target_var.get()
        if not target:
            self.info_label.config(text="No databases available")
            return
        
        for db in self.databases:
            if db["name"] == target:
                info_text = f"Type: {db['type']}\n"
                if db.get("description"):
                    info_text += f"Description: {db['description']}\n"
                info_text += f"Created: {db.get('created', 'Unknown')}"
                self.info_label.config(text=info_text)
                break
    
    def on_move(self):
        """Handle move button."""
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select at least one item to move.", parent=self)
            return
        
        target = self.target_var.get()
        if not target:
            messagebox.showerror("Error", "No target database available.", parent=self)
            return
        
        selected_items = [self.items[i] for i in selection]
        
        confirm = messagebox.askyesno(
            "Confirm Move",
            f"Move {len(selected_items)} item(s) from '{self.current_db}' to '{target}'?\n\n"
            "This action cannot be undone.",
            parent=self
        )
        
        if confirm:
            self.result = {
                "items": selected_items,
                "target": target
            }
            self.destroy()


class DatabaseInfoDialog(tk.Toplevel):
    """Dialog showing database information and management options."""
    
    def __init__(self, parent, db_manager, on_delete_callback: Callable = None, on_switch_callback: Callable = None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.on_delete_callback = on_delete_callback
        self.on_switch_callback = on_switch_callback
        self.result = None
        
        self.title("Database Management")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup UI components."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="Database Management", 
                 font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Database list with info
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Treeview for databases
        columns = ("Type", "Characters", "CoAs", "Created")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=12)
        
        self.tree.heading("#0", text="Database Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Characters", text="Characters")
        self.tree.heading("CoAs", text="CoAs")
        self.tree.heading("Created", text="Created")
        
        self.tree.column("#0", width=150)
        self.tree.column("Type", width=120)
        self.tree.column("Characters", width=100)
        self.tree.column("CoAs", width=100)
        self.tree.column("Created", width=180)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to switch database
        self.tree.bind('<Double-Button-1>', lambda e: self.switch_database())
        
        # Populate tree
        self.refresh_list()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Switch To", command=self.switch_database).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Backup Selected", command=self.backup_selected).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side="left")
        
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side="right")
        
        self.bind('<Escape>', lambda e: self.destroy())
    
    def refresh_list(self):
        """Refresh database list."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get databases
        databases = self.db_manager.get_database_list()
        
        for db in databases:
            # Skip backups folder and backup entries (format: YYYYMMDD_HHMMSS_*)
            db_name = db["name"]
            if db_name.lower() == "backups" or "backup" in db_name.lower():
                continue
            # Skip backup database entries (date pattern at start)
            if len(db_name) > 8 and db_name[8] == '_' and db_name[:8].isdigit():
                continue
            
            stats = self.db_manager.get_database_stats(db["name"])
            
            created_date = db.get("created", "")
            if created_date:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_date)
                    created_date = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            # Highlight current database (check both character and coa)
            is_current = (db["name"] == self.db_manager.config.get("current_character_db") or 
                         db["name"] == self.db_manager.config.get("current_coa_db"))
            item_id = self.tree.insert("", "end", text=db["name"], values=(
                db["type"],
                stats["character_count"],
                stats["coa_count"],
                created_date
            ))
            
            if is_current:
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
    
    def switch_database(self):
        """Switch to selected database."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to switch to.", parent=self)
            return
        
        db_name = self.tree.item(selection[0])["text"]
        
        # Check if already active (for either character or coa)
        current_char = self.db_manager.config.get("current_character_db")
        current_coa = self.db_manager.config.get("current_coa_db")
        
        if db_name == current_char and db_name == current_coa:
            messagebox.showinfo("Already Active", f"Database '{db_name}' is already active for both characters and CoAs.", parent=self)
            return
        
        self.result = db_name
        self.destroy()
    
    def backup_selected(self):
        """Backup selected database."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to backup.", parent=self)
            return
        
        db_name = self.tree.item(selection[0])["text"]
        
        backup_path = self.db_manager.backup_database(db_name)
        
        if backup_path:
            messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}", parent=self)
        else:
            messagebox.showerror("Error", "Failed to create backup.", parent=self)
    
    def delete_selected(self):
        """Delete selected database."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to delete.", parent=self)
            return
        
        db_name = self.tree.item(selection[0])["text"]
        
        if db_name == "Default":
            messagebox.showerror("Error", "Cannot delete the default database.", parent=self)
            return
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete database '{db_name}'?\n\n"
            "This will permanently delete all data and cannot be undone.",
            parent=self
        )
        
        if confirm:
            if self.db_manager.delete_database(db_name):
                messagebox.showinfo("Success", f"Database '{db_name}' deleted.", parent=self)
                self.refresh_list()
                if self.on_delete_callback:
                    self.on_delete_callback()
            else:
                messagebox.showerror("Error", "Failed to delete database.", parent=self)
