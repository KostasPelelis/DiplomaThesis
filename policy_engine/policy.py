from condition import ConditionParser
from action import Action

class Policy:

	"""
	The base Policy class that will check the conditions and will do an action
	according to the schema file
	"""

	def __init__(self, event=None, name=None, conditions=None, action=None):

		self.name 				= name
		self.conditions 		= []
		self.action 			= None
		self.event_namespace 	= []

		if "arguments" in event:
			self.event_namespace = event["arguments"]  

		for condition in conditions:
			try:
				self.conditions.append(ConditionParser.parse(condition))
			except Exception:
				raise
		self.action	= Action(name=action["name"], args=action["arguments"])

	def trigger(self, event_data):

		if _validate_conditions(event_data):
			self.action.run(event_data)

	def _validate_conditions(data):
		for condition in conditions:
			if not condition.validate():
				return False
		return True


