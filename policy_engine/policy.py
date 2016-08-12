from policy_engine.condition import ConditionParser
from policy_engine.action import Action

class Policy:

	"""
	The base Policy class that will check the conditions and will do an action
	according to the schema file
	"""

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

		if self._validate_conditions(event_data):
			self.action.run(event_data)

	def _validate_conditions(self, data):
		for condition in self.conditions:
			if not condition.validate(data):
				return False
		return True


