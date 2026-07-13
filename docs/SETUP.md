# DeskOwn — Setup Guide

## Prerequisites

### 1. Python 3.13+

Verify Python is installed:
```bash
python --version
# Expected: Python 3.13.x or higher
```

### 2. Ollama

Ollama must be installed and running locally.

**Install Ollama:**
1. Download from https://ollama.com/download
2. Run the installer
3. Ollama starts automatically as a service

**Verify Ollama:**
```bash
ollama --version
# Expected: ollama version 0.31.x or higher
```

**Pull a model (first time only):**
```bash
ollama pull qwen2.5:3b
# Downloads ~2GB model
```

**Verify model:**
```bash
ollama list
# Should show: qwen2.5:3b
```

**Test Ollama:**
```bash
curl http://localhost:11434
# Expected: Ollama is running
```

---

## Installation

### 1. Clone or Download

```bash
cd C:\Users\ankit\OneDrive\Documents\GitHub
git clone <repo-url> deskown
cd deskown
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Additional System Dependencies

**FFmpeg** (required by faster-whisper for audio processing):
```bash
# Using winget:
winget install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to system PATH
```

**Microsoft Visual C++ Redistributable** (required by some audio libraries):
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## First Run

### 1. Start DeskOwn

```bash
python main.py
```

### 2. Verify

- System tray icon should appear (bottom-right corner of taskbar)
- On Windows 11, you may need to click "Show hidden icons" to see it
- Double-click the icon to open the popup window
- Type a message in the chat and press Enter

### 3. Pull Additional Models (Optional)

```bash
# For better quality (requires more RAM):
ollama pull qwen2.5:7b

# For faster responses:
ollama pull qwen2.5:1.5b

# List all available models:
ollama list
```

---

## Voice Setup

### 1. Verify Microphone Access

Windows Settings → Privacy → Microphone → Enable for Desktop Apps

### 2. Test Voice

1. Click the microphone button in the Voice tab
2. Hold and speak
3. Release to transcribe
4. The transcribed text appears in the chat

### 3. Install Voice Models (Auto-downloaded)

Voice models are downloaded automatically on first use:
- **STT**: `base` model (~150MB)
- **TTS**: `en_US-amy-medium` (~60MB)

---

## Hotkey

Default global hotkey: **Ctrl+Shift+D**

Press this combination anywhere in Windows to toggle the DeskOwn popup window.

To change the hotkey, edit `config.py`:
```python
HOTKEY = "ctrl+shift+d"  # Change to your preference
```

---

## Auto-start on Login

1. Right-click the tray icon
2. Select "Auto-start" to toggle on/off
3. When enabled, DeskOwn starts automatically when you log in

To disable auto-start manually:
```bash
# Open Registry Editor:
regedit

# Navigate to:
HKEY_CURRENT_USER\Software\Microsoft\Microsoft\Windows\CurrentVersion\Run

# Delete the "DeskOwn" entry
```

---

## Troubleshooting

### "Ollama is not running"

```bash
# Start Ollama:
ollama serve

# Or check if it's running:
curl http://localhost:11434
```

### "Model not found"

```bash
# Pull the model:
ollama pull qwen2.5:3b
```

### "Microphone not working"

1. Check Windows microphone permissions
2. Test with another app (Voice Recorder)
3. Check `sounddevice` can see your mic:
   ```python
   import sounddevice
   print(sounddevice.query_devices())
   ```

### "No tray icon visible"

Windows 11 hides tray icons by default:
1. Click the "^" arrow in the taskbar
2. Right-click the DeskOwn icon
3. Select "Pin to taskbar"

### "Popup window not appearing"

The popup may appear on a different monitor. Try:
1. Press Ctrl+Shift+D to toggle
2. Check all monitors for the popup

### "Console window appears on startup"

If auto-starting, ensure you're using `pythonw.exe` not `python.exe`. The `autostart.py` module handles this automatically.

---

## Configuration

All settings are in `config.py`. Key settings:

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:3b` | Which Ollama model to use |
| `POPUP_WIDTH` | `450` | Popup window width |
| `POPUP_HEIGHT` | `600` | Popup window height |
| `HOTKEY` | `ctrl+shift+d` | Global toggle hotkey |
| `STT_MODEL` | `base` | Whisper model size |
| `TTS_VOICE` | `en_US-amy-medium` | Piper TTS voice |
| `MONITOR_INTERVAL` | `2` | Stats refresh rate (seconds) |

---

## Uninstall

1. Disable auto-start (right-click tray → Auto-start → Off)
2. Delete the `deskown` folder
3. Remove the virtual environment:
   ```bash
   rm -rf venv
   ```
4. (Optional) Remove Ollama models:
   ```bash
   ollama rm qwen2.5:3b
   ```
