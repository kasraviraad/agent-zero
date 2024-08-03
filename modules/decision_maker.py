from typing import List, Dict, Any
from modules.knowledge_base import KnowledgeBase
from modules.objective_handler import ObjectiveHandler, Objective

class DecisionMaker:
    def __init__(self, knowledge_base: KnowledgeBase, objective_handler: ObjectiveHandler):
        self.knowledge_base = knowledge_base
        self.objective_handler = objective_handler

    def make_decision(self) -> Dict[str, Any]:
        top_objective = self.objective_handler.get_top_objective()
        if not top_objective:
            return {"action": "idle", "reason": "No objectives available"}

        relevant_knowledge = self.get_relevant_knowledge(top_objective)
        action = self.determine_action(top_objective, relevant_knowledge)

        return {
            "action": action,
            "objective": str(top_objective),
            "reason": f"Based on objective and relevant knowledge: {relevant_knowledge}"
        }

    def get_relevant_knowledge(self, objective: Objective) -> List[str]:
        # This is a simplified version. In a more advanced system,
        # this would involve more sophisticated knowledge retrieval.
        return [
            value for key, value in self.knowledge_base.knowledge.items()
            if objective.description.lower() in key.lower()
        ]

    def determine_action(self, objective: Objective, relevant_knowledge: List[str]) -> str:
        # This is a placeholder for more complex decision-making logic
        if not relevant_knowledge:
            return f"research_{objective.description.replace(' ', '_')}"
        elif objective.progress < 0.5:
            return f"work_on_{objective.description.replace(' ', '_')}"
        else:
            return f"finalize_{objective.description.replace(' ', '_')}"