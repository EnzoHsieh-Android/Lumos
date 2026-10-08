"""CLI 行為考卷；預期結果來自人工分類，不呼叫掃描器算 oracle。"""
import json
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).with_name('test_quality_scan.py')
SEMGREP_TOOL = Path(__file__).with_name('test_quality_semgrep.py')


class ScanTests(unittest.TestCase):
    @staticmethod
    def semgrep_module():
        loader = SourceFileLoader('test_quality_semgrep_control', str(SEMGREP_TOOL))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module

    def scan(self, source, implementation=None, suffix='.py', check_helper=None):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            test = root / ('test_example' + suffix)
            test.write_text(source, encoding='utf-8')
            before = test.read_bytes()
            command = [sys.executable, str(TOOL), str(test), '--json']
            if check_helper:
                command += ['--check-helper', check_helper]
            if implementation is not None:
                impl = root / 'pricing.py'
                impl.write_text(implementation, encoding='utf-8')
                command += ['--implementation', 'pricing=' + str(impl)]
            run = subprocess.run(command, capture_output=True, text=True, timeout=20)
            self.assertEqual(test.read_bytes(), before, '掃描不可改寫輸入')
            return run.returncode, json.loads(run.stdout)

    def rules(self, report):
        return [item['rule_id'] for item in report['findings']]

    def test_custom_check_helper_is_explicit_and_behaves_like_assert(self):
        source = "def t_split():\n    check('group behavior', split_for('G1') == split_for('G1'), '')\n"
        _, default = self.scan(source)
        self.assertEqual(default['findings'], [])
        self.assertEqual(default['inputs'][0]['tests_with_known_assertions'], 0)
        _, explicit = self.scan(source, check_helper='check')
        self.assertEqual(self.rules(explicit), ['same-comparison'])
        self.assertEqual(explicit['inputs'][0]['tests_with_known_assertions'], 1)
        self.assertEqual(explicit['assertion_helpers'], ['check'])

    def test_same_call_comparison_is_candidate_not_verdict(self):
        rc, out = self.scan("def test_split():\n    assert split_for('G1') == split_for('G1')\n")
        self.assertEqual(rc, 0)
        self.assertEqual(self.rules(out), ['same-comparison'])
        self.assertEqual(out['findings'][0]['status'], 'candidate')
        self.assertEqual(out['verdict'], 'not_assessed')
        self.assertEqual(out['inputs'][0]['tests_seen'], 1)

    def test_independent_known_value_has_no_candidate(self):
        rc, out = self.scan('def test_total():\n    assert total(3, 5) == 15\n')
        self.assertEqual(rc, 0)
        self.assertEqual(out['findings'], [])
        self.assertEqual(out['verdict'], 'not_assessed')

    def test_expected_reuses_same_function_with_other_input(self):
        _, out = self.scan('def test_total():\n    expected = total(3, 5)\n    self.assertEqual(total(5, 3), expected)\n')
        self.assertEqual(self.rules(out), ['oracle-reuses-call'])

    def test_source_only_and_mixed_behavior_are_distinct(self):
        source = 'import inspect\ndef test_pid():\n    src = inspect.getsource(save)\n    self.assertIn("getpid", src)\n'
        _, only = self.scan(source)
        self.assertEqual(self.rules(only), ['source-only'])
        _, mixed = self.scan(source + '    assert save_path(101) == "backlog.101.tmp"\n')
        self.assertNotIn('source-only', self.rules(mixed))

    def test_inspect_alias_and_transformation(self):
        _, out = self.scan('from inspect import getsource as gs\ndef test_shape():\n    src = gs(save).strip()\n    assert "getpid" in src\n')
        self.assertEqual(self.rules(out), ['source-only'])

    def test_mirror_expression_requires_explicit_implementation(self):
        source = 'from pricing import total\ndef test_total():\n    q, p = 3, 5\n    expected = q * p\n    assert total(q, p) == expected\n'
        _, without = self.scan(source)
        self.assertNotIn('mirror-expression', self.rules(without))
        _, with_source = self.scan(source, 'def total(quantity, price):\n    return quantity * price\n')
        self.assertEqual(self.rules(with_source), ['mirror-expression'])

    def test_literal_expectation_is_not_reclassified_as_mirror(self):
        _, out = self.scan('from pricing import total\ndef test_total():\n    assert total(3, 5) == 15\n', 'def total(q, p):\n    return q * p\n')
        self.assertEqual(out['findings'], [])

    def test_reassigned_expected_does_not_use_stale_binding(self):
        _, out = self.scan('def test_total():\n    expected = total(3, 5)\n    expected = 15\n    assert total(3, 5) == expected\n')
        self.assertEqual(out['findings'], [])

    def test_nested_helper_assert_is_not_a_test_assertion(self):
        _, out = self.scan('def test_outer():\n    def helper():\n        assert total(3, 5) == total(3, 5)\n    assert total(3, 5) == 15\n')
        self.assertEqual(out['findings'], [])

    def test_independent_collection_consistency_is_not_same_oracle(self):
        _, out = self.scan('def test_wiring():\n    self.assertEqual(set(prompt_ids), set(runner_ids))\n')
        self.assertEqual(out['findings'], [])

    def test_parse_error_reports_incomplete(self):
        rc, out = self.scan('def test_broken(:\n')
        self.assertEqual(rc, 2)
        self.assertFalse(out['complete'])
        self.assertEqual(out['inputs'][0]['status'], 'error')

    def test_no_tests_is_not_clean(self):
        rc, out = self.scan('x = 1\n')
        self.assertEqual(rc, 2)
        self.assertFalse(out['complete'])
        self.assertEqual(out['inputs'][0]['status'], 'no_tests')

    def test_other_language_is_explicitly_unsupported(self):
        rc, out = self.scan('fun testTotal() = assertEquals(15, total(3, 5))', suffix='.kt')
        self.assertEqual(rc, 2)
        self.assertFalse(out['complete'])
        self.assertEqual(out['inputs'][0]['language'], 'kotlin')
        self.assertEqual(out['inputs'][0]['status'], 'unsupported')

    def test_untrusted_module_is_not_executed(self):
        rc, out = self.scan('raise RuntimeError("DO NOT IMPORT")\ndef test_total():\n    assert total(3, 5) == 15\n')
        self.assertEqual(rc, 0)
        self.assertEqual(out['findings'], [])

    def test_backend_errors_and_skipped_snapshot_are_not_clean(self):
        for payload in ({'results': [], 'errors': [{'message': 'parse failed'}], 'paths': {'scanned': []}},
                        {'results': [], 'errors': [], 'paths': {'scanned': []}}):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as td:
                source = Path(td) / 'Test.swift'
                source.write_text('func testTotal() { XCTAssertEqual(total(3, 5), 15) }')
                fake = Path(td) / 'semgrep'
                fake.write_text('#!' + sys.executable + '\nprint(' + repr(json.dumps(payload)) + ')\n')
                fake.chmod(0o700)
                run = subprocess.run([sys.executable, str(TOOL), str(source), '--json', '--semgrep', str(fake)], capture_output=True, text=True, timeout=20)
                out = json.loads(run.stdout)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(out['inputs'][0]['status'], 'error')
                self.assertFalse(out['complete'])

    def test_semgrep_findings_decode_once_and_reject_out_of_range_line(self):
        module = self.semgrep_module()
        source = Path('/isolated/test_snapshot.php')
        original = Path('/project/test_price.php')

        class Raw:
            calls = 0

            def decode(self, encoding):
                self.calls += 1
                return 'first line\nsecond line\n'

        raw = Raw()
        result = {
            'results': [
                {'check_id': 'lumos.same-comparison', 'path': str(source), 'start': {'line': 1}},
                {'check_id': 'lumos.same-comparison', 'path': str(source), 'start': {'line': 2}},
            ]
        }
        findings = module.backend_findings(result, source, original, raw)
        self.assertEqual(raw.calls, 1)
        self.assertEqual([item['snippet'] for item in findings], ['first line', 'second line'])

        result['results'][1]['start']['line'] = 3
        with self.assertRaisesRegex(ValueError, 'invalid finding location'):
            module.backend_findings(result, source, original, b'first line\nsecond line\n')

    def test_corpus_runner_reports_unavailable_languages(self):
        runner = TOOL.parent.parent / 'governance/eval/test_quality_corpus.py'
        run = subprocess.run([sys.executable, str(runner)], capture_output=True, text=True, timeout=30)
        out = json.loads(run.stdout)
        self.assertEqual(run.returncode, 2)
        self.assertFalse(out['complete'])
        self.assertFalse(out['supported_checks_match'])
        python_cases = [c for c in out['cases'] if c['language'] == 'python']
        self.assertEqual(len(python_cases), 4)
        self.assertEqual({c['status'] for c in python_cases}, {'verified_for_supported_rules'})
        self.assertEqual({c['status'] for c in out['cases'] if c['language'] != 'python'}, {'unavailable'})

    def test_optional_backend_missing_is_not_clean(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / 'TestTotal.swift'
            source.write_text('func testTotal() { XCTAssertEqual(total(3, 5), 15) }')
            run = subprocess.run([sys.executable, str(TOOL), str(source), '--json', '--semgrep', str(Path(td)/'missing-semgrep')], capture_output=True, text=True, timeout=20)
            out = json.loads(run.stdout)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(out['complete'])
            self.assertEqual(out['inputs'][0]['status'], 'unavailable')

    def test_swift_testing_macro_is_not_claimed_supported(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / 'Test.swift'
            source.write_text('@Test func price() { #expect(total(3, 5) == 15) }')
            run = subprocess.run([sys.executable, str(TOOL), str(source), '--json', '--semgrep', str(Path(td)/'missing')], capture_output=True, text=True, timeout=20)
            out = json.loads(run.stdout)
            self.assertIn('Swift Testing #expect 未支援；僅 XCTest。', out['inputs'][0]['limitations'])
            self.assertFalse(out['complete'])

    def test_cross_language_corpus_python_cases_have_fixed_oracles(self):
        corpus = json.loads((TOOL.parent.parent / 'governance/eval/test-quality/corpus-v1.json').read_text())
        for case in corpus['cases']:
            if case['language'] == 'python':
                with self.subTest(case=case['id']):
                    rc, out = self.scan(case['source'], corpus['implementation']['source'])
                    self.assertEqual(rc, 0)
                    self.assertEqual(self.rules(out), case['expected_candidate_rules'])
        self.assertEqual({c['language'] for c in corpus['cases']},
                         {'python', 'kotlin', 'java', 'swift', 'csharp', 'javascript', 'typescript'})

    def test_missing_and_partial_inputs_are_not_clean(self):
        with tempfile.TemporaryDirectory() as td:
            good = Path(td) / 'test_good.py'
            good.write_text('def test_ok():\n    assert total(3, 5) == 15\n')
            run = subprocess.run([sys.executable, str(TOOL), str(good), str(Path(td)/'missing.py'), '--json'], capture_output=True, text=True, timeout=20)
            out = json.loads(run.stdout)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(out['complete'])
            self.assertEqual(len(out['inputs']), 2)


if __name__ == '__main__':
    unittest.main()
