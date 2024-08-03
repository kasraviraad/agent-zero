from helpers.tool import Tool, Response
import json

class TaskAdjuster(Tool):
    def execute(self, **kwargs):
        tasks = self.args.get("tasks", [])
        alignment_issues = self.args.get("alignment_issues", [])
        adjusted_tasks = self.adjust_tasks(tasks, alignment_issues)
        return Response(message=json.dumps(adjusted_tasks), break_loop=False)

    def adjust_tasks(self, tasks, alignment_issues):
        adjustment_prompt = f"Adjust these tasks to resolve the following alignment issues: Tasks: {json.dumps(tasks)}. Alignment issues: {json.dumps(alignment_issues)}"
        adjustment_result = self.agent.config.chat_model.generate(adjustment_prompt)
        
        # Parse the result to get adjusted tasks
        # This is a simplified example; you'd need more sophisticated parsing
        adjusted_tasks = json.loads(adjustment_result)
        
        return adjusted_tasks