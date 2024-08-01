from python.helpers.tool import Tool, Response

class ToolCreator(Tool):
    def execute(self, tool_description, **kwargs):
        tool_code = self.generate_tool_code(tool_description)
        self.save_tool(tool_code)
        return Response(message=f"Tool created: {tool_description}", break_loop=False)

    def generate_tool_code(self, description):
        prompt = f"Generate Python code for a tool that does the following: {description}"
        return self.agent.config.chat_model.generate(prompt)

    def save_tool(self, code):
        # Logic to save the generated tool code
        pass