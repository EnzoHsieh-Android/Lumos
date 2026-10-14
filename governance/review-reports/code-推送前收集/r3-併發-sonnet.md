severity: minor

我用模擬腳本(`/bin/bash` 3.2.57,結構照抄掛鉤:主殼加 `( run_group ) &` 子殼,子殼裡 4 個 `&` 片,四個 trap 與 `_pp_kill_jobs` 都照抄)實測。沒有跑真正的 `pre-push`,也沒有用真正的 `test_lumos.py`。實驗目錄和殘留行程都已清掉,最後 `ps` 沒有 `sleep 77` 或 `sim.sh` 殘留。

已讀,無 finding 的部分:
- `jobs -p` 在子殼的 `$(...)` 裡看得到那個子殼自己起的 4 片,在主殼看得到兩個子殼。兩處都實測過。
- 在計時空窗之外,TERM、HUP、INT、INT+HUP、HUP+INT、HUP+TERM、INT+TERM、TERM+TERM 各種組合,離開碼都對(143、129、130),沒有 hang,各片都收乾淨。
- 陷阱裡又收到訊號(TERM 後 1ms 再 TERM、INT 後再 TERM)沒有死鎖,也沒有卡住。
- `_pids` 現在只拿來 `wait`,從 `for _p in "${_pids[@]}"` 的 `wait` 迴圈看不出新問題。
- 純 INT 若用背景方式送(非互動 shell 的 `&` 會讓 INT 被忽略)收不到,這是我的測試方式造成的,不是掛鉤的問題。前景 Ctrl-C 的路徑用 Python 以預設 INT 處理的方式起程序後送 INT,實測正常。

severity: minor
blocking: 否 — 只發生在訊號剛好落在起片後約 5 到 8ms 的窗口,留下的孤兒最多跑幾分鐘,單人使用下機率極低,也不會影響推送結果
引句:「自己記的話,「& 起片」與「記下 pid」是兩個敘述,訊號落在中間時剛起的那片不在清單上、漏收。」
問題:修補宣稱改用 `jobs -p` 後這個空窗就關上了,但實測沒有完全關上。我讓模擬掛鉤在啟動後 4.5 到 11ms 內收到 TERM,250 次裡有 6 次留下孤兒。其中 5 次是單一片 `sleep 77` 的 ppid=1,子殼已死。另 1 次是整個子殼加 4 片都存活,ppid=1,離開碼 143,只有主殼死了。HUP 在 150 次裡也有 1 次單片孤兒。
具體失敗情境:使用者或 ssh 的訊號落在測試剛起的那幾毫秒,主殼 `exit 143` 後 EXIT 陷阱刪掉暫存目錄,漏掉的片繼續在背景跑,log 寫進已刪的資料夾。推測原因有兩個,我沒有逐一證實。一是訊號在子殼剛 fork 完、還沒重設 trap 的瞬間被吞掉。二是訊號落在 `&` 起片與工作表登記之間。工作表登記的時機,我推測是 bash 3.2 內部行為,同樣未證實。
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:842`、`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:814`

severity: minor
blocking: 否 — 被殺的是 python 片本身,測試自己起的短命子行程(git、子行程)通常很快結束,不會長期占資源
引句:「子殼收到 TERM 或 HUP 就把各片收掉再結束。」
問題:`_pp_kill_jobs` 只對 `jobs -p` 的直接子行程送 TERM。我讓每片自己再起一個 `sleep 77` 當測試子行程,片被收掉後,這個孫行程變成 ppid=1 的孤兒。TERM 和 HUP 各測一次,8 片全部留下孫行程。上一輪第三點「測試自己起的子行程」這個修補沒有處理。
具體失敗情境:收片當下,若某個測試正在跑長一點的子行程(像是 `test_lumos.py` 裡 `start_new_session=True` 的 pre-commit 或 bootstrap 模擬),該子行程在片死後繼續跑到自己結束或逾時。
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:303`、`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/test_lumos.py:10421`

最高等級 minor,blocking 0 條。
