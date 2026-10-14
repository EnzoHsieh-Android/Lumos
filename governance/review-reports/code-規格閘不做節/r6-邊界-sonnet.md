severity: minor

這輪修補的邊界大致守住。我發現一條 minor:圍欄開頭那一行本身不被掃。我另外用破壞測試驗過,新增的測試能抓到把判斷改壞。實驗用的暫存目錄與 gctl 現場都已刪。

severity: minor
blocking: 否 — 只是留一個小盲區,危險詞要放在圍欄開頭那一行才繞得過,而且該行與內容本身是作者自己寫的
引句:「_visible_lines(text.splitlines(), keep_fenced=_DOOR_SCAN_FENCED)」
問題:`keep_fenced=True` 只保留圍欄內部的行,圍欄標記行(開頭那行 ```、~~~ 加語言標記)本身仍被 `_visible_lines` 跳過。
具體失敗情境:實測 ``` ```退款\nx\n``` ```(危險詞緊貼在開頭標記後)和單行 ``` ```退款``` ``` 都回 hits=[],判風險低。圍欄內容裡的詞才會翻高,標記行上的詞不會。標記行上也不是自然會寫正文的位置,所以只算 minor。
佐證:``file: `scripts/lumos:4935` ``(`_visible_lines` 的 is_marker 分支 `continue`)。

severity: minor
blocking: 否 — 席名自報本來就是天花板(計劃 d1),方向偏安全
引句:「return "架構對齊" in s or "arch" in s」
問題:`_nogo_is_arch_seat` 用 `nfc` 加 `lower`,沒有做全形折疊(NFKC)。
具體失敗情境:實測 `ａｒｃｈ` 回 False(全形),`大架構席` 也回 False(沒寫「對齊」)。這類席名會被當成通才席,可單獨放行輕量審。反方向的誤判(Research、March、Monarch、archive、Search-Arch 都回 True)只會多擋,是計劃自己承認的取捨。

已讀,無 finding 的部分:
- 圍欄的其他邊界:四個反引號、縮排圍欄、波浪號、沒閉合的圍欄、不做節裡的圍欄,都判到風險高,不做清單的略過行號沒有錯位。
- 路徑邊界:`_same_file_path` 在 NUL、兩邊都不存在、符號連結三種情況下行為合理。`_prov_check` 的 ValueError 也接住了。
- 計劃改名後,迴圈編號跟著變,舊帳不會誤綁,只會走「沒有輕量審」的擋法,合理。
- `_sh_quote` 用 shlex 包好。唯一會漏的是計劃檔名以 `-` 開頭時,shlex 不加引號,輸出可能被當成選項,極小。
- 測試有咬到行為。清 `__pycache__` 後做了四個破壞:
  - 把 `_DOOR_SCAN_FENCED` 改成 False,`-k fenced_keywords_count` 4 支紅。
  - 拿掉 `arch` 判斷,`-k arch_seat_names` 5 支紅。
  - 讓 `samefile` 一律丟例外,`-k nogo_light_bad_paths` 1 支紅。
  - 把 `_prov_check` 的 ValueError 拿掉,同一組 2 支紅。

最高等級 minor,blocking 0 條。
