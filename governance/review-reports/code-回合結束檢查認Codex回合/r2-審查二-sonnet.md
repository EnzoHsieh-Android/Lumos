severity: minor

審查結論:沒有發現會做出錯行為或破壞合約的問題,只有一條測試覆蓋上的 minor。我沒有跑測試,以下都是讀 patch 與真代碼走執行路徑得出的。

**修補差異回歸(`_kept_start`)走查**
- 時刻為 0 或負數:`_turn_start` 對 `t<=0` 回 None,所以 `_kept_start(...) or time.time()` 會落到 `time.time()`。因為 `_turn_start` 只回正的有限浮點數,`or` 不會把合法值誤吞。
- 舊紀錄讀失敗、壞 JSON、深層巢狀、非物件、時刻不合法:都回 None,改寫成新時刻。這是當沒起點、重新開始,行為安全。
- 兩個會談交錯:`d / sid` 與寫入、`_on_stop` 讀取用同一個消毒後檔名,不會讀錯檔。
- Claude Code 下同一個 prompt_id 重送(假設會發生):起點保留原值,只會多查、不會漏查,方向安全。
- 沒有 prompt_id 也沒有 turn_id:`key` 是 None,`_kept_start` 直接回 None,行為跟改動前相同。

**角色鏡頭**
- be-api-compat:起點紀錄的鍵名 `prompt_id` 沒改,舊版寫的紀錄新鉤子讀得懂,新版寫的舊鉤子也讀得懂。
- be-authz:沒有端點,不適用。紀錄檔仍走 `_stop_dir_ok` 的信任目錄檢查。

**圖譜鏡頭**
- 固定席節點(測試假綠形態、授權與歸屬等)牽連檔都只是 `scripts/test_lumos.py`,這份 diff 沒碰任何 INVARIANT 的綁定測試,也沒動授權檔或白名單。
- `測試假綠形態` 的 INVARIANT 要求還原翻紅釘配前置斷言。⑤用 `t_first` 比對,先確認第一次寫入成功,有前置,沒破壞。
- 另外,`Systems/回合結束寫法檢查.md` 的 summary 與天花板說明跟程式一致。

1. 測試漏掉 `_on_prompt` 在起點紀錄被改壞時的行為,拿掉 `_kept_start` 的 RecursionError 接法測試照綠
   - 位置:`scripts/hooks/claude/stop-lint-hook.py:238` 與 `scripts/test_lumos.py` 的 `t_stop_lint_hook_codex_turn_id`。
   - 具體改壞:把 `_kept_start` 的 `except (OSError, ValueError, RecursionError)` 改成 `except (OSError, ValueError)`。再讓 `stop-turn/<會談>` 內容是深層巢狀 JSON,且送出提示帶任何 turn_id。這時 `json.loads` 的 RecursionError 會一路冒出到 `_on_prompt`。
   - 後果:紀錄不會被改寫成新起點,舊的壞紀錄留著,之後收工因 `rec` 不是 dict 而永遠印「沒記到起點」不檢查。這是靜默退化成不守衛。
   - 為什麼測試抓不到:⑤只測合法舊紀錄(同 key 保留、換 key 換新),沒有任何一步在送出提示前預先寫入壞紀錄、超大數字或 `t<=0` 的紀錄再送出提示。既有 `t_stop_lint_*` 的壞紀錄案例只打 Stop 端的 `_on_stop`,沒打送出提示端新加的 `_kept_start`。
   - 降級理由:`main` 外層有 `_guard`,最壞是靜默不檢查而非崩潰,而且只有手動改壞紀錄才走得到,所以是覆蓋可以更完整。
   - 引句:「    t = _kept_start(d / sid, key) or time.time()」
   - 佐證:`scripts/hooks/claude/stop-lint-hook.py:253`、`scripts/hooks/claude/stop-lint-hook.py:579`
   - 建議補一支:先寫 `{"prompt_id":"t-s","t":-1}` 或巢狀 JSON 的紀錄,再送同 turn_id 的送出提示,斷言紀錄被改寫成正的新時刻。
severity: minor
blocking: 否

總結:最高等級 minor,blocking 條數 0。
