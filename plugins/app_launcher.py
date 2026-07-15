import subprocess


class Plugin:
    name = "app_launcher"
    description = "Open applications by name"

    APP_NAMES = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "vscode": "code.exe",
        "code": "code.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
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

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_application",
                    "description": "Opens a desktop application. Provide the common name of the application.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "The name of the application to open, e.g. 'chrome', 'notepad', 'vscode'."
                            }
                        },
                        "required": ["app_name"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "open_application":
            app_name = arguments.get("app_name", "").strip().lower()
            exe = self.APP_NAMES.get(app_name, f"{app_name}.exe")
            try:
                subprocess.Popen([exe], creationflags=subprocess.DETACHED_PROCESS)
                return f"{app_name.title()} opened successfully."
            except FileNotFoundError:
                return f"Could not find '{app_name}'. Try providing the full executable name."
            except Exception as e:
                return f"Failed to open {app_name}: {e}"
        return f"Unknown tool: {tool_name}"
