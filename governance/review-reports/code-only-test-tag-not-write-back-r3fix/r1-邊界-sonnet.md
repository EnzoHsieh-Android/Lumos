severity: minor

# 第三輪修正驗收:邊界席(極端輸入)

做法:用 importlib 載入 /Users/enzo/harness/lumos-rtb3/scripts/lumos 直接呼叫 `_nodehome_strip_test_tags`、`_nodehome_tag_only_change`(判定函式用 stub),再用 `_nh_tag_repo` 夾具跑 `home check --staged` 端到端(真判定),共約 50 個極端輸入。沒有找到「內容變了卻判沒變」的繞過。

## 已驗證守得住(逐項)
- 名稱 `_`、`__init__`:端到端指到真測試(`test__`、`test___init__`)時放行,指不到時擋。
- 純數字開頭 `1abc`、é、全形英數 `ｔｅｓｔ`:`_NODEHOME_TAG_NAME_RE` / 值字元集都不收,判有變(擋)。
- `[test::test_x]`、`[test:x：test_x]`(前綴空字串/全形冒號):擋。
- `[test:Delete-all-docs:test_x_1]`(前綴塞連字號詞):單看 `_NODEHOME_TAG_NAME_RE` 會過,但端到端被真判定擋下(prefix prose 回 1)。
- 超長識別字:超過 200 碼不拿、擋;5000 碼舊標記拿掉也正常;兩萬個標記同一行 0.08 秒、五萬行 0.22 秒、未配對方括號/深巢狀都在 0.01 秒內,沒有效能問題。
- `@` 後大寫十六進位、41 碼、6 碼:`test-gone` 值不收,整段留在正文,擋。
- `- [ ] [test:t]`、`- [x] [test:t]`、`- [ ]`→`- [x] [test:t]`:核取方塊行不丟,勾選狀態變化擋住。
- `- x`→`- [連結](x) [test:t]`、`- [[節點]] [test:t]` 新增:有 `[` 的行不丟,算新增內容,擋。
- 單獨成行綁定夾在空行間、`A\n\n- [test:t]\nB`:空行規則只吃剛丟掉那行造成的多餘空行,`A\nB`→`A\n\n- [test:t]\n\nB`(段落被拆)仍判有變。
- 全形空白、tab 前後夾標記、行首 tab 縮排:空白規則一致,不誤判也不放過內容。

## Finding

severity: minor
blocking: 否。判準:只會多擋(誤判成有寫說明,走既有拆提交出口),沒有放過內容,不屬守衛被繞過。
問題:標記後面緊接中文標點(全形逗號、句號)時,標記前的空白被保留,拿掉標記後跟「沒寫過標記」的原行不一樣,於是只加綁定被判成有改內容。
重現:old=`a，`、new=`a [test:t]，`(t 指得到真測試)→ `_nodehome_tag_only_change` 回 False;對照 `a [test:t] b` 回 True。程式在 `_slot_strip_keys` 的條件 `line[b] in _SLOT_STRIP_WS`。
引句:「前面有空白、後面緊接著字(「a [k:v]b」)時前面的空白照留,不把原本沒有的空白當成沒變」
file: `scripts/lumos:4191`

## 其他觀察(不標等級)
- 沒有 finding 屬於「判沒變卻有變」。唯一的結構性寬鬆是 `- a\n- [test:t]\n  nested`:丟掉整行後縮排內容改掛到上一項,Markdown 巢狀歸屬可能改變,但只涉及空白結構、沒有文字增減,給不出具體失敗場景,不標。

總結:全份最高等級 minor
