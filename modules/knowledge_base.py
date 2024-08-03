import json
from typing import Dict, Any, Optional

class KnowledgeBase:
    def __init__(self, initial_knowledge: Optional[Dict[str, Any]] = None):
        self.knowledge: Dict[str, Any] = initial_knowledge if initial_knowledge is not None else {}

    def add_knowledge(self, key: str, value: Any):
        self.knowledge[key] = value

    def get_knowledge(self, key: str) -> Any:
        return self.knowledge.get(key)

    def update_knowledge(self, new_knowledge: Dict[str, Any]):
        self.knowledge.update(new_knowledge)

    def serialize(self) -> str:
        return json.dumps(self.knowledge)

    @classmethod
    def deserialize(cls, serialized_data: str):
        return cls(json.loads(serialized_data))

    def sync_with_peer(self, peer_knowledge: Dict[str, Any]):
        for key, value in peer_knowledge.items():
            if key not in self.knowledge or self.knowledge[key] != value:
                self.knowledge[key] = value
        # Here, we might want to add more sophisticated merging logic in the future

    def __str__(self):
        return f"KnowledgeBase(items: {len(self.knowledge)})"