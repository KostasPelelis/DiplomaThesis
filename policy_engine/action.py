from .util import format_kwargs, format_event_data


class Action:

    def __init__(self, name=None, args=None, policy_engine=None):
        self.method = None
        self.pe = policy_engine
        self.args = format_kwargs(args)
        try:
            self.method = getattr(policy_engine.action_context, name)
        except AttributeError:
            raise Exception('Unknown action method {0}'.format(name))

    def run(self, data):
        final_args = format_event_data(self.args, data, self.pe.filters)
        return self.method(**final_args)
