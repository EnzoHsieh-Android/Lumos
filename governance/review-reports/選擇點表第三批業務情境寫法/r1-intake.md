preflight-4: ran

# 選擇點表第三批業務情境寫法 r1 收貨

## 首輪前掃(四項)

派一席 sonnet 對計劃初稿(提交 9de4ed9c6)掃四項,共 9 條命中,全部直接修進計劃真檔,不算 findings。計劃沒有「核心裁定」節,沒有命中需要升格成正式 finding 交席位審的。

- ① 未定義的詞 1 條:「跑不出結果」母計劃〈用詞〉沒有定義(第二批沿襲)→ 〈用詞〉另立一條,指向 Systems/規格閘 的統計口徑。
- ② 壞引用 1 條:`CoroutineStart.LAZY` 列對應決策表寫 D-1,D-1 是「互不依賴的一次性呼叫」、沒有 LAZY → 改成 —(觸發字表標決策不問;相關檢查 CO-18),互指清單拿掉 D-1。
- ③ 範圍自相矛盾 3 條:擴充處數「兩處」對範圍 3 實際改三支函式 → 改「三處」並逐支寫走不到的條件;「子協程」定義只寫直接呼叫、跟範圍 2 迴圈呼叫不一致,「迴圈呼叫」沒定義 → 〈用詞〉改寫子協程、新增迴圈呼叫;範圍 1 漏寫 `singleOrNull` 列的 import 與 `single`、`singleOrNull` 的對應決策表 → 補上。

## 語意類命中(修改前 → 修改後)

- ④-1 `_choice_api_edits` 拿不到 `$A`:
  - 修改前:「`_choice_api_edits` 的 `(拿掉呼叫)`:命中帶 `$A` 時刪掉 `$A` 結尾到命中結尾那一段」
  - 修改後:「`_choice_api_edits` 的 `(拿掉呼叫)`:現在只收 `s, e`,`_choice_anchor_edits` 要把命中的 `mv` 一併傳進去;命中帶 `$A` 時刪掉 `mv["A"]` 結尾到 `e` 那一段」
  - 依據:`scripts/lumos` 的 `_choice_api_edits(b, s, e, op, tpl)` 與呼叫端 `_choice_anchor_edits` 只傳 `s, e`。
- ④-2 `_choice_also` 缺命中範圍、`op` 為 None 先被擋:
  - 修改前:「`_choice_also`(補 import)多收錨點「運算元起始」而候選是單一識別字的列(作用域兩列):原寫法取命中節點文字」
  - 修改後:「`_choice_also`(補 import)多收命中範圍 `(s, e)`:…原寫法取 `b[s:e]`,不再要求 `op` 不是 None(運算元起始的 `op` 一律是 None);…`_choice_pick` 呼叫它的地方跟著傳範圍」
  - 依據:`_choice_also(text, row, b, op, new)` 開頭 `row["anchor"] != "方法名" or op is None` 就回 None。
- ④-3 換行寫法的壞法身分:
  - 修改前:預期值表 S2「第二行整段刪掉,第一行不動;錨點行是第二行」
  - 修改後:「結果是第一行原樣、第二行消失;錨點行是第二行,壞法的 `old` 含第一、二兩行」;〈用詞〉整個呼叫命中補一句說明這是母計劃「只有錨點那一行」的例外
  - 依據:`_choice_identity` 用編輯起點的行當 `old` 的起行,編輯起點是 `$A` 結尾(上一行行尾)。
- ④-4 `replay` 命中節點:
  - 修改前:「`replay` 兩列:value_argument 的名字是 `replay`、值是整數字面值 `1`(或 `0`)」
  - 修改後:「`replay` 兩列:命中節點是整數字面值 `1`(或 `0`)本身,用 `inside` 限定它的外層 value_argument 名稱是 `replay`」
  - 依據:通用路徑把整個命中節點換成樣板;命中整個引數會變成 `MutableSharedFlow<Int>(0)`、丟掉 `replay =`。

前掃另驗證過、跟計劃一致的:方法名與運算元起始錨點現行算法、通用路徑樣板沒有 `$` 時整個節點換成樣板、`mv` 來自 ast-grep 的 metaVariables(`$A.retry($$$B)` 單行、換行、帶 lambda、`?.` 實跑命中)、check.py 類別與錨點白名單不用改、型錄「不收」行與統計行與 `已撤列號:(無)` 的現況、`_SrcOnly` 存在。

## 收貨(六席)

席位:正確性、邊界、整合、資源併發、回滾、架構對齊,全 sonnet,全新代理,各自只讀凍結快照 r1-snapshot.md(sha256 91422dc4…)。六份報告收齊後才一次從逐字稿存檔;收齊前沒動計劃真檔與工作目錄(派工單 r1-dispatch.json 是編排者檔,收貨時發現寫成清單、被 seat-check 拒讀,改寫成物件格式,席位材料內容不變)。
收貨三道:六份都已是正規化格式;引句全數錨定(正確性席首交一句引句都沒有,退回該席只補三行引句、其餘一字未改後重交,錨定通過);refcheck 全 ok;seat-check 對派工單判 vacuous 豁免(同代碼審)。
reflog 只有編排者自己的提交;席位沒留 worktree;這一輪臨時目錄收齊後已刪。

發現共 25 條:正確性 c1–c3、邊界 b1–b7、整合 i1–i7、資源併發 r1–r2、回滾 rb1–rb4、架構對齊 a1–a2。blocking 4 條(a1、b1、b2、rb1)。

## 重現表

| id | 席 | 等級 | 編排者重現 | 處置 |
|---|---|---|---|---|
| a1 | 架構對齊 | major | HIT(讀碼):`_choice_anchor`、`_choice_anchor_edits` 都依 `row["anchor"]` 分支,第二批的「安全呼叫符」「引數」是另立錨點;計劃讓 retry 沿用「方法名」靠有沒有 `$A` 分流 | 折:新錨點「整個呼叫」 |
| a2 | 架構對齊 | minor | HIT(讀文件):第二批範圍 6 有母計劃天花板與規則包逐檔段 | 折:範圍 6 補齊 |
| b1 | 邊界 | major | HIT:kotlinx.coroutines MutableSharedFlow 官方文件寫明非 SUSPEND 只在 replay>0 或 extraBufferCapacity>0 時支援;席位另以 1.11.0 jar 實跑 | 折:範圍 1、2 排除帶 onBufferOverflow 沒帶 extraBufferCapacity 的呼叫 |
| c1 | 正確性 | minor | HIT:同 b1(兩席獨立) | 折:同 b1 |
| b2 | 邊界 | major | HIT:編排者用先前試做的規則跑 `supervisorScope { val x = coroutineScope { async { 1 }.await() }; val y = coroutineScope { async { 2 }.await() } }`,外層第 1 行命中 | 折:子協程改成最近一層 lambda 的定義 |
| b5 | 邊界 | minor | HIT(現象,同 c2):同一陳述兩個 async、for、repeat 不命中 | 折:〈用詞〉作用域有兩個以上子協程、迴圈呼叫補 repeat 與 for/while |
| c2 | 正確性 | minor | HIT:同 b5 | 折:同 b5 |
| b3 | 邊界 | minor | HIT(席位 ast-grep 實跑,同 c3):夾註解不命中 | 折:錨點改用 `_CHOICE_GAP_SKIP_RE`;樣式本身不命中寫進天花板 |
| c3 | 正確性 | minor | HIT:同 b3 | 折:同 b3 |
| b4 | 邊界 | minor | HIT(席位實跑 `$A` 是完整接收者) | 折:排除接收者最後一段是 Result |
| b6 | 邊界 | minor | HIT(讀計劃):只排除 .await() | 折:補 .join(),只看直接接在後面那一層 |
| b7 | 邊界 | minor | HIT(席位實跑) | 折:限定 MutableSharedFlow 與 .shareIn;位置引數寫進天花板 |
| i1 | 整合 | minor | HIT(讀文件):型錄欄位說明、規則包正文兩處、規格閘 WHY | 折:範圍 1 說明段、範圍 6 |
| i2 | 整合 | minor | HIT(讀型錄觸發字表) | 折:定「對應決策表」填法;互指改成單向的實際說法 |
| i3 | 整合 | minor | HIT(讀程式與筆記) | 折:RETIRE-IF 補不適用;範圍 5 補規格閘 WHY 一句 |
| i4 | 整合 | minor | HIT(讀計劃) | 折:翻案理由另寫一行、S6 只看 `不收(` 開頭那一行 |
| i5 | 整合 | minor | HIT(讀型錄 CO-18) | 折:實務隱患補一條,守門測試寫法進型錄行為差異欄 |
| i6 | 整合 | minor | HIT(讀 test-templates.md 只有 API-4 範本) | 折:範圍 6 新開 Verification;範本不在這批補,寫 REVISIT |
| i7 | 整合 | minor | HIT(讀 `t_choice_samples_batch2` 的 C-1..C-31 判法) | 折:範圍 4 改成只看 C-32..C-37,S7 另釘 choice-batch2.kt |
| r1 | 資源併發 | minor | HIT(現象,席位 ast-grep 實測;極端深度) | 折:實務隱患記數字與「落成驗不了只提醒」 |
| r2 | 資源併發 | minor | HIT(讀 `_choice_file_points` 用 line..end_line 判 ERROR 交集) | 折:整個呼叫錨點改用錨點行到 end_line 判 |
| rb1 | 回滾 | major | HIT(讀測試):第二批 S6 測試 `if rid not in have: continue`,計劃 S5、S6 寫死第三批列 | 折:S5、S6 對表裡沒有的列跳過 |
| rb2 | 回滾 | minor | HIT(讀第二批回退第 2 項) | 折:回退第 2 項補齊 |
| rb3 | 回滾 | minor | HIT(讀 `_choice_disposition`) | 折:回退第 3 項寫明外溢與重看步驟 |
| rb4 | 回滾 | minor | HIT:同 i3 | 折:同 i3 |

## 分組(依根因)

- 錨點命名(a1):命中形狀不同 → 另立錨點,照第二批。
- 換完會建構就丟例外(b1、c1):排除會造出 trivial mutant 的寫法。
- 子協程怎麼數(b2、b5、c2):定義改成最近一層 lambda,補同陳述、for/while、repeat。
- 撤列與回退(rb1、rb2、rb3、rb4、i3):測試對撤掉的列跳過、回退善後補齊、門檻口徑補齊。
- 規則漏判與排除(b3、c3、b4、b6、b7、r2):各自補排除或寫進天花板。
- 文件同步(a2、i1、i2、i4、i6、i7、i5):範圍 1、4、6 與實務隱患補齊。
- 資源(r1):記實測數字,沿用驗不了只提醒。

## 先查世界

- PRIOR-ART:換完會建構就丟例外——kotlinx.coroutines MutableSharedFlow API 文件寫明「BufferOverflow.SUSPEND 以外的值只在 replay > 0 或 extraBufferCapacity > 0 時支援」、不支援的組合建構丟 IllegalArgumentException(https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow.html );變異測試文獻把「幾乎任何測試都殺得掉」的壞法歸 trivial mutant、沒有資訊量(Ammann 與 Offutt 教材 https://www.inf.ed.ac.uk/teaching/courses/st/2016-17/Mutest.pdf )。採用:事前排除那種組合。
- PRIOR-ART:最近一層 lambda——ast-grep 關係規則文件寫明 `stopBy` 收 "neighbor"、"end" 或規則物件,停下的那一層也算命中(https://ast-grep.github.io/guide/rule-config/relational-rule.html )。採用:`inside` 加 `stopBy: {kind: lambda_literal}`;排除 `stopBy: end`(會越過內層作用域,本輪已重現)。
- PRIOR-ART:錨點命名——專案內既有做法是第二批新增「安全呼叫符」「引數」兩個錨點、check.py 白名單加在尾端([[Projects/選擇點表第二批常見誤用寫法_計劃]] 範圍 3、4)。採用。
- 不加新機制的最小解:新錨點「整個呼叫」是唯一新增的機制;不加它的最小解(沿用方法名、靠 `$A` 分流)正是架構對齊席判的第二種做法,所以不夠。其餘折入只改規則條件、文件與測試範圍,不加新設定鍵、新帳欄或新指令。
