from policy_engine.condition import ConditionParser
from policy_engine.action import Action

class Policy:

	"""
	The base Policy class that will check the conditions and will do an action
	according to the schema file
	"""
class EventData(object):

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

	def __init__(self, event=None, name=None, conditions=None, action=None):

		self.name 				= name
		self.conditions 		= []
		self.action 			= None

		for condition in conditions:
			try:
				self.conditions.append(ConditionParser.parse(condition))
			except Exception as e:
				raise
		self.action	= Action(name=action["name"], args=action["arguments"])

	def trigger(self, event_data):
		event_data = EventData(event_data)
		if self._validate_conditions(event_data):
			self.action.run(event_data)

	def _validate_conditions(self, data):
		for condition in self.conditions:
			if not condition.validate(data):
				return False
		return True


