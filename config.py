import os

APP_NAME = "DeskOwn"
APP_VERSION = "1.0.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_HOST = "http://localhost:11434"
SYSTEM_PROMPT = (
    "You are DeskOwn, a helpful desktop AI assistant. "
    "You are concise, friendly, and helpful. "
    "You can help with answering questions, opening applications, "
    "searching files, and providing system information. "
    "Keep responses short and to the point."
)
MAX_HISTORY = 20

POPUP_WIDTH = 450
POPUP_HEIGHT = 600

TRAY_ICON_PATH = os.path.join(BASE_DIR, "assets", "icon.ico")

HOTKEY = "ctrl+shift+a"

WAKE_WORD = "hello deskown"
WAKE_WORD_THRESHOLD = 0.05

STT_MODEL = "base"
STT_DEVICE = "cpu"
STT_LANGUAGE = "en"

TTS_VOICE = "en_US-amy-medium"

SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_DTYPE = "float32"

MONITOR_INTERVAL = 2

AUTOSTART_KEY = "DeskOwn"
AUTOSTART_REGISTRY = r"Software\Microsoft\Windows\CurrentVersion\Run"

COLORS = {
    "background": "rgba(30, 30, 30, 230)",
    "surface": "rgba(45, 45, 45, 200)",
    "text": "#ffffff",
    "text_secondary": "#aaaaaa",
    "accent": "#4a9eff",
    "user_bubble": "#4a9eff",
    "ai_bubble": "#3a3a3a",
    "success": "#4caf50",
    "warning": "#ff9800",
    "error": "#f44336",
}

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 14
