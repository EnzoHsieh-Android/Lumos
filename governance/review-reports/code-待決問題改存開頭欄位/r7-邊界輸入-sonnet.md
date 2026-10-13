severity: major

**發現清單**

1. 整題縮到頂格,題目靜默消失(修復回歸)
   - 輸入:一個 `pending_questions` 清單後面,先接 `summary: x`,再接頂格的 `id: Q2`、`text: …`、`class: 需求`、`stage: 架構`、`status: 待人`。
   - 修前 `pq_parse` 回報「這一題寫在 pending_questions 清單範圍外」。修後 errs=0、n=1,Q2 不見。
   - 端到端用 `spec-gate --no-run`:修前是 `✗ … 無法判定`,修後是 `✓ — 1 題,沒有擋進實作的`。
   - 只有 `blocking`、`irreversible` 掉到頂格會被點名。其餘題目鍵只在清單項底下才檢查,頂格的不檢查。
   - 同一個頂格 `id: Q2` 後面不接 `summary`、直接緊貼清單時,修前也漏。
   - 這與計劃筆記的說法衝突:「任何『鍵: 值』的鍵名是題目才有的鍵…就拒讀」。
severity: major
   - blocking: 是
   - 引句:「if owner.lower() in _PQ_BOOL_KEYS:」
   - file: `scripts/lumos:7349`、`scripts/lumos:7086`
   - 歸因:有證據的修復回歸。查證命令:在 `lumos_before` 與 `lumos_after`(各是 19bd4719、36d4ffed 的 `scripts/lumos`)分別對上述文字跑 `pq_parse`,修前 errs=1,修後 errs=0。

2. `decisions` 底下的流式題目整題消失(原有漏查)
   - 輸入:`decisions:` 底下除了正常的 d1,再加 `  - {id: Q2, text: 流式寫的題要人決定, class: 需求, stage: 架構, status: 待人, blocking: true}`。
   - 實跑 `spec-gate Projects/c_計劃 --no-run`:修前、修後都印 `✓ — 1 題,沒有擋進實作的`。標了阻塞的 Q2 照樣放行。
   - `  - - id: Q2` 這種巢狀清單同樣 errs=0。
   - 原因:`_pq_mapping_parts("{id: Q2, …")` 把 `{id` 當鍵名,題目鍵檢查認不出來。決策項目沒有拒絕流式 `{…}`。
severity: major
   - blocking: 是
   - 引句:「parts = _pq_mapping_parts(text[2:])」
   - file: `scripts/lumos:7165`
   - 歸因:有證據的原有漏查。修前修後對照:兩版 `pq_parse` 都回 errs=0。

3. 正常語系文字被誤擋(修復回歸)
   - 蒙古文自由變體選擇符 U+180B,Malayalam 舊式 chillu(`അവന്‍` 的 ZWJ 後接空白),波斯文 ZWNJ(`می‌` 後接空白)。三者修前都能寫,修後都擋。
   - 實跑 `question-add Projects/u_計劃 "ᠮᠣᠩᠭᠣᠯ\u180b ᠪᠢᠴᠢᠭ" --class 需求 --stage 架構`:修前 `✓`,修後 `擋下:題目文字不能換行、含 tab 或控制字元(U+180B)`。
   - 後兩句輸出同樣是 U+200D、U+200C 被擋。
   - 原因:`_pq_dicp_kind_ok` 完全沒有 U+180B–U+180F。ZWJ/ZWNJ 還要求兩側都是字母。
   - 訊息把這些字說成「控制字元」,也誤導。
   - 派工單點名要驗蒙古文。
severity: major
   - blocking: 是
   - 引句:「def _pq_dicp_kind_ok(v, i):」
   - file: `scripts/lumos:6984`、`scripts/lumos:6977`
   - 歸因:有證據的修復回歸。查證:`_strict_scalar` 對 `ᠠ\u180b` 修前回 ok,修後回 BAD U+180B。

4. 字母之間可任意夾 ZWJ、ZWNJ、軟連字號,看不見通道仍開著(原有漏查)
   - `question-add … "a\u200db\u200dc\u200dd"` 與 `"a\u00adb\u00adc"` 修前修後都回 `✓`。
   - 規則只看兩側「是字母」(`_pq_is_letterish`),不管文字系統。拉丁字母之間本來不該有 ZWJ。
   - 每個字母間隙有三種狀態(無、ZWJ、ZWNJ、軟連字號),等於任意高容量的看不見通道。
   - `🧑` 接 200 個 ZWJ 加 `🧑` 也放行。
   - 這與筆記「限制任意、高容量的隱形通道」的宣稱不符。
severity: major
   - blocking: 是
   - 引句:「_pq_is_letterish(v[i - 1]) and _pq_is_letterish(v[i + 1])」
   - file: `scripts/lumos:6981`、`scripts/lumos:6989`
   - 歸因:有證據的原有漏查。查證命令:兩版 `_pq_bad_char` 對 `a\u200db\u200dc` 都回 None。

5. 決策項第一個鍵是 block scalar 時,內文被誤當題目(修復回歸)
   - 輸入:`decisions:` 底下 `  - content: |`,內文 6 格縮排,其中一行是 `stage: 架構`;另有 `id: d1`。
   - `question-add` 修前寫入成功,修後 `擋下:寫完會讀不懂(第 7 行 … 出現題目的鍵 'stage')`,檔案沒動。
   - 原因:`- key: |` 這種寫法下,內文界線被算成 6 格,實際 5 格以上就算內文。
   - 工具自己的 `decision-add` 寫單行加引號,不受影響。這只影響手寫的舊筆記。
severity: minor
   - blocking: 否
   - 引句:「return indent + (4 if indent == 2 else 0), None」
   - file: `scripts/lumos:7194`
   - 歸因:有證據的修復回歸。查證:`qa/docs/x-knowledge/Projects/a_計劃.md` 在兩版各跑一次 `question-add`,結果如上。

6. 合法 YAML 的其他欄位讓整份清單無法判定,訊息還說錯(修復回歸)
   - 有 `pending_questions` 的筆記,只要頂格鍵不是英文字母或底線開頭,就整份判無法判定。例如 `中文鍵: 值`、`"owner": bob`、`2fa: yes`、`x/y: 1`。訊息是「頂格寫了…不是 `鍵: 值`」,但這些都是合法 YAML。
   - 續行的純量(`description: 說明\n  續行`)和巢狀 mapping(`meta:\n  owner: bob`)也判無法判定。修前這些都能讀。
   - 工具自己的 `set`、`append`、`question-add` 不會寫出這類鍵。repo 1826 篇筆記加一題後都讀得懂,所以只影響手寫筆記。
severity: minor
   - blocking: 否
   - 引句:「_PQ_TOP_KEY_RE = re.compile(」
   - file: `scripts/lumos:7057`、`scripts/lumos:7366`
   - 歸因:有證據的修復回歸。兩版 `pq_parse` 對照:修前 errs=0,修後 errs=1。

7. `decision-add` 的 `--context`、`--why` 帶換行會寫壞筆記(原有漏查)
   - 命令:`decision-add Projects/d_計劃 "採甲" --decided 2026-10-13 --why $'因為甲\n乙也可以'`,rc0 印 `✓`。
   - 寫進檔案的是跨行的雙引號值,第二行頂格。之後 `spec-gate` 回 `✗ 無法判定(第 15 行頂格寫了 …)`。
   - 修前修後都寫壞。`append`、`decision-supersede`、`summary-line`、`set` 都會讀回驗證並擋下,只有這兩個選項沒有。
   - 結果大聲失敗(gate rc1),但工具回報成功,和 `question-add` 寫前先驗的做法不一致。
severity: minor
   - blocking: 否
   - 引句:「def _pq_decisions_section(fm_lines, start, end, line0):」
   - file: `scripts/lumos:21390`
   - 歸因:有證據的原有漏查。兩版同一命令結果一樣。

8. 非 NFC 的錯誤訊息指到錯的字(未判定)
   - `a\u2000b` 這類字串被 NFC 改寫成 U+2002,`_pq_bad_char` 卻回 `v[0]`,訊息顯示 U+0061。
   - 另外日文 IVS(`葛\U000E0100`)修前修後都被擋,屬於 ⚠:是否算「正常日文」要人裁。
severity: minor
   - blocking: 否
   - 引句:「return next((c for c in v if unicodedata.combining(c))」
   - file: `scripts/lumos:7017`
   - 歸因:未判定。

9. 圖譜與程式對不上
   - 對不上的有三處:
     - `lumos-cli-read.md` 的「2026-10-13 待決問題嚴格讀法」。
     - 計劃筆記的 S2 條款(「清單範圍外出現像題號的行(不論落在哪個欄位底下、題目行怎麼寫歪)」)。
     - 計劃筆記第 85 行「任何『鍵: 值』的鍵名…就拒讀」。
   - 程式只對非 pending 擁有者的清單項與決策行做鍵名檢查,頂格鍵(發現 1)與決策流式項(發現 2)都不查。
   - 筆記沒有說這兩處例外。照 CLAUDE.md 以程式碼為準,要立 Issue 記下筆記錯在哪,且不能拿這些句子當驗收依據。
   - 另外 `規格閘.md`、`lumos-cli-write.md` 這輪沒有和上面矛盾的句子。
severity: minor
   - blocking: 否
   - 引句:「★認題目靠鍵名、不靠題號長相★」
   - file: `scripts/lumos:7086`、`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:85`
   - 歸因:有證據的修復回歸(筆記宣稱比程式範圍大)。

**沒找到問題的部分**
- 題目鍵名用 `Id`、全形 `ｉｄ`、`"id"`、`id :`、`id` 加 NBSP 再冒號:全部在清單外被讀成題目並拒讀。
- 西里爾 `і` 和中間夾零寬字元的 `id` 不會被認成題目鍵。標準 YAML 也不會把它當 `id`,可接受。
- 以下 block scalar 寫法一律當文字:`id: |` 後接 `- id: Q2`、`|2`、`|+`、`>- # c`。
- 5 萬字元的看不見字元連續序列、3000 題、2 萬行,耗時都在 0.2 秒內。
- 用 `new`、`set`、`append`、`decision-add`(內容含 `text: x`、`stage: 架構`)、`decision-amend`、`decision-supersede`、`question-add`、`question-set`、`summary-line`、`signoff`、`guard bind` 以各種順序組合,沒有哪一步讓清單變成讀不懂。含 `&`、`*`、`!`、`[`、`{`、`|`、`>` 開頭的值也都沒問題。
- 用 PyYAML 對 6000 個隨機結構做比對。縮排的 `- id:`、流式 `{…}`、縮排的鍵,只要在有 `pending_questions` 的清單裡,全都被拒讀。漏的只有發現 1 和發現 2 那兩類。
- 沒有 `pending_questions` 欄位標頭時,放在 `meta:` 底下的題目形狀不會被掃描。這是設計取捨,沒有列為發現。
- 阿拉伯文、希伯來文、泰文、天城文、藏文、韓文、日文,以及國旗、鍵帽、膚色、家庭、職業 ZWJ、`❤️‍🔥`,都沒被誤擋。

**三問**
1. 原問題的修復效果:縮 2、3、4 格或掛在其他欄位底下的題目、大小寫鍵名、全形鍵名、流式清單、block scalar 內文,實跑都有效。證據是修前修後 `pq_parse` 對拍,以及 6000 筆隨機組合。缺口是頂格鍵(發現 1)與決策流式項(發現 2)。看不見字元那邊,DICP 全表加位置規則有效,但誤擋了蒙古文、舊式 Malayalam、波斯文(發現 3),字母間隙的通道也沒封(發現 4)。
2. 修補處的相鄰路徑:工具指令的正常流程仍成立,repo 1826 篇筆記加一題都讀得懂。已確認的相鄰路徑問題是發現 5、6(手寫筆記的誤擋)與發現 7(`decision-add` 帶換行)。
3. 新發現的案例在修前修後各是什麼結果:發現 1、3、5、6 是修前正常、修後被擋或漏,屬於回歸。發現 2、4、7 是修前修後相同,屬於原有漏查。發現 8 與日文 IVS 修前修後都被擋。

這輪修補沒有達成統一判法:頂格題目鍵和決策流式項要補,看不見字元要改成依文字系統判,並放行蒙古文選擇符與詞尾 ZWJ、ZWNJ。

暫存位置:`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r7-邊界輸入-sonnet/`(含 `lumos_before`、`lumos_after`、`h.py`、`fuzz*.py`、`qa/` 與 `repo_lumos_*`),請編排者收貨後刪。
