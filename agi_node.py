import uuid
import asyncio
from typing import Optional
from modules.network_communication import NetworkCommunication
from modules.knowledge_base import KnowledgeBase
from modules.objective_handler import ObjectiveHandler, Objective
from modules.module_manager import ModuleManager
from modules.decision_maker import DecisionMaker
from modules.module_generator import ModuleGenerator
from modules.knowledge_tool import Knowledge  # Add this import
from modules.knowledge_base import KnowledgeBase  # Add this import
from agent import Agent , AgentConfig  # Add this import
import models  # Import the models module


class AGINode(Agent):
    def __init__(self, host='localhost', port=8080):
        config = AgentConfig(
            chat_model=models.get_openai_chat(temperature=0),
            utility_model=models.get_openai_chat(temperature=0),
            embeddings_model=models.get_embedding_openai()
        )
        super().__init__(number=0,config=config)
        self.id = f"AGI-Node-{uuid.uuid4()}"
        self.network = NetworkCommunication(host, port)
        self.knowledge_base = KnowledgeBase()
        self.objectives = ObjectiveHandler()
        self.modules = ModuleManager(modules_dir="custom_modules")
        self.decision_maker = DecisionMaker(self.knowledge_base, self.objectives)
        self.module_generator = ModuleGenerator(self.knowledge_base, self.objectives)
        self.knowledge_tool: Optional[Knowledge] = None
    def initialize_knowledge_tool(self):
        self.knowledge_tool = Knowledge(agent=self, name="knowledge", args={}, message="")
    def request_stop(self):
        self.set_data("stop_requested", True)
    async def cleanup(self):
        # Perform any necessary cleanup here
        print(f"Cleaning up AGINode {self.id}")
        # Add any other cleanup tasks here
    async def start(self):
        await self.network.start()
        await self.join_network()
        await self.sync_knowledge()
        await self.align_objectives()
        print(f"AGI Node {self.id} has started and is ready for operation.")
    
    async def join_network(self):
        print(f"Node {self.id} is attempting to join the network...")

    async def sync_knowledge(self):
        self.knowledge_base.add_knowledge("problem_solving_techniques", "brainstorming, root cause analysis")
        self.knowledge_base.add_knowledge("knowledge_expansion_methods", "research, experimentation, collaboration")
        print(f"Node {self.id} synchronized knowledge.")

    async def align_objectives(self):
        self.objectives.add_objective(Objective("Improve problem-solving skills", 2))
        self.objectives.add_objective(Objective("Expand knowledge base", 1))
        print(f"Node {self.id} aligned objectives.")

    async def run_cycle(self):
        print(f"\nNode {self.id} running cycle:")
        print(f"Knowledge: {self.knowledge_base}")
        print(f"Objectives: {self.objectives}")
        print(f"Modules: {self.modules}")

        decision = self.decision_maker.make_decision()
        print(f"Decision: {decision}")

        if decision['action'] == 'acquire_knowledge' and self.knowledge_tool is not None:
            response = self.knowledge_tool.execute(question=decision['query'])
            print(f"Acquired knowledge: {response.message}")
            # Update knowledge base with new information
            self.knowledge_base.add_knowledge(decision['query'], response.message)
        else:
            # Execute other types of actions
            await self.execute_action(decision['action'])

        overall_progress = self.objectives.evaluate_overall_progress()
        print(f"Overall progress: {overall_progress:.2f}")

        await asyncio.sleep(5)  # Wait for 5 seconds before the next cycle
    
    async def create_custom_module(self, module_name: str, objective: str):
        print(f"Generating custom module: {module_name}")
        module_code = await self.module_generator.generate_module(module_name, objective)
        self.modules.create_module(module_name, module_code)
        print(f"Created custom module: {module_name}")

    async def execute_action(self, action: str):
        print(f"Executing action: {action}")
        
        action_parts = action.split('_')
        action_type = action_parts[0]
        objective_description = '_'.join(action_parts[1:])

        if action_type == 'work_on':
            module_name = objective_description.replace(' ', '_')
            module = self.modules.get_module(module_name)
            if not module:
                await self.create_custom_module(module_name, objective_description)
                module = self.modules.get_module(module_name)
            
            if module:
                try:
                    result = getattr(module, f"solve_{module_name}")(self.knowledge_base, self.objectives)
                    print(f"{module_name.capitalize()} module result: {result}")
                    self.knowledge_base.add_knowledge(f"{objective_description}_result", result)
                except AttributeError:
                    print(f"Module {module_name} doesn't have a solve_{module_name} method")
            else:
                print(f"Failed to create or retrieve module for {objective_description}")
        
        elif action_type == 'research':
            research_result = f"New insights on {objective_description.replace('_', ' ')}"
            self.knowledge_base.add_knowledge(f"research_result_{objective_description}", research_result)
            print(f"Research completed: {research_result}")
        
        elif action_type == 'finalize':
            finalize_result = f"Finalized work on {objective_description.replace('_', ' ')}"
            self.knowledge_base.add_knowledge(f"finalize_result_{objective_description}", finalize_result)
            print(f"Finalization completed: {finalize_result}")
        
        else:
            print(f"Unknown action type: {action_type}")

        # Update progress
        for obj in self.objectives.objectives:
            if obj.description.lower() == objective_description.replace('_', ' ').lower():
                current_progress = obj.progress
                new_progress = min(current_progress + 0.2, 1.0)  # Increment progress by 20%
                self.objectives.update_progress(obj.description, new_progress)
                break

        # Simulate some time passing
        await asyncio.sleep(1)  

def create_agi_node(host='localhost', port=8080) -> AGINode:
    node = AGINode(host, port)
    node.initialize_knowledge_tool()
    return node
# Usage
async def main():
    node = create_agi_node()
    await node.start()
    while True:
        await node.run_cycle()

if __name__ == "__main__":
    asyncio.run(main())