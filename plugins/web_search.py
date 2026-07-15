import webbrowser
import urllib.parse


class Plugin:
    name = "web_search"
    description = "Search the web"

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Searches the web using a query. This will open the user's default browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on the web."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "search_web":
            query = arguments.get("query", "").strip()
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
            try:
                webbrowser.open(search_url)
                return f"Opened browser and searched for '{query}'"
            except Exception as e:
                return f"Failed to open browser: {e}"
        return f"Unknown tool: {tool_name}"
