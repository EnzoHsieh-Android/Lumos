#!/usr/bin/env python3
"""Frozen synthetic handbook experiment; Claude calls are opt-in, no push or policy edits.

Only fixed unittest fixtures are executed, with an AST-restricted generated test subset.
Trigger lane simulates metadata discovery via Read, not the native Skill router.
"""
import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
MATERIAL = ROOT / 'governance/eval/test-quality'
TASKS = {
    'pricing': {
        'brief': '為 total(quantity, unit_price) 補 unittest。兩參數為非負整數；quantity >= 3 時總價乘 95% 並向下取整，其他照原價；任一負數拋 ValueError("negative")。已確認例子：total(3,101)=287，total(2,101)=202，total(0,101)=0。最近修過三件 bug：折扣消失、門檻把 3 排除、錯誤理由回傳其他文字。',
        'source': 'def total(quantity, unit_price):\n    if quantity < 0 or unit_price < 0:\n        raise ValueError("negative")\n    amount = quantity * unit_price\n    return amount * 95 // 100 if quantity >= 3 else amount\n',
        'faults': [('no-discount', 'amount * 95 // 100', 'amount'), ('threshold', 'quantity >= 3', 'quantity > 3'), ('reason', '"negative"', '"other"')],
    },
    'routing': {
        'brief': '為 route(user_id, active) 補 unittest。本題 active 只傳入 bool，user_id 只傳入非 bool 的整數或拒絕案例的字串。先驗 user_id 是非負整數（否則 ValueError("invalid-user")），再驗 active 為 True（否則 ValueError("inactive")）；合法用戶 user_id 偶數回 A、奇數回 B。已確認例子 route(2,True)=A、route(3,True)=B。最近修過三件 bug：永遠回 A、漏掉 inactive 拒絕、inactive 的錯誤理由錯。',
        'source': 'def route(user_id, active):\n    if not isinstance(user_id, int) or user_id < 0:\n        raise ValueError("invalid-user")\n    if not active:\n        raise ValueError("inactive")\n    return "A" if user_id % 2 == 0 else "B"\n',
        'faults': [('constant', '"A" if user_id % 2 == 0 else "B"', '"A"'), ('skip-guard', 'if not active:', 'if False:'), ('reason', '"inactive"', '"other"')],
    },
}
ALLOWED_ASSERTS = {'assertEqual', 'assertNotEqual', 'assertTrue', 'assertFalse', 'assertRaises', 'assertRaisesRegex', 'assertIn', 'assertIsInstance'}
ALLOWED_NODES = {ast.Module, ast.Import, ast.ImportFrom, ast.alias, ast.ClassDef, ast.FunctionDef,
                 ast.arguments, ast.arg, ast.Expr, ast.Constant, ast.Assign, ast.Name, ast.Load,
                 ast.Store, ast.Attribute, ast.Call, ast.keyword, ast.Assert, ast.Compare, ast.Eq,
                 ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.BinOp, ast.Add, ast.Sub, ast.Mult,
                 ast.FloorDiv, ast.Mod, ast.UnaryOp, ast.USub, ast.Not, ast.With, ast.withitem,
                 ast.Pass, ast.Tuple, ast.List, ast.Dict, ast.Subscript}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def validate_test(code):
    """Bounded benchmark grammar, not a general sandbox or Python quality verdict."""
    tree = ast.parse(code)
    if len(list(ast.walk(tree))) > 3000:
        raise ValueError('test-too-large')
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_NODES:
            raise ValueError('unsupported-test-node:' + type(node).__name__)
        if isinstance(node, ast.Import) and any(a.name != 'unittest' or a.asname for a in node.names):
            raise ValueError('unsupported-import')
        if isinstance(node, ast.ImportFrom) and (node.module != 'subject' or node.level or any(a.name not in {'total', 'route'} or a.asname for a in node.names)):
            raise ValueError('unsupported-import')
        if isinstance(node, ast.Name) and node.id.startswith('__'):
            raise ValueError('unsupported-dunder')
        if isinstance(node, ast.Attribute):
            permitted = ((isinstance(node.value, ast.Name) and node.value.id == 'self' and node.attr in ALLOWED_ASSERTS)
                         or (isinstance(node.value, ast.Name) and node.value.id == 'unittest' and node.attr == 'TestCase')
                         or (isinstance(node.value, ast.Name) and node.value.id == 'subject' and node.attr in {'total', 'route'})
                         or node.attr == 'exception')
            if not permitted:
                raise ValueError('unsupported-attribute:' + node.attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id not in {'total', 'route', 'str', 'ValueError'}:
            raise ValueError('unsupported-call:' + node.func.id)
    return tree


def execute_tests(code, source):
    """Called only inside a time-limited child, with restricted imports/builtins."""
    validate_test(code)
    mod = types.ModuleType('subject')
    exec(source, mod.__dict__)
    sys.modules['subject'] = mod
    def imports(name, *args, **kwargs):
        if name not in {'subject', 'unittest'}:
            raise ImportError(name)
        return mod if name == 'subject' else unittest
    namespace = {'__name__': 'generated_tests', '__builtins__': {'__import__': imports, '__build_class__': __build_class__,
                 'str': str, 'ValueError': ValueError, 'True': True, 'False': False}}
    exec(compile(code, '<generated-tests>', 'exec'), namespace)
    suite = unittest.TestSuite()
    for value in namespace.values():
        if isinstance(value, type) and issubclass(value, unittest.TestCase):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(value))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'tests_run': result.testsRun, 'passed': result.wasSuccessful(),
            'failures': [(t.id(), error) for t, error in result.failures],
            'errors': [(t.id(), error) for t, error in result.errors], 'output': stream.getvalue()}


def run_test(code, source):
    try:
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'],
                              input=json.dumps({'code': code, 'source': source}), text=True,
                              capture_output=True, timeout=15,
                              env={'PATH': os.defpath, 'PYTHONDONTWRITEBYTECODE': '1'})
        result = json.loads(proc.stdout)
        result['returncode'] = proc.returncode
        return result
    except subprocess.TimeoutExpired:
        return {'status': 'timeout'}
    except json.JSONDecodeError:
        return {'status': 'invalid', 'stderr': proc.stderr[-2000:]}


def score(task_id, code):
    task = TASKS[task_id]
    baseline = run_test(code, task['source'])
    checks = []
    for fid, old, new in task['faults']:
        mutant = run_test(code, task['source'].replace(old, new, 1))
        restored = run_test(code, task['source'])
        states = [baseline, mutant, restored]
        if any(r.get('status') != 'executed' or r.get('tests_run', 0) == 0 for r in states):
            status = 'invalid'
        elif not baseline['passed'] or not restored['passed'] or mutant['errors']:
            status = 'invalid'
        elif mutant['passed']:
            status = 'survived'
        elif mutant['failures']:
            status = 'detected'
        else:
            status = 'unknown'
        checks.append({'fault_id': fid, 'status': status, 'mutant': mutant, 'restored': restored,
                       'mutant_source_sha256': sha(task['source'].replace(old, new, 1))})
    return {'baseline': baseline, 'checks': checks, 'test_sha256': sha(code), 'source_sha256': sha(task['source'])}


def events(text):
    rows = []
    for line in text.splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def tool_calls(parsed):
    calls = []
    for row in parsed:
        message = row.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                calls.append({"name": item["name"], "input": item.get("input", {})})
    return calls


def run_model(directory, system, prompt, model, timeout, behavior, raw_path):
    tools = 'Read,Write,Bash' if behavior else 'Read'
    cmd = ['claude', '-p', prompt, '--model', model, '--effort', 'low', '--safe-mode', '--restricted',
           '--strict-mcp-config', '--setting-sources', '', '--no-session-persistence', '--permission-mode', 'dontAsk',
           '--tools', tools, '--allowedTools', 'Read', '--output-format', 'stream-json', '--verbose', '--system-prompt', system]
    if behavior:
        cmd += ['--allowedTools', 'Write', 'Bash(python3 verify.py)']
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=timeout)
        raw, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout or b''
        raw = raw.decode() if isinstance(raw, bytes) else raw
        stderr, rc = 'model-timeout', None
    raw_path.write_text(raw)
    raw_path.with_suffix(".stderr.txt").write_text(stderr)
    parsed = events(raw)
    init = next((r for r in parsed if r.get('subtype') == 'init'), {})
    result = next((r for r in reversed(parsed) if r.get('type') == 'result'), {})
    calls = tool_calls(parsed)
    valid = (rc == 0 and result.get('subtype') == 'success' and not result.get('is_error')
             and init.get('model') == model and not result.get('permission_denials'))
    return {'valid': valid, 'actual_model': init.get('model'), 'elapsed_seconds': round(time.monotonic()-start, 2),
            'returncode': rc, 'calls': calls, 'answer': result.get('result', ''),
            'cost_usd': result.get('total_cost_usd'), 'stderr': stderr}, raw


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--child', action='store_true')
    ap.add_argument('--verify', choices=TASKS)
    ap.add_argument('--run', action='store_true', help='Opt-in paid/usage-consuming fixed model calls')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--lane', choices=['all', 'behavior', 'trigger'], default='all')
    ap.add_argument('--timeout', type=int, default=180)
    args = ap.parse_args()
    if args.child:
        try:
            data = json.load(sys.stdin)
            result = execute_tests(data['code'], data['source'])
            result['status'] = 'executed'
        except Exception as exc:
            result = {'status': 'invalid', 'reason': type(exc).__name__ + ':' + str(exc)}
        print(json.dumps(result))
        return 0
    if args.verify:
        print(json.dumps(score(args.verify, Path('tests.py').read_text()), ensure_ascii=False, indent=2))
        return 0
    if not args.run or not args.out:
        ap.error('Use --run --out NEW_DIRECTORY for the frozen model experiment')
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((MATERIAL/'handbook-manifest.json').read_text())
    manifest['runner_sha256'] = sha(Path(__file__).read_text())
    manifest['tasks'] = TASKS
    docs = {arm: (MATERIAL/f'handbook-{arm}.md').read_text() for arm in manifest['arms']}
    manifest['handbook_sha256'] = {arm: sha(doc) for arm, doc in docs.items()}
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    rows = []
    jobs = [('trigger', q['id'], 0) for q in manifest['trigger_queries']]
    jobs += [('behavior', task, n) for n in range(manifest['repeats']) for task in TASKS]
    jobs = [job for job in jobs if args.lane == 'all' or job[0] == args.lane]
    manifest['selected_lane'] = args.lane
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for index, (lane, case, repeat) in enumerate(jobs):
        arms = ['baseline', 'candidate'] if index % 2 == 0 else ['candidate', 'baseline']
        for arm in arms:
            name = f'{lane}-{case}-{repeat}-{arm}'
            with tempfile.TemporaryDirectory(prefix='lumos-handbook-') as temp:
                work = Path(temp)
                (work/'SKILL.md').write_text('寫或改測試時，讀 handbook.md 再完成任務。\n')
                (work/'handbook.md').write_text(docs[arm])
                system = ('你在隔離實驗目錄工作，只處理本題。可用 Read 讀取本目錄文件。\n'
                          '可用技能：lumos-project-notes，描述：'+manifest['arms'][arm]+'\n'
                          '適用時讀 SKILL.md 載入技能。')
                if lane == 'trigger':
                    query = next(q for q in manifest['trigger_queries'] if q['id'] == case)
                    prompt = query['query']+'\n本題僅做準備：決定需要讀哪些現有文件並實際讀取，然後簡短交代下一步；若任務不需要文件則直接回答。'
                    system += '\n本題沒有實作檔案，先做準備即可。'
                else:
                    task = TASKS[case]
                    (work/'subject.py').write_text(task['source'])
                    wrapper = 'import subprocess,sys\nsubprocess.run([sys.executable,'+repr(str(Path(__file__).resolve()))+',"--verify",'+repr(case)+'],check=True)\n'
                    (work/'verify.py').write_text(wrapper)
                    system += '\n本題測試規範已載入如下：\n'+docs[arm]
                    prompt = task['brief']+'\n請讀 subject.py，寫 tests.py，使用 unittest.TestCase 的 test_ 方法。可用 self.assertEqual／assertNotEqual／assertTrue／assertFalse／assertRaisesRegex；import unittest 及 from subject import 函式即可，檔尾不用 main。可用 python3 verify.py 驗證已寫測試；其他命令不提供。交付測試及簡短驗證報告。'
                (args.out/(name+'.prompt.json')).write_text(json.dumps({'system':system,'prompt':prompt},ensure_ascii=False,indent=2))
                row, raw = run_model(work, system, prompt, manifest['model'], args.timeout, lane == 'behavior', args.out/(name+'.events.jsonl'))
                row.update({'id':name, 'lane':lane, 'case':case, 'arm':arm, 'repeat':repeat})
                (args.out/(name+'.events.jsonl')).write_text(raw)
                if lane == 'trigger':
                    row['positive'] = query['positive']
                    row['skill_read'] = any(c['name']=='Read' and Path(c['input'].get('file_path','')).name=='SKILL.md' for c in row['calls'])
                    row['handbook_read'] = any(c['name']=='Read' and Path(c['input'].get('file_path','')).name=='handbook.md' for c in row['calls'])
                else:
                    locked = (work/'subject.py').read_text()==task['source'] and (work/'verify.py').read_text()==wrapper
                    row['locked_material_unchanged'] = locked
                    row['valid'] = row['valid'] and locked
                    row['tests_written'] = (work/'tests.py').is_file()
                    if row['tests_written']:
                        code = (work/'tests.py').read_text()
                        (args.out/(name+'.tests.py.txt')).write_text(code)
                        row['score'] = score(case,code) if locked else {'status':'modified-fixture'}
                rows.append(row)
                (args.out/'results.json').write_text(json.dumps({'manifest_sha256':sha((args.out/'manifest.json').read_text()),'rows':rows},ensure_ascii=False,indent=2)+'\n')
                print(name, 'valid='+str(row['valid']), flush=True)
    return 0 if all(row['valid'] for row in rows) else 2


if __name__ == '__main__':
    sys.exit(main())
