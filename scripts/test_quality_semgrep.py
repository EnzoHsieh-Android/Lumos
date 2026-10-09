# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
"""選配 Semgrep CE 來源語法適配器；只用本機固定規則掃描快照。"""
import hashlib
import json
import os
from pathlib import Path
import tempfile

from test_quality import CaptureInterrupted, CaptureTimeout, run_capture_command

BACKEND_TIMEOUT = 40

PATTERNS = {
    'php': ['$this->assertSame($X, $X, ...)', '$this->assertEquals($X, $X, ...)',
            'expect($X)->toBe($X)', 'expect($X)->toEqual($X)'],
    'kotlin': ['assertEquals($X, $X, ...)'],
    'java': ['assertEquals($X, $X, ...)', 'Assertions.assertEquals($X, $X, ...)'],
    'swift': ['XCTAssertEqual($X, $X, ...)'],
    'csharp': ['Assert.Equal($X, $X)', 'Assert.AreEqual($X, $X, ...)', '$X.Should().Be($X, ...)'],
    'javascript': ['expect($X).toBe($X)', 'expect($X).toEqual($X)', 'assert.equal($X, $X, ...)', 'assert.strictEqual($X, $X, ...)'],
    'typescript': ['expect($X).toBe($X)', 'expect($X).toEqual($X)', 'assert.equal($X, $X, ...)', 'assert.strictEqual($X, $X, ...)'],
}


def backend_findings(result, source, path, raw):
    findings = []
    source_lines = raw.decode('utf-8').splitlines()
    for item in result['results']:
        if not isinstance(item, dict) or not isinstance(item.get('start'), dict):
            raise ValueError('invalid finding shape')
        rule = item.get('check_id')
        if not isinstance(rule, str):
            raise ValueError('invalid finding rule')
        if rule.split('.')[-1] != 'same-comparison' or item.get('path') != str(source):
            raise ValueError('unexpected finding rule or snapshot')
        line = item['start']['line']
        if type(line) is not int or line < 1 or line > len(source_lines):
            raise ValueError('invalid finding location')
        findings.append({'rule_id': 'same-comparison', 'status': 'candidate', 'path': str(path),
                         'line': line, 'test': 'unknown', 'oracle_source': 'unknown',
                         'reason': '斷言兩側是相同語法表達式',
                         'verification': '確認斷言的測試目的與獨立答案；穩定性測試可能合理。',
                         'snippet': source_lines[line-1][:1200]})
    return findings


def scan(path, language, executable):
    entry = {'path': str(path), 'language': language, 'adapter': 'semgrep-ce',
             'supported_rules': ['same-comparison'], 'test_identity': 'unverified', 'interfaces': PATTERNS[language],
             'limitations': ['只辨識列出的斷言介面自比；未分析判準同源、重抄算法或執行情境。'] + (['Swift Testing #expect 未支援；僅 XCTest。'] if language == 'swift' else [])}
    findings = []
    try:
        with path.open('rb') as stream:
            raw = stream.read(10 * 1024 * 1024 + 1)
        if len(raw) > 10 * 1024 * 1024:
            raise ValueError('input exceeds 10 MiB limit')
        entry['sha256'] = hashlib.sha256(raw).hexdigest()
        config = {'rules': [{'id': 'same-comparison', 'languages': [language], 'severity': 'INFO',
                            'message': 'same assertion operands; review purpose and independent oracle',
                            'pattern-either': [{'pattern': p} for p in PATTERNS[language]]}]}
        entry['rules_sha256'] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        # 本機自訂規則與來源快照；不載入來源專案的 config／ignore／登入設定。
        env = {k: v for k, v in os.environ.items() if not k.startswith('SEMGREP_')}
        with tempfile.TemporaryDirectory(prefix='lumos-static-') as temp:
            root = Path(temp)
            source = root / ('test_snapshot' + path.suffix)
            source.write_bytes(raw)
            rules = root / 'rules.json'
            rules.write_text(json.dumps(config), encoding='utf-8')
            env.update(SEMGREP_SEND_METRICS='off', SEMGREP_SETTINGS_FILE=str(root/'settings.yml'))
            command = [executable, 'scan', '--config', str(rules), '--json', '--quiet',
                       '--metrics', 'off', '--disable-version-check', '--no-git-ignore',
                       '--oss-only', '--strict', '--timeout', '5', str(source)]
            returncode, stdout, _ = run_capture_command(command, BACKEND_TIMEOUT, cwd=root, env=env)
            result = json.loads(stdout.decode('utf-8'))
            if not isinstance(result, dict) or not isinstance(result.get('results'), list) or not isinstance(result.get('errors'), list):
                raise ValueError('invalid Semgrep report shape')
            entry['backend_version'] = result.get('version', 'unknown')
            entry['backend_errors'] = result['errors']
            paths = result.get('paths')
            if not isinstance(paths, dict) or not isinstance(paths.get('scanned'), list):
                raise ValueError('missing scanned snapshot evidence')
            scanned = paths['scanned']
            if returncode != 0 or result['errors'] or str(source) not in scanned:
                entry.update(status='error', reason='backend errors, nonzero result or snapshot not scanned', returncode=returncode)
                return entry, findings
            findings.extend(backend_findings(result, source, path, raw))
            entry['status'] = 'scanned'
    except CaptureInterrupted:
        raise
    except CaptureTimeout:
        entry.update(status='timeout', reason='backend timed out')
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, IndexError) as exc:
        entry.update(status='unavailable', reason=str(exc))
    return entry, findings
