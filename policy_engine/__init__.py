"""Policy Engine Module
Policy engine module provides high level mechanism for creating and managing
network policies. These policies can be either YAML files with a predefined
schema or web-defined from the UI the application is providing. In this module
there is only the singleton ``PolicyEngine`` class which is used to complete
all these actions as well as propagate network event to ``Policy`` instances

Example:
    If you want to use the policy engine you just need to initialize the
    ``PolicyEngine`` class:

        from policy_engine import PolicyEngine

        pe = PolicyEngine()

    Then you can dispatch any event data that you want as follows:
    data = {* Network Data *}
    pe.dispatch_event(data)

TODO:
    Completely remove pykwalify
"""

import os
import re
from yamlschema.yamlschema.parser import Parser
from policy_engine.policy import Policy
import logging
import json
from policy_engine.errors import InvalidPolicyException

log = logging.getLogger('noc-netmode')


class PolicyEngine(object):

    """The Policy Engine Singleton Class

    """
    POLICY_SCHEMA = "./policy_engine/policy_schema.yml"
    POLICIES_FOLDER = "./policy_engine/policies"

    def __init__(self, policies_folder=None, policy_schema=None):

        log.debug('Initializing Policy Engine')
        self.policies = {}
        # Check if we have a schema to use
        if policy_schema is None:
            policy_schema = self.POLICY_SCHEMA
        log.debug('Using {0} as the policies schema'.format(policy_schema))
        # Create the policy parser
        self._parser = Parser(schema_file=policy_schema)
        # Dummy way of checking yaml files legitimacy
        self._yaml_regex = re.compile(r'^.*\.(yaml|yml)$')
        # Walk the policies folder and parse all policies
        if policies_folder is None:
            policies_folder = self.POLICIES_FOLDER
            log.debug('Using {0} as the policies folder'.format(
                policies_folder))
        for subdir, dirs, files in os.walk(policies_folder):
            for file in files:
                filepath = subdir + os.sep + file
                try:
                    # Add each policy to the list
                    self.add_policy(filepath)
                except Exception:
                    pass
        log.debug('Loaded {0} policies'.format(len(self.policies)))

    def add_policy(self, file):
        if self._yaml_regex.match(file):
            log.debug('Adding policy from file {0}'.format(file))
            try:
                # Parse the policy data
                policy_data = self._parser.parse(source_file=file)
                # We use the event name as the key to the dictionary
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
                log.error('Error while adding policy {0}. Reason {1}'.format(
                    file, e))
                raise InvalidPolicyException

    def remove_policy(self, policy_name):
        pass

    def update_policy(self):
        pass

    def dispatch_event(self, event):
        log.info("Dispatching event:")
        policies_to_trigger = self.policies[event["name"]]
        for policy in policies_to_trigger:
            policy.trigger(event["data"])
