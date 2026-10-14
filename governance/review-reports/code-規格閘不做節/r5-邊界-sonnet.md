severity: minor

已讀:本輪 repair patch 裡 `scripts/lumos` 的 `_nogo_review_unbound`、`_nogo_light_window`、`_spec_gate_push_light`、`_spec_gate_push_nogo_only`、`_spec_gate_push_scan`、`_light_gate_fails`、`_nogo_light_cmd`,以及新增測試與文件。我在 scratchpad 的複本上做了變異測試,另寫了 14 組探針,跑完已刪。`-k prepush_nogo` 的 83 個案例全綠,耗時約 66 秒。

以下情境已讀並實測,無 finding:
- 快照路徑含空白與 NFD、符號連結的審材、符號連結的快照(指向的檔被刪就擋)、BOM 加 CRLF 的計劃、審查帳裡的超深巢狀行。
- 刪掉的計劃(別的筆記還在時)、散文在快照之後才修改、舊格式帳列(沒有 `spec_path`)、迴圈編號帶尾端空白。
- 對 342 份 Projects 筆記重判門共約 1.1 秒;50000 行不做清單約 0.6 秒;長行與巢狀行都在 0.2 秒內。

severity: minor
blocking: 否 — 只多擋(安全方向),訊息也講得出原因。
引句:「if nfc(str(_at(sp))) != nfc(str((env.vault / prel).resolve())):」
問題:macOS 預設不分大小寫,`canary record --spec` 記帳時只做 `resolve()`,不會校正大小寫。路徑大小寫寫得跟磁碟上不同,記帳照過,存進帳的就是那個寫法。推送前拿它跟磁碟實際大小寫的路徑逐字比,不相等。
具體失敗情境:審查席用 `--spec …/projects/甲_計劃.md`(小寫 projects)記一筆合格審查。我實測推送前 rc1,訊息是「審的是 docs/x-knowledge/projects/甲_計劃.md,不是這份計劃」。實際審的檔就是同一份,只能重記一筆。
佐證:``file: `scripts/lumos:9157` ``(`_nogo_review_unbound` 的比對那行,位置依我讀的工作樹)

severity: minor
blocking: 否 — 帳是手改才會出現這種值,fail-closed,威脅模型內。
引句:「return (q if q.is_absolute() else root / q).resolve()」
問題:這輪補了 `findings` 與雜湊的型別檢查,但帳上 `spec_path`、`snapshot_path` 字串裡有 NUL 字元時,`Path.resolve()` 會丟 `ValueError`。`_at` 只被 `except OSError` 包著讀檔那一步,`_at(sp)` 本身沒包。
具體失敗情境:帳列的 `spec_path` 是 "a\u0000b"。我實測推送前直接印 Traceback(`ValueError: lstat: embedded null character in path`),rc1,沒有「判不了」的說明。與 r4 邊2 同族(手改帳的欄位值讓檢查崩潰),這一組沒掃到。

severity: minor
blocking: 否 — 測試缺口,程式現況行為正確。
引句:「and _nogo_review_unbound(env, prel, r, nogo_skipped) is None)」
問題:`_seat_ok` 有四個判斷,測試只釘住其中一部分。我逐一拿掉後,`-k nogo_light` 的 40 個案例全綠:
- (a) 拿掉 `_nogo_review_unbound(...) is None`。
- (b) 拿掉 `a.strip()` 的去空白。
- (c) 拿掉 `kind in (caught, none)` 與 `severity in (clean, minor)`。
- (d) 拿掉 `nfc()` 的路徑正規化(比對審材路徑那一行)。

具體失敗情境:有人把這幾行改壞,例如通才席綁到別的檔、卻讓架構對齊席綁好,或通才席是 missed,推送前會錯放行,測試不會紅。我手動跑 X11 與 X12,現行程式都正確擋下,所以只是釘不住。另一個沒測的行為是推送範圍刪掉計劃時不擋:拿掉 `if not p.is_file(): return None` 後 `-k nogo_plan` 的 5 個案例全綠。

severity: minor
blocking: 否 — 席名約定上的天花板,單人依序操作的威脅模型內。
引句:「and not nfc(a.strip()).startswith("架構對齊")」
問題:判斷「架構對齊以外的一席」只靠席名開頭是不是「架構對齊」。
具體失敗情境:實測以下席名單獨一席就放行(rc0):`claude-架構對齊`、`ARCH-alignment`。`' 架構對齊-sonnet '` 與 `架構對齊` 則正確被擋。前綴型席名或英文席名的架構席,會被當成通才席,「要有一席逐行看被略過那幾行」的保證因此落空。

最高等級 minor,blocking 0 條。
