from dispatcher import ConditionDispatcher

class BaseCondition:

	def validate(self, args):
		pass

class OperatorCondition(BaseCondition):

	def __init__(self, operator_method=None, args=[], rhs=None):
		self.operator_method 	= operator_method
		self.rhs 				= rhs
		self.args 				= []

	def validate(self, data):
		# Use map to simplify code
		for arg in self.args:
			lhs = None
			if arg['type'] == 'ref':
				lhs = data[arg]
			else:
				lhs = arg
			if not self.operator_method(lhs, self.rhs):
				return False
		return True

class FuncCondition(BaseCondition):

	def __init__(self, operator_method=None, args=[]):
		self.operator_method 	= operator_method
		self.args 				= args

	def validate(self, data):
		final_args = {}
		for key, val in self.args.items():
			if val['type'] == 'ref':
				final_args[key] = data[val['value']] 
			else:
				final_args[key] = val['value']
		return self.operator_method(**final_args)

class ConditionParser:

	def parse(data=None, event_namespace=[]):

		cond_name = None
		if data['type'] == 'op':
			args = format_args(data['arguments'], event_namespace)
			if 'value' not in data:
				raise Exception('Operator condition does not contain right side argument(value)')
			operator = data['method']
			if operator == '=':
				cond_name = 'equal_method' 
			if operator == '!=':
				cond_name = 'not_equal_method'
			if operator == '>':
				cond_name = 'gt_method'
			if operator == '<':
				cond_name = 'lt_method'
			if operator == '>=':
				cond_name = 'gte_method'
			if operator == '<=':
				cond_name = 'lte_method'
			condition_method = getattr(ConditionDispatcher, cond_name)
			return OperatorCondition(operator_method=condition_method, args=args, rhs=data['value'])

		elif data['type'] == 'func':
			args = format_kwargs(data['arguments'], event_namespace)
			cond_name = data['method']
			try:
				condition_method = getattr(ConditionDispatcher, cond_name)
				return FuncCondition(operator_method=condition_method, args=args)
			except Exception:
				raise Exception('Could not find condition method {0}'.format(cond_name))
			
		if cond_name is None:
			raise Exception('Unknown condition type {0}'.format(data['type']))