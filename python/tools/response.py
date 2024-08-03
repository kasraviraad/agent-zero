from agent import Agent
from helpers import files
from helpers.print_style import PrintStyle

from agent import Agent
from helpers.tool import Tool, Response
from helpers import files
from helpers.print_style import PrintStyle

class ResponseTool(Tool):

    def execute(self,**kwargs):
        self.agent.set_data("timeout", self.agent.config.response_timeout_seconds)
        return Response(message=self.args["text"], break_loop=True)

    def before_execution(self, **kwargs):
        pass # do not add anything to the history or output
    
    def after_execution(self, response, **kwargs):
        pass # do not add anything to the history or output