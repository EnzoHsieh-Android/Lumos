# 可逆性(Check R)+ 治理事件帳 實作計畫

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development(建議)或 superpowers:executing-plans。Steps 用 checkbox 追蹤。

**Goal:** 在 lumos 加「可逆性」軸(★CHECKPOINT★/★IRREVERSIBLE★ + [rollback:] + doctor Check R + lint)與唯讀治理查詢 `lumos gov`。

**Architecture:** 可逆性走**平行函式**(`extract_reversibility`),完全不碰 `extract_contracts` 管線。`[rollback:decisions]` 解析=本節點 `decisions[]` 有非空 `rollback`(`parse_decisions` 已支援任意鍵,無需改)。`lumos gov` 是**唯讀彙整器**讀 3 個本機 jsonl,不改既有 hook 寫入路徑;governance-log 由 `doctor --ci` 單一寫者產生。

**Tech Stack:** python3 stdlib only(對齊 `scripts/lumos`);測試用 `scripts/test_lumos.py` 的 subprocess harness(`mkvault`/`write`/`run`/`check`,**非 pytest**)。

## Global Constraints
- 零第三方依賴(stdlib only)。
- 測試風格:subprocess-only,`run(vault, *args, expect_rc=)` + `check(name, cond, detail)`;新增 `t_*` 函式自動被收集。
- 既有測試全綠(回歸,目前 130)。
- 可逆性標記**僅限 `type: system`**。
- `[rollback:]` v1 唯一形式 `[rollback:decisions]`;天花板:證「有寫」≠「能用」。
- doctor governance-log 寫入**只在 `--ci`**、非 git / 取不到 HEAD 則跳過。
- 完整設計見 `docs/design/2026-06-19-reversibility-and-governance-ledger.md`。

---

### Task 1: 可逆性解析 + `lumos lint` Check R

**Files:**
- Modify: `scripts/lumos`(`INVARIANT_RE` 區附近加 regex/函式;`cmd_lint` 加檢查)
- Test: `scripts/test_lumos.py`(新增 `t_reversibility_lint`)

**Interfaces:**
- Produces: `CHECKPOINT_RE`, `IRREVERSIBLE_RE`, `ROLLBACK_REF_RE`, `reversibility_rollback_ref(text)->str|None`, `extract_reversibility(note)->list[(marker,clean,ref)]`, `_rollback_resolved(note,ref)->bool`(Task 2 共用)

- [ ] **Step 1: 寫失敗測試** — 加到 `scripts/test_lumos.py`:

```python
def t_reversibility_lint():
    v = mkvault()
    # irreversible 無 rollback → error rc1
    write(v, "Systems/Mig.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑 schema 遷移", body="# M\n")
    r = run(v, "lint", "Systems/Mig")
    check("lint: ★IRREVERSIBLE★ 缺回退 → rc1", r.returncode == 1 and "缺實質回退" in r.stdout, r.stdout)
    # irreversible + [rollback:decisions] 但 decisions 無 rollback → 仍 rc1
    write(v, "Systems/Mig2.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 用樂觀鎖\n    decided: 2026-06-19\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移 [rollback:decisions]", body="# M2\n")
    r = run(v, "lint", "Systems/Mig2")
    check("lint: [rollback:] 指到無實質 rollback → rc1", r.returncode == 1, r.stdout)
    # irreversible + decisions 有非空 rollback → rc0
    write(v, "Systems/Mig3.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 用樂觀鎖\n    decided: 2026-06-19\n    rollback: 跑 revert_v4.sql\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移 [rollback:decisions]", body="# M3\n")
    r = run(v, "lint", "Systems/Mig3")
    check("lint: irreversible 有實質回退 → rc0", r.returncode == 0, r.stdout)
    # checkpoint 缺回退 → warning 不擋(rc0)
    write(v, "Systems/Cp.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★CHECKPOINT★ 部署 lab2", body="# C\n")
    r = run(v, "lint", "Systems/Cp")
    check("lint: ★CHECKPOINT★ 缺回退 → warning rc0", r.returncode == 0 and "建議補回退" in r.stdout, r.stdout)
    # 標記在非 Systems → error
    write(v, "Issues/Bad.md",
          "type: issue\nstatus: open\nsummary: |-\n  KEY:★IRREVERSIBLE★ 標錯地方", body="# B\n")
    r = run(v, "lint", "Issues/Bad")
    check("lint: 可逆性標記在非 Systems → rc1", r.returncode == 1 and "只能在 Systems" in r.stdout, r.stdout)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -A1 reversibility`
Expected: FAIL(lint 還沒有可逆性檢查,irreversible 那條不會 rc1)

- [ ] **Step 3: 加 regex 與解析函式** — 在 `scripts/lumos` 的 `AUDIT_REF_RE`/`INV_TAG_RE` 定義之後加:

```python
# 可逆性軸(獨立於 ★INVARIANT★ 合約軸;走平行函式,不碰 extract_contracts/INV_TAG_RE)
CHECKPOINT_RE = re.compile(r"^KEY:\s*(?:\([^)]*\)\s*)?★CHECKPOINT★\s*(.*)")
IRREVERSIBLE_RE = re.compile(r"^KEY:\s*(?:\([^)]*\)\s*)?★IRREVERSIBLE★\s*(.*)")
ROLLBACK_REF_RE = re.compile(r"\[rollback:\s*([^\]]+)\]")


def reversibility_rollback_ref(text):
    m = ROLLBACK_REF_RE.search(text)
    return m.group(1).strip() if m else None


def extract_reversibility(note):
    """從 summary KEY 行抽 (marker, 去 [rollback:] 的乾淨文字, rollback_ref)。"""
    summ = note.fields.get("summary")
    out = []
    if isinstance(summ, str):
        for raw in summ.split("\n"):
            line = raw.strip()
            for marker, rx in (("★CHECKPOINT★", CHECKPOINT_RE), ("★IRREVERSIBLE★", IRREVERSIBLE_RE)):
                m = rx.match(line)
                if m:
                    body = m.group(1)
                    out.append((marker, ROLLBACK_REF_RE.sub("", body).strip(),
                                reversibility_rollback_ref(body)))
    return out


def _rollback_resolved(note, ref):
    """[rollback:decisions] 視為已解析 ⟺ 本節點 decisions[] 有 ≥1 條非空 rollback。"""
    if not ref or ref.strip().lower() != "decisions":
        return False
    return any(str(d.get("rollback", "")).strip() for d in parse_decisions(note.fm_lines))
```

- [ ] **Step 4: 接進 `cmd_lint`** — 在 `cmd_lint` 既有 `errs`/`warns` 收集尾端(`if not errs and not warns:` 之前)插入:

```python
    # Check R 單檔版:可逆性回退綁定 + 標錯型別
    for marker, clean, ref in extract_reversibility(n):
        if t != "system":
            errs.append(f"{marker} 只能在 Systems 節點(本節點 type={t!r}):{first_line(clean, 40)}")
            continue
        if not _rollback_resolved(n, ref):
            if marker == "★IRREVERSIBLE★":
                errs.append(f"{marker} 缺實質回退(行尾加 [rollback:decisions],decisions[] 要有非空 rollback):{first_line(clean, 40)}")
            else:
                warns.append(f"{marker} 建議補回退([rollback:decisions]):{first_line(clean, 40)}")
```

- [ ] **Step 5: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -E 'reversibility|passed|failed'`
Expected: 5 條 reversibility checks 全 ✓,整體 passed 數 +5

- [ ] **Step 6: Commit**

```bash
git add scripts/lumos scripts/test_lumos.py
git commit -m "feat(lint): 可逆性 Check R 單檔版 — ★CHECKPOINT★/★IRREVERSIBLE★ + [rollback:]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: doctor Check R(`ci` 參數 + `warn_soft`)

**Files:**
- Modify: `scripts/lumos`(`run_doctor` 簽名/閉包/新 section;`main` dispatch)
- Test: `scripts/test_lumos.py`(新增 `t_reversibility_doctor`)

**Interfaces:**
- Consumes: `extract_reversibility`, `_rollback_resolved`(Task 1)
- Produces: `run_doctor(env, strict, color, suggest=False, ci=False)`;function-local `gov_events`(Task 3 用)

- [ ] **Step 1: 寫失敗測試**

```python
def t_reversibility_doctor():
    v = mkvault()
    write(v, "Systems/Mig.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移", body="# M\n")
    r = run(v, "doctor", "--ci")
    check("doctor Check R: irreversible 缺回退 → rc1", r.returncode == 1 and "缺實質回退" in r.stdout, r.stdout)
    # 只有 checkpoint 缺回退 → warn_soft 不擋 rc0
    v2 = mkvault()
    write(v2, "Systems/Cp.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★CHECKPOINT★ 部署 lab2", body="# C\n")
    r2 = run(v2, "doctor", "--ci")
    check("doctor Check R: 只有 checkpoint 缺回退 → rc0(warn_soft 不計 issues)", r2.returncode == 0, r2.stdout)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -A1 reversibility_doctor`
Expected: FAIL(尚無 Check R)

- [ ] **Step 3: 改 `run_doctor` 簽名 + 加 `warn_soft`** — 簽名改為 `def run_doctor(env: Env, strict: bool, color: bool, suggest=False, ci=False):`。在 `warn` 閉包之後加:

```python
    def warn_soft(lines, head, advice=None):
        print(f"  {C['Y']}⚠{C['X']} {head}")
        for l in lines:
            print(f"      • {l}")
        if advice:
            print(f"  {C['B']}建議{C['X']}: {advice}")
        # 刻意不動 issues:軟提醒不影響 rc(R3-MAJOR-3)
```

並在 `issues = 0` 附近加 `gov_events = []`(Task 3 用)。

- [ ] **Step 4: 加 Check R section** — 在 Check T 的 `print()` 之後、最終 summary 之前插入:

```python
    section("R", "可逆性回退綁定 (★IRREVERSIBLE★ 動手前要有實質回退)")
    rev_err, rev_soft = [], []
    for rel, nnote in sorted(notes.items()):
        for marker, clean, ref in extract_reversibility(nnote):
            t_ = nnote.fields.get("type")
            if t_ != "system":
                rev_err.append(f"{rel}: {marker} 標在非 Systems(type={t_!r})")
                gov_events.append({"gate": "check-r", "kind": "blocked", "hard": True, "nodes": [nnote.stem]})
            elif not _rollback_resolved(nnote, ref):
                if marker == "★IRREVERSIBLE★":
                    rev_err.append(f"{rel}: {first_line(clean, 60)}")
                    gov_events.append({"gate": "check-r", "kind": "blocked", "hard": True, "nodes": [nnote.stem]})
                else:
                    rev_soft.append(f"{rel}: {first_line(clean, 60)}")
                    gov_events.append({"gate": "check-r", "kind": "warned", "hard": False, "nodes": [nnote.stem]})
    if not rev_err and not rev_soft:
        ok("無未綁回退的可逆性標記")
    if rev_err:
        warn(rev_err, f"發現 {len(rev_err)} 條 ★IRREVERSIBLE★ 缺實質回退/標錯型別:",
             "標記行加 [rollback:decisions] 且 decisions[] 寫非空 rollback;★ 僅用於 Systems")
    if rev_soft:
        warn_soft(rev_soft, f"{len(rev_soft)} 條 ★CHECKPOINT★ 建議補回退(不擋):",
                  "加 [rollback:decisions] + decisions rollback")
    print()
```

- [ ] **Step 5: 改 `main` dispatch** — `scripts/lumos` 約 2870 行:

```python
        return run_doctor(env, strict=(args.strict or args.ci), color=color, suggest=args.suggest, ci=args.ci)
```

- [ ] **Step 6: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -E 'reversibility_doctor|passed|failed'`
Expected: 2 條 ✓;既有測試不退步

- [ ] **Step 7: Commit**

```bash
git add scripts/lumos scripts/test_lumos.py
git commit -m "feat(doctor): Check R 可逆性閘 + warn_soft(軟提醒不擋)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: governance-log 寫入(doctor --ci 單一寫者)

**Files:**
- Modify: `scripts/lumos`(加 `_append_governance_log`;`run_doctor` 結尾 `if ci:` 呼叫)
- Test: `scripts/test_lumos.py`(新增 `t_governance_log_write`)

**Interfaces:**
- Consumes: `gov_events`(Task 2)
- Produces: `<vault.parent>/.governance-log.jsonl`,schema `{ts,commit,gate,kind,hard,nodes}`

- [ ] **Step 1: 寫失敗測試**(需 git repo fixture,git rev-parse 才有 HEAD)

```python
def t_governance_log_write():
    import subprocess as sp
    root = Path(tempfile.mkdtemp(prefix="gctl-gov-"))
    vault = root / "docs" / "kg"
    for sub in ("Systems", "MOC"):
        (vault / sub).mkdir(parents=True)
    (vault / "MOC" / "i.md").write_text("---\ntype: moc\n---\n# i\n", encoding="utf-8")
    (vault / "Systems" / "Mig.md").write_text(
        "---\ntype: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 跑遷移\n---\n# M\n", encoding="utf-8")
    sp.run(["git", "init", "-q"], cwd=str(root)); sp.run(["git", "add", "-A"], cwd=str(root))
    sp.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"], cwd=str(root))
    try:
        run(vault, "doctor", "--ci")
        log = root / "docs" / ".governance-log.jsonl"
        check("gov-log: --ci 寫入 governance-log", log.exists() and "check-r" in log.read_text(), "未寫")
        # 非 --ci 不寫
        log.unlink()
        run(vault, "doctor")
        check("gov-log: 純 doctor 不寫", not log.exists(), "不該寫")
    finally:
        import shutil; shutil.rmtree(root, ignore_errors=True)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -A1 governance_log`
Expected: FAIL(尚未寫 log)

- [ ] **Step 3: 加寫入函式** — `scripts/lumos`(`run_doctor` 之前):

```python
def _append_governance_log(vault, events):
    """doctor --ci 唯一寫者:把本輪 gate findings append 到 docs/.governance-log.jsonl。
    非 git / 取不到 HEAD → 跳過(不報錯)。dedup 留給讀時(lumos gov)。"""
    if not events:
        return
    import json, datetime, subprocess
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, cwd=str(vault)).stdout.strip()
    except Exception:
        commit = ""
    if not commit:
        return
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    path = vault.parent / ".governance-log.jsonl"
    try:
        with open(path, "a", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps({"ts": ts, "commit": commit, **e}, ensure_ascii=False) + "\n")
    except OSError:
        pass
```

- [ ] **Step 4: `run_doctor` 結尾呼叫** — 在 `return 1 if strict else 0` **之前**加:

```python
    if ci:
        _append_governance_log(env.vault, gov_events)
```

- [ ] **Step 5: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -E 'governance_log|passed|failed'`
Expected: 2 條 ✓

- [ ] **Step 6: Commit**

```bash
git add scripts/lumos scripts/test_lumos.py
git commit -m "feat(doctor): --ci 寫 governance-log(單一寫者,非 git 則跳過)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: `lumos gov` 唯讀彙整查詢

**Files:**
- Modify: `scripts/lumos`(加 `cmd_gov`;subparser + dispatch)
- Test: `scripts/test_lumos.py`(新增 `t_gov_query`)

**Interfaces:**
- Consumes: `docs/.bypass-log.jsonl` / `.rot-queue.jsonl` / `.governance-log.jsonl`
- Produces: `cmd_gov(env, node=None, since_days=90)`

- [ ] **Step 1: 寫失敗測試**

```python
def t_gov_query():
    root = Path(tempfile.mkdtemp(prefix="gctl-govq-"))
    vault = root / "docs" / "kg"
    (vault / "MOC").mkdir(parents=True)
    (vault / "MOC" / "i.md").write_text("---\ntype: moc\n---\n# i\n", encoding="utf-8")
    docs = root / "docs"
    (docs / ".bypass-log.jsonl").write_text(
        '{"ts":"2026-06-18T10:00:00","commit":"abc","subject":"skip graph"}\n', encoding="utf-8")
    (docs / ".rot-queue.jsonl").write_text(
        '{"ts":"2026-06-18T11:00:00","commit":"abc12","verification":"docs/kg/Verification/Foo.md","reason":"schema 變"}\n', encoding="utf-8")
    (docs / ".governance-log.jsonl").write_text(
        '{"ts":"2026-06-19T09:00:00","commit":"def","gate":"check-r","kind":"blocked","hard":true,"nodes":["OrderSvc"]}\n', encoding="utf-8")
    try:
        r = run(vault, "gov")
        check("gov: 三來源合併", "check-r" in r.stdout and "skip graph" in r.stdout and "schema 變" in r.stdout, r.stdout)
        r = run(vault, "gov", "OrderSvc")
        check("gov <node>: 命中 governance-log 事件", "check-r" in r.stdout, r.stdout)
        r = run(vault, "gov", "Foo")
        check("gov <node>: stem 命中 rot-queue 的 Verification", "schema 變" in r.stdout, r.stdout)
    finally:
        import shutil; shutil.rmtree(root, ignore_errors=True)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -A1 gov_query`
Expected: FAIL(`gov` 未知子命令)

- [ ] **Step 3: 加 `cmd_gov`** — `scripts/lumos`:

```python
def cmd_gov(env, node=None, since_days=90):
    """唯讀彙整 bypass-log/rot-queue/governance-log → 治理事件時間軸 / 某節點被哪幾道閘攔過。
    本機開發可見性工具(非合規物)。L2 無 node、L3 以 Verification 為鍵 → 對 Systems 為部分視圖。"""
    import json, datetime
    docs = env.vault.parent
    cutoff = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()

    def stem(s):
        return Path(str(s)).stem.lower()

    rows = []

    def load(name, mapper):
        p = docs / name
        if not p.exists():
            return
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(mapper(json.loads(line)))
            except (ValueError, KeyError):
                continue

    load(".bypass-log.jsonl", lambda d: {"ts": d.get("ts", ""), "commit": d.get("commit", ""),
         "gate": "L2", "kind": "bypassed", "hard": False, "nodes": [], "detail": d.get("subject", "")})
    load(".rot-queue.jsonl", lambda d: {"ts": d.get("ts", ""), "commit": d.get("commit", ""),
         "gate": "L3", "kind": "warned", "hard": False, "nodes": [stem(d.get("verification", ""))],
         "detail": d.get("reason", "")})
    load(".governance-log.jsonl", lambda d: {"ts": d.get("ts", ""), "commit": d.get("commit", ""),
         "gate": d.get("gate", "?"), "kind": d.get("kind", "?"), "hard": bool(d.get("hard")),
         "nodes": [stem(x) for x in d.get("nodes", [])], "detail": ""})

    rows = [r for r in rows if (r["ts"][:10] or "9999") >= cutoff]
    seen, ded = set(), []
    for r in sorted(rows, key=lambda r: r["ts"]):
        k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"])
        if k in seen:
            continue
        seen.add(k)
        ded.append(r)
    if node:
        q = stem(node)
        ded = [r for r in ded if q in r["nodes"]]
    for r in ded:
        mark = "硬擋" if r["hard"] else "軟"
        print(f"{r['ts'][:10]} [{r['gate']}/{r['kind']}/{mark}] {','.join(r['nodes']) or '-'}  {r['detail'][:50]}")
    if node:
        print("\n(註:L2 繞過無 node、L3 以 Verification 為鍵;對 Systems 節點為部分視圖)")
    print(f"\n{len(ded)} 筆(近 {since_days} 天)")
    return 0
```

- [ ] **Step 4: subparser + dispatch** — subparser 區(contracts 附近):

```python
    p = sub.add_parser("gov", help="唯讀治理事件帳:時間軸 / 某節點歷來被哪幾道閘攔過")
    p.add_argument("node", nargs="?")
    p.add_argument("--since", type=int, default=90, help="近 N 天(預設 90)")
```

dispatch 區(contracts 之後):

```python
    if args.cmd == "gov":
        return cmd_gov(env, args.node, args.since)
```

- [ ] **Step 5: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -E 'gov_query|passed|failed'`
Expected: 3 條 ✓

- [ ] **Step 6: Commit**

```bash
git add scripts/lumos scripts/test_lumos.py
git commit -m "feat(gov): lumos gov 唯讀彙整治理事件帳(bypass/rot/governance-log)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: 文件四面同步 + 漂移測試

**Files:**
- Modify: `scripts/templates/graph-discipline.md`(速查補可逆性)
- Modify: `skills/lumos-project-notes/SKILL.md`(新增可逆性節 + 工具表 gov 列)
- Modify: `scripts/lumos`(`NEW_HINT["system"]` 加一行)
- Test: `scripts/test_lumos.py`(新增 `t_marker_doc_sync`)

- [ ] **Step 1: 寫失敗測試**

```python
def t_marker_doc_sync():
    import pathlib
    repo = pathlib.Path(__file__).resolve().parent.parent
    skill = repo / "skills" / "lumos-project-notes" / "SKILL.md"
    disc = repo / "scripts" / "templates" / "graph-discipline.md"
    if not skill.exists() or not disc.exists():
        check("drift: skills/template 不在(vendored)→ 跳過", True); return
    st, dt = skill.read_text(encoding="utf-8"), disc.read_text(encoding="utf-8")
    for m in ("★CHECKPOINT★", "★IRREVERSIBLE★", "[rollback:"):
        check(f"drift: {m} 在 SKILL.md", m in st, "SKILL 缺")
        check(f"drift: {m} 在 graph-discipline", m in dt, "disc 缺")
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -A1 doc_sync`
Expected: FAIL(文件尚未提及標記)

- [ ] **Step 3: 速查表加可逆性** — `scripts/templates/graph-discipline.md` 的「合約鏈」區塊後加:

```markdown
**可逆性(危險動作動手前先寫好怎麼收回)**:
- `KEY:★IRREVERSIBLE★ <收不回:上架/prod遷移> [rollback:decisions]` — **必綁**回退(decisions[] 要有非空 rollback),否則 doctor 擋。
- `KEY:★CHECKPOINT★ <改了難救:部署測試機>` — 建議補 `[rollback:decisions]`(缺=提醒不擋)。
- 未標 = 可逆。`[rollback:]` 證「有寫下 undo」≠「驗過能跑」。僅用於 Systems 節點。
```

- [ ] **Step 4: SKILL.md 加可逆性節** — 在 `[audit:]` 節之後加一節:

```markdown
### ★CHECKPOINT★ / ★IRREVERSIBLE★ → `[rollback:]` 可逆性綁定(2026-06-19;doctor Check R)

不可逆動作(上架、prod DB 遷移)動手前要寫好怎麼收回。KEY 行前綴(僅 Systems):
- `KEY:★IRREVERSIBLE★ <宣稱> [rollback:decisions]` — 必綁;`[rollback:decisions]` 需本節點 `decisions[]` 有非空 `rollback` 欄位(實際回退 SQL/補償步驟)。缺=doctor Check R **error**(--ci/pre-push 擋)。
- `KEY:★CHECKPOINT★ <宣稱>` — 改了難救;建議補 `[rollback:decisions]`,缺=warning 不擋。
- **天花板**:`[rollback:]` 證「你寫下了 undo」,**不證明它跑得動 / 與現行 schema 一致**(同 [test:]/[audit:])。別把「有寫」當「安全」。
- v1 手寫 [rollback:](無專用指令);`lumos lint`/`doctor` 把關。
```

並在工具表加一列:

```markdown
| 治理事件帳(某節點歷來被哪幾道閘攔過) | `python3 scripts/lumos gov [<筆記名>] [--since N]` — 唯讀彙整 bypass/rot/governance-log;本機可見性 |
```

- [ ] **Step 5: `NEW_HINT["system"]` 加一行** — `scripts/lumos` 的 `NEW_HINT` dict,`system` list 加:

```python
        "可逆性: 不可逆動作(prod遷移/上架)標 ★IRREVERSIBLE★ + [rollback:decisions];改了難救標 ★CHECKPOINT★",
```

- [ ] **Step 6: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -E 'doc_sync|passed|failed'`
Expected: 6 條 drift ✓

- [ ] **Step 7: Commit**

```bash
git add scripts/lumos scripts/templates/graph-discipline.md skills/lumos-project-notes/SKILL.md scripts/test_lumos.py
git commit -m "docs(reversibility): 速查/skill/new 同步可逆性標記 + 漂移測試

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: 全套回歸

**Files:** 無(僅驗證)

- [ ] **Step 1: 跑全套**

Run: `python3 scripts/test_lumos.py 2>&1 | tail -3`
Expected: `XXX passed, 0 failed`(原 130 + 本計畫新增 ~18 ≈ 148）

- [ ] **Step 2: syntax + 冒煙**

Run: `python3 -c "import ast; ast.parse(open('scripts/lumos').read()); print('OK')"` 然後手動冒煙 `lumos lint`/`doctor`/`gov` 各跑一次小 vault。
Expected: OK,三指令正常輸出。

- [ ] **Step 3: 若有失敗** → 回對應 Task 修;全綠才算完成。

---

## Self-Review
- **Spec coverage**:①標記(T1/T2)、[rollback:]解析(T1)、Check R 強制(T2)、型別限制(T1/T2)、warn_soft(T2)、governance-log 寫(T3)、gov 讀(T4)、文件四面+漂移(T5)、回歸(T6)、天花板措辭(T5 文件)。§6 callsite:只動 cmd_lint/run_doctor/main/NEW_HINT,**未碰** extract_contracts 家族 ✓。
- **Placeholder scan**:每步有實碼/實指令,無 TBD ✓。
- **Type consistency**:`extract_reversibility`→`(marker,clean,ref)`、`_rollback_resolved(note,ref)`、`run_doctor(...,ci=False)`、`cmd_gov(env,node,since_days)` 各 Task 引用一致 ✓。
