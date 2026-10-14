severity: minor

實驗用 `/bin/bash` 3.2、假 `PY`(用 `sleep` 模擬各片)和掛鉤原樣的陷阱與 `run_group`,沒跑真的全套測試。實驗目錄已刪,沒有留下孤兒行程。

已讀,無 finding:
- 對掛鉤 pid 送 TERM、對掛鉤 pid 送 INT、對整個行程群組送 INT、對整個行程群組送 TERM,四種情況掛鉤都分別以 143、130、130、143 結束,8 片全部被收掉,`$_PP_TMP` 被清。
- 各片繼承忽略 SIGINT 時,各片自己收不到 INT,但掛鉤 INT 陷阱送 TERM 給子殼、子殼再送 TERM 給各片,這條路成立。
- 子殼的 TERM 陷阱沒有誤跑父層的 EXIT 陷阱。
- 各片正在寫 log 時被收:各片被殺,log 檔留在 `$_PP_TMP` 內,隨 EXIT 一起清,沒有殘檔。
- 補丁新增的 `{ …; } 2>/dev/null`、`tee` 加 `2>/dev/null` 和 `grep … 2>/dev/null`,都沒有訊號或資源面的問題。

severity: minor
blocking: 否 — 只在 TERM 恰好落在極短的空窗時漏掉一片,各片最多自己跑完,不影響擋推送的判定。
引句:「trap 'kill ${_pids[@]+"${_pids[@]}"} 2>/dev/null; exit 143' TERM」
問題:`run_group` 裡每片是先 `&` 起、下一個敘述才 `_pids+=($!)`。TERM 的陷阱在兩個敘述之間執行時,剛起的那一片還不在 `_pids` 裡,不會被收。
具體失敗情境:對掛鉤送 TERM,時間點在掛鉤啟動後 10 到 50 毫秒內隨機,重複 120 次,有 1 次留下 1 個孤兒片,在我手動殺掉前一直活著。
修法:`&` 之後馬上記 pid 無法消除空窗。改成子殼 TERM 陷阱用 `jobs -p` 收,或在陷阱裡 `kill 0` 搭配子殼自己忽略 TERM,可以不依賴 `_pids`。
佐證:``file: `scripts/hooks/pre-push:808` ``、``file: `scripts/hooks/pre-push:817` ``

severity: minor
blocking: 否 — 只影響單獨被送 SIGHUP 的情況;終端機掛斷時整個群組都會收到 HUP,各片多半會跟著死。
引句:「trap '_pp_kill_jobs; exit 143' TERM」
問題:掛鉤只接 INT 和 TERM,沒有接 HUP。對掛鉤 pid 單獨送 HUP,掛鉤死了,EXIT 陷阱照跑、`$_PP_TMP` 被刪,但兩個子殼和 8 片全部繼續活著(8/8),輸出寫進已刪的目錄。這正是補丁想堵的孤兒情境,只是換了訊號。
具體失敗情境:ssh 或編輯器只對掛鉤行程送 HUP(沒送整個群組)時,各片會跑到底,最久約八分鐘。
修法:INT、TERM 之外再加一行 `trap '_pp_kill_jobs; exit 129' HUP`,子殼那層也同樣接 HUP。
佐證:``file: `scripts/hooks/pre-push:304` ``、``file: `scripts/hooks/pre-push:305` ``

severity: minor
blocking: 否 — 這是推測,沒有跑真的 `test_lumos.py`,而且屬於測試本身的資源,不是掛鉤補丁的缺口。
引句:「子殼收到 TERM 就把各片收掉再結束。」
問題:補丁只送 TERM 給各片的 python 行程本身。我 grep 過 `scripts/test_lumos.py`:沒有 TERM 的處理,也沒有收尾清理。它有三處用 `start_new_session=True` 起子行程(約 10421、10438、10502 行),那些子行程在別的 session,收不到掛鉤送的 TERM。測試留下的 `gctl-run-*` 等暫存也不會被清。
具體失敗情境:中斷時正在跑的那些子行程要等自己逾時(程式裡寫 60 秒),暫存目錄會累積,和全域的暫存清理規則衝突。
修法:`test_lumos.py` 裝 SIGTERM 處理器收掉自己起的子行程並刪暫存;或掛鉤用 `kill -- -pgid` 收整組。
佐證:``file: `scripts/test_lumos.py:10421` ``

最高等級 minor,blocking 0 條。
