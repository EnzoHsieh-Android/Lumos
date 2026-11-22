severity: minor

整合鏡頭的結論:這份計劃對程式碼端的接線(`choice_tables` 讀表、`_choice_anchor` 與 `_choice_api_edits` 與 `_choice_also` 的簽名、統計列數的核對、樣本標記)大致對得上。我找到 7 條文件與型錄同步上的缺口,都是只會讓三個月後的接手者讀到過期說法,不會讓實作做錯,沒有一條需要擋。

## i1 文件同步清單漏了型錄說明段的欄位定義與 Systems 筆記的正文
severity: minor
blocking: 否 判準:不改也能做出可用的系統,只是型錄與筆記會留下過期敘述,接手者讀到錯的語意。
- 位置:範圍 1「說明段同步」與範圍 6「文件」。
- 問題:說明段與筆記正文有三處,上線後會跟事實不符,清單都沒列。
  - 型錄〈選擇點表〉說明段的欄位定義寫「API 列是換成的方法名」,「(拿掉呼叫)」寫成刪掉 `.方法名()`。第三批的候選有 `0`、`DEFAULT`、`coroutineScope`、`kotlin.coroutines.EmptyCoroutineContext`,都不是方法名。第三批的 `(拿掉呼叫)` 也不再只刪 `.方法名()`,而是從接收者結尾刪到呼叫結尾。
  - Systems/kotlin規則包正文說 api.yml「多半命中方法名那一段;第二批的 LaunchedEffect、remember 命中引數清單」。第三批會讓 api.yml 多出運算元起始的識別字、整個呼叫命中和 `BufferOverflow.` 後那一段。
  - 同一篇正文逐檔列出樣本檔,其中有 choice-batch2.kt 和「另開新檔是因為行指紋」的說明,沒有 batch3。
  - Systems/規格閘 的 WHY 列舉的錨點只到「運算子、方法名、安全呼叫符、引數」。範圍 6 只讓它補「整個呼叫命中」一句,運算元起始與陳述起始本來就沒寫。
- 失敗場景:三個月後接手者照型錄說明段判斷 `replay` 那一列的候選 `0` 怎麼換,或照 Systems 筆記判斷 api.yml 的命中形狀,得到錯答案。第二批的範圍 6 明列了要改掉「寫死的那句與逐檔列規則的那段」,第三批沒有照做。

引句:「Systems/kotlin規則包 `about_code` 加 `samples/choice-batch3.kt`,補一條 WHY 行」
- file: `skills/kotlin-idioms/checks-catalog.md:1658`
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:150`
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:153`
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:66`

## i2 「對應決策表」欄的取捨規則沒有一致套用,「互指」也只有單向
severity: minor
blocking: 否 判準:這一欄是自由文字,沒有任何機械檢查讀它,不會讓系統壞掉。
- 位置:範圍 1 的各列對應決策表,以及〈舊否決比對〉。
- 問題:
  - LAZY 列的決策表填 `—`,理由是型錄觸發字表標「決策不問」。但 `replay` 在觸發字表也是「決策不問 FLOW-25」,`BufferOverflow` 是「決策不問 代碼審」。計劃卻把它們填成 D-7、D-15、D-16。D-16 的觸發字是 buffer、conflate、collectLatest 那幾個,不含 BufferOverflow;D-7、D-15 的觸發字也不含 `replay`。
  - `coroutineScope` 列只填 D-8、D-9,但觸發字表給它 D-1、D-8、D-9。
  - 〈舊否決比對〉說決策表重疊的列「用列號互指」。實際上只有選擇點列單向指向 D-n,決策表的 D 列沒有任何 C-n 引用,範圍也沒有改 D 列。
- 失敗場景:實作者無從判斷第三批其他列(replay、BufferOverflow)該照 LAZY 的規則填 `—`,還是照其他列填 D-n。填法不一,日後對照決策表時查不到反向連結。

引句:「候選互換、對應決策表 D-16」
引句:「跟決策表重疊的列(D-4、D-7、D-8、D-9、D-11、D-15、D-16、D-17、D-26)用列號互指」
- file: `skills/kotlin-idioms/checks-catalog.md:1399`
- file: `skills/kotlin-idioms/checks-catalog.md:1110`
- file: `skills/kotlin-idioms/checks-catalog.md:755`
- file: `skills/kotlin-idioms/checks-catalog.md:1183`

## i3 RETIRE-IF 寫「同第二批」,但分母口徑與統計標題沒跟著同步
severity: minor
blocking: 否 判準:數字照樣印得出來,只是兩年內口徑的說法有可能分叉。
- 位置:RETIRE-IF 與範圍 5「統計沿用第二批,不改」。
- 問題:
  - 第二批的 RETIRE-IF 明寫「不適用算分母不算分子」,第三批只寫「同第二批」,卻把括號省掉。
  - `gov --stats` 依列號的輸出標頭寫死「Projects/選擇點表第二批常見誤用寫法_計劃 範圍 5」。
  - Systems/規格閘 的 WHY 說這條是「給第二批的 RETIRE-IF 讀」。
  - 第三批的人照 `gov --stats` 看數字時,讀到的出處是第二批。
- 失敗場景:兩個月後有人判斷第三批某列「等價 4 筆、不適用 3 筆」該不該撤,算不出分母。
- 補充:`gov` 預設 `--since 90`,兩個月的讀取窗夠用,這一點沒問題。

引句:「RETIRE-IF: 同第二批:上線日(寫進第三批的 Verification)起滿兩個月」
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:80`
- file: `scripts/lumos:18007`
- file: `scripts/lumos:18486`

## i4 驗收條款 S6 的「不收清單不再有 coroutineScope」沒定義抽取範圍,會跟翻案句自相衝突
severity: minor
blocking: 否 判準:只影響測試怎麼寫,實作者看第一次紅燈就會發現。
- 位置:範圍 1 說明段同步,與驗收條款 S6。
- 問題:
  - 範圍 1 要求在「不收」清單拿掉 `coroutineScope`/`supervisorScope`,同一段補一句翻案理由與日期,這句話本身會再次出現這兩個名字。
  - 現有的「不收」那句位在同一個說明段段落,S6 沒說測試抽哪一段。
  - 回退第 2 項又要把這兩個名字加回同一份清單。
- 失敗場景:實作者對整個說明段做 `not in`,翻案句會讓自己的測試紅。反過來若用「第一個冒號到第一個句號」切段,切法一改測試就變成空驗證,不再抓得到「清單漏拿」。

引句:「拿掉 `coroutineScope`/`supervisorScope` 並補一句翻案理由與日期」
- file: `skills/kotlin-idioms/checks-catalog.md:1660`

## i5 LAZY 列的業務問題與型錄 CO-18 的既有判斷沒對齊
severity: minor
blocking: 否 判準:不影響機制運作,影響的是這一列的行為差異欄寫得準不準,以及基準不綠的比例。
- 位置:〈白話〉延後啟動、〈依據來源〉表的 LAZY 列。
- 問題:
  - 計劃把問題寫成「條件不成立時能不能根本不做」,依據欄寫「不 await 就不做」。
  - 型錄 CO-18 把 `coroutineScope { val d = async(start = LAZY){…}; if (cond) d.await() }` 判為卡死:`coroutineScope` 會等所有子協程,沒啟動的 lazy 子協程讓它永不結束。
  - 計劃只在範圍 1 把 CO-18 當「相關檢查」,沒說明「不做」這一邊在 `coroutineScope` 裡本身就是已知缺陷。
- 失敗場景:作者為 `if (cond) d.await()` 補「cond 為假要不呼叫」的測試。基準版本在 `coroutineScope` 裡 cond 為假時會 hang,`runTest` 逾時,落成基準不綠或跑不出結果。這一列的跑不出結果比例被墊高,RETIRE-IF 用「超過一半」撤列時看到的是假訊號。

引句:「`CoroutineStart.LAZY` 的依序陷阱與不 await 就不做」
- file: `skills/kotlin-idioms/checks-catalog.md:299`

## i6 Verification 筆記與測試範本兩個交付物沒有對應的範圍條目
severity: minor
blocking: 否 判準:現在是缺了漏掉的風險,不改也能照第二批的慣例補上。
- 位置:RETIRE-IF、範圍 7、S8,以及〈實務隱患〉測試成本那一條。
- 問題 A,Verification:
  - RETIRE-IF、REVISIT、S8、〈回退〉都說要寫進「第三批的 Verification」(上線日、每列命中次數、撤列前的依列號數字)。
  - 範圍清單沒有「新建 Verification 筆記並掛上 Systems/kotlin規則包 的 `verified_by`」這一項。第二批的 Systems 筆記有掛 Verification 連結。
- 問題 B,測試範本:
  - 〈實務隱患〉測試成本把「這些寫法寫進型錄列的出處欄指向 test-templates.md 既有範本,沒有就由人放行」寫成已定案,範圍 1 沒有對應條目。型錄「出處」欄現行用途是來源引用,只要求非空。
  - 我查過 test-templates.md:只有 API-4 的 supervisorScope(連坐與不連坐)有範本。`replay`、`DROP_*`、`retry`、`mapLatest`、`LAZY` 都沒有範本。
- 失敗場景:九組裡八組沒有範本可指,實際上變成全靠人放行。「不是需求」放行偏多會直接撞到 RETIRE-IF 的八成門檻,第三批多數列容易被誤撤。

引句:「這些寫法寫進型錄列的出處欄指向 skills/kotlin-idioms/test-templates.md 既有範本,沒有就由人放行」
- file: `skills/kotlin-idioms/test-templates.md:1036`
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:110`

## i7 既有測試 `t_choice_samples_batch2` 把 C-32 以後所有列都當第二批,第三批的缺口會紅在第二批測試上
severity: minor
blocking: 否 判準:會紅的只有實作中途或樣本不齊的情況,錯誤訊息標籤誤導,不會做出壞系統。
- 位置:範圍 4、驗收條款 S5 與 S7。
- 問題:
  - `t_choice_samples_batch2` 篩問題的條件是 `x[0] in have - {C-1..C-31}`,也就是任何 id 不在 C-1 到 C-31 的列都算第二批。第三批加了 C-38 以後,第三批某列缺 HIT 或範圍 7 撤列後重編號,都會在「第二批樣本」這支測試裡以第二批名義變紅。
  - 計劃沒有要求把這個硬寫的 31(實際涵蓋 C-32 到 C-37)改成 C-37。
  - S7 要求的「加入前結果」還需要把 choice-batch2.kt 一起釘住。`_CB2_S7_PIN` 只涵蓋六個舊檔,不含 choice-batch2.kt。計劃已寫「實作第一步先跑一次」,所以這條只是提醒要把 choice-batch2.kt 納入。
- 失敗場景:範圍 7 擋下一列、後面往前補號時,第三批的 HIT 標記沒跟著改,紅燈出現在第二批的測試裡,排查方向被帶偏。

引句:「當第三批樣本檔跑過選擇點樣本核對,每條第三批規則 應 命中該命中的、不命中不該命中的」
- file: `scripts/test_lumos.py:146545`
- file: `scripts/test_lumos.py:146550`

## 各節已讀結果(無 finding 的部分)
- 〈白話〉、〈舊否決比對〉、〈用詞〉、〈範圍〉2 到 3 與 5 到 7、〈不做〉、〈回退〉、〈天花板〉:已讀,無其他 finding。
- 已核對成立的宣稱:
  - 型錄「選擇點表:37 列」與 `choice_tables` 重數、`已撤列號:(無)` 的現況。
  - `_choice_candidates` 能收 `0`、`DEFAULT` 與 `kotlin.coroutines.EmptyCoroutineContext`;`_CHOICE_IMPORT_RE` 收得下計劃的 import。
  - 現有的 `retry` 樣本都是參數名,不是呼叫,不會被新規則誤命中。
  - 對 `$A.retry($$$B)`、帶 lambda 的版本與 `?.` 版本,ast-grep 0.51.1(CI 釘版)與 0.51.2(本機)輸出一致:`$A` 範圍、命中行與 `Result.retry()` 都一樣。
  - 推送前那一道對規則包樣本檔不當產品碼(`_RULEPACK_SAMPLE_RE`),所以 `samples/choice-batch3.kt` 不會被那一道掃。
  - 現有 `_choice_anchor` 的呼叫端沒有簽名衝突,`_choice_api_edits` 與 `_choice_also` 沒有測試直接呼叫。

## 實務隱患鏡頭
- 編不過與等價存活:計劃已涵蓋,我沒有新增。
- 併發:單人單機依序操作,判範圍外。
- 金流與對外送出:只改型錄、規則與產壞法程式,無。
- 不可逆:治理帳逐筆追加、撤列後處置續用,計劃已寫,無新增。
- 守衛面:計劃自己標「不排除」並走設計審,合理。新增的風險只有 i7(測試標籤誤導)與 i5(基準不綠墊高跑不出結果比例)。

## 圖譜節點逐條判
- Systems/kotlin規則包(計劃連結):不影響它宣稱的合約。它沒有 KEY、沒有合約行,第三批只加規則與樣本。但正文有兩處會過期(i1),計劃要改的 about_code 與 WHY 只是其中一部分。
- Systems/規格閘(計劃連結,20 行 KEY):不影響。計劃不改處置鍵 (檔, 行指紋)、一行一個壞法、回報上限與殺傷力判定。「依列號」的口徑照舊,但 WHY 與輸出標頭仍寫第二批(i3)。
- 事故節點:計劃提到的 scripts/lumos 牽連 229 篇,太泛不列。整合鏡頭另外查過「規則包樣本被當產品碼」那則事故,選擇點那一道已排除規則包樣本,所以對這份計劃不影響。

總結:最高嚴重度 minor,blocking 共 0 條
