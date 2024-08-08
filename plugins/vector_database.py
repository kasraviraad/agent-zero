import numpy as np
from typing import Dict, Any, Optional

class VectorDatabase:
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.vectors: Dict[str, np.ndarray] = {}

    def add_plugin(self, name: str, description: str, code: str, vector: np.ndarray):
        self.plugins[name] = {"description": description, "code": code}
        self.vectors[name] = vector

    def find_plugin(self, query_vector: np.ndarray) -> Optional[str]:
        if not self.vectors:
            return None
        
        similarities = {name: np.dot(query_vector, plugin_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(plugin_vector))
                        for name, plugin_vector in self.vectors.items()}
        
        return max(similarities, key=similarities.get) if similarities else None