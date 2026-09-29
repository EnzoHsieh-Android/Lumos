severity: major

## F1 c2 --keep 忽略 --dry-run,直接寫下表態
severity: major
blocking: 是
引句:「--dry-run", dest="dr_dry", action="store_true", help="只印改前改後,不寫筆記、不寫帳」
file: `scripts/lumos:28069`(cmd_drift_fix:`kind == "c2" and o.get("keep")` 在 dry_run 判斷之前就 `return cmd_drift_ack(...)`)
照做:04 指令文件與 `drift fix` 的 help 都說 `[--dry-run]` 只預覽不寫;06/04 文件與計劃教人「先 --dry-run 看改法」。
1. 在 `git clone --shared` 的臨時目錄跑:`python3 scripts/lumos drift fix Issues/linter-gap實務隱患 3 --kind c2 --keep --reason "<為什麼還沒解決>" --dry-run`
2. 輸出「✓ 表態記下了(DACK-53ab972d)...」,rc 0;`git status` 出現 `M governance/drift-acks.jsonl`,新增一行 `"kind": "c2", "reason": "<為什麼還沒解決>", ..., "seq": 1`。
3. 壞在:預覽旗標變成真寫入。t_drift_fix_dry_run_lock_and_ledger 只測 c3 的 dry-run,沒有 c2 --keep 的 dry-run 案例,所以沒抓到。表態一旦提交,該 Issue 不再被列出(同 c2 只列出層,但 gate 事件也記了 acked)。

## F2 程式印出的修法提示照抄可跑,但會把占位字原樣寫進筆記與表態檔
severity: major
blocking: 是
引句:「' --close --status done --reason "<為什麼算解決,附提交或測試>"',」
file: `scripts/lumos:27572`(`_drift_fix_hint` c2 兩條、c4 範本 `<sha>`/`<卷證>`;`_drift_fix_reason_ok` 只驗 4–200 字、`_drift_c4_text_err` 不擋 `<`、`>`)
照做:`drift scan` 印「改法:」清單,最自然的動作是複製那條指令。
1. 複製 scan 第一條 c2:`python3 scripts/lumos drift fix Issues/linter-gap實務隱患 3 --kind c2 --close --status done --reason "<為什麼算解決,附提交或測試>" --dry-run`
2. 預覽輸出 `+ > 已結案(2026-09-29,done):<為什麼算解決,附提交或測試>。以下是當時的排查紀錄,不是現況。`,rc 0;拿掉 --dry-run 就會 status 改 done、橫幅寫入,且經過了「形狀擋」。--keep 那條同樣(見 F1)把 `<為什麼還沒解決>` 寫進 drift-acks.jsonl 當理由。
3. 壞在:提示的占位符不會被擋,一次複製貼上就把一篇未解決的 Issue 標成已結案、理由是尖括號占位字。c4 範本在 shallow 或找不到卷證時是 `提交 <sha>;代碼審見 <卷證>`,同樣通過 `--new` 檢查(⚠ 未實跑 c4 寫入,依 `_drift_c4_text_err` 讀碼得出)。c3 的 `--status <a/b/c>` 因為要在枚舉內,複製會被擋,無此問題。

## F3 存量漂移防線計劃「修復結果」表仍寫工具鏈修後 0,與新表態語意下的現況不符
severity: minor
blocking: 否
引句:「| 工具鏈(2026-09-29) | 主線 dcffa974 | 20(c2 18、c4 2) | 0(剩 19 筆全數表態)」
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`(本次只改了 rtb 缺口那段,沒動這張表)
1. 新版把沒記 related 的舊表態視為無效(見 存量漂移守衛 新增 WHY)。在臨時目錄跑 `python3 scripts/lumos drift scan`:`c2 17、已表態 2`,17 筆舊 c2 表態全部重新列成未表態。
2. 接手的人讀表格會以為工具鏈是 0 筆待處理。表格是 2026-09-29 當時快照,但同一輪改動讓它失真,沒加一句「之後因表態改綁 related 而重新列出 17 筆,見改法計劃」。c2 是只列出層不擋,故 minor。

## 圖譜鏡頭固定席逐條判定
- guard-kill ★INVARIANT★(rc 優先序、--json 純度):改動在 `guard settle` 的 pass 分支(`_guard_settle_pass`)與 `_guard_pass_rewrite`,不碰 `guard kill` 的 rc 判定與 JSON 輸出路徑;不影響。新增的 WHY 行(settle 對 pass 補改、前提不符回 2、不拿今天充數)與 `cmd_guard_settle`/`_guard_settle_pass`/`_guard_settled_date` 讀起來一致;argparse 的 `--test` 改可選、`--date` 新增,06 文件寫法對得上(待完成缺 --test 會回 2,pass 帶 --date 走補改)。
- lumos-cli-read(search 排除 superseded 的 INVARIANT):改動只在 doctor E5 標「已結案 Issue」,不碰 search 濾網;不影響。
- lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 內):改動是 `_BOOKKEEPING_FILES` 加 `governance/drift-fixes.jsonl`(`scripts/lumos:21445` 已有),不碰 re-inject;不影響。
- bound-tests-gate、授權與歸屬、測試假綠形態、design-loop、pitfalls-code-loop:diff 只在 drift/guard/set 區段新增,SPDX 檔頭與 _VENDORED_TOOLKIT 沒動;新增測試 12 支都存在於 test_lumos.py(逐一 grep 有 def),綁定測試不會懸空。不影響。
- 其餘只列名的節點:未見直接牽連。

## 其他確認過、沒有問題
- skills 文件旗標對 argparse:04 的 `--dry-run/--date/--close/--status/--reason/--keep/--by/--old/--new` 全部存在;c1 的 `--date`、c5 無參數、c3 `--status` 範圍(驗證狀態扣 pending)一致。`lumos set <Issue> status wontfix/resolved` 實跑會列出全部 REVISIT 行,與 lumos-cli-write 新寫句一致。
- 新增的圖譜句子都是 WHY/TEST 前綴,無 FACT/FLOW/DEP、無新程式行號引用。
- 防線計劃刪掉的 `REVISIT:2026-10-13`:理由成立,五項缺口在程式裡都有對應(fix c1/c3/c4、settle pass、E5、ack related+seq,對應測試存在);唯一的落差是 F3 的表格。

最高等級:major
