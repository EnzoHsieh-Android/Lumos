severity: minor

整體判斷:誠實流程(輕量審乾淨就放行;抓到 major 就開 `-std` 走完整設計審)仍走得通。我讀了程式,並在實驗環境用 `importlib` 載入 `scripts/lumos` 跑了探針,沒有在 spec-gate-nondo 寫帳。

**Finding**

severity: minor
blocking: 否 — 只對刻意夾控制字元的人有效,威脅模型是單人自填,而且影響僅限「略過的危險詞是否被擋」
引句:「它跟一般空白一樣是看得見的分隔,「pay ment」本來就比不到,是已知天花板,不是這支要管的。」
問題:`_is_invisible` 一律把 `str.isspace()` 為真的字元當成「看得見的空白」,不刪。但 `\x1f`(Unit Separator)被 Python 判成空白,實際上是 Cc 控制字元。多數編輯器和終端機畫成零寬或一個小方框,不是一個空隙。`\x1f` 也不在 `splitlines` 的切行集合裡,所以不會被切成兩行。「看不見的字元」這一族前面已被打穿四次,這是同一族的第五個入口。
具體失敗情境:計劃裡寫 `- 實作 pay\x1fment 流程`,輸入後 `_door_keyword_hits` 回 `[]`,同樣內容寫 `payment` 會命中「金流」。`退\x1f款` 同樣漏掉。危險詞被略過卻不算進風險,門判成風險低。
佐證:``scripts/lumos: `_is_invisible` 開頭的 `if ch.isspace(): return False` 與 `_ASCII_INVISIBLE`(用 `not chr(c).isspace()` 排除)``。實測 `'\x1f'.isspace()` 為 True,而 `'a\x1fb'.splitlines()` 回 `['a\x1fb']`。
補救方向:ASCII 與 Unicode 的 Cc 一律刪,只保留真正會換行或留出明顯間隔的空白(`\t`、`\n`、`\r`、`\x0b`、`\x0c`、一般空白、NBSP、全形空白)。`\x1c`、`\x1d`、`\x1e`、`\x85`、`\u2028` 會被 `splitlines` 切成兩行,不是漏洞。

**逐項檢查結果**

- **先刪、NFKC、再刪**:已讀,無 finding。我跑了這些輸入:
  - 全形 `ｐａｙｍｅｎｔ` 折成 `payment`。
  - `pay\u0301ment`、`pa\u0308yment` 得到 `payment`。
  - 夾 `\u200b`、`\u2800`、`\x01`、`\ue000`、tag 字元的詞都能折回。
  - 日文濁點、半形濁點(`\uff9e` 經 NFKC 變 `\u3099` 再被第二次刪)正常。
  - 全部 Unicode 碼位掃一遍:被判看不見的字元,NFKC 後沒有任何一個變出可見的字母或數字,所以沒有「刪掉反而漏命中」的路徑。
  - 漢字區(U+4E00–9FFF)沒有被判看不見的字元。
  - 中文詞不受影響。Mn 整類被刪只影響其他文字的組合寫法,以及搜尋字對回退裡的組合寫法;計劃已把這點寫進天花板。
  - 效能:38 萬字約 0.19 秒。
- **壞行 fail-closed(出路與訊息)**:已讀,無 finding。
  - `ctx["bad"]` 是整本 `.canary-log.jsonl` 的壞行,不分迴圈。舊帳裡一行壞行(例如寫到一半被中斷的行)會讓所有走 (b) 的 `-std` 都被擋。
  - 這跟 `loop status --disposal` 是同一個行為。擋下訊息帶「修好或搬走壞行再問」和壞行行號,而且 `_nogo_full_review_gate` 在帳上沒有該 `-std` 紀錄時先回 `""`,所以不會誤擋還沒開 `-std` 的人。
  - (a) 輕量審仍然跳過壞行,與 `loop status --light` 一致,不算新問題。
  - 本 repo 的帳實測 0 行壞行。
- **`-std` 完整設計審的形狀檢查**:已讀,無 finding。
  - `_nogo_full_review_shape` 要求每筆有輪次字串,分級只看有帶 `tier` 的那幾筆,且必須是 standard 或 high。`canary record` 與 `loop next` 的 `--tier` 本來就只有 light、standard、high 三種。
  - 一般設計審的紀錄帶輪次、不是每筆都帶 `tier`,不會被誤擋。
- **`gov` 傳遞**:已讀,無 finding。`_cap_retro_status` 收到的事件會再照編號篩;`gov` 讀失敗時不快取,下一份計劃會重讀。
- **`_ledger_physical_lines` 改用 bytearray**:已讀,無 finding。`scan` 與 `pos` 的換算,以及區塊結尾剛好是 `\r` 的情況,邏輯正確。
- **`_under_root`(`_cap_retro_check`、`cmd_impact`)**:已讀,無 finding。語意與原本的 `os.path.isabs` 拼法相同,包括 `root` 為 `None` 時照原路徑。
- **釘版**:已讀,無 finding。`t_door_scan_logic_version_pin` 現在涵蓋 `_strip_zero_width`、`_is_invisible`、`_pq_is_default_ignorable`,再加類別集合、預設可忽略全表(`_PQ_DICP_RANGES`)、空白圖形,改了會紅。
- **門規則版本 8 對既有風險低留痕**:已讀,無 finding。推送前會用現行規則重判門。新規則下才浮現的略過詞會改變條款區塊指紋,要重跑 spec-gate;擋下訊息也補了版本 8 的例子。「未指派」這類判斷跟執行的 Python 版本走,專案已規定最低 3.14,不構成問題。
- **資料狀態五問**:已讀,無 finding。
  - 空帳:`rows` 為空時回 `""`,只講怎麼開 `-std`。
  - 單筆帳:被形狀檢查擋下,並指向範本。
  - 壞行:fail-closed 並帶行號。
  - 多份計劃共用 `gov`:只讀一次,不跨計劃污染。
  - 舊版本留痕:會提示重審。

最高等級 minor,blocking 0 條。
