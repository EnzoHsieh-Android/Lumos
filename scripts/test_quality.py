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


class CaptureTimeout(ValueError):
    """Deadline reached; keeps the partial streams for callers that archive them."""

    def __init__(self, stdout=b'', stderr=b''):
        super().__init__('timeout; never detected')
        self.stdout, self.stderr = stdout, stderr


class CaptureInterrupted(ValueError):
    """SIGTERM reached the runner; callers must stop instead of treating it as one bad input."""


def terminate_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        # macOS 對只剩殭屍 leader 的程序群回 EPERM；leader 被 reap 之前 PGID 不會被別人重用。
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


def run_capture_command(command, timeout, cwd=None, env=None):
    import time
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    previous = signal.getsignal(signal.SIGTERM)

    def interrupted(signum, frame):
        raise CaptureInterrupted('execution interrupted by signal ' + str(signum))

    proc = None
    group_stopped = False
    signal.signal(signal.SIGTERM, interrupted)
    try:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, start_new_session=True)
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(proc.stderr, selectors.EVENT_READ, 'stderr')
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise CaptureTimeout(bytes(buffers['stdout']), bytes(buffers['stderr']))
                read_ready_output(selector, selector.select(min(remaining, 0.1)), buffers)
                if proc.poll() is not None and not group_stopped:
                    terminate_group(proc)
                    group_stopped = True
        try:
            proc.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise CaptureTimeout(bytes(buffers['stdout']), bytes(buffers['stderr'])) from exc
        return proc.returncode, bytes(buffers['stdout']), bytes(buffers['stderr'])
    finally:
        signal.signal(signal.SIGTERM, previous)
        if proc is not None and not group_stopped:
            terminate_group(proc)
        if proc is not None:
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


JUNIT_MAX_DEPTH = 64


class JUnitRejected(ValueError):
    """JUnit 拒收:訊息字串照舊(既有呼叫端照樣接得到 ValueError),另帶原因代碼 code 給安全證據閘用,
    不讓呼叫端比對訊息字串(Projects/安全主張驗收閘_計劃〈讀不可信資料的上限與失敗處理〉)。"""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class NoDtdTreeBuilder(ET.TreeBuilder):
    """拒 DTD 的唯一一處:丟帶原因代碼的 JUnitRejected(仍是 ValueError、訊息照舊,既有呼叫端照樣接得到),
    安全證據閘不必比對訊息字串。_JUnitStream 委派給它。"""

    def doctype(self, name, pubid, system):
        raise JUnitRejected('report_unparseable', "DTD/entity declarations not accepted")


class ReceiptRejected(ValueError):
    """收證或三階段核對拒收:訊息照舊,另帶原因代碼。"""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class _JUnitStream:
    """XMLParser 的 target:start/end 回呼裡數深度(超過上限立刻停)、testcase 結束就濃縮成一筆並清掉元素。
    內部包一個 NoDtdTreeBuilder 建元素,拒 DTD 委派給它(只有一個拒收點)。"""

    def __init__(self):
        self.tb = NoDtdTreeBuilder()
        self.depth, self.stack = 0, []
        self.root_tag = None
        self.cases, self.missing_name = [], False
        self.any_error_elem = self.outside = False
        self.suites, self.suite_stack = [], []

    def doctype(self, name, pubid, system):
        self.tb.doctype(name, pubid, system)

    def start(self, tag_name, attrib):
        self.depth += 1
        if self.depth > JUNIT_MAX_DEPTH:
            raise JUnitRejected('report_too_deep', f'JUnit nesting exceeds {JUNIT_MAX_DEPTH} levels')
        node = self.tb.start(tag_name, attrib)
        t = xml_tag(node)
        if self.root_tag is None:
            self.root_tag = t
        if t in {'testsuite', 'testsuites'}:
            ent = (t, dict(node.attrib), {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0})
            self.suites.append(ent)
            self.suite_stack.append(ent)
        if t == 'error':
            self.any_error_elem = True
        if t in {'failure', 'skipped'} and (not self.stack or self.stack[-1] != 'testcase'):
            self.outside = True
        self.stack.append(t)
        return node

    def data(self, text):
        self.tb.data(text)

    def end(self, tag_name):
        node = self.tb.end(tag_name)
        self.depth -= 1
        t = self.stack.pop()
        if t == 'testcase':
            self.case(node)
        elif t in {'testsuite', 'testsuites'}:
            self.suite_stack.pop()
        return node

    def case(self, node):
        tag = xml_tag
        name = node.get('name')
        if not name:
            self.missing_name = True
        else:
            cid = node.get('classname', '') + '::' + name
            failures = [n for n in node if tag(n) == 'failure']
            errors = [n for n in node if tag(n) == 'error']
            skipped = any(tag(n) == 'skipped' for n in node)
            reason = '\n'.join(n.get('type', '') + ' ' + n.get('message', '') + ' ' + ''.join(n.itertext())
                               for n in failures + errors)
            assertion = bool(failures) and all(assertion_failure(n) for n in failures)
            status = 'error' if errors else 'skipped' if skipped else 'failure' if failures else 'passed'
            self.cases.append({'id': cid, 'status': status, 'assertion_failure': assertion if status == 'failure' else False,
                               'reason': reason[:4000]})
        for _t, _a, c in self.suite_stack:
            c['tests'] += 1
            c['failures'] += any(tag(n) == 'failure' for n in node)
            c['errors'] += any(tag(n) == 'error' for n in node)
            c['skipped'] += any(tag(n) == 'skipped' for n in node)
        node.clear()

    def close(self):
        return self.tb.close()


def junit(raw):
    """JUnit XML → 案例清單。邊解析邊數深度(超過 JUNIT_MAX_DEPTH 層立刻停),每個案例處理完就清掉元素,
    不先建整棵樹;拒收訊息與優先序跟整棵樹讀法相同(語法錯先丟,其餘檢查照原順序在讀完後判)。"""
    st = _JUnitStream()
    parser = ET.XMLParser(target=st)
    parser.feed(raw)
    parser.close()
    if st.root_tag not in {'testsuites', 'testsuite'}:
        raise JUnitRejected('report_malformed', 'expected JUnit testsuite(s)')
    if st.missing_name:
        raise JUnitRejected('report_malformed', 'testcase missing name')
    cases = st.cases
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise JUnitRejected('report_duplicate_identity', 'duplicate test identities')
    if not cases:
        raise JUnitRejected('zero_cases', 'zero testcases')
    # Suite-level errors must not disappear behind passing testcase rows.
    if st.any_error_elem or any(int(a.get('errors', '0')) > 0 for t, a, _c in st.suites if t == 'testsuite'):
        raise JUnitRejected('suite_error', 'runner/suite errors')
    if st.outside:
        raise JUnitRejected('report_malformed', "outcome outside testcase")
    validate_suite_counts(st.suites)
    return cases


def validate_suite_counts(suites):
    """suites=[(tag, 屬性, 實數)]:每個 testsuite(s) 宣告的計數要等於它底下案例實際的數。"""
    for _t, attrib, observed in suites:
        for field in ('tests', 'failures', 'errors', 'skipped'):
            if field in attrib and int(attrib[field]) != observed[field]:
                raise JUnitRejected('count_mismatch', 'suite summary inconsistent with testcase rows: ' + field)


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


def load_receipt_data(get):
    """一份 capture 的核對本體,只吃資料:get(檔名) → 位元組(讀不到丟 ValueError)。
    load_receipt 從磁碟讀、安全證據閘從提交樹讀,都呼叫這一支。"""
    r = json.loads(get('receipt.json'))
    if r.get('schema_version') != 1 or r.get('kind') != 'execution-receipt' or r.get('status') != 'executed':
        raise ReceiptRejected('receipt_not_executed', 'missing or invalid execution receipt')
    raw = get('report.xml')
    if sha(raw) != r.get('report_sha256'):
        raise ReceiptRejected('receipt_hash_mismatch', 'report hash mismatch')
    cases = junit(raw)
    if cases != r.get('tests'):
        raise ReceiptRejected('receipt_hash_mismatch', 'recorded test outcomes differ from raw report')
    signatures = {}
    for item in r['snapshots']:
        artifact = item['artifact']
        if Path(artifact).name != artifact:
            raise ReceiptRejected('report_malformed', 'snapshot artifact must be basename')
        if sha(get(artifact)) != item['sha256']:
            raise ReceiptRejected('receipt_hash_mismatch', 'snapshot hash mismatch')
        key = (item['role'], item['path'])
        if key in signatures:
            raise ReceiptRejected('report_malformed', 'duplicate snapshots')
        signatures[key] = item['sha256']
    if not all(any(k[0] == role for k in signatures) for role in ('implementation', 'tests')):
        raise ReceiptRejected('report_malformed', 'missing implementation/test snapshots')
    return r, signatures, {c['id']: c for c in cases}


def load_receipt(folder):
    return load_receipt_data(lambda name: read(folder/name))


def validate_phases(phases, base, bs, tests):
    for name, (r, signatures, cases) in phases.items():
        if (r['language'], r['framework'], r['command'], r['cwd']) != (base['language'], base['framework'], base['command'], base['cwd']):
            raise ReceiptRejected('report_malformed', 'runtime selection or command changed across phases')
        if set(cases) != set(tests) or signatures.keys() != bs.keys():
            raise ReceiptRejected('report_malformed', 'test identities or tracked files changed')
        if any(signatures[k] != bs[k] for k in bs if k[0] != 'implementation'):
            raise ReceiptRejected('report_malformed', 'tests/context changed across phases')
        if name in {'baseline', 'restored', 'refactor'} and (r['exit_code'] != 0 or any(c['status'] != 'passed' for c in cases.values())):
            raise ReceiptRejected('nontarget_failure', name + ' not all green')
        if name == 'restored' and signatures != bs:
            raise ReceiptRejected('receipt_hash_mismatch', 'restoration snapshot mismatch')
        if name in {'fault', 'refactor'} and signatures == bs:
            raise ReceiptRejected('report_malformed', name + ' implementation did not change')


def fault_check(phases, target, oracle_note=None):
    """三階段(或四階段)核對本體,只吃 load_receipt_data 的結果 → 結果 dict(fault_evidence 是 detected 或 survived)。
    target 是宣告的目標清單(可重複時照舊拒收)。check 與安全證據閘共用。"""
    result = {'kind': 'fault-evidence', 'verdict': 'not_assessed', 'fault_evidence': 'invalid',
              'oracle': {'status': 'declared' if oracle_note else 'unknown', 'source': oracle_note},
              'limitations': ['只核對收證內容一致性；報告可偽造，非執行真實性認證。',
                             '故障檢出不證明獨立判準或業務正確；context覆蓋與重構等價性另審。']}
    base, bs, tests = phases['baseline']
    targets = set(target)
    if not targets or len(targets) != len(target) or not targets <= set(tests):
        raise ReceiptRejected('target_missing', 'missing/duplicate target test identity')
    validate_phases(phases, base, bs, tests)
    r, _, cases = phases['fault']
    failed = {cid for cid, c in cases.items() if c['status'] != 'passed'}
    if not failed:
        result['fault_evidence'] = 'survived'
    elif r['exit_code'] == 1 and failed <= targets and all(cases[t]['assertion_failure'] and cases[t]['status'] == 'failure' for t in failed):
        result['fault_evidence'] = 'detected'
    else:
        raise ReceiptRejected('nontarget_failure' if not failed <= targets else 'nonassertion_failure',
                              'non-target, skipped or non-assertion failure')
    result['targets'] = sorted(targets)
    result['failed_targets'] = sorted(failed)
    return result


def check(args):
    phases = {name: load_receipt(path) for name, path in [('baseline', args.baseline), ('fault', args.fault), ('restored', args.restored)]}
    if args.refactor:
        phases['refactor'] = load_receipt(args.refactor)
    result = fault_check(phases, args.target, args.oracle_note)
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
