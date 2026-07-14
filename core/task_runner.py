import importlib
import os
import pkgutil
import re

import config


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

    def match(self, command: str):
        for plugin in self.plugins:
            if plugin.match(command):
                return plugin
        return None

    def execute(self, command: str, context: dict = None) -> str:
        context = context or {}
        plugin = self.match(command)
        if plugin:
            try:
                return plugin.execute(command, context)
            except Exception as e:
                return f"Plugin error: {e}"
        return ""

    def list_plugins(self) -> list[dict]:
        return [
            {"name": p.name, "description": p.description}
            for p in self.plugins
        ]

    def reload_plugins(self):
        self._discover_plugins()
