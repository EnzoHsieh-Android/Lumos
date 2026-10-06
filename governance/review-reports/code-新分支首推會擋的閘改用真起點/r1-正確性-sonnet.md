severity: minor

整體判斷:bash 3.2.57(macOS 內建)實跑確認 `[[ "$1" =~ ^0{40}(0{24})?$ ]]` 對 40 個 0、64 個 0 命中,41 個 0 不命中;印出格式的正則 40..40 命中。`set` 只開 `-u`(沒開 `-e`),`${4:-}` 處理正確;pp_block_range_for 設的全域 `_PP_BR`/`pr_rc` 沒被 pp_touched_file 的 `local _f _r`、`local _n _ok` 遮蔽(而且它在 `$(...)` 子殼裡跑、全域不外洩);子殼裡 pp_stop_if_signaled 的 exit 退出子殼,外層 `|| tf_rc=$?` 接得到。多 ref、頂端已在主線(印 頂端..頂端,測試 ④ 放行)、SHA-256(正則與空樹都吃 64)、REPO_ROOT 有空白(都有加引號)走過沒找到錯。push-range 印出任何不合格式都退空樹並講一句(fail-closed 方向)。cmd_push_range 的 `_push_range_start` 回值三種(None、判不了/空樹、一般 sha)都有對應分支。

## F1 訊號停下的測試沒釘到 pp_touched_file 那一路
severity: minor
blocking: 否 因為只是測試對一條已存在的防線釘得不夠緊,掛鉤行為本身正確。
file: `scripts/hooks/pre-push`:316(複製到臨時目錄的行號)與 `scripts/test_lumos.py` 的 t_prepush_new_branch_block_range ⑦
具體場景:⑦ 的推送行(新分支首推、push-range 被 SIGTERM)會先走 pp_touched_file(子殼,先被殺)、再走主迴圈。我把 `pp_stop_if_signaled "$tf_rc"` 那行從臨時副本刪掉,`python3.14 scripts/test_lumos.py -k prepush_new_branch_block_range` 仍是 `8 passed, 0 failed`(⑦ 由主迴圈裡 pp_block_range_for 自己那行 pp_stop_if_signaled 接住)。同理只拿掉 `|| tf_rc=$?` 而留著 stop 行,t_prepush_gates_stop_on_signal 的「八行」計數照綠、⑦ 也照綠,但 doctor 的觸及清單那條路被殺掉後會悄悄放行。測試註解宣稱「迴圈裡一次、餵 doctor 的觸及清單一次」兩處都有驗,實際只驗到第一個先觸發的。
引句:「pp_stop_if_signaled "$tf_rc" "新分支首推起點(push-range)"」
佐證:臨時副本刪該行後 ⑦ 仍 ✓;t_prepush_gates_stop_on_signal 只數行數(n == 8),刪行會紅(我沒跑它),但換壞變數或拿掉 `|| tf_rc=$?` 不會。建議用只在 pp_touched_file 路徑殺 push-range 的包裝腳本(例如第一次呼叫殺、之後放行)單獨釘。

## F2 部分 diff 失敗時仍交出殘缺清單,與註解不符
severity: minor
blocking: 否 因為只在多 ref 同推且其中一個 git diff 失敗時才發生,失敗前就如此(原本是 `|| true`),不是這次新增的退步,只是新註解的承諾沒兌現。
file: `scripts/hooks/pre-push` pp_touched_file 尾端(diff 檔 348-362 行)
具體場景:同推兩個 ref,第一個 diff 有檔、第二個 `git diff` 失敗(逾時、物件讀不出)→ `_ok=0` 但 `-s "$_f"` 為真 → 交出只含第一個 ref 的清單,doctor 以它收窄,第二個 ref 碰到的檔不被擋。新註解寫「任何一個 diff 失敗 → 不交(doctor 照舊全擋)」,實際只在「全部都空」時成立。未能在本機造出 git diff 失敗的 ref,屬推論。
引句:「if [[ -s "$_f" || ( "$_n" -gt 0 && "$_ok" -eq 1 ) ]]; then printf '%s' "$_f"; else rm -f "$_f"; fi」
佐證:條件是 `-s || (n>0 && ok)`,沒有「ok=0 就不交」。把條件改成 `[[ "$_ok" -eq 1 && ( -s "$_f" || "$_n" -gt 0 ) ]]` 即與註解一致。

最高 minor,blocking 0 條
