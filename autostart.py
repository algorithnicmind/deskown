import os
import sys
import winreg

import config


def add_autostart():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.AUTOSTART_REGISTRY,
            0,
            winreg.KEY_SET_VALUE,
        )
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable
        winreg.SetValueEx(
            key,
            config.AUTOSTART_KEY,
            0,
            winreg.REG_SZ,
            f'"{python_exe}" "{os.path.abspath("main.py")}"',
        )
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to add autostart: {e}")
        return False


def remove_autostart():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.AUTOSTART_REGISTRY,
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.DeleteValue(key, config.AUTOSTART_KEY)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Failed to remove autostart: {e}")
        return False


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            config.AUTOSTART_REGISTRY,
            0,
            winreg.KEY_READ,
        )
        winreg.QueryValueEx(key, config.AUTOSTART_KEY)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
