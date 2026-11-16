# 第二批計劃前掃報告(只讀)

被掃:`docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md`(repo /Users/enzo/harness/lumos-near-miss,掃描當下該檔在工作樹有未提交改動,以工作樹版為準)。
程式行號皆為 `scripts/lumos`(L)、`configs/ast-grep/kotlin-android/check.py`(C)、`scripts/test_lumos.py`(T)。

## ① 未定義的詞

1. 「類別」未定:第二批除 NUL 外,`let`、`combine`、`LaunchedEffect`、`remember` 各列填哪個類別(API?新類別?)計劃沒寫。
   - 原句:`api.yml` 補 `let`、`combine`(接收者寫法)、新增頂層 `combine` 呼叫的規則
   - 依據:`C:1392` CHOICE_CATEGORIES 只有 AOR/LCR/ROR/UOI/SBR/API;`L:77386` 類別是洗牌單位,填錯會改挑選順序。
   - 修改:〈用詞〉或〈範圍〉1 加一句「`let`、`combine` 列類別 API;`LaunchedEffect`、`remember` 列類別 ○○(沿用 API 或新增 COM)」。若沿用 API,要說明 anchor 「引數」的列也算 API。
2. 「引數」「函式名」錨點的「起始行」「所在行」判法與第一版錨點(「運算子」「方法名」)並列時,缺「識別字(simple_identifier)」節點名與「value_arguments 起始行」的對照,計劃只寫「`value_arguments` 節點起始行」,但 `LaunchedEffect(` 與 `(` 常同一行,多行引數的起始行是左括號行——可讀懂,屬低風險。
   - 修改:不必改,最多加半句「左括號所在行」。
3. 「接收者寫法」「頂層函式寫法」只在〈範圍〉2、S3 出現,〈用詞〉沒定義(`a.combine(b)` vs `combine(a, b)`)。
   - 原句:`combine`(接收者寫法)、新增頂層 `combine` 呼叫的規則
   - 修改:〈用詞〉補「接收者寫法=`a.combine(b) {…}`,頂層寫法=`combine(a, b) {…}`」。
4. 「類別 NUL」與 NUL 字元(L:426 等處註解常用「NUL」指 `\0`)同名,易混;型錄類別欄英文縮寫其餘都是論文運算子縮寫,NUL 不是。建議在〈用詞〉標明「NUL = null-safety 運算子,非論文縮寫,也不是 NUL 字元」。

## ② 壞引用

1. 〈回退〉編號:RETIRE-IF 寫「(計劃〈回退〉第 2 條)」,但〈回退〉是兩個無編號的項目,且「單列拿掉」是第 1 項、第 2 項是「整批撤掉」。
   - 原句:就把那一列從表裡拿掉(計劃〈回退〉第 2 條)
   - 依據:計劃 〈回退〉節(兩項,第一項「單列誤報或編不過多:從〈選擇點表〉拿掉那一列」)。
   - 修改:改成「(計劃〈回退〉第 1 項)」,或把〈回退〉加編號 1、2 並指向 1。
2. `lands_in` 列了 `Systems/guard-kill`,〈範圍〉沒有任何一項寫進 guard-kill(5 只提 kotlin規則包與第一版計劃)。
   - 原句:lands_in: - Systems/kotlin規則包 - Systems/guard-kill
   - 修改:拿掉 `Systems/guard-kill`,或〈範圍〉5 補「Systems/guard-kill 補一行第二批列的 `--stats` 口徑」(若真要做,見 ④-9)。
3. 其餘引用都存在:`Projects/改動選擇點都要有需求守住_計劃`、`Verification/2026-11-15_…端到端驗收`、`Systems/規格閘`、`Systems/kotlin規則包`、`Systems/guard-kill` 節點皆在;`configs/ast-grep/kotlin-choice/rules-choice/api.yml` 在;`nul.yml`、`compose.yml` 為計劃說要新建;`samples/`(choice.kt 等)在;`skills/kotlin-idioms/checks-catalog.md`〈選擇點表〉(1654 行起,31 列)、〈乾節點規則〉(1696 行起)、A-8(1709)都在。函式名 `_choice_anchor`(L:77118)、`_choice_edits`(L:77252)、`_choice_ctx_safe`(L:77142)、`_choice_excluded`(L:77199)皆在;`_KT_SIT_BUDGET`(L:40217)、`_CHOICE_PICK_BUDGET`(L:78321)皆在;`t_kotlin_rulepack_samples`(T:126882)、`t_choice_points_stable`(T:143573)皆在。

## ③ 範圍自相矛盾

1. S1 與〈實務隱患〉矛盾:一處說不設型別前提,一處又要「null 字面值不產生」。
   - 原句(實務隱患):語法樹沒有型別,這兩列不設型別前提
   - 原句(S1):`$A` 是 null 字面值的不產生 [test:t_choice_points_nul_elvis]
   - 依據:型錄型別前提只有三種合法值 `C:1394`;「運算元有 null 字面值」是檢查 `$A`、`$B` 任一個(`L:77205` `"null" in ops`),不是只看 `$A`。
   - 修改:二擇一。(a)不設前提(填「(無)」),S1 與預期值表第三列刪掉;(b)用「運算元有 null 字面值」,但要講清楚它同時擋 `x ?: null`(`$B` 是 null)與 `null ?: x`,並改 S1 為「`$A` 或 `$B` 是 null 字面值不產生」。
2. 預期值表 S1 第三列自己對不上:輸入 `x ?: null`,說明卻寫「`$A` 是 null」。`x ?: null` 的 `$A` 是 `x`、`$B` 才是 null。
   - 原句:`x ?: null` 的 `$A` 是 null | 不產生
   - 修改:改成「`null ?: x`(`$A` 是 null 字面值)」,或維持 `x ?: null` 並改說明為「`$B` 是 null」,同時處理上一條的前提欄。
3. S7「第一版各列在既有樣本上挑出的壞法應不變」與新增規則會命中舊樣本同一行(`?.`、`?:`、`.let {`)衝突:同一行新增 NUL 類節點,`_choice_pick` 用 `cats` 洗牌,類別數變了種子洗出的順序也變(`L:77378`)。第二批 `?:`、`?.`、`let` 非常普遍,舊樣本與真實碼只要有這些就會換壞法。
   - 原句:第一版各列在既有樣本上挑出的壞法 應 不變(行指紋相同、壞法相同)
   - 修改:S7 改成「既有樣本中不含第二批語法的行,挑出的壞法不變」,並在〈回退〉或〈實務隱患〉註明含第二批語法的行會換壞法,舊處置因鍵是 (檔, 行指紋) 仍有效。
4. RETIRE-IF 與〈實務隱患〉依賴「`gov --stats` 依列號分列的編不過/等價比例」,〈範圍〉與〈驗收條款〉都沒有對應工作(見 ④-9)。
   - 原句:`gov --stats` 的選擇點分列 / `--stats` 依列號累計,編不過超過一半照 RETIRE-IF 拿掉那一列
   - 修改:〈範圍〉新增一項「`--stats` 選擇點段補每列(列號)的 killed/survived/no_result/放行理由計數」並加驗收條款;或把 RETIRE-IF 改成讀現有數字(放行 shape 依 (列號, 外層宣告) 計)。
5. 〈範圍〉1 只寫「〈選擇點表〉說明段補第二批來源與不收理由」,但說明段另有兩句被第二批推翻:「錨點只用…四種」「型別前提只用…三種」(catalog 1658 行),加新錨點或新前提後這兩句會變成假的,且〈統計〉`選擇點表:31 列` 要同步(`C:631-633` stats_problems 會比對,不更新會被 check.py 擋)。
   - 修改:〈範圍〉1 補「同步改說明段的錨點/型別前提清單與〈統計〉列數」。
6. 〈不做〉「不改…乾節點…規則」vs 〈範圍〉2 新增的 compose/nul 規則若要避開 Compose 的 `Unit`/`true` 已是常數的 key(換成 Unit 是等價),須有排除機制;〈不做〉與〈範圍〉都沒處理(見 ④-7)。

## ④ 機械宣稱驗語意

下列逐句對照程式。「語意不符」=程式現況與計劃宣稱的行為不一樣;「只是不存在」=計劃宣稱要新增、現在沒有(合理,但計劃沒寫清楚)。

1. 【語意不符】`$A ?: $B` 的錨點。計劃沒指定 elvis 列的錨點;若照第一版 AOR/ROR 慣例填「運算子」,`_choice_anchor` 的運算子正規式 `_CHOICE_OP_RE` 不含 `?:`(`L:76877`),`m` 為 None 回 `(None, None)`,節點被 `_choice_file_points` 整個丟掉(`L:77455` `anchor is None` → continue),NUL 列永遠不產壞法。
   - 原句:`nul.yml`(`elvis_expression`、`?.` 的 navigation_suffix)
   - 修改:〈用詞〉或〈範圍〉1 明寫 elvis 列錨點用「運算元起始」(`L:77133` 回節點開頭,不用 op),並在〈範圍〉3 說明不改 `_CHOICE_OP_RE`。
2. 【語意不符】`$A!!` 的括號。計劃寫「整節點替換,外層是運算式時加括號」。實際 `_choice_edits` 的通用路徑是:組完文字後 `if not _choice_atomic(text) and not _choice_ctx_safe(...)` 才加括號(`L:77275`),括號加在整個替換文字,不加在 `$A` 上。elvis 優先序低於加減乘除、`as?`,所以 `$A` 常是複合運算式,例如 `a + b ?: c` 的 `$A` 是 `a + b`,替換後 `a + b!!` 的 `!!` 只套到 `b`,語意變了(不是計劃要的壞法,可能編得過但測不出該測的)。
   - 原句:`$A!!`(整節點替換,外層是運算式時加括號)
   - 修改:改成「`$A` 非原子(`_choice_atomic` 為假)時先對 `$A` 加括號再接 `!!`(`($A)!!`),外層是運算式時再整體加括號」,並加預期值表一列:`a + b ?: c` → `(a + b)!!`。這需要在 `_choice_edits` 對 `$A!!` 樣板另開分支,現有通用路徑不處理。
3. 【語意不符】「`?.`→`!!.`(只換那兩個字元)」所用錨點與替換機制。現有「方法名」錨點的 `_choice_edits` 一律走 `_choice_api_edits`(`L:77260`),替換的是方法名識別字(`op` 位移,`L:77123` `m.start(2)`),不是 `?.`;且 `_choice_also`(`L:77356`)限 `anchor == "方法名"` 才補 import。計劃把 `?.` 列的錨點與編輯種類只用一句話帶過,沒說是新錨點還是改寫既有。
   - 原句:`?.`→`!!.`(只換那兩個字元)
   - 修改:〈範圍〉3 明寫「NUL 的 `?.` 列用新錨點(例:「安全呼叫符」,位移取 navigation_suffix 開頭 2 位元組)與新編輯種類(換 `!!.`)」,不要沿用「方法名」。
4. 【語意不符】「引數清單換成 `(Unit)`」。通用路徑 `text=tpl` 後 `_choice_atomic("(Unit)")` 為假(去掉成對括號後是空字串,`L:77263` `fullmatch` 空字串失敗),前一字元是識別字不在 `_choice_ctx_safe` 的允許集(`L:77146`),結果會被包成 `((Unit))`,產出 `LaunchedEffect((Unit)) {…}`——雖然仍編得過,但不是計劃預期的 `LaunchedEffect(Unit)`;S4 預期值會不符。刪掉引數(`remember(k) {`→`remember {`)走 `tpl == "delete"`(`L:77258`)可行,但 `delete` 是現有的「(刪掉)」特殊值,語意是刪整個命中節點,成立。
   - 原句:引數清單換成 `(Unit)` 或刪掉
   - 修改:〈範圍〉3 補「引數錨點的替換不經 `_choice_ctx_safe`/加括號,直接以樣板文字覆蓋 value_arguments 範圍」。
5. 【語意不符】頂層 `combine(a, b) { x, y -> x + y }` → `zip(a, b) { x, y -> x + y }`。kotlinx.coroutines 沒有兩個 Flow 引數的頂層 `zip` 函式,`zip` 只有擴充函式 `Flow<T1>.zip(other, transform)`;頂層 `combine(a, b)` 的壞法是替換識別字會編不過,不是等價換寫。計劃在預期值表給出這個壞法,並要求補 `kotlinx.coroutines.flow.zip` import,補了也編不過(import 對得上 `zip` 擴充函式,但頂層呼叫形狀不對)。
   - 原句:`combine(a, b) { x, y -> x + y }` | `zip(a, b) { x, y -> x + y }`,補 `kotlinx.coroutines.flow.zip` import 時檔頭有逐一 import combine
   - 依據:`L:77118` 錨點只換識別字;`L:77261` `_choice_api_edits` 同樣只換識別字。
   - 修改:頂層寫法要改寫成 `a.zip(b) { x, y -> x + y }`(需要把第一個引數移到接收者,是多節點編輯,違反一對一)。建議直接把「頂層 combine」從第二批拿掉,只留接收者寫法;或承認編不過、落 no_result(但那樣是已知必壞列,違背〈實務隱患〉「近似條件判不準寧可讓它跑」的前提)。
6. 【只是不存在,但計劃寫得像現有能力】`_choice_anchor` 認新錨點「函式名」「引數」、`_choice_also` 補 `zip` import。現在 `_choice_anchor` 只認「方法名」「運算子」,其餘一律回節點開頭 `hit["s"]`(`L:77133`);`_choice_also` 限定錨點是「方法名」(`L:77358`)。計劃〈範圍〉3 提了 `_choice_anchor` 但沒提 `_choice_also`,S3 預期卻包含頂層 `combine` 補 `zip` import。
   - 原句:`_choice_anchor` 認新錨點「函式名」「引數」
   - 修改:〈範圍〉3 補「`_choice_also` 放寬到錨點「函式名」」(若保留頂層 combine,見上一條)。
7. 【語意不符】「等價存活」與型別前提:`LaunchedEffect(Unit) {…}`、`LaunchedEffect(true)` 這類 key 本來就是常數,換成 `(Unit)` 是等價壞法。計劃的〈實務隱患〉列了 `$A!!` 的等價,沒列這兩列;現有型別前提白名單(`C:1394`)沒有能表達「key 已是 Unit」的值,計劃也沒新增。
   - 修改:〈範圍〉補新型別前提「引數已是 Unit」,或把它列進 RETIRE-IF 前的〈實務隱患〉並說明靠放行(等價)。
8. 【語意不符】S6 綁的測試。
   - 原句:當新樣本檔跑過 check.py,每條第二批規則 應 命中該命中的、不命中不該命中的 [test:t_kotlin_rulepack_samples]
   - 依據:`T:126882` `t_kotlin_rulepack_samples` 測的是 kotlin-android 規則包自己的壞例/好例樣本與 `files:` 區塊判讀,不碰 `configs/ast-grep/kotlin-choice/samples/`;選擇點樣本的 HIT/MISS 核對在 `t_choice_table_missing`(`T:143731`,內含 `kp.choice_sample_problems`,`T:143773`)。
   - 修改:S6 改綁 `t_choice_table_missing` 或新測試(例 `t_choice_samples_batch2`),不要綁 `t_kotlin_rulepack_samples`。
9. 【語意不符】S7 綁的 `t_choice_points_stable`(`T:143573`)測的是種子穩定與型別前提換類別(合成命中,不讀 `samples/` 或真型錄),不比較「加入第二批列前後」。要驗 S7 需新斷言。
   - 修改:S7 補一個新測試或在 `t_choice_points_stable` 加「換成含第二批列的型錄後,只含第一版語法的行挑法不變」的斷言,並照 ③-3 縮窄 S7。
10. 【語意不符】RETIRE-IF / 〈實務隱患〉說「`--stats` 依列號累計」。現行 `gov --stats` 選擇點段(`L:17896-17975`)不依列號累計 no_result 或放行比例:放行只按 (列號, 外層宣告) 數形狀 ≥3 才列(`L:17963`),no_result 按原因冒號前文字計(`L:17938`),被回報存活只按 (檔, 行指紋) 計。沒有「每列被回報的存活裡判等價超過八成」或「每列編不過超過一半」的現成數字。
    - 原句:上線兩個月後讀 `gov --stats` 的選擇點分列:第二批任一列被回報的存活裡判「等價或不是需求」超過八成
    - 修改:同 ③-4:要嘛〈範圍〉新增 `--stats` 依列號分列的工作與驗收條款,要嘛 RETIRE-IF 改成現有數字(放行 shape、no_result 原因)讀。
11. 【語意不符】「類別白名單加 NUL」放在〈範圍〉3(lumos 讀表與產壞法)。類別與錨點白名單只在 `check.py`:`CHOICE_CATEGORIES`、`CHOICE_ANCHORS`(`C:1392-1393`、`_choice_row` `C:1428-1437`),lumos 沒有第二份白名單,它透過 `_choice_tables`(`L:76891`)呼叫 `mod.choice_tables`,且 `tables["categories"]` 直接來自 check.py(`C:1493`)。lumos 只在 `_choice_anchor`(`L:77118`)/ `_choice_edits`(`L:77252`)硬寫錨點與編輯種類。
    - 原句:類別白名單加 NUL / `check.py` 與 lumos 讀表時認得它
    - 修改:把「類別、錨點白名單加 NUL/函式名/引數」移到〈範圍〉4(check.py);〈範圍〉3 只留 `_choice_anchor`、`_choice_edits`、`_choice_also` 的程式改動。S5 的「check.py 與 lumos 讀表都擋」其實是同一處(lumos 轉述 check.py 的問題),預期值表 S5 第一列說明可改成「lumos 讀表經 check.py 擋」。另提醒:CHOICE_CATEGORIES 順序即洗牌基準(`C:1392` 註解),NUL 應附在尾端以免動到第一版順序。
12. 【驗過沒問題,不必改】
    - 「沒有可守測試時只提醒不擋」是第一版現行行為:第一版〈範圍〉4 判定段「碰到了但沒有可守的測試 → 不擋,印『這次的選擇點沒有測試守,只能人驗』」,驗收條款 S17 `t_spec_gate_push_choice_no_plan`;注意 `choice-kill` 指令本身是 rc 2(「計劃沒有可守的測試條款」),只有推送前那一道是只提醒。計劃〈實務隱患〉寫的是推送前那一道,正確。
    - `_KT_SIT_BUDGET`、`_CHOICE_PICK_BUDGET` 都存在,語意與計劃所述一致(掃描時限 30 秒、挑壞法 15 秒)。
    - 「沿用 API 列補 import 做法」:`_choice_also`(`L:77352`)確實是「檔頭逐一 import 原寫法才補兄弟寫法」,只對錨點「方法名」有效(見 ④-6)。
    - `_choice_excluded` 前提:只認「運算元有 null 字面值」「運算元是字串」兩種(`L:77199-77208`),計劃沒新增前提,與「不設型別前提」一致(但與 S1 矛盾,見 ③-1)。
    - `.let`→`.also`:經現有「方法名」錨點與 `_choice_api_edits` 可行(換 navigation_suffix 內的識別字,`?.let` 也算,`L:77123` 正規式 `(\?\.|\.)\s*name`)。
    - `?.` 連鎖「一行一個壞法、其餘 `?.` 不動」:`_choice_pick` 每行只取一個節點(`L:77378-77396`),成立。
    - 型錄接 C-32:現有最大列號 C-31,銜接正確。

## 統計

- ① 未定義的詞:4 條
- ② 壞引用:2 條(第 3 點是驗過沒問題的備查)
- ③ 範圍自相矛盾:6 條
- ④ 機械宣稱驗語意:11 條命中(語意不符 10 條:1、2、3、4、5、7、8、9、10、11;只是不存在 1 條:6),第 12 點為驗過沒問題的備查
