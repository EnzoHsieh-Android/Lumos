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
import signal
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
ALLOWED_ASSERTS = {'assertEqual', 'assertNotEqual', 'assertTrue', 'assertFalse', 'assertRaises', 'assertRaisesRegex', 'assertIn', 'assertIsInstance', 'subTest'}
ALLOWED_NODES = {ast.Module, ast.Import, ast.ImportFrom, ast.alias, ast.ClassDef, ast.FunctionDef,
                 ast.arguments, ast.arg, ast.Expr, ast.Constant, ast.Assign, ast.Name, ast.Load,
                 ast.Store, ast.Attribute, ast.Call, ast.keyword, ast.Assert, ast.Compare, ast.Eq,
                 ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.BinOp, ast.Add, ast.Sub, ast.Mult,
                 ast.FloorDiv, ast.Mod, ast.UnaryOp, ast.USub, ast.Not, ast.With, ast.withitem,
                 ast.For, ast.Pass, ast.Tuple, ast.List, ast.Dict, ast.Subscript}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def bounded_iteration_count(node, bindings=None):
    bindings = bindings or {}
    try:
        if isinstance(node, (ast.Tuple, ast.List)):
            size = len(ast.literal_eval(node))
        elif isinstance(node, ast.Name) and isinstance(bindings.get(node.id), (tuple, list, dict)):
            size = len(bindings[node.id])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'items' and not node.args and not node.keywords and isinstance(node.func.value, ast.Name) and isinstance(bindings.get(node.func.value.id), dict):
            size = len(bindings[node.func.value.id])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'range' and not node.keywords:
            values = [ast.literal_eval(arg) for arg in node.args]
            if not 1 <= len(values) <= 3 or any(type(value) is not int for value in values):
                raise ValueError('nonliteral-range')
            size = len(range(*values))
        else:
            raise ValueError('nonliteral-loop')
    except (TypeError, SyntaxError, OverflowError) as exc:
        raise ValueError('unsupported-loop') from exc
    if size > 1000:
        raise ValueError('loop-too-large')
    return max(size, 1)


def literal_binding_scopes(tree):
    scopes = {}
    functions = [tree] + [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for function in functions:
        bindings = {}
        for statement in function.body:
            if isinstance(statement, ast.Assign):
                try:
                    value = ast.literal_eval(statement.value)
                except (ValueError, TypeError, SyntaxError):
                    value = None
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        bindings[target.id] = value
        for node in ast.walk(function):
            scopes[id(node)] = bindings
    return scopes


def validate_node_access(node, scopes):
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
                     or node.attr == 'exception'
                     or (node.attr == 'items' and isinstance(node.value, ast.Name) and isinstance(scopes[id(node)].get(node.value.id), dict)))
        if not permitted:
            raise ValueError('unsupported-attribute:' + node.attr)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id not in {'total', 'route', 'str', 'ValueError', 'range'}:
        raise ValueError('unsupported-call:' + node.func.id)


def validate_test(code):
    """Bounded benchmark grammar, not a general sandbox or Python quality verdict."""
    tree = ast.parse(code)
    if len(list(ast.walk(tree))) > 3000:
        raise ValueError('test-too-large')
    loop_budget = 1
    scopes = literal_binding_scopes(tree)
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_NODES:
            raise ValueError('unsupported-test-node:' + type(node).__name__)
        if isinstance(node, ast.For):
            loop_budget *= bounded_iteration_count(node.iter, scopes[id(node)])
            if loop_budget > 10000:
                raise ValueError('loop-budget-exceeded')
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'range':
            bounded_iteration_count(node)
        validate_node_access(node, scopes)
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
                 'str': str, 'ValueError': ValueError, 'range': range, 'True': True, 'False': False}}
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


def draft_before_verify(calls):
    draft = None
    for call in calls:
        data = call.get('input', {})
        if call['name'] == 'Bash' and data.get('command', '').strip() == 'python3 verify.py':
            break
        if call['name'] == 'Write' and Path(data.get('file_path', '')).name == 'tests.py':
            draft = data.get('content')
    return draft


def model_command(cmd, directory, timeout):
    previous = signal.getsignal(signal.SIGTERM)

    def interrupted(signum, frame):
        raise ValueError('model interrupted by signal ' + str(signum))

    signal.signal(signal.SIGTERM, interrupted)
    proc = None
    try:
        proc = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            exc.stdout, exc.stderr = proc.communicate()
            raise
        return subprocess.CompletedProcess(cmd, proc.returncode, stdout, stderr)
    finally:
        signal.signal(signal.SIGTERM, previous)
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if proc.poll() is None:
                proc.communicate()


def run_model(directory, system, prompt, model, timeout, behavior, raw_path, native=False):
    tools = 'Read,Write,Bash' if behavior else ('Read,Skill' if native else 'Read')
    cmd = ['claude', '-p', prompt, '--model', model, '--effort', 'low',
           '--strict-mcp-config', '--setting-sources', 'project' if native else '', '--no-session-persistence', '--permission-mode', 'dontAsk',
           '--tools', tools, '--allowedTools', 'Read', '--output-format', 'stream-json', '--verbose', '--system-prompt', system]
    if native:
        cmd += ['--settings', json.dumps({'disableAllHooks': True, 'disableBundledSkills': True, 'autoMemoryEnabled': False, 'skillOverrides': {'design': 'off', 'doctor': 'off', 'plugin-authoring': 'off'}}), '--allowedTools', 'Skill(lumos-project-notes)']
    else:
        cmd += ['--safe-mode', '--restricted']
    if behavior:
        cmd += ['--allowedTools', 'Write', 'Bash(python3 verify.py)']
    start = time.monotonic()
    try:
        proc = model_command(cmd, directory, timeout)
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
    advertised = init.get('skills', [])
    valid = (rc == 0 and result.get('subtype') == 'success' and not result.get('is_error')
             and init.get('model') == model and not result.get('permission_denials')
             and (not native or advertised == ['lumos-project-notes']))
    return {'valid': valid, 'advertised_skills': advertised, 'actual_model': init.get('model'), 'elapsed_seconds': round(time.monotonic()-start, 2),
            'returncode': rc, 'calls': calls, 'answer': result.get('result', ''),
            'cost_usd': result.get('total_cost_usd'), 'stderr': stderr}, raw


def child_main():
    try:
        data = json.load(sys.stdin)
        result = execute_tests(data['code'], data['source'])
        result['status'] = 'executed'
    except Exception as exc:
        result = {'status': 'invalid', 'reason': type(exc).__name__ + ':' + str(exc)}
    print(json.dumps(result))
    return 0


def selected_jobs(manifest, lane):
    jobs = [('trigger', q['id'], 0) for q in manifest['trigger_queries']]
    jobs += [('behavior', task, n) for n in range(manifest['repeats']) for task in TASKS]
    if lane == 'native-trigger':
        jobs = [('native-trigger', q['id'], 0) for q in manifest['trigger_queries']]
    else:
        jobs = [job for job in jobs if lane == 'all' or job[0] == lane]
    return jobs


def score_submission(row, lane, query, work, task, wrapper, case, out, name):
    if lane in {'trigger', 'native-trigger'}:
        row['skill_invoked'] = any(c['name'] == 'Skill' and c['input'].get('skill') == 'lumos-project-notes' for c in row['calls'])
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
            (out/(name+'.tests.json')).write_text(json.dumps({'code':code,'sha256':sha(code)},ensure_ascii=False,indent=2)+'\n')
            row['score'] = score(case,code) if locked else {'status':'modified-fixture'}
            draft = draft_before_verify(row['calls'])
            if draft is not None and locked:
                row['first_draft_score'] = score(case, draft)
                (out/(name+'.first-draft.json')).write_text(json.dumps({'code':draft,'sha256':sha(draft)},ensure_ascii=False,indent=2)+'\n')
            else:
                row['first_draft_score'] = {'status':'unavailable'}


def main():
    global TASKS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--child', action='store_true')
    ap.add_argument('--verify', choices=[*TASKS, 'shipping', 'calendar'])
    ap.add_argument('--suite', choices=['wording', 'holdout'], default='wording')
    ap.add_argument('--run', action='store_true', help='Opt-in paid/usage-consuming fixed model calls')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--lane', choices=['all', 'behavior', 'trigger', 'native-trigger'], default='all')
    ap.add_argument('--timeout', type=int, default=180)
    args = ap.parse_args()
    suite_file = MATERIAL / ('handbook-holdout.json' if args.suite == 'holdout' else 'handbook-manifest.json')
    if args.suite == 'holdout':
        TASKS = json.loads(suite_file.read_text())['tasks']
    if args.lane == 'native-trigger' and args.suite != 'holdout':
        ap.error('--lane native-trigger requires --suite holdout')
    if args.child:
        return child_main()
    if args.verify:
        print(json.dumps(score(args.verify, Path('tests.py').read_text()), ensure_ascii=False, indent=2))
        return 0
    if not args.run or not args.out:
        ap.error('Use --run --out NEW_DIRECTORY for the frozen model experiment')
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads(suite_file.read_text())
    manifest['runner_sha256'] = sha(Path(__file__).read_text())
    manifest['tasks'] = TASKS
    docs = {arm: (MATERIAL/manifest.get('handbooks', {}).get(arm, f'handbook-{arm}.md')).read_text() for arm in manifest['arms']}
    manifest['handbook_sha256'] = {arm: sha(doc) for arm, doc in docs.items()}
    (args.out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    rows = []
    jobs = selected_jobs(manifest, args.lane)
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
                description_arm = manifest.get('behavior_description_arm', arm) if lane == 'behavior' else arm
                system = ('你在隔離實驗目錄工作，只處理本題。可用 Read 讀取本目錄文件。\n'
                          '可用技能：lumos-project-notes，描述：'+manifest['arms'][description_arm]+'\n'
                          '適用時讀 SKILL.md 載入技能。')
                if lane == 'native-trigger':
                    (work/'SKILL.md').unlink()
                    (work/'handbook.md').unlink()
                    subprocess.run(['git', 'init', '--quiet'], cwd=work, check=True)
                    skill = work/'.claude/skills/lumos-project-notes'
                    skill.mkdir(parents=True)
                    skill_text = '---\nname: lumos-project-notes\ndescription: '+json.dumps(manifest['arms'][arm],ensure_ascii=False)+'\n---\n寫測試前讀本技能資料夾 handbook.md，依規格設定獨立預期值，完成請說明判準與未驗範圍。\n'
                    (skill/'SKILL.md').write_text(skill_text)
                    (skill/'handbook.md').write_text(docs['baseline'])
                    (work/'subject.py').write_text(manifest['tasks']['shipping']['source'])
                    (work/'tests.py').write_text('import unittest\nfrom subject import total\nclass Tests(unittest.TestCase):\n    def test_same(self):\n        self.assertEqual(total(2,False),total(2,False))\n')
                    (work/'README.md').write_text(manifest['tasks']['shipping']['brief'])
                    query = next(q for q in manifest['trigger_queries'] if q['id'] == case)
                    prompt = query['query']
                    system = '你在隔離臨時專案中處理使用者請求，工具僅供唯讀，直接交付可完成的內容與未驗範圍。'
                    (args.out/(name+'.skill.md')).write_text(skill_text)
                elif lane == 'trigger':
                    query = next(q for q in manifest['trigger_queries'] if q['id'] == case)
                    prompt = query['query']+'\n本題僅做準備：決定需要讀哪些現有文件並實際讀取，然後簡短交代下一步；若任務不需要文件則直接回答。'
                    system += '\n本題沒有實作檔案，先做準備即可。'
                else:
                    task = TASKS[case]
                    (work/'subject.py').write_text(task['source'])
                    wrapper = 'import subprocess,sys\nsubprocess.run([sys.executable,'+repr(str(Path(__file__).resolve()))+',"--suite",'+repr(args.suite)+',"--verify",'+repr(case)+'],check=True)\n'
                    (work/'verify.py').write_text(wrapper)
                    system += '\n本題測試規範已載入如下：\n'+docs[arm]
                    prompt = task['brief']+'\n請讀 subject.py，用 Write 工具寫及修訂 tests.py，使用 unittest.TestCase 的 test_ 方法。可用 self.assertEqual／assertNotEqual／assertTrue／assertFalse／assertRaisesRegex；import unittest 及 from subject import 函式即可，檔尾不用 main。可用 python3 verify.py 驗證已寫測試；其他命令不提供。交付測試及簡短驗證報告。'
                (args.out/(name+'.prompt.json')).write_text(json.dumps({'system':system,'prompt':prompt},ensure_ascii=False,indent=2))
                row, raw = run_model(work, system, prompt, manifest['model'], args.timeout, lane == 'behavior', args.out/(name+'.events.jsonl'), native=lane == 'native-trigger')
                row.update({'id':name, 'lane':lane, 'case':case, 'arm':arm, 'repeat':repeat})
                (args.out/(name+'.events.jsonl')).write_text(raw)
                score_submission(row, lane, query if lane != 'behavior' else None, work, task if lane == 'behavior' else None, wrapper if lane == 'behavior' else None, case, args.out, name)
                rows.append(row)
                (args.out/'results.json').write_text(json.dumps({'manifest_sha256':sha((args.out/'manifest.json').read_text()),'rows':rows},ensure_ascii=False,indent=2)+'\n')
                print(name, 'valid='+str(row['valid']), flush=True)
    return 0 if all(row['valid'] for row in rows) else 2


if __name__ == '__main__':
    sys.exit(main())
