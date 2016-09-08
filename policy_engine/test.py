from .policy_engine import PolicyEngine
from .policy import Policy


__all__ = ['TestPolicyEngine']


class TestPolicyEngine(object):

    def test_ctx_decorator(self):
        
        self.pe = PolicyEngine()

        def add_2(val):
            return val + 2
        
        @self.pe.filter('remove_2')
        def remove_2(val):
            return val - 2

        self.pe.filters['add_2'] = add_2 
        

        assert(len(self.pe.filters.keys()) == 2)
        assert(self.pe.filters.get('add_2') is not None)
        assert(self.pe.filters.get('remove_2') is not None)

        @self.pe.action_ctx
        class CustomContext:

            def FooAction(foo=2):
                return foo

        assert(self.pe.action_context.FooAction() == 2)

    def test_policy_dispatch(self):
        p = Policy(
            event={'name': 'EventPls'},
            name='EventPls',
            conditions=[{'type': 'op', 'method': '=', 'lhs': 42, 'rhs': '$bar | add_2 | remove_2'}],
            action={'name': 'FooAction', 'arguments': {'foo': '$bar | add_2 | add_2'}},
            policy_engine=self.pe
        )
        assert(p._validate_conditions({'bar': 42}))
        assert(p.action.run({'bar': 42}) == 46)