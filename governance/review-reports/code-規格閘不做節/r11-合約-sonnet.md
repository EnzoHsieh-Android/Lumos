severity: major

我看的範圍是修補差異與 `spec-gate-nondo` 樹(該樹的 HEAD 1657fad9;與 065cd5b1 只差第十一輪卷證材料)。`spec-trace` 讀到 67 條款全綁、`lint` 對三篇筆記都是 0 問題,`spec-gate --door-rule` 印 `door_rule=9`,指紋與測試釘值 `ad5777cf…` 一致。版本號在計劃、Systems、程式常數三邊一致:掃法 5、不做清單邏輯 4、門規則 9,S5 也是 9。舊說法也清乾淨了。程式裡剩下的 `isspace` 只在 `_pq_blank` 等寫入端,那是刻意分工。程式碼與 Systems 的 `splitlines` 在規格閘這一族已無殘留,計劃只在歷史敘述與 S66 描述裡提到。程式與 Systems 的壞行訊息也沒有殘留的「已跳過」。

另外兩件事我沒有逐項判成 finding。固定席的 ★INVARIANT★ 沒被破壞:`clause_bindings` 換成 `_note_lines` 之後,design-loop 的第五步條款綁定仍是 67 條全綁。`anchor-baseline.json` 在補丁裡寫的測試檔雜湊是 `a44d8098…`,但 065cd5b1 與目前樹裡是 `46c48b62…`(與檔案實際雜湊一致),補丁與樹對不上的原因我沒查清。

severity: major
blocking: 是 — 條款 S65 與 S64 承諾的「看得見的空白類分隔」在五個字元上實際被刪掉,多字危險詞(`DROP TABLE`、`DELETE FROM`、`pre-push hook`、`anchor verify`、`LINE 推送`)仍可繞過,而且測試沒覆蓋這一型。
引句:「其餘 isspace 為真的(含行分隔 Zl、段分隔 Zp)一律當看不見拿掉」
問題:`_is_invisible` 把 `\x0b`、`\x0c`、`\x85`、U+2028、U+2029 全部「刪掉」。這五個字在編輯器與瀏覽器裡就是空白或換行,真正拿來當詞間分隔的時候,刪掉就把兩個字黏在一起。tab、全形空白、NBSP 則是壓成一個空格,所以命中。同一類字元的處理方式不一致。`\x1c`–`\x1f` 也一樣,不過它們在畫面上多半是看不見的。
具體失敗情境:我載入 `scripts/lumos` 實測 `_door_keyword_hits`:
- `執行 DROP\x0cTABLE x`、`DROP\u2028TABLE`、`DROP\u2029TABLE`、`DROP\x85TABLE`、`DROP\x0bTABLE` 都回 `[]`。
- `關掉 pre-push\u2028hook`、`改 LINE\x0c推送` 也是 `[]`。
- 對照:用 tab、`\u3000`、一般空格當分隔都命中。
這是同一族第六次空白繞過。
測試缺口:S65 的 `t_door_scan_break_chars_dropped` 只拿單字詞(`payment`、`退款`)測,沒測「這幾個字取代多字詞的詞間空格」。S64 的 `t_door_scan_space_runs_fold` 也沒包含這五個字。如果改成「把它們換成空格再壓」,現有測試仍然全綠,但改回現況也不會紅。
佐證:``file: `scripts/lumos:5046`、`scripts/lumos:8196-8210`(`_is_invisible`、`_door_scan_text`)``、``file: `scripts/test_lumos.py`(t_door_scan_break_chars_dropped、t_door_scan_space_runs_fold)``。

severity: minor
blocking: 否 — 上限的說明有一處指到錯的位置,影響的是下次讀筆記的人,不影響行為。
引句:「換 Python 版本時照下面那行回頭條件重跑窮舉」
問題:`Systems/規格閘.md` 的 PITFALL「Cn 跟 Python 版本走」寫的是「照下面那行回頭條件」。但它正下面兩行是「跨行切開的詞」的 REVISIT,講的是硬換行段落有幾份。Unicode 17 那條 REVISIT 在它上面的 102 行。另外,計劃〈實務隱患〉沒有這個 Cn 上限,只有 S57 與 r10 的發現清單提到,所以三處說法不一致。程式碼的 `_strip_zero_width` docstring 與 REVISIT 倒是有。
具體失敗情境:照字面往下找回頭條件的人會去數硬換行段落,而不是重跑窮舉測試。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:110-113`、`:102```。

severity: minor
blocking: 否 — 承認了會誤判的代價卻沒有回頭條件,屬於過期的風險說法。
引句:「r10 起 isspace 為真卻看不見的控制字元與行段分隔一律拿掉、連續空白壓成一個、漢字之間的空白拿掉(代碼審 r10 G1)。方向是多判高」
問題:「漢字間空白拿掉」這個上限(「面對 外部」會拼成「對外」)在計劃、Systems PITFALL、`_door_scan_text` docstring 三處都只講「方向是多判高」,沒有回頭條件。照專案鐵則 4,承認風險要附回頭看的條件。跨行切開那條有 REVISIT,另外兩條(漢字間、Cn)沒有或指錯。
具體失敗情境:這條規則若造成大量誤判高,沒有任何機制會提醒人回來看。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:181`、`docs/lumos-toolchain-knowledge/Systems/規格閘.md:105-106`、`scripts/lumos:8196-8210```。

severity: minor
blocking: 否 — 完整設計審形狀檢查放寬了,但只在程式註解交代,計劃與 Systems 的說法還是舊的,測試也沒釘這個放寬。
引句:「定錨之後其他非 light 的怪值不另擋(寫入端 canary record、loop next 的 --tier」
問題:`_nogo_full_review_shape` 改成只看定錨分級是 standard 或 high,再加「沒有 light」。以前是「帳上每一筆 tier 都要是 standard 或 high」,所以像 `tier: "foo"` 這種後來的怪值現在不擋了。S59 條款文字有跟上定錨,但:
- `Systems/規格閘.md:115` 的 PITFALL 修法,與計劃第 97 行的做法敘述,仍寫「每一筆都帶輪次、分級是 standard 或 high」。
- `t_nogo_full_review_shape_unit` 沒有「定錨之後記一筆怪值」的案例,放寬與否都不會紅。
- 計劃第 59 行與第 66 行描述釘值涵蓋的函式清單,沒有加上 `_note_lines`、`_VISIBLE_CONTROLS`、`_ASCII_INVISIBLE`、兩支正則,與測試實際釘的內容不符。
具體失敗情境:下一個讀 Systems 的人以為每一筆都被檢查,實際上只有定錨與 light 被檢查。
佐證:``file: `scripts/lumos:9468-9490`、`docs/lumos-toolchain-knowledge/Systems/規格閘.md:115`、`docs/lumos-toolchain-knowledge/Projects/規格閘不把不做節的詞算進風險_計劃.md:59,66,97`、`scripts/test_lumos.py`(t_nogo_full_review_shape_unit)``。

severity: minor
blocking: 否 — S58 守衛的掃描詞太窄,目前內容都對,但「手冊各處」並沒有被機械守住。
引句:「同一行講 major 與 -std(代碼審 r10 合4:之前只看 -std)」
問題:`_nogo_manual_lines` 只收同時含「不做清單」與「輕量」的行,或含 not-doing 與 light 的英文行。`docs/心智模型.md:181` 寫的是「「## 不做」清單裡寫了危險詞…輕量設計審」。字面是「## 不做」加「清單」,不是連續的「不做清單」,所以守衛掃不到。我手動檢查,那行現在確實有 major 與 `-std`,但之後改壞沒有測試會紅。S58 宣稱涵蓋手冊(含英文手冊),守衛實際涵蓋的是詞面符合的 19 行。
具體失敗情境:有人把心智模型第 181 行的 `-std` 拿掉,`t_design_loop_manuals_nogo_major_std` 仍然綠。
佐證:``file: `scripts/test_lumos.py:65704-65719`、`docs/心智模型.md:181```。

最高等級 major,blocking 1 條。
