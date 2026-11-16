severity: major

我把整份 spec 讀完,r2-delta 改過的段落特別細看,並對照 `/Users/enzo/harness/lumos-near-miss` 的程式碼、型錄和 `ast-grep 0.51.2` 逐項驗過。以下是檔級最高 severity(major)和 8 條 finding,其中 2 條 blocking。

**已讀、無 finding 的段落**
- 白話、舊否決比對、不做、依據來源、回退(5 條 `check.py` 旗標、規則對列號、列數三項檢查都核對過存在)、天花板:已讀,無 finding。
- 範圍 1 的欄位值:已讀,無 finding。
  - 型錄現況是 C-1 到 C-31、〈統計〉寫「31 列」、「14 列」,與 spec 相符。
  - D-5、D-6、D-32 都存在。
  - `row["dt"]` 在 `scripts/lumos` 裡沒有程式讀它,新列不會連動。
- 範圍 4 的 `check.py` 白名單:`CHOICE_CATEGORIES`、`CHOICE_ANCHORS`、`choice_tables`、`choice_sample_problems` 都在,把 NUL 加在尾端不會動到第一版的相對順序。
- 新事件欄位的相容性:`_choice_event_extra` 已帶 `row` 和 `new_sha`,`_GOV_FIELD_TYPES` 也已登記 `new_sha`,spec 沒有加任何新欄位,舊讀者不受影響。
- 固定席(規格閘、kotlin規則包)逐條判:這份設計不破壞兩篇筆記宣稱的行為。
  - 規格閘:`dedup` 的 token(choice-kill 事件用隨機碼、放行事件用 `檔:fp`)不變,第一版「同鍵最新一筆」處置判法不變,所以不影響。
  - kotlin規則包:規則 id 等於列號的 1:1 對應由 `check.py` 的 `_choice_rules_match` 守住,新增 `nul.yml` 與 `api.yml` 補的規則仍在這個機制內,所以不影響。
  - 但兩篇各有一處措辭會過期(見 i6)。

---

**i1. 範圍 3「`_CHOICE_OP_RE` 最前面加 `?:`」會讓既有的優先序計算 KeyError 崩潰**
severity: major
blocking: 是。照 spec 實作就做出會崩的系統,而且崩在常見寫法 `flag ?: false && other` 上。
- spec 段落:範圍 3 第 1 條、〈用詞〉`?:` 的錨點。
引句:「`_CHOICE_OP_RE` 最前面加 `?:`。」
- 問題:`_CHOICE_OP_RE` 不只用在 `_choice_anchor`,`_choice_top_prec` 也用它切運算子,然後直接取 `_CHOICE_PREC[m.group(0)]`。`_CHOICE_PREC` 沒有 `?:` 這個鍵。
  - 現況下 `?:` 不在正規式裡,所以 `_choice_top_prec("x ?: y")` 回 0(一律加括號),該函式的 docstring 也寫「有表外的運算子(?:、..)回 0」。
  - 加進正規式後,只要 LCR(`&&`、`||`)的運算元頂層有 `?:`,`_choice_swap_edits` 呼叫 `_choice_top_prec` 就丟 KeyError。
  - 因為 `?:` 優先序高於 `&&`、`||`,`a ?: false && b` 的 `$A` 就是 `a ?: false`。
  - spec 說「第一版各列的運算子位置不會變成 `?:`」,只對錨點位置成立,漏了這條計算路徑。S7 又排除含 `?:` 的行,所以守不到。
- 重現:
  ```
  python3.14 /tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/整合-sonnet/t2.py
  ```
  輸出:
  ```
  0 [('mutant', 'C-9')]
  1 CRASH KeyError('?:')
  ```
  這是把 `m._CHOICE_OP_RE` 換成含 `?:` 的版本後,對 `val ok1 = flag ?: false && other` 跑真實 `ast-grep` 加 `_choice_file_points` 的結果。
  - 單點驗證:`m._choice_top_prec("x ?: y")` 加之前回 0、加之後丟 KeyError。
- 佐證:
  - file: `scripts/lumos:77177` 到 `77190`(`_choice_top_prec` 取 `_CHOICE_PREC[...]`)。
  - file: `scripts/lumos:77877`(`_CHOICE_OP_RE` 定義)。
  - file: `scripts/lumos:77293` 到 `77306`(`_choice_swap_edits` 的呼叫端)。
- 建議:`?:` 另用獨立正規式只給 `_choice_anchor` 的 `?:` 列使用,或同時在 `_CHOICE_PREC` 補 `?:` 的層級並更新 `_choice_top_prec`。
- 另需補一條先紅的測試:LCR 運算元含頂層 `?:`。

**i2. 範圍 5「依列號」統計:資料來源與排序鍵跟程式現況對不上**
severity: major
blocking: 是。照字面做拿不到 `new_sha`,終態又沒有可判的先後,RETIRE-IF 要讀的數字會算錯。
- spec 段落:範圍 5 前三條、S8 預期值表、RETIRE-IF。
引句:「吃已去重的統計列(`_render_gov_choice` 收到的那份,不重讀帳)」
- 問題 a:spec 要求「吃已去重的統計列,不重讀帳」,並以 `(檔, 行指紋, new_sha)` 為一個壞法。但 `_gov_row` 的 `ck` 只收 `file, fp, killing_test, changed, mutant_lines, secs, reasons`,`new_sha` 沒進統計列。範圍 5 沒有列出要擴 `_gov_row` 的映射。
- 問題 b:「取時間最新那筆當終態」的時間欄是 `ts`,而 `ts` 是 HEAD 的 commit 時間,不是事件時間。
  - 同一個 HEAD 上先寫 `survived`、再用 `situation-rule` 寫 `killed`,兩筆 `ts` 相同。
  - 去重前用 `sorted(rows, key=ts)`,同值時照載入順序(版控帳與本機帳各自讀入),跨帳順序不確定。
  - 第一版處理同一件事的慣例是 `_choice_ledger_index` 的「檔內順序」,spec 沒說沿用哪一種。
  - S8 的「乙 先存活後被殺掉」輸入沒有指定時間,實作者自己建夾具就會過,但真實帳上同 HEAD 會算錯。
- 問題 c:放行事件 `ck_waive` 本來就帶 `row`(放行當下挑到的壞法列號),`c["shape"]` 也在用它。spec 改成「接到之前最近一筆存活事件取其 `row`」,沒說兩者不同時以哪個為準。放行事件與存活事件同樣有 `ts` 相同的順序問題。
- 問題 d:「基準沒綠所以沒跑」要排除,程式裡的實際原因字串是「基準不綠沒跑」(`reason` 取冒號前整段)。spec 沒說用逐字比對。另外「壞法數」是否含這類也沒定,但 RETIRE-IF 的分母「至少 5 個壞法」要靠它。
- 佐證:
  - file: `scripts/lumos:18424`(`ck` 欄位清單,沒有 `new_sha`)。
  - file: `scripts/lumos:18486` 到 `18488`(依 `ts` 排序後去重)。
  - file: `scripts/lumos:74623`(註解寫 `ts` 是 HEAD commit 時間,`written_at` 才是事件時間)。
  - file: `scripts/lumos:77705` 到 `77716`(`_choice_ledger_index` 用檔內順序)。
  - file: `scripts/lumos:77862`(`"基準不綠沒跑"`)。
  - file: `scripts/lumos:18426`(`ck_waive` 含 `row`)。

**i3. 既有測試 `t_choice_table_missing` 寫死「31 列」,型錄改成 37 列後會紅;spec 沒列出要改的既有測試**
severity: minor
blocking: 否。跑測試立刻看得到,不會做出壞系統。
- spec 段落:範圍 1 最後一條(31 → 37)、驗收條款開頭「測試做法」。
引句:「的選擇點表列數(31 → 37)與括號裡的說明一起改(check.py 會比對列數)」
- 問題:`kp.stats_problems(real.replace("- 選擇點表:31 列", "- 選擇點表:30 列"), ...)` 在型錄改成 37 列後,`replace` 沒換到任何字,文字等於正確值。`stats_problems` 就不回問題,`check("S23 〈統計〉選擇點表列數寫錯 → 報重數不對", st != [])` 會紅。
- spec 只列新測試,沒有「既有測試哪些會因計數或類別數變動」的清單,這是我要查的重點之一。
- 佐證:file: `scripts/test_lumos.py:143765`。另外 `143755` 的 `>= 31` 不受影響。
- 建議:這條測試改成從 `real` 解析出實際列數再改寫,或在範圍 1 列一句要同步改的既有測試。

**i4. 範圍 2 `?:` 的 pattern 在 YAML 裡必須加引號,spec 沒寫**
severity: minor
blocking: 否。實作者第一次跑 `ast-grep` 就會碰到,不會做出壞系統。
- spec 段落:範圍 2 `nul.yml` 第一條。
引句:「`?:` 用 pattern `$A ?: $B`(只寫節點種類 `elvis_expression` 拿不到 `$A`、`$B`,壞法與型別前提都會失效)」
- 問題:`pattern: $A ?: $B` 的 `?: ` 讓 YAML 判成巢狀 mapping,`ast-grep` 回 `mapping values are not allowed in this context`。
- 重現:在 `/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/整合-sonnet/x/` 下用未加引號的 `r.yml` 跑 `ast-grep scan -r r.yml --json=stream t.kt`,得到上述錯誤。改成 `pattern: '$A ?: $B'` 後正常,`$A`、`$B` 都抓得到,巢狀 `x ?: y ?: z` 回兩個命中。
- 附帶確認:`?.` 前面是行註解時,規則可用 `follows: {kind: line_comment}` 排除,這部分可行。區塊註解要另補 `multiline_comment`。

**i5. 「S1–S4 用合成型錄列、撤列不會讓它們紅」與「規則對列號 1:1」、回退步驟不一致**
severity: minor
blocking: 否。撤列時測試紅會被推送閘擋住,屬於回退步驟不完整,不會讓系統壞掉。
- spec 段落:驗收條款開頭「測試做法」、回退第 1 項。
引句:「S1–S4 用測試裡合成的型錄列與 Kotlin 片段(不讀真型錄,撤列不會讓它們紅)」
- 問題:S1–S4 要用真的 `ast-grep` 掃新規則才會挑出壞法,規則檔來自真實的 `rules-choice/`。
  - `_choice_rules_match` 要求型錄列和規則檔雙向 1:1。合成型錄只放幾列、卻掃真實規則目錄,會報「規則在型錄沒有對應的列」。
  - 若測試複製整個規則目錄(像 `t_choice_table_missing` 那樣 `copytree`),規則是複本,真實列撤掉後測試才不紅。spec 沒說這樣做。
  - 若直接讀真規則,單列撤掉(回退第 1 項要求連規則一起拿掉)後 S1–S4 就紅,「撤列不會讓它們紅」不成立。
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:1451`(`_choice_rules_match`)。
- 建議:在測試做法裡明寫「S1–S4 的規則檔以測試內嵌文字寫進暫存目錄」,或把撤列時要同步改的測試列進回退。

**i6. 範圍 6 文件同步遺漏三處,其中一處是新樣本放哪個檔沒講清楚**
severity: minor
blocking: 否。只是筆記過期或測試常數漂移,實作者做出的系統本身沒壞。
- spec 段落:範圍 2 `samples/` 條、範圍 6、S7。
引句:「〈天花板〉第 1 條補指向這份。」
- 問題:
  - `Systems/規格閘.md` 的 WHY 第 66 行寫「選擇點以那一列的錨點(運算子、方法名)所在行判在不在改到的行上」。這份計劃改成「引數」錨點以節點範圍內任一改動行判定,那句會失真。範圍 6 只要求補「依列號」口徑,沒要求改這句。
  - 第一版計劃範圍 1 寫死類別清單是六類、PRIOR-ART 還有「第六類」,加 NUL 後變七類,範圍 6 只說補天花板第 1 條。
  - 「補每列的命中與不命中樣本」沒指定寫進哪個檔。S7 要把「第一版既有樣本行」的行指紋釘成常數,行指紋含前後各 2 行。若新樣本插進既有的 `choice.kt`、`chain.kt` 等檔,鄰近行的指紋會變,S7 的常數就失效。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:66`。
  - file: `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:59`。
  - file: `scripts/lumos:77308`(`_choice_fp`,行指紋含前後各 2 行)。
- 建議:寫明新樣本進新檔(例如 `batch2.kt`),並在範圍 6 補上這兩條筆記更新。

**i7. `.let` 排除條件「整個呼叫單獨成一個陳述」跟白話段「只收回傳值有被用到的」不是同一件事**
severity: minor
blocking: 否。多挑或少挑壞法,最差落成放行或漏判,不會壞掉。
- spec 段落:白話第二批清單第 2 項、範圍 2 `api.yml` 補四條的 `.let`。
引句:「`.let`(排除整個呼叫單獨成一個陳述的寫法,例 `x?.let { show(it) }`——回傳值沒人用,換成 `also` 必然等價)」
- 問題:當 `x?.let { … }` 是 lambda 的最後一個陳述、`when` 或 `if` 的值、或表達式本體 `= x.let { }` 時,它仍是「單獨成陳述」,但回傳值被拿去用。
  - 第一版的 C-18 為了這個情況,在 `sbr.yml` 寫了 `value-pos` 與 `nthChild reverse` 的整套判法。
  - spec 只說「照 C-18 先例用 `not:`」,沒說是否重用 `value-pos` 那段。
  - 單純「陳述清單的直接子節點就排除」會把 lambda 最後一行的 `.let` 也排除(漏判);不排除又違反「回傳值沒人用」的描述。
- 佐證:file: `configs/ast-grep/kotlin-choice/rules-choice/sbr.yml`(`utils: value-pos`)。
- 建議:明寫 `.let` 沿用 `value-pos`(或明寫「只排除父節點是 `statements` 且不是 lambda 最後一行」)。

**i8. 兩個新補進來的未查證宣稱**
severity: minor
blocking: 否。只是依據寫得不準,不影響設計與實作。
- spec 段落:實務隱患「挑壞法時限」的最後一句、依據來源表第 3 列。
引句:「掃描時限 `_KT_SIT_BUDGET` 照第一版(ast-grep 多兩支規則實測持平)」
- 問題 a:「掃描時限 `_KT_SIT_BUDGET` 照第一版(ast-grep 多兩支規則實測持平)」。
  - 實際新增是 6 條規則(`nul.yml` 2 條加 `api.yml` 4 條),不是「兩支」。
  - 沒有給實測數字,S9 與範圍 7 量的只有「有選擇點行比例」和「最大檔挑壞法耗時」,沒有量掃描耗時。
  - `_KT_SIT_BUDGET` 在程式裡是 30 秒,超過就算不出來,所以掃描時間才是這份設計新增規則最直接影響的量。
- 問題 b:依據表寫「`?.` 換行寫在續行是官方建議寫法」,出處列 `kotlinlang.org/docs/reference/grammar.html`。我依既有知識判斷(沒有實際開網頁驗):文法頁只說明 `?.` 前面可以有換行,「建議」出自 Kotlin 的 coding conventions(換行時把 `.`、`?.` 放在下一行)。這條宣稱是 spec 自帶的,出處不對應。
- 佐證:file: `scripts/lumos:40217`(`_KT_SIT_BUDGET = 30.0`)。
- 建議:S9 加一欄「掃描耗時」,依據表把出處換成 coding conventions 頁並標上述判斷依據。

---

**實務隱患鏡頭**
- 併發與交易、金流、對外送出:無。這個 repo 是單人工具鏈,spec 也已排除,我沒有發現新增的寫入路徑或外送路徑。
- 不可逆:無。治理帳逐筆追加,spec 沒有改事件格式,處置以 (檔, 行指紋) 為單位續用。
- 資源與時限:有一項。新增 6 條規則讓掃描量上升,但 S9 沒有量掃描耗時(見 i8)。
- 崩潰:有,見 i1。

可重現的暫存檔在 `/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/整合-sonnet/`,收貨後由編排者刪除。

最嚴重 severity: major,blocking 共 2 條(i1、i2)。
