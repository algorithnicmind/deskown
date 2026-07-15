import pyautogui

class Plugin:
    name = "pc_control"
    description = "Control the computer keyboard and mouse."

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "type_text",
                    "description": "Types text using the keyboard.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to type."
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "press_key",
                    "description": "Presses a specific key on the keyboard, e.g., 'enter', 'tab', 'win', 'space'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The key to press."
                            }
                        },
                        "required": ["key"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "type_text":
            text = arguments.get("text", "")
            try:
                pyautogui.write(text, interval=0.01)
                return f"Successfully typed: {text}"
            except Exception as e:
                return f"Failed to type text: {e}"
                
        elif tool_name == "press_key":
            key = arguments.get("key", "")
            try:
                pyautogui.press(key)
                return f"Successfully pressed key: {key}"
            except Exception as e:
                return f"Failed to press key {key}: {e}"
                
        return f"Unknown tool: {tool_name}"
