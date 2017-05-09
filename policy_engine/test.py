from .policy_engine import PolicyEngine
from .policy import Policy


__all__ = ['TestPolicyEngine']


class TestPolicyEngine(object):

    def test_ctx_decorator(self):

        pe = PolicyEngine()

        def add_2(val):
            return val + 2

        @pe.filter('remove_2')
        def remove_2(val):
            return val - 2

        pe.filters['add_2'] = add_2

        assert(len(self.pe.filters.keys()) == 2)
        assert(self.pe.filters.get('add_2') is not None)
        assert(self.pe.filters.get('remove_2') is not None)

        @pe.action_ctx
        class CustomContext:

            def FooAction(foo=2):
                return foo

        @pe.action
        def demo_action():
            print('bar')
