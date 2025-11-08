# CK3 Character & CoA Manager

<div align="center">

![CK3 Manager](https://img.shields.io/badge/CK3-Character_&_CoA_Manager-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Unified Manager for Characters & Coats of Arms in Crusader Kings III**

</div>

---

## 🎯 Overview

CK3 Character & CoA Manager is a comprehensive desktop application that manages both character galleries and coat of arms collections for Crusader Kings III. Features multiple database support, DNA duplication, cross-database operations, and multi-language support.

### ✨ Key Features

#### 🗄️ **Multiple Database System**

- Create and manage multiple databases (characters, CoAs, or both)
- Switch between databases on the fly
- Backup databases with timestamp
- Move characters/CoAs between databases
- Database statistics and management dialog

#### 📁 **Character Gallery Management**

- Create and manage multiple galleries (e.g., Male, Female, Historical)
- Add, edit, copy, and delete character entries
- Tag-based organization and search
- Import/Export galleries for sharing
- Portrait management with crop and zoom tools

#### 🛡️ **Coat of Arms (CoA) Management**

- Dedicated CoA mode with gallery system
- Parse and store CK3 coat of arms codes
- Tag-based organization for CoAs
- Import/Export CoA collections
- Automatic mode switching

#### 🧬 **DNA Duplicator** (Character Mode)

- Duplicate DNA values for consistent character inheritance
- Validate DNA format
- Quick copy to clipboard
- Integrated with character gallery

#### 🎨 **Portrait Management**

- Drag-to-reposition and scroll-to-zoom crop tool
- Paste directly from clipboard (Ctrl+V)
- Support for multiple image formats (PNG, JPG, BMP, GIF, WEBP)

#### ⌨️ **Keyboard Shortcuts**

- `Ctrl+S`: Save current character/CoA
- `Ctrl+N`: New character/CoA
- `Ctrl+C`: Copy character/CoA
- `Ctrl+D`: Duplicate DNA (Character mode only)
- `Ctrl+V`: Paste portrait from clipboard
- `Ctrl+F`: Focus search box
- `Delete`: Delete selected item

#### 🌐 **Multi-Language Support**

- English (English)
- Spanish (Español)
- Chinese (中文) - AI-translated\*
- Japanese (日本語) - AI-translated\*
- Korean (한국어) - AI-translated\*
- French (Français) - AI-translated\*
- Portuguese (Português) - AI-translated\*
- German (Deutsch) - AI-translated\*
- Italian (Italiano) - AI-translated\*
- Russian (Русский) - AI-translated\*
- Ukrainian (Українська) - AI-translated\*
- Arabic (العربية) - AI-translated\*

_\*Non-English/Spanish translations were generated using AI assistance. Native speakers are welcome to contribute improvements via pull requests._

---

## 📥 Installation

### Option 1: Run from Source

1. **Requirements**:

   - Python 3.10 or higher
   - pip (Python package manager)

2. **Clone or download** this repository

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Option 2: Use Compiled Executable (Recommended)

1. Download the latest `.exe` from the releases page
2. Double-click to run (no installation needed)
3. **Note**: Windows may show a warning on first run. Click "More info" → "Run anyway"

---

## 🔨 Building Executable

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name "CK3 Character Manager" ^
            --onefile ^
            --windowed ^
            --add-data "assets;assets" ^
            --icon=assets/icon.ico ^
            main.py
```

The executable will be created in the `dist/` folder.

### Using Nuitka (Alternative - Better Performance)

```bash
# Install Nuitka
pip install nuitka

# Build executable
python -m nuitka --standalone ^
                 --onefile ^
                 --windows-disable-console ^
                 --output-filename="CK3-Character-Manager.exe" ^
                 --windows-icon-from-ico=assets/icon.ico ^
                 main.py
```

---

## 📖 Usage Guide

### Creating a Character

1. Click **"➕ New"** in the left panel
2. Enter character name
3. Add portrait image (click portrait area or use "📁 Change Portrait")
4. Paste or type DNA in the right panel
5. Add tags (optional, comma-separated)
6. Click **"💾 Save"** or press `Ctrl+S`

### Duplicating DNA

DNA in CK3 has two values for each gene. When you customize a character, children may inherit from either your edited version or the original base DNA, leading to inconsistent appearance.

**Solution**: Use the DNA Duplicator!

1. Paste DNA into the editor
2. Click **"🧬 Duplicate DNA"** or press `Ctrl+D`
3. The tool copies the first value to the second value
4. Children will now consistently inherit your customizations

**Example**:

```
Before: height_gene = { "tall" 5 "short" 2 }
After:  height_gene = { "tall" 5 "tall" 5 }
```

### Organizing with Galleries

- Create different galleries for organization (e.g., "Nobles", "Commoners", "Historical")
- Use the **⋮ menu** to rename, delete, import, or export galleries
- Export galleries to share with friends

### Managing Databases

Access the **Database** menu for advanced operations:

- **Create New Database**: Organize your characters and CoAs into separate databases
- **Switch Database**: Change to a different database instantly
- **Backup Database**: Create timestamped backups of your current database
- **Manage Databases**: View statistics and delete unused databases
- **Move Items**: Transfer characters or CoAs between databases

### Switching Between Character and CoA Mode

Use the **View** menu to toggle modes:

- **Character Mode**: Full DNA editor, portrait management, character galleries
- **CoA Mode**: CoA code editor, coat of arms galleries (DNA editor hidden)

### Working with Coats of Arms

1. Switch to **View > Coat of Arms Mode**
2. Click **"➕ New"** to create a new CoA entry
3. Paste your CK3 coat of arms code
4. Add tags for organization (e.g., "dynasty", "kingdom", "custom")
5. Optionally add an image of the rendered CoA
6. Click **"💾 Save"**

### Searching Characters

- **By Name**: Search characters by their name
- **By Tag**: Filter by tags (use the radio buttons to switch)
- Type in the search box with autocomplete suggestions
- Click **"✕ Clear"** to reset filters

---

## 📂 Project Structure

```
CK3-Character-App/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
├── README.md                    # This file
├── src/
│   ├── core/                    # Core functionality
│   │   ├── dna_duplicator.py    # DNA duplication logic
│   │   ├── gallery_manager.py   # Character gallery management
│   │   ├── coa_manager.py       # CoA gallery management
│   │   └── database_manager.py  # Multi-database system
│   ├── ui/                      # User interface
│   │   ├── main_window.py       # Main application window
│   │   ├── image_cropper.py     # Image crop dialog
│   │   └── database_dialogs.py  # Database management dialogs
│   └── utils/                   # Utility functions
│       └── clipboard.py         # Clipboard operations
├── assets/                      # Icons and resources
├── build/                       # Build scripts and configs
└── databases/                   # Application data (auto-created)
    ├── db_config.json           # Database configuration
    ├── default/                 # Default database
    │   ├── character_data/      # Character galleries
    │   ├── portraits/           # Character portraits
    │   ├── coa_data/            # CoA galleries
    │   └── coa_images/          # CoA images
    └── backups/                 # Database backups
```

---

## 🎮 Data Storage

- **Location**: `databases/` folder (created automatically)
- **Database config**: Stored in `db_config.json`
- **Multiple databases**: Each database has its own folder structure
- **Character data**: Stored in `<database>/character_data/` as JSON files
- **Character portraits**: Stored in `<database>/portraits/` as PNG files
- **CoA data**: Stored in `<database>/coa_data/` as JSON files
- **CoA images**: Stored in `<database>/coa_images/` as PNG files
- **Backups**: Created in `databases/backups/` as ZIP files with timestamps
- **Export**: Use gallery export to share specific collections

---

## 🔧 Troubleshooting

### "Failed to copy to clipboard"

- **Windows**: Built-in support, should work automatically
- **Linux**: Install `xclip` or `xsel`
  ```bash
  sudo apt install xclip
  ```

```

- **macOS**: Built-in support via `pbcopy`

### "Failed to paste from clipboard"

- Make sure you have an image copied (screenshot tool, snipping tool, etc.)
- Supported formats: PNG, JPG, BMP, GIF, WEBP

### "Cannot delete the last gallery"

- You must have at least one gallery
- Create a new gallery before deleting the last one

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

This application combines, extends, and unifies features from two excellent tools:

### Original Projects

- **[CK3-Character-Gallery](https://github.com/huangfanglong/CK3-Character-Gallery)** by [huangfanglong](https://github.com/huangfanglong)

  - Character gallery management system
  - Portrait handling and organization
  - [Reddit Post](https://www.reddit.com/r/CKTinder/comments/1offc3u/ck3_local_character_warehouse/)

- **[CK3-DNA-Duplicator](https://github.com/Deticaru/CK3-DNA-Duplicator)** by [Deticaru](https://github.com/Deticaru)
  - DNA duplication functionality
  - DNA validation system
  - [Reddit Post](https://www.reddit.com/r/CKTinder/comments/1ob8yzr/for_dna_enthusiasts/)

### This Project

**Developed by [Alfarojo](https://github.com/Alfarojo25)**

- **Unified Application**: Combined both tools into a single, cohesive application
- **Multiple Database System**: Added support for managing multiple databases
- **Coat of Arms Support**: Extended functionality to include CoA management
- **Cross-Database Operations**: Implemented item movement between databases
- **Enhanced UI/UX**: Reorganized interface with menu system and improved workflows
- **Multi-Language Support**: Added support for 12 languages including English, Spanish, Chinese, Japanese, Korean, French, Portuguese, German, Italian, Russian, Ukrainian, and Arabic (non-English/Spanish translations generated with AI assistance)

_Special thanks to huangfanglong and Deticaru for their excellent original work, and to the CK3 modding community for inspiration and feedback._

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing issues for solutions

---

<div align="center">

**Made with ❤️ for the CK3 modding community**

</div>
```
