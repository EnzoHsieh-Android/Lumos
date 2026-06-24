# Check R [guard:decisions] 事前預防路徑 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Check R 對 `★IRREVERSIBLE★` 動作新增 `[guard:decisions]`(事前冪等鍵/核可閘)作為 `[rollback:decisions]`(事後補償)的同等合規路徑——兩軌任一合規即放行。

**Architecture:** 純加法擴充可逆性軸。`extract_reversibility` 回傳從 3-tuple 改 4-tuple(加 `guard_ref`),同步 2 個解包點(doctor L622 / lint L1142);Check R 的 inner 分支對 `★IRREVERSIBLE★` 改判「rollback OR guard 任一 resolved」,`★CHECKPOINT★` 行為完全不變(guard 靜默忽略)。

**Tech Stack:** Python(`scripts/lumos` 單檔)、自訂測試 runner `scripts/test_lumos.py`(`t_` 前綴函式 + `check(name,cond,detail)`/`run(vault,*args)`/`write(v,rel,fm,body)`/`mkvault()`,**非 pytest**;跑全部:`python3 scripts/test_lumos.py`)。

## Global Constraints

- **兩軌任一合規即放行**:`★IRREVERSIBLE★` 有非空 `[rollback:decisions]` **或** 非空 `[guard:decisions]` 即 pass;兩者皆無才 error。
- **`[guard:]` 僅對 `★IRREVERSIBLE★` 生效**:`★CHECKPOINT★` 分支只讀 `_rollback_resolved`、不讀 guard;CHECKPOINT 有 `[guard:]` → 靜默忽略,無 rollback 仍出 `rev_soft` warning(行為等同現狀)。
- **v1 只支援 `[guard:decisions]` 字面**:`ref` 非 `decisions` → 視為未解析(同 rollback)。
- **誠實邊界**:只驗「decisions 有沒有記錄守衛」,**不驗守衛已在 code 實作**(同 `[rollback:]` 上界)。
- **不廢棄 `[rollback:]`**:兩軌並存。
- **4-tuple 同步**:`extract_reversibility` 改 4-tuple 後,L622(doctor)+ L1142(lint)兩解包點**必須同一 commit** 改,否則中間狀態紅燈。
- **防漂移同 commit**:`scripts/templates/graph-discipline.md` + `skills/lumos-project-notes/SKILL.md` + `t_marker_doc_sync` tuple 三者**同一 commit**(Task 2),否則 `t_marker_doc_sync` 立即紅燈。
- **不改**:`parse_decisions`、`IRREVERSIBLE_RE`、`CHECKPOINT_RE`、`ROLLBACK_REF_RE`、`_rollback_resolved`、型別守衛(`scripts/lumos:624`/`:1143`)、invariant/合約軸。

---

### Task 1: 核心 guard 路徑(scripts/lumos + 測試,原子)

**Files:**
- Modify: `scripts/lumos`(可逆性軸函式區 L991-1022、Check R doctor L618-642、Check R lint L1141-1149、NEW_HINT L2697)
- Test: `scripts/test_lumos.py`(擴 `t_reversibility_lint` + 新增 `t_reversibility_guard_doctor`)

**Interfaces:**
- Consumes(既有,已 ground-truth 坐實):`ROLLBACK_REF_RE`(L994)、`reversibility_rollback_ref`(L997)、`extract_reversibility`(L1002,現回 3-tuple)、`_rollback_resolved`(L1018)、`parse_decisions(note.fm_lines)`(L1740)、`extract_reversibility` 解包點 doctor L622 / lint L1142。
- Produces:`GUARD_REF_RE`、`reversibility_guard_ref(text)→str|None`、`_guard_resolved(note,ref)→bool`、`extract_reversibility` 改回 `(marker, clean, rollback_ref, guard_ref)` 4-tuple。

- [ ] **Step 1: 寫失敗測試(擴 `t_reversibility_lint` 末尾加 guard cases)**

在 `scripts/test_lumos.py` 的 `t_reversibility_lint` 函式**末尾**(現有最後一個 `check(...)` 之後、函式結束前)追加:

```python
    # ── [guard:decisions] 事前預防路徑(與 rollback 兩軌任一合規)──
    write(v, "Systems/Gd1.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登 API\n    decided: 2026-06-22\n    guard: 冪等鍵 X-Idempotency-Key + Redis 60s 去重\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄發票通知信 [guard:decisions]", body="# G1\n")
    r = run(v, "lint", "Systems/Gd1")
    check("lint: IRREVERSIBLE + 非空 guard → rc0", r.returncode == 0, r.stdout)
    write(v, "Systems/Gd2.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登\n    decided: 2026-06-22\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄信 [guard:decisions]", body="# G2\n")
    r = run(v, "lint", "Systems/Gd2")
    check("lint: IRREVERSIBLE + 空 guard → rc1", r.returncode == 1, r.stdout)
    write(v, "Systems/Gd5.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 雙保險\n    decided: 2026-06-22\n    rollback: revert.sql\n    guard: 冪等鍵\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 遷移 [rollback:decisions] [guard:decisions]", body="# G5\n")
    r = run(v, "lint", "Systems/Gd5")
    check("lint: rollback+guard 兩者皆有 → rc0", r.returncode == 0, r.stdout)
    write(v, "Systems/Gd6.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 部署\n    decided: 2026-06-22\n    guard: 核可閘\n"
          "summary: |-\n  KEY:★CHECKPOINT★ 部署 lab [guard:decisions]", body="# G6\n")
    r = run(v, "lint", "Systems/Gd6")
    check("lint: CHECKPOINT + guard → guard 靜默忽略、無 rollback 仍 warning rc0",
          r.returncode == 0 and "建議補回退" in r.stdout, r.stdout)
```

新增獨立 doctor 測試函式(放在 `t_reversibility_doctor` 之後):

```python
def t_reversibility_guard_doctor():
    v = mkvault()
    # IRREVERSIBLE + 非空 guard → 不報 error(doctor --ci rc0)
    write(v, "Systems/Gd.md",
          "type: system\nstatus: doing\n"
          "decisions:\n  - content: 補登 API\n    decided: 2026-06-22\n    guard: 冪等鍵 + Redis 去重\n"
          "summary: |-\n  KEY:★IRREVERSIBLE★ 寄信 [guard:decisions]", body="# Gd\n")
    r = run(v, "doctor", "--ci")
    check("doctor: IRREVERSIBLE + 非空 guard → rc0", r.returncode == 0, r.stdout)
    # IRREVERSIBLE 兩者皆無 → error,提示含兩選項
    v2 = mkvault()
    write(v2, "Systems/Bad.md",
          "type: system\nstatus: doing\nsummary: |-\n  KEY:★IRREVERSIBLE★ 寄信沒守衛", body="# B\n")
    r = run(v2, "doctor")
    check("doctor: IRREVERSIBLE 兩軌皆無 → 提示 rollback 或 guard",
          "[guard:decisions]" in r.stdout and "[rollback:decisions]" in r.stdout, r.stdout)
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -iE "guard|FAIL|✗" | head`
Expected: 新 guard cases 失敗(`[guard:]` 尚未解析,IRREVERSIBLE+guard 仍被當缺回退 → rc1 而非 rc0;doctor 提示也不含 `[guard:decisions]`)。

- [ ] **Step 3: 實作 scripts/lumos(可逆性軸 + Check R doctor/lint + NEW_HINT)**

(3a) `ROLLBACK_REF_RE`(L994)**之後**加:

```python
GUARD_REF_RE = re.compile(r"\[guard:\s*([^\]]+)\]")  # 可逆性軸,平行於 ROLLBACK_REF_RE
```

(3b) `reversibility_rollback_ref`(L997-999)**之後**加:

```python
def reversibility_guard_ref(text):
    m = GUARD_REF_RE.search(text)
    return m.group(1).strip() if m else None
```

(3c) `extract_reversibility`(L1002-1015)改回 4-tuple——把 `out.append(...)` 那行(L1013-1014)替換為:

```python
                    body = m.group(1)
                    clean_body = ROLLBACK_REF_RE.sub("", GUARD_REF_RE.sub("", body)).strip()
                    out.append((marker, clean_body,
                                reversibility_rollback_ref(body), reversibility_guard_ref(body)))
```

並把 docstring(L1003)更新為:`"""從 summary KEY 行抽 (marker, 去 [rollback:]/[guard:] 的乾淨文字, rollback_ref, guard_ref)。"""`

(3d) `_rollback_resolved`(L1018-1022)**之後**加:

```python
def _guard_resolved(note, ref):
    """[guard:decisions] 視為已解析 ⟺ 本節點 decisions[] 有 ≥1 條非空 guard。"""
    if not ref or ref.strip().lower() != "decisions":
        return False
    return any(str(d.get("guard", "")).strip() for d in parse_decisions(note.fm_lines))
```

(3e) Check R doctor 解包 + inner 分支(L622、L627-633)。把 L622 `for marker, clean, ref in extract_reversibility(nnote):` 改為:

```python
        for marker, clean, ref, guard_ref in extract_reversibility(nnote):
```

把 inner `elif not _rollback_resolved(nnote, ref):` 區塊(L627-633)替換為:

```python
            elif marker == "★IRREVERSIBLE★":
                if not (_rollback_resolved(nnote, ref) or _guard_resolved(nnote, guard_ref)):
                    rev_err.append(f"{rel}: {first_line(clean, 60)} (加 [rollback:decisions] 或 [guard:decisions])")
                    gov_events.append({"gate": "check-r", "kind": "blocked", "hard": True, "nodes": [nnote.stem]})
            elif not _rollback_resolved(nnote, ref):  # ★CHECKPOINT★;guard_ref 不讀
                rev_soft.append(f"{rel}: {first_line(clean, 60)}")
                gov_events.append({"gate": "check-r", "kind": "warned", "hard": False, "nodes": [nnote.stem]})
```

(3f) Check R lint 解包 + 分支(L1142、L1145-1149)。把 L1142 `for marker, rclean, ref in extract_reversibility(n):` 改為:

```python
    for marker, rclean, ref, guard_ref in extract_reversibility(n):
```

把 `elif not _rollback_resolved(n, ref):` 區塊(L1145-1149)替換為:

```python
        elif marker == "★IRREVERSIBLE★":
            if not (_rollback_resolved(n, ref) or _guard_resolved(n, guard_ref)):
                errs.append(f"{marker} 缺實質回退(行尾加 [rollback:decisions] 或 [guard:decisions],decisions[] 要有非空 rollback/guard):{first_line(rclean, 40)}")
        elif not _rollback_resolved(n, ref):  # ★CHECKPOINT★;guard_ref 不讀
            warns.append(f"{marker} 建議補回退([rollback:decisions]):{first_line(rclean, 40)}")
```

(3g) `NEW_HINT["system"]`(L2697)字串尾追加:

```
;外部不可逆(信已送/下游已消費)改用 [guard:decisions] 記冪等鍵/核可閘([guard:] 僅對 ★IRREVERSIBLE★ 生效;屬可逆性軸,與 lumos guard bind 的合約軸正交)
```

- [ ] **Step 4: 跑測試確認通過 + 全回歸**

Run: `python3 scripts/test_lumos.py 2>&1 | tail -3`
Expected: 全綠(含新 guard cases + 既有 `t_reversibility_lint`/`t_reversibility_doctor` rollback 回歸)。若某 doctor case rc 與預期不符,確認 `mkvault()` 預設節點不含其他 IRREVERSIBLE 干擾(用獨立 `v2` 已隔離)。

- [ ] **Step 5: Commit**

```bash
git add scripts/lumos scripts/test_lumos.py
git commit -m "feat(check-r): [guard:decisions] 事前預防路徑——IRREVERSIBLE 兩軌任一合規

extract_reversibility 改 4-tuple(同步 doctor/lint 兩解包點);_guard_resolved 驗 decisions[].guard 非空;CHECKPOINT 行為不變(guard 靜默忽略)。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: 防漂移文件同步(graph-discipline + SKILL + t_marker_doc_sync,原子)

**Files:**
- Modify: `scripts/test_lumos.py`(`t_marker_doc_sync` tuple 加 `"[guard:"`,L1073)
- Modify: `scripts/templates/graph-discipline.md`(可逆性段加 `[guard:decisions]` 說明)
- Modify: `skills/lumos-project-notes/SKILL.md`(可逆性/rollback 段加 `[guard:decisions]` 說明)

**Interfaces:**
- Consumes:`t_marker_doc_sync`(L1064-1075)掃 tuple 內每個字串是否同時在 SKILL.md 與 graph-discipline.md。

- [ ] **Step 1: `t_marker_doc_sync` tuple 加 `"[guard:"`**

`scripts/test_lumos.py:1073` 的 tuple 改為:

```python
    for m in ("★CHECKPOINT★", "★IRREVERSIBLE★", "[rollback:", "[guard:"):
```

- [ ] **Step 2: 跑測試確認失敗(doc 還沒加 `[guard:`)**

Run: `python3 scripts/test_lumos.py 2>&1 | grep -iE "drift.*guard|✗" | head`
Expected: `drift: [guard: 在 SKILL.md` 與 `drift: [guard: 在 graph-discipline` 兩條失敗。

- [ ] **Step 3: 兩個 doc 加 `[guard:decisions]` 說明**

先定位:`grep -n "\[rollback:" scripts/templates/graph-discipline.md skills/lumos-project-notes/SKILL.md`

在 `scripts/templates/graph-discipline.md` 提到 `[rollback:decisions]` 的可逆性說明行**之後**,補一行:

```markdown
- 外部不可逆(信已送出/下游已消費,事後無逆操作)→ 改用 `[guard:decisions]` 記事前守衛(冪等鍵/核可閘);`[guard:]` 僅對 `★IRREVERSIBLE★` 生效,與 `[rollback:]` 兩軌任一合規即放行。
```

在 `skills/lumos-project-notes/SKILL.md` 提到 `[rollback:decisions]` 的段落**之後**,補一句(照該檔既有行文密度):

```markdown
外部不可逆動作(信已送出、prod 遷移下游已消費)事後無逆操作 → 用 `[guard:decisions]`(decisions[] 記非空 `guard`:冪等鍵/核可閘)取代 `[rollback:]`;兩軌任一即過 Check R,`[guard:]` 僅 `★IRREVERSIBLE★` 適用。
```

- [ ] **Step 4: 跑測試確認通過**

Run: `python3 scripts/test_lumos.py 2>&1 | tail -3`
Expected: 全綠(`t_marker_doc_sync` 4 個 marker × 2 doc 全命中)。

- [ ] **Step 5: Commit**

```bash
git add scripts/test_lumos.py scripts/templates/graph-discipline.md skills/lumos-project-notes/SKILL.md
git commit -m "docs(check-r): [guard:decisions] 同步進 graph-discipline + project-notes + 漂移測試

t_marker_doc_sync 守 [guard: 在兩 doc(同 commit 防紅燈)。

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## 驗證(計畫完成後)

- **單元測試**:`python3 scripts/test_lumos.py` 全綠(新 guard cases + 既有回歸 + 漂移守衛)。
- **手動煙霧**:對一個 `★IRREVERSIBLE★` + `[guard:decisions]` + 非空 guard 的真實 vault 跑 `lumos doctor`,Check R 段應 pass。
- **誠實天花板**(向人提醒):`[guard:]` 只證「decisions 記了守衛」,不證守衛在 code 真生效——code 層靠 `[test:]` + CI;同 `[rollback:]` 上界。

## Spec 覆蓋自檢

- 組件 1(GUARD_REF_RE)→ T1 Step 3a;2(reversibility_guard_ref)→ 3b;3(_guard_resolved)→ 3d;4(extract_reversibility 4-tuple + 2 解包點)→ 3c+3e+3f;5(doctor 分支)→ 3e;6(lint 分支)→ 3f;7(NEW_HINT)→ 3g;8(graph-discipline)→ T2 Step 3;9(project-notes SKILL)→ T2 Step 3;10(t_marker_doc_sync)→ T2 Step 1。
- 測試策略 1-9 → T1 Step 1(lint 1/2/5/6 + doctor 1/3)+ 既有回歸(4/8)+ T2(9 漂移)。
