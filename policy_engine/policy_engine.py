import os
import re
from yamlschema.yamlschema.parser import Parser
from policy_engine.policy import Policy
import logging
import json

log = logging.getLogger('noc-netmode')

class PolicyEngine(object):


	POLICY_SCHEMA 	= "./policy_engine/policy_schema.yml"
	POLICIES_FOLDER = "./policy_engine/policies"

	"""Policy Engine base class"""
	"""
	This class should have all the policies and a CRUD like
	behaviour. Also it has a method to dispatch an event from
	the publisher. Each time a policy is to be added, we need
	to check the constraints of the schema
	"""
	
	def __init__(self, policies_folder=None, policy_schema=None):

		log.debug('Initializing Policy Engine')
		self.policies = {}

		if policy_schema is None:
			policy_schema = self.POLICY_SCHEMA
		log.debug('Using {0} as the policies schema'.format(policy_schema))
		self._parser = Parser(schema_file=policy_schema)
		
		self._yaml_regex = re.compile(r'^.*\.(yaml|yml)$')
		if policies_folder is None:
			policies_folder = self.POLICIES_FOLDER
			log.debug('Using {0} as the policies folder'.format(policies_folder))

		for subdir, dirs, files in os.walk(policies_folder):
			for file in files:
				filepath = subdir + os.sep + file
				try:
					self.add_policy(filepath)
				except Exception:
					pass
		log.debug('Loaded {0} policies'.format(len(self.policies)))

	def add_policy(self, file):
		if self._yaml_regex.match(file):
			log.debug('Adding policy from file {0}'.format(file))
			try:
				policy_data = self._parser.parse(source_file=file)
				event_name = policy_data['event']['name'] 
				if event_name not in self.policies:
					self.policies[event_name] = []
				self.policies[event_name].append(
					Policy(	
						event=policy_data['event'], 
						name=policy_data['name'], 
						conditions=policy_data['conditions'], 
						action=policy_data['action']
					))
			except Exception as e:
				log.error('Error while adding policy {0}. Reason {1}'.format(file, e))
				raise


	def remove_policy(self, policy_name):
		pass

	def update_policy(self):
		pass

	def dispatch_event(self, event):
		log.info("Dispatching event:")
		log.info(json.dumps(event, sort_keys=True, indent=4, separators=(',', ': ')))
		policies_to_trigger = self.policies[event["name"]]
		for policy in policies_to_trigger:
			policy.trigger(event["data"])


if __name__ == "__main__":
	p = PolicyEngine()