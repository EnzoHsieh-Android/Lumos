severity: major

# r1 架構對齊審查(只味道一不一致,不找 bug)

## 問 1 分層與依賴方向
結構對得上鄰居。新函式 `_nodehome_strip_test_tags` 只被 `_nodehome_parse_note` 呼叫,sig 由那裡產出,提交前與推送前兩條路都讀同一個 sig,一處改兩處生效。
file: `scripts/lumos:26839` `_nodehome_parse_note` 把 sig 組成 (摘要, 決策, 正文),摘要與正文都是「逐行去尾端空白再 strip」,在這兩欄前面多過一支正規化,形狀與既有寫法一致。
file: `scripts/lumos:27239` `_nodehome_mark_note_content` 與 file: `scripts/lumos:27335` `_nodehome_evaluate` 都直接比 `["sig"]`,不自己再算,設計沒有跨層直呼。
沒有不對齊。⚠ 小提醒:新函式是通用的行內標記文字處理,卻掛 `_nodehome_` 前綴放在 nodehome 區(約 26839 附近);行內標記的同族函式在 4138-4190 一帶,前綴是 `_slot_`。這是放置選擇,不構成不對齊(只有 sig 一個呼叫端)。

## 問 2 命名與錯誤處理
命名:`_nodehome_strip_test_tags` 跟同區 `_nodehome_*` 前綴一致;動詞 strip 與 `_strip_inline_markup`(file: `scripts/lumos:368`)、`_strip_code_text` 一致。
錯誤處理:是純字串函式,不丟例外、不讀檔,跟 `slot_parse`(file: `scripts/lumos:4145`)同為「壞輸入就照字面留」的風格(不成對反引號、不收尾的方括號都當正文)。`_nodehome_parse_note` 內只有決策欄用 try/except(file: `scripts/lumos:26850` 附近),因為它呼叫會丟例外的 `parse_decisions`;新函式不需要。
spec 未寫的一處:不成對的反引號怎麼處理。`slot_parse` 的既有判法是「不成對的反引號到行尾都當正文」,建議明寫跟它一致。
severity: minor
blocking: 否 + 判準:結構對,只是 spec 沒交代不成對反引號與既有判法對齊,屬補寫。
引句:「由左往右掃,碰到行內程式碼(反引號到下一個反引號)整段照留」

## 問 3 第二種做法
專案裡辨認行內 `[鍵:值]` 標記已經有一整套:`_SLOT_KEY_RE`(file: `scripts/lumos:4138`)、`_SLOT_CANON` 鍵正規化(file: `scripts/lumos:4128`)、`slot_parse` 由左往右掃並處理反引號段(file: `scripts/lumos:4145`)、`_slot_value_end` 數方括號層數找收尾 `]`(file: `scripts/lumos:4175`)。`_test_names_of`(file: `scripts/lumos:29587`)與 `_ns_test_ref_lines`(file: `scripts/lumos:29617`)都建在 `slot_parse` 上,筆記測試綁定整條線沒有第二套掃描器。
本案新函式自己再寫一個由左往右的掃描器,而且「值」的判定另起一套:
1. 值的合法字元用白名單(英數、底線、點等,含半形圓括號、單引號),值裡有方括號或中文就整個不拿掉;`slot_parse` 的規則是方括號成對就收(`_slot_value_end`),不限字元。兩邊對「什麼算一個 `[test:…]` 標記」的邊界判法不同:例如值裡有成對方括號,`slot_parse` 算一個欄位,新函式算非標記。
2. 鍵比對:spec 說「鍵的寫法同 `_SLOT_KEY_RE`」,但沒說是否走 `_SLOT_CANON`(`test` 與 `test-gone` 的大小寫正規化已在那裡),等於另寫一次大小寫不分。
3. 值的切分與反引號剝除在 `_test_names_of`(file: `scripts/lumos:29587-29613`)已有一套,spec 的值字元限制是第三份對「測試名長什麼樣」的描述。
另起的理由:spec〈做法〉1 說「不直接呼叫 `slot_parse`:它只解析一行、回欄位不回位置,而這裡要的是拿掉後的文字」。站得住一半:
- 站得住的部分:`slot_parse` 確實不回位置。
- 站不住的部分:它回傳的 `core`(去掉所有欄位後剩下的字)正好就是「拿掉後的文字」,只是壓縮空白,而且是拿掉全部白名單鍵而非只拿 test 與 test-gone;可以替 `slot_parse` 加一個「只拿掉指定鍵、回保留原樣的文字」的兄弟(共用 `_slot_value_end` 與反引號判法),而不必新寫整個掃描器。另外「逐行解析」不是理由:呼叫端可以逐行呼叫(`_ns_test_ref_lines` 就是逐行呼叫 `slot_parse`)。
severity: major
blocking: 是 + 判準:引入第二種辨認行內標記的做法,與 `slot_parse`、`_slot_value_end` 的邊界判法會分歧,且〈做法〉1 的理由只說明了不能直接呼叫,沒說明為何不能擴充或共用它的零件。⚠ 判不準處:值字元白名單是刻意的安全收窄(防藏說明),那一條可以保留為「拿掉前的過濾」,但標記邊界(鍵、冒號、值收尾)應共用 `_SLOT_KEY_RE` 與 `_slot_value_end`。
引句:「不直接呼叫 `slot_parse`:它只解析一行、回欄位不回位置,而這裡要的是「拿掉後的文字」。」

## 問 4 落點合不合理
`Systems/每支檔有家` 目前 74 行、約 16 KB(file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`),規模中等,這次只加「摘要一行 WHY」,不用另開新節點。該篇已是 `_nodehome_*` 判定的家,`about_code` 覆蓋 `scripts/lumos`,落點對。
⚠ 若採問 3 的建議把正規化做成 `slot_parse` 的兄弟函式,則那個函式屬行內標記文法,它的家是管 `slot_parse` 的那篇(不是每支檔有家),`lands_in` 需補那篇。
severity: minor
blocking: 否 + 判準:現在的落點合理;只有問 3 修法改變函式位置時才要同步調整 lands_in。

不對齊共 2 條,其中 major 1 條
