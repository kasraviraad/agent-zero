import importlib
import importlib.util
import os
from typing import Dict, Any

class ModuleManager:
    def __init__(self, modules_dir: str = "custom_modules"):
        self.modules_dir = modules_dir
        self.modules: Dict[str, Any] = {}
        self.ensure_modules_dir()
        self.load_modules()

    def ensure_modules_dir(self):
        os.makedirs(self.modules_dir, exist_ok=True)

    def load_modules(self):
        if not os.path.exists(self.modules_dir):
            print(f"Modules directory '{self.modules_dir}' does not exist. No modules loaded.")
            return

        for filename in os.listdir(self.modules_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = os.path.join(self.modules_dir, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is not None and spec.loader is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.modules[module_name] = module

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