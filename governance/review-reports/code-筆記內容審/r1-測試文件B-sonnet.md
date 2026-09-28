severity: clean

## 審查範圍與方法

逐 hunk 讀完整份 `r1-snapshot-b.patch`(ARCHITECTURE.md、`Projects/筆記內容審_計劃.md`、`Projects/筆記形狀擋_計劃.md`、新建的 `Systems/筆記內容審.md`、`Systems/筆記內容閘.md` 的 responsibility 改動、`scripts/test_lumos.py` 新增的 766 行測試、`skills/lumos-project-notes/commands/03-寫回圖譜.md`、`06-代碼審與推送.md`、`INDEX.md`、`reference.md`),並對照 `scripts/lumos` 的真代碼(`_notelines_*`、`_note_audit_*`、`cmd_decision_amend`、`_lens_push_base`、`_visible_lines`、`_BOOKKEEPING_DIRS`、`_VENDORED_TREE_FILES`)逐條核對每一句宣稱。

按第 1 條鏡頭要求,在 `mktemp` 出來的臨時複本(`cp -r` 整份 repo,不動審查現場)裡對三處關鍵斷言做「改壞翻紅」實測,附指令與輸出:

**實測 1 — S7 上下文信任方向**(`cmd_note_audit_record` 的 `if not heavy and cur_ctx.get(rid) != lst["rows"][rid]:`,`scripts/lumos:24718`):把條件改成 `if False and ...`(等於拿掉「上下文變了、輕的判定不收」這條規則),跑:
```
python3 scripts/test_lumos.py -k t_note_audit_record_per_row_trust_direction
```
基線 10 passed / 0 failed;改壞後 → `✗ ④上下文變了:判脈絡的不收`,9 passed / 1 failed。同時證明了「現場成立」:斷言④原本能過,不是因為別的原因擋掉那一行,而是這條 context-fingerprint 檢查真的在起作用(拿掉它,原本被排除的「目標行一」真的被收進去了)。

**實測 2 — S12 decision-amend 撞號拒絕**(`cmd_decision_amend` 裡遠端已有該決策編號時的 `raise ValueError(...)`,`scripts/lumos:24873-24875`):把 `if re.search(...)` 改成 `if False and re.search(...)`,跑:
```
python3 scripts/test_lumos.py -k t_decision_amend_field_fetch_remote_rename
```
基線 10 passed / 0 failed;改壞後 → `✗ ②遠端已有這個編號 → 拒絕…` 與 `✗ ④改名後:跟著改名找到遠端舊路徑,d1 照拒` 雙雙翻紅,8 passed / 2 failed。同時證明了「遠端追蹤參照真的存在」:測試 fixture 有真的 `git remote add origin <bare>` + `git push`,不是空講。

**實測 3 — S16 判定檔被刪次數**(`_note_audit_doctor_lines` 的 `n = sum(...)`,`scripts/lumos:24940`):加一行 `n = 0` 蓋掉真實計數,跑:
```
python3 scripts/test_lumos.py -k t_doctor_note_audit_ci_and_bypass_scan
```
基線 5 passed / 0 failed;改壞後 → `✗ ⑤印主線歷史裡判定檔被刪過幾次`,4 passed / 1 failed。

三處都翻紅,證明這幾支新測試不是裝飾性斷言,確實守到了對應規則。`t_note_lines_shared_new_lines` 我用讀碼交叉核對(`_note_shape_eval` 呼叫 `_notelines_new` 且不覆寫 `hook`/`per_commit`,故第一層行為不變;`_notelines_headings` 對圍欄的判定與 `_visible_lines(keep_fenced=True)` 的行為一致)確認邏輯自洽,未另外做破壞性重現。

## 文件/規格/程式碼比對結果

- **子命令計數 76→78**:`python3 scripts/lumos --help` 的 `positional arguments` choices 實測有 78 個(含新增的 `note-audit`、`decision-amend`),跟 ARCHITECTURE.md 與 `reference.md` 改後的數字一致,沒有漂移。
- **`codex exec -m <model> --sandbox read-only -o <報告檔> "<內容>" < /dev/null`**(`skills/lumos-project-notes/commands/06-代碼審與推送.md:45`)看起來跟 repo 裡其他地方一律用 stdin+shell 重導向的既有寫法(不帶 `-m`/`-o`)不同,一開始懷疑是編造的旗標;實測 `codex exec --help` 確認 `-m, --model` 與 `-o, --output-last-message <FILE>` 都是真旗標,寫法可用,不是問題。
- **派工詞範本**(`scripts/templates/note-audit-judge.md`)三個分類定義逐字比對 `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md` 第 8–10 行,一字不差;檔頭有 `SPDX-FileCopyrightText`/`SPDX-License-Identifier: MIT` 兩行,滿足 `Systems/授權與歸屬.md` 的 ★INVARIANT★(被複製的檔至少要有 SPDX 行);且此檔已登記進 `_VENDORED_TREE_FILES`(`scripts/lumos:16930`),不是只在計劃裡講講。
- **S1/S2/S3/S4/S5/S6/S7/S8/S9/S10/S12/S13/S16/S17/S18** 逐條讀對應函式(`_notelines_regions/_notelines_headings/_notelines_structural_lines/_notelines_content_id/_note_audit_items/_note_audit_closed_plans/_note_audit_fold/_note_audit_write_verdict/_note_audit_load_verdicts/cmd_note_audit_*/cmd_decision_amend/_note_audit_doctor_lines/_lens_push_base`),行為跟條款文字與測試斷言一致,沒發現條款講的行為程式沒做、或程式做了條款沒講的落差。
- **S10/S16 改寫的「範圍起點照三道檢查共用的推送起點判法」**:讀了 `_lens_push_base`(`scripts/lumos:29037`),確認它真的是 note-shape / home-check / note-audit 三處共用同一份函式(不是三份各自實作再假裝共用),「40 個 0 且找不到主線 → 空樹」「頂端已在主線上 → 沒有新東西」「其他從跟主線的分岔點算」三支路徑都在,跟計劃第 3 節第 6、9 點的新措辭一致,S10/S16 改動前後也沒有互相打架。
- **S1 措辭改動**(「小標題由同組的小標題函式照行給」)與程式一致:`_notelines_new` 本身不算 heading,由呼叫端另外呼叫 `_notelines_headings`,測試 `t_note_lines_shared_new_lines` 也是分開呼叫兩支函式驗證。

## 圖譜鏡頭(牽連節點)

- `Systems/lumos-cli-read.md`(★INVARIANT★,search 排除 superseded/保留 stale):這次改動不碰 `search`/ranking 邏輯,不影響。
- `Systems/guard-kill.md`(★INVARIANT★,`guard kill` rc 優先序與 JSON 純淨):這次改動不碰 `guard kill`,不影響。
- `Systems/授權與歸屬.md`(★INVARIANT★,LICENSE 不得進 `_VENDORED_TOOLKIT`、被複製的檔要有 SPDX):這次新增了一支會被 vendor 的檔(`scripts/templates/note-audit-judge.md`),是唯一有實際碰到這條合約的節點——已如上核對過,合規。
- `Systems/測試假綠形態.md`(★INVARIANT★,修法要配前置斷言證明現場成立):這次新增的測試正是這條合約要求的對象,已用三次破壞性重現實測驗過現場成立且真的會翻紅(見上)。
- `Systems/lumos-cli-lifecycle.md`(★INVARIANT★,re-inject sentinel 外部位元組相同):不碰 CLAUDE.md/AGENTS.md re-inject 邏輯,不影響。
- `Systems/design-loop.md`(★INVARIANT★,處置閘第五步的迴圈判定):這次沒有新開或碰 design-loop 迴圈,不影響。
- `Systems/pitfalls-code-loop.md`(★RISK★)、`Systems/loop-convergence-recording.md`(★RISK★):S17 讓 `governance/note-verdicts/` 進 `_BOOKKEEPING_DIRS`(`scripts/lumos:20361-20362`),同一組常數被小改動閘、風險型樣掃描、風險分級、代碼審留痕四處共用,新增判定檔不會被這兩個系統誤判成程式改動或推高風險,行為符合 S17 條款,不影響既有風險判斷邏輯本身。
- 其餘「超出上限,只列名」節點(`lumos-deinit`、`reversibility-governance-ledger`、`節點範圍與索引守衛`、`doctor-irreversible-hint`、`cochange-guard`、`lumos-refcheck`、`check-r-guard`、`check-t-sentinel`、`雙向門放行_計劃`、`bound-tests-gate`、`canary-audit`、`slim-get/install/uninstall`、`規格落成可驗收條件_計劃`、`逃逸自動記_計劃`、`core-invariant-baseline`、`judge-severity-gate`):這次改動的檔案集合(`scripts/lumos` 新增函式段落、`scripts/test_lumos.py` 新增測試段落、知識筆記、skill 文件)跟這些節點描述的機制(refcheck、cochange、bound-tests、canary、slim 安裝器、逃逸帳、判定嚴重度閘等)沒有函式層級的交集,判「不影響」。

## 總結

未發現 blocker/major/minor 可站得住的問題。總結:最嚴重等級 clean,blocking 0 條。
