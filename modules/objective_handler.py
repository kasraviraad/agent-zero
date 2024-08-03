import json
from typing import List, Dict, Any, Optional

class Objective:
    def __init__(self, description: str, priority: int = 1, progress: float = 0.0):
        self.description = description
        self.priority = priority
        self.progress = progress

    def __str__(self):
        return f"Objective(description: {self.description}, priority: {self.priority}, progress: {self.progress:.2f})"

class ObjectiveHandler:
    def __init__(self):
        self.objectives: List[Objective] = []

    def add_objective(self, objective: Objective):
        self.objectives.append(objective)
        self.objectives.sort(key=lambda x: x.priority, reverse=True)

    def remove_objective(self, description: str):
        self.objectives = [obj for obj in self.objectives if obj.description != description]

    def get_top_objective(self) -> Optional[Objective]:
        return self.objectives[0] if self.objectives else None

    def update_progress(self, description: str, progress: float):
        for obj in self.objectives:
            if obj.description == description:
                obj.progress = min(max(progress, 0.0), 1.0)  # Ensure progress is between 0 and 1
                break

    def evaluate_overall_progress(self) -> float:
        if not self.objectives:
            return 1.0  # If there are no objectives, we consider everything complete
        total_priority = sum(obj.priority for obj in self.objectives)
        weighted_progress = sum(obj.progress * obj.priority for obj in self.objectives)
        return weighted_progress / total_priority if total_priority > 0 else 1.0

    def serialize(self) -> str:
        return json.dumps([{
            "description": obj.description, 
            "priority": obj.priority,
            "progress": obj.progress
        } for obj in self.objectives])

    @classmethod
    def deserialize(cls, serialized_data: str):
        handler = cls()
        objectives_data = json.loads(serialized_data)
        for obj_data in objectives_data:
            handler.add_objective(Objective(
                obj_data["description"], 
                obj_data["priority"],
                obj_data.get("progress", 0.0)
            ))
        return handler

    def align_objectives(self, peer_objectives: List[Dict[str, Any]]):
        # This is a simple alignment strategy. In a real-world scenario, 
        # this would involve more complex negotiation and consensus algorithms.
        new_objectives = [Objective(
            obj["description"], 
            obj["priority"],
            obj.get("progress", 0.0)
        ) for obj in peer_objectives]
        
        # Merge objectives, keeping the highest priority and progress for each
        merged_objectives = {}
        for obj in self.objectives + new_objectives:
            if obj.description in merged_objectives:
                existing = merged_objectives[obj.description]
                existing.priority = max(existing.priority, obj.priority)
                existing.progress = max(existing.progress, obj.progress)
            else:
                merged_objectives[obj.description] = obj
        
        self.objectives = list(merged_objectives.values())
        self.objectives.sort(key=lambda x: x.priority, reverse=True)

    def __str__(self):
        return f"ObjectiveHandler(objectives: {len(self.objectives)}, overall progress: {self.evaluate_overall_progress():.2f})"