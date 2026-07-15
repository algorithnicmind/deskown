import importlib
import os
import pkgutil

class TaskRunner:
    def __init__(self, plugin_dir: str = None):
        self.plugin_dir = plugin_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "plugins"
        )
        self.plugins = []
        self._discover_plugins()

    def _discover_plugins(self):
        self.plugins = []
        if not os.path.exists(self.plugin_dir):
            return

        for _, module_name, _ in pkgutil.iter_modules([self.plugin_dir]):
            if module_name.startswith("_"):
                continue
            try:
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "Plugin"):
                    plugin_class = module.Plugin
                    plugin_instance = plugin_class()
                    self.plugins.append(plugin_instance)
            except Exception as e:
                print(f"Failed to load plugin {module_name}: {e}")

    def get_ollama_tools(self) -> list[dict]:
        """Returns the list of tool schemas for Ollama."""
        tools = []
        for plugin in self.plugins:
            if hasattr(plugin, "get_tools"):
                tools.extend(plugin.get_tools())
        return tools

    def execute_tool(self, tool_name: str, arguments: dict, context: dict = None) -> str:
        """Executes a specific tool by routing it to the appropriate plugin."""
        context = context or {}
        for plugin in self.plugins:
            # Check if this plugin owns the tool
            if hasattr(plugin, "get_tools"):
                for tool in plugin.get_tools():
                    if tool.get("function", {}).get("name") == tool_name:
                        try:
                            if hasattr(plugin, "execute_tool"):
                                return str(plugin.execute_tool(tool_name, arguments, context))
                            else:
                                return f"Plugin {plugin.name} lacks execute_tool method."
                        except Exception as e:
                            return f"Error executing {tool_name}: {e}"
        return f"Tool {tool_name} not found."

    def list_plugins(self) -> list[dict]:
        return [
            {"name": p.name, "description": p.description}
            for p in self.plugins if hasattr(p, "name")
        ]

    def reload_plugins(self):
        self._discover_plugins()
