severity: minor

我在 spec-gate-nondo 這份程式上做了合成大帳實測,實驗目錄已刪。推送前檢查的耗時和記憶體都在可接受範圍,只有下面三條 minor。

### Finding 1
severity: minor
blocking: 否 — 只多佔暫時記憶體,單人單次推送不會超時或耗盡
引句:「by.setdefault(nfc(str(d["loop"])), []).append(d)」
問題:`_spec_gate_ledger_index` 把整本審查帳每一筆解析後的 dict 全留在記憶體。舊的 `_spec_gate_latest_records` 邊讀邊丟,只留每個迴圈最後一筆規格閘留痕。
失敗情境:我造了 5 萬筆、47.6MB 的帳(每筆帶 600 字備註)。讀進來後峰值 RSS 從 33MB 升到約 298MB,建表耗時 0.41 秒。帳長到數十萬筆、數百 MB 時,峰值會升到 GB 級。時間上沒問題,只是記憶體是「整本帳 × 約 5.5 倍」,而且推送前每次都付,即使沒有任何計劃用到輕量審。
佐證:``scripts/lumos:9225``

### Finding 2
severity: minor
blocking: 否 — 要靠很多筆 major 加上各自不同的快照才會慢,一般計劃不會碰到
引句:「or _nogo_review_unbound(env, prel, r, nogo_skipped, ctx) is None:」
問題:`_nogo_major_carried` 會掃整個迴圈所有抓到 major 的紀錄。只要一筆的 `nogo_rows_sha` 不等於現在的值,它就逐筆走 `_nogo_review_unbound`。每份「不同」的快照要讀兩次(`_prov_check` 算雜湊一次,`read_bytes` 再一次),再整份重算被略過的行。`ctx["snap"]` 只在同一次推送內有效,下次推送從零開始。所謂「同一份快照只讀一次」,其實是每份不同快照讀兩次。
失敗情境:我實測一份 2000 行的計劃,3000 筆 major、各自帶不同快照,`_nogo_major_carried` 耗時 24.4 秒(約 8ms/份)。同一份快照重複 2 萬筆則只要 1.9 秒。每個 major 輪次多留一份快照。如果計劃被改過很多版,而且每一版都有 major,每次推送的成本是「major 輪數 × 快照大小」,並且乘上本次推送碰到的、有被略過危險詞的計劃數。沒有上限,也不會因為窗口重開而減少。這是這輪「整本帳當窗口」的直接代價。
佐證:``scripts/lumos:9258``

### Finding 3
severity: minor
blocking: 否 — 要審查帳讀不到才發生,威脅模型外;但它是修補新造成的行為改變
引句:「return {"by_loop": {}, "err": e, "snap": {}}」
問題:`_nogo_ctx` 吞掉讀帳的 OSError,把空表交給 `_spec_gate_latest_records(env, ctx["by_loop"])`。空表不是 None,所以不會重讀帳。每份計劃的 `latest.get(...)` 都回 None,於是 `full` 判為假。沒有被推送範圍碰到的 doing 風險低計劃,會被靜默略過整套檢查(留痕過期判斷和測試真跑),不印任何訊息。
失敗情境:帳檔權限壞掉或被換成目錄,`.canary-log.jsonl` 讀不到。修補前這個 OSError 會直接讓檢查崩掉(擋下)。修補後,範圍碰到的計劃才會講「審查帳讀不到」,其餘計劃的測試閘安靜放行。
佐證:``scripts/lumos:9164``、``scripts/lumos:9399-9418``

### 已讀,無 finding
- `_nogo_snapshot_rows` 的快取鍵與負面結果快取。
- `_same_file_path` 的 `samefile` 呼叫,每筆只是兩次 stat;`_vault_repo_root` 也只是 stat,不起子行程。我實測 2 萬筆每筆走一次都只要 1.9 秒。
- `_nogo_light_window` 和 `_seat_ok`:窗口掃描是線性的,`any` 會短路。
- `_light_gate_fails`:只判最後一筆,計劃只讀一次。
- 帳的讀取次數:推送前檢查開頭讀一次,`_spec_gate_push_scan` 內之後都查表。另一個沒走表的讀者在 `scripts/lumos:3222`,不在推送前路徑上。
- 門的關鍵字掃描加圍欄(`_DOOR_SCAN_FENCED`):多掃行數而已,沒有新的子行程或讀檔。
- 這輪沒有新增子行程,git 環境變數調整也不影響資源。

最高等級 minor,blocking 0 條。
