from policy_engine.context import ActionContext
from policy_engine.util import format_kwargs, format_event_data


class Action:

    def __init__(self, name=None, args=None):
        self.method = None
        self.args = format_kwargs(args)
        try:
            self.method = getattr(ActionContext, name)
        except AttributeError:
            raise Exception('Unknown action method {0}'.format(name))

    def run(self, data):
        final_args = format_event_data(self.args, data)
        self.method(**final_args)
