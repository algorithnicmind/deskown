# DeskOwn — Build & Packaging Guide

## Overview

DeskOwn can be packaged into a single `.exe` file using PyInstaller. This allows distribution without requiring Python to be installed on the target machine.

---

## Prerequisites

### 1. Install Build Dependencies

```bash
pip install pyinstaller
```

### 2. Verify Ollama Model

Make sure the Ollama model is pulled:

```bash
ollama pull qwen2.5:3b
```

Note: The Ollama model is NOT bundled in the .exe — users must have Ollama installed separately.

---

## Build Commands

### Quick Build

```bash
pyinstaller --onefile --windowed --name DeskOwn main.py
```

### Full Build (Recommended)

```bash
pyinstaller build.spec
```

### Build Output

```
dist/
├── DeskOwn.exe          # Single-file executable
```

---

## Build Spec File (`build.spec`)

The `build.spec` file configures PyInstaller:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('core/*', 'core'),
        ('ui/*', 'ui'),
        ('plugins/*', 'plugins'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'ollama',
        'faster_whisper',
        'piper',
        'psutil',
        'sounddevice',
        'pyautogui',
        'pynput',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DeskOwn',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

---

## Bundle Contents

The .exe includes:

| Included | Not Included |
|---|---|
| All Python files | Ollama (must install separately) |
| UI assets (icon) | Ollama models (downloaded separately) |
| Config defaults | Voice models (downloaded on first use) |
| Core modules | FFmpeg (must install separately) |
| Plugin modules | |
| Hidden imports | |

---

## Distribution

### Method 1: Direct .exe Share

1. Build the .exe
2. Share `dist/DeskOwn.exe`
3. User runs it directly

### Method 2: Installer (Optional)

Use Inno Setup or NSIS to create a proper Windows installer:

```inno
[Setup]
AppName=DeskOwn
AppVersion=1.0.0
DefaultDirName={autopf}\DeskOwn
DefaultGroupName=DeskOwn
OutputDir=installer
OutputBaseFilename=DeskOwn-Setup

[Files]
Source: "dist\DeskOwn.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\DeskOwn"; Filename: "{app}\DeskOwn.exe"
Name: "{autostartup}\DeskOwn"; Filename: "{app}\DeskOwn.exe"; Flags: unchecked

[Run]
Filename: "{app}\DeskOwn.exe"; Description: "Launch DeskOwn"; Flags: postinstall nowait
```

### Method 3: ZIP Distribution

1. Build the .exe
2. Create `DeskOwn-v1.0.0.zip` containing:
   - `DeskOwn.exe`
   - `README.md`
   - `SETUP.md`
3. Share the ZIP file

---

## User Requirements

Users must have these installed separately:

1. **Ollama** — https://ollama.com/download
   ```bash
   ollama pull qwen2.5:3b
   ```

2. **Microsoft Visual C++ Redistributable** (usually pre-installed)
   - https://aka.ms/vs/17/release/vc_redist.x64.exe

3. **FFmpeg** (optional, for advanced audio features)
   ```bash
   winget install ffmpeg
   ```

---

## Build Optimization

### Reduce .exe Size

```bash
# Exclude unnecessary modules
pyinstaller --onefile --windowed \
    --exclude-module tkinter \
    --exclude-module matplotlib \
    --exclude-module scipy \
    --exclude-module PIL \
    --name DeskOwn main.py
```

### UPX Compression

PyInstaller uses UPX by default. To disable:

```python
exe = EXE(
    ...
    upx=False,  # Disable UPX
    ...
)
```

### Debug Build

For troubleshooting:

```bash
pyinstaller --onefile --windowed --debug=all --name DeskOwn-debug main.py
```

---

## Rebuild Process

```bash
# Clean previous build
rmdir /s /q build
rmdir /s /q dist
del DeskOwn.spec

# Rebuild
pyinstaller build.spec
```

---

## Troubleshooting Build

### "Module not found" Error

Add the module to `hiddenimports` in `build.spec`:

```python
hiddenimports=[
    'missing_module_name',
],
```

### "No module named" at Runtime

The .exe may be missing data files. Add them to `datas`:

```python
datas=[
    ('path/to/file', 'destination/folder'),
],
```

### Large .exe Size

This is normal for PyQt6 applications. The base size is ~50-80MB due to:
- PyQt6 framework (~30MB)
- Python runtime (~15MB)
- Application code (~5MB)
- Icons and assets (~1MB)

### Antivirus False Positive

Some antivirus software flags PyInstaller .exe files. To resolve:
1. Code sign the .exe (requires certificate)
2. Add exception in antivirus
3. Distribute via trusted channel

---

## Version Management

Update version in `config.py`:

```python
APP_VERSION = "1.0.0"
```

This version is displayed in:
- About dialog
- Tray tooltip
- Command line output
