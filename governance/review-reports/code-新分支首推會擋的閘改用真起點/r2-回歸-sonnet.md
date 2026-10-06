severity: minor

## F1 觸及清單「任何一個 diff 失敗就不交」沒有測試釘住
severity: minor
blocking: 否
引句:「  if [[ "$_ok" -eq 1 && ( -s "$_f" || "$_n" -gt 0 ) ]]; then printf '%s' "$_f"; else rm -f "$_f"; fi」
這次 diff 沒有動任何測試檔(只有計劃筆記、pre-push、lumos、INDEX.md)。`file: scripts/test_lumos.py:17757` 起的 t_prepush_block_range_callers 只靜態檢查 pp_touched_file 有呼叫 pp_block_range_for,沒有跑「多個 ref、其中一個 git diff 失敗、另一個有輸出」的情境。把條件改回舊式 `-s "$_f" || (...)` 沒有任何測試會紅(我試著在複本上翻紅,但測試沒有跑出結果,所以這點是從測試內容讀出來的,不是翻紅實證)。修法本身語意正確,所以只標 minor。建議補一支:兩行推送,第二行的遠端舊值故意壞掉(例如不存在的 sha),斷言不傳 --touched-from。

## 各鏡頭查證(無其他問題)
1. 正確性:引句:「local _out pr_rc=0」——`local` 宣告與 `_out="$(...)" || pr_rc=$?` 分在兩行(`file: scripts/hooks/pre-push:56-58`),不會吞 rc;pp_stop_if_signaled 收到的仍是 push-range 的 rc。`[[ A && ( B || C ) ]]` 的括號兩側有空白,bash 3.2 與 5 都合法。t_prepush_gates_stop_on_signal 用的 regex `\$[a-z]+_rc` 仍比到 `$pr_rc` 與 `$tf_rc`,實數 8 行(59、315、381、393、431、458、512、541),數字沒變。
2. 測試:引句:「return cmd_push_range(repo=args.prg_repo, diff_range=args.prg_diff, push_remote=args.prg_remote,」——函式簽名 `cmd_push_range(repo, diff_range, push_remote, pushed_ref)`(`file: scripts/lumos:41911`)四個關鍵字全對得上,t_push_range_cli 走 CLI 路徑涵蓋;除 F1 外沒看到假綠。
3. 圖譜:引句:「| 代碼要推、要過高風險審 | `commands/06-代碼審與推送.md` | pitfalls --diff」——INDEX 補了 push-range;固定席節點沒附,不逐條答。

只有一條 minor(觸及清單失敗分支缺測試),其餘三個鏡頭沒有發現問題。
