#!/usr/bin/env python3
"""跨語言固定語法考卷；未支援的規則不算通過。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
EXTS = {'python': '.py', 'kotlin': '.kt', 'java': '.java', 'swift': '.swift',
        'csharp': '.cs', 'javascript': '.js', 'typescript': '.ts'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--semgrep', help='選配固定版本的本機 Semgrep CE')
    args = parser.parse_args()
    corpus_path = ROOT/'governance/eval/test-quality/corpus-v1.json'
    corpus = json.loads(corpus_path.read_text())
    report = {'schema_version': 1, 'kind': 'corpus', 'verdict': 'not_assessed',
              'corpus_sha256': hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
              'tool': {'name': 'test-quality-corpus', 'version': '0.1', 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              'cases': [], 'complete': False}
    with tempfile.TemporaryDirectory(prefix='lumos-quality-corpus-') as td:
        root = Path(td)
        frozen_scanner = root/'test_quality_scan.py'
        frozen_scanner.write_bytes((ROOT/'scripts/test_quality_scan.py').read_bytes())
        (root/'test_quality_semgrep.py').write_bytes((ROOT/'scripts/test_quality_semgrep.py').read_bytes())
        impl = root/'pricing.py'
        impl.write_text(corpus['implementation']['source'])
        for case in corpus['cases']:
            source = root/('test_'+case['id']+EXTS[case['language']])
            # 非 Java/C# 樣本為函式片段；這兩種加 class 容器，仍不宣稱可編譯。
            text = case['source']
            if case['language'] in {'java', 'csharp'}:
                text = 'class TestPrice {\n' + text + '\n}'
            source.write_text(text)
            command = [sys.executable, str(frozen_scanner), str(source), '--json']
            if case['language'] == 'python':
                command += ['--implementation', 'pricing='+str(impl)]
            elif args.semgrep:
                command += ['--semgrep', args.semgrep]
            entry = {'case_id': case['id'], 'language': case['language'], 'status': 'unknown',
                     'manual_disposition': case['manual_disposition']}
            report['cases'].append(entry)
            try:
                run = subprocess.run(command, capture_output=True, text=True, timeout=50)
                result = json.loads(run.stdout)
                entry['evidence'] = result
                if not result['complete'] or run.returncode != 0:
                    entry['status'] = 'unavailable'
                    continue
                supported = {'same-comparison', 'mirror-expression', 'oracle-reuses-call', 'source-only'} if case['language'] == 'python' else {'same-comparison'}
                expected = set(case['expected_candidate_rules'])
                entry['unanalysed_rules'] = sorted(expected - supported)
                actual = {f['rule_id'] for f in result['findings']}
                entry['actual_rules'] = sorted(actual)
                entry['expected_supported_rules'] = sorted(expected & supported)
                entry['status'] = 'mismatch' if actual != expected & supported else ('unanalysed' if expected - supported else 'verified_for_supported_rules')
            except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError) as exc:
                entry.update(status='unavailable', reason=str(exc))
    report['complete'] = all(c['status'] == 'verified_for_supported_rules' for c in report['cases'])
    report['supported_checks_match'] = all(c['status'] in {'verified_for_supported_rules', 'unanalysed'} for c in report['cases'])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    sys.exit(main())
