import re
import subprocess


class Plugin:
    name = "app_launcher"
    description = "Open applications by name"
    patterns = [
        r"open (.+)",
        r"launch (.+)",
        r"start (.+)",
    ]

    APP_NAMES = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "vscode": "code.exe",
        "code": "code.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "powershell": "pwsh.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "slack": "slack.exe",
        "teams": "teams.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
    }

    def match(self, command: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command: str, context: dict) -> str:
        for pattern in self.patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip().lower()
                exe = self.APP_NAMES.get(app_name, f"{app_name}.exe")
                try:
                    subprocess.Popen([exe], creationflags=subprocess.DETACHED_PROCESS)
                    return f"{app_name.title()} opened successfully"
                except FileNotFoundError:
                    return f"Could not find '{app_name}'. Try the full executable name."
                except Exception as e:
                    return f"Failed to open {app_name}: {e}"
        return "Could not parse application name"
