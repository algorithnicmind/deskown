from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFocusEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QApplication, QSystemTrayIcon,
)

import config


class PopupWindow(QWidget):
    def __init__(self, tray_icon: QSystemTrayIcon, parent=None):
        super().__init__(parent)
        self.tray_icon = tray_icon
        self.chat_widget = None
        self.send_callback = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(config.POPUP_WIDTH)
        self.setFixedHeight(config.POPUP_HEIGHT)

        self._setup_ui()
        self._apply_style()

        self._focus_timer = QTimer(self)
        self._focus_timer.setSingleShot(True)
        self._focus_timer.timeout.connect(self._check_hide)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(12, 8, 12, 12)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self._on_send)
        self.input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(60)
        self.send_button.clicked.connect(self._on_send)
        self.input_layout.addWidget(self.send_button)

        layout.addLayout(self.input_layout)

    def set_chat_widget(self, widget):
        self.chat_widget = widget

    def set_send_callback(self, callback):
        self.send_callback = callback

    def _on_tab_changed(self, index):
        tab_text = self.tabs.tabText(index)
        if tab_text == "Chat":
            self.input_field.show()
            self.send_button.show()
            self.input_field.setPlaceholderText("Type a message...")
        else:
            self.input_field.hide()
            self.send_button.hide()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {config.COLORS['background']};
                color: {config.COLORS['text']};
                font-family: '{config.FONT_FAMILY}';
                font-size: {config.FONT_SIZE}px;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar {{
                background-color: {config.COLORS['surface']};
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {config.COLORS['text_secondary']};
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {config.COLORS['accent']};
                border-bottom: 2px solid {config.COLORS['accent']};
            }}
            QTabBar::tab:hover {{
                color: {config.COLORS['text']};
            }}
            QLineEdit {{
                background-color: {config.COLORS['surface']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                color: {config.COLORS['text']};
                font-size: {config.FONT_SIZE}px;
            }}
            QLineEdit:focus {{
                border: 1px solid {config.COLORS['accent']};
            }}
            QPushButton {{
                background-color: {config.COLORS['accent']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: {config.FONT_SIZE}px;
            }}
            QPushButton:hover {{
                background-color: #3a8ee6;
            }}
            QPushButton:pressed {{
                background-color: #2a7ed6;
            }}
        """)

    def add_tab(self, widget: QWidget, title: str):
        self.tabs.addTab(widget, title)

    def show_at_tray(self):
        geo = self.tray_icon.geometry()
        if geo.isNull():
            screen = QApplication.primaryScreen()
            geo = screen.availableGeometry()

        screen = QApplication.screenAt(geo.center())
        if screen is None:
            screen = QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()

        x = geo.x()
        y = geo.y() - self.height() - 5

        if y < screen_geo.top():
            y = geo.bottom() + 5

        x = max(screen_geo.left(), min(x, screen_geo.right() - self.width()))
        y = max(screen_geo.top(), min(y, screen_geo.bottom() - self.height()))

        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_at_tray()

    def focusOutEvent(self, event: QFocusEvent):
        self._focus_timer.start(100)
        super().focusOutEvent(event)

    def _check_hide(self):
        app = QApplication.instance()
        focused = app.focusWidget()
        if focused is None or not self.isAncestorOf(focused):
            if self.isVisible():
                self.hide()

    def _on_send(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            if self.chat_widget:
                self.chat_widget.send_message(text)
            if self.send_callback:
                self.send_callback(text)
