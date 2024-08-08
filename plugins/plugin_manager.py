# File: src/plugin_system/plugin_manager.py
import os
import importlib
from typing import Dict, Any, Optional
import numpy as np
from .plugin_base import Plugin
from .vector_database import VectorDatabase
from .plugin_request_system import PluginRequestSystem

class PluginManager:
    def __init__(self, vector_db: VectorDatabase, plugin_dir: str = "plugins", developer_api_url: str = "http://api.plugindeveloper.com"):
        self.vector_db = vector_db
        self.loaded_plugins: Dict[str, Plugin] = {}
        self.plugin_dir = plugin_dir
        os.makedirs(self.plugin_dir, exist_ok=True)
        self.request_system = PluginRequestSystem(developer_api_url)
    def load_plugin(self, plugin_name: str):
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        if os.path.exists(plugin_path):
            # Load the plugin from file
            plugin_module = __import__(f'plugins.{plugin_name}', fromlist=[plugin_name])
            plugin = getattr(plugin_module, plugin_name.capitalize())()
            self.loaded_plugins[plugin_name] = plugin
            return plugin
        else:
            # Plugin not found, could implement logic to request/generate it
            return None
    async def get_plugin(self, query_vector: np.ndarray, request_description: str) -> Optional[Plugin]:
        plugin_name = self.vector_db.find_plugin(query_vector)
        
        if not plugin_name:
            print("Plugin not found in database. Requesting from developer...")
            plugin_data = await self.request_system.request_plugin(query_vector, request_description)
            if plugin_data:
                self.vector_db.add_plugin(
                    plugin_data["name"],
                    plugin_data["description"],
                    plugin_data["code"],
                    np.array(plugin_data["vector"])
                )
                plugin_name = plugin_data["name"]
            else:
                print("Failed to obtain plugin from developer.")
                return None
        
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        local_plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        
        if os.path.exists(local_plugin_path):
            return self._load_local_plugin(plugin_name)
        else:
            return self._load_db_plugin(plugin_name)
    
        
    def _load_local_plugin(self, plugin_name: str) -> Plugin:
        module_name = f"plugins.{plugin_name}"
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, f"{plugin_name.capitalize()}Plugin")
        plugin_instance = plugin_class()
        plugin_instance.initialize()
        self.loaded_plugins[plugin_name] = plugin_instance
        return plugin_instance

    def _load_db_plugin(self, plugin_name: str) -> Plugin:
        plugin_data = self.vector_db.plugins[plugin_name]
        plugin_code = plugin_data["code"]
        
        plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        with open(plugin_path, "w") as f:
            f.write(plugin_code)
        
        return self._load_local_plugin(plugin_name)

    def execute_plugin(self, plugin_name: str, function_name: str, **kwargs):
        plugin = self.load_plugin(plugin_name)
        if plugin:
            if hasattr(plugin, function_name):
                return getattr(plugin, function_name)(**kwargs)
            else:
                raise AttributeError(f"Function {function_name} not found in plugin {plugin_name}")
        else:
            raise ValueError(f"Plugin {plugin_name} not found")
    
    def shutdown(self):
        for plugin in self.loaded_plugins.values():
            plugin.shutdown()
        self.loaded_plugins.clear()