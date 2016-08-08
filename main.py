from logger import init_logging
from policy_engine.policy_engine import PolicyEngine
init_logging('noc-netmode')

p = PolicyEngine()
p.dispatch_event({
	'data': {
		'foo': 2,
		'bar': 42, 
		'baz': 2,
	},
	'name': 'EventName'
})