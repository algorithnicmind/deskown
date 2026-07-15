import os
import fnmatch


class Plugin:
    name = "file_search"
    description = "Find files on disk"

    SEARCH_DIRS = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~"),
    ]

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Searches for files on the disk using a query or glob pattern.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The file name or glob pattern to search for (e.g. '*.txt' or 'report')."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: dict, context: dict) -> str:
        if tool_name == "search_files":
            query = arguments.get("query", "").strip()
            results = self._search(query)
            if results:
                return f"Found {len(results)} file(s):\n" + "\n".join(results[:10])
            return f"No files found matching '{query}'"
        return f"Unknown tool: {tool_name}"

    def _search(self, query: str) -> list[str]:
        results = []
        is_glob = any(c in query for c in ["*", "?", "["])
        for search_dir in self.SEARCH_DIRS:
            if not os.path.exists(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                for fname in files:
                    if is_glob:
                        if fnmatch.fnmatch(fname.lower(), query.lower()):
                            results.append(os.path.join(root, fname))
                    elif query.lower() in fname.lower():
                        results.append(os.path.join(root, fname))
                    if len(results) >= 20:
                        return results
                dirs[:] = [d for d in dirs if not d.startswith(".")]
        return results
