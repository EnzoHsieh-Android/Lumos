---
type: system
status: done
created: 2026-06-26
updated: 2026-06-26
self_audit: sonnet/2026-06-26
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-06-19_reversibility-governance-ledger]]"
summary: |-
  FLOW:① 可逆性 — Systems KEY 行標 ★IRREVERSIBLE★/★CHECKPOINT★ + [rollback:decisions]/[guard:decisions] → doctor Check R / lint 強制 → ③ findings 經 doctor(僅 --ci)append .governance-log.jsonl → lumos gov 唯讀彙整查詢
  KEY:可逆性走平行函式 extract_reversibility,完全不碰 extract_contracts 的 7 個 callsite(invariant 合約家族零靜默失效)[test:t_reversibility_doctor]
  KEY:不可逆標記缺實質回退 → doctor --ci / lint error(硬擋);兩軌任一合規即放行:[rollback:decisions](事後回退)或 [guard:decisions](事前冪等/核可閘)[test:t_reversibility_guard_doctor]
  KEY:checkpoint 標記缺回退只 warn_soft(印但不計 issues)→ doctor --ci 仍 rc0;新增 warn_soft 因既有 warn 會 issues+=1 在 --ci 下誤擋[test:t_reversibility_doctor]
  KEY:可逆性標記僅限 type=system;標在 Issue/Verification → error 標錯型別;type 缺失/非字串不崩不誤報
  KEY:[rollback:]/[guard:] v1 唯一支援形式 = decisions,語義=本節點 decisions[] 有 ≥1 條非空 rollback/guard 內容;其他 ref 值視為未解析
  KEY:lumos gov 唯讀彙整器,不合併寫入路徑(避 bash+python 多寫者搶檔 race);四來源 = bypass-log(L2)/rot-queue(L3)/governance-log(doctor)/canary-log;dedup 在讀時做
  KEY:gov 三檔皆 gitignore local-only,是本機開發可見性工具,非合規物;L2 無 node、L3 以 Verification 為鍵 → 對 Systems 為部分視圖
  KEY:Check H(後加)僅 --ci 掃 git diff,正則命中疑似不可逆動作(prod/smtp/DROP TABLE…)而無不可逆標記時軟提醒,不擋
  DEP:scripts/lumos run_doctor(Check R/Check H)｜cmd_lint(單檔 Check R)｜cmd_gov｜extract_reversibility/_rollback_resolved/_guard_resolved｜parse_decisions(吃 rollback/guard sub-key)
  DEP:文件四面同步 — graph-discipline.md 速查｜lumos-project-notes SKILL.md｜NEW_HINT[system]｜lint;漂移測試守衛(碼有強制 → 文件必須提)[test:t_reversibility_drift]
  TEST:258 passed(macOS);t_reversibility_lint/doctor/guard_doctor/governance_log_write/gov_query/drift
  VERIFY:[[Verification/2026-06-19_reversibility-governance-ledger]]
decisions:
  - content: 可逆性走自己的平行函式 extract_reversibility,完全不碰 extract_contracts 管線
    context: design-loop R1-BLOCKER-1 / R2-BLOCKER-A — 若把可逆性塞進 extract_contracts,其 7 個 callsite(Check T、cmd_contracts、guard 家族、_html_model)語義被牽動,有靜默失效風險
    why_chosen: 平行路讓 ★INVARIANT★/★DEBT★ 家族全維持原狀、零回歸;CHECKPOINT_RE/IRREVERSIBLE_RE 寫死對齊 INVARIANT_RE 形狀
    decided: 2026-06-19
    valid: true
  - content: KEY 行 [rollback:](獨立 extractor 自剝 tag)與 decisions[].rollback(frontmatter 欄位)是兩個不同結構的機制,實作分清
    context: design-loop R2-BLOCKER-B — 原稿把二者混為一談;[rollback:] 是指針、decisions[].rollback 是實際回退內容,_rollback_resolved 要求指針指到 decisions 真有非空 rollback
    why_chosen: 不碰 INV_TAG_RE/strip_test_refs(避動到 guard bind 比對語義);要求解析到實質內容,不能只是冒號後有字
    decided: 2026-06-19
    valid: true
  - content: ③ 治理帳改唯讀彙整器,doctor 是唯一新寫者且只在 --ci append,dedup 在讀時做
    context: design-loop R1-BLOCKER-3 / R2-MAJOR-2 — 原提案合併多 hook 寫入路徑,bash+python 多寫者搶檔有 race / schema 不一;且 doctor 非 --ci 不該寫(R2-MINOR-2)
    why_chosen: 既有 bypass-log/rot-queue 維持原樣;doctor 純 append(不必每 push 讀全檔)、gov 顯示時才 dedup(key=commit+frozenset(nodes)+gate+kind+token);非 git / 取不到 HEAD 則跳過寫入不報錯
    decided: 2026-06-19
    valid: true
  - content: CHECKPOINT 類 warning 走新增 warn_soft()(印但不計 issues),不走會計 issues 的 warn()
    context: design-loop R3-MAJOR-3 — run_doctor 既有 warn() 一律 issues += len,任何 warn 在 --ci 下會 rc1,會誤擋只有 checkpoint 缺 rollback 的情況
    why_chosen: Check R 只對 error 級(irreversible 缺實質回退、標錯型別)呼叫 warn(),對 checkpoint/懸空呼叫 warn_soft();回歸測 t_reversibility_doctor 斷言「只有 checkpoint 缺回退 → rc0」
    decided: 2026-06-19
    valid: true
---
# reversibility-governance-ledger

治理日報點名的方法論兩盲點，一起補：四道把關只問「有沒有寫、真不真」，不問**改動能不能安全收回**（可逆性）；治理訊號散在多個 hook，無法**一次查某節點歷來被哪幾道閘攔過**（稽核軌跡）。

源起：日報 2026-06-19（reversibility + audit-trail 兩軸，點名為 lumos 方法論盲點）。

## 是什麼
- **功能 ①（Check R）**：在 Systems 節點 summary 的 KEY 行用 `★IRREVERSIBLE★`/`★CHECKPOINT★` 標記不可逆/難救動作，逼作者在動手前寫下 undo 路徑（`[rollback:decisions]`）或事前防護（`[guard:decisions]`）。doctor 與 lint 強制。
- **功能 ②（`lumos gov`）**：唯讀彙整器，把分散的治理事件 log 合成一條時間軸，或查某節點歷來被哪幾道閘攔過。gov 寫路徑（doctor `--ci` append `.governance-log.jsonl`）是本功能的子機制，非獨立功能。

## 關鍵機制
### Check R 標記與強制
- `★IRREVERSIBLE★`：收不回（上架、prod DB 遷移）。缺實質回退 → **error**（doctor `--ci` / pre-push 擋，同裸合約）。
- `★CHECKPOINT★`：改了難救，動手前先存還原點。缺回退只 **warning**（文件性，不擋）。
- 強制行為見 `scripts/lumos` `run_doctor` 的 Check R 區段（約 L621）與 `cmd_lint` 單檔版（約 L1229）。
- 「實質回退」判定（`_rollback_resolved`/`_guard_resolved`，L1099-1110）：ref 字面必須是 `decisions`，且本節點 `decisions[]` 有 ≥1 條非空 `rollback`（或 `guard`）內容；其他 ref 值一律視為未解析。

### 兩軌合規（spec 後擴充，commit eb73b22）
原 spec v1 只有 `[rollback:decisions]`（事後回退）。實作另加 `[guard:decisions]` 事前預防路徑：`★IRREVERSIBLE★` 只要 `_rollback_resolved` **或** `_guard_resolved` 任一為真即放行 —— 對「寄信／送外部 API」這類無回退但可用冪等鍵／核可閘事前防護的動作開一條合規路。`★CHECKPOINT★` 不讀 guard_ref。

### 天花板（誠實表述）
硬擋的語義是「逼你寫下 undo 路徑」，**證明你寫了補償步驟，不證明補償跑得動、不證明與現行 schema 一致**（那是 validation，工具到不了）。「有 `[rollback:]`」≠「驗過能用」。措辭刻意與硬擋一致：硬擋的是「有沒有寫下實質 undo」，不是「undo 能不能跑」。

### `lumos gov` 唯讀彙整
- 四來源（`cmd_gov`，L1252）：`.bypass-log.jsonl`（L2 繞過）、`.rot-queue.jsonl`（L3 rot）、`.governance-log.jsonl`（doctor `--ci` 新寫者）、`.canary-log.jsonl`（canary 審計留痕，spec 後加，commit 58ae539）。
- dedup 在**讀時**做，key = `(commit, frozenset(nodes), gate, kind, token)`；`nodes` 寫入即 stem 化，讀時 stem 比對。
- 預設 `--since 90`（單位：天）；三檔皆 gitignore，**本機開發可見性工具，非合規物**（移除了原提案的歐盟 Art.12 合規宣稱）。
- 已知限制（輸出明確標示）：L2 繞過無 node、L3 以 Verification 為鍵 → 對 Systems 節點為**部分**視圖；v1 不載 vault graph 做 Systems↔Verification 反查 join。

### Check H（spec 後加，commit 2482746）
`run_doctor` 另有 Check H（約 L690），僅 `--ci` 掃 `git diff`，正則命中疑似不可逆動作（`prod`/`smtplib`/`DROP TABLE`/`requests.post`/`boto3`… 見 `IRREVERSIBLE_HINT_PATTERNS` L1027）而該節點無 `★IRREVERSIBLE★` 時軟提醒、不擋。這正是原 spec §5 YAGNI 砍掉的「commit-time 軟提醒」之後以 push-time / 純軟提醒形式回歸（掃 diff 而非檔名 stem 配對）。

## 關鍵決策
見上方 decisions[]（四條，皆 design-loop 四輪對抗審計揪出的 blocker/major）。完整 alternatives 與逐輪修正史見設計稿末「審計修正紀錄」（四輪 CONVERGED）。

## 已知限制
- `gov <node>` 對 L2/Systems 為部分視圖（見上）。
- `[rollback:]`/`[guard:]` v1 無寫入指令（手寫進 KEY 行），對比 `guard bind` 寫 `[test:]` 的不對稱明確接受，留 v2。
- 工具天花板：證明「有寫」≠ 證明「能跑」。

## 相關
- 設計稿：`docs/design/2026-06-19-reversibility-and-governance-ledger.md`（design-loop 四輪 CONVERGED）。
- 實作計畫：`docs/design/2026-06-19-reversibility-and-governance-ledger-plan.md`（6 任務 TDD）。
- 後續擴充計畫：`docs/superpowers/plans/2026-06-24-check-r-guard.md`（[guard:] 兩軌）、`docs/superpowers/plans/2026-06-25-doctor-irreversible-hint.md`（Check H）。
- 實作落點：`scripts/lumos` `run_doctor`(Check R/H)、`cmd_lint`、`cmd_gov`、`extract_reversibility`/`_rollback_resolved`/`_guard_resolved`、`CHECKPOINT_RE`/`IRREVERSIBLE_RE`/`ROLLBACK_REF_RE`/`GUARD_REF_RE`。
