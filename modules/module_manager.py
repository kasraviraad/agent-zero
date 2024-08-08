import importlib
import importlib.util
import os
from typing import Dict, Any
from plugins.plugin_manager import PluginManager
class ModuleManager:
    def __init__(self, modules_dir: str = "custom_modules"):
        self.modules_dir = modules_dir
        self.modules: Dict[str, Any] = {}
        self.ensure_modules_dir()
        self.load_modules()
        # Existing initialization code
        self.modules = {}  # Dictionary to store loaded modules
        self.plugin_manager = PluginManager(vector_db)

    def ensure_modules_dir(self):
        os.makedirs(self.modules_dir, exist_ok=True)

    def load_module(self, module_name: str):
        if module_name in self.modules:
            return self.modules[module_name]
        
        try:
            # Attempt to load as a regular module
            module = self._load_regular_module(module_name)
            self.modules[module_name] = module
            return module
        except ImportError:
            # If regular module not found, try loading as a plugin
            return self.plugin_manager.load_plugin(module_name)
    def _load_regular_module(self, module_name: str):
        # Implementation for loading a regular module
        # This could involve importing from a predefined modules directory
        # For example:
        module = __import__(f'modules.{module_name}', fromlist=[module_name])
        return getattr(module, module_name.capitalize())()
    def get_module(self, module_name: str) -> Any:
        return self.modules.get(module_name)

    def create_module(self, module_name: str, module_code: str):
        module_path = os.path.join(self.modules_dir, f"{module_name}.py")
        with open(module_path, "w") as f:
            f.write(module_code)
        
        # Reload the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            if spec.loader is not None:
                spec.loader.exec_module(module)
                self.modules[module_name] = module
                return module
        
        raise ImportError(f"Failed to create module {module_name}")

    def remove_module(self, module_name: str):
        if module_name in self.modules:
            del self.modules[module_name]
            module_path = os.path.join(self.modules_dir, f"{module_name}.py")
            if os.path.exists(module_path):
                os.remove(module_path)

    def __str__(self):
        return f"ModuleManager(modules: {list(self.modules.keys())})"