#!/usr/bin/env python3
"""固定測試品質考卷的故障驗證；只執行 repo 內已知考卷，不接受任意命令。

不跑外部服務、不修改正式輸入。stdout 是證據 JSON；rc 0=預定結果皆成立，2=未成立。
"""
import hashlib
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / 'scripts/test_quality_scan.py'
TESTS = ROOT / 'scripts/test_test_quality_scan.py'
HARNESS = '''import io,json,runpy,sys,unittest
from pathlib import Path
ns=runpy.run_path(sys.argv[1])
cls=ns['ScanTests']
cls.scan.__globals__['TOOL']=Path(sys.argv[2])
suite=unittest.TestSuite([cls(sys.argv[3])])
stream=io.StringIO()
r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
print(json.dumps({'tests_run':r.testsRun,'failures':[(t.id(),s) for t,s in r.failures],'errors':[(t.id(),s) for t,s in r.errors],'passed':r.wasSuccessful(),'output':stream.getvalue()}))
'''


def digest(source):
    return hashlib.sha256(source.encode()).hexdigest()


def run(path, test):
    try:
        proc = subprocess.run([sys.executable, '-c', HARNESS, str(TESTS), str(path), test],
                              capture_output=True, text=True, timeout=30,
                              env={**os.environ, 'PYTHONPATH': str(ROOT/'scripts')})
    except subprocess.TimeoutExpired:
        return {'status': 'timeout'}
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {'status': 'unavailable', 'returncode': proc.returncode, 'stderr': proc.stderr[-2000:]}
    result['status'] = 'executed' if proc.returncode == 0 else 'unavailable'
    return result


def main():
    original = SCANNER.read_text(encoding='utf-8')
    report = {'schema_version': 1, 'kind': 'fault', 'complete': False, 'verdict': 'not_assessed',
              'tool': {'name': 'test-quality-fixed-pilot', 'version': '0.1', 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              'test_source_sha256': hashlib.sha256(TESTS.read_bytes()).hexdigest(), 'checks': []}
    cases = [
        ('disable-self-comparison', 'if key(left) == key(right):', 'if False:',
         'test_same_call_comparison_is_candidate_not_verdict'),
        ('drop-source-only-candidate', 'if seen and all(from_source for _, from_source in seen):', 'if False:',
         'test_source_only_and_mixed_behavior_are_distinct'),
    ]
    with tempfile.TemporaryDirectory(prefix='lumos-test-quality-') as temp:
        path = Path(temp) / 'scanner.py'
        (Path(temp)/'test_quality_semgrep.py').write_bytes((ROOT/'scripts/test_quality_semgrep.py').read_bytes())
        for cid, old, new, test in cases:
            check = {'case_id': cid, 'test': test, 'status': 'unknown', 'baseline': {}, 'mutant': {}, 'restored': {}}
            report['checks'].append(check)
            if original.count(old) != 1:
                check['status'] = 'invalid-mutant'
                continue
            path.write_text(original, encoding='utf-8')
            check['baseline'] = run(path, test)
            mutated = original.replace(old, new, 1)
            check['source_sha256'] = {'baseline': digest(original), 'mutant': digest(mutated), 'restored': digest(original)}
            path.write_text(mutated, encoding='utf-8')
            check['mutant'] = run(path, test)
            path.write_text(original, encoding='utf-8')
            check['restored'] = run(path, test)
            results = [check[k] for k in ('baseline', 'mutant', 'restored')]
            if any(r['status'] == 'timeout' for r in results):
                check['status'] = 'timeout'
            elif any(r['status'] != 'executed' or r['tests_run'] != 1 or r['errors'] for r in results):
                check['status'] = 'unavailable'
            elif not results[0]['passed'] or not results[2]['passed']:
                check['status'] = 'unknown'
            elif results[1]['passed']:
                check['status'] = 'survived'
            elif len(results[1]['failures']) == 1 and results[1]['failures'][0][0].endswith('.' + test):
                check['status'] = 'detected'
    report['complete'] = all(c['status'] == 'detected' for c in report['checks'])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    sys.exit(main())
