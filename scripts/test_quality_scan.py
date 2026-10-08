#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
"""唯讀 Python 測試品質候選掃描。零候選不代表測試有用；不執行輸入。

python3 scripts/test_quality_scan.py <測試檔或目錄> --json
選填 --implementation MODULE=PATH 比對單一 return 算式。rc 0=掃描完成，2=不完整。
"""
import argparse
import ast
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tokenize
import time

VERSION = '0.1'
LANGUAGES = {'.py': 'python', '.kt': 'kotlin', '.java': 'java', '.swift': 'swift',
             '.cs': 'csharp', '.php': 'php', '.js': 'javascript', '.ts': 'typescript',
             '.jsx': 'javascript', '.tsx': 'typescript', '.mjs': 'javascript',
             '.cjs': 'javascript', '.mts': 'typescript', '.cts': 'typescript'}
EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', 'build', 'dist', 'vendor', 'storage'}
LIMIT = 10 * 1024 * 1024


def key(node):
    return ast.dump(node, include_attributes=False)


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return base + '.' + node.attr if base else ''
    return ''


def parse_file(path):
    with path.open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('input exceeds 10 MiB limit')
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    source = raw.decode(encoding)
    return source, ast.parse(source, filename=str(path)), hashlib.sha256(raw).hexdigest()


def imports(tree):
    aliases = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for item in node.names:
                aliases[item.asname or item.name.split('.')[0]] = item.name if item.asname else item.name.split('.')[0]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for item in node.names:
                aliases[item.asname or item.name] = node.module + '.' + item.name
    return aliases


def qualified(node, aliases):
    name = dotted(node)
    first, dot, rest = name.partition('.')
    return aliases.get(first, first) + (dot + rest if dot else '')


class Expand(ast.NodeTransformer):
    """只展開當前直線區塊的局部代入，不執行或求值。"""
    def __init__(self, bindings):
        self.bindings = bindings

    def visit_Name(self, node):
        return copy.deepcopy(self.bindings.get(node.id, node))


def expand(node, bindings):
    expanded = Expand(bindings).visit(copy.deepcopy(node))
    if sum(1 for _ in ast.walk(expanded)) > 4000:
        raise ValueError('local expression expansion exceeds 4000 nodes')
    return expanded


def own_nodes(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
        return
    yield node
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            yield from own_nodes(child)


def assertions(statement, check_helpers=()):
    for node in own_nodes(statement):
        if isinstance(node, ast.Assert):
            yield node, node.test
        elif isinstance(node, ast.Call) and dotted(node.func) in check_helpers and len(node.args) >= 2:
            yield node, node.args[1]
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr.startswith('assert'):
            # unittest self.assert*: 外部函式與 arbitrary assert* 不當成已知介面。
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                yield node, node


def pairs(expr):
    if isinstance(expr, ast.Compare) and len(expr.ops) == 1 and isinstance(expr.ops[0], ast.Eq):
        return expr.left, expr.comparators[0]
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr in {'assertEqual', 'assertAlmostEqual'} and len(expr.args) >= 2:
        return expr.args[0], expr.args[1]
    return None


def source_based(node, aliases):
    return any(isinstance(item, ast.Call) and qualified(item.func, aliases) == 'inspect.getsource'
               for item in ast.walk(node))


def mirror(call, expected, models, aliases):
    if not isinstance(call, ast.Call) or not isinstance(expected, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)):
        return False
    model = models.get(qualified(call.func, aliases))
    if model is None or any(isinstance(arg, ast.Starred) for arg in call.args) or any(k.arg is None for k in call.keywords):
        return False
    params, body = model
    bound = dict(zip(params, call.args))
    if len(call.args) > len(params):
        return False
    for item in call.keywords:
        if item.arg not in params or item.arg in bound:
            return False
        bound[item.arg] = item.value
    return set(bound) == set(params) and key(expand(body, bound)) == key(expected)


def comparison_rule(expr, models, aliases):
    pair = pairs(expr)
    if not pair:
        return None
    left, right = pair
    if key(left) == key(right):
        return 'same-comparison'
    containers = {'set', 'list', 'tuple', 'dict', 'str', 'int', 'float', 'bool', 'len', 'sorted', 'frozenset'}
    if isinstance(left, ast.Call) and isinstance(right, ast.Call) and qualified(left.func, aliases) == qualified(right.func, aliases) and qualified(left.func, aliases) not in containers:
        return 'oracle-reuses-call'
    if mirror(left, right, models, aliases) or mirror(right, left, models, aliases):
        return 'mirror-expression'
    return None


def update_bindings(statement, bindings):
    if isinstance(statement, (ast.Assign, ast.AnnAssign)):
        value = statement.value
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        resolved = expand(value, bindings) if value is not None else None
        for target in targets:
            if isinstance(target, ast.Name):
                if resolved is not None:
                    bindings[target.id] = resolved
                else:
                    bindings.pop(target.id, None)
            elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(resolved, (ast.Tuple, ast.List)) and len(target.elts) == len(resolved.elts):
                for name, item in zip(target.elts, resolved.elts):
                    if isinstance(name, ast.Name):
                        bindings[name.id] = item
            else:
                bindings.clear()
    elif not isinstance(statement, (ast.Expr, ast.Assert, ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef)):
        # 分支／迴圈／with 等不推資料流；清除直線假設，避免用舊 expected。
        bindings.clear()


def inspect_test(fn, path, aliases, models, lines, check_helpers=()):
    bindings, findings, seen = {}, [], []
    for statement in fn.body:
        for location, expr in assertions(statement, check_helpers):
            current = expand(expr, bindings)
            seen.append((location, source_based(current, aliases)))
            rule = comparison_rule(current, models, aliases)
            if rule:
                findings.append(finding(rule, fn.name, path, location, lines))
        update_bindings(statement, bindings)
    if seen and all(from_source for _, from_source in seen):
        findings.append(finding('source-only', fn.name, path, seen[0][0], lines))
    return findings


REASONS = {
    'same-comparison': ('斷言兩側是相同語法表達式', '確認是否只驗穩定性；另找能區分錯誤輸出的獨立答案。'),
    'oracle-reuses-call': ('斷言兩側呼叫同一函式，可能共用被測算法', '確認是否為合法關係測試或可信參考；用相關故障驗證抓錯能力。'),
    'mirror-expression': ('expected 與明確提供的單一 return 算式相同', '改用需求例子或可信獨立參考；同算法不等於業務正確。'),
    'source-only': ('已辨識的斷言都依賴 inspect.getsource', '確認目的是否只守結構；宣稱功能正確時補可觀察行為。'),
}


def finding(rule, test, path, node, lines):
    reason, verification = REASONS[rule]
    return {'rule_id': rule, 'status': 'candidate', 'path': str(path), 'line': node.lineno,
            'test': test, 'reason': reason, 'verification': verification,
            'oracle_source': 'unknown', 'snippet': '\n'.join(lines[node.lineno-1:node.end_lineno])[:1200]}


def discover(paths, report):
    files = set()
    for path in paths:
        if path.is_symlink():
            report['inputs'].append({'path': str(path), 'status': 'error', 'reason': 'explicit symlink not scanned'})
        elif path.is_file():
            files.add(path)
        elif path.is_dir():
            def error(exc):
                report['inputs'].append({'path': str(exc.filename), 'status': 'error', 'reason': str(exc)})
            for directory, dirs, names in os.walk(path, followlinks=False, onerror=error):
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(directory)/d).is_symlink())
                for name in sorted(names):
                    p = Path(directory) / name
                    if p.suffix in LANGUAGES and 'test' in str(p.relative_to(path)).lower():
                        if p.is_symlink():
                            report['inputs'].append({'path': str(p), 'status': 'error', 'reason': 'symlink not scanned'})
                        else:
                            files.add(p)
        else:
            report['inputs'].append({'path': str(path), 'status': 'error', 'reason': 'missing or not a regular file/directory'})
    return sorted(files)


def add_scan_arguments(parser):
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--check-helper', action='append', default=[], metavar='NAME', help='明示 check(name, condition, detail) 類斷言 helper，可重複')
    parser.add_argument('--semgrep', metavar='EXECUTABLE', help='選配本機 Semgrep CE；其他語言先只辨識來源自比')
    parser.add_argument('--json', action='store_true', help='輸出共用 JSON 報告')
    parser.add_argument('--implementation', action='append', default=[], metavar='MODULE=PATH', help='Python 算式比對來源（只 parse，不 import）')
    return parser


def load_models(specs, report):
    models = {}
    errors = (OSError, UnicodeError, SyntaxError, ValueError, RecursionError, MemoryError)
    for spec in specs:
        module, sep, name = spec.partition('=')
        entry = {'module': module, 'path': name}
        report['implementations'].append(entry)
        try:
            if not sep or not module or not name or module in {x['module'] for x in report['implementations'][:-1]}:
                raise ValueError('expected unique MODULE=PATH')
            _, tree, digest = parse_file(Path(name))
            entry.update(status='parsed', sha256=digest)
            supported = []
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                    params = [arg.arg for arg in node.args.posonlyargs + node.args.args]
                    if not (node.args.vararg or node.args.kwarg or node.args.kwonlyargs or node.args.defaults or node.decorator_list):
                        body = node.body[0].value
                        if isinstance(body, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)):
                            models[module + '.' + node.name] = (params, body)
                            supported.append(node.name)
            entry['modeled_functions'] = supported
            entry['unmodeled_functions'] = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name not in supported]
        except errors as exc:
            entry.update(status='error', reason=str(exc))
    return models


def inspect_python_file(path, entry, report, models, check_helpers):
    errors = (OSError, UnicodeError, SyntaxError, ValueError, RecursionError, MemoryError)
    try:
        source, tree, digest = parse_file(path)
        tests = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(('test_', 't_')):
                tests.append(node)
            elif isinstance(node, ast.ClassDef):
                tests.extend(fn for fn in node.body if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name.startswith('test_'))
        entry.update(status='scanned' if tests else 'no_tests', sha256=digest, tests_seen=len(tests))
        aliases, lines = imports(tree), source.splitlines()
        entry['tests_with_known_assertions'] = sum(any(list(assertions(st, check_helpers)) for st in fn.body) for fn in tests)
        for fn in tests:
            report['findings'].extend(inspect_test(fn, path, aliases, models, lines, check_helpers))
    except errors as exc:
        entry.update(status='error', reason=str(exc))


def main(argv=None, *, args=None):
    from test_quality_semgrep import scan as semgrep_scan
    started = time.monotonic()
    if args is None:
        parser = add_scan_arguments(argparse.ArgumentParser(description=__doc__))
        args = parser.parse_args(argv)
    report = {'schema_version': 1, 'kind': 'static', 'tool': {'name': 'test-quality-scan', 'version': VERSION, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              'complete': True, 'verdict': 'not_assessed', 'inputs': [], 'implementations': [],
              'findings': [], 'limitations': ['Python assert／unittest self.assert*／明示 check helper；局部直線代入，非跨函式資料流。',
                  '不能證明業務判準、情境成立或測試抓錯能力；非 Python 適配器只含選配來源自比規則。',
                  '目錄模式只選路徑含 test 的已知語言檔，排除 ' + ', '.join(sorted(EXCLUDED))]}
    report['tool']['adapter_source_sha256'] = hashlib.sha256(Path(__file__).with_name('test_quality_semgrep.py').read_bytes()).hexdigest()
    report['assertion_helpers'] = args.check_helper
    models = load_models(args.implementation, report)
    files = discover(args.paths, report)
    for path in files:
        language = LANGUAGES.get(path.suffix, 'unknown')
        entry = {'path': str(path), 'language': language}
        report['inputs'].append(entry)
        if language != 'python':
            if args.semgrep and language != 'unknown':
                backend_entry, found = semgrep_scan(path, language, str(Path(args.semgrep).resolve()) if '/' in args.semgrep else args.semgrep)
                entry.update(backend_entry)
                report['findings'].extend(found)
            else:
                entry.update(status='unsupported', reason='optional Semgrep adapter not enabled')
            continue
        inspect_python_file(path, entry, report, models, args.check_helper)
    if not report['inputs']:
        report['inputs'].append({'path': ', '.join(str(p) for p in args.paths), 'status': 'no_tests', 'reason': 'no test candidates discovered'})
    report['complete'] = bool(report['inputs']) and all(i['status'] == 'scanned' for i in report['inputs']) and all(i['status'] == 'parsed' for i in report['implementations'])
    report['summary'] = {'files_scanned': sum(i['status'] == 'scanned' for i in report['inputs']),
                         'tests_seen': sum(i.get('tests_seen', 0) for i in report['inputs']),
                         'candidates': len(report['findings'])}
    report['elapsed_seconds'] = round(time.monotonic() - started, 6)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print('掃描完成' if report['complete'] else '掃描不完整')
        print('候選不是裁決；零候選不代表測試有用。')
        for item in report['inputs']:
            print(f"{item['status']}: {item['path']}")
        for item in report['findings']:
            print(f"{item['path']}:{item['line']} {item['test']} [{item['rule_id']}] {item['reason']}")
            print('  ' + item['verification'])
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    sys.exit(main())
