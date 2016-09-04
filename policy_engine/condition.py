from .context import ConditionContext
from .util import (
    format_args,
    format_kwargs,
    format_arg,
    format_event_data
)


class BaseCondition:

    def validate(self, args):
        pass


class OperatorCondition(BaseCondition):

    def __init__(self, operator_method=None, lhs=None, rhs=None):
        self.operator_method = operator_method
        self.lhs = lhs
        self.rhs = rhs

    def validate(self, data):
        lhs = None
        if self.lhs['type'] == 'ref':
            lhs = data[self.lhs['value']]
        else:
            lhs = self.lhs['value']
        return self.operator_method(lhs, self.rhs)


class FuncCondition(BaseCondition):

    def __init__(self, method=None, args=[]):
        self.method = method
        self.args = args

    def validate(self, data):
        final_args = format_event_data(self.args, data)
        return self.operator_method(**final_args)


class ConditionParser:

    def parse(data=None, ctx=None):

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
                operator_method = getattr(ConditionContext, cond_name)
                return OperatorCondition(
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
                if ctx is None:
                    method = getattr(ConditionContext, method_name)
                else:
                    method = getattr(ctx, method_name)
                return FuncCondition(
                    method=method,
                    args=args
                )
            except AttributeError:
                raise Exception('Could not find condition method {0}'.format(
                    method_name))
        else:
            raise Exception('Unknown condition type {0}'.format(data['type']))
