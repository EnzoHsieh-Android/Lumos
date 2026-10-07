#!/usr/bin/env python3
"""Fixed historical lock test-generation trial; no verifier feedback to model."""
import argparse
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import unittest

import historical_test_quality as history
from test_quality_handbook import run_model

MODEL = 'claude-opus-5-5'
ASSERTS = {'assertTrue', 'assertFalse', 'assertEqual', 'assertGreater'}
API = '''subject.fixture(mode) 是隔離測試 context manager。mode 只用 "normal" 或 "cache-moved"。
with fixture(mode) as s: 建立獨立筆記庫、私有測試HOME；cache-moved 模擬使用者將快取目錄搬到另一個磁碟。
s.lock() 是被測歷史 _vault_write_lock 的 context manager；s.fallback_ready() 回傳主要快取路徑是否不可信；s.held() 回傳筆記庫目前是否確實有鎖；s.external_written() 回傳外部快取目錄是否寫入鎖。
鎖規格：同一程序重複取同一筆記庫鎖可重入；主要快取目錄不可信時換到筆記庫自身鎖，不能不鎖，不能寫入外部快取目錄；離開最外層後釋放鎖。
只寫 unittest.TestCase 的 test_ 方法，import unittest、from subject import fixture。
固定可執行語法：with fixture("normal"或"cache-moved") as s、with s.lock()、pass，以及 self.assertTrue/assertFalse/assertEqual/assertGreater(s.fallback_ready()/s.held()/s.external_written(), 字面值)。可省略斷言第二參數。可巢狀 with，不用迴圈/變數赋值/其他API/import/函式/例外捕捉/檔尾main。
fixture 的 s.lock() 最多等待2秒，無法進入時記錄具體取鎖失敗並拋 AssertionError；程序15秒上限只是執行器防卡，不算測試檢出。'''

LEAN_API = '''測試介面：from subject import fixture。
fixture("normal") 或 fixture("cache-moved") 提供隔離的筆記庫與家目錄設定，with fixture(...) as s 使用。
s.lock() 是鎖的 context manager；s.fallback_ready() 查主要快取路徑是否不可信；s.held() 查鎖是否存在；s.external_written() 查外部快取目錄是否有鎖寫入。
輸出 unittest.TestCase 的 test_ 方法，只 import unittest 與 from subject import fixture。
可執行語法：with fixture(...) as s、with s.lock()、pass、self.assertTrue/assertFalse/assertEqual/assertGreater 搭配以上查詢及字面值。with 可依 Python 語法組合。測試用名稱 self 與 s，不使用其他變數、迴圈、額外呼叫或匯入；可含標準 main 尾段。
fixture 有取鎖等待上限；取鎖失敗回報 AssertionError。程序逾時、語法或環境錯誤列無效。'''
LEAN_TASK = '''請為笔記修改的鎖加實際有用的測試，自行選擇情境。
需求：同一程序對同一筆記庫可重入；使用者可以搬移快取目錄，這項設定下仍須保持鎖的行為，鎖只寫在可信位置；使用完應釋放。
最後只輸出一個 python code fence。implementation.txt 是目前實作的程式投影（去除註解與文件字串）；先讀。沒有執行工具或驗證回饋。'''


def validate(code):
    tree = ast.parse(code)
    footer = ast.parse('if __name__ == "__main__":\n    unittest.main()\n').body[0]
    checked = tree
    if tree.body and ast.dump(tree.body[-1]) == ast.dump(footer):
        # This exact conventional footer is false under generated_tests module name.
        # Keep original code for execution/hash; validate the test body separately.
        checked = ast.Module(body=tree.body[:-1], type_ignores=[])
    allowed = {ast.Module, ast.Import, ast.ImportFrom, ast.alias, ast.ClassDef,
               ast.FunctionDef, ast.arguments, ast.arg, ast.With, ast.withitem,
               ast.Expr, ast.Call, ast.Attribute, ast.Name, ast.Load, ast.Store,
               ast.Constant, ast.Pass}
    if len(list(ast.walk(tree))) > 2000:
        raise ValueError('test-too-large')
    for node in ast.walk(checked):
        if type(node) not in allowed:
            raise ValueError('unsupported-node:' + type(node).__name__)
        if isinstance(node, ast.Import) and [(a.name, a.asname) for a in node.names] != [('unittest', None)]:
            raise ValueError('unsupported-import')
        if isinstance(node, ast.ImportFrom) and (node.module != 'subject' or node.level or [(a.name, a.asname) for a in node.names] != [('fixture', None)]):
            raise ValueError('unsupported-import')
        if isinstance(node, ast.FunctionDef) and (not node.name.startswith('test_') or len(node.args.args) != 1 or node.args.args[0].arg != 'self' or node.decorator_list or node.returns):
            raise ValueError('unsupported-method')
        if isinstance(node, ast.ClassDef) and (len(node.bases) != 1 or ast.unparse(node.bases[0]) != 'unittest.TestCase' or node.decorator_list or node.keywords):
            raise ValueError('unsupported-class')
        if isinstance(node, ast.Name) and node.id not in {'unittest', 'fixture', 's', 'self'}:
            raise ValueError('unsupported-name')
        if isinstance(node, ast.Attribute):
            attrs = {'self': ASSERTS, 's': {'lock', 'fallback_ready', 'held', 'external_written'}, 'unittest': {'TestCase'}}
            if not isinstance(node.value, ast.Name) or node.attr not in attrs.get(node.value.id, set()):
                raise ValueError('unsupported-attribute')
        if isinstance(node, ast.Call):
            if node.keywords:
                raise ValueError('unsupported-keywords')
            if isinstance(node.func, ast.Name) and (node.func.id != 'fixture' or len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or node.args[0].value not in {'normal', 'cache-moved'}):
                raise ValueError('unsupported-call')
            if not isinstance(node.func, (ast.Name, ast.Attribute)):
                raise ValueError('unsupported-call')
    return tree


def execute(code, source, work):
    validate(code)
    path = work / 'historical_lumos.py'
    path.write_text(source)
    spec = importlib.util.spec_from_file_location('historical_lumos', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    evidence = {'blocked_nested_fallback': False, 'assertions': 0, 'entries': []}

    class Scenario:
        def __init__(self, home, vault, external):
            self.home, self.vault, self.external = home, vault, external
            self.depth = 0

        def fallback_ready(self):
            return not module._trusted_private_dir(self.home / '.cache/lumos/vault-lock', '.cache', 'lumos', 'vault-lock')

        def held(self):
            return any(self.vault.glob('*.lock')) or any((self.home / '.cache/lumos/vault-lock').glob('*.lock'))

        def external_written(self):
            return any(self.external.rglob('*.lock'))

        @contextlib.contextmanager
        def lock(self):
            depth, fallback = self.depth, self.fallback_ready()
            def expired(*unused):
                raise TimeoutError('lock-enter-incomplete')
            previous = signal.signal(signal.SIGALRM, expired)
            signal.alarm(2)
            cm = module._vault_write_lock(self.vault)
            try:
                try:
                    cm.__enter__()
                except TimeoutError:
                    evidence['blocked_nested_fallback'] |= depth > 0 and fallback
                    evidence['entries'].append({'depth': depth, 'fallback': fallback, 'completed': False})
                    raise AssertionError('lock-enter-incomplete') from None
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous)
            evidence['entries'].append({'depth': depth, 'fallback': fallback, 'completed': True})
            self.depth += 1
            try:
                yield
            finally:
                self.depth -= 1
                cm.__exit__(None, None, None)

    @contextlib.contextmanager
    def fixture(mode):
        with tempfile.TemporaryDirectory(dir=work) as directory:
            base = Path(directory)
            home, vault, external = (base / name for name in ('home', 'vault', 'external'))
            for p in (home, vault, external, home / '.cache'):
                p.mkdir()
            if mode == 'cache-moved':
                (home / '.cache/lumos').symlink_to(external)
            else:
                (home / '.cache/lumos/vault-lock').mkdir(parents=True, mode=0o700)
            previous = os.environ['HOME']
            os.environ['HOME'] = str(home)
            try:
                yield Scenario(home, vault, external)
            finally:
                os.environ['HOME'] = previous

    class Counted(unittest.TestCase):
        pass
    for name in ASSERTS:
        def counted(self, *args, _name=name):
            evidence['assertions'] += 1
            return getattr(unittest.TestCase, _name)(self, *args)
        setattr(Counted, name, counted)
    proxy = type('UnittestAPI', (), {'TestCase': Counted})
    def importer(name, *unused):
        if name == 'unittest':
            return proxy
        if name == 'subject':
            return type('SubjectAPI', (), {'fixture': staticmethod(fixture)})
        raise ImportError(name)
    namespace = {'__name__': 'generated_tests', '__builtins__': {'__import__': importer, '__build_class__': __build_class__}}
    exec(compile(code, '<generated-tests>', 'exec'), namespace)
    suite = unittest.TestSuite()
    for value in namespace.values():
        if isinstance(value, type) and issubclass(value, Counted) and value is not Counted:
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(value))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream).run(suite)
    return {'status': 'executed', 'tests_run': result.testsRun, 'passed': result.wasSuccessful(),
            'failures': [text for _, text in result.failures], 'errors': [text for _, text in result.errors],
            'output': stream.getvalue(), 'evidence': evidence}


def grade(code):
    scores = {}
    for key, commit in history.VERSIONS.items():
        source = history.historical_file(commit, 'scripts/lumos')
        with tempfile.TemporaryDirectory(prefix='history-grade-') as directory:
            work = Path(directory)
            (work / 'home').mkdir()
            try:
                proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child'],
                                      input=json.dumps({'code': code, 'source': source}), capture_output=True,
                                      text=True, cwd=work, env={'HOME': str(work / 'home'), 'PATH': os.defpath, 'TMPDIR': str(work)}, timeout=15)
                scores[key] = json.loads(proc.stdout) if proc.returncode == 0 else {'status': 'invalid', 'stderr': proc.stderr}
            except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                scores[key] = {'status': 'invalid', 'reason': type(exc).__name__}
    baseline, fault = scores['fixed'], scores['faulty']
    valid = all(s.get('status') == 'executed' and s.get('tests_run', 0) > 0 and s['evidence']['assertions'] > 0 and not s['errors'] for s in scores.values()) and baseline.get('passed', False)
    detected = valid and bool(fault['failures']) and fault['evidence']['blocked_nested_fallback'] and any('AssertionError: lock-enter-incomplete' in f for f in fault['failures'])
    return {'status': 'detected' if detected else ('survived' if valid and fault['passed'] else 'invalid'), 'versions': scores, 'test_sha256': history.sha(code)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--prompt-profile', choices=['explicit', 'lean'], default='explicit')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.child:
        try:
            data = json.load(sys.stdin)
            result = execute(data['code'], data['source'], Path.cwd())
        except Exception as exc:
            result = {'status': 'invalid', 'reason': type(exc).__name__ + ':' + str(exc)}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if not args.out or not (args.controls or args.run):
        parser.error('Use --controls or --run with --out NEW_DIRECTORY')
    args.out.mkdir(parents=True, exist_ok=False)
    if args.controls:
        head = 'import unittest\nfrom subject import fixture\nclass LockTests(unittest.TestCase):\n    def test_lock(self):\n        with fixture("cache-moved") as s:\n            self.assertTrue(s.fallback_ready())\n'
        weak = head + '            with s.lock():\n                self.assertTrue(s.held())\n            with s.lock():\n                self.assertTrue(s.held())\n'
        strong = head + '            with s.lock():\n                with s.lock():\n                    self.assertTrue(s.held())\n'
        normal = head.replace('"cache-moved"', '"normal"').replace('assertTrue(s.fallback_ready())', 'assertFalse(s.fallback_ready())') + '            with s.lock():\n                self.assertTrue(s.held())\n            self.assertFalse(s.held())\n'
        cases = {'weak': weak, 'strong': strong, 'empty': 'import unittest\n', 'bad-baseline': head + '            self.assertFalse(s.fallback_ready())\n', 'unsupported': 'import os\n', 'normal': normal,
                 'canonical-footer': strong + '\nif __name__ == "__main__":\n    unittest.main()\n',
                 'noncanonical-footer': strong + '\nif True:\n    unittest.main()\n'}
        scores = {name: grade(code) for name, code in cases.items()}
        expected = {'weak': 'survived', 'strong': 'detected', 'empty': 'invalid', 'bad-baseline': 'invalid', 'unsupported': 'invalid', 'normal': 'survived', 'canonical-footer': 'detected', 'noncanonical-footer': 'invalid'}
        result = {'runner_sha256': history.sha(Path(__file__).read_text()), 'cases': cases, 'scores': scores}
        (args.out / 'controls.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        passed = all(scores[k]['status'] == v for k, v in expected.items())
        print('controls_passed=' + str(passed))
        return 0 if passed else 2
    command_doc = (history.REPO / 'skills/lumos-project-notes/commands/03-寫回圖譜.md').read_text()
    handbook = command_doc.split('**測試必須有獨立的判準')[1].split('## ')[0]
    handbook = '**測試必須有獨立的判準' + handbook
    source = history.historical_file(history.VERSIONS['faulty'], 'scripts/lumos')
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == '_vault_write_lock')
    visible = ast.get_source_segment(source, node)
    api = API
    prompt = API + '\n請為此內部鎖合約補實際有用的測試。最後只輸出一個 python code fence，不要其他文字。\n實作片段在 implementation.txt；先讀。沒有執行工具或驗證回饋。'
    if args.prompt_profile == 'lean':
        for function in ast.walk(node):
            if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) and function.body and isinstance(function.body[0], ast.Expr) and isinstance(function.body[0].value, ast.Constant) and isinstance(function.body[0].value.value, str):
                function.body = function.body[1:]
        visible = ast.unparse(node)
        api = LEAN_API
        prompt = api + '\n' + LEAN_TASK
    manifest = {'model': MODEL, 'repeats': 2, 'prompt_profile': args.prompt_profile, 'api': api, 'prompt': prompt, 'handbook': handbook,
                'visible_source': visible, 'visible_source_sha256': history.sha(visible), 'versions': history.VERSIONS,
                'runner_sha256': history.sha(Path(__file__).read_text()), 'primary': 'only submission before any verifier feedback'}
    (args.out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    rows = []
    for repeat in range(2):
        for arm in (['control', 'handbook'] if repeat == 0 else ['handbook', 'control']):
            name = str(repeat) + '-' + arm
            with tempfile.TemporaryDirectory(prefix='history-model-') as directory:
                work = Path(directory)
                (work / 'implementation.txt').write_text(visible)
                system = '你是開發者，為既有功能寫測試。僅讀目前目錄提供的 implementation.txt。'
                if arm == 'handbook':
                    system += '\n正式測試手冊：\n' + handbook
                row, raw = run_model(work, system, prompt, MODEL, 180, False, args.out / (name + '.events.jsonl'))
                reads = [c for c in row['calls'] if c['name'] == 'Read']
                row['only_visible_material_read'] = bool(reads) and all(
                    c['name'] == 'Read' and Path(c['input'].get('file_path', '')).resolve() == (work / 'implementation.txt').resolve()
                    for c in row['calls'])
                row['valid'] = row['valid'] and row['only_visible_material_read'] and (work / 'implementation.txt').read_text() == visible
                row.update(arm=arm, repeat=repeat)
                matches = re.findall(r'```python\s*\n(.*?)```', row['answer'], re.S)
                if row['valid'] and len(matches) == 1:
                    code = matches[0]
                    row['score'] = grade(code)
                    (args.out / (name + '.tests.json')).write_text(json.dumps({'code': code, 'sha256': history.sha(code)}, ensure_ascii=False, indent=2) + '\n')
                else:
                    row['score'] = {'status': 'invalid', 'reason': 'invalid-session-or-output'}
                rows.append(row)
                (args.out / 'results.json').write_text(json.dumps({'rows': rows}, ensure_ascii=False, indent=2) + '\n')
                print(name, 'session_valid=' + str(row['valid']), 'score=' + row['score']['status'], flush=True)
    return 0 if all(r['valid'] and r['score']['status'] != 'invalid' for r in rows) else 2


if __name__ == '__main__':
    raise SystemExit(main())
