from policy_engine.dispatcher import ActionDispatcher
from policy_engine.util import format_kwargs

class Action:

	def __init__(self, name=None, args=None):
		self.args = None
		self.method = None
		
		self.args = format_kwargs(args)
		if name is not None:
			self.method = getattr(ActionDispatcher, name)

	def run(self, data):
		final_args = {}
		if self.method is not None:
			for key, val in self.args.items():
				if val['type'] == 'ref':
					final_args[key] = data[val['value']] 
				else:
					final_args[key] = val['value']
			self.method(**final_args)