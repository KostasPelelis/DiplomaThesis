import unittest
from .policy_engine import PolicyEngine
from .policy import Policy


class TestPolicyEngine(unittest.TestCase):

    def test_policy_with_ctx(self):
        import sys
        from io import StringIO

        class CustomContext(object):

            def FooAction(foo=2):
                print(foo)

        p = Policy(
            event={'name': 'EventPls'},
            name='EventPls',
            conditions=[{'type': 'op', 'method': '=', 'lhs': 42, 'rhs': 42}],
            action={'name': 'FooAction', 'arguments': {'foo': '$bar'}},
            action_context=CustomContext
        )
        saved_stddout = sys.stdout
        out = StringIO()
        sys.stdout = out
        p.trigger({'bar': 42})
        output = out.getvalue().strip()
        sys.stdout = saved_stddout
        self.assertEqual(output, '42')
