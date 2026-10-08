#!/usr/bin/env python3
"""Independent controls for the fixed handbook experiment grader."""
import unittest
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from unittest import mock
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

    def test_initial_draft_stops_before_verifier_feedback(self):
        calls = [{'name': 'Write', 'input': {'file_path': '/tmp/tests.py', 'content': 'initial'}},
                 {'name': 'Write', 'input': {'file_path': '/tmp/tests.py', 'content': 'complete'}},
                 {'name': 'Bash', 'input': {'command': 'python3 verify.py'}},
                 {'name': 'Write', 'input': {'file_path': '/tmp/tests.py', 'content': 'after-feedback'}}]
        self.assertEqual(ev.draft_before_verify(calls), 'complete')
        self.assertIsNone(ev.draft_before_verify([]))

    def test_literal_parameterized_loop_preserves_detection(self):
        code = HEADER + '    def test_examples(self):\n        for quantity, price, expected in ((3,101,287),(4,10,38)):\n            self.assertEqual(total(quantity,price),expected)\n    def test_reason(self):\n        for quantity in (-1,-2):\n            with self.assertRaisesRegex(ValueError,"^negative$"):\n                total(quantity,101)\n'
        result = ev.score('pricing', code)
        self.assertEqual([c['status'] for c in result['checks']], ['detected'] * 3)

    def test_literal_range_is_executable(self):
        code = HEADER + '    def test_zero_price(self):\n        for quantity in range(7):\n            self.assertEqual(total(quantity,0),0)\n'
        self.assertTrue(ev.run_test(code, ev.TASKS['pricing']['source'])['passed'])

    def test_unbounded_and_dynamic_loops_are_rejected(self):
        for body in ['for x in range(1000000):\n    pass', 'for x in total(3,101):\n    pass']:
            with self.assertRaises(ValueError):
                ev.validate_test(body)

    def test_literal_dict_subtests_preserve_fault_detection(self):
        code = HEADER + '    def test_cases(self):\n        cases = {(3,101):287,(4,10):38}\n        for pair, expected in cases.items():\n            with self.subTest(case=pair):\n                self.assertEqual(total(pair[0],pair[1]),expected)\n    def test_reason(self):\n        with self.assertRaisesRegex(ValueError,"^negative$"):\n            total(-1,101)\n'
        result = ev.score('pricing', code)
        self.assertEqual([c['status'] for c in result['checks']], ['detected'] * 3)

    def test_unknown_dict_loop_is_rejected(self):
        with self.assertRaises(ValueError):
            ev.validate_test('for value in unknown.items():\n    pass')

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


class ModelCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    @staticmethod
    def alive(pid):
        run = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True
        )
        return (
            run.returncode == 0
            and bool(run.stdout.strip())
            and not run.stdout.strip().startswith("Z")
        )


    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_model_timeout_stops_worker_without_paid_call(self):
        module = ev
        binary = self.root / "bin"
        binary.mkdir()
        fake = binary / "claude"
        pidfile = self.root / "worker.pid"
        fake.write_text(
            "#!"
            + sys.executable
            + '\nimport subprocess,sys,time\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"])\nPath('
            + repr(str(pidfile))
            + ").write_text(str(p.pid))\ntime.sleep(60)\n"
        )
        fake.chmod(0o755)
        with mock.patch.dict(
            os.environ, {"PATH": str(binary) + os.pathsep + os.environ["PATH"]}
        ):
            self.assertEqual(
                shutil.which("claude"),
                str(fake),
                "fixture entrypoint, never real provider",
            )
            result, _ = module.run_model(
                self.root,
                "fixture",
                "fixture",
                "fixture-model",
                1,
                False,
                self.root / "raw.jsonl",
            )
        self.assertTrue(pidfile.exists(), "worker actually launched before timeout")
        pid = int(pidfile.read_text())
        self.addCleanup(
            lambda: os.kill(pid, signal.SIGKILL) if self.alive(pid) else None
        )
        self.assertFalse(result["valid"])
        self.assertIsNone(result["returncode"])
        deadline = time.monotonic() + 2
        while self.alive(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(self.alive(pid))

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_model_error_stops_detached_stream_worker(self):
        binary = self.root / "bin"
        binary.mkdir()
        fake = binary / "claude"
        pidfile = self.root / "worker-error.pid"
        fake.write_text(
            "#!"
            + sys.executable
            + "\nimport subprocess,sys\nfrom pathlib import Path\n"
            + "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],"
              "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
            + "Path(" + repr(str(pidfile)) + ").write_text(str(p.pid))\nsys.exit(1)\n"
        )
        fake.chmod(0o755)
        result = ev.model_command([str(fake)], self.root, 5)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(pidfile.exists(), "worker actually launched before launcher error")
        pid = int(pidfile.read_text())
        self.addCleanup(
            lambda: os.kill(pid, signal.SIGKILL) if self.alive(pid) else None
        )
        deadline = time.monotonic() + 2
        while self.alive(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(self.alive(pid))

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_exited_model_with_stream_holding_worker_is_not_timeout(self):
        fake = self.root / "claude"
        fake.write_text(
            "#!" + sys.executable + "\nimport subprocess,sys,time\n"
            "p=subprocess.Popen([sys.executable,'-c',"
            "'import time; print(\"worker-holds-stream\",flush=True); time.sleep(60)'])\n"
            "time.sleep(0.3)\nimport os\nprint('model-cwd',os.getcwd(),flush=True)\n"
            "print('model-done',p.pid,flush=True)\n"
        )
        fake.chmod(0o755)
        started = time.monotonic()
        result = ev.model_command([str(fake)], self.root, 5)
        self.assertLess(time.monotonic() - started, 3, "exited model is not a timeout")
        self.assertEqual(result.returncode, 0)
        words = result.stdout.split()
        self.assertIn("worker-holds-stream", words, "worker really shared the model stream")
        self.assertEqual(Path(words[words.index("model-cwd") + 1]).resolve(), self.root.resolve())
        pid = int(words[words.index("model-done") + 1])
        self.addCleanup(
            lambda: os.kill(pid, signal.SIGKILL) if self.alive(pid) else None
        )
        deadline = time.monotonic() + 2
        while self.alive(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(self.alive(pid))

    def test_model_output_over_limit_is_invalid_session_not_abort(self):
        binary = self.root / "bin"
        binary.mkdir()
        fake = binary / "claude"
        fake.write_text("#!" + sys.executable + "\nimport sys\nsys.stdout.write('x' * (11 * 1024 * 1024))\n")
        fake.chmod(0o755)
        raw = self.root / "raw.jsonl"
        with mock.patch.dict(os.environ, {"PATH": str(binary) + os.pathsep + os.environ["PATH"]}):
            self.assertEqual(shutil.which("claude"), str(fake), "fixture entrypoint, never real provider")
            result, _ = ev.run_model(self.root, "fixture", "fixture", "fixture-model", 20, False, raw)
        self.assertFalse(result["valid"])
        self.assertIsNone(result["returncode"])
        self.assertIn("output exceeds 10 MiB", result["stderr"])
        self.assertTrue(raw.exists(), "session record still written")

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_model_timeout_keeps_partial_stream(self):
        fake = self.root / "claude"
        fake.write_text(
            "#!" + sys.executable + "\nimport time\n"
            "print('{\"type\":\"system\",\"subtype\":\"init\"}',flush=True)\ntime.sleep(60)\n"
        )
        fake.chmod(0o755)
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            ev.model_command([str(fake)], self.root, 1)
        partial = caught.exception.stdout
        partial = partial.decode() if isinstance(partial, bytes) else partial
        self.assertIn('"subtype":"init"', partial)


if __name__ == '__main__':
    unittest.main()
