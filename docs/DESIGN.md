# DeskOwn — Design Document

## 1. Project Overview

DeskOwn is a Windows desktop AI assistant that lives in the system tray and launches automatically on login. It provides:

- **Chat Interface** — Text conversation with a local LLM via Ollama
- **Voice Assistant** — Push-to-talk speech-to-text and text-to-speech
- **Task Automation** — Open apps, search files, search the web via natural language
- **System Monitor** — Real-time CPU, RAM, disk, battery, network stats
- **Auto-start** — Registers in Windows to start on login

All AI processing runs **100% locally** — no API keys, no cloud, no data leaves your machine.

### Architecture

```
┌─────────────────────────────────────────────┐
│              System Tray Icon               │
│       (right-click menu, double-click)      │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│            Main Popup Window                │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │  Chat    │ │  Voice   │ │  Monitor   │  │
│  │  Widget  │ │  Widget  │ │  Widget    │  │
│  └────┬─────┘ └────┬─────┘ └─────┬──────┘  │
│       │             │             │          │
│  ┌────▼─────────────▼─────────────▼──────┐  │
│  │           Tab Navigation             │  │
│  └───────────────────────────────────────┘  │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│              Core Engine Layer              │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │AI Engine │ │  Voice   │ │   Task     │  │
│  │(Ollama)  │ │  Engine  │ │  Runner    │  │
│  │          │ │ STT + TTS│ │ (Plugins)  │  │
│  └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────────────────────────────────┐   │
│  │         System Monitor (psutil)      │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 2. Tech Stack

| Component | Library | Why |
|---|---|---|
| Language | Python 3.13 | Rich ecosystem, fast prototyping |
| UI Framework | PyQt6 | Native Windows look, system tray, transparency |
| AI Backend | Ollama (local) | No API key needed, privacy-first |
| Chat SDK | `ollama` (official) | Streaming, async, typed responses |
| STT | `faster-whisper` | 4x faster than original Whisper, CPU-optimized |
| TTS | `piper-tts` | Fast offline neural TTS, 30+ languages |
| Mic Capture | `sounddevice` | Simpler than pyaudio on Windows |
| Audio VAD | `webrtcvad` | Voice activity detection for auto-stop |
| System Stats | `psutil` | Cross-platform CPU, RAM, disk, battery |
| Automation | `pyautogui` + `subprocess` | Keyboard/mouse simulation, app launching |
| Global Hotkey | `pynput` | Cross-platform keyboard listener |
| Auto-start | `winreg` (stdlib) | Windows Registry manipulation |
| Packaging | PyInstaller | Single .exe distribution |

---

## 3. Project Structure

```
deskown/
├── main.py                        # Entry point — tray, popup, hotkey
├── config.py                      # All settings and constants
├── requirements.txt               # pip dependencies
├── autostart.py                   # Windows auto-start registry
├── build.spec                     # PyInstaller config
├── assets/
│   └── icon.ico                   # System tray icon
├── core/
│   ├── __init__.py
│   ├── ai_engine.py               # Ollama chat, streaming, history
│   ├── voice_engine.py            # STT (whisper) + TTS (piper)
│   ├── task_runner.py             # Plugin dispatcher, command matching
│   └── system_monitor.py          # psutil stats collection
├── ui/
│   ├── __init__.py
│   ├── tray.py                    # QSystemTrayIcon + context menu
│   ├── popup_window.py            # Frameless popup, positioning
│   ├── chat_widget.py             # Chat messages + input
│   ├── voice_widget.py            # Mic button + status
│   └── monitor_widget.py          # System stats dashboard
├── plugins/
│   ├── __init__.py
│   ├── app_launcher.py            # Open applications by name
│   ├── file_search.py             # Find files on disk
│   └── web_search.py              # DuckDuckGo browser search
└── docs/
    ├── DESIGN.md                  # This file
    ├── SETUP.md                   # Installation guide
    ├── MODULES.md                 # Core module API docs
    ├── UI.md                      # UI component docs
    ├── PLUGINS.md                 # Plugin system docs
    └── BUILD.md                   # Packaging guide
```

---

## 4. Core Modules

### 4.1 AI Engine (`core/ai_engine.py`)

Responsible for all LLM interaction via Ollama.

**Key Functions:**
- `chat(message: str) -> str` — Send message, get response
- `chat_stream(message: str) -> Generator[str]` — Streaming response
- `clear_history()` — Reset conversation
- `set_model(model: str)` — Switch Ollama model

**Conversation History:**
```python
messages = [
    {"role": "system", "content": "You are DeskOwn, a helpful desktop assistant."},
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I don't have weather data..."},
    # ... more turns
]
# Trimmed to last 20 messages to stay within context window
```

**Streaming:**
```python
stream = ollama.chat(model=model, messages=messages, stream=True)
for chunk in stream:
    yield chunk['message']['content']
```

### 4.2 Voice Engine (`core/voice_engine.py`)

Handles speech-to-text and text-to-speech.

**STT (Speech-to-Text):**
- Library: `faster-whisper` with `base` model
- Mode: CPU with int8 quantization
- Audio format: 16kHz mono PCM
- VAD: `webrtcvad` for automatic speech end detection

**TTS (Text-to-Speech):**
- Library: `piper-tts`
- Voice: `en_US-amy-medium` (default, configurable)
- Output: WAV audio played via `sounddevice`

**Workflow:**
1. User holds hotkey (Ctrl+Space or mic button)
2. Audio captured via `sounddevice` at 16kHz
3. On release: `faster-whisper` transcribes audio
4. Transcribed text sent to AI engine
5. AI response spoken aloud via `piper-tts`

### 4.3 Task Runner (`core/task_runner.py`)

Plugin-based command dispatcher.

**Plugin Interface:**
```python
class Plugin:
    name: str
    description: str
    patterns: list[str]  # Regex patterns to match commands

    def match(self, command: str) -> bool:
        """Check if this plugin handles the command."""

    def execute(self, command: str, context: dict) -> str:
        """Execute the command, return result text."""
```

**Available Plugins:**
- `app_launcher` — "open chrome", "launch vscode"
- `file_search` — "find readme.md", "search for *.py"
- `web_search` — "search for python tutorials"

### 4.4 System Monitor (`core/system_monitor.py`)

Real-time system statistics via `psutil`.

**Collected Stats:**
- CPU: overall usage %, per-core usage
- RAM: used/total GB, percentage
- Disk: per-drive usage, I/O bytes
- Battery: percentage, charging status, time remaining
- Network: bytes sent/received, connection count
- Top Processes: by CPU and RAM usage

**Update Interval:** 2 seconds (configurable)

---

## 5. UI Modules

### 5.1 System Tray (`ui/tray.py`)

- `QSystemTrayIcon` with custom icon
- Tooltip: "DeskOwn - Desktop AI Assistant"
- Context menu: Open, Settings, Voice Toggle, Auto-start Toggle, Quit
- Double-click: toggle popup window visibility
- Balloon messages for notifications

### 5.2 Popup Window (`ui/popup_window.py`)

- Frameless, always-on-top, no taskbar entry
- Translucent background (WA_TranslucentBackground)
- Rounded corners via stylesheet
- Positioned near system tray icon
- Auto-hides on focus loss
- Toggle via double-click tray or Ctrl+Shift+D

### 5.3 Chat Widget (`ui/chat_widget.py`)

- Scrollable message area with user/AI bubbles
- User messages: right-aligned, blue background
- AI messages: left-aligned, dark background
- Streaming text display (tokens appear in real-time)
- Markdown rendering: code blocks with syntax highlighting
- Input field with send button (Enter to send)
- Copy button on code blocks

### 5.4 Voice Widget (`ui/voice_widget.py`)

- Large microphone button (hold to talk)
- Visual state indicators:
  - Idle: gray mic icon
  - Listening: pulsing red indicator
  - Thinking: spinning loader
  - Speaking: animated speaker icon
- Transcribed text display
- Volume level indicator

### 5.5 Monitor Widget (`ui/monitor_widget.py`)

- Dashboard layout with stat cards
- CPU usage progress bar (color: green < 50%, yellow < 80%, red > 80%)
- RAM usage progress bar with used/total text
- Disk usage per drive
- Battery indicator (charging icon, percentage)
- Network speed display (up/down)
- Top 5 processes table
- Refresh button

---

## 6. Plugins

### Plugin System Architecture

```
User Command → TaskRunner.match(command) → Plugin.execute() → Result → AI/Display
```

Plugins are discovered automatically from the `plugins/` directory. Each plugin:
1. Has a `Plugin` class with `name`, `description`, `patterns`
2. Implements `match(command)` and `execute(command, context)`
3. Returns a string result

### Built-in Plugins

| Plugin | Matches | Action |
|---|---|---|
| `app_launcher` | "open *", "launch *", "start *" | Opens application via subprocess |
| `file_search` | "find *", "search for *", "locate *" | Searches disk with os.walk |
| `web_search` | "search for *", "look up *", "google *" | Opens DuckDuckGo in browser |

---

## 7. Auto-start

Uses Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`:

```python
import winreg

def add_autostart():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "DeskOwn", 0, winreg.REG_SZ,
        f'pythonw.exe "{os.path.abspath("main.py")}"')
    winreg.CloseKey(key)

def remove_autostart():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.DeleteValue(key, "DeskOwn")
    winreg.CloseKey(key)
```

Uses `pythonw.exe` (not `python.exe`) to avoid showing a console window.

---

## 8. Configuration (`config.py`)

All settings in one place:

```python
APP_NAME = "DeskOwn"
APP_VERSION = "1.0.0"

# Ollama
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_HOST = "http://localhost:11434"
SYSTEM_PROMPT = "You are DeskOwn, a helpful desktop AI assistant..."
MAX_HISTORY = 20

# UI
POPUP_WIDTH = 450
POPUP_HEIGHT = 600
TRAY_ICON_PATH = "assets/icon.ico"
HOTKEY = "ctrl+shift+d"

# Voice
STT_MODEL = "base"
STT_DEVICE = "cpu"
TTS_VOICE = "en_US-amy-medium"
SAMPLE_RATE = 16000

# System Monitor
MONITOR_INTERVAL = 2  # seconds

# Auto-start
AUTOSTART_KEY = "DeskOwn"
AUTOSTART_REGISTRY = r"Software\Microsoft\Windows\CurrentVersion\Run"
```

---

## 9. Build & Distribution

PyInstaller creates a single .exe:

```bash
pyinstaller build.spec
# Output: dist/DeskOwn.exe
```

The .exe:
- Includes all Python files, assets, and dependencies
- Runs without Python installed
- Can be set to auto-start on login
- Size: ~50-80MB

---

## 10. Implementation Phases

| Phase | Files | Deliverable |
|---|---|---|
| **0** | `docs/*` | Documentation complete |
| **1** | `requirements.txt`, `config.py`, `__init__.py` x3 | Project skeleton |
| **2** | `ui/tray.py`, `ui/popup_window.py`, `main.py` | Tray icon + popup |
| **3** | `core/ai_engine.py`, `ui/chat_widget.py` | Working chat |
| **4** | `core/voice_engine.py`, `ui/voice_widget.py` | Voice I/O |
| **5** | `core/task_runner.py`, `plugins/*.py` | Task automation |
| **6** | `core/system_monitor.py`, `ui/monitor_widget.py` | System monitor |
| **7** | `autostart.py`, `build.spec` | Auto-start + packaging |
