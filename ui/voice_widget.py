from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSizePolicy,
)
from PyQt6.QtGui import QFont

import config
from core.voice_engine import VoiceEngine


class TranscribeThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, engine: VoiceEngine, audio_data):
        super().__init__()
        self.engine = engine
        self.audio_data = audio_data

    def run(self):
        try:
            text = self.engine.transcribe(self.audio_data)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class SpeakThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, engine: VoiceEngine, text: str):
        super().__init__()
        self.engine = engine
        self.text = text

    def run(self):
        try:
            self.engine.speak(self.text)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class VoiceWidget(QWidget):
    speak_requested = pyqtSignal(str)

    def __init__(self, voice_engine: VoiceEngine, parent=None):
        super().__init__(parent)
        self.voice_engine = voice_engine
        self.transcribe_thread = None
        self.speak_thread = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Click to start listening")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {config.COLORS['text_secondary']};
            font-size: 13px;
            margin-bottom: 20px;
        """)
        layout.addWidget(self.status_label)

        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(80, 80)
        self.mic_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.COLORS['surface']};
                border: 3px solid {config.COLORS['text_secondary']};
                border-radius: 40px;
                font-size: 30px;
            }}
            QPushButton:hover {{
                border-color: {config.COLORS['accent']};
            }}
        """)
        self.mic_button.setText("\U0001f3a4")
        self.mic_button.pressed.connect(self._on_mic_pressed)
        self.mic_button.released.connect(self._on_mic_released)
        layout.addWidget(self.mic_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.transcribed_label = QLabel("")
        self.transcribed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transcribed_label.setWordWrap(True)
        self.transcribed_label.setMaximumHeight(80)
        self.transcribed_label.setStyleSheet(f"""
            color: {config.COLORS['text']};
            font-size: 13px;
            margin-top: 20px;
            padding: 8px;
            background-color: {config.COLORS['surface']};
            border-radius: 8px;
        """)
        layout.addWidget(self.transcribed_label)

        layout.addStretch()

    def _on_mic_pressed(self):
        self.voice_engine.start_recording()
        self.status_label.setText("Listening... Release to stop")
        self.mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(244, 67, 54, 0.3);
                border: 3px solid #f44336;
                border-radius: 40px;
                font-size: 30px;
            }}
        """)

    def _on_mic_released(self):
        audio_data = self.voice_engine.stop_recording()
        self.status_label.setText("Transcribing...")
        self.mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.COLORS['surface']};
                border: 3px solid {config.COLORS['warning']};
                border-radius: 40px;
                font-size: 30px;
            }}
        """)

        if len(audio_data) < config.SAMPLE_RATE * 0.5:
            self.status_label.setText("Audio too short. Try again.")
            self._reset_button()
            return

        self.transcribe_thread = TranscribeThread(self.voice_engine, audio_data)
        self.transcribe_thread.finished.connect(self._on_transcribed)
        self.transcribe_thread.error.connect(self._on_error)
        self.transcribe_thread.start()

    def _on_transcribed(self, text: str):
        self.transcribed_label.setText(f'You said: "{text}"')
        self.status_label.setText("Processing...")
        self._reset_button()
        self.speak_requested.emit(text)

    def _on_error(self, error: str):
        self.status_label.setText(f"Error: {error}")
        self._reset_button()

    def _reset_button(self):
        self.mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.COLORS['surface']};
                border: 3px solid {config.COLORS['text_secondary']};
                border-radius: 40px;
                font-size: 30px;
            }}
            QPushButton:hover {{
                border-color: {config.COLORS['accent']};
            }}
        """)

    def speak_response(self, text: str):
        self.status_label.setText("Speaking...")
        self.speak_thread = SpeakThread(self.voice_engine, text)
        self.speak_thread.finished.connect(self._on_speak_finished)
        self.speak_thread.error.connect(self._on_speak_error)
        self.speak_thread.start()

    def _on_speak_finished(self):
        self.status_label.setText("Click to start listening")

    def _on_speak_error(self, error: str):
        self.status_label.setText(f"TTS Error: {error}")
