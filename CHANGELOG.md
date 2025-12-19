# Changelog

All notable changes to CK3 Character & CoA Manager will be documented in this file.

## [2.3.0] - 2025-12-19

### Added

- 🐍 **Automatic Python Installation & Verification**
  - Created `install_python.bat` script for automatic Python installation
  - Supports Windows Package Manager (winget) and Chocolatey package managers
  - Automatic Python download and installation if managers not available
  - Integrated dependency verification in `app.py` main entry point
  - REQUIREMENTS list in app.py for easy dependency management
- 📖 **Quick Start Guides**
  - Added `INICIO_RAPIDO.txt` (Spanish) - Step-by-step setup instructions
  - Added `QUICK_START.txt` (English) - English version of quick start guide
  - Comprehensive troubleshooting sections
  - User-friendly setup process

### Fixed

- 🛡️ **CoA Mode Data Loading**
  - Fixed TypeError in `CoAManager.get_gallery_names()` when loading single object JSON
  - Added automatic JSON structure normalization for single object vs array handling
  - Improved `reload_from_disk()` functionality in CoA mode
  - Gallery list now properly reloads when switching databases in CoA mode

- 🎨 **UI Improvements**
  - Fixed character list display in CoA mode (now shows CoAs instead of characters)
  - Implemented mode-aware `filter_characters()` function for proper content filtering
  - Enhanced `on_character_select()` to handle both character and CoA selections
  - Added `load_coa()` method to properly display CoA data in UI
  - Reorganized search bar with clear button (X) positioned inline

### Changed

- 📝 **File Naming**
  - Renamed `main.py` to `app.py` for clarity
  - Renamed `verify_python.bat` to `install_python.bat`
  - Updated all references in `main.spec`, `README.md`, and configuration files

- 🔄 **Dependency Management**
  - Moved from `requirements.txt` to inline REQUIREMENTS list in `app.py`
  - Automatic dependency installation on startup if missing
  - Reduced file clutter with fewer configuration files

### Removed

- Deleted `verify_python.py` (Python cannot verify Python installation)
- Deleted `verify_python.ps1` (simplified to single .bat installer)
- Removed `requirements.txt` (dependencies now in app.py)

## [2.2.0] - 2025-11-29

### Added

- 📝 **Comprehensive Logging System**
  - Automatic logging to `log/log.txt` with rotation (5MB max, 3 backups)
  - All operations logged: character CRUD, database operations, image handling
  - Detailed logging in core modules (GalleryManager, CoAManager, DatabaseManager)
  - Operation tracking with timestamps, success/failure status, and context
- 🛡️ **Error Handling & Exception Management**
  - Global Python exception handler (`sys.excepthook`) for uncaught errors
  - Tkinter exception handler (`report_callback_exception`) for GUI errors
  - Full stack traces logged for all exceptions
  - User-friendly error dialogs with technical details logged
- 🔍 **Operation Tracking**
  - Character operations: create, save, update, delete
  - Gallery operations: create, save, reload
  - CoA operations: add, delete, image handling
  - Database operations: create, switch, initialization
  - Image file operations with success/failure logging

### Technical Details

- Enhanced `logger.py` with global exception handlers
- Added logging to `gallery_manager.py`: save_galleries, create_gallery, add_character, delete_character
- Added logging to `coa_manager.py`: save_galleries, create_gallery, add_coa, delete_coa
- Added logging to `database_manager.py`: create_database
- Added logging to `main_window.py`: all character operations, database switching, Tkinter error handler
- All file I/O operations wrapped in try-catch with comprehensive error logging
- Log rotation prevents excessive disk usage
- Console output (WARNING+) and file output (INFO+) with different verbosity levels

## [2.1.0] - 2025-11-07

### Added

- 🌐 **Multi-Language Support**
  - Added support for 12 languages
  - English (en) - Default
  - Spanish (es) - Español
  - Chinese (zh) - 中文 (AI-translated)
  - Japanese (ja) - 日本語 (AI-translated)
  - Korean (ko) - 한국어 (AI-translated)
  - French (fr) - Français (AI-translated)
  - Portuguese (pt) - Português (AI-translated)
  - German (de) - Deutsch (AI-translated)
  - Italian (it) - Italiano (AI-translated)
  - Russian (ru) - Русский (AI-translated)
  - Ukrainian (uk) - Українська (AI-translated)
  - Arabic (ar) - العربية (AI-translated)
- 🔤 **Language Menu**
  - Easy language switching from the menu bar
  - Native language names displayed
  - Persistent language preference
- 📝 **Translation Note**
  - Non-English/Spanish translations generated using AI assistance
  - Native speakers welcome to contribute improvements

### Changed

- 📝 **Full UI Translation**
  - All menus, buttons, and labels translated
  - Dialog boxes and messages in all languages
  - Help text and tooltips localized
  - Status messages translated

### Technical Details

- Added `locales/` directory with JSON language files
- Implemented `LanguageManager` for translation handling
- Updated all UI components to use translation keys
- Added right-to-left (RTL) text support for Arabic

## [2.0.0] - 2025-11-07

### Added

- 🗄️ **Multiple Database System**
  - Create and manage multiple databases
  - Switch between databases on the fly
  - Database backup functionality
  - Support for character-only, CoA-only, or combined databases
  - Database management dialog with statistics
- 🛡️ **Coat of Arms (CoA) Mode**
  - Complete CoA gallery system
  - Parse and display CK3 coat of arms codes
  - Tag-based organization for CoAs
  - Import/Export CoA galleries
  - Automatic mode switching (Character ↔ CoA)
- 🔄 **Cross-Database Operations**
  - Move characters between databases
  - Move CoAs between databases
  - Bulk move operations with selection dialog
- 📋 **Enhanced Menu System**
  - Database menu with full management options
  - View menu for mode switching
  - Help menu with shortcuts and about info
- ✨ **Improved UI Organization**
  - Reorganized buttons in 2x2 grid layout
  - Added Edit button for quick access
  - Better button spacing and alignment
  - Width-constrained buttons for consistency
- 🔍 **Enhanced Search**
  - Context-aware autocomplete (tags/names/CoA IDs)
  - Mode-specific search functionality
  - Clear button for quick filter reset

### Changed

- 🏗️ **Architecture Improvements**
  - New `DatabaseManager` for multi-database support
  - New `CoAManager` for coat of arms handling
  - Separated database dialogs into dedicated module
  - Enhanced modular structure
- 🎨 **UI/UX Improvements**
  - DNA editor auto-hides in CoA mode
  - Dynamic title updates based on active mode
  - Better visual organization of controls
  - Improved status messages

### Technical Details

- Added `database_manager.py` core module
- Added `coa_manager.py` core module
- Added `database_dialogs.py` UI module
- Refactored `main_window.py` with menu bar
- Enhanced type hints and documentation
- Improved error handling across all operations

## [1.0.0] - 2025-11-07

### Added

- ✨ Initial release of unified CK3 Character Manager
- 📁 Character Gallery Management
  - Create, rename, and delete galleries
  - Add, edit, and delete character entries
  - Tag-based organization and search
  - Import/Export gallery functionality
- 🧬 DNA Duplicator
  - Duplicate DNA values for consistent inheritance
  - Validate DNA format
  - Quick copy to clipboard
- 🎨 Portrait Management
  - Interactive crop tool with drag and zoom
  - Paste from clipboard support
  - Multiple image format support (PNG, JPG, BMP, GIF)
- ⌨️ Keyboard Shortcuts
  - Ctrl+S: Save character
  - Ctrl+N: New character
  - Ctrl+D: Duplicate DNA
  - Ctrl+V: Paste portrait
  - Ctrl+F: Focus search
  - Delete: Delete character
- 💾 Persistent Data Storage
  - JSON-based gallery database
  - Automatic image management
- 🔧 Build System
  - PyInstaller build script
  - Nuitka build script
  - Cross-platform support

### Technical Details

- Built with Python 3.10+
- Tkinter-based GUI
- PIL/Pillow for image processing
- Modular architecture with separated concerns
- Type hints for better code quality
- Comprehensive error handling

### Credits

- Based on CK3-Character-Gallery by huangfanglong
- Integrated CK3-DNA-Duplicator by Deticaru

- Combined and enhanced with unified interface

---

## Future Roadmap

### Planned Features (v1.1.0)

- [ ] Batch DNA duplication for multiple characters
- [ ] Character comparison view
- [ ] DNA export/import in various formats
- [ ] Search filters by tags
- [ ] Sort characters by multiple criteria
- [ ] Undo/Redo for character edits

### Potential Features (v2.0.0)

- [ ] Dark/Light theme toggle
- [ ] Character traits visualization
- [ ] DNA compatibility checker
- [ ] Backup/Restore functionality
- [ ] Multi-language support
- [ ] Cloud sync (optional)

---

## Version History

| Version | Date       | Status   | Notes                   |
| ------- | ---------- | -------- | ----------------------- |
| 1.0.0   | 2025-11-07 | Released | Initial unified release |

---

## Migration Notes

### From CK3-Character-Gallery

If you were using the original Character Gallery:

1. Export your galleries from the old app
2. Import them into CK3 Character Manager
3. Your data will be preserved

### From CK3-DNA-Duplicator

DNA duplication is now integrated:

- Same functionality as the standalone tool
- Plus save DNA directly to character profiles
- No need to copy/paste between applications

---

## Known Issues

### v1.0.0

- None reported yet

---

## Support

For bug reports and feature requests:

- Open an issue on GitHub
- Include version number and error details
- Screenshots are helpful

---

## License

MIT License - See LICENSE file for details

---

## Credits

### Version 2.0.0+ (Unified Application)

**Developed by [Alfarojo](https://github.com/Alfarojo25)**

- Unified application architecture
- Multi-database system
- Coat of Arms support
- Enhanced UI/UX

### Based on Original Projects

- **CK3-Character-Gallery** by [huangfanglong](https://github.com/huangfanglong)
- **CK3-DNA-Duplicator** by [Deticaru](https://github.com/Deticaru)
