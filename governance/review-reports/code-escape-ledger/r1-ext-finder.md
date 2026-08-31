ESC-01|major|引句:「語意:某個審查迴圈收斂放行了,下游(實作/CI/prod/人)發現可歸因的缺陷→記一筆。」|scripts/lumos:5299|守衛只要 `.canary-log.jsonl` 任一合法 JSON 的 `loop` 相同便放行，未檢查該迴圈是否真正收斂或放行；`missed`、未完成首輪甚至非審查事件都能冒充可歸因迴圈，污染 ground truth。

ESC-02|blocker|引句:「與攔截帳(★圖譜攔截★記號,同計劃)互為兩面。append-only、不進任何閘;」|scripts/lumos:5311|新帳用一般文字 `open(...,"a")` 寫入，未使用本檔既有 `_ledger_append` 的 `O_APPEND + 單次 os.write + ≤4KB + O_NOFOLLOW` 合約；任意長 `--desc`、程序中斷或並行 writer 可留下半行，且 symlink 可把紀錄追加到非預期檔案，造成帳本或目標檔資料損壞。

ESC-03|major|引句:「提醒:逃逸帳有一行壞損(非法 JSON),跳過不計;帳檔」|scripts/lumos:5269|讀側只攔 JSON 語法錯；合法 JSON 的 `null`、陣列、字串會在下一段 `r.get(...)` 直接崩潰，物件中 `ts:null` 也會在 `[:10]` 崩潰，因此一筆壞帳即可讓全部 `--list` 永久不可讀。

ESC-04|major|引句:「記逃逸要同時給 --severity 與 --desc(或用 --list 看帳)」|scripts/lumos:17439|`--list` 與 `loop_id/--severity/--desc/--stage` 沒有互斥檢查；例如完整記帳命令誤帶 `--list` 會 rc0 只列帳、靜默不寫入，令操作者誤以為逃逸已成功記錄。

severity: blocker
