<div align="center">

# 🖥️ DeskOwn

### Your Personal Desktop AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.7+-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

**DeskOwn** is a sleek, modern desktop AI assistant that lives in your system tray. Powered by local AI models, it offers chat, voice commands, and smart automation — all with a beautiful dark UI.

</div>

---

## ✨ Features

<table>
<tr>
<td>

#### 🤖 **AI-Powered Chat**
Natural language conversations powered by Ollama (supports any model)

</td>
<td>

#### 🎤 **Voice Input**
Speech-to-text using Whisper for hands-free interaction

</td>
</tr>
<tr>
<td>

#### 🔊 **Voice Output**
Text-to-speech responses with Piper TTS

</td>
<td>

#### ⌨️ **Global Hotkey**
Toggle with `Ctrl+Shift+D` from anywhere

</td>
</tr>
<tr>
<td>

#### 🎨 **Modern Dark UI**
Sleek, translucent design with smooth animations

</td>
<td>

#### 📌 **System Tray**
Minimizes to tray, runs in background

</td>
</tr>
<tr>
<td>

#### 🧩 **Plugin System**
Extensible architecture for custom features

</td>
<td>

#### ⚡ **Lightweight**
Low resource usage with psutil monitoring

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** - Install from [ollama.com](https://ollama.com)
- **Windows 10/11** (primary support)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/deskown.git
cd deskown

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull AI model
ollama pull qwen2.5:3b
```

### Running DeskOwn

```bash
python main.py
```

<div align="center">

**Press `Ctrl+Shift+D` to toggle the assistant**

</div>

---

## 📸 Interface

```
┌─────────────────────────────┐
│  🔵 DeskOwn                 │
│  ─────────────────────────  │
│                             │
│  ┌─────────────────────┐    │
│  │ 🟢 Connected        │    │
│  └─────────────────────┘    │
│                             │
│  You: What can you do?      │
│  ┌─────────────────────┐    │
│  │ I can help with:    │    │
│  │ • Answer questions  │    │
│  │ • Open apps         │    │
│  │ • System info       │    │
│  │ • File search       │    │
│  └─────────────────────┘    │
│                             │
│  ┌─────────────────────┐    │
│  │ Type a message...🎤 │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_MODEL` | `qwen2.5:3b` | AI model to use |
| `HOTKEY` | `ctrl+shift+d` | Toggle shortcut |
| `STT_MODEL` | `base` | Whisper model size |
| `TTS_VOICE` | `en_US-amy-medium` | Voice for TTS |
| `POPUP_WIDTH` | `450` | Window width |
| `POPUP_HEIGHT` | `600` | Window height |

### 🎨 Theme Colors

```python
COLORS = {
    "background": "rgba(30, 30, 30, 230)",
    "accent": "#4a9eff",
    "user_bubble": "#4a9eff",
    "ai_bubble": "#3a3a3a",
    # ... more colors in config.py
}
```

---

## 🛠️ Tech Stack

<div align="center">

| Component | Technology |
|-----------|------------|
| **UI Framework** | PyQt6 |
| **AI Backend** | Ollama (Local LLM) |
| **Speech-to-Text** | Faster Whisper |
| **Text-to-Speech** | Piper TTS |
| **Audio Processing** | SoundDevice + NumPy |
| **Voice Detection** | WebRTC VAD |
| **System Monitoring** | psutil |
| **Automation** | PyAutoGUI |
| **Global Hotkeys** | pynput |

</div>

---

## 📁 Project Structure

```
deskown/
├── 📄 main.py              # Application entry point
├── 📄 config.py            # Configuration settings
├── 📄 requirements.txt     # Python dependencies
├── 📁 ui/                  # User interface modules
│   ├── chat_widget.py      # Chat interface
│   ├── voice_widget.py     # Voice controls
│   ├── popup_window.py     # Main popup window
│   └── tray.py             # System tray icon
├── 📁 core/                # Core functionality
│   ├── ai_engine.py        # Ollama integration
│   └── voice_engine.py     # STT/TTS engine
├── 📁 plugins/             # Plugin system
└── 📁 assets/              # Icons and resources
```

---

## 🔧 Building Executable

```bash
# Build standalone .exe
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing`)
3. 💾 Commit changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to branch (`git push origin feature/amazing`)
5. 📬 Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

### ⭐ Star this repo if you find it useful!

**Made with ❤️ for the desktop AI community**

</div>
