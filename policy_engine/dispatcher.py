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

	def test_action(ip):
		print("test_action")

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

		