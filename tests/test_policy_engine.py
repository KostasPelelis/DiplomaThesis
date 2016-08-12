import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/..')))
from policy_engine.policy_engine import PolicyEngine

class TestPolicyEngine(unittest.TestCase):
	
	def run_test(self):
		p = PolicyEngine()
		self.assertTrue(isinstance(p, PolicyEngine))
		
		p.dispatch_event({
			'data': {
				'foo': 2,
				'bar': 42, 
				'baz': 2,
			},
			'name': 'EventName'
		})
		self.assertTrue(isinstance(p, PolicyEngine))

if __name__ == "__main__":
	a = TestPolicyEngine()
	a.run_test()