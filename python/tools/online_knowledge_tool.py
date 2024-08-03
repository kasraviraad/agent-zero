from agent import Agent
from helpers import perplexity_search
from helpers.tool import Tool, Response

class OnlineKnowledge(Tool):
    def execute(self,**kwargs):
        return Response(
            message=process_question(self.args["question"]),
            break_loop=False,
        )

def process_question(question):
    return str(perplexity_search.perplexity_search(question))