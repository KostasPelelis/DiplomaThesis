import os
import re
from yamlschema.yamlschema.parser import Parser
from policy_engine.policy import Policy
import logging
import json
import io

log = logging.getLogger('noc-netmode')

class PolicyEngine(object):


	"""Policy Engine base class"""
	"""
	This class should have all the policies and a CRUD like
	behaviour. Also it has a method to dispatch an event from
	the publisher. Each time a policy is to be added, we need
	to check the constraints of the schema
	"""
	class __PolicyEngine:

		POLICY_SCHEMA 	= "./policy_engine/policy_schema.yml"
		POLICIES_FOLDER = "./policy_engine/policies"

		def __init__(self, policies_folder=None, policy_schema=None):

			log.debug('Initializing Policy Engine')
			self.policies = {}
			self.serialized_policies = []

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
						self.add_policy(file=filepath)
					except Exception:
						pass
			log.debug('Loaded {0} policies'.format(len(self.policies)))

		def add_policy(self, file=None, data=None, from_json=False):
			policy_data = None
			try:
				if file is not None and self._yaml_regex.match(file):
					log.debug('Adding policy from file {0}'.format(file))
					policy_data = self._parser.parse(source_file=file)
				elif data is not None:
					log.debug('Adding policy from data {0}'.format(data))
					policy_data = self._parser.parse(source_data=data, from_json=from_json)
			except Exception as e:
				log.error("Error while parsing policy")
				print(e)
				raise Exception("Error while parsing policy")
			self.serialized_policies.append(policy_data)
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


		def remove_policy(self, policy_name):
			pass

		def update_policy(self):
			pass

		def get_policy(self, id=None, name=None):
			if id is not None and id < len(self.serialized_policies):
				return self.serialized_policies[id]
			return None

		def list_policies(self):
			return self.serialized_policies

		def dispatch_event(self, event):
			log.info("Dispatching event:")
			policies_to_trigger = self.policies[event["name"]]
			for policy in policies_to_trigger:
				policy.trigger(event["data"])


	__instance = None
	
	def __init__(self, **kwargs):
		if PolicyEngine.__instance is None:
			PolicyEngine.__instance = self.__PolicyEngine(**kwargs)

	def __getattr__(self, name):
		return getattr(self.__instance, name)

if __name__ == "__main__":
	p = PolicyEngine()