severity: minor

# 驗收審(邊界席,極端輸入立場)

方法:用 SourceFileLoader 載入 `/Users/enzo/harness/lumos-rtb3/scripts/lumos`,對 `_slot_strip_keys` 以 19 種緊接字元(底線、反引號、單雙引號、括號、連字號、斜線、全形英數、假名、emoji、不換行空白、零寬字元、另一個 test 或 test-gone 標記、句號、重音字母、阿拉伯數字)乘 7 種前綴(含不換行空白、零寬字元、清單符號、縮排)逐一跑;再用 `_nodehome_strip_test_tags` 加 `_nodehome_tag_only_change` 跑 30 組兩版比對(test-gone 的前綴、大小寫、反引號、@ 提交大小寫、雙 @、逗號夾帶說明、帶括號與大於號的新名稱)。

## 通過的部分

引句:「if b >= len(line) or not line[b].isalnum():」
- 全形英數、假名、重音字母、阿拉伯數字都被 `isalnum` 判成字,前面的空白照留,跟「沒寫過標記的同一行」一致。
- 零寬字元、不換行空白緊接在標記後或前面,都因空白規則只認半形、tab、全形而不被吃掉,結果跟原行不同、判為有改(誤擋方向,安全)。
- 連續兩個標記、test 接 test-gone,逐個處理後 `a [test:x][test:y]b` 變 `ab`,跟原行 `a b` 不同、判為有改(誤擋,安全)。
- test-gone 整串一致:`T_old`、前綴不同、`@ABCDEF1`、雙 `@`、夾帶別的名稱都被擋;`t_old @abcdef1`、反引號包住、逗號後重複同名放行,這幾種沒有帶進新字。

引句:「if nm not in old_tests:」
- 我替 test-gone 想的夾帶說明路徑(新名稱帶英文句子、帶括號或大於號)全被擋在 `_NODEHOME_TAG_NAME_RE` 或 old_tests 比對,未能繞過。

## finding 1

severity: minor
blocking: 否。判準:只是在標記旁多出或少掉一格半形空白,沒有新字進筆記,也沒有說明文字能藏進去;沒到能夾帶說明的程度。

標記後緊接非英數的標點或符號(底線、反引號、引號、括號、連字號、斜線、句點、emoji)時,標記前的半形空白會被連帶吃掉,所以「原本緊貼、新版在標記前多一格空白」會被判成只換測試綁定,守衛被繞過一格空白。

引句:「out = [head.rstrip(_SLOT_STRIP_WS)]」

最小重現(已跑,輸出為 `(True, True, ...)`,即 sig_t 一樣且放行):
- 舊版 `a_b`,新版 `a [test:t_real]_b`,judge 對 t_real 回 yes → `_nodehome_tag_only_change` 回 True。
- 舊版 `a` 加反引號行內程式碼 `` a`b` ``,新版 ``a [test:t_real]`b` `` → True。這會讓「字緊貼行內程式碼」變成「字加空白再接行內程式碼」,渲染有差。
- 舊版 `--b`,新版 `- [test:t_real]-b` → True,文字行變成清單項目。
反方向(舊版 `a [test:x]_b` 之後把空白拿掉變 `a_b`)同樣放行。

這是空白規則刻意選的取捨(標點接在標記後,標記前的空白當成標記的一部分),只能換到一格空白的差,不是說明文字。要收緊可把「後面是標點」也改成保留前面空白、只在行尾或後面是空白時才吃,代價是 `a [k:v]。` 這類原本放行的寫法會被擋。是否收緊由主持人裁。

## 結論

極端輸入下,test-gone 整串一致與新名稱單一識別字兩條守衛都沒找到能夾帶說明的繞過;空白規則剩一格半形空白的差(標記後緊接標點時)能偷渡,屬 minor。

總結:全份最高等級 minor
