from policy_engine import util
from policy_engine import errors


class Action:

    def __init__(self, name=None, args=None, policy_engine=None):
        self.method = None
        self.pe = policy_engine
        self.args = util.format_kwargs(args)
        try:
            self.method = getattr(policy_engine.action_context, name)
        except AttributeError:
            raise MethodNotFound('Unknown action method {0}'.util.format(name))

    def run(self, data):
        final_args = util.format_event_data(self.args, data, self.pe.filters)
        return self.method(**final_args)
