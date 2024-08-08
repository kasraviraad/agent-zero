import asyncio
import inspect
from anthropic import AsyncAnthropic, RateLimitError, APIError
from plugin_system.vector_database import VectorDatabase
from plugin_system.plugin_manager import PluginManager
import numpy as np
from typing import Any, Optional

class SelfEvolvingAgent:
    def __init__(self, vector_db: VectorDatabase, developer_api_url: str, api_key: str):
        self.plugin_manager = PluginManager(vector_db, developer_api_url=developer_api_url)
        self.client = AsyncAnthropic(api_key=api_key)
        self.version = 1
        self.update_count = 0
        self.new_module_count = 0
        self.total_attempts = 0
        self.max_attempts = 3

    async def run(self):
        failures = 0
        while failures < self.max_attempts:
            try:
                prompt = await self.get_user_input()
                if prompt is None:
                    print("Exiting the program.")
                    break
                if prompt.lower() == 'exit':
                    print("Exiting the program.")
                    break
                if not prompt.strip():
                    print("Empty prompt. Please enter a valid prompt or 'exit'.")
                    continue

                print(f"Received prompt: {prompt}")  # Debug print
                success = await self.update_or_generate_code(prompt)
                if success:
                    failures = 0  # Reset failure count on success
                else:
                    failures += 1
                    print(f"Failed attempt {failures}/{self.max_attempts}")

                performance = self.analyze_performance()
                print(f"Performance Analysis: {performance}")

                if failures >= self.max_attempts:
                    print(f"Maximum failures ({self.max_attempts}) reached. Exiting.")
                    break

            except asyncio.CancelledError:
                print("\nOperation cancelled. Exiting gracefully.")
                break
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                failures += 1
                print(f"Failed attempt {failures}/{self.max_attempts}")
                if failures >= self.max_attempts:
                    print(f"Maximum failures ({self.max_attempts}) reached. Exiting.")
                    break

    async def get_user_input(self) -> Optional[str]:
        print("Enter a prompt to evolve the agent (or 'exit' to quit):")
        print("You can enter a multi-line prompt. Type '##END##' on a new line to finish:")
        lines = []
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.strip().lower() == 'exit':
                    return 'exit'
                if line.strip() == '##END##':
                    break
                lines.append(line)
            except EOFError:
                return None
            except KeyboardInterrupt:
                return None
        return '\n'.join(lines)

    async def get_claude_response(self, prompt) -> Optional[str]:
        max_wait_time = 60  # Maximum wait time in seconds
        for attempt in range(self.max_attempts):
            try:
                message = await self.client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
            except (RateLimitError, APIError) as e:
                print(f"Claude API error (Attempt {attempt + 1}/{self.max_attempts}): {e}")
                if attempt < self.max_attempts - 1:
                    wait_time = min(2 ** (attempt + 2), max_wait_time)
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print("Max attempts reached. Unable to get response from Claude.")
                    return None
            except Exception as e:
                print(f"Unexpected error (Attempt {attempt + 1}/{self.max_attempts}): {e}")
                if attempt < self.max_attempts - 1:
                    wait_time = min(2 ** (attempt + 2), max_wait_time)
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print("Max attempts reached. Unable to get response from Claude.")
                    return None
        return None

    async def update_or_generate_code(self, prompt) -> bool:
        self.total_attempts += 1
        try:
            current_source = inspect.getsource(self.__class__)
        except Exception as e:
            print(f"Error getting source code: {e}")
            current_source = "Unable to retrieve source code"

        code_prompt = f"""
        Based on the following prompt, either update the existing SelfEvolvingAgent class or generate a new module to be imported by the agent. If updating, provide the full updated class. If generating a new module, provide the full module code.

        Prompt: {prompt}

        Current SelfEvolvingAgent class:

        {current_source}

        Respond with:
        UPDATE if updating the main class, or
        NEW_MODULE: module_name if creating a new module, followed by the code.
        """

        response = await self.get_claude_response(code_prompt)
        if response is None:
            print("Failed to get a response from Claude.")
            return False

        if response.strip().startswith("UPDATE"):
            success = await self.update_self(response.strip()[7:])  # Remove "UPDATE\n"
        elif response.strip().startswith("NEW_MODULE"):
            module_name = response.split('\n')[0].split(': ')[1]
            module_code = '\n'.join(response.split('\n')[1:])
            success = await self.create_new_module(module_name, module_code)
        else:
            print("Unexpected response format from Claude.")
            success = False

        return success

    async def update_self(self, new_code) -> bool:
        # Implement the update logic here
        # Return True if successful, False otherwise
        print("Update self method called")  # Debug print
        return True

    async def create_new_module(self, module_name, module_code) -> bool:
        # Implement the new module creation logic here
        # Return True if successful, False otherwise
        print(f"Create new module method called: {module_name}")  # Debug print
        return True

    def analyze_performance(self):
        total_successes = self.update_count + self.new_module_count
        efficiency_score = total_successes / self.total_attempts if self.total_attempts > 0 else 0
        return {
            "updates": self.update_count,
            "new_modules": self.new_module_count,
            "total_attempts": self.total_attempts,
            "efficiency_score": efficiency_score
        }

    def shutdown(self):
        self.plugin_manager.shutdown()