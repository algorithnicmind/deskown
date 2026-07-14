import re
import webbrowser
import urllib.parse


class Plugin:
    name = "web_search"
    description = "Search the web"
    patterns = [
        r"search for (.+)",
        r"google (.+)",
        r"look up (.+)",
        r"find online (.+)",
    ]

    def match(self, command: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command: str, context: dict) -> str:
        for pattern in self.patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                try:
                    webbrowser.open(search_url)
                    return f"Searching for '{query}' in your browser"
                except Exception as e:
                    return f"Failed to open browser: {e}"
        return "Could not parse search query"
