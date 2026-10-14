severity: major

第八輪修補的 finding 有 3 條:1 條 major(門掃漏零寬以外的隱形字元),2 條 minor(NFD 編號走不通 -std 出口、測試沒釘 NFC 這一行)。實驗都在 scratchpad 的複本上做,工作樹沒動,做完已刪。

severity: major
blocking: 是 — 隱形字元修補只補了零寬空白一族,同一類繞過(r7 邊2)換個字元就過,門判成風險低就不派設計審
引句:「再拿掉零寬字元(共用 _strip_zero_width;」
問題:`_door_scan_text` 是 NFKC 加 `_strip_zero_width`。後者只刪 U+200B–U+200F 和 U+FEFF。NFKC 不會處理軟連字號 U+00AD、字連接符 U+2060、變體選擇符 U+FE0F、U+034F、U+180E、雙向控制字元 U+202C、U+2061、韓文填充字元 U+3164 和 U+115F 這些隱形字元。
具體失敗情境:我對 `_door_keyword_hits` 實測,下列寫法全部回空:
- `退\u2060款`
- `pay\u00adment`(從網頁複製的軟連字號斷字,是常見的無心來源)
- `退\u00ad款`
- `re\u034ffund`
- `退\ufe0f款`
- `pay\u180ement`
- `pay\u202cment`

只有 `退\u200b款` 和全形 `ｐａｙｍｅｎｔ` 會命中。
這些計劃會被判風險低:不走多席設計審;寫在「## 不做」節裡的也不會被記成略過,連輕量審都不用。
`_strip_zero_width` 同時被搜尋排序共用(`_RANK_CJK_RE` 那條路)。要補就得為門掃另寫一份,或改用 `unicodedata.category` 為 Cf 或 Mn 的字元一併刪。
佐證:``scripts/lumos: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:5000` ``(`_strip_zero_width`)、``scripts/lumos: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:8078` ``(`_door_scan_text`)

severity: minor
blocking: 否 — 失敗方向是多擋,不會漏放;只在計劃檔名本身是 NFD 時出現
引句:「std_id = loop_id + "-std"」
問題:`_nogo_std_gate` 用 NFC 的 `std_id` 查 `by_loop`(這張表按 NFC 分組),所以帳上的列找得到。但它接著呼叫 `cmd_loop_status(env, std_id, …)`,後者用原字串比對 `d.get("loop") == loop_id`。帳是用 NFD 編號記的時候,處置閘看到零筆紀錄。
具體失敗情境:計劃檔名是 NFD(例如 `café_計劃.md`),照 `_nogo_light_cmd` 印的指令用 NFD 的 `café-std` 記一輪乾淨的完整設計審。我實測推送前仍被擋,訊息是「café-std 的處置閘沒過(無記錄…)」。同樣的流程改用 NFC 的計劃名和 NFC 記帳就放行。
使用者照訊息操作不會成功,因為訊息裡印的編號和他記的編號長得一樣,只差正規化。這跟作者承認的「NFD 寫法判沒有紀錄」是同一件事,但現在會卡死在 -std 出口,沒有可照做的修法。修法是 `cmd_loop_status` 的比對也走 NFC,或 `_nogo_std_gate` 給它實際記帳用的原寫法。
佐證:``scripts/lumos: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9380` ``(組 `std_id`)、``scripts/lumos: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:13459` ``(`cmd_loop_status` 內 `d.get("loop") == loop_id`,行號約略)

severity: minor
blocking: 否 — 測試缺口,不是程式行為錯誤
引句:「loop_id = nfc(_loop_id_for_plan(prel))」
問題:我把這行的 `nfc(...)` 拿掉(破壞實驗),跑 `-k prepush_nogo`,結果 138 passed、0 failed。沒有任何測試涵蓋「NFC 與 NFD 的編號走 -std 出口」。`t_prepush_nogo_light_nfc_loop` 只測 light 路徑。上一條的缺陷也因此沒被測試抓到。
對照:拿掉 `_door_scan_text` 的 NFKC,`t_spec_gate_door_nfkc_zero_width` 會紅。拿掉 `_nogo_line_key` 的 NFC,`t_nogo_line_key_normalized` 會紅。這兩處釘得住。

已讀,無 finding:
- 計劃名本身以 `-std` 結尾(`foo-std_計劃`)。`foo` 的 -std 編號會與它撞,但 `_nogo_std_gate` 會檢查 `spec_path` 是否為這份計劃,撞到會擋下,沒有放行的路徑。
- 全形英數、羅馬數字、上標經 NFKC 後誤中危險詞:我掃過所有 NFKC 會變形的單一碼點,對四類詞庫的新增命中是 0。唯一的誤判形狀是 `ⅮROP TABLE` 這類刻意寫法,算正確的折疊。
- `_nogo_line_key` 回到「NFC 加去空白」是自洽的。快照與現況用同一函式算,詞是折過之後的寫法但兩邊一致。
- `_under_root` 的說明與行為相符。
- 行雜湊用原文、比對用折過的文字,兩邊沒有互相打架。

最高等級 major,blocking 1 條。
