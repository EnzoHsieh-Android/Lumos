severity: minor

**①提示注入**
已看,無。新增的寫入與讀取路徑,外來文字都有處理:
- 席名先對同輪帳上的 `--auditor` 比中,才寫進帳。
- 事件字串裡的 loop 與 auditor 都過 `_esc_clean`。
- `gov --stats` 印出的席名只會是已通過比對的字串,不會把自由文字送進派工詞或 hook 附加段。

**②讀寫與執行越界**
已看,無。
- 這份 diff 沒有新增 `subprocess`、`os.system` 或 shell 插值。
- 沒有新增下載來源,也沒有新的路徑寫檔。
- 全文 grep 沒找到真實密鑰或信箱。

**③非刻意、一步就能繞過的守衛**

severity: minor
blocking: 否
- 誰:使用者本人,或照常操作的 AI。
- 從哪:shell 裡殘留的 `LUMOS_FINDING_SEAT_SINCE`,例如沿用跑測試時的環境,或別的程序帶進來。
- 送什麼:照常的 `lumos canary record none --loop code-… --findings-set …` 載體記帳,不帶 `--finding-seat`。
- 拿到什麼:`--finding-seat` 必填這道守衛被意外走過,載體照樣入帳,沒有出處席位。
- 為什麼只算 minor:這個繞法不是靜默的,守衛會提醒並留紀錄。
  - 程式會在 stderr 印提醒,並留一筆 `finding-seat-since-overridden` 的 canary warned 事件。
  - `_finding_seat_required_block` 的 `return None` 仍放行,所以帳會被寫進去,缺 `finding_seats` 的列要事後才看得出來。
  - 事件如果寫不進去,`_gate_event_or_warn` 的行為這份 diff 看不出,我沒有去查。
引句:「不是刻意設的就 unset 它再記」

**③另一處已看,無**
`_finding_seat_since_key` 收到無法解析的環境值時,會退回常數,所以拼錯的環境值不會讓必填失效。

最嚴重等級 minor
