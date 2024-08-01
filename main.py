import threading, time, models, os, json
from ansio import application_keypad, mouse_input, raw_input
from ansio.input import InputEvent, get_input_event
from agent import Agent, AgentConfig
from python.helpers.print_style import PrintStyle
from python.helpers.files import read_file
from python.helpers import files
import python.helpers.timed_input as timed_input
from python.tools.task_adjuster import TaskAdjuster
from python.tools.AlignmentChecker import AlignmentChecker
input_lock = threading.Lock()
os.chdir(files.get_abs_path("./work_dir")) #change CWD to work_dir


def load_objectives():
    objectives_path = os.path.join("prompts", "objective.md")
    return files.read_file(objectives_path)

def initialize():
    print("Initializing framework...")

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
    main_agent = Agent(number=0, config=config)

    # Load objectives
    objectives = load_objectives()
    main_agent.set_data("objectives", objectives)
    
    # Start the objective decomposition process
    decompose_and_execute_objectives(main_agent)

def decompose_and_execute_objectives(agent):
    objectives = agent.get_data("objectives")
    decomposition_result = agent.message_loop(json.dumps({
        "thoughts": ["I need to decompose the main objectives into subtasks."],
        "tool_name": "objective_decomposer",
        "tool_args": {"objectives": objectives}
    }))
    
    # Process the decomposed objectives and tasks
    process_decomposed_tasks(agent, json.loads(decomposition_result), objectives)

def process_decomposed_tasks(agent, tasks, original_objective):
    alignment_checker = AlignmentChecker(agent)
    alignment_issues = alignment_checker.execute(tasks, original_objective)
    
    if alignment_issues:
        # Handle alignment issues, possibly by re-decomposing or adjusting tasks
        print("Alignment issues detected. Adjusting tasks...")
        tasks = adjust_tasks(agent, tasks, alignment_issues)
    
    for task in tasks:
        if task["type"] == "executable":
            execute_task(agent, task)
        elif task["type"] == "needs_tool":
            create_tool(agent, task)
        else:
            further_decompose(agent, task)

def execute_task(agent, task):
    print(f"Executing task: {task['description']}")
    result = agent.message_loop(json.dumps({
        "thoughts": ["Executing the following task:", task['description']],
        "tool_name": "code_execution_tool",
        "tool_args": {"runtime": "python", "code": task['code']}
    }))
    print(f"Task result: {result}")

def create_tool(agent, task):
    print(f"Creating tool for task: {task['description']}")
    result = agent.message_loop(json.dumps({
        "thoughts": ["Creating a new tool for the following task:", task['description']],
        "tool_name": "tool_creator",
        "tool_args": {"tool_description": task['description']}
    }))
    print(f"Tool creation result: {result}")

def further_decompose(agent, task):
    print(f"Further decomposing task: {task['description']}")
    subtasks = agent.decompose_objective(task['description'])
    process_decomposed_tasks(agent, subtasks, task['description'])

def adjust_tasks(agent, tasks, alignment_issues):
    print("Adjusting tasks based on alignment issues...")
    adjustment_result = agent.message_loop(json.dumps({
        "thoughts": ["Adjusting tasks based on the following alignment issues:", str(alignment_issues)],
        "tool_name": "task_adjuster",
        "tool_args": {"tasks": tasks, "alignment_issues": alignment_issues}
    }))
    return json.loads(adjustment_result)

# User intervention during agent processing
def intervention():
    if Agent.streaming_agent and not Agent.paused:
        Agent.paused = True # stop agent processing
        PrintStyle(background_color="#6C3483", font_color="white", bold=True, padding=True).print(f"User intervention ('e' to leave, empty to continue):")        

        import readline # this fixes arrow keys in terminal
        user_input = input("> ").strip()
        PrintStyle(font_color="white", padding=False, log_only=True).print(f"> {user_input}")        
        
        if user_input.lower() == 'e': os._exit(0) # exit the process when the user types 'exit'
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
    initialize()