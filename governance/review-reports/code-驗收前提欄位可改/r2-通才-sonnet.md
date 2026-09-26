severity: major

## F1 日期樣式的值不加引號,標準 YAML(Obsidian/js-yaml)會讀成日期物件不是字串
severity: major
blocking: yes
引句:「return (v != "" and v == v.strip() and "\n" not in v and "\t" not in v」

`_yaml_plain_ok` 沒有排除 `YYYY-MM-DD` 這種形狀。`valid_under`/`revalidate_when` 不在 `DATE_KEYS` 裡,所以走一般白名單判斷:字串 `"2026-09-26"` 開頭字元 `2` 不在 `_YAML_PLAIN_BAD_START`、沒有 `": "`、沒有 `" #"`、不是布林字、也不吃數字正則,判定為「安全」,不加引號寫出 `valid_under: 2026-09-26`。

實測(已裝 PyYAML 6.0.3,SafeLoader 對日期/特殊數值的解法跟 js-yaml 預設 schema 同源):
```
yaml.safe_load("valid_under: 2026-09-26")["valid_under"]
-> datetime.date(2026, 9, 26)   # 不是字串 "2026-09-26"
```
用本工具實跑重現(乾淨複本 /tmp/vaulttest):
```
python3 scripts/lumos --vault /tmp/vaulttest set Verification/V valid_under "2026-09-26"
grep valid_under /tmp/vaulttest/Verification/V.md
# valid_under: 2026-09-26   ← 沒加引號
```
Obsidian 用 js-yaml 讀 frontmatter 也認得裸日期(`YYYY-MM-DD`)為 timestamp 型別,這是社群公認的 Obsidian frontmatter 老坑(裸日期要加引號)。這兩欄的值是「什麼情況下才成立/該回頭驗」的散文條件,使用者完全可能只給一個日期(例如把 CLAUDE.md 範例 `REVISIT:YYYY-MM-DD` 去掉冒號後的說明只剩日期,或條件本身就是「2026-12-31」)。一旦命中,Obsidian 端讀到的不是字串而是日期物件,跟本工具用字串比對(`_conds`/`str(c)`)的假設不一致,是這次 patch 明確要解決的「標準 YAML 讀出來不一樣」問題裡最容易踩到的一種,但白名單完全沒防。
重現步驟:在任一 vault 用 `lumos set <verification 節點> valid_under "2026-09-26"`,再用任何標準 YAML 函式庫(PyYAML/js-yaml)解析該行,得到的型別是 date 不是 str。

## F2 十六進位/八進位/六十進位(sexagesimal)/.inf/.nan 等 YAML 數值特殊字面值未被擋,會被標準 YAML 讀成數字
severity: major
blocking: yes
引句:「and not re.fullmatch(r"[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?", v))」

這行是 `_yaml_plain_ok` 用來擋「純數字」的正則,只認十進位(含小數、科學記號),沒有涵蓋 YAML 1.1 / js-yaml 預設 schema 還會解析成數字的其他字面值:
- 十六進位 `0x1A`、二進位 `0b101`、八進位 `0o17`(新式)或 `017`(舊式前導零)
- 冒號分隔的六十進位整數,例如 `1:20:30`、`12:34`
- 特殊浮點 `.inf` / `-.inf` / `.nan`
- 底線分位的整數,例如 `1_000`

實測(PyYAML SafeLoader,同源於 js-yaml 預設 schema 對 YAML 1.1 型別的解析):
```
'0x1A' -> 26          (int)
'1:20:30' -> 4830      (int, 六十進位)
'.inf' -> inf          (float)
'.nan' -> nan          (float)
'1_000' -> 1000        (int)
```
用本工具實跑重現:
```
python3 scripts/lumos --vault /tmp/vaulttest set Verification/V valid_under "0x1A"
grep valid_under /tmp/vaulttest/Verification/V.md   # valid_under: 0x1A  (沒加引號)
python3 scripts/lumos --vault /tmp/vaulttest set Verification/V valid_under "1:20:30"
grep valid_under /tmp/vaulttest/Verification/V.md   # valid_under: 1:20:30 (沒加引號,沒有 ": " 所以沒觸發冒號規則)
python3 scripts/lumos --vault /tmp/vaulttest set Verification/V valid_under ".inf"
grep valid_under /tmp/vaulttest/Verification/V.md   # valid_under: .inf (沒加引號)
```
註解裡明講「YAML 型別劫持守衛」的目的就是防「純數字被讀成數字」,但正則覆蓋不到上面這幾種標準 YAML 承認的數字字面值,屬於守衛本身的實作缺口,跟這次 patch 想解決的問題同一類、同一支函式,沒有理由不修。條件文字本身通常是散文,命中純十六進位/純冒號時間格式的機率雖低於 F1 的裸日期,但一旦命中就是「標準 YAML 讀出來變成完全不同的型別和值」,而不是「多一層引號的美觀問題」,故列 major。

已看,無:S1–S5(整欄換掉的四種舊形狀清乾淨、多值清單順序內容、空值/換行擋下、其他欄位單值限制、插入位置)邏輯讀過並用 mkvault 情境跑過,行為與條款一致,沒發現問題;`_yaml_quote` 對「無反斜線無雙引號→雙引號」「無單引號→單引號」「兩者都有→擋」的分支邏輯跟 `strip_quotes`(只剝外層一層引號、不解跳脫)的讀法完全對稱,S6 測試裡列的六種情境(冒號結尾、反斜線、單雙引號同時出現、含 `#`、以 `[[` 開頭)都手動用標準 YAML 驗證過讀法一致,`append`/`fmt_list_item` 走同一支函式也複驗過;把 `fmt_scalar`/`fmt_list_item` 還原成修法前的舊版本後,新增的 `t_set_condition_fields_standard_yaml_safe` 立刻翻紅 8 條斷言,證明測試真的接得住這次修的洞;把新版程式碼實跑在既有 `set`/`append`/`decision-add`/`self_audit`/`signoff` 測試子集(共 174+76+60+14=324 條)全部綠燈,沒發現既有寫入指令輸出格式因這次改動跑掉的迴歸;`COND_KEYS` 插入位置改用 `fm_structure` 找第一個 list/block 欄位、跟 `edit_fm_scalar` 邏輯一致,也有專屬測試覆蓋(沒有這欄時插在 `related` 之前)。
