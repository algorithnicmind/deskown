import os
import re
import fnmatch


class Plugin:
    name = "file_search"
    description = "Find files on disk"
    patterns = [
        r"find (.+)",
        r"search for (.+)",
        r"locate (.+)",
        r"find file (.+)",
    ]

    SEARCH_DIRS = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~"),
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
                results = self._search(query)
                if results:
                    return f"Found {len(results)} file(s):\n" + "\n".join(results[:10])
                return f"No files found matching '{query}'"
        return "Could not parse search query"

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
