severity: minor

我在 spec-gate-nondo 上實測了推送範圍很大的情況。下面是量到的數字和一條 finding。

實測結果:
- 用真實圖譜(870 篇筆記、342 份 Projects 計劃)對全部計劃各重判一次門,約 1.1 秒。
- 對全部計劃跑 `_spec_gate_push_nogo_only`,也約 1.1 秒。
- 讀一次真實審查帳(4.4MB)的 `_nogo_light_window`,約 50 毫秒。
- `_nogo_skipped_rows` 算一份快照,約 0.13 秒每 MB(2MB 快照 0.27 秒;單行 50 萬個「退款」0.24 秒)。這是線性的,沒有二次方爆炸。
- 測試程序的最大記憶體約 433MB,主要來自載入整個圖譜,不是這次修補造成的。

severity: minor
blocking: 否 — 只是推送前變慢,線性成長,單人依序操作的情境下可以接受,不會出錯或誤判
引句:「window, before = _nogo_light_window(env, loop_id)」
問題:每份「不做清單略過了危險詞、風險低」的計劃,都會把整本審查帳重讀一次,並對每一行做 `json.loads`。`_spec_gate_latest_records` 已經在 `_spec_gate_push_scan` 開頭讀過同一本帳一次,但那份結果沒有被重用。`_seat_ok` 還會對窗口裡的每一筆紀錄各重讀一次快照、重算一次被略過的行,而且同一份快照會被重複處理。
具體失敗情境:一次推送改到 150 份這類計劃,帳是 4.4MB,光讀帳就約 150 × 50 毫秒,也就是 7 到 8 秒。帳繼續長大,推送前檢查的時間就跟著線性變長。
另一個情境:某個編號在上次規格閘留痕之後累積 N 筆輕量審紀錄,且都綁同一份 2MB 快照。檢查會重複算快照最多 N × 0.27 秒。這種情況在輕量審正常使用時很少出現,只在審了很多次還沒過的時候才會。
佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9179` ``(`_nogo_light_window` 每次呼叫都讀整本帳),``file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9214` ``(每份計劃各呼叫一次),``file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9233` ``(`_seat_ok` 逐筆重算快照)。
建議:在 `_spec_gate_push_scan` 開頭把帳一次讀成「每個編號的窗口」,每份計劃查表。`_nogo_review_unbound` 對同一個 `snapshot_path` 的結果也可以快取。

已讀,無 finding:
- `_spec_gate_push_scan` 的 `idx` 三態(None、False、有值)。
- `_spec_gate_touched_plans`。
- 超深巢狀行的 `RecursionError` 處理。
- `_light_gate_fails` 新增的型別檢查。
- `_nogo_light_cmd` 的 shell 引號。

測試時我把寫治理帳的函式換成空函式,沒有動到 repo。暫存目錄已刪。

最高等級 minor,blocking 0 條。
