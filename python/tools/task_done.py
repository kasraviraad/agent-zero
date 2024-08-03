from agent import Agent
from helpers import files
from helpers.print_style import PrintStyle

from agent import Agent
from helpers.tool import Tool, Response
from helpers import files
from helpers.print_style import PrintStyle

class TaskDone(Tool):

    def execute(self,**kwargs):
        self.agent.set_data("timeout", 0)
        return Response(message=self.args["text"], break_loop=True)

    def before_execution(self, **kwargs):
        pass # do not add anything to the history or output
    
    def after_execution(self, response, **kwargs):
        pass # do add anything to the history or output