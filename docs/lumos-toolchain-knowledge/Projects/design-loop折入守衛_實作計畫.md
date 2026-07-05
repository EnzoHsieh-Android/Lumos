---
type: project
status: doing
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/project
  - status/doing
related:
  - "[[design-loop折入守衛_計劃]]"
plan_refs:
  - "[[design-loop折入守衛_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:「design-loop 折入守衛」TDD 實作計畫(設計見 [[design-loop折入守衛_計劃]]);兩交付=lumos fold-check <path> 指令(scripts/lumos)+ lumos-design-loop SKILL.md step7 強制子步
  KEY:任務序=T1 argparse+讀盤+鏡像段列舉(容節號標題)→ T2 value-drift(全文域單一 pattern-value、排除審計紀錄段)→ T3 reverse-omission(全文顯著 token、排除 <…>placeholder+審計紀錄段)→ T4 rc+--json schema → T5 SKILL.md step7 更新+回歸(對 impact spec 跑 fold-check)
  KEY:算法權威在設計 §2(fold-check)、§3(skill step7);每 task 給可執行測試+實作要點
  DECISION:實作用 subagent-driven-development;merge 前全 test_lumos.py + 對現有 spec 跑 fold-check 回歸不誤傷
  DEP:[[design-loop折入守衛_計劃]]
  TEST:未開工(計畫定稿)
---
# design-loop 折入守衛 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development。Steps 用 `- [ ]`。
> **設計權威**:[[design-loop折入守衛_計劃]](§2 fold-check 演算法 / §3 skill step7 / §4 天花板 / §5 測試)。本計畫每 task 給可執行測試 + 實作要點,算法細節以設計 § 為準。

**Goal:** 造 `lumos fold-check <path>` + 改 `lumos-design-loop` SKILL.md step7,把 design-loop 折入漂移從審計員盤子挪到機械閘。

**Architecture:** `lumos fold-check <path>` 讀盤 → 列舉鏡像段(summary/json fence/審計紀錄/天花板,標題容節號)+ 全文域 value-drift(同識別詞不同值)+ 全文域 reverse-omission(顯著 token 某段缺),掃描域排除審計紀錄段與 `<…>`placeholder;rc1=有 flag(給 Claude 訊號非機械 abort);SKILL.md step7 加「寫審計紀錄→fold-check→解 flag→grep canary=0→commit」。

**Tech Stack:** python3 標準庫(同 scripts/lumos);既有 `cmd_refcheck`(吃 md_path 可參考讀盤模式)。

## Global Constraints
- 零第三方依賴;讀盤(`Note` 不存 body,同 refcheck `read_text()`)。
- 掃描域**排除 `## …審計修正紀錄` 段**(刻意引歷史舊值,掃它必假陽)。
- reverse-omission **排除 `<…>` placeholder**。
- 鏡像段標題比對**容節號前綴**(regex `^##\s+(§\d+\s+)?(審計修正紀錄|誠實天花板)`)。
- 閘是紀律:rc1 是訊號,不是 script abort。
- 測試進 `scripts/test_lumos.py`;merge 前對現有 spec 跑 fold-check 回歸不誤傷。

---

### Task 1: `lumos fold-check <path>` argparse + 讀盤 + 鏡像段列舉

**Files:** Modify `scripts/lumos`(新 `cmd_fold_check` + argparse);Test `scripts/test_lumos.py`

**Interfaces:** Produces: `cmd_fold_check(path, as_json=False) -> int`;`_fold_mirror_sections(text) -> list[str]`(容節號標題)。

- [ ] **Step 1: 失敗測試**
```python
def t_fold_mirror_sections():
    text = "---\nsummary: |-\n  KEY:x\n---\n## §2 A\n```json\n{}\n```\n## §4 誠實天花板\nc\n## §5 審計修正紀錄\nd"
    secs = _fold_mirror_sections(text)
    assert "summary" in secs
    assert any("誠實天花板" in s for s in secs)   # 容 §4 前綴(r1-F5)
    assert any("審計修正紀錄" in s for s in secs)
    assert any("json" in s.lower() for s in secs)  # json fence 算鏡像段
```
- [ ] **Step 2: FAIL**。Run: `python3 scripts/test_lumos.py -k fold_mirror`
- [ ] **Step 3: 實作** — argparse `fold-check`(`path` 位置參數 + `--json`);`cmd_fold_check` 讀 `Path(path).read_text()`;`_fold_mirror_sections` 掃 summary block + ` ```json ` fence + 標題 regex `^##\s+(§\d+\s+)?(審計修正紀錄|誠實天花板)`(設計 §2.1)。
- [ ] **Step 4: PASS**。
- [ ] **Step 5: Commit** `feat(fold-check): argparse + 讀盤 + 鏡像段列舉(容節號)`

---

### Task 2: value-drift(全文域、單一 pattern-value、排除審計紀錄段)

**Files:** Modify `scripts/lumos`(新 `_fold_value_drift`);Test。

**Interfaces:** Produces: `_fold_value_drift(text) -> list[dict]`(每筆 `{key, a, b}`;掃描域排審計紀錄段)。

- [ ] **Step 1: 失敗測試**
```python
def t_fold_value_drift():
    text = "§1 用 `fold-check <node>`\n§2 用 `fold-check <path>`\n## §9 審計修正紀錄\nfold-check <node> 舊史"
    d = _fold_value_drift(text)
    keys = [x["key"] for x in d]
    assert "fold-check" in keys                    # 全文域 body↔body(r2-F1)
    # 審計紀錄段的 <node> 不算(r2:排除掃描)——不應因它多一筆
    assert len([x for x in d if x["key"]=="fold-check"]) == 1
    assert _fold_value_drift("只有 `fold-check <path>` 一種") == []   # 一致→無 flag
```
- [ ] **Step 2: FAIL**。
- [ ] **Step 3: 實作** — 見設計 §2.2:先切掉 `## …審計修正紀錄` 段;掃值 pattern(`\d+\.\.\w+`/`\d+min`/`§\d+`/`fold-check \S+` 類「識別詞+值」),同識別詞不同值 → 一筆。單一抽取法(不混兩法)。
- [ ] **Step 4: PASS**。
- [ ] **Step 5: Commit** `feat(fold-check): value-drift 全文域(單一法、排除審計紀錄段)`

---

### Task 3: reverse-omission(全文顯著 token、排除 placeholder + 審計紀錄段)

**Files:** Modify `scripts/lumos`(新 `_fold_reverse_omission`);Test。

**Interfaces:** Produces: `_fold_reverse_omission(text) -> list[dict]`(每筆 `{token, present_in, missing_in}`)。

- [ ] **Step 1: 失敗測試**
```python
def t_fold_reverse_omission():
    text = "---\nsummary: |-\n  KEY:用 --foo\n---\n## §2 body\n用 --foo 和 --bar 和 `<path>`"
    r = _fold_reverse_omission(text)
    toks = [x["token"] for x in r]
    assert "--bar" in toks              # body 有 summary 無
    assert "--foo" not in toks          # 兩邊都有→不 flag
    assert "<path>" not in toks and "path" not in toks  # placeholder 排除(r2-F5)
```
- [ ] **Step 2: FAIL**。
- [ ] **Step 3: 實作** — 見設計 §2.3:切審計紀錄段;抽顯著 token(`--flag`/`★MARKER★`/`\w+\.\w+`/CamelCase/backtick code),**排除 `<…>`**;某段缺其他段有的 → 一筆(summary vs body 為主軸)。
- [ ] **Step 4: PASS**。
- [ ] **Step 5: Commit** `feat(fold-check): reverse-omission(排除 placeholder+審計紀錄段)`

---

### Task 4: rc + `--json` schema 輸出 + 人讀輸出

**Files:** Modify `scripts/lumos`(組裝 `cmd_fold_check`);Test。

**Interfaces:** Produces: `--json` 依設計 §2.4 schema(`{path, mirror_sections, value_drift, reverse_omission}`);rc = flag 數>0 ? 1 : 0。

- [ ] **Step 1: 失敗測試**
```python
def t_fold_check_rc_json():
    clean = make_tmp_spec_consistent()      # 無 drift
    assert run_lumos(["fold-check", clean]) == 0
    drifty = make_tmp_spec_with_node_path_drift()
    assert run_lumos(["fold-check", drifty]) == 1
    out = json.loads(run_lumos_capture(["fold-check", drifty, "--json"]))
    assert set(out) == {"path","mirror_sections","value_drift","reverse_omission"}
```
- [ ] **Step 2: FAIL**。
- [ ] **Step 3: 實作** — 組裝三部分;`--json` `json.dumps(ensure_ascii=False)`;rc = (value_drift 或 reverse_omission 非空) ? 1 : 0;人讀印「☐ 複查 <段>」+ `⚠ flag`。
- [ ] **Step 4: PASS**。
- [ ] **Step 5: Commit** `feat(fold-check): rc + --json schema + 人讀輸出`

---

### Task 5: SKILL.md step7 更新 + 回歸(不誤傷現有 spec)

**Files:** Modify `skills/lumos-design-loop/SKILL.md`(step 7);Test(回歸)。

**Interfaces:** Consumes: T1-T4 的 `lumos fold-check`。

- [ ] **Step 1: 失敗測試(回歸)** — 對現有已固化的 spec 跑 fold-check,應乾淨或只剩已知可接受 warning(證不誤傷)。
```python
def t_fold_check_regression():
    rc = run_lumos(["fold-check", "docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_計劃.md"])
    # 已多次固化;若有 flag 須為可解釋的自指範例,人工判;此測試至少確認不 crash、rc in (0,1)
    assert rc in (0, 1)
```
- [ ] **Step 2: FAIL/確認行為**。
- [ ] **Step 3: 實作** — 見設計 §3:SKILL.md step 7 折入後插入「寫審計紀錄 → `lumos fold-check <真檔 path>` → 解 flag+逐段勾 → grep canary=0 → commit」;跑回歸確認現有 spec 不爆假陽(爆則調啟發式閾值)。
- [ ] **Step 4: PASS** + 全量 `python3 scripts/test_lumos.py`。
- [ ] **Step 5: Commit** `feat(design-loop): SKILL.md step7 強制 fold-check 子步 + 回歸`

---

## 落地回填
實作完成寫 `Verification/2026-..._design-loop折入守衛.md`,`plan_refs: "[[design-loop折入守衛_計劃]]"` 回指;設計節點 `TEST:`/`verified_by` 更新;Issue [[design-loop折入漂移_機械守衛]] 轉 status/done。
