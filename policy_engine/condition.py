from .context import OperatorContext
from .util import (
    format_args,
    format_kwargs,
    format_arg,
    format_event_data,
    format_event_value
)


class BaseCondition:

    def validate(self,args):
        pass


class OperatorCondition(BaseCondition):

    def __init__(self, policy_engine=None, operator_method=None,lhs=None, rhs=None):
        self.pe = policy_engine
        self.operator_method = operator_method
        self.lhs = lhs
        self.rhs = rhs

    def validate(self, data):

        lhs = format_event_value(self.lhs, data, self.pe.filters)
        rhs = format_event_value(self.rhs, data, self.pe.filters)
        return self.operator_method(lhs, rhs)


class FuncCondition(BaseCondition):

    def __init__(self, policy_engine=None, method=None, args=[]):
        self.pe = policy_engine
        self.method = method
        self.args = args

    def validate(self, data):
        final_args = format_event_data(self.args, data, self.pe.filters)
        return self.method(**final_args)


class ConditionParser:

    def parse(data=None, policy_engine=None):

        if data['type'] == 'op':
            lhs = format_arg(data['lhs'])
            rhs = format_arg(data['rhs'])
            operator = data['method']
            cond_name = None
            if operator == '=':
                cond_name = 'equal_method'
            if operator == '!=':
                cond_name = 'not_equal_method'
            if operator == '>':
                cond_name = 'gt_method'
            if operator == '<':
                cond_name = 'lt_method'
            if operator == '>=':
                cond_name = 'gte_method'
            if operator == '<=':
                cond_name = 'lte_method'
            try:
                operator_method = getattr(OperatorContext, cond_name)
                return OperatorCondition(
                    policy_engine=policy_engine,
                    operator_method=operator_method,
                    lhs=lhs,
                    rhs=rhs
                )
            except AttributeError:
                raise Exception('Unknown method {0}'.format(cond_name))
        elif data['type'] == 'func':
            args = format_kwargs(data['arguments'])
            method_name = data['method']
            try:
                method = getattr(policy_engine.condition_context, method_name)
                return FuncCondition(
                    policy_engine=policy_engine,
                    method=method,
                    args=args
                )
            except AttributeError:
                raise Exception('Could not find condition method {0}'.format(
                    method_name))
        else:
            raise Exception('Unknown condition type {0}'.format(data['type']))
