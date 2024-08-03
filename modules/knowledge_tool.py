import os
import concurrent.futures
from typing import Dict, Any,TYPE_CHECKING
from modules import memory_tool
from helpers import perplexity_search, duckduckgo_search, files
from helpers.tool import Tool, Response

if TYPE_CHECKING:
    from agent import Agent
class Knowledge(Tool):
    def __init__(self, agent: 'Agent', name: str, args: Dict[str, Any], message: str):
        super().__init__(agent, name, args, message)

    def execute(self, question: str = "", **kwargs) -> Response:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []

            # Perplexity search, if API provided
            if perplexity_search.call_llm:
                futures.append(executor.submit(perplexity_search.perplexity_search, question))
            
            # DuckDuckGo search
            futures.append(executor.submit(duckduckgo_search.search, question))

            # Memory search
            futures.append(executor.submit(memory_tool.search, self.agent, question))

            # Wait for all functions to complete
            results = [future.result() for future in futures]

        # Combine results
        online_sources = "\n\n".join(filter(None, results[:-1]))  # All but the last result (memory)
        memory_result = results[-1]

        msg = files.read_file("prompts/tool.knowledge.response.md", 
                              online_sources=online_sources,
                              memory=memory_result)

        if self.agent.handle_intervention(msg): pass  # Wait for intervention and handle it, if paused

        return Response(message=msg, break_loop=False)