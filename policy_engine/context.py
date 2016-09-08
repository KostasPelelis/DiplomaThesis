"""
In this file we will implement all the functions
that will be done after a policy is triggered. Also
here we can model the functions that will be used as
the conditions. It is importang that the functions should
be:
(args) -> (bool)
or else the system will throw an exception
"""

import logging
log = logging.getLogger('noc-netmode')


class ActionContext(object):
    """Available methods/actions for policies"""

    def FooAction(foo=None, fooval=None):
        print("FooAction foo={0} fooval={1}".format(foo, fooval))

    def announce_ntua_ip(IP=None, proto='UDP'):
        print("Found a NTUA IP {0} with protocol {1}".format(IP, proto))

    def new_action(arg1=None, arg2=None):
        pass


class OperatorContext(object):

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


class ConditionContext(object):

    def FourtyCheck(bar=None, baz=None):
        return bar - baz == 40

    def ntua_origin(IP=None):
        log.debug('NTUA Origin ' + IP)
        if IP is None:
            return False
        elif IP.split('.')[0] == '147':
            return True
        return False
