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
import logging
import json
from queue import Queue
import threading
from yamlschema.yamlschema.parser import Parser

from policy_engine.errors import InvalidPolicy
from policy_engine.policy import Policy

log = logging.getLogger('noc-netmode')


class PolicyEngine(object):

    POLICY_SCHEMA = "./policy_engine/policy_schema.yml"
    POLICIES_FOLDER = "./policy_engine/policies"

    class Dispatcher(threading.Thread):

        def __init__(self, queue, policy_engine, id):
            threading.Thread.__init__(self)
            self.queue = queue
            self.policy_engine = policy_engine
            self.id = id

        def run(self):
            while True:
                event = self.queue.get()
                event = json.loads(event)
                log.info('Worker {0} handling event {1}'
                         .format(self.id, event))
                policies_to_trigger = self.policy_engine.policies.get(
                    event["name"], [])
                for policy in policies_to_trigger:
                    try:
                        policy.trigger(event['event_data'])
                    except KeyError:
                        continue
                    except Exception as e:
                        log.error(e)
                        continue
                self.queue.task_done()

    def __init__(self, name, action_context=None, condition_context=None,
                 workers=3):

        log.debug('Initializing Policy Engine')
        self.name = name
        self.policies = {}
        # Check if we have a schema to use
        policy_schema = self.POLICY_SCHEMA
        log.debug('Using {0} as the policies schema'.format(policy_schema))
        # Create the policy parser
        self._parser = Parser(schema_file=policy_schema)
        # Dummy way of checking yaml files legitimacy
        self._yaml_regex = re.compile(r'^.*\.(yaml|yml)$')
        self.event_queue = Queue()
        self.workers = []
        log.debug('Creating Job Queue with {0} workers'.format(workers))
        for index in range(0, workers):
            worker = self.Dispatcher(self.event_queue, self, index)
            worker.daemon = True
            self.workers.append(worker)
            worker.start()

        if action_context is None:
            from .context import ActionContext
            self.action_context = ActionContext
        else:
            self.action_context = action_context
        if condition_context is None:
            from .context import ConditionContext
            self.condition_context = ConditionContext
        else:
            self.condition_context = condition_context
        self.filters = {}

    def run(self, policies_folder=None, policy_schema=None):
        if policy_schema is not None:
            self._parser = Parser(schema_file=policy_schema)
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
                new_policy = Policy(
                    event=policy_data['event'],
                    name=policy_data['name'],
                    conditions=policy_data['conditions'],
                    action=policy_data['action'],
                    policy_engine=self
                )
                self.policies[event_name].append(new_policy)
            except Exception as e:
                log.exception('Error while adding policy {0}'
                              .format(file))
                raise InvalidPolicy

    @property
    def action_ctx(self):
        return self.action_context

    @action_ctx.setter
    def action_ctx(self, ctx):
        self.action_context = ctx

    @property
    def condition_ctx(self):
        return self.condition_context

    @condition_ctx.setter
    def condition_ctx(self, ctx):
        self.condition_context = ctx

    def condition(self, func):
        setattr(self.condition_context, func.__name__, func)
        return

    def action(self, func):
        setattr(self.action_context, func.__name__, func)
        return

    def filter(self, filter_name):
        def decorator(func):
            self.filters[filter_name] = func
        return decorator

    def remove_policy(self, policy_name):
        pass

    def update_policy(self):
        pass

    def enqueue_event(self, event):
        log.debug("Enqueing Event: {0}".format(event))
        event = json.dumps(event)
        self.event_queue.put(event)
