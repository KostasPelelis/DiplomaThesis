# Import the base class from the module
from policy_engine import PolicyEngine

pe = PolicyEngine('Network Policy Engine')
# Define the Action Context that your policy engine
# will get its methods from
@pe.action_ctx
class ActionContext:

	def action_method(arg1=None, arg2=None):
		# Apply any logic here
		# ......
		print(arg1 - arg2)
		return 'All ok'

@pe.condition_ctx
class ConditionContext:

	def condition_method(arg1=None, arg2=None):
		# Apply logic and return True or False
		# ...
		print(arg1, arg2)
		return arg1 + arg2 == 42

# You can define your filters in 2 ways
# 1) With the filter decorator
@pe.filter('my_filter')
def filter_func(val):
	# change the value as you want
	# and reutrn the new one
	return val + 5

# 2) With direct access to the fitlers
# object
def other_filter_func(val):
	return val - 5

pe.filters['my_second_filter'] = other_filter_func

# And now you can load your policies. Be aware that if
# you want to use custom context you need to load after
# you define it

pe.load_policies()

# The typical usage is: Send a data object 
# to the policy engine through the dispatch_event
# method and let it do the magic

# Lets say we have the following policy defined in YAML

# When defining a policy you can use '$' to declare a variable
# that will be taken directly from the event data and '| filter_name' to declare
# that this data will be piped to the filter filter_name. You can use as many
# filters as you want
"""
name: 'PolicyName'
event:
  name: 'EventName'
conditions:
  - type: 'op'
    method: '='
    lhs: '$foo | my_filter'
    rhs: 10
  - type: 'func'
    method: 'condition_method'
    arguments:
      'arg1': '$bar | my_second_filter'
      'arg2': 2
action:
  name: 'action_method'
  arguments:
    'arg1': '$baz'
    'arg2': 10
"""

pe.dispatch_event({
	# The data should have a field called name
	# which should be the name of the event of your policy
	'name': 'EventName',
	'data': {
		'foo': 5,
		'bar': 45,
		'baz': 52
	}
})

# Should Execute and print 52 - 10 = 42