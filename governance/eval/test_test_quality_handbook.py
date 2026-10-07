#!/usr/bin/env python3
"""Independent controls for the fixed handbook experiment grader."""
import unittest
import test_quality_handbook as ev

HEADER = 'import unittest\nfrom subject import total\nclass Tests(unittest.TestCase):\n'
GOOD = HEADER + '''    def test_boundary(self):
        self.assertEqual(total(3,101),287)
    def test_reason(self):
        with self.assertRaisesRegex(ValueError,"^negative$"):
            total(-1,101)
'''


class GraderTests(unittest.TestCase):
    def test_independent_oracles_detect_three_faults(self):
        result = ev.score('pricing', GOOD)
        self.assertTrue(result['baseline']['passed'])
        self.assertEqual(result['baseline']['tests_run'], 2)
        self.assertEqual([c['status'] for c in result['checks']], ['detected'] * 3)
        self.assertTrue(all(c['restored']['passed'] for c in result['checks']))

    def test_self_comparison_survives(self):
        result = ev.score('pricing', HEADER + '    def test_same(self):\n        self.assertEqual(total(3,101),total(3,101))\n')
        self.assertEqual([c['status'] for c in result['checks']], ['survived'] * 3)

    def test_wrong_baseline_is_not_detection(self):
        result = ev.score('pricing', GOOD.replace('287', '999'))
        self.assertEqual([c['status'] for c in result['checks']], ['invalid'] * 3)

    def test_import_error_is_not_detection(self):
        result = ev.score('pricing', 'from subject import missing\n')
        self.assertEqual([c['status'] for c in result['checks']], ['invalid'] * 3)

    def test_zero_tests_are_invalid(self):
        result = ev.score('pricing', 'import unittest\n')
        self.assertEqual(result['baseline']['tests_run'], 0)
        self.assertEqual([c['status'] for c in result['checks']], ['invalid'] * 3)

    def test_disallowed_io_is_rejected_before_execution(self):
        with self.assertRaises(ValueError):
            ev.validate_test('open("/tmp/not-a-handbook-test", "w")')
        with self.assertRaises(ValueError):
            ev.validate_test('import os')

    def test_syntax_error_is_not_detection(self):
        result = ev.score('pricing', 'def ???')
        self.assertEqual([c['status'] for c in result['checks']], ['invalid'] * 3)

    def test_event_text_message_is_not_a_tool_call(self):
        rows = [{"message": "notice"}, {"message": {"content": "text"}}, {"message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "SKILL.md"}}]}}]
        self.assertEqual(ev.tool_calls(rows), [{"name": "Read", "input": {"file_path": "SKILL.md"}}])

    def test_routing_independent_oracles(self):
        code = '''import unittest
from subject import route
class Tests(unittest.TestCase):
    def test_odd(self):
        self.assertEqual(route(3,True),"B")
    def test_inactive(self):
        with self.assertRaisesRegex(ValueError,"^inactive$"):
            route(2,False)
'''
        result = ev.score('routing', code)
        self.assertEqual([c['status'] for c in result['checks']], ['detected'] * 3)


if __name__ == '__main__':
    unittest.main()
