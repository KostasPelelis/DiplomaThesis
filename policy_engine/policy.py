from policy_engine.condition import ConditionParser
from policy_engine.action import Action
from policy_engine.errors import ConditionParseError


class Policy:

    """
    The base Policy class that will check the conditions and will do an action
    according to the schema file
    """
    class _EventData(object):

        def __init__(self, data):
            self.data = data

        def __getitem__(self, key):
            val = self.data
            for fragment in key.split('.'):
                if isinstance(val, dict) and fragment not in val.keys():
                    raise KeyError
                val = val[fragment]
            return val

        def __setitem__(self, key, val):
            _dict = self.data
            fragments = key.split('.')
            for fragment in fragments[:-1]:
                _dict = _dict[fragment]
            _dict[fragments[-1]] = val

    def __init__(self, event=None, name=None, conditions=None, action=None,
                 policy_engine=None):

        self.name = name
        self.conditions = []
        self.action = None
        self.policy_engine = policy_engine
        for condition in conditions:
            try:
                self.conditions.append(
                    ConditionParser.parse(data=condition,
                                          policy_engine=self.policy_engine))
            except Exception as e:
                raise ConditionParseError(e)
        self.action = Action(name=action["name"], args=action.get("arguments"),
                             policy_engine=self.policy_engine)

    """
    Trigger function is called to activate a policy with some
    specific data
    """
    def trigger(self, event_data):
        event_data = Policy._EventData(event_data)
        if self._validate_conditions(event_data):
            self.action.run(event_data)

    """
    Validate all Conditions and return True if ALL conditions are
    satisfied
    """
    def _validate_conditions(self, data):
        for condition in self.conditions:
            if not condition.validate(data):
                return False
        return True
