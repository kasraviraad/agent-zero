from helpers.tool import Tool, Response
import json

class AlignmentChecker(Tool):
    def execute(self, **kwargs):
        tasks = kwargs.get('tasks', [])
        original_objective = kwargs.get('original_objective', '')
        alignment_issues = self.check_alignment(tasks, original_objective)
        if alignment_issues:
            return Response(message=json.dumps(alignment_issues), break_loop=False)
        return Response(message="All tasks aligned with objectives", break_loop=False)

    def check_alignment(self, tasks, original_objective):
        prompt = f"Check if these tasks align with the original objective. Original objective: {original_objective}. Tasks: {json.dumps(tasks)}"
        result = self.agent.config.chat_model.generate(prompt)
        # Parse the result to identify any alignment issues
        # This is a simplified example; you'd need more sophisticated parsing
        return [issue.strip() for issue in result.split("\n") if "misalignment" in issue.lower()]