import re

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QLabel, QSizePolicy,
)

import config
from core.ai_engine import AIEngine


class ChatStreamThread(QThread):
    token_received = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, engine: AIEngine, message: str):
        super().__init__()
        self.engine = engine
        self.message = message

    def run(self):
        try:
            for token in self.engine.chat_stream(self.message):
                self.token_received.emit(token)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class ChatWidget(QWidget):
    def __init__(self, engine: AIEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.stream_thread = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 0)
        layout.setSpacing(0)

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                color: {config.COLORS['text']};
                border: none;
                font-family: '{config.FONT_FAMILY}';
                font-size: {config.FONT_SIZE}px;
                padding: 8px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.chat_display)

        self._add_welcome_message()

    def _add_welcome_message(self):
        self.chat_display.setHtml(self._format_system(
            f"Welcome to <b>{config.APP_NAME}</b>!<br>"
            f"Ask me anything. I'm powered by <b>{config.OLLAMA_MODEL}</b> via Ollama."
        ))

    def send_message(self, text: str):
        if not text.strip():
            return

        self._append_user_message(text)
        self._set_streaming(True)

        self.stream_thread = ChatStreamThread(self.engine, text)
        self.stream_thread.token_received.connect(self._on_token)
        self.stream_thread.finished.connect(self._on_stream_finished)
        self.stream_thread.error.connect(self._on_error)
        self.stream_thread.start()

    def _on_token(self, token: str):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def _on_stream_finished(self):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml("<br><br>")
        self.chat_display.setTextCursor(cursor)
        self._set_streaming(False)

    def _on_error(self, error: str):
        self._append_ai_message(f"Error: {error}")
        self._set_streaming(False)

    def _set_streaming(self, streaming: bool):
        pass

    def _append_user_message(self, text: str):
        html = self._format_user(text)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def _append_ai_message(self, text: str):
        html = self._format_ai(text)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def _format_user(self, text: str) -> str:
        text = self._escape_html(text)
        text = self._render_markdown(text)
        return (
            f'<div style="text-align: right; margin: 8px 0;">'
            f'<span style="background-color: {config.COLORS["user_bubble"]}; '
            f'color: white; padding: 8px 12px; border-radius: 12px 12px 2px 12px; '
            f'display: inline-block; max-width: 80%;">{text}</span>'
            f'</div>'
        )

    def _format_ai(self, text: str) -> str:
        text = self._escape_html(text)
        text = self._render_markdown(text)
        return (
            f'<div style="text-align: left; margin: 8px 0;">'
            f'<span style="background-color: {config.COLORS["ai_bubble"]}; '
            f'color: {config.COLORS["text"]}; padding: 8px 12px; border-radius: 12px 12px 12px 2px; '
            f'display: inline-block; max-width: 80%;">{text}</span>'
            f'</div>'
        )

    def _format_system(self, text: str) -> str:
        return (
            f'<div style="text-align: center; margin: 16px 0;">'
            f'<span style="color: {config.COLORS["text_secondary"]}; font-size: 12px;">{text}</span>'
            f'</div>'
        )

    def _escape_html(self, text: str) -> str:
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace("\n", "<br>")
        return text

    def _render_markdown(self, text: str) -> str:
        text = re.sub(r'```(\w*)\n(.*?)```', r'<pre style="background-color: #1e1e1e; padding: 8px; border-radius: 4px; font-family: Consolas, monospace; font-size: 12px; overflow-x: auto;">\2</pre>', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'<code style="background-color: rgba(255,255,255,0.1); padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 12px;">\1</code>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        return text
