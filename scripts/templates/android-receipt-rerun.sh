#!/bin/sh
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# lumos-android-evidence 收據的重跑腳本:照 queries.sql 標頭重跑每條查詢並比對 expect。
# 全部相符回 0、比對不符回 1、收據本身寫錯回 2。單一來源在工具鏈 scripts/templates/,消費專案照抄進收據目錄。
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT="$HERE/../../.."          # 收據在 <專案>/.lumos/receipts/<run-id>/
exec python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'
import json, re, subprocess, sys, tempfile, os
here, root, tp = sys.argv[1], sys.argv[2], sys.argv[3]
man = json.load(open(f'{here}/manifest.json'))
paths = {a['id']: os.path.join(root, a['path']) for a in man['artifacts']}
text = open(f'{here}/queries.sql', encoding='utf-8').read()
qs = {}
for qid, head, sql in re.findall(r'^-- \[(Q\d+)\] (.+?)\n(.*?;)\s*$', text, re.S | re.M):
    qs[qid] = (dict(x.split('=', 1) for x in head.split()), sql)
# 不准空轉:標頭數跟解析到的條數要一樣(漏分號、標頭寫歪會少)、至少一條帶 expect、manifest 列的 Q 都要在
heads = re.findall(r'^--\s*\[(Q\d+)\]', text, re.M)
listed = {q for layer in man.get('layers', []) for q in layer.get('queries', [])}
problems = []
if len(heads) != len(qs):
    problems.append(f'queries.sql 有 {len(heads)} 個標頭、只解析到 {len(qs)} 條(標頭要寫成 -- [Qn],SQL 要以 ; 結尾)')
if not any(kv.get('expect', '-') != '-' for kv, _ in qs.values()):
    problems.append('沒有任何一條帶 expect,等於什麼都沒驗')
if listed - set(qs):
    problems.append(f'manifest 列了 queries.sql 沒有的查詢:{sorted(listed - set(qs))}')
bad_trace = sorted({kv.get('trace', '?') for kv, _ in qs.values() if kv.get('trace') not in paths})
if bad_trace:
    problems.append(f'查詢指到 manifest artifacts 裡沒有的 id:{bad_trace}')
bad_req = sorted({r for kv, _ in qs.values() for r in kv.get('requires', '-').split(',') if r != '-' and r not in qs})
if bad_req:
    problems.append(f'requires 指到不存在的查詢:{bad_req}')
if problems:
    print('擋下:收據本身寫錯——' + ';'.join(problems), file=sys.stderr)
    sys.exit(2)

def chain(qid, seen=()):
    """requires 遞移展開,前置語句在前;前置只能是 INCLUDE / CREATE 這類不回傳列的語句"""
    req = qs[qid][0].get('requires', '-')
    out = []
    for r in ([] if req == '-' else req.split(',')):
        if r not in seen:
            out += [x for x in chain(r, seen + (qid,)) if x not in out]
    return out + [qid]

fail = 0
for qid, (kv, sql) in qs.items():
    if kv.get('expect', '-') == '-':
        continue
    trace = paths[kv['trace']]
    with tempfile.NamedTemporaryFile('w', suffix='.sql', delete=False) as f:
        f.write(''.join(qs[x][1] + '\n' for x in chain(qid)))
    r = subprocess.run([tp, trace, '-q', f.name], capture_output=True, text=True)
    os.unlink(f.name)
    key, _, pairs = kv['expect'].partition(':')
    rows = [l for l in r.stdout.splitlines() if l.startswith('"')]
    hdr = [h.strip('"') for h in rows[0].split(',')] if rows else []
    row = next((x for x in rows[1:] if x.split(',')[0].strip('"') == key), None)
    ok = r.returncode == 0 and row is not None
    if ok:
        vals = dict(zip(hdr, [v.strip('"') for v in row.split(',')]))
        for p in pairs.split(','):
            k, v = p.split('=')
            try:
                ok &= round(float(vals.get(k, 'nan')), 2) == round(float(v), 2)
            except ValueError:
                ok &= vals.get(k) == v
    print(('OK  ' if ok else 'BAD ') + qid, kv['expect'], '' if r.returncode == 0 else r.stderr.strip()[-200:])
    fail += not ok
sys.exit(1 if fail else 0)
PY
