from dispatcher import ConditionDispatcher

class BaseCondition:

	def validate(self):
		pass

class OperatorCondition(BaseCondition):

	def __init__(self, operator_method=None, rhs=None):
		self.operator_method = operator_method
		self.rhs = rhs

	def validate(self, args=None):
		for arg in args:
			if not self.operator_method(arg, self.rhs):
				return False
		return True

class FuncCondition(BaseCondition):

	def __init__(self, operator_method=None):
		self.operator_method = operator_method

	def validate(self, args):
		return self.operator_method(**args)

class ConditionParser:

	def parse(data=None):

		cond_name = None
		if data['type'] == 'op':
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
			return OperatorCondition(operator_method=condition_method, args=data['arguments'], rhs=data['value'])

		elif data['type'] == 'func':
			cond_name = data['method']
			try:
				condition_method = getattr(ConditionDispatcher, cond_name)
				return FuncCondition(operator_method=condition_method, args=data['arguments'])
			except Exception:
				raise Exception('Could not find condition method {0}'.format(cond_name))
			
		if cond_name is None:
			raise Exception('Unknown condition type {0}'.format(data['type']))