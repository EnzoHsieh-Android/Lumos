#!/usr/bin/env python3
"""Fixed trusted oracle/fault/refactor experiment. No arbitrary commands or input code."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

VARIANTS = ('correct', 'wrong-policy', 'constant-zero', 'refactor', 'restored')
PROFILES = ('independent', 'copied-correct', 'copied-wrong', 'structure', 'stability')
# Human-fixed outcomes, not calculated from the subject's formula.
EXPECTED = {
    'independent': [True, False, False, True, True],
    'copied-correct': [True, False, False, True, True],
    'copied-wrong': [False, True, False, False, False],
    'structure': [True, True, False, False, True],
    'stability': [True, True, True, True, True],
}
ORACLE = {'requirement': 'integer amount, ten percent discount; amounts divisible by 100',
          'examples': [[100, 90], [200, 180], [0, 0]],
          'provenance': 'human-authored frozen synthetic specification, not SUT-generated',
          'scope': 'only these fixed examples; not exhaustive business correctness'}
PY_HARNESS = '''import json, unittest
results = []
class Tests(unittest.TestCase):
    def test_behavior(self):
BODY
suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
r = unittest.TestResult()
suite.run(r)
print(json.dumps({'tests_run': r.testsRun, 'assertions': results,
 'failures': len(r.failures), 'errors': len(r.errors), 'passed': r.wasSuccessful()}))
'''
JS_HARNESS = '''const assert = require('node:assert/strict');
const results = [];
let failures = 0;
function check(id, actual, expected) {
 try { assert.strictEqual(actual, expected); results.push({id, passed:true}); }
 catch(e) { if (!(e instanceof assert.AssertionError)) throw e;
 failures++; results.push({id, passed:false}); }
}
BODY
console.log(JSON.stringify({tests_run:1, assertions:results, failures, errors:0, passed:failures===0}));
'''


def subject(language, variant):
    mode = 'correct' if variant == 'restored' else variant
    if language == 'python':
        bodies = {'correct': '    subtotal = amount\n    return subtotal - subtotal // 10\n',
                  'wrong-policy': '    subtotal = amount\n    return subtotal - subtotal * 12 // 100\n',
                  'constant-zero': '    return 0\n',
                  'refactor': '    return amount * 9 // 10\n'}
        return 'def price(amount):\n' + bodies[mode]
    bodies = {'correct': 'const subtotal = amount; return subtotal - Math.floor(subtotal / 10);',
              'wrong-policy': 'const subtotal = amount; return subtotal - Math.floor(subtotal * 12 / 100);',
              'constant-zero': 'return 0;', 'refactor': 'return Math.floor(amount * 9 / 10);'}
    return 'function price(amount) { ' + bodies[mode] + ' }\n'


def test_body(language, profile):
    if profile in {'independent', 'copied-correct', 'copied-wrong'}:
        pairs = [(100, '90'), (200, '180'), (0, '0')]
        if profile != 'independent':
            factor = '10' if profile == 'copied-correct' else '12'
            pairs = [(n, f'{n} - {n} * {factor} // 100' if language == 'python'
                      else f'{n} - Math.floor({n} * {factor} / 100)') for n, _ in pairs]
        expressions = [(f'amount-{n}', f'price({n})', expected) for n, expected in pairs]
    elif profile == 'structure':
        expressions = [('source-subtotal', "'subtotal' in SUBJECT" if language == 'python'
                        else "SUBJECT.includes('subtotal')", 'True' if language == 'python' else 'true')]
    else:
        expressions = [('determinism', 'price(100)', 'price(100)')]
    if language == 'node':
        return '\n'.join(f'check({json.dumps(cid)}, {actual}, {expected});'
                         for cid, actual, expected in expressions)
    # subTest preserves all assertions, including failures, without counting errors as detection.
    return '\n'.join('        with self.subTest(id=' + repr(cid) + '):\n'
                     f'            actual, expected = {actual}, {expected}\n'
                     f'            results.append({{"id": {cid!r}, "passed": actual == expected}})\n'
                     '            self.assertEqual(actual, expected)'
                     for cid, actual, expected in expressions)


def run_cell(language, executable, folder, profile, variant):
    source = subject(language, variant)
    harness = PY_HARNESS if language == 'python' else JS_HARNESS
    declaration = 'SUBJECT = ' + repr(source) + '\n' if language == 'python' else 'const SUBJECT = ' + json.dumps(source) + ';\n'
    code = source + declaration + harness.replace('BODY', test_body(language, profile))
    path = folder / (profile + '--' + variant + ('.py' if language == 'python' else '.cjs'))
    path.write_text(code, encoding='utf-8')
    started = time.monotonic()
    cell = {'profile': profile, 'variant': variant, 'source_sha256': hashlib.sha256(code.encode()).hexdigest(),
            'subject_sha256': hashlib.sha256(source.encode()).hexdigest(), 'artifact': path.name}
    try:
        proc = subprocess.run([executable, str(path)], cwd=folder, capture_output=True, text=True, timeout=10)
        cell.update(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        data = json.loads(proc.stdout)
        valid = (proc.returncode == 0 and data['tests_run'] == 1 and data['errors'] == 0
                 and len(data['assertions']) == (3 if profile.startswith(('independent', 'copied')) else 1))
        cell.update(result=data, status='executed' if valid else 'invalid')
        cell['matches_frozen_expectation'] = valid and data['passed'] == EXPECTED[profile][VARIANTS.index(variant)]
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, OSError) as exc:
        cell.update(status='invalid', reason=type(exc).__name__, matches_frozen_expectation=False)
    cell['elapsed_seconds'] = round(time.monotonic() - started, 4)
    return cell


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path, help='new output directory; existing paths refused')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    out = args.out.resolve()
    manifest = {'schema_version': 1, 'oracle': ORACLE, 'expected': EXPECTED,
                'profiles': PROFILES, 'variants': VARIANTS,
                'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'claims': 'fixed mechanism experiment, not model-effect or native framework qualification'}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    report = {'languages': {}, 'complete': True, 'model_calls': 0}
    for language, executable in [('python', sys.executable), ('node', shutil.which('node'))]:
        if not executable:
            report['languages'][language] = {'status': 'unavailable', 'cells': []}
            report['complete'] = False
            continue
        folder = out/language
        folder.mkdir()
        version = subprocess.run([executable, '--version'], capture_output=True, text=True, timeout=10)
        cells = [run_cell(language, executable, folder, profile, variant)
                 for profile in PROFILES for variant in VARIANTS]
        cycle_folder = folder/'wrong-policy-cycle'
        cycle_folder.mkdir()
        cycle = []
        for phase, variant in [('baseline', 'wrong-policy'), ('fault', 'constant-zero'), ('restored', 'wrong-policy')]:
            phase_folder = cycle_folder/phase
            phase_folder.mkdir()
            cell = run_cell(language, executable, phase_folder, 'copied-wrong', variant)
            cell['phase'] = phase
            cycle.append(cell)
        qualified = (version.returncode == 0 and all(c['matches_frozen_expectation'] for c in cells + cycle)
                     and cycle[0]['source_sha256'] == cycle[2]['source_sha256'])
        report['languages'][language] = {'status': 'synthetic-harness-verified' if qualified else 'invalid',
                                        'executable': executable, 'version': version.stdout.strip() or version.stderr.strip(),
                                        'cells': cells, 'wrong_policy_cycle': cycle}
        report['complete'] &= qualified
    (out/'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'complete': report['complete'], 'languages': {k: {'status': v['status'], 'cells': len(v['cells'])}
                                                                 for k, v in report['languages'].items()}}))
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
