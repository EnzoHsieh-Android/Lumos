#!/usr/bin/env python3
"""Independent evidence validity controls; no implementation formula copied into expected."""

import hashlib
import os
import re
import signal
import stat
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
        receipt = json.loads((self.root / "capture" / "receipt.json").read_text())
        self.assertEqual(receipt["status"], "invalid")
        self.assertEqual(receipt["reason"], "execution interrupted by signal 15")

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_timeout_after_streams_close_keeps_partial_output(self):
        command = [
            sys.executable,
            "-c",
            "import os,time; print('partial',flush=True); os.close(1); os.close(2); time.sleep(30)",
        ]
        module = self.quality_module()
        with self.assertRaises(module.CaptureTimeout) as caught:
            module.run_capture_command(command, 5)
        self.assertEqual(caught.exception.stdout.strip(), b"partial")
        self.assertEqual(str(caught.exception), "timeout; never detected")

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_zombie_only_group_permission_error_is_not_fatal(self):
        module = self.quality_module()
        calls = []

        def zombie_group(pgid, sig):
            calls.append(pgid)
            raise PermissionError(1, "Operation not permitted")

        with mock.patch.object(module.os, "killpg", zombie_group):
            rc, out, _ = module.run_capture_command([sys.executable, "-c", "print('done')"], 5)
        self.assertTrue(calls, "cleanup really reached killpg")
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), b"done")

    @unittest.skipUnless(os.name == "posix", "POSIX process group qualification")
    def test_failed_capture_stops_stream_detached_worker(self):
        pidfile = self.root / "failed-worker.pid"
        command = [
            sys.executable,
            "-c",
            "import subprocess,sys; from pathlib import Path; "
            "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],"
            "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
            "Path(" + repr(str(pidfile)) + ").write_text(str(p.pid)); sys.exit(1)",
        ]
        module = self.quality_module()
        rc, _, _ = module.run_capture_command(command, 5)
        self.assertEqual(rc, 1)
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
    def test_failed_capture_stops_worker_that_inherits_streams(self):
        command = [
            sys.executable,
            "-c",
            "import subprocess,sys,time; "
            "p=subprocess.Popen([sys.executable,'-c',"
            "'import time; print(\"worker-holds-stream\",flush=True); time.sleep(60)']); "
            "time.sleep(0.3); print('launcher-failed',p.pid,flush=True); sys.exit(1)",
        ]
        module = self.quality_module()
        rc, out, _ = module.run_capture_command(command, 5)
        self.assertEqual(rc, 1)
        lines = out.decode().split()
        self.assertIn("worker-holds-stream", lines, "worker really shared the captured stream")
        pid = int(lines[lines.index("launcher-failed") + 1])
        self.addCleanup(
            lambda: os.kill(pid, signal.SIGKILL) if self.alive(pid) else None
        )
        deadline = time.monotonic() + 2
        while self.alive(pid) and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(self.alive(pid))

    @staticmethod
    def lumos_module():
        from importlib.machinery import SourceFileLoader

        loader = SourceFileLoader("quality_lumos_control", str(TOOL))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    @staticmethod
    def quality_module():
        from importlib.machinery import SourceFileLoader

        path = TOOL.with_name("test_quality.py")
        loader = SourceFileLoader("test_quality_process_control", str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def test_eval_attachments_keep_actual_code_as_impact_seeds(self):
        module = self.lumos_module()
        prefix = "governance/eval/results/fixture/"
        for suffix in ["txt", "xml", "log", "trx", "zip"]:
            self.assertFalse(
                module._impact_diff_seed_ok(
                    prefix + "report." + suffix, "100644", False
                )
            )
        for name, mode, shebang in [
            ("test.py", "100644", None),
            ("runner.txt", "100755", None),
            ("runner", "100644", True),
        ]:
            self.assertTrue(module._impact_diff_seed_ok(prefix + name, mode, shebang))
        self.assertTrue(module._impact_diff_seed_ok(prefix + "unknown.txt"))
        self.assertNotIn("governance/eval/results/", module._BOOKKEEPING_DIRS)

    def test_deinit_removes_only_vendored_bytecode(self):
        module = self.lumos_module()
        cache = self.root / "scripts/__pycache__"
        cache.mkdir(parents=True)
        owned = cache / "test_quality.cpython-314.pyc"
        user = cache / "user_app.cpython-314.pyc"
        owned.write_bytes(b"owned")
        user.write_bytes(b"user")
        module._deinit_remove_vendored(self.root)
        self.assertFalse(owned.exists())
        self.assertEqual(user.read_bytes(), b"user")
        user.unlink()
        cache.rmdir()
        external = self.root / "external"
        external.mkdir()
        target = external / owned.name
        target.write_bytes(b"external")
        cache.symlink_to(external, target_is_directory=True)
        module._deinit_remove_vendored(self.root)
        self.assertEqual(target.read_bytes(), b"external")

    def test_scan_entrypoints_share_options_and_results(self):
        test_file = self.root / "test_sample.py"
        test_file.write_text("def test_same():\n    assert 1 == 1\n")
        cli_rc, cli_result = self.run_cli(
            "scan", "--json", test_file, "--check-helper", "check"
        )
        run = subprocess.run(
            [
                sys.executable,
                str(TOOL.with_name("test_quality_scan.py")),
                "--json",
                str(test_file),
                "--check-helper",
                "check",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        standalone = json.loads(run.stdout)
        self.assertEqual(run.returncode, cli_rc)
        for report in [cli_result, standalone]:
            report.pop("elapsed_seconds")
        self.assertEqual(cli_result, standalone)
        self.assertEqual(cli_result["findings"][0]["rule_id"], "same-comparison")

    def copied_bundle(self, old=False):
        target = self.root / "scripts"
        target.mkdir()
        for name in [
            "lumos",
            "test_quality.py",
            "test_quality_scan.py",
            "test_quality_semgrep.py",
        ]:
            shutil.copy2(TOOL.with_name(name), target / name)
        if old:
            core = target / "test_quality.py"
            current = core.read_bytes()
            previous = current.replace(b"    validate_suite_counts(root)\n", b"")
            self.assertNotEqual(
                previous, current, "old package fixture must omit summary validation"
            )
            core.write_bytes(previous)
        return target

    def test_mixed_sidecars_refused_before_false_green(self):
        target = self.copied_bundle(old=True)
        (self.root / "source.txt").write_text("production")
        (self.root / "tests.txt").write_text("independent")
        xml = '<testsuite tests="1" failures="1"><testcase name="x"/></testsuite>'
        run = subprocess.run(
            [
                sys.executable,
                str(target / "lumos"),
                "test-quality",
                "capture",
                "--out",
                "capture",
                "--source",
                "source.txt",
                "--test-source",
                "tests.txt",
                "--junit-stdout",
                "--language",
                "fixture",
                "--framework",
                "control",
                "--",
                sys.executable,
                "-c",
                "print(" + repr(xml) + ")",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertEqual(json.loads(run.stdout)["verdict"], "not_assessed")
        self.assertFalse((self.root / "capture").exists())

    def test_orphan_failure_refused(self):
        rc, report = self.capture(
            '<testsuite><testcase classname="T" name="x"/><failure type="AssertionError">boom</failure></testsuite>'
        )
        self.assertEqual(rc, 2, report)
        self.assertIn("outcome outside testcase", report["reason"])

    def test_php_and_node_variants_kept_in_impact(self):
        tool = self.lumos_module()
        for name in ["Test.php", "runner.cjs", "runner.mts", "runner.cts"]:
            with self.subTest(name=name):
                self.assertTrue(
                    tool._impact_diff_seed_ok(
                        "governance/eval/results/example/" + name, "100644", None
                    )
                )

    def test_owned_extensionless_cache_removed(self):
        target = self.copied_bundle()
        from importlib.machinery import SourceFileLoader

        loader = SourceFileLoader("copied_lumos_cache", str(target / "lumos"))
        module_spec = importlib.util.spec_from_loader(loader.name, loader)
        tool = importlib.util.module_from_spec(module_spec)
        loader.exec_module(tool)
        cache = target / "__pycache__"
        owned = list(cache.glob("lumos*.pyc"))
        self.assertTrue(owned, "SourceFileLoader must actually create bytecode")
        user = cache / "lumos_user.cpython-314.pyc"
        user.write_bytes(b"user bytes")
        tool._deinit_remove_vendored(self.root)
        self.assertFalse(any(p.exists() for p in owned))
        self.assertEqual(user.read_bytes(), b"user bytes")

    def test_resolved_cache_escape_preserved(self):
        tool = self.lumos_module()
        target = self.root / "external"
        target.mkdir()
        artifact = target / "test_quality.cpython-314.pyc"
        artifact.write_bytes(b"external")
        (self.root / "scripts").mkdir()
        cache = self.root / "scripts/__pycache__"
        cache.symlink_to(target, target_is_directory=True)
        self.assertEqual(cache.resolve(), target.resolve())
        with mock.patch.object(Path, "is_symlink", return_value=False):
            tool._deinit_remove_vendored(self.root)
        self.assertEqual(artifact.read_bytes(), b"external")

    def test_results_rename_preserves_original_role_source(self):
        tool = self.lumos_module()
        repository = self.root / "rename"
        repository.mkdir()

        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(repository), *args],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10,
            ).strip()

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (repository / "service.py").write_text("def public_api():\n    return 42\n")
        git("add", "service.py")
        git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false", "commit", "-qm", "before")
        before = git("rev-parse", "HEAD")
        destination = repository / "governance/eval/results/run/report.txt"
        destination.parent.mkdir(parents=True)
        git("mv", "service.py", str(destination.relative_to(repository)))
        git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false", "commit", "-qm", "after")
        after = git("rev-parse", "HEAD")
        self.assertTrue(
            git("diff", "--name-status", "-M", before, after).startswith("R100"),
            "real rename must be recognized",
        )
        self.assertIn(
            ("service.py", before),
            tool._review_role_changed_files(repository, before, after),
        )

    def test_mixed_scanner_retains_legacy_help(self):
        target = self.copied_bundle()
        (target / "test_quality_scan.py").write_text(
            "# previous scanner has no shared argument export\n"
        )
        run = subprocess.run(
            [sys.executable, str(target / "lumos"), "--help"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn("Traceback", run.stderr)

    def test_invalid_semgrep_rule_has_structured_shape_error(self):
        source = self.root / "test_sample.php"
        source.write_text("<?php assert(true);")
        backend = self.root / "semgrep"
        backend.write_text(
            "#!"
            + sys.executable
            + "\n"
            + "import json,sys\n"
            + "p=sys.argv[-1]\n"
            + 'print(json.dumps({"results":[{"check_id":None,"path":p,"start":{"line":1}}],"errors":[],"paths":{"scanned":[p]}}))\n'
        )
        backend.chmod(0o755)
        rc, report = self.run_cli("scan", "--json", "--semgrep", backend, source)
        self.assertEqual(rc, 2)
        self.assertFalse(report["complete"])
        self.assertEqual(report["verdict"], "not_assessed")
        self.assertIn("invalid finding rule", report["inputs"][0]["reason"])

    def plant_stale_bytecode(self, path, needle, replacement):
        """把 needle 換掉編出舊 bytecode,再還原同大小、同時間戳的正確來源。"""
        from importlib.machinery import SourceFileLoader

        good = path.read_bytes()
        old = good.replace(needle, replacement, 1)
        self.assertLess(len(old), len(good))
        path.write_bytes(old + b" " * (len(good) - len(old)))
        loader = SourceFileLoader("quality_old_cache_" + path.stem, str(path))
        loader.exec_module(importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader)))
        cache = Path(importlib.util.cache_from_source(str(path)))
        self.assertTrue(cache.exists(), "stale cache must exist before restoration")
        old_stamp = path.stat()
        path.write_bytes(good)
        os.utime(path, ns=(old_stamp.st_atime_ns, old_stamp.st_mtime_ns))
        self.assertEqual(path.read_bytes(), good, "source actually restored")

    def test_source_bytes_not_stale_bytecode_authorize_capture(self):
        target = self.copied_bundle()
        self.plant_stale_bytecode(target / "test_quality.py", b"    validate_suite_counts(root)\n", b"")
        (self.root / "source.txt").write_text("production")
        (self.root / "tests.txt").write_text("independent")
        xml = '<testsuite tests="1" failures="1"><testcase name="x"/></testsuite>'
        run = subprocess.run(
            [
                sys.executable,
                str(target / "lumos"),
                "test-quality",
                "capture",
                "--out",
                "capture",
                "--source",
                "source.txt",
                "--test-source",
                "tests.txt",
                "--junit-stdout",
                "--language",
                "fixture",
                "--framework",
                "control",
                "--",
                sys.executable,
                "-c",
                "print(" + repr(xml) + ")",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(run.returncode, 2, run.stdout)
        report = json.loads(run.stdout)
        self.assertEqual(report["status"], "invalid")
        self.assertIn("suite summary inconsistent with testcase rows", report["reason"])

    def test_semgrep_adapter_uses_verified_runner_not_stale_bytecode(self):
        target = self.copied_bundle()
        self.plant_stale_bytecode(target / "test_quality.py", b"    import time\n", b"    1/0\n")
        source = self.root / "Test.swift"
        source.write_text("func testTotal() { XCTAssertEqual(total(3, 5), 15) }")
        fake = self.root / "semgrep"
        fake.write_text(
            "#!" + sys.executable + "\nimport json,sys\n"
            "print(json.dumps({'results':[],'errors':[],'paths':{'scanned':[sys.argv[-1]]},'version':'fixture'}))\n"
        )
        fake.chmod(0o700)
        run = subprocess.run(
            [sys.executable, str(target / "lumos"), "test-quality", "scan", str(source),
             "--json", "--semgrep", str(fake)],
            cwd=self.root, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)["inputs"][0]["status"], "scanned")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO")
    def test_fifo_sidecar_does_not_hang_other_commands(self):
        target = self.copied_bundle()
        sidecar = target / "test_quality_scan.py"
        sidecar.unlink()
        os.mkfifo(sidecar)
        self.assertTrue(stat.S_ISFIFO(sidecar.stat().st_mode), "sidecar really replaced by a FIFO")
        version = subprocess.run([sys.executable, str(target / "lumos"), "--version"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(version.returncode, 0, version.stderr)
        quality = subprocess.run([sys.executable, str(target / "lumos"), "test-quality", "capabilities"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(quality.returncode, 2)
        self.assertFalse(json.loads(quality.stdout)["complete"])

    def test_bundle_reference_guard_rejects_wrong_load_order(self):
        module = self.lumos_module()
        names = ("test_quality", "test_quality_scan", "test_quality_semgrep")
        saved = {n: sys.modules.pop(n) for n in names if n in sys.modules}
        self.addCleanup(lambda: [sys.modules.pop(n, None) for n in names] and sys.modules.update(saved))
        self.assertIsNone(module._test_quality_load_bundle(), "correct order loads cleanly")
        for n in names:
            sys.modules.pop(n, None)
        wrong = ("test_quality_semgrep.py", "test_quality_scan.py", "test_quality.py")
        with mock.patch.object(module, "_TEST_QUALITY_LOAD_ORDER", wrong):
            error = module._test_quality_load_bundle()
        self.assertIsNotNone(error)
        self.assertIn("混到未驗來源", error)

    def test_bundle_reference_guard_judges_by_identity(self):
        import functools
        import types

        guard = self.lumos_module()._test_quality_bundle_unverified_refs
        core = types.ModuleType("core")

        def real():
            return 1

        @functools.wraps(real)
        def wrapped():
            return real()

        def make():
            def inner():
                return 2
            return inner

        class Option:
            pass

        core.real, core.wrapped, core.made, core.DEFAULT = real, wrapped, make(), Option()
        for obj in (real, wrapped, core.made):
            obj.__module__ = "core"
        Option.__module__ = "core"
        user = types.ModuleType("user")
        user.rc, user.wrapped, user.main, user.d2, user.core = real, wrapped, core.made, core.DEFAULT, core
        self.assertIsNone(guard({"core": core, "user": user}), "wrapped, factory and aliased instances are verified")
        stale = types.ModuleType("core")
        user.core = stale
        self.assertIn("user.core", guard({"core": core, "user": user}))

    def test_incomplete_bundle_short_help_is_structured(self):
        target = self.copied_bundle()
        (target / "test_quality_semgrep.py").unlink()
        run = subprocess.run([sys.executable, str(target / "lumos"), "test-quality", "-h"],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 2, run.stderr)
        report = json.loads(run.stdout)
        self.assertFalse(report["complete"])
        self.assertIn("lumos update", report["reason"])

    def test_sidecar_runtime_error_only_blocks_test_quality(self):
        target = self.copied_bundle()
        sidecar = target / "test_quality_scan.py"
        broken = sidecar.read_bytes() + b"\nraise RuntimeError('sidecar import failure')\n"
        sidecar.write_bytes(broken)
        lumos = target / "lumos"
        text = lumos.read_text(encoding="utf-8")
        old_digest = re.search(r"'test_quality_scan\.py': '([0-9a-f]{64})'", text).group(1)
        new_digest = hashlib.sha256(broken.replace(b"\r\n", b"\n")).hexdigest()
        lumos.write_text(text.replace(old_digest, new_digest), encoding="utf-8")
        version = subprocess.run([sys.executable, str(lumos), "--version"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(version.returncode, 0, version.stderr)
        quality = subprocess.run([sys.executable, str(lumos), "test-quality", "capabilities"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(quality.returncode, 2)
        self.assertIn("sidecar import failure", json.loads(quality.stdout)["reason"])

    def test_utf16_dtd_is_not_a_valid_receipt(self):
        xml = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE testsuite [<!ENTITY label "ok">]><testsuite><testcase name="&label;"/></testsuite>'
        command = [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(" + repr(xml) + '.encode("utf-16"))',
        ]
        rc, report = self.capture("", command=command)
        self.assertEqual(rc, 2)
        self.assertEqual(report["status"], "invalid")
        self.assertIn("DTD", report["reason"])

    def test_plain_utf16_report_retains_valid_capture(self):
        xml = '<?xml version="1.0" encoding="UTF-16"?><testsuite><testcase name="ok"/></testsuite>'
        command = [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(" + repr(xml) + '.encode("utf-16"))',
        ]
        rc, report = self.capture("", command=command)
        self.assertEqual(rc, 0)
        self.assertEqual(report["status"], "executed")

    def test_global_vault_option_retains_structured_deployment_error(self):
        target = self.copied_bundle()
        (target / "test_quality_scan.py").unlink()
        (self.root / "sample.py").write_text("def value():\n    return 1\n")
        run = subprocess.run(
            [
                sys.executable,
                str(target / "lumos"),
                "--vault",
                str(self.root / "vault"),
                "test-quality",
                "scan",
                "sample.py",
                "--json",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(run.returncode, 2, run.stderr)
        report = json.loads(run.stdout)
        self.assertFalse(report["complete"])
        self.assertEqual(report["verdict"], "not_assessed")
        self.assertIn("test_quality_scan.py", report["reason"])
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
