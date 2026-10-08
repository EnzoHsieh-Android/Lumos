severity: minor

驗收範圍:r2-delta 的 `_slot_strip_keys` 空白規則(isalnum 判斷)與 `_nodehome_tag_only_change` test-gone 整串比對。無 blocker、無 major;實測沒找到能把說明夾帶進去的輸入,只有兩個過擋(安全方向)的小情形。

實測 isalnum 回傳(python3.14):底線、連字號、emoji、組合字元(U+0301)、全形句點為 False;全形英數(Ａ)、日文假名(ア)、數字上標(²)、阿拉伯數字(٣)、羅馬數字(ⅷ)、中文為 True。對「a [test:x]X」拿掉標記的結果:X=`_` 得 `a_b`、`ア` 得 `a ア`、`²` 得 `a ²`、`😀` 得 `a😀`、`-` 得 `a-b`、`(b)` 得 `a(b)`、組合字元得 `áb`(空白被吞,組合字元併到 a 上)。

針對題目那句:原句 a_b 改成 a [test:x]_b,拿掉標記得 `a_b`,跟原句一樣,判沒變。這是對的:使用者只是在標記前多打一個空白,沒有加說明,不會誤擋也不會放進說明。

severity: minor
blocking: 否——只會多擋、不會漏放(判準:過擋可用拆提交的既有出口解,沒有說明能藉此混過)
file: `scripts/lumos:4191`
失敗場景:原句本來就有空白、字是 isalnum 為 False 的符號(底線、emoji、組合字元),例如舊版 `a 😀`、新版 `a [test:x]😀`;拿掉標記得 `a😀` 與 `a 😀` 不同,被判成改了說明。反向 `a😀` 改成 `a [test:x]😀` 反而判沒變。實測 `'a [test:x]😀'` 拿掉後是 `'a😀'`。發生機率低(標記緊貼 emoji 或底線開頭的字),後果只是多擋一次。
引句:「if b >= len(line) or not line[b].isalnum():」

severity: minor
blocking: 否——只會多擋(判準:不會讓說明混過;已在程式註解寫明「前綴寫法不同的照算內容(多擋)」)
file: `scripts/lumos:26930`
失敗場景:上一版綁 `[test:python:test_x]`,新版寫 `[test-gone:test_x]`(沒帶前綴,最自然的寫法)。實測 tag_names 是 `('test','python:test_x')` 對 `('test-gone','test_x')`,sig_t 相同,`_nodehome_tag_only_change` 回 False;寫成 `[test-gone:python:test_x]` 才回 True。使用者改名後標已刪必須照抄舊前綴,否則被當寫說明擋,錯誤訊息若沒提示這點會讓人困惑。
引句:「if nm not in old_tests:」

總結:全份最高等級 minor
