severity: major

## c1 C-34 的 `value-used` 規則有兩處子句拿掉後樣本照綠
severity: major
blocking: 是 測試抓不住具體且合理的改壞,被保護的是「只收確定是值的位置」這條條款。

引句:「規則每個子句拿掉都要有一行翻紅(代碼審 r3 c1 g1)」

這句話對 `value-used` 的兩處不成立。我把 `api.yml` 複製到臨時目錄逐條改壞,對 `choice-batch2.kt` 跑 `ast-grep scan`,比對 HIT/MISS 標記。

- **子句 4b 的 `matches: value-direct` 沒有樣本守住**
  - 改法:把第 4 個 `all` 裡 `when_entry` 那個分支(`api.yml:184`)的 `matches: value-direct` 拿掉。
  - 結果:樣本核對全綠,標記跟命中完全一致。
  - 對照:4a(第 29 行)、4c(第 34 行)、4d(第 43 行)各有一行 MISS 守住同一個子句,只有 4b 沒有。
  - 具體輸入:`if (c) when (d) { true -> { go(); x.let { show(it) } }; else -> go() }`。`when` 是陳述、`.let` 的值沒人用。
  - 預期:不命中。實際:改壞後命中 C-34。
- **「最後一個陳述」條件沒有樣本守住**
  - 改法:拿掉第 4 個 `all` 裡的 `nthChild: {position: 1, reverse: true, ...}`(`api.yml:179`)。拿掉 `value-pos` 裡同樣的 `nthChild`(`api.yml:165`)也一樣。
  - 結果:樣本照綠。
  - 具體輸入:`val v = if (c) { x.let { go(it) }; 5 } else 0`,以及 `list.map { x.let { go(it) }; 1 }`。非最後一個陳述的 `.let` 值被丟掉。
  - 預期:不命中。實際:改壞後兩者都命中。

重現(我造的探針 `/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/probe.kt` 第 2、3、4 行):

| 版本 | 結果 |
|---|---|
| 修後原規則 | 這三行都不命中 C-34 |
| 4b 拿掉 `matches` | 第 2 行命中 |
| 子句 4 拿掉 `nthChild` | 第 3 行命中 |
| `value-pos` 拿掉 `nthChild` | 第 4 行命中 |

歸因:有證據的原有漏查。修前版本同樣照綠,而且修前連 4a、4d、子句 3 的改壞都照綠。這輪補的樣本只補了一部分,「每個子句拿掉都翻紅」的宣稱仍然不完整。

修法方向:加兩行 MISS 樣本,一行是 when 區塊最後一個陳述掛在 if 底下,一行是非最後一個陳述。

## c2 字串插值 `${…}` 一支樣本都沒有,C-36 和 C-37 都是
severity: major
blocking: 是 被保護的是「不含 `$` 的字串才算字面值」這條定義,拿掉其中一支測試照綠。

引句:「        - kind: string_literal」

這句是 `api.yml` 裡 C-36、C-37 各一份的 `literal-arg`;其下 `has: any: [interpolated_identifier, interpolated_expression]` 的後半支沒有樣本。

- 把 `{kind: interpolated_expression}` 從 C-36 和 C-37 兩份同時拿掉(兩份一起改,「一字不差」比對測試才不會紅):`t_choice_samples_batch2` 照綠。
- 探針:`LaunchedEffect("k${id}") { load() }`、`remember("k${id}") { 3 }`。預期:命中。
- 改壞後:兩者都不命中。這兩種寫法在 Compose 很常見,守衛會漏掉真正的選擇點。
- 現有的第 56 行 `"user_$id"` 只守住 `interpolated_identifier` 那一支,拿掉它會翻紅。
- 歸因:有證據的原有漏查。修前修後規則和樣本在這一支上相同。
- 未判定:`stopBy: end` 拿掉後我找不到會改變結果的輸入,不報。

## c3 撤號守衛只收緊了「撤號行」,表裡的列號寫法沒收緊,前導零或全形仍可繞過
severity: minor
blocking: 否 需要刻意把列號寫成 `C-040` 或 `C-４０` 才會繞過,日常不會碰到。

引句:「# 列號只認半形數字、不帶前導零(\d 也收全形數字,C-040 跟表裡的 C-40 字串比不上,撤號守衛會靜默漏擋;代碼審 r3 b1)」

表的列號讀取用的是 `_CHOICE_ROW_RE = r"^\|\s*C-\d+\s*\|"`(`configs/ast-grep/kotlin-android/check.py:1389`)。Python 的 `\d` 也收全形數字和前導零。

- 輸入:撤號行寫 `已撤列號:C-40`,表裡加一列 `| C-040 | API | ... |`(或 `C-４０`)。
- 預期:報「列號不准重用」。
- 實際:`choice_tables` 回 `probs == []`,列號 `C-040` 被當成新列收進表。實跑結果是 `C-040 C-40 []`,同樣的 `C-４０` 也是 `[]`。
- 對照:表裡寫 `C-40` 時正確回「已撤,列號不准重用」。
- 歸因:修前修後同樣漏。修前撤號行與表列號用相同字串才比得上,這輪的修法只收緊了撤號行這一側,留下另一側。
- 測試只測了撤號行寫全形或前導零(三條),沒有表的列號寫成這種寫法的案例。

## 作者問題的逐條答覆

**撤號新判法**(撤號行內容與 `_choice_retired` 回傳,實跑):

| 輸入 | 回傳 |
|---|---|
| `C-0`、`C-01`、`C-1a`、`C-１`、`C-4０`、`c-40` | 報看不懂 |
| `C-40,` | 認 `{C-40}` |
| `C-40、C-41` | 認 `{C-40, C-41}` |
| 行尾空白、行尾 tab | 認 |
| 全形逗號 `C-40，C-41` | 報看不懂(非靜默;正則裡的兩個逗號都是半形) |
| `C-40;C-41` | 報看不懂 |
| `C-40C-41` | 認兩個(無害) |
| `（無）`、`無`、空 | 報看不懂 |
| 縮排、前綴 tab 的撤號行 | 報「恰好一行」 |

表裡的列號寫成前導零或全形:不會誤擋,但會漏擋,見 c3。

**新樣本的 HIT/MISS 標記**
- 我用 ast-grep 實跑,C-34 命中 `[20,21,28,36,38-42]`、C-36 命中 `[55,56,65,66]`、C-37 命中 `[80,81,85,87]`,跟標記完全一致。
- 第 37、67 行的說明註解含 HIT 和 MISS 字樣,不會被標記解析誤讀,測試綠。

**每行是否測它註解說的那個子句**
- 第 38 行只被子句 3 命中、第 39 行只被 4a、第 40 行只被 4b、第 41 行只被 4c、第 42 行只被 4d,各自拿掉後翻紅。
- 第 29、34、43 行各自守住 4a、4c、4d 的 `matches` 後綴;4b 的 `matches` 沒有對應行(c1)。
- C-36 九種字面值(boolean、null、integer、real、long、hex、bin、unsigned、character)和六種帶號運算元(integer、real、long、hex、bin、unsigned),各拿掉一個都有一行翻紅。`+` 前綴改成只收 `-` 也會翻紅。

**C-37 有沒有同樣的樣本**
- 沒有。C-37 的樣本只有 `Unit` 與 `-1` 兩種字面值。
- C-37 的字面值清單靠測試裡「C-36 與 C-37 的 literal-arg 要一字不差」的比對(`scripts/test_lumos.py:146072`)加上 C-36 的樣本間接守住。這條我只讀了,沒實跑 C-37 單獨改壞,未判定。
- C-37 規則頭的三處我實跑改壞:拿掉「不全是字面值」、拿掉 `annotated_lambda`、拿掉 `remember` 名稱比對,各自翻紅。拿掉 `nthChild: 1` 和 `call_suffix` 兩處照綠,我找不到會改變結果的輸入,不報。

## 修補鏡頭三問

**1. 原問題的修復效果**
- claim:拿掉 C-34 值位置任一選項或 C-36 字面值任一種,樣本翻紅。
- input:逐一改壞 `api.yml` 的子句。
- before(`87093835`):改壞 4a、4d、子句 3、C-36 的 boolean 全都照綠。
- after(`59c41038`):這四個都翻紅,C-36 九種字面值與六種帶號運算元也都翻紅。
- comparison:修復成立。
- 例外:c1 的兩處與 c2 沒被補到。
- 撤號:修前 `_choice_retired("C-４０")` 回 `{'C-４０'}`(靜默收下),修後回看不懂。

**2. 修補處的正常、錯誤、相鄰路徑**
- `t_choice_table_batch2`(16 個檢查)、`t_choice_samples_batch2`(33 個)、`t_choice_points_compose`(7 個)修後在我的臨時副本全綠。
- 頂格撤號、頓號與逗號分隔、全形冒號、縮排拒絕都維持原行為。
- 相鄰的表列號讀取沒有跟著收緊,見 c3。

**3. 新發現的修前修後**
- c1 與 c2:修前修後都漏,歸因為原有漏查,不是這輪造成的回歸。
- c3:修前修後都漏,歸因為原有漏查,修補只收緊了一側。

## 圖譜鏡頭與角色卡
- `Systems/kotlin規則包.md`(check.py、`api.yml`、`test_lumos.py` 的家)受 c1、c2、c3 影響,筆記宣稱的守衛行為有缺口。這輪修補沒有改規則檔本身。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`測試假綠形態`、`lumos-cli-read` 的合約:這輪只動樣本與撤號判斷,不影響這些合約。
- `pitfalls-code-loop`、`loop-convergence-recording`:只改 `scripts/lumos` 以外的檔,不影響。
- 角色卡 be-api-compat、be-authz:這是本機命令列工具,沒有對外端點或呼叫端相容問題,不適用。

## 沒驗到的部分
- 沒有造大型輸入。磁碟用量不是問題(可用 126Gi)。
- 這輪沒有改動規則檔的效能與記憶體面,不測。
- 第二批六列的錨點與編輯(`?:`、`?.`、combine、依列號統計)我沒逐一重做,只依這輪修補範圍加上跑過的測試。
- 臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/正確性-sonnet/` 內有 `repo`、`before`、`mut.py`、`mutb.py`、`probe.kt`,待編排者刪除;我已刪掉自己造的 `mw`。

最嚴重:major;blocking 共 2 條
