# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Launch the Application

**From Source:**

```bash
python main.py
```

**From Executable:**
Double-click `CK3-Character-Manager.exe`

---

### Step 2: Create Your First Character

1. **Click "➕ New"** in the left panel
2. **Enter a name** (e.g., "King Harald")
3. **Add a portrait**:
   - Click the portrait area
   - Select an image file, OR
   - Take a screenshot and press `Ctrl+V`
4. **Add DNA**:
   - Copy DNA from CK3 game
   - Paste into the DNA editor
5. **Save**: Press `Ctrl+S`

Done! Your character is saved.

---

### Step 3: Duplicate DNA (Optional but Recommended)

Why? DNA has two values per gene. Children inherit randomly from both. Duplicating ensures consistent appearance.

1. **Click "🧬 Duplicate DNA"** or press `Ctrl+D`
2. DNA is automatically processed
3. **Copy DNA**: Click "📋 Copy DNA"
4. **Paste into CK3** game files

---

## 📚 Common Tasks

### Create a New Gallery

1. Click the gallery dropdown
2. Select "➕ New Gallery..."
3. Enter name (e.g., "My Dynasty")

### Search Characters

- **By name**: Type in search box
- **By tag**: Add tags like "warrior, red_hair"

### Export Gallery (Backup/Share)

1. Click **⋮** menu
2. Select "Export Gallery"
3. Choose folder
4. Share the exported folder!

### Import Gallery

1. Click **⋮** menu
2. Select "Import Gallery"
3. Select exported folder
4. Enter new gallery name

---

## ⌨️ Keyboard Shortcuts Reference

| Shortcut | Action                        |
| -------- | ----------------------------- |
| `Ctrl+S` | Save current character        |
| `Ctrl+N` | New character                 |
| `Ctrl+D` | Duplicate DNA                 |
| `Ctrl+V` | Paste portrait from clipboard |
| `Ctrl+F` | Focus search box              |
| `Delete` | Delete selected character     |

---

## 🎯 Pro Tips

### Efficient Workflow

1. **Take screenshots in-game** (Windows: `Win+Shift+S`)
2. **Immediately paste** into character (`Ctrl+V`)
3. **Copy DNA from console**
4. **Duplicate DNA** before saving
5. **Use tags** for organization

### Organizing Characters

```
Good tags:
✓ "dynasty, male, warrior"
✓ "historical, french, 1066"
✓ "custom, tall, blonde"

Bad tags:
✗ "my character" (too vague)
✗ "test123" (not searchable)
```

### Portrait Tips

- **Use high-res screenshots** (will be cropped)
- **Zoom in** on face during crop
- **Center the face** in red box
- **Scroll to adjust zoom** during crop

---

## ❓ FAQ

### Where is my data stored?

`character_data/` folder in the app directory:

- `galleries.json`: All character data
- `images/`: Portrait images

**Backup**: Export galleries regularly!

### Can I use this with mods?

Yes! Works with any CK3 DNA, vanilla or modded.

### DNA not working in-game?

Make sure to:

1. ✓ Validate DNA format (click "✓ Validate DNA")
2. ✓ Save character after changes
3. ✓ Copy entire DNA string
4. ✓ Paste into correct section of game files

### App won't start?

**From source:**

```bash
pip install -r requirements.txt
python main.py
```

**Executable:**

- Check antivirus (may need exception)
- Try running as administrator
- Download fresh copy

### Can I share my galleries?

Yes!

1. Export gallery (⋮ menu → Export)
2. Share the exported folder
3. Others import with (⋮ menu → Import)

---

## 🆘 Getting Help

1. **Check README.md** for detailed documentation
2. **Check CHANGELOG.md** for known issues
3. **Open GitHub issue** with:
   - What you were doing
   - Error message (if any)
   - Screenshot (if helpful)

---

## 🎉 You're Ready!

Start building your character collection!

**Next Steps:**

- Create multiple galleries for organization
- Use tags for easy searching
- Export galleries for backup
- Share with the CK3 community!

---

_Happy character managing! 👑_
