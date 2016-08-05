import os
import re
from yamlschema.yamlschema.parser import Parser
from policy import Policy


class PolicyEngine(object):


	POLICY_SCHEMA 	= "./policy_schema.yml"
	POLICIES_FOLDER = "./policies"

	"""Policy Engine base class"""
	"""
	This class should have all the policies and a CRUD like
	behaviour. Also it has a method to dispatch an event from
	the publisher. Each time a policy is to be added, we need
	to check the constraints of the schema
	"""
	
	def __init__(self):

		self.policies = {}
		self._parser = Parser(schema_file=self.POLICY_SCHEMA)
		self._yaml_regex = re.compile(r'^.*\.(yaml|yml)$')
		for subdir, dirs, files in os.walk(self.POLICIES_FOLDER):
			for file in files:
				filepath = subdir + os.sep + file
				try:
					self.add_policy(filepath)
				except Exception:
					pass

	def add_policy(self, file):
		if self._yaml_regex.match(file):
			try:
				policy_data = self._parser.parse(source_file=file)
				event_name = policy_data["event"]["name"] 
				if event_name not in self.policies:
					self.policies[event_name] = []
				self.policies[event_name].append(policy_data)
			except Exception as e:
				raise


	def remove_policy(self, policy_name):
		pass

	def update_policy(self):
		pass

	def dispatch_event(self, event):
		policies_to_trigger = self.policies[event.name]
		for policy in policies_to_trigger:
			policy.trigger(event.data)


if __name__ == "__main__":
	p = PolicyEngine()
	print(p.policies)