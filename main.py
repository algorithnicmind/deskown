import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import config
from ui.tray import SystemTray
from ui.popup_window import PopupWindow
from ui.chat_widget import ChatWidget
from ui.voice_widget import VoiceWidget
from ui.monitor_widget import MonitorWidget
from core.ai_engine import AIEngine
from core.voice_engine import VoiceEngine
from core.task_runner import TaskRunner
from core.system_monitor import SystemMonitor


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)

    if not os.path.exists(config.TRAY_ICON_PATH):
        os.makedirs(os.path.dirname(config.TRAY_ICON_PATH), exist_ok=True)

    ai_engine = AIEngine()
    voice_engine = VoiceEngine()
    task_runner = TaskRunner()
    system_monitor = SystemMonitor()

    tray = SystemTray()
    popup = PopupWindow(tray.tray)

    chat_widget = ChatWidget(ai_engine)
    voice_widget = VoiceWidget(voice_engine)
    monitor_widget = MonitorWidget(system_monitor)

    popup.add_tab(chat_widget, "Chat")
    popup.add_tab(voice_widget, "Voice")
    popup.add_tab(monitor_widget, "Monitor")
    popup.set_chat_widget(chat_widget)

    def on_send_message(text):
        response = ai_engine.chat(text, task_runner=task_runner, context={
            "ai_engine": ai_engine,
            "voice_engine": voice_engine,
            "task_runner": task_runner,
            "config": config,
        })
        if response:
            chat_widget._append_ai_message(response)

    popup.set_send_callback(on_send_message)

    def on_voice_speak(text):
        response = ai_engine.chat(text, task_runner=task_runner, context={
            "ai_engine": ai_engine,
            "voice_engine": voice_engine,
            "task_runner": task_runner,
            "config": config,
        })
        if response:
            chat_widget._append_ai_message(response)
            voice_widget.speak_response(response)

    voice_widget.speak_requested.connect(on_voice_speak)

    def on_open():
        popup.toggle_visibility()

    def on_quit():
        voice_engine.stop_wake_word_listener()
        system_monitor.stop()
        tray.hide()
        app.quit()

    def on_activate():
        QTimer.singleShot(0, popup.toggle_visibility)

    def on_voice_toggled(enabled):
        if enabled:
            voice_engine.start_wake_word_listener(on_activate)
        else:
            voice_engine.stop_wake_word_listener()

    def on_autostart_toggled(enabled):
        try:
            import autostart
            if enabled:
                autostart.add_autostart()
            else:
                autostart.remove_autostart()
        except ImportError:
            pass

    tray.open_requested.connect(on_open)
    tray.quit_requested.connect(on_quit)
    tray.voice_toggled.connect(on_voice_toggled)
    tray.autostart_toggled.connect(on_autostart_toggled)

    try:
        from pynput import keyboard

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

    system_monitor.start()
    
    if tray.voice_enabled:
        voice_engine.start_wake_word_listener(on_activate)

    tray.show()
    tray.show_message(config.APP_NAME, f"Running. Press {config.HOTKEY} to toggle.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
