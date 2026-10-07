#!/usr/bin/env python3
"""Replay one pinned historical weak-test case, never model-generated code."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
VERSIONS = {
    'faulty': '2b4cb7ce22a49a07f215f2e1762b352c9e54415d',
    'fixed': '810beb93dbe4329a8ac0c340c5985d38bdff011a',
}
METHOD = 't_vault_lock_falls_back_instead_of_giving_up'
TARGET = '★同一個程序真巢狀拿同一把鎖不會卡死自己★(退路換了位置,可重入的鍵要跟著換)'


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def historical_file(commit, path):
    return subprocess.run(['git', 'show', commit + ':' + path], cwd=REPO,
                          capture_output=True, text=True, check=True, timeout=20).stdout


def test_function(source):
    matches = [n for n in ast.parse(source).body
               if isinstance(n, ast.FunctionDef) and n.name == METHOD]
    if len(matches) != 1:
        raise ValueError('historical-test-not-unique')
    return ast.get_source_segment(source, matches[0]) + '\n'


def replay(source, test):
    # Historical test is trusted repository code. These paths are isolated fixtures,
    # not a sandbox suitable for arbitrary model output.
    with tempfile.TemporaryDirectory(prefix='lumos-history-') as directory:
        work = Path(directory)
        (work / 'lumos.py').write_text(source)
        (work / 'home').mkdir()
        harness = '''import importlib.util,json,sys,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('historical_lumos','lumos.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def _lm(): return m
def mkvault(): return Path(tempfile.mkdtemp(prefix='vault-',dir='.'))
checks=[]
def check(label,condition,detail):
    checks.append({'label':label,'passed':bool(condition),'detail':str(detail)})
'''
        harness += test + '\n' + METHOD + '()\nprint("RESULT_JSON="+json.dumps(checks,ensure_ascii=False))\n'
        (work / 'replay.py').write_text(harness)
        env = {'PATH': os.defpath, 'HOME': str(work / 'home'),
               'TMPDIR': str(work), 'PYTHONDONTWRITEBYTECODE': '1'}
        try:
            result = subprocess.run([sys.executable, 'replay.py'], cwd=work, env=env,
                                    capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            return {'status': 'invalid', 'reason': 'child-timeout'}
        raw = {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
        lines = [line.removeprefix('RESULT_JSON=') for line in result.stdout.splitlines()
                 if line.startswith('RESULT_JSON=')]
        if result.returncode or len(lines) != 1:
            return dict(raw, status='invalid', reason='child-error-or-missing-result')
        checks = json.loads(lines[0])
        if not checks or not checks[0]['label'].startswith('★前置★') or not checks[0]['passed']:
            return dict(raw, checks=checks, status='invalid', reason='fixture-not-established')
        return dict(raw, checks=checks, status='executed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='New output directory')
    args = parser.parse_args()
    if os.name != 'posix' or not hasattr(__import__('signal'), 'SIGALRM'):
        parser.error('This historical case requires POSIX symlinks and SIGALRM')
    args.out.mkdir(parents=True, exist_ok=False)
    sources = {key: historical_file(commit, 'scripts/lumos') for key, commit in VERSIONS.items()}
    files = {key: historical_file(commit, 'scripts/test_lumos.py') for key, commit in VERSIONS.items()}
    original = {key: test_function(value) for key, value in files.items()}
    assert original['fixed'].count('_sig.alarm(8)') == 1
    tests = {'weak': original['faulty'], 'strong': original['fixed'].replace('_sig.alarm(8)', '_sig.alarm(2)', 1)}
    rows = []
    for version, source in sources.items():
        for kind, test in tests.items():
            row = replay(source, test)
            row.update(version=version, test_kind=kind, source_sha256=sha(source), test_sha256=sha(test))
            rows.append(row)
    valid = all(row['status'] == 'executed' for row in rows)
    for row in rows:
        failed = [check for check in row.get('checks', []) if not check['passed']]
        labels = [check['label'] for check in row.get('checks', [])]
        required_target = TARGET if row['test_kind'] == 'strong' else '同一個程序巢狀拿同一把鎖不會卡死自己'
        valid = valid and len(labels) == 4 and required_target in labels
        expected_red = row['version'] == 'faulty' and row['test_kind'] == 'strong'
        valid = valid and (len(failed) == 1 and failed[0]['label'] == TARGET and
                          '巢狀拿同一把鎖卡住了' in failed[0]['detail'] if expected_red else not failed)
    report = {
        'case': 'fallback-lock-reentrancy', 'preflight_passed': bool(valid),
        'versions': VERSIONS, 'runner_sha256': sha(Path(__file__).read_text()),
        'historical_file_sha256': {k: {'scripts/lumos': sha(sources[k]), 'scripts/test_lumos.py': sha(files[k])} for k in VERSIONS},
        'original_test_sha256': {k: sha(v) for k, v in original.items()},
        'instrument': 'Only strong test alarm shortened from 8 to 2 seconds; production unchanged; child deadline 15 seconds',
        'rows': rows,
    }
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.out / 'test-materials.json').write_text(json.dumps({'original': original, 'executed': tests}, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'preflight_passed': bool(valid), 'report': str(args.out / 'report.json')}))
    return 0 if valid else 2


if __name__ == '__main__':
    raise SystemExit(main())
