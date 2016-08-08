"""
In this file we will implement all the functions
that will be done after a policy is triggered. Also
here we can model the functions that will be used as
the conditions. It is importang that the functions should
be:
(args) -> (bool)
or else the system will throw an exception
"""
class ActionDispatcher(object):
	"""Available methods/actions for policies"""

	def FooAction(foo=None, fooval=None):
		print("FooAction foo={0} fooval={1}".format(foo, fooval))


class ConditionDispatcher(object):

	def equal_method(lhs, rhs):
		return lhs == rhs

	def not_equal_method(lhs, rhs):
		return lhs != rhs

	def gt_method(lhs, rhs):
		return lhs > rhs

	def lt_method(lhs, rhs):
		return lhs < rhs

	def gte_method(lhs, rhs):
		return lhs >= rhs

	def gle_method(lhs, rhs):
		return lhs >= rhs

	def FourtyCheck(bar=None, baz=None):
		return bar - baz == 40