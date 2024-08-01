class ObjectiveDecomposer(Tool):
    def execute(self, objectives, **kwargs):
        decomposed_tasks = self.decompose_objectives(objectives)
        return Response(message=json.dumps(decomposed_tasks), break_loop=False)

    def decompose_objectives(self, objectives):
        decomposition_prompt = f"Decompose these objectives into subtasks: {objectives}"
        decomposition_result = self.agent.config.chat_model.generate(decomposition_prompt)
        
        tasks = []
        for task_description in decomposition_result.split("\n"):
            if task_description.strip():
                task_type = self.classify_task(task_description)
                task = {"description": task_description.strip(), "type": task_type}
                if task_type == "executable":
                    task["code"] = self.generate_task_code(task_description)
                tasks.append(task)
        
        return tasks

    def classify_task(self, task):
        if "create tool" in task.lower():
            return "needs_tool"
        elif any(keyword in task.lower() for keyword in ["analyze", "compute", "calculate"]):
            return "executable"
        else:
            return "needs_decomposition"

    def generate_task_code(self, task_description):
        code_prompt = f"Generate Python code to accomplish this task: {task_description}"
        return self.agent.config.chat_model.generate(code_prompt)