# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
"""Installed test-quality entry points. Execution receipts are evidence, not semantic verdicts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import selectors
import subprocess
import xml.etree.ElementTree as ET

LIMIT = 10 * 1024 * 1024


def read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('not a regular non-symlink file: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('file exceeds 10 MiB: ' + str(path))
    return raw


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def xml_tag(node):
    return node.tag.split('}')[-1]


def validate_suite_counts(root):
    for suite in root.iter():
        if xml_tag(suite) not in {'testsuite', 'testsuites'}:
            continue
        cases = [n for n in suite.iter() if xml_tag(n) == 'testcase']
        observed = {'tests': len(cases)}
        for field, tag in [('failures', 'failure'), ('errors', 'error'), ('skipped', 'skipped')]:
            observed[field] = sum(any(xml_tag(c) == tag for c in case) for case in cases)
        for field, count in observed.items():
            if field in suite.attrib and int(suite.get(field)) != count:
                raise ValueError('suite summary inconsistent with testcase rows: ' + field)


def terminate_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()


def read_ready_output(selector, ready, buffers):
    for key, _ in ready:
        chunk = os.read(key.fd, 65536)
        if not chunk:
            selector.unregister(key.fileobj)
            continue
        buffers[key.data].extend(chunk)
        if len(buffers[key.data]) > LIMIT:
            raise ValueError('output exceeds 10 MiB')


def run_capture_command(command, timeout):
    import time
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    previous = signal.getsignal(signal.SIGTERM)

    def interrupted(signum, frame):
        raise ValueError('execution interrupted by signal ' + str(signum))

    proc = None
    signal.signal(signal.SIGTERM, interrupted)
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(proc.stderr, selectors.EVENT_READ, 'stderr')
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ValueError('timeout; never detected')
                read_ready_output(selector, selector.select(remaining), buffers)
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise ValueError('timeout; never detected') from exc
        return proc.returncode, bytes(buffers['stdout']), bytes(buffers['stderr'])
    finally:
        signal.signal(signal.SIGTERM, previous)
        if proc is not None:
            terminate_group(proc)
            proc.stdout.close()
            proc.stderr.close()


def assertion_failure(node):
    kind = node.get('type', '')
    message = node.get('message', '')
    if re.search(r'(?:^|[.\\])(?:AssertionError|AssertionFailedError|ExpectationFailedException|ComparisonFailure|AssertFailedException)$', kind):
        return True
    if kind == 'NUnit.Framework.AssertionException':
        return True
    if re.fullmatch(r'Xunit\.Sdk\.(?:Equal|NotEqual|True|False|Null|NotNull|Throws|Contains|Empty|Single|Same)Exception', kind):
        return True
    # Measured Node reporter cause; an arbitrary message mentioning assertion
    # names is not failure attribution.
    if kind == 'testCodeFailure':
        return bool(re.search(r'cause: AssertionError \[ERR_ASSERTION\]:', ''.join(node.itertext())))
    if kind == 'failure':
        return bool(re.match(r'^Assert\.(?:Equal|NotEqual|True|False|Null|NotNull|Throws|Contains|Empty|Single|Same)\(\) Failure:', message))
    if not kind:
        # AGP instrumentation XML omits type/message; the first exception and
        # its JUnit assertion frame identify the measured failure origin.
        text = ''.join(node.itertext()).strip()
        if text.startswith('java.lang.AssertionError:') and re.search(r'\bat org\.junit\.Assert\.(?:fail|assert)\w*\(', text):
            return True
        return bool(re.match(r'^.+\.swift:\d+(?::\d+)? - XCTAssert(?:Equal|NotEqual|True|False|Nil|NotNil|ThrowsError|NoThrow|GreaterThan|LessThan) failed:', message))
    return False


class NoDtdTreeBuilder(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        raise ValueError("DTD/entity declarations not accepted")


def junit(raw):
    root = ET.fromstring(raw, parser=ET.XMLParser(target=NoDtdTreeBuilder()))
    tag = xml_tag
    if tag(root) not in {'testsuites', 'testsuite'}:
        raise ValueError('expected JUnit testsuite(s)')
    cases = []
    for node in root.iter():
        if tag(node) != 'testcase':
            continue
        name = node.get('name')
        if not name:
            raise ValueError('testcase missing name')
        cid = node.get('classname', '') + '::' + name
        failures = [n for n in node if tag(n) == 'failure']
        errors = [n for n in node if tag(n) == 'error']
        skipped = any(tag(n) == 'skipped' for n in node)
        reason = '\n'.join(n.get('type', '') + ' ' + n.get('message', '') + ' ' + ''.join(n.itertext())
                           for n in failures + errors)
        assertion = bool(failures) and all(assertion_failure(n) for n in failures)
        status = 'error' if errors else 'skipped' if skipped else 'failure' if failures else 'passed'
        cases.append({'id': cid, 'status': status, 'assertion_failure': assertion if status == 'failure' else False,
                      'reason': reason[:4000]})
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate test identities')
    if not cases:
        raise ValueError('zero testcases')
    # Suite-level errors must not disappear behind passing testcase rows.
    if any(tag(n) == 'error' for n in root.iter()) or any(int(n.get('errors', '0')) > 0 for n in root.iter() if tag(n) == 'testsuite'):
        raise ValueError('runner/suite errors')
    attached = {id(n) for case in root.iter() if tag(case) == "testcase"
                for n in case if tag(n) in {"failure", "skipped"}}
    if any(tag(n) in {"failure", "skipped"} and id(n) not in attached for n in root.iter()):
        raise ValueError("outcome outside testcase")
    validate_suite_counts(root)
    return cases


def add_parser(sub):
    p = sub.add_parser('test-quality', help='測試品質候選掃描、可信本機測試收證與三階段JUnit證據核對；不裁決業務答案')
    actions = p.add_subparsers(dest='tqcmd', required=True)
    scan = actions.add_parser('scan', help='唯讀來源掃描，零候選不是品質通過')
    try:
        from test_quality_scan import add_scan_arguments
    except ModuleNotFoundError as exc:
        if exc.name != 'test_quality_scan':
            raise
        scan.add_argument('scan_args', nargs=argparse.REMAINDER)
    else:
        add_scan_arguments(scan)
    actions.add_parser('capabilities', help='列實際接入範圍與未驗邊界')
    capture = actions.add_parser('capture', help='明示執行可信本機測試，保存JUnit與不可覆寫快照；不提供沙盒')
    capture.add_argument('--out', type=Path, required=True)
    capture.add_argument('--source', action='append', type=Path, required=True)
    capture.add_argument('--test-source', action='append', type=Path, required=True)
    capture.add_argument('--context', action='append', type=Path, default=[])
    capture.add_argument('--report', type=Path, help='命令新產生的JUnit檔案；與--junit-stdout二選一')
    capture.add_argument('--junit-stdout', action='store_true')
    capture.add_argument('--target', action='append', default=[], help='預期實際執行的JUnit classname::name；拒絕只跑到檔案包裝案例的假綠')
    capture.add_argument('--timeout', type=int, default=60)
    capture.add_argument('--language', required=True)
    capture.add_argument('--framework', required=True)
    capture.add_argument('command', nargs=argparse.REMAINDER)
    check = actions.add_parser('check', help='核對三份capture目錄；報告來源可偽造，不證明業務正確')
    check.add_argument('baseline', type=Path)
    check.add_argument('fault', type=Path)
    check.add_argument('restored', type=Path)
    check.add_argument('--target', action='append', required=True, help='JUnit classname::name，可重複')
    check.add_argument('--refactor', type=Path)
    check.add_argument('--oracle-note', help='獨立需求來源指路；只記declared，不替代人工審查')
    check.add_argument('--out', type=Path, help='新報告檔，不覆寫')


def dump(value, out=None):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if out:
        with out.open('x', encoding='utf-8') as stream:
            stream.write(text)
    print(text, end='')


def tracked_entries(args):
    entries = []
    for role, paths in [('implementation', args.source), ('tests', args.test_source), ('context', args.context)]:
        for path in paths:
            entries.append({'role': role, 'path': str(path.resolve()), 'raw': read(path)})
    if len({e['path'] for e in entries}) != len(entries):
        raise ValueError('duplicate tracked paths')
    return entries


def capture(args):
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or bool(args.report) == args.junit_stdout or not 1 <= args.timeout <= 300:
        raise ValueError('require command, exactly one JUnit source, timeout 1..300')
    if args.report and args.report.exists():
        raise ValueError('report must be new; stale report refused')
    entries = tracked_entries(args)
    args.out.mkdir(parents=True, exist_ok=False)
    receipt = {'schema_version': 1, 'kind': 'execution-receipt', 'language': args.language,
               'framework': args.framework, 'command': command, 'cwd': str(Path.cwd()),
               'status': 'invalid', 'verdict': 'not_assessed', 'snapshots': [],
               'limitations': ['明示可信本機命令，非沙盒；外部服務隔離由呼叫者負責。', '快照不自動枚舉依賴；context須明示環境/設定/lock。']}
    for i, entry in enumerate(entries):
        name = f'snapshot-{i}.txt'
        (args.out/name).write_bytes(entry['raw'])
        receipt['snapshots'].append({k: entry[k] for k in ('role', 'path')} | {'artifact': name, 'sha256': sha(entry['raw'])})
    try:
        exit_code, out, err = run_capture_command(command, args.timeout)
        (args.out/'stdout.txt').write_bytes(out)
        (args.out/'stderr.txt').write_bytes(err)
        raw = out if args.junit_stdout else read(args.report)
        (args.out/'report.xml').write_bytes(raw)
        cases = junit(raw)
        selected = {c['id']: c for c in cases}
        if len(set(args.target)) != len(args.target) or any(t not in selected or selected[t]['status'] == 'skipped' for t in args.target):
            raise ValueError('expected target missing, duplicate or skipped')
        receipt['expected_targets'] = args.target
        if any(read(Path(e['path'])) != e['raw'] for e in entries):
            raise ValueError('tracked sources changed during execution')
        passed = all(c['status'] == 'passed' for c in cases)
        if (passed and exit_code != 0) or (not passed and exit_code != 1):
            raise ValueError('exit status inconsistent with testcase results')
        receipt.update(status='executed', exit_code=exit_code, report_sha256=sha(raw), tests=cases)
    except (OSError, ValueError, ET.ParseError) as exc:
        receipt['reason'] = str(exc)
    (args.out/'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    dump(receipt)
    return 0 if receipt['status'] == 'executed' else 2


def load_receipt(folder):
    r = json.loads(read(folder/'receipt.json'))
    if r.get('schema_version') != 1 or r.get('kind') != 'execution-receipt' or r.get('status') != 'executed':
        raise ValueError('missing or invalid execution receipt')
    raw = read(folder/'report.xml')
    if sha(raw) != r.get('report_sha256'):
        raise ValueError('report hash mismatch')
    cases = junit(raw)
    if cases != r.get('tests'):
        raise ValueError('recorded test outcomes differ from raw report')
    signatures = {}
    for item in r['snapshots']:
        artifact = item['artifact']
        if Path(artifact).name != artifact:
            raise ValueError('snapshot artifact must be basename')
        if sha(read(folder/artifact)) != item['sha256']:
            raise ValueError('snapshot hash mismatch')
        key = (item['role'], item['path'])
        if key in signatures:
            raise ValueError('duplicate snapshots')
        signatures[key] = item['sha256']
    if not all(any(k[0] == role for k in signatures) for role in ('implementation', 'tests')):
        raise ValueError('missing implementation/test snapshots')
    return r, signatures, {c['id']: c for c in cases}


def validate_phases(phases, base, bs, tests):
    for name, (r, signatures, cases) in phases.items():
        if (r['language'], r['framework'], r['command'], r['cwd']) != (base['language'], base['framework'], base['command'], base['cwd']):
            raise ValueError('runtime selection or command changed across phases')
        if set(cases) != set(tests) or signatures.keys() != bs.keys():
            raise ValueError('test identities or tracked files changed')
        if any(signatures[k] != bs[k] for k in bs if k[0] != 'implementation'):
            raise ValueError('tests/context changed across phases')
        if name in {'baseline', 'restored', 'refactor'} and (r['exit_code'] != 0 or any(c['status'] != 'passed' for c in cases.values())):
            raise ValueError(name + ' not all green')
        if name == 'restored' and signatures != bs:
            raise ValueError('restoration snapshot mismatch')
        if name in {'fault', 'refactor'} and signatures == bs:
            raise ValueError(name + ' implementation did not change')


def check(args):
    result = {'kind': 'fault-evidence', 'verdict': 'not_assessed', 'fault_evidence': 'invalid',
              'oracle': {'status': 'declared' if args.oracle_note else 'unknown', 'source': args.oracle_note},
              'limitations': ['只核對收證內容一致性；報告可偽造，非執行真實性認證。',
                             '故障檢出不證明獨立判準或業務正確；context覆蓋與重構等價性另審。']}
    phases = {name: load_receipt(path) for name, path in [('baseline', args.baseline), ('fault', args.fault), ('restored', args.restored)]}
    if args.refactor:
        phases['refactor'] = load_receipt(args.refactor)
    base, bs, tests = phases['baseline']
    targets = set(args.target)
    if not targets or len(targets) != len(args.target) or not targets <= set(tests):
        raise ValueError('missing/duplicate target test identity')
    validate_phases(phases, base, bs, tests)
    r, _, cases = phases['fault']
    failed = {cid for cid, c in cases.items() if c['status'] != 'passed'}
    if not failed:
        result['fault_evidence'] = 'survived'
    elif r['exit_code'] == 1 and failed <= targets and all(cases[t]['assertion_failure'] and cases[t]['status'] == 'failure' for t in failed):
        result['fault_evidence'] = 'detected'
    else:
        raise ValueError('non-target, skipped or non-assertion failure')
    result['targets'] = sorted(targets)
    result['failed_targets'] = sorted(failed)
    result['refactor'] = 'green-reported-equivalence-unreviewed' if args.refactor else 'not-run'
    dump(result, args.out)
    return 0 if result['fault_evidence'] == 'detected' else 2


def dispatch(args):
    try:
        if args.tqcmd == 'scan':
            from test_quality_scan import main
            return main(args=args)
        if args.tqcmd == 'capture':
            return capture(args)
        if args.tqcmd == 'check':
            return check(args)
        from test_quality_semgrep import PATTERNS
        dump({'static': {'python': 'stdlib-ast', **{lang: {'backend': 'optional-semgrep', 'interfaces': patterns} for lang, patterns in PATTERNS.items()}},
              'execution': {'formats': ['JUnit XML'], 'capture': 'explicit trusted command, no sandbox',
                            'framework_qualification': 'per project; format support does not qualify frameworks'},
              'verdict': 'not_assessed'})
        return 0
    except (OSError, ValueError, TypeError, KeyError, ImportError, ET.ParseError) as exc:
        dump({'verdict': 'not_assessed', 'complete': False, 'reason': str(exc)})
        return 2
