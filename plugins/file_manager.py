import os

class Plugin:
    name = "file_manager"
    description = "Manage files and directories."

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "Lists the contents of a directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the directory."
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Reads the contents of a text file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to read."
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Writes text to a file, overwriting its contents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to write."
                            },
                            "content": {
                                "type": "string",
                                "description": "The text content to write into the file."
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "list_directory":
            path = arguments.get("path", "")
            try:
                items = os.listdir(path)
                return f"Contents of {path}: {', '.join(items)}"
            except Exception as e:
                return f"Failed to list directory: {e}"
                
        elif tool_name == "read_file":
            path = arguments.get("path", "")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return f"Contents of {path}:\n{content}"
            except Exception as e:
                return f"Failed to read file: {e}"
                
        elif tool_name == "write_file":
            path = arguments.get("path", "")
            content = arguments.get("content", "")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote to {path}"
            except Exception as e:
                return f"Failed to write file: {e}"
                
        return f"Unknown tool: {tool_name}"
