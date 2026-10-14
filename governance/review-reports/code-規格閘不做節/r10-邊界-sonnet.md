severity: major

我沒動 spec-gate-nondo,實驗都在複本上做。實驗目錄已刪。

**範圍**:修補差異(`/tmp/code-規格閘不做節-r10-repair.patch`)裡我有讀的部分是 `_is_invisible`、`_strip_zero_width`、`_door_scan_text`、窮舉測試、`_ledger_physical_lines` 和 `_nogo_full_review_shape`。複本上跑過 `-k zero_width`(32 綠)、`-k ledger_physical`(8 綠)、`-k nogo_std`(31 綠),基線都綠。

severity: major
blocking: 是 — 危險詞夾「畫面上看不見」的空白類控制字元仍判風險低,這是同一族「看不見字元繞過風險判定」的第五次,而且窮舉測試的判準把它們當「看得見」,所以測試看不到這個洞。
引句:「if ch.isspace():
        return False」
問題:`_is_invisible` 把 `str.isspace()` 為真的字元全部保留。這不只是空格和 tab:Cc 類裡的 `\x0b`、`\x0c`、`\x1c`–`\x1f`、`\x85`,以及 U+2028、U+2029 也被保留。其中 `\x1f` 在 Markdown 渲染和多數終端機裡完全看不見,也不是 `splitlines` 的換行點。計劃的天花板說明把這些寫成「跟 pay ment 一樣」,但 `pay ment` 看得到空格,`\x1f` 看不到。窮舉測試的 `_zw_visible` 也用 `ch.isspace()` 判「看得見」,所以這幾個碼位被當成「該保留」,測試不會紅。
具體失敗情境:計劃寫 `實作退\x1f款流程` 或 `串接 pay\x1fment 服務`。我在複本上實測 `_door_keyword_hits` 的結果:`\x1f`、`\x0b`、`\x0c`、`\x1c`、`\x85`、U+2028 全回空清單,同一行的 `\x00`、U+180B 等則照常命中。NFKC 後的第二次刪除也救不了,因為這些字元本來就被判成空白而保留。
修法建議:只保留真的看得見的分隔(空格、tab、換行、NBSP 與 Zs),其餘 `isspace` 為真的控制字元(`\x0b`、`\x0c`、`\x1c`–`\x1f`、`\x85`)改成刪除,並讓 `_zw_visible` 同步。
佐證:``scripts/lumos: `scripts/lumos:5026-5029` ``(`_is_invisible`);``scripts/test_lumos.py: `scripts/test_lumos.py` 的 `_zw_visible` ``(patch 內 `return ch.isspace() or cat[0] in "LNPS" or cat in ("Zs", "Mc")`)。

severity: minor
blocking: 否 — `_door_scan_text` 第二次刪除只是備援,拿掉它沒有任何行為測試會紅,風險是未來被誤刪;目前行為正確。
引句:「return _strip_zero_width(unicodedata.normalize("NFKC", _strip_zero_width(ln)))」
問題:NFKC 之後才冒出來的看不見字,要靠最外層那次 `_strip_zero_width` 才刪得掉。半形濁點 U+FF9E、U+FF9F 經 NFKC 變成 U+3099、U+309A(Mn);U+00B4 這類字經 NFKC 變成「空格加組合記號」。我找到 130 個輸入的第二次刪除會改變結果。
具體失敗情境:我把外層那次刪除拿掉(只留「刪、NFKC」)。`pay\uff9ement` 和 `退\uff9e款` 立刻從命中變成不命中。但 `-k zero_width` 與 `-k door` 的行為測試全綠,只有 `t_door_scan_logic_version_pin` 的原始碼雜湊紅,而那個釘值是作者改完直接更新的。
修法建議:在 `t_zero_width_strip_all_invisible` 或 `t_spec_gate_door_nfkc_zero_width` 加一組 U+FF9E、U+FF9F 夾在危險詞中間的案例。
佐證:``scripts/lumos: `scripts/lumos:8166` ``。

severity: minor
blocking: 否 — 只是測試覆蓋缺口,沒有現行錯誤行為。
引句:「if not isinstance(rid, str) or not rid.strip():」
問題:`_nogo_full_review_shape` 的輪次型別檢查,測試只覆蓋「完全沒有 round 欄位」(None)。我把條件改成 `if rid is None:`,`-k needs_full_review_shape` 四條斷言全綠。
我直接呼叫該函式實測:整數 1、`True`、`["r1"]`、`""`、`" "` 都被擋(訊息統一是「沒帶輪次」,對整數有點誤導);`"r0"`、`"banana"` 會放行。放行不算錯,因為輪次是記帳的人自填的,屬於計劃已承認的天花板。
具體失敗情境:有人把檢查放寬成只看 None,現有測試不會發現。
修法建議:補一個單元測試,直接對 `_nogo_full_review_shape` 餵整數、空字串、空白、非字串。
佐證:``scripts/lumos: `scripts/lumos:9440-9446` ``(`_nogo_full_review_shape` 的迴圈)。

severity: minor
blocking: 否 — 兩處都是測試對改壞的敏感度問題,現行實作正確。
引句:「check("② 1 秒內讀完(線性)", el < 1.0, f"{el:.2f}s")」
問題:長行線性測試靠牆鐘門檻。我在本機量到舊版 bytes 實作 1.6 秒、新版 0.04 秒,門檻只比舊版快 1.6 倍,換到更快的機器舊實作可能低於 1 秒而假綠。另外,窮舉測試跳過代理區(`0xD800`–`0xDFFF`),`_INVISIBLE_CATS` 裡的 `Cs` 沒人驗證:我把 `Cs` 拿掉,`-k zero_width` 仍 32 綠。plan 讀入走 UTF-8 嚴格解碼時進不來代理字元,所以現在不影響行為。
具體失敗情境:CI 機器夠快時,誰把 `bytearray` 改回 `bytes` 也不會紅。
修法建議:線性測試改成不靠時間的判準(例如算緩衝複製的次數或位元組數),或把門檻拉到比舊版快 10 倍以上。
佐證:``scripts/test_lumos.py: `scripts/test_lumos.py` 的 `t_ledger_physical_lines_long_line_linear` ``。

**已讀,無 finding**:
- 窮舉測試的結構沒有假綠:
  - 「兩大段串成一行」只要有一個字沒被刪,整串就不命中,測試只會紅,不會因為別的字被刪而掩蓋。
  - 逐一跑的那段,我數過 `direct` 共 6034 碼位(Cc 55、Cf 170、Mn 2020、Me 13、Lo 4、Cn 3769、So 3),沒有漏碼位。
  - 我把 Me、ASCII 的 `translate`、第一次刪除、Mn 分別改壞,各自都有斷言變紅。
  - 大段 Cn 與 Co 約 95 萬個,在 Python 3.15 新增指派數千個碼位後仍高於 900000 的斷言。
- 刪 Mn 對中文、日文、英文沒有影響。因為只用在比對:`か` 加 U+3099(濁點分解形)變成 `か`,`José` 的分解形變成 `Jose`,預組合的 `が` 與 `é` 不動,中文字不受影響。行雜湊照用原文。其他文字(泰文、印地文、越南文)的組合寫法會被拿掉,計劃已明說只顧中英文。
- 刪除對所有碼位都收斂:我對全部碼位檢查,`_door_scan_text` 之後沒有殘留的看不見字,二次套用結果不變(冪等)。
- `_ledger_physical_lines`:
  - 對 6000 組隨機位元組(含 `\r`、`\n`、`\r\n`、中文、空塊)乘以區塊大小 1、2、3、4、5、7、64,共 42000 組,行、行號和位元組起點跟整本切完全一致。
  - 30MB 單行加 20 萬行 0.24 秒;300 萬個純 `\r` 行尾 1.4 秒。
  - 我把 `scan -= pos` 或 `base + pos` 改壞,`-k ledger_physical` 都會紅。
- (b) 出口的 `ctx["bad"]`、`ctx["gov"]`、`_nogo_has_named_seat` 以及 `_under_root` 的收編,都沒看到問題。

最高等級 major,blocking 1 條。
