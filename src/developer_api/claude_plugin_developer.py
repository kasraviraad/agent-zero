from anthropic import AsyncAnthropic
import numpy as np
from typing import Dict, Any

class ClaudePluginDeveloper:
    def __init__(self, api_key):
        self.client = AsyncAnthropic(api_key=api_key)
        self.plugin_counter = 0

    async def generate_plugin(self, query_vector: np.ndarray, description: str) -> Dict[str, Any]:
        self.plugin_counter += 1
        plugin_name = f"generated_plugin_{self.plugin_counter}"
        
        prompt = f"""
        Create a Python plugin named {plugin_name} that does the following:

        Description: {description}

        The plugin should inherit from the Plugin base class and implement the following methods:
        1. __init__
        2. initialize
        3. execute
        4. shutdown

        Provide the full Python code for this plugin.
        """

        try:
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            plugin_code = message.content[0].text
        except Exception as e:
            print(f"Error getting response from Claude: {e}")
            return None

        # Extract the Python code from the response
        plugin_code = self._extract_python_code(plugin_code)
        
        if not plugin_code:
            print("Failed to generate valid plugin code.")
            return None

        return {
            "name": plugin_name,
            "description": description,
            "code": plugin_code,
            "vector": query_vector.tolist()
        }

    def _extract_python_code(self, response: str) -> str:
        # Extract code between triple backticks
        import re
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        else:
            # If no code blocks, return the entire response
            return response.strip()

# Simulated API endpoint
async def request_plugin_endpoint(api_key: str, query_vector: np.ndarray, description: str) -> Dict[str, Any]:
    developer = ClaudePluginDeveloper(api_key)
    return await developer.generate_plugin(query_vector, description)