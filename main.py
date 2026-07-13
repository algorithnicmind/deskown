import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import config
from ui.tray import SystemTray
from ui.popup_window import PopupWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)

    if not os.path.exists(config.TRAY_ICON_PATH):
        os.makedirs(os.path.dirname(config.TRAY_ICON_PATH), exist_ok=True)

    tray = SystemTray()
    popup = PopupWindow(tray.tray)

    def on_open():
        popup.toggle_visibility()

    def on_quit():
        tray.hide()
        app.quit()

    tray.open_requested.connect(on_open)
    tray.quit_requested.connect(on_quit)

    try:
        from pynput import keyboard

        def on_activate():
            QTimer.singleShot(0, popup.toggle_visibility)

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(config.HOTKEY),
            on_activate
        )

        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        listener.start()
    except ImportError:
        pass
    except Exception:
        pass

    tray.show()
    tray.show_message(config.APP_NAME, f"Running. Press {config.HOTKEY} to toggle.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
