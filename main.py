import asyncio
import sys
import threading
import time
import os
import json
from ansio import application_keypad, mouse_input, raw_input
from ansio.input import InputEvent, get_input_event
from agent import Agent, AgentConfig
from agi_node import AGINode, create_agi_node
from helpers.print_style import PrintStyle
from helpers.files import read_file
from helpers import files
import helpers.timed_input as timed_input
from python.tools.task_adjuster import TaskAdjuster
from dotenv import load_dotenv
import models
import pysqlite3
import sqlite3
print(f"SQLite version: {sqlite3.sqlite_version}")
sys.modules['sqlite3'] = pysqlite3
load_dotenv()
print(os.getenv('OPENAI_API_KEY'))
with open('.env', 'r') as f:
    print(f.read())
work_dir = files.get_abs_path("work_dir")
os.makedirs(work_dir, exist_ok=True)
input_lock = threading.Lock()
os.chdir(files.get_abs_path("./work_dir")) #change CWD to work_dir

def load_objectives():
    objectives_path = "prompts/objective.md"
    try:
        content = files.read_file(objectives_path)
        print(f"Successfully loaded objectives from {files.get_abs_path(objectives_path)}")
        return content
    except FileNotFoundError:
        print(f"Warning: Objectives file not found at {files.get_abs_path(objectives_path)}. Using default objectives.")
        return """
        # Default AGI Objectives

        1. Continuous Learning: Constantly acquire and integrate new knowledge.
        2. Problem Solving: Develop and improve general problem-solving capabilities.
        3. Adaptive Reasoning: Enhance ability to reason and adapt to new situations.
        4. Ethical Decision Making: Make decisions that align with ethical principles.
        5. Efficient Resource Management: Optimize use of computational and memory resources.
        6. Human Collaboration: Improve ability to interact and collaborate with humans effectively.
        7. Self-Improvement: Continuously work on enhancing own capabilities and efficiency.
        """

def initialize():
    print("Initializing framework...")
    try:
        # main chat model used by agents (smarter, more accurate)
        chat_llm = models.get_openai_chat(temperature=0)

        # utility model used for helper functions (cheaper, faster)
        utility_llm = models.get_openai_chat(temperature=0)
        
        # embedding model used for memory
        embedding_llm = models.get_embedding_openai()

        # agent configuration
        config = AgentConfig(
            chat_model = chat_llm,
            utility_model = utility_llm,
            embeddings_model = embedding_llm,
            auto_memory_count = 0,
            code_exec_docker_enabled = True,
            code_exec_ssh_enabled = True,
        )
        
        # create the main agent
        main_agent = create_agi_node(host='localhost', port=8080)

        # Load objectives
        objectives = load_objectives()
        main_agent.set_data("objectives", objectives)
        
        return main_agent
    except ValueError as e:
        print(f"Error during initialization: {e}")
        return None

async def decompose_and_execute_objectives(agent):
    objectives = agent.get_data("objectives")
    decomposition_result = await agent.message_loop(json.dumps({
        "thoughts": ["I need to decompose the main objectives into subtasks."],
        "tool_name": "objective_decomposer",
        "tool_args": {"objectives": objectives}
    }))
    
    # Process the decomposed objectives and tasks
    await process_decomposed_tasks(agent, json.loads(decomposition_result), objectives)

async def process_decomposed_tasks(agent, tasks, original_objective):
    alignment_checker = agent.get_tool("AlignmentChecker")
    alignment_issues = await alignment_checker.execute(tasks, original_objective)
    
    if alignment_issues:
        # Handle alignment issues, possibly by re-decomposing or adjusting tasks
        print("Alignment issues detected. Adjusting tasks...")
        tasks = await adjust_tasks(agent, tasks, alignment_issues)
    
    for task in tasks:
        if task["type"] == "executable":
            await execute_task(agent, task)
        elif task["type"] == "needs_tool":
            await create_tool(agent, task)
        else:
            await further_decompose(agent, task)

async def execute_task(agent, task):
    print(f"Executing task: {task['description']}")
    result = await agent.message_loop(json.dumps({
        "thoughts": ["Executing the following task:", task['description']],
        "tool_name": "code_execution_tool",
        "tool_args": {"runtime": "python", "code": task['code']}
    }))
    print(f"Task result: {result}")

async def create_tool(agent, task):
    print(f"Creating tool for task: {task['description']}")
    result = await agent.message_loop(json.dumps({
        "thoughts": ["Creating a new tool for the following task:", task['description']],
        "tool_name": "tool_creator",
        "tool_args": {"tool_description": task['description']}
    }))
    print(f"Tool creation result: {result}")

async def further_decompose(agent, task):
    print(f"Further decomposing task: {task['description']}")
    subtasks = await agent.decompose_objective(task['description'])
    await process_decomposed_tasks(agent, subtasks, task['description'])

async def adjust_tasks(agent, tasks, alignment_issues):
    print("Adjusting tasks based on alignment issues...")
    adjustment_result = await agent.message_loop(json.dumps({
        "thoughts": ["Adjusting tasks based on the following alignment issues:", str(alignment_issues)],
        "tool_name": "task_adjuster",
        "tool_args": {"tasks": tasks, "alignment_issues": alignment_issues}
    }))
    return json.loads(adjustment_result)

async def main():
    main_agent = initialize()
    if main_agent is None:
        print("Failed to initialize the agent. Exiting.")
        return
    
    await main_agent.start()
    
    # Decompose and execute objectives
    await decompose_and_execute_objectives(main_agent)
    
    try:
        while True:
            await main_agent.run_cycle()
            if main_agent.get_data("stop_requested"):
                print("Stop requested. Shutting down...")
                break
    finally:
        # Perform any cleanup here
        await main_agent.cleanup()

# User intervention during agent processing
def intervention():
    if Agent.streaming_agent and not Agent.paused:
        Agent.paused = True # stop agent processing
        PrintStyle(background_color="#6C3483", font_color="white", bold=True, padding=True).print(f"User intervention ('e' to leave, empty to continue):")        

        import readline # this fixes arrow keys in terminal
        user_input = input("> ").strip()
        PrintStyle(font_color="white", padding=False, log_only=True).print(f"> {user_input}")        
        
        if user_input.lower() == 'e': 
            if isinstance(Agent.streaming_agent, AGINode):
                Agent.streaming_agent.request_stop()  # Call request_stop if it's an AGINode
            else:
                print("Warning: streaming_agent is not an AGINode, cannot request stop.")
        if user_input: Agent.streaming_agent.intervention_message = user_input # set intervention message if non-empty
        Agent.paused = False # continue agent processing

# Capture keyboard input to trigger user intervention
def capture_keys():
    global input_lock
    intervent = False            
    while True:
        if intervent: intervention()
        intervent = False
        time.sleep(0.1)
        
        if Agent.streaming_agent:
            with input_lock, raw_input, application_keypad:
                event: InputEvent | None = get_input_event(timeout=0.1)
                if event and (event.shortcut.isalpha() or event.shortcut.isspace()):
                    intervent = True
                    continue

if __name__ == "__main__":
    print("Initializing framework...")

    # Start the key capture thread for user intervention during agent processing
    threading.Thread(target=capture_keys, daemon=True).start()

    # Start the AGI development process
    asyncio.run(main())