# File: src/plugin_system/plugin_base.py
from abc import ABC, abstractmethod
from typing import Any

class Plugin(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass

    @abstractmethod
    def shutdown(self):
        pass