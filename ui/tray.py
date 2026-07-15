import os
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle

import config


class SystemTray(QObject):
    open_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    voice_toggled = pyqtSignal(bool)
    autostart_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon(QApplication.instance())
        
        if os.path.exists(config.TRAY_ICON_PATH):
            self.tray.setIcon(QIcon(config.TRAY_ICON_PATH))
        else:
            style = QApplication.style()
            icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            self.tray.setIcon(icon)
            
        self.tray.setToolTip(f"{config.APP_NAME} - Desktop AI Assistant")

        self.menu = QMenu()
        self._build_menu()

        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._on_activated)

        self.voice_enabled = True
        self.autostart_enabled = False

    def _build_menu(self):
        open_action = QAction("Open", self.menu)
        open_action.triggered.connect(self.open_requested.emit)
        self.menu.addAction(open_action)

        self.menu.addSeparator()

        self.voice_action = QAction("Voice: ON", self.menu)
        self.voice_action.triggered.connect(self._toggle_voice)
        self.menu.addAction(self.voice_action)

        self.autostart_action = QAction("Auto-start: OFF", self.menu)
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.menu.addAction(self.autostart_action)

        self.menu.addSeparator()

        about_action = QAction(f"About {config.APP_NAME}", self.menu)
        about_action.triggered.connect(self._show_about)
        self.menu.addAction(about_action)

        self.menu.addSeparator()

        quit_action = QAction("Quit", self.menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(quit_action)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_requested.emit()

    def _toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.voice_action.setText(f"Voice: {'ON' if self.voice_enabled else 'OFF'}")
        self.voice_toggled.emit(self.voice_enabled)

    def _toggle_autostart(self):
        self.autostart_enabled = not self.autostart_enabled
        self.autostart_action.setText(f"Auto-start: {'ON' if self.autostart_enabled else 'OFF'}")
        self.autostart_toggled.emit(self.autostart_enabled)

    def _show_about(self):
        self.tray.showMessage(
            config.APP_NAME,
            f"Version {config.APP_VERSION}\nDesktop AI Assistant powered by Ollama",
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )

    def show(self):
        self.tray.show()

    def hide(self):
        self.tray.hide()

    def show_message(self, title: str, message: str, duration: int = 3000):
        self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration)
