severity: blocker

## F1 放寬後的 Python 掃描會把字串/docstring 裡的縮排範例文字當成真測試,原地重現這批要修的那個 bug

severity: blocker
blocking: yes

引句:「這裡多算沒關係:多算只是維持原本的嚴格,少算才會放過假綠。」

這句話(`scripts/lumos:10438`,loose_for 的 docstring)是整批改動安全性的核心假設:作者認為「放寬」只會多算、多算不影響正確性,只有少算才危險。這個假設對 Kotlin/Java/C#/Playwright/Dart/Swift/Jest 七棧成立(它們的 method_re 本來就沒有行首錨,已用實跑證實 loose 與 strict 結果完全相同,見下方驗證①)。**但對 Python 不成立**:Python profile 的 `comment_strip` 設成 `"none"`(`scripts/lumos:3979`「comment_strip="none":Python 無 C 式註解,剝了反被字串/中文註解裡的 /*..*/ 誤吃大段內容」),代表字串字面 / docstring 內容從不會被剝掉再比對。原本的行首錨(欄位 0)其實同時兼任了「防字串內容污染」的守門(`scripts/lumos:3980`「被註解的 # def 不在行首,行首錨天然排除」)。這批改動把錨放寬成「該行前面只有空白」(`scripts/lumos:4354`:`if src.startswith("(?m)^") and not src.startswith("(?m)^[") and not src.startswith("(?m)^\\s"):`),縮排的 docstring/字串內容從此不再被排除。

重現(最小案例,實際跑過):
一支「真的只宣告了一支」的參數化測試,docstring 裡照這批 PR 常見的寫法夾了一段程式範例(這種寫法在 lumos 自己的程式庫裡到處都是,見下方②):
```python
def t_widget():
    """Runs the widget-creation contract test.

    Example of a related helper some other module defines:
        def t_widget_helper():
            pass
    """
    pass
```
`tests/run.py` 模擬 `t_widget` 跑出 9 個案例(單一測試的參數化)。實際跑 `lumos spec-gate`:
- 用這批改動前(strict-only,即把 `_loose_of` 換回讀 `methods_for`):`[spec-gate] 跑: S1 綠(t_widget)` —— 正確。
- 用這批改動後(現況):`[spec-gate] 跑: S1 弱證據(t_widget;篩選匹配到 9 支,測試名要唯一(換更長、不互為子字串的名字)(程式裡有 2 支名字對得上))` —— **錯誤地判成撞名**,`_loose_declared_methods` 把 docstring 裡縮排的 `def t_widget_helper():` 也當成一支真宣告(因為 `[ \t]*` 不再排除縮排,`comment_strip="none"` 又不剝字串)。

這正是這批 PR 存在的理由(`scripts/lumos` 新增的另一句「★2026-09-22 rtb-production-agent-demo 回報...對方 4 支合約因此全被擋住」),現在被同一批改動用另一條路徑原地重現:一支乾淨、貨真價實的單一參數化測試,因為 docstring 裡剛好寫了範例程式碼,被判「測試名要唯一」擋下。

驗證①(七棧 loose==strict,無退化;Python/Maestro 才實際被放寬):對 9 個內建 profile 各造一份「攤平宣告＋縮排在類別裡的宣告」樣本後實跑 `discover_test_methods` vs `_loose_declared_methods`,C#/Kotlin/Java/Playwright/Dart/Swift/Jest 的 strict 與 loose 結果逐字相同(規則本來就沒有行首錨);只有 maestro 與 python 的 loose 多抓到縮排/類別內那支,符合設計初衷。

驗證②(不是憑空案例,拿這個 repo 自己的 `scripts/test_lumos.py` 實跑):
```
strict count: 1065
loose  count: 1213
extra (loose-only) count: 148
```
其中一組額外命中直接來自一段字串字面(`mini.write_text(textwrap.dedent('''...`),`scripts/test_lumos.py:16993`:`def t_a(): check("a", True)`)——這三行 `t_a`/`t_b`/`t_c` 只是某支測試寫進暫存檔案的「範例腳本內容」,根本不是這個 repo 裡真的宣告過的測試,strict 掃描本來就排除它們(不在行首),loose 掃描現在會把它們當成「程式裡真的宣告了」的測試名。這說明 148 這個數字不是理論上的噪音,是這個 repo 現在就會踩到的規模。

為什麼是 bug 不是風格:這條規則的唯一存在理由就是「不要把非測試的東西誤判成撞名」,而它現在對 Python 的表現方向反了——會把根本不存在的宣告當真,讓乾淨的參數化測試被判「弱證據」。判定閘要求風險低計劃全綠才放行(`_spec_gate_push_one` 沒過會被推送閘擋下並自動記 `major` 逃逸),所以這不是印出來的訊息不準,是真的會擋下本該放行的變更——跟這批 PR 的 r1/r2 blocker 是同一等級的錯法,只是方向相反(這次是少一支的相反面:多算出一支不存在的)。

## F2 「判斷這條 method_re 是不是錨在欄位 0」的守門條件本身邏輯有洞,遇到特定形狀會靜默不放寬

severity: major
blocking: yes

引句:「if src.startswith("(?m)^") and not src.startswith("(?m)^[") and not src.startswith("(?m)^\\s"):」

程式碼(`scripts/lumos:4354`)判斷「要不要放寬」的邏輯是:pattern 開頭是 `(?m)^` **而且**緊接著的字元不是 `[` 也不是 `\s`,才進行改寫;否則落到 else 分支,註解寫的是「本來就不是錨在欄位 0 的樣式,直接用」(`scripts/lumos:4357`)。

這個理由對「不是以 `(?m)^` 開頭」的樣式成立,但對「以 `(?m)^[` 開頭」不成立——`(?m)^[A-Z]...` 明明白白就是錨在欄位 0(`^` 後面接字元類別只是決定第一個字元要符合什麼形狀,不影響它仍然錨在行首)。也就是說,只要有一個 method_re 是「錨在欄位 0 + 開頭是字元類別」(例如某個未來/自訂棧要求測試名必須大寫開頭,寫成 `(?m)^[A-Z]\w*_test\(`),`_loose_declared_methods` 會誤判成「本來就不用放寬」,直接回傳跟 strict 一模一樣的結果——放寬完全沒發生,縮排/類別內的宣告一樣掃不到。

實際跑過驗證(用等價於此形狀但非 9 個內建棧的合成 profile,因為 9 個內建棧都不巧不落在這個分支——已用實跑核對,見下方③):
```python
custom_re = re.compile(r"(?m)^[A-Z](\w*_test)\(")
```
對含有 `Flat_test()`(欄位 0)與 `class C:\n    Nested_test()`(縮排在類別裡)的檔案:
```
strict: {'lat_test'}
loose : {'lat_test'}
```
loose 跟 strict 完全一樣,`Nested_test` 兩邊都沒掃到——這正是代碼審 r1 blocker 要堵的那個洞(「少算一支就把真撞名當成參數化放行」),在這個形狀上完全沒被堵住,是靜默失敗(不報錯、不印警告,呼叫端拿到的就是跟沒放寬前一樣的結果)。

驗證③(9 個內建棧確認都不落在這個分支,所以現行出貨行為不受影響):C#/Kotlin/Java/Playwright/Dart/Swift/Jest 的 method_re 完全沒有 `(?m)^` 前綴;Maestro(`^name:...`)與 Python(`^def ...`)開頭都不是 `[` 也不是 `\s`,兩者都正常走放寬分支(見 F1 驗證①的輸出)。所以這個洞目前不會被 9 個內建 profile 觸發,只有透過 `.lumos/config.json` 的 `test.method_regex` 自訂逃生口(`load_test_profile` 的 inline 覆蓋,`_safe_user_regex` 只擋 ReDoS 形狀、不擋這種寫法)才可能撞到。但既然這批 PR 的整個目的就是堵「掃描器少算導致假綠」這個類別的洞,守門條件本身留了一個會讓同一類洞原地重現的分支,而且沒有任何測試覆蓋這個分支,判 major、要求修。

建議修法方向(僅供參考,不要求照抄):判斷「是不是已經夠寬鬆」應該直接檢查 `(?m)^` 後面是不是已經有一段可以匹配 0 到多個空白的結構(例如用 `re.match(r"\(\?m\)\^(?:\\s\*|\[[ \t]", src)` 之類更貼近語意的判斷),而不是用「下一個字元是不是 `[`」這種跟「有沒有錨」無關的表面特徵。

---

## 已查但沒發現問題的路徑

- **快取是否互污染**:`_platform_test_index` 裡 `mcache`(strict,給 `methods_for`)與 `lcache`(loose,給 `methods_for.loose`)是兩個獨立的 dict,各自用 `plat` 當 key,分屬不同的閉包變數,沒有共用 key 空間;`discover_test_methods` 本身沒有任何跨呼叫的記憶化(每次都重新 `os.walk`),所以不存在「strict 用到 loose 算出來的結果」或反過來的風險。三個呼叫點(`_spec_gate_run_clauses` / `_spec_gate_regress` / `_spec_gate_push_one`)拿到的 `methods_for` 全部溯源回同一支 `_platform_test_index`(逐一核對 `scripts/lumos:5529`/`5805`/`6160` 皆是),`.loose` 屬性保證存在,`_loose_of` 不會拿到少了 `.loose` 屬性的函式物件。
- **`_spec_gate_verdict` 的分支扁平化**(`if n is not None and n >= 2 and declared != 1:`):逐條列出真值表跟原本的巢狀 `if...pass...else` 比對,兩者在 `declared` 為 `1`/`None`/其他整數三種情況下行為完全一致,純重構無語意變化。
- **群組編號位移**:放寬時只在 pattern 前面接 `"(?m)^[ \t]*"`,這段字串不含任何未跳脫的小括號,不會讓 `mre.finditer(txt)` 裡 `m.group(1)` 的編號跑掉——已用 Python/Maestro 實跑核對抓到的名字正確(`t_flat`/`t_nested` 而非其他群組內容)。
- **實測整套規格閘測試**:`python3 scripts/test_lumos.py -k spec_gate` 97 support 全綠(含 r2 新增的 `t_spec_gate_collision_inside_class_still_weak`),`-k spec_gate_collision` 單獨跑也綠;並用 `_loose_of` 改寫成直接回傳 `methods_for(plat)`(等價於「換回正規那支」)的副本,實際跑同一份 fixture 重現了 r1 那個 blocker(S1 從弱證據變成綠),證實這支翻紅釘測試是有牙齒的、也證實 F1 的最小案例在「改動前 vs 改動後」的落差是真實可重現的。

以上兩項發現都用實際執行(不是讀程式碼推論)得到,腳本存在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/verify/`(唯讀環境,未改動 /Users/enzo/harness/lumos-toolchain 底下任何檔案或 git 狀態)。
