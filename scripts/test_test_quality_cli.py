#!/usr/bin/env python3
"""Independent evidence validity controls; no implementation formula copied into expected."""

import hashlib
import os
import signal
import time
import importlib.util
from unittest import mock
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).with_name("lumos")


class QualityCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def run_cli(self, *args):
        r = subprocess.run(
            [sys.executable, str(TOOL), "test-quality", *map(str, args)],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        return r.returncode, json.loads(r.stdout)

    def receipt(
        self,
        phase,
        outcome="passed",
        impl="correct",
        tests="independent",
        failure_type="AssertionError",
    ):
        folder = self.root / phase
        folder.mkdir()
        failure = (
            ""
            if outcome == "passed"
            else "<skipped/>"
            if outcome == "skipped"
            else f'<{outcome} type="{failure_type}">wrong charge</{outcome}>'
        )
        xml = f'<testsuite><testcase classname="PriceTest" name="known_90">{failure}</testcase></testsuite>'.encode()
        (folder / "report.xml").write_bytes(xml)
        snaps = []
        for i, (role, value) in enumerate(
            [("implementation", impl), ("tests", tests), ("context", "locked")]
        ):
            raw = value.encode()
            artifact = f"snapshot-{i}.txt"
            (folder / artifact).write_bytes(raw)
            snaps.append(
                {
                    "role": role,
                    "path": "/isolated/" + role,
                    "artifact": artifact,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
        cases = [
            {
                "id": "PriceTest::known_90",
                "status": outcome,
                "assertion_failure": outcome == "failure"
                and failure_type == "AssertionError",
                "reason": ""
                if outcome == "passed" or outcome == "skipped"
                else failure_type + "  wrong charge",
            }
        ]
        r = {
            "schema_version": 1,
            "kind": "execution-receipt",
            "status": "executed",
            "language": "fixture",
            "framework": "junit-control",
            "command": ["trusted-runner"],
            "cwd": "/isolated",
            "exit_code": 0 if outcome == "passed" else 1,
            "report_sha256": hashlib.sha256(xml).hexdigest(),
            "tests": cases,
            "snapshots": snaps,
        }
        (folder / "receipt.json").write_text(json.dumps(r))
        return folder

    def check(
        self,
        fault="failure",
        kind="AssertionError",
        changed_tests=False,
        restored="correct",
        **kwargs,
    ):
        b = self.receipt("baseline")
        f = self.receipt(
            "fault", fault, "wrong", "changed" if changed_tests else "independent", kind
        )
        r = self.receipt("restored", impl=restored)
        return self.run_cli(
            "check",
            b,
            f,
            r,
            "--target",
            "PriceTest::known_90",
            *kwargs.get("extra", []),
        )

    def test_target_assertion_is_detected_without_semantic_verdict(self):
        rc, r = self.check()
        self.assertEqual(rc, 0)
        self.assertEqual(r["fault_evidence"], "detected")
        self.assertEqual(r["verdict"], "not_assessed")
        self.assertEqual(r["oracle"]["status"], "unknown")

    def test_surviving_fault_is_not_pass(self):
        rc, r = self.check("passed")
        self.assertEqual(rc, 2)
        self.assertEqual(r["fault_evidence"], "survived")

    def test_non_assertion_failure_is_invalid(self):
        rc, r = self.check(kind="RuntimeException")
        self.assertEqual(rc, 2)
        self.assertIn("non-assertion", r["reason"])

    def test_skipped_target_not_detection(self):
        self.assertEqual(self.check("skipped")[0], 2)

    def test_test_edits_not_detection(self):
        rc, r = self.check(changed_tests=True)
        self.assertEqual(rc, 2)
        self.assertIn("tests/context changed", r["reason"])

    def test_restoration_must_match_original(self):
        self.assertEqual(self.check(restored="not-restored")[0], 2)

    def test_non_target_identity_rejected(self):
        self.assertEqual(self.check(extra=["--target", "Wrong::identity"])[0], 2)

    def test_tampered_raw_report_is_invalid(self):
        b = self.receipt("baseline")
        f = self.receipt("fault", "failure", "wrong")
        r = self.receipt("restored")
        (f / "report.xml").write_text("<testsuite/>")
        rc, report = self.run_cli("check", b, f, r, "--target", "PriceTest::known_90")
        self.assertEqual(rc, 2)
        self.assertIn("hash mismatch", report["reason"])

    def capture(self, xml, command=None, **kwargs):
        (self.root / "source.txt").write_text("production")
        (self.root / "tests.txt").write_text("known case")
        args = [
            "capture",
            "--out",
            self.root / "capture",
            "--source",
            "source.txt",
            "--test-source",
            "tests.txt",
            "--language",
            "fixture",
            "--framework",
            "control",
            "--junit-stdout",
            "--timeout",
            kwargs.get("timeout", 10),
        ]
        for target in kwargs.get("targets", []):
            args += ["--target", target]
        args += ["--"]
        return self.run_cli(
            *args, *(command or [sys.executable, "-c", "print(" + repr(xml) + ")"])
        )

    def test_xunit_generic_logger_assertion_is_attributed(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure type="failure" message="Assert.Equal() Failure: Values differ"/></testcase></testsuite>'
        )
        self.assertTrue(rows[0]["assertion_failure"])

    def test_runtime_exception_mentioning_xunit_message_not_assertion(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure type="RuntimeException" message="Assert.Equal() Failure: Values differ"/></testcase></testsuite>'
        )
        self.assertFalse(rows[0]["assertion_failure"])

    def test_xctest_native_assertion_message_is_attributed(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure message="/tmp/Test.swift:5 - XCTAssertEqual failed: wrong amount"/></testcase></testsuite>'
        )
        self.assertTrue(rows[0]["assertion_failure"])

    def test_runtime_exception_with_assertion_words_is_not_attributed(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure type="RuntimeException" message="AssertionError ERR_ASSERTION /tmp/Test.swift:5 - XCTAssertEqual failed:"/></testcase></testsuite>'
        )
        self.assertFalse(rows[0]["assertion_failure"])

    def test_android_native_assertion_without_type_is_attributed(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure>java.lang.AssertionError: expected 90\nat org.junit.Assert.assertEquals(Assert.java:1)</failure></testcase></testsuite>'
        )
        self.assertTrue(rows[0]["assertion_failure"])

    def test_android_runtime_cause_mention_is_not_attributed(self):
        from test_quality import junit

        rows = junit(
            b'<testsuite><testcase name="x"><failure>java.lang.IllegalStateException: runtime failed\nCaused by java.lang.AssertionError: description\nat org.junit.Assert.assertEquals(Assert.java:1)</failure></testcase></testsuite>'
        )
        self.assertFalse(rows[0]["assertion_failure"])

    def test_zero_cases_capture_invalid(self):
        rc, r = self.capture("<testsuite/>")
        self.assertEqual(rc, 2)
        self.assertIn("zero testcases", r["reason"])

    def test_wrapper_success_without_selected_target_invalid(self):
        rc, r = self.capture(
            '<testsuite><testcase classname="test" name="file.cjs"/></testsuite>',
            targets=["test::known_90"],
        )
        self.assertEqual(rc, 2)
        self.assertIn("expected target missing", r["reason"])

    def test_suite_error_capture_invalid(self):
        rc, r = self.capture(
            '<testsuite><testcase name="x"/><error type="ImportError"/></testsuite>'
        )
        self.assertEqual(rc, 2)
        self.assertIn("suite errors", r["reason"])

    def test_duplicate_identity_capture_invalid(self):
        rc, r = self.capture(
            '<testsuite><testcase name="x"/><testcase name="x"/></testsuite>'
        )
        self.assertEqual(rc, 2)
        self.assertIn("duplicate", r["reason"])

    def test_entity_declaration_capture_invalid(self):
        self.assertEqual(self.capture("<!DOCTYPE testsuite><testsuite/>")[0], 2)

    def test_command_not_found_invalid(self):
        self.assertEqual(self.capture("", command=["/no-such-runtime"])[0], 2)

    def test_timeout_not_detection(self):
        rc, r = self.capture(
            "", command=[sys.executable, "-c", "import time; time.sleep(30)"], timeout=1
        )
        self.assertEqual(rc, 2)
        self.assertIn("timeout", r["reason"])

    def test_missing_quality_sidecar_does_not_break_legacy_help(self):
        alone = self.root / "lumos"
        shutil.copy2(TOOL, alone)
        r = subprocess.run(
            [sys.executable, str(alone), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(r.returncode, 0)

    def test_suite_failure_summary_cannot_hide_green_case(self):
        rc, result = self.capture(
            '<testsuite tests="1" failures="1"><testcase name="x"/></testsuite>'
        )
        self.assertEqual(rc, 2)
        self.assertEqual(result["status"], "invalid")

    def test_root_failure_summary_cannot_hide_green_case(self):
        rc, _ = self.capture(
            '<testsuites failures="1"><testsuite><testcase name="x"/></testsuite></testsuites>'
        )
        self.assertEqual(rc, 2)

    def test_consistent_suite_summary_retains_green_capture(self):
        rc, result = self.capture(
            '<testsuite tests="1" failures="0" errors="0" skipped="0"><testcase name="x"/></testsuite>'
        )
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "executed")

    def test_partial_sidecar_returns_structured_invalid(self):
        for missing in ["test_quality_scan.py", "test_quality_semgrep.py"]:
            with self.subTest(missing=missing):
                directory = self.root / missing
                directory.mkdir()
                for name in [
                    "lumos",
                    "test_quality.py",
                    "test_quality_scan.py",
                    "test_quality_semgrep.py",
                ]:
                    if name != missing:
                        shutil.copy2(TOOL.with_name(name), directory / name)
                run = subprocess.run(
                    [
                        sys.executable,
                        str(directory / "lumos"),
                        "test-quality",
                        "scan",
                        str(TOOL),
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(run.returncode, 2)
                self.assertFalse(json.loads(run.stdout)["complete"])
                self.assertNotIn("Traceback", run.stderr)

    def test_missing_all_sidecars_explains_update(self):
        alone = self.root / "lumos"
        shutil.copy2(TOOL, alone)
        run = subprocess.run(
            [sys.executable, str(alone), "test-quality", "scan", "tests.py", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(run.returncode, 2)
        self.assertIn("lumos update", run.stdout + run.stderr)

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_output_limit_stops_writer_before_completion(self):
        marker = self.root / "writer-completed"
        command = [
            sys.executable,
            "-c",
            "import sys; from pathlib import Path; sys.stdout.buffer.write(b'x'*(30*1024*1024)); sys.stdout.flush(); Path("
            + repr(str(marker))
            + ").write_text('completed')",
        ]
        rc, result = self.capture("", command=command)
        self.assertEqual(rc, 2)
        self.assertIn("output exceeds", result["reason"])
        self.assertFalse(marker.exists())

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
    def test_cancelled_capture_stops_child(self):
        source = self.root / "source.txt"
        tests = self.root / "tests.txt"
        source.write_text("production")
        tests.write_text("known case")
        pidfile = self.root / "pid.txt"
        command = [
            sys.executable,
            "-c",
            "import os,time; from pathlib import Path; Path("
            + repr(str(pidfile))
            + ").write_text(str(os.getpid())); time.sleep(60)",
        ]
        args = [
            sys.executable,
            str(TOOL),
            "test-quality",
            "capture",
            "--out",
            str(self.root / "capture"),
            "--source",
            str(source),
            "--test-source",
            str(tests),
            "--language",
            "fixture",
            "--framework",
            "control",
            "--junit-stdout",
            "--",
            *command,
        ]
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 5
        while not pidfile.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(pidfile.exists(), "child actually entered before cancellation")
        pid = int(pidfile.read_text())
        self.addCleanup(
            lambda: os.kill(pid, signal.SIGKILL) if self.alive(pid) else None
        )
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=5)
        deadline = time.monotonic() + 2
        while self.alive(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(self.alive(pid))

    @staticmethod
    def lumos_module():
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader('quality_lumos_control', str(TOOL))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def test_eval_attachments_keep_actual_code_as_impact_seeds(self):
        module = self.lumos_module()
        prefix = 'governance/eval/results/fixture/'
        for suffix in ['txt', 'xml', 'log', 'trx', 'zip']:
            self.assertFalse(module._impact_diff_seed_ok(prefix + 'report.' + suffix, '100644', False))
        for name, mode, shebang in [('test.py', '100644', None), ('runner.txt', '100755', None), ('runner', '100644', True)]:
            self.assertTrue(module._impact_diff_seed_ok(prefix + name, mode, shebang))
        self.assertTrue(module._impact_diff_seed_ok(prefix + 'unknown.txt'))
        self.assertNotIn('governance/eval/results/', module._BOOKKEEPING_DIRS)

    def test_deinit_removes_only_vendored_bytecode(self):
        module = self.lumos_module()
        cache = self.root / 'scripts/__pycache__'
        cache.mkdir(parents=True)
        owned = cache / 'test_quality.cpython-314.pyc'
        user = cache / 'user_app.cpython-314.pyc'
        owned.write_bytes(b'owned')
        user.write_bytes(b'user')
        module._deinit_remove_vendored(self.root)
        self.assertFalse(owned.exists())
        self.assertEqual(user.read_bytes(), b'user')
        user.unlink()
        cache.rmdir()
        external = self.root / 'external'
        external.mkdir()
        target = external / owned.name
        target.write_bytes(b'external')
        cache.symlink_to(external, target_is_directory=True)
        module._deinit_remove_vendored(self.root)
        self.assertEqual(target.read_bytes(), b'external')

    def test_scan_entrypoints_share_options_and_results(self):
        test_file = self.root / 'test_sample.py'
        test_file.write_text('def test_same():\n    assert 1 == 1\n')
        cli_rc, cli_result = self.run_cli('scan', '--json', test_file, '--check-helper', 'check')
        run = subprocess.run([sys.executable, str(TOOL.with_name('test_quality_scan.py')), '--json', str(test_file), '--check-helper', 'check'], capture_output=True, text=True, timeout=10)
        standalone = json.loads(run.stdout)
        self.assertEqual(run.returncode, cli_rc)
        for report in [cli_result, standalone]:
            report.pop('elapsed_seconds')
        self.assertEqual(cli_result, standalone)
        self.assertEqual(cli_result['findings'][0]['rule_id'], 'same-comparison')

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_model_timeout_stops_worker_without_paid_call(self):
        path = TOOL.parent.parent / "governance/eval/test_quality_handbook.py"
        spec = importlib.util.spec_from_file_location("test_handbook_worker", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
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


if __name__ == "__main__":
    unittest.main()
