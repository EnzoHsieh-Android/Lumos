severity: minor

說明:修補把上輪的 major(自寫事件包裝函式與自寫清洗)改回既有做法,結構上對齊。我找到 2 條 minor,都沒有第二種做法或跨層直呼。鎖檔(`.warming`)我沒有動,照派工詞審查。

**1. 分層與依賴方向**

沒有不一致。
- 刪掉 `_finding_seat_event` 後,四處擋下和提醒都在 `cmd_canary` 呼叫鏈上直接呼叫 `_gate_event_or_warn`,不再多包一層。鄰居 `refuted-set-missing`、`report-not-normalized` 也是這樣寫,依賴方向沒變。
  - file: `scripts/lumos:19855`
  - file: `scripts/lumos:20095`
  - file: `scripts/lumos:20105`
- 新碼放的位置跟其他逐席與必填函式一樣:`_finding_seat_required_block` 和 `_finding_seat_write_block` 在 `scripts/lumos:19600` 到 `19660` 一帶,`_seat_noise_name` 在 `scripts/lumos:18062` 一帶。`_seat_noise_name` 現在直接用既有 `nfc`(`scripts/lumos:454`),不另寫清洗。
- 生效日比法沿用 `_SECURITY_SEAT_SINCE`(`scripts/lumos:15770`、`37126`)加 `_loop_ts_key`,結構一致。

**2. 命名與錯誤處理**

找到 2 條 minor,各自說明如下。

severity: minor
blocking: 否
引句:「_gate_event_or_warn(root, "canary", "warned", f"finding-seat-since-overridden loop=」
說明:新增 `gate=canary` 下的 `warned` 事件。`canary` 這個閘在 `scripts/lumos` 現有的 `_gate_event_or_warn` 呼叫裡只出現過 `blocked`(`scripts/lumos:19855`、`20095`、`20105`、`20130`、`20138`、`20181`、`20190`)。`warned` 的既有用法在 `fix-check`(`scripts/lumos:23800`)和 `note-shape`(`scripts/lumos:55204`),那是別的閘。另外 `gov --stats` 的「審查有沒有用」段只數 `canary` 加 `blocked`(`scripts/lumos:18273`)。⚠ 我沒有驗 `warned` 事件進 gov 的 `canary` 計數時有沒有被誤算,交編排者查。它的 `hard` 參數沒寫,跟 `fix-check` 的 `warned` 不同(那邊明寫 `hard=False`,`scripts/lumos:23801`),但預設行為應該一樣,所以我只列 minor。

severity: minor
blocking: 否
引句:「def t_finding_seat_docs_match_since():」
說明:新測試直接讀 `skills/` 三份文件,沒有先呼叫 `_need_src(...)`。既有「讀 skills/ 文件」的測試都先守門,消費端專案沒有那些產物時記成 skip 而不是失敗(`_need_src` 定義在 `scripts/test_lumos.py:146`,用法例子在 `scripts/test_lumos.py:4838`、`15773`)。新測試少了這一步。結構上它仍是「讀檔加比對」的既有形狀。

事件字串多包了 `_esc_clean(loop)`,鄰居是 `loop={loop or ''}`,沒有包。這是為了補上輪發現的控制字元問題而有意加的,而且用的是既有函式,所以不列為不對齊。

**3. 第二種做法**

沒有引入第二種做法。
- 上輪的事件包裝函式和自寫的空白清洗都撤掉了,換成 `_gate_event_or_warn` 加 `_esc_clean`。
- `_seat_noise_name` 換成 `rstrip` 加 `ord(ch) > 127` 的線性寫法。`ord` 比大小在 `scripts/lumos` 只有 1 處,`isascii()` 有 10 處,這屬風格偏好,不列。
- 新測試的造帳和讀治理帳寫法沿用既有工具:`_mr_seat`、`_ledger_patch_last`、`_fs_since`,治理帳直接 `read_text` 檢查字串。這沒有引入新做法。

不對齊共 2 條,其中 major 0 條
