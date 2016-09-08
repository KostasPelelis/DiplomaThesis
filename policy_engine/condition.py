from policy_engine.context import OperatorContext
from policy_engine import util
from policy_engine import errors


class BaseCondition:

    def validate(self, args):
        pass


class OperatorCondition(BaseCondition):

    def __init__(self, policy_engine=None, operator_method=None,
                 lhs=None, rhs=None):
        self.pe = policy_engine
        self.operator_method = operator_method
        self.lhs = lhs
        self.rhs = rhs

    def validate(self, data):

        lhs = util.format_event_value(self.lhs, data, self.pe.filters)
        rhs = util.format_event_value(self.rhs, data, self.pe.filters)
        return self.operator_method(lhs, rhs)


class FuncCondition(BaseCondition):

    def __init__(self, policy_engine=None, method=None, args=[]):
        self.pe = policy_engine
        self.method = method
        self.condition_arguments = args

    def validate(self, data):
        final_args = util.format_event_data(self.condition_arguments, data,
                                            self.pe.filters)
        return self.method(**final_args)


class ConditionParser:

    def parse(data=None, policy_engine=None):

        if data['type'] == 'op':
            lhs = util.format_arg(data['lhs'])
            rhs = util.format_arg(data['rhs'])
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
                raise errors.MethodNotFound('Unknown method {0}'
                                            .format(cond_name))
        elif data['type'] == 'func':
            args = util.format_kwargs(data['arguments'])
            method_name = data['method']
            try:
                method = getattr(policy_engine.condition_context, method_name)
                return FuncCondition(
                    policy_engine=policy_engine,
                    method=method,
                    args=args
                )
            except AttributeError:
                raise errors.MethodNotFound(
                    'Could not find condition method {0}'.format(method_name))
        else:
            raise errors.BadCondition('Unknown condition type {0}'
                                      .format(data['type']))
