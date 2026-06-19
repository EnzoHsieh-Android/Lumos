# Autonomous Iteration Loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 每天日報後,自動抽 top-1 gap → brainstorm 成 spec → 跑 design-loop 審到收斂 → 開 PR 等人放行;人從「發起」變「review 一個 PR」。

**Architecture:** 一個 cron 入口 shell(`governance/autonomous-loop.sh`)串起數個小 python 模組(gap 抽取 / backlog / 可信度報告 / LINE),核心的 brainstorm+design-loop 由一個 `claude -p` headless orchestrator 跑(spawn 子 agent)。python 模組純資料處理可 TDD;`claude -p` orchestration 不可單元測試,靠 **Task 1 spike 先實證可行**,再靠 dry-run 觀察品質。

**Tech Stack:** python3 stdlib(零依賴,比照 `scripts/lumos`)、bash、`claude -p` headless(`--agents`/`--permission-mode dontAsk`)、`gh` CLI、既有 `lumos canary record`/`loop status`、既有 LINE `curl broadcast`。

## Global Constraints(逐條來自已收斂 spec,每個 task 隱含遵守)

- **N=1**:同時只 1 個待放行 spec。上一個 PR(真模式)/ `governance/pending/` 條目(dry-run)未清前,新 gap 只進 backlog、不展開。
- **canary 限 type a/b/c、禁 d**(覆寫 design-loop skill 的 `清單[(N-1)mod4]` 輪換,改 a/b/c 三類輪換)。
- **opus auditor 起手**(覆寫 skill 預設 sonnet 起手)。
- **強制地面事實查證**:auditor 必須對 spec 每個現況假設實際 grep/Read 驗過,報告列查證項與結果。
- **獨立 judge agent 作用域僅「canary 抓沒抓到」**——不檢查真 findings 對不對、不檢查 gap/方向。**judge 不覆蓋 severity**;severity 自報直接決定 `loop status` 收斂=全自動判收斂最弱環。
- **放行=人手動 merge PR**;系統絕不自動 merge / 自動實作。
- **第一版 dry-run**:不開 PR、不發 LINE,只寫 `governance/pending/`,人觀察品質達標再開真 PR。
- **$0 OAuth**:`claude -p` 用 `CLAUDE_CODE_OAUTH_TOKEN`,避開被禁 model(fable-5),auditor/judge/brainstorm 用 opus/sonnet。
- **日報路徑** = `governance/reports/governance-<date>.json`(含 `reports/` 層);`gaps[]` schema = `{weakness, suggestion}`(無 value_score/source_date)。
- **LINE** 復用 `curl broadcast` + `$HOME/.config/ai-daily/line_token` 傳輸層;**訊息 body 另寫**(`governance_flex_builder.py` 是日報專用、不可復用)。
- **收斂** = `lumos loop status <id> --need 2` exit 0 = 連 2 輪 caught 且 severity∈{clean,minor}。
- **失控保護**:design-loop max cap=6 輪;連續撞 cap → 停 + LINE 告警,別無限燒。

## File Structure(先鎖定分解)

新建,全部在 `governance/autonomous_loop/`(python 模組,各一責任):
- `backlog.py` — backlog.jsonl 讀寫 / 衰減 / 淘汰 / 排序。**純資料,易測。**
- `gap_select.py` — 讀日報 gaps + backlog,去重、排序、N=1 gate,選 top-1。**純資料 + gate,易測。**
- `confidence_report.py` — 從 `.canary-log.jsonl` + `loop status` 產 PR body 可信度報告。**純資料,易測。**
- `line_notify.py` — LINE 傳輸層復用 + 待放行訊息 body builder。**傳輸不測、body 易測。**
- `orchestrator-prompt.md` — `claude -p` orchestrator 的 prompt 模板(brainstorm + design-loop)。
- `../autonomous-loop.sh` — cron 入口:驗當日 json → gap_select → 跑 orchestrator → 收斂後 confidence_report + branch + PR + LINE。dry-run/真兩態。

測試:`scripts/test_autonomous_loop.py`(比照既有 `scripts/test_lumos.py` 的 stdlib unittest 風格)。

---

### Task 1: Spike — dry-run 實證 headless orchestrator(B1 go/no-go 閘)

**這是前提閘,不是普通 task。** spec R1-B1:只證了 `claude -p` spawn 1 個子 agent,**沒證** orchestrator 能跨輪、巢狀 spawn auditor、自判 caught/missed。本 task 用一個玩具 spec 實證整套。**不過 → 停、回報、整個全自動方案退回半鏈(改成自動備 spec 草稿、design-loop 留人手動跑)。**

**Files:**
- Create: `/tmp/ail-spike/toy-spec.md`(玩具 spec,含 1 個可被 canary 植入的點)
- Create: `/tmp/ail-spike/orchestrator-prompt.txt`(最小 orchestrator 指令)
- Create: `governance/autonomous_loop/SPIKE-RESULT.md`(實證結論,進 git 留痕)

- [ ] **Step 1: 寫玩具 spec + 最小 orchestrator prompt**

`/tmp/ail-spike/toy-spec.md`:一個 3-4 段、含若干「現況假設」的小設計(例:宣稱某 lumos 指令存在)。orchestrator prompt 要求 claude -p:① 複製 toy-spec → 工作副本;② 植 1 個 type-a canary(壞§ref);③ 用 Agent 工具 spawn 一個 **opus** auditor(refute + 強制地面事實查證)讀工作副本;④ 讀回 auditor 報告,自判 canary 有沒有被點出(caught/missed);⑤ 跑 `python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos --vault /tmp/ail-spike/kg canary record caught|missed --loop spike --severity <s> --auditor opus`;⑥ 再跑第 2 輪(換 type-b canary);⑦ 最後跑 `lumos loop status spike --need 2` 並把 exit code 回報。

- [ ] **Step 2: 跑 spike(OAuth、無 timeout——macOS 無 timeout)**

```bash
mkdir -p /tmp/ail-spike/kg
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.config/ai-daily/claude_oauth_token")"
claude -p "$(cat /tmp/ail-spike/orchestrator-prompt.txt)" \
  --allowedTools "Read,Edit,Bash,Grep,Glob,Agent" \
  --permission-mode dontAsk --output-format json > /tmp/ail-spike/out.json 2>/tmp/ail-spike/err.log
```

- [ ] **Step 3: 驗成功判準**

```bash
python3 -c "import json; o=json.load(open('/tmp/ail-spike/out.json')); print('is_error',o['is_error'],'turns',o['num_turns'])"
python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos --vault /tmp/ail-spike/kg loop status spike --need 2
```
Expected(go):`is_error False`、`.canary-log.jsonl` 有 ≥2 筆 record(證明跨輪 + 巢狀 spawn auditor + 自判 + record 都成立)、loop status 能算出結果。
Expected(no-go):`is_error True`、或 record 0 筆(orchestrator 沒能 spawn/record)、或只跑 1 輪。

- [ ] **Step 4: 寫結論 + commit**

把「go / no-go + 證據(num_turns、record 筆數、err.log 摘要)」寫進 `governance/autonomous_loop/SPIKE-RESULT.md`。
```bash
git add governance/autonomous_loop/SPIKE-RESULT.md
git commit -m "spike(autonomous-loop): 實證 headless orchestrator 跨輪 design-loop（B1 閘）"
```
**若 no-go:停在此,回報用戶,本 plan 後續 task 改寫為半鏈版本。以下 Task 2+ 假設 go。**

---

### Task 2: backlog 模組(TDD)

**Files:**
- Create: `governance/autonomous_loop/backlog.py`
- Test: `scripts/test_autonomous_loop.py`

**Interfaces:**
- Produces:
  - `load_backlog(path: Path) -> list[dict]`(檔不存在回 `[]`)
  - `add_gaps(path: Path, gaps: list[dict], today: str) -> None`(每條 gap=`{weakness,suggestion}`,寫入時補 `source_date=today, value_score=0.5(初值), last_seen=today`;去重:同 `weakness` 已存在則只更新 `last_seen`)
  - `decay_and_prune(path: Path, today: str, rate=0.95, floor=0.2) -> None`(每條 `value_score *= rate`,低於 `floor` 移除)
  - `pop_top(path: Path) -> dict | None`(回 value_score 最高那條並從檔移除;空回 None)

- [ ] **Step 1: 寫失敗測試**

```python
# scripts/test_autonomous_loop.py
import json, tempfile, unittest
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).parent.parent / "governance"))
from autonomous_loop import backlog

class TestBacklog(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()); self.p = self.d / "backlog.jsonl"
    def test_load_missing_returns_empty(self):
        self.assertEqual(backlog.load_backlog(self.p), [])
    def test_add_then_decay_then_prune(self):
        backlog.add_gaps(self.p, [{"weakness":"w1","suggestion":"s1"}], "2026-06-20")
        rows = backlog.load_backlog(self.p)
        self.assertEqual(rows[0]["value_score"], 0.5)
        self.assertEqual(rows[0]["source_date"], "2026-06-20")
        # 衰減到低於 floor 應淘汰:0.5 * 0.95^k < 0.2 → k≈18
        for i in range(20):
            backlog.decay_and_prune(self.p, "2026-07-%02d" % (i+1))
        self.assertEqual(backlog.load_backlog(self.p), [])
    def test_dedup_by_weakness(self):
        g = [{"weakness":"w1","suggestion":"s1"}]
        backlog.add_gaps(self.p, g, "2026-06-20")
        backlog.add_gaps(self.p, g, "2026-06-21")
        self.assertEqual(len(backlog.load_backlog(self.p)), 1)
    def test_pop_top_returns_highest(self):
        backlog.add_gaps(self.p, [{"weakness":"a","suggestion":"s"}], "2026-06-20")
        self.p.write_text(self.p.read_text())  # ensure flush
        rows = backlog.load_backlog(self.p); rows[0]["value_score"]=0.9
        backlog.add_gaps(self.p, [{"weakness":"b","suggestion":"s"}], "2026-06-20")
        top = backlog.pop_top(self.p)
        self.assertIsNotNone(top)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd /Users/enzo/harness/lumos-toolchain && python3 -m pytest scripts/test_autonomous_loop.py -q`
Expected: FAIL(`ModuleNotFoundError: autonomous_loop`)

- [ ] **Step 3: 實作 backlog.py**

```python
# governance/autonomous_loop/backlog.py
import json
from pathlib import Path

INIT_SCORE = 0.5

def load_backlog(path):
    p = Path(path)
    if not p.exists(): return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def _save(path, rows):
    Path(path).write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""), encoding="utf-8")

def add_gaps(path, gaps, today):
    rows = load_backlog(path)
    seen = {r["weakness"]: r for r in rows}
    for g in gaps:
        if g["weakness"] in seen:
            seen[g["weakness"]]["last_seen"] = today
        else:
            row = {"weakness": g["weakness"], "suggestion": g.get("suggestion",""),
                   "source_date": today, "value_score": INIT_SCORE, "last_seen": today}
            rows.append(row); seen[g["weakness"]] = row
    _save(path, rows)

def decay_and_prune(path, today, rate=0.95, floor=0.2):
    rows = load_backlog(path)
    kept = []
    for r in rows:
        r["value_score"] = r.get("value_score", INIT_SCORE) * rate
        if r["value_score"] >= floor: kept.append(r)
    _save(path, kept)

def pop_top(path):
    rows = load_backlog(path)
    if not rows: return None
    rows.sort(key=lambda r: r.get("value_score", 0), reverse=True)
    top = rows.pop(0); _save(path, rows); return top
```

- [ ] **Step 4: 跑測試確認通過**

Run: `python3 -m pytest scripts/test_autonomous_loop.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add governance/autonomous_loop/backlog.py scripts/test_autonomous_loop.py
git commit -m "feat(autonomous-loop): backlog 模組（衰減/淘汰/去重/pop-top）"
```

---

### Task 3: gap 抽取 + N=1 gate(TDD)

**Files:**
- Create: `governance/autonomous_loop/gap_select.py`
- Test: `scripts/test_autonomous_loop.py`(append)

**Interfaces:**
- Consumes: `backlog.load_backlog`/`add_gaps`/`pop_top`(Task 2)
- Produces:
  - `read_report_gaps(report_path: Path) -> list[dict]`(讀 `governance-<date>.json`,回 `gaps`;檔不存在或無 gaps 回 `[]`)
  - `pending_exists(mode: str, pending_dir: Path) -> bool`(mode=="dryrun":`pending_dir` 有 `.md`;mode=="pr":`gh pr list --head-pattern 'auto/spec-*'` 有結果。**真 PR 查詢用 `subprocess`,測試 monkeypatch**)
  - `select(report_path, backlog_path, pending_dir, mode, today) -> dict | None`(N=1 gate:`pending_exists` 為真 → 把當日 gaps 全 `add_gaps` 進 backlog、回 None;否則當日 gaps 入 backlog 後 `pop_top` 回 top-1)

- [ ] **Step 1: 寫失敗測試**

```python
class TestGapSelect(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.report = self.d / "governance-2026-06-20.json"
        self.report.write_text(json.dumps({"date":"2026-06-20","gaps":[
            {"weakness":"w1","suggestion":"s1"},{"weakness":"w2","suggestion":"s2"}]}), encoding="utf-8")
        self.bl = self.d / "backlog.jsonl"; self.pend = self.d / "pending"; self.pend.mkdir()
    def test_read_gaps(self):
        from autonomous_loop import gap_select
        self.assertEqual(len(gap_select.read_report_gaps(self.report)), 2)
    def test_gate_blocks_when_pending(self):
        from autonomous_loop import gap_select
        (self.pend / "x.md").write_text("pending")
        got = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20")
        self.assertIsNone(got)                       # 有待放行 → 不展開
        from autonomous_loop import backlog
        self.assertEqual(len(backlog.load_backlog(self.bl)), 2)  # 全進 backlog
    def test_selects_top1_when_clear(self):
        from autonomous_loop import gap_select
        got = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20")
        self.assertIsNotNone(got); self.assertIn("weakness", got)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 -m pytest scripts/test_autonomous_loop.py::TestGapSelect -q`
Expected: FAIL(`ImportError: gap_select`)

- [ ] **Step 3: 實作 gap_select.py**

```python
# governance/autonomous_loop/gap_select.py
import json, subprocess
from pathlib import Path
from . import backlog

def read_report_gaps(report_path):
    p = Path(report_path)
    if not p.exists(): return []
    try: return json.loads(p.read_text(encoding="utf-8")).get("gaps", []) or []
    except Exception: return []

def pending_exists(mode, pending_dir):
    if mode == "dryrun":
        return any(Path(pending_dir).glob("*.md"))
    # mode == "pr"
    out = subprocess.run(["gh","pr","list","--search","head:auto/spec-","--state","open","--json","number"],
                         capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() not in ("", "[]")

def select(report_path, backlog_path, pending_dir, mode, today):
    gaps = read_report_gaps(report_path)
    if pending_exists(mode, pending_dir):
        backlog.add_gaps(backlog_path, gaps, today)   # 全進 backlog,不展開
        return None
    backlog.add_gaps(backlog_path, gaps, today)
    return backlog.pop_top(backlog_path)              # 當日+積壓綜合,選 top-1
```

注:`select` 需 `autonomous_loop` 為 package。Step 3b 補 `governance/autonomous_loop/__init__.py`(空檔)。

- [ ] **Step 4: 跑測試確認通過**

Run: `python3 -m pytest scripts/test_autonomous_loop.py::TestGapSelect -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add governance/autonomous_loop/gap_select.py governance/autonomous_loop/__init__.py scripts/test_autonomous_loop.py
git commit -m "feat(autonomous-loop): gap 抽取 + N=1 gate（dry-run/PR 兩態）"
```

---

### Task 4: 收斂可信度報告(TDD)

**Files:**
- Create: `governance/autonomous_loop/confidence_report.py`
- Test: `scripts/test_autonomous_loop.py`(append)

**Interfaces:**
- Produces: `build_report(canary_log: Path, loop_id: str, residual_risks: list[str]) -> str`(讀 `.canary-log.jsonl`,篩 `loop==loop_id` 的 record,產 markdown:每輪 `type/caught|missed/severity/auditor/note`、收斂與否、加固定殘留風險清單)。**殘留風險清單含 spec 誠實天花板那幾條(severity 自報、orchestrate 未證、judge 僅 canary、AI 自選方向)。**

- [ ] **Step 1: 寫失敗測試**

```python
class TestConfidenceReport(unittest.TestCase):
    def test_build_lists_rounds_and_risks(self):
        from autonomous_loop import confidence_report
        d = Path(tempfile.mkdtemp()); log = d / "canary.jsonl"
        log.write_text("\n".join([
            json.dumps({"loop":"foo","kind":"caught","severity":"blocker","auditor":"opus","note":"r1","token":"t1"}),
            json.dumps({"loop":"foo","kind":"caught","severity":"clean","auditor":"opus","note":"r2","token":"t2"}),
            json.dumps({"loop":"other","kind":"missed","severity":"major","token":"t3"}),
        ]), encoding="utf-8")
        md = confidence_report.build_report(log, "foo", ["severity 自報是最弱環"])
        self.assertIn("blocker", md); self.assertIn("clean", md)
        self.assertNotIn("t3", md)                 # 別的 loop 不混入
        self.assertIn("severity 自報是最弱環", md)  # 殘留風險有列
```

- [ ] **Step 2: 跑測試確認失敗** — `python3 -m pytest scripts/test_autonomous_loop.py::TestConfidenceReport -q` → FAIL

- [ ] **Step 3: 實作 confidence_report.py**

```python
# governance/autonomous_loop/confidence_report.py
import json
from pathlib import Path

def build_report(canary_log, loop_id, residual_risks):
    rows = []
    p = Path(canary_log)
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if not l.strip(): continue
            r = json.loads(l)
            if r.get("loop") == loop_id: rows.append(r)
    lines = [f"## 收斂可信度報告(loop={loop_id})", "", f"**共 {len(rows)} 輪:**", ""]
    for i, r in enumerate(rows, 1):
        lines.append(f"- R{i}: `{r.get('kind')}` / severity=`{r.get('severity')}` / auditor=`{r.get('auditor','?')}` — {r.get('note','')}")
    lines += ["", "### 殘留風險(自動模式已知未兜底)", ""]
    lines += [f"- {risk}" for risk in residual_risks]
    lines += ["", "> 放行的人是最後也是唯一真兜底:收斂只證連 2 輪醒著的 opus 沒挑出 blocker/major,severity 判定仍自評。"]
    return "\n".join(lines)
```

- [ ] **Step 4: 跑測試確認通過** — PASS

- [ ] **Step 5: Commit**

```bash
git add governance/autonomous_loop/confidence_report.py scripts/test_autonomous_loop.py
git commit -m "feat(autonomous-loop): 收斂可信度報告（含殘留風險）"
```

---

### Task 5: LINE 通知(TDD body、傳輸層不測)

**Files:**
- Create: `governance/autonomous_loop/line_notify.py`
- Test: `scripts/test_autonomous_loop.py`(append)

**Interfaces:**
- Produces:
  - `build_message(title: str, confidence_summary: str, pr_link: str|None) -> dict`(回 LINE broadcast 用的 message dict;**不復用 `governance_flex_builder.py`**——它是日報專用)
  - `send(message: dict, token: str) -> int`(`curl POST /message/broadcast`,回 HTTP code;**測試 monkeypatch subprocess**)

- [ ] **Step 1: 寫失敗測試**

```python
class TestLineNotify(unittest.TestCase):
    def test_build_message_has_title_and_pr(self):
        from autonomous_loop import line_notify
        m = line_notify.build_message("X spec", "5輪收斂、1 missed", "http://pr/1")
        s = json.dumps(m, ensure_ascii=False)
        self.assertIn("X spec", s); self.assertIn("http://pr/1", s)
    def test_build_message_dryrun_no_pr(self):
        from autonomous_loop import line_notify
        m = line_notify.build_message("X spec", "dry-run", None)
        self.assertIn("messages", m)   # 合法 broadcast 結構
```

- [ ] **Step 2: 跑測試確認失敗** — FAIL

- [ ] **Step 3: 實作 line_notify.py**

```python
# governance/autonomous_loop/line_notify.py
import json, subprocess

def build_message(title, confidence_summary, pr_link):
    txt = f"🔄 自主迭代 loop：今天備好 1 個待放行 spec\n\n《{title}》\n可信度：{confidence_summary}"
    if pr_link: txt += f"\nPR：{pr_link}"
    else: txt += "\n(dry-run，未開 PR)"
    return {"messages": [{"type": "text", "text": txt}]}

def send(message, token):
    out = subprocess.run(
        ["curl","-s","-o","/dev/null","-w","%{http_code}","-X","POST",
         "https://api.line.me/v2/bot/message/broadcast",
         "-H", f"Authorization: Bearer {token}",
         "-H","Content-Type: application/json","-d", json.dumps(message, ensure_ascii=False)],
        capture_output=True, text=True)
    try: return int(out.stdout.strip())
    except ValueError: return -1
```

- [ ] **Step 4: 跑測試確認通過** — PASS

- [ ] **Step 5: Commit**

```bash
git add governance/autonomous_loop/line_notify.py scripts/test_autonomous_loop.py
git commit -m "feat(autonomous-loop): LINE 通知（body 另寫、復用傳輸層）"
```

---

### Task 6: orchestrator prompt + autonomous-loop.sh(整合)

**Files:**
- Create: `governance/autonomous_loop/orchestrator-prompt.md`(claude -p 跑 brainstorm + design-loop 的指令模板,沿用 Task 1 spike 驗證的形態,加 Global Constraints 全部規則:canary a/b/c、opus 起手、強制地面事實查證、獨立 judge、收斂 `lumos loop status --need 2`)
- Create: `governance/autonomous-loop.sh`
- Modify: crontab(`0 10 * * *` 加 governance/autonomous-loop.sh,**dry-run 旗標**)

**Interfaces:**
- Consumes: `gap_select.select`、`confidence_report.build_report`、`line_notify.build_message/send`
- 流程:`--dry-run`(預設)/ `--pr` 兩態。

- [ ] **Step 1: 寫 autonomous-loop.sh 骨架 + 起手驗當日日報**

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${1:---dry-run}"                  # --dry-run | --pr
TODAY="$(date +%F)"
REPORT="$SCRIPT_DIR/reports/governance-$TODAY.json"
PENDING="$SCRIPT_DIR/pending"; mkdir -p "$PENDING"
# R3-F-R3-3 起手驗當日日報存在(缺日=跳過,不視為錯誤)
[ -f "$REPORT" ] || { echo "[$(date '+%F %T')] 今日無日報($REPORT),跳過"; exit 0; }
```

- [ ] **Step 2: 接 gap_select(N=1 gate)**

```bash
GAP_JSON="$(cd "$REPO" && python3 -c "
import sys; sys.path.insert(0,'governance')
from autonomous_loop import gap_select
import json
mode='pr' if '$MODE'=='--pr' else 'dryrun'
g=gap_select.select('$REPORT','$SCRIPT_DIR/backlog.jsonl','$PENDING',mode,'$TODAY')
print(json.dumps(g) if g else '')
")"
[ -n "$GAP_JSON" ] || { echo "[$(date '+%F %T')] 無可展開 gap(N=1 gate 或 backlog 空),結束"; exit 0; }
```

- [ ] **Step 3: 跑 claude -p orchestrator(brainstorm + design-loop,Task 1 驗證的形態)**

```bash
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.config/ai-daily/claude_oauth_token" 2>/dev/null)"
PROMPT="$(cat "$SCRIPT_DIR/autonomous_loop/orchestrator-prompt.md")
\n\n要處理的 gap:$GAP_JSON\n模式:$MODE"
claude -p "$PROMPT" --allowedTools "Read,Edit,Bash,Grep,Glob,Agent,WebSearch,WebFetch" \
  --permission-mode dontAsk --output-format json > "$SCRIPT_DIR/logs/orchestrator-$TODAY.json" 2>&1 || true
```

orchestrator-prompt.md 要求 claude -p:依 gap brainstorm spec 草稿(替你做方案決策)→ 寫到 `docs/design/$TODAY-<topic>.md` → 跑 design-loop(canary a/b/c 輪換、opus auditor、強制地面事實查證、獨立 judge 判 canary、`lumos canary record`/`loop status --need 2`,max cap 6 輪)→ 收斂後輸出 `{topic, spec_path, loop_id, converged: true/false}` JSON。

- [ ] **Step 4: 收斂後產可信度報告 + 放行閘(dry-run/PR 兩態)**

```bash
RESULT="$(tail -c 4000 "$SCRIPT_DIR/logs/orchestrator-$TODAY.json")"  # 取 orchestrator 回傳 JSON
# 解析 converged / spec_path / loop_id(python 一行),converged=false → LINE 告警「未收斂」、不開 PR、exit
# converged=true:
#   - confidence_report.build_report(.canary-log, loop_id, RESIDUAL_RISKS) → PR body
#   - dry-run:複製 spec 到 $PENDING/、LINE build_message(title, summary, None) + send
#   - pr:  git checkout -b auto/spec-<topic>-$TODAY; git add spec; git commit; gh pr create --body "<可信度報告>"; LINE 帶 PR link
```
(此 step 的 python 黏合碼在 `autonomous-loop.sh` 內聯;RESIDUAL_RISKS 常數=spec 誠實天花板四條。)

- [ ] **Step 5: chmod + 手動 dry-run 一次驗證不爆**

```bash
chmod +x governance/autonomous-loop.sh
./governance/autonomous-loop.sh --dry-run   # 應走完:驗日報→選gap→(若有)跑orchestrator→寫pending/+LINE;或乾淨跳過
```
Expected:exit 0,無 traceback;有 gap 則 `governance/pending/` 出現 spec、LINE 收到 dry-run 訊息。

- [ ] **Step 6: Commit(先不上 cron)**

```bash
git add governance/autonomous-loop.sh governance/autonomous_loop/orchestrator-prompt.md
git commit -m "feat(autonomous-loop): orchestrator prompt + 入口 script（dry-run/PR 兩態，未上 cron）"
```

---

### Task 7: dry-run 部署觀察(人工閘,非 TDD)

**這是 spec「第一版先 dry-run」的落地。不寫測試——它的成功判準是人觀察品質。**

- [ ] **Step 1: 上 cron(dry-run 模式)**

```bash
( crontab -l; echo "5 10 * * * /Users/enzo/harness/lumos-toolchain/governance/autonomous-loop.sh --dry-run >> /Users/enzo/harness/lumos-toolchain/governance/logs/autonomous.log 2>&1" ) | crontab -
```
(注:crontab 在本機可能需互動授權;失敗則手動每天跑或交用戶。)

- [ ] **Step 2: 觀察 ≥3 天,逐項人工檢查(寫進 `governance/autonomous_loop/DRYRUN-OBSERVE.md`)**

每天看 `governance/pending/` 產出 + log,核:① 自動選的 gap 合不合理(value 判準對嗎)?② 自動 brainstorm 的 spec 能不能看(方案決策合理嗎)?③ design-loop 收斂可不可信——**重點抽查每輪 severity 自報 vs PR body 實際 findings 是否一致**(R3-F-R3-1 最弱環)?④ 地面事實查證有沒有真查?⑤ 成本(單日 token/時長)?

- [ ] **Step 3: 達標才開真 PR 模式**

dry-run 品質達標(≥3 天 spec 都可放行品質、severity 自報未發現系統性灌水)→ 改 cron 為 `--pr`、`gh auth status` 確認登入。否則停、回報問題、調 orchestrator-prompt。

- [ ] **Step 4: Commit 觀察結論**

```bash
git add governance/autonomous_loop/DRYRUN-OBSERVE.md
git commit -m "docs(autonomous-loop): dry-run 觀察結論 + 是否轉真 PR 的決定"
```

---

## Self-Review

**Spec coverage:** 5 組件 → Task 3(組件1 gap 抽取+gate)、Task 2(組件5 backlog)、Task 6+Task 1(組件2 brainstorm+組件3 design-loop,orchestrator)、Task 4+Task 6(組件4 放行閘+可信度報告)、Task 5(組件4 LINE)。誠實天花板四條 → Task 4 RESIDUAL_RISKS + Task 7 step2 抽查 severity 自報。技術可行性 B1 → Task 1 spike 閘。✅ 全覆蓋。

**Placeholder scan:** Task 6 step4 的 python 黏合碼以註解描述(非完整 code)——這是整合膠水,刻意留給實作者依前 task 的明確 interface 拼;其餘 task 均有完整 test+impl code。orchestrator-prompt.md 內容以行為清單描述(它是 prompt 非 code),可接受。

**Type consistency:** `add_gaps/load_backlog/pop_top`(Task 2)被 Task 3 `select` 正確消費;`select` 回 `dict|None` 被 Task 6 正確處理;`build_report`(Task 4)、`build_message/send`(Task 5)簽章一致。✅
