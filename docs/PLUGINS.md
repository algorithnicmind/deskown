# DeskOwn — Plugin System

## Overview

DeskOwn uses a plugin system for task automation. Each plugin handles a category of commands (e.g., opening apps, searching files).

---

## Plugin Architecture

```
User types: "open chrome"
         │
         ▼
┌─────────────────┐
│   TaskRunner    │
│ .match(command) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AppLauncher    │
│ .execute(cmd)   │
└────────┬────────┘
         │
         ▼
   Result: "Notepad opened"
```

---

## Plugin Interface

Every plugin must define a `Plugin` class with these attributes:

```python
class Plugin:
    """Base plugin interface."""
    name: str                    # Unique identifier
    description: str             # Human-readable description
    patterns: list[str]          # Regex patterns to match commands

    def match(self, command: str) -> bool:
        """Check if this plugin handles the command."""
        ...

    def execute(self, command: str, context: dict) -> str:
        """Execute the command and return result text."""
        ...
```

### `context` Dictionary

Passed to `execute()`:

```python
context = {
    "ai_engine": AIEngine,      # Access to chat
    "voice_engine": VoiceEngine, # Access to TTS
    "task_runner": TaskRunner,   # Access to other plugins
    "config": config,            # App configuration
}
```

---

## Writing a New Plugin

### Step 1: Create the File

Create a new Python file in `plugins/`:

```
plugins/my_plugin.py
```

### Step 2: Define the Plugin Class

```python
import re
from plugins import Plugin


class Plugin:
    name = "my_plugin"
    description = "Does something cool"
    patterns = [
        r"do something (.+)",
        r"run (.+)",
    ]

    def match(self, command: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command: str, context: dict) -> str:
        match = re.search(self.patterns[0], command, re.IGNORECASE)
        if match:
            arg = match.group(1)
            return f"Did something with: {arg}"
        return "No match found"
```

### Step 3: Restart DeskOwn

The plugin is automatically discovered on startup.

---

## Built-in Plugins

### 1. App Launcher (`app_launcher.py`)

Opens applications by name.

**Patterns:**
- `open (.+)`
- `launch (.+)`
- `start (.+)`

**Examples:**
```
"open chrome"        → Opens Google Chrome
"launch vscode"      → Opens Visual Studio Code
"start notepad"      → Opens Notepad
"open calculator"    → Opens Calculator
```

**How it works:**
1. Maps common app names to executable paths
2. Falls back to Windows `start` command
3. Uses `subprocess.Popen` for non-blocking launch

**App Name Mapping:**
```python
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
}
```

---

### 2. File Search (`file_search.py`)

Finds files on disk.

**Patterns:**
- `find (.+)`
- `search for (.+)`
- `locate (.+)`
- `find file (.+)`

**Examples:**
```
"find readme.md"          → Lists all readme.md files
"search for *.py"         → Lists all Python files
"locate config.json"      → Finds config.json
```

**How it works:**
1. Uses `os.walk()` to traverse directories
2. Supports glob patterns (`*.py`, `*.txt`)
3. Searches common locations (Desktop, Documents, Downloads)
4. Returns list of matching file paths

**Search Locations:**
```python
SEARCH_DIRS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~"),
]
```

---

### 3. Web Search (`web_search.py`)

Opens a web search in the default browser.

**Patterns:**
- `search for (.+)`
- `google (.+)`
- `look up (.+)`
- `find online (.+)`

**Examples:**
```
"search for python tutorials"  → Opens DuckDuckGo search
"google machine learning"       → Opens Google search
"look up PyQt6 docs"           → Opens DuckDuckGo search
```

**How it works:**
1. URL-encodes the search query
2. Opens DuckDuckGo in default browser
3. Uses `webbrowser.open()`

**Search URL:**
```python
search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
webbrowser.open(search_url)
```

---

## Task Runner Integration

The `TaskRunner` in `core/task_runner.py` manages all plugins:

```python
from core.task_runner import TaskRunner

runner = TaskRunner()

# Match a command
plugin = runner.match("open chrome")
if plugin:
    result = plugin.execute("open chrome", context)
    print(result)  # "Chrome opened"

# List all plugins
for p in runner.list_plugins():
    print(f"{p['name']}: {p['description']}")
```

### Command Flow

```
1. User types command in chat or voice
2. TaskRunner.match(command) checks each plugin
3. First matching plugin is selected
4. plugin.execute(command, context) runs
5. Result returned to user
```

### Plugin Priority

Plugins are checked in alphabetical order. First match wins.

If no plugin matches, the command is sent to the AI engine as a regular chat message.

---

## Example: Calculator Plugin

Here's a complete example of a custom plugin:

```python
import re
import math


class Plugin:
    name = "calculator"
    description = "Calculate math expressions"
    patterns = [
        r"calculate (.+)",
        r"compute (.+)",
        r"what is (\d+[\+\-\*\/]\d+)",
    ]

    def match(self, command: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command: str, context: dict) -> str:
        # Extract the math expression
        for pattern in self.patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                expr = match.group(1)
                try:
                    # Safe evaluation (no eval()!)
                    result = self._safe_calc(expr)
                    return f"Result: {result}"
                except Exception as e:
                    return f"Error: {e}"
        return "Could not parse expression"

    def _safe_calc(self, expr: str) -> float:
        """Safely evaluate a math expression."""
        # Only allow numbers and basic operators
        allowed = set("0123456789+-*/.().")
        if not all(c in allowed for c in expr):
            raise ValueError("Invalid characters in expression")

        # Use compile/eval with restricted globals
        code = compile(expr, "<string>", "eval")
        return eval(code, {"__builtins__": {}}, {
            "abs": abs, "round": round,
            "sqrt": math.sqrt, "pow": pow,
        })
```

---

## Tips

1. **Keep plugins simple** — one responsibility per plugin
2. **Use regex patterns** — flexible command matching
3. **Return clear messages** — users see the result text
4. **Handle errors gracefully** — never crash
5. **Test patterns** — make sure they match intended commands
