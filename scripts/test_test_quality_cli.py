#!/usr/bin/env python3
"""Independent evidence validity controls; no implementation formula copied into expected."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).with_name('lumos')


class QualityCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def run_cli(self, *args):
        r = subprocess.run([sys.executable, str(TOOL), 'test-quality', *map(str, args)],
                           cwd=self.root, capture_output=True, text=True, timeout=20)
        return r.returncode, json.loads(r.stdout)

    def receipt(self, phase, outcome='passed', impl='correct', tests='independent', failure_type='AssertionError'):
        folder = self.root/phase
        folder.mkdir()
        failure = '' if outcome == 'passed' else '<skipped/>' if outcome == 'skipped' else f'<{outcome} type="{failure_type}">wrong charge</{outcome}>'
        xml = f'<testsuite><testcase classname="PriceTest" name="known_90">{failure}</testcase></testsuite>'.encode()
        (folder/'report.xml').write_bytes(xml)
        snaps = []
        for i, (role, value) in enumerate([('implementation', impl), ('tests', tests), ('context', 'locked')]):
            raw = value.encode(); artifact = f'snapshot-{i}.txt'
            (folder/artifact).write_bytes(raw)
            snaps.append({'role': role, 'path': '/isolated/'+role, 'artifact': artifact, 'sha256': hashlib.sha256(raw).hexdigest()})
        cases = [{'id': 'PriceTest::known_90', 'status': outcome, 'assertion_failure': outcome == 'failure' and failure_type == 'AssertionError',
                  'reason': '' if outcome == 'passed' or outcome == 'skipped' else failure_type+'  wrong charge'}]
        r = {'schema_version': 1, 'kind': 'execution-receipt', 'status': 'executed', 'language': 'fixture',
             'framework': 'junit-control', 'command': ['trusted-runner'], 'cwd': '/isolated',
             'exit_code': 0 if outcome == 'passed' else 1, 'report_sha256': hashlib.sha256(xml).hexdigest(),
             'tests': cases, 'snapshots': snaps}
        (folder/'receipt.json').write_text(json.dumps(r))
        return folder

    def check(self, fault='failure', kind='AssertionError', changed_tests=False, restored='correct', **kwargs):
        b = self.receipt('baseline')
        f = self.receipt('fault', fault, 'wrong', 'changed' if changed_tests else 'independent', kind)
        r = self.receipt('restored', impl=restored)
        return self.run_cli('check', b, f, r, '--target', 'PriceTest::known_90', *kwargs.get('extra', []))

    def test_target_assertion_is_detected_without_semantic_verdict(self):
        rc, r = self.check()
        self.assertEqual(rc, 0)
        self.assertEqual(r['fault_evidence'], 'detected')
        self.assertEqual(r['verdict'], 'not_assessed')
        self.assertEqual(r['oracle']['status'], 'unknown')

    def test_surviving_fault_is_not_pass(self):
        rc, r = self.check('passed')
        self.assertEqual(rc, 2)
        self.assertEqual(r['fault_evidence'], 'survived')

    def test_non_assertion_failure_is_invalid(self):
        rc, r = self.check(kind='RuntimeException')
        self.assertEqual(rc, 2)
        self.assertIn('non-assertion', r['reason'])

    def test_skipped_target_not_detection(self):
        self.assertEqual(self.check('skipped')[0], 2)

    def test_test_edits_not_detection(self):
        rc, r = self.check(changed_tests=True)
        self.assertEqual(rc, 2)
        self.assertIn('tests/context changed', r['reason'])

    def test_restoration_must_match_original(self):
        self.assertEqual(self.check(restored='not-restored')[0], 2)

    def test_non_target_identity_rejected(self):
        self.assertEqual(self.check(extra=['--target', 'Wrong::identity'])[0], 2)

    def test_tampered_raw_report_is_invalid(self):
        b=self.receipt('baseline');f=self.receipt('fault','failure','wrong');r=self.receipt('restored')
        (f/'report.xml').write_text('<testsuite/>')
        rc, report=self.run_cli('check',b,f,r,'--target','PriceTest::known_90')
        self.assertEqual(rc,2);self.assertIn('hash mismatch',report['reason'])

    def capture(self, xml, command=None, **kwargs):
        (self.root/'source.txt').write_text('production')
        (self.root/'tests.txt').write_text('known case')
        args=['capture','--out',self.root/'capture','--source','source.txt','--test-source','tests.txt',
              '--language','fixture','--framework','control','--junit-stdout','--timeout',kwargs.get('timeout',10)]
        for target in kwargs.get('targets', []):
            args += ['--target', target]
        args += ['--']
        return self.run_cli(*args, *(command or [sys.executable,'-c','print('+repr(xml)+')']))

    def test_xunit_generic_logger_assertion_is_attributed(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure type="failure" message="Assert.Equal() Failure: Values differ"/></testcase></testsuite>')
        self.assertTrue(rows[0]['assertion_failure'])

    def test_runtime_exception_mentioning_xunit_message_not_assertion(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure type="RuntimeException" message="Assert.Equal() Failure: Values differ"/></testcase></testsuite>')
        self.assertFalse(rows[0]['assertion_failure'])

    def test_xctest_native_assertion_message_is_attributed(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure message="/tmp/Test.swift:5 - XCTAssertEqual failed: wrong amount"/></testcase></testsuite>')
        self.assertTrue(rows[0]['assertion_failure'])

    def test_runtime_exception_with_assertion_words_is_not_attributed(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure type="RuntimeException" message="AssertionError ERR_ASSERTION /tmp/Test.swift:5 - XCTAssertEqual failed:"/></testcase></testsuite>')
        self.assertFalse(rows[0]['assertion_failure'])

    def test_android_native_assertion_without_type_is_attributed(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure>java.lang.AssertionError: expected 90\nat org.junit.Assert.assertEquals(Assert.java:1)</failure></testcase></testsuite>')
        self.assertTrue(rows[0]['assertion_failure'])

    def test_android_runtime_cause_mention_is_not_attributed(self):
        from test_quality import junit
        rows=junit(b'<testsuite><testcase name="x"><failure>java.lang.IllegalStateException: runtime failed\nCaused by java.lang.AssertionError: description\nat org.junit.Assert.assertEquals(Assert.java:1)</failure></testcase></testsuite>')
        self.assertFalse(rows[0]['assertion_failure'])

    def test_zero_cases_capture_invalid(self):
        rc,r=self.capture('<testsuite/>')
        self.assertEqual(rc,2);self.assertIn('zero testcases',r['reason'])

    def test_wrapper_success_without_selected_target_invalid(self):
        rc,r=self.capture('<testsuite><testcase classname="test" name="file.cjs"/></testsuite>', targets=['test::known_90'])
        self.assertEqual(rc,2);self.assertIn('expected target missing',r['reason'])

    def test_suite_error_capture_invalid(self):
        rc,r=self.capture('<testsuite><testcase name="x"/><error type="ImportError"/></testsuite>')
        self.assertEqual(rc,2);self.assertIn('suite errors',r['reason'])

    def test_duplicate_identity_capture_invalid(self):
        rc,r=self.capture('<testsuite><testcase name="x"/><testcase name="x"/></testsuite>')
        self.assertEqual(rc,2);self.assertIn('duplicate',r['reason'])

    def test_entity_declaration_capture_invalid(self):
        self.assertEqual(self.capture('<!DOCTYPE testsuite><testsuite/>')[0],2)

    def test_command_not_found_invalid(self):
        self.assertEqual(self.capture('',command=['/no-such-runtime'])[0],2)

    def test_timeout_not_detection(self):
        rc,r=self.capture('',command=[sys.executable,'-c','import time; time.sleep(30)'],timeout=1)
        self.assertEqual(rc,2);self.assertIn('timeout',r['reason'])

    def test_missing_quality_sidecar_does_not_break_legacy_help(self):
        alone=self.root/'lumos';shutil.copy2(TOOL,alone)
        r=subprocess.run([sys.executable,str(alone),'--help'],capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,0)


if __name__ == '__main__':
    unittest.main()
