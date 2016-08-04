from dispatcher import ActionDispatcher
from util import format_args

class Action:

	def __init__(self, name=None, args=None):
		self.args = None
		self.method = None
		
		self.args = format_args(args)
		if name is not None:
			self.method = getattr(ActionDispatcher, name)

	def run(self, extra_args=None):
		if self.method is not None:
			final_args = dict(self.args, **extra_args)
			self.method(**final_args)