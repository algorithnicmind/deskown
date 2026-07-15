import os
from PyQt6.QtWidgets import QApplication

class Plugin:
    name = "system_commands"
    description = "Execute system commands like shutdown or closing the assistant"

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "system_power_action",
                    "description": "Perform a system power action (shutdown or restart).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The power action to perform.",
                                "enum": ["shutdown", "restart"]
                            }
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "quit_deskown",
                    "description": "Closes the DeskOwn application completely.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "quit_deskown":
            QApplication.quit()
            return "Closing DeskOwn. Goodbye!"
            
        elif tool_name == "system_power_action":
            action = arguments.get("action", "")
            if action == "restart":
                os.system("shutdown /r /t 5")
                return "Restarting your computer in 5 seconds."
            elif action == "shutdown":
                os.system("shutdown /s /t 5")
                return "Shutting down your computer in 5 seconds."
            else:
                return f"Invalid action: {action}"
                
        return f"Unknown tool: {tool_name}"
