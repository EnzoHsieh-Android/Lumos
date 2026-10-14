severity: major

審查範圍是 `scripts/lumos` 的修補段。我讀了程式、對照 `a132aa6e..7cb71dc5`,另外做了兩個小實驗:`_ledger_physical_lines` 隨機切塊比對,以及 `_strip_zero_width` 實跑。

## finding 1

severity: major
blocking: 是 — 危險詞夾一個沒被列到的隱形字元,關鍵字比對就看不到,整個門與不做清單的外層看門都被繞過。這是「危險詞夾隱形字元就判風險低」同一族,已是第四次被換字元打穿。
引句:「另加不歸 Cf 但一樣看不見的:變體選擇符 U+FE00–FE0F 與 U+E0100–E01EF、組合字形連接符 U+034F、韓文填充字 U+115F、U+1160、U+3164、U+FFA0」

問題:r9 的補法是 Cf 全類加一張手列的補充表(`_INVISIBLE_EXTRA`),本質仍是補字表。表外還有看不見但不屬 Cf 的字元:
- U+180B、U+180C、U+180D、U+180F:蒙古文自由變體選擇符,類別 Mn。
- U+17B4、U+17B5:高棉文固有母音,類別 Mn。
- U+2800:盲文空白,類別 So。
- 注意 U+180E 是 Cf 所以有處理,同族的 180B–180D 反而漏了。

失敗情境:計劃正文(不論是否在不做清單)寫 `退` + U+180B + `款`。
- 輸入:這一行經 NFKC 後,`_strip_zero_width` 實測回傳 `'退᠋款'`,隱形字元還在。
- 錯誤結果:`_door_scan_text` 比不到「退款」,四類關鍵字沒命中,門判風險低。
- 對照:同樣位置放 U+200B 或 U+FE0F 就會被拿掉並命中。

佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:5018`

建議:不要再補表。比對前改成「只留可見字元的白名單形狀」,或把 Mn/Me/Cf/Zs 以及 So 裡的盲文空白整類在比對用字串裡拿掉(只用在比對、不改行雜湊)。

## finding 2

severity: minor
blocking: 否 — 推送前比 `loop status --disposal` 寬鬆,但沒有系統性繞過路徑,且 (a) 本來就這樣接。
引句:「讀帳讀不懂的行在索引那一頭就跳過(跟 (a) 同一個接法,ctx["skipped"] 記行數)。」

問題:讀不懂的行在三處的處理不一致。
- `loop status --disposal` 與 `loop next` 讀整本帳,任何壞行都傳進 `_disposal_judge(bad_linenos=…)`,處置閘 fail-closed 回 rc2。
- 推送前 (b) 呼叫 `_disposal_judge` 時沒傳 `bad_linenos`,預設是空元組,壞行只在失敗訊息裡多印一句「已跳過」。
- 這是行為退步:舊版 (b) 是直接叫 `cmd_loop_status`,壞行會 fail-closed。

失敗情境:`-std` 最後一輪的 major 那一列因寫入中斷成為半截 JSON。
- 輸入:壞行被跳過,剩下的列看起來是乾淨收斂。
- 錯誤結果:`loop status X-std --disposal` 回 rc2,但推送前放行。兩者對同一本帳結論相反。

佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9437`

建議:至少在索引中屬於這個編號的壞行(或整本壞行數 > 0)時,(b) 也 fail-closed,或把訊息講成「`loop status` 會擋、這裡放行」。

## finding 3

severity: minor
blocking: 否 — 只在單行異常巨大的帳才發作,正常帳是線性的。
引句:「不靠 `for chunk in f`(二進位檔迭代只認 \\n,整本純 \\r 行尾的帳會變成一塊整本讀進來;代碼審 code-規格閘不做節 r8 併2、合4)。」

問題:`_ledger_physical_lines` 用 `buf += blk`。一行跨很多塊時每塊都複製整個 buf,耗時是平方級。
- 實測單行 20MB 約 0.63 秒,80MB 約 15.4 秒。
- 舊的 `for chunk in f` 對單行是線性。
- 隨機切塊的正確性我另外驗過(塊大小 1、2、3、4、7,行號、行內容、位元組起點都與 `_ledger_lines` 一致),切行邏輯沒問題。

失敗情境:帳裡有一行幾十 MB(被貼進一整份 patch 的備註)。
- 輸入:這一行的讀取要幾十秒。
- 錯誤結果:推送前檢查、`loop next`、`loop status` 都跟著卡住。

佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:13900`

建議:用 `bytearray` 累積,或把跨塊的片段放進 list 最後再 `join`。

## 已讀,無 finding

- **`_disposal_judge` 抽出**:`loop status --disposal` 的順序沒變(roster 觀測、互斥檢查、`--spec` 必填仍在 `cmd_loop_status` 前段)。`loop next` 在 `spec is None` 時早已回 gate-pending,不會把 spec 缺失帶進處置閘。兩處的標準輸出與 rc 邏輯我讀下來是逐字等價的。
  - 唯一有意的差異是不是物件的行與超深巢狀行現在算壞行,以前會帶堆疊崩。
  - `cmd_loop_status` 刪掉函式內的 `import json` 無影響,函式內沒用到 json。
- **`g3_sha_override`**:
  - 它讓第一步 G3 的「窗末 result 等於現在的檔」恆成立。
  - 審完又改了被略過行以外的內容時,綁定靠 `_nogo_review_unbound`(快照雜湊、`reviewed_sha256` 等於快照、被略過行集合相等)。
  - 這跟 (a) 同一個天花板,是計劃明寫接受的設計,我沒當成 bug。
  - 若在被略過行或其上下文結構上動手,`nogo_skipped` 會變,仍被擋。
  - 誠實流程(乾淨輕量審放行、major 開 `-std`、完整設計審過處置閘、實作後寫回 status/lands_in)我讀下來走得通。
- **`_under_root` 六處收斂**:六處和原寫法等價,唯一差異是 `root=None` 時從崩潰變成回相對路徑,無害。
- **`_spec_gate_full_row` 與 NFC 分組**:行為合理。邊角是計劃檔名本身以 `code-` 開頭時列會被裁欄位,機率極低,不另列。

資料狀態五問,兩處有小缺口:
1. 帳不存在或空:回 `{}` 或 `""`,通過。
2. 壞行與非 UTF-8:壞行見 finding 2,非 UTF-8 的位元組位置換算我讀下來正確。
3. 舊版留痕與規則版本:`door_rule` 較舊、較新的訊息分支存在。
4. 同一檔被併發追加:最後一行半截會成壞行,等同 finding 2。
5. 大輸入:見 finding 3。

最高等級 major,blocking 1 條。
