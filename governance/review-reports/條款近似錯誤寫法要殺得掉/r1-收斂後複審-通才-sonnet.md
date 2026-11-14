severity: major

## t1 「同一列觸發字互換」不是兄弟寫法,舊否決 d1 的不衝突論證站不住
severity: major
blocking: 是。照字面實作,多數型錄列產生不出能編譯的壞法,〈舊否決比對〉也不成立。

- 位置:〈舊否決比對〉第一條、〈用詞〉兄弟寫法宣告。
- 問題:spec 說型錄那一列是「兩個寫法行為不同、選哪個看需求」的宣告,所以等價問題已判過。
  - 型錄的「觸發字」欄是檢索關鍵字清單,不是可互換的選項集。
  - D-4 的觸發字含 `debounce`、`viewModelScope.launch`,它們跟 `flatMapConcat` 不是互為替代。
  - D-40 的觸發字有 `startActivity、NavHost、NavDisplay`,D-44 有 `Database、Migration、AutoMigration`,互換後只會編不過。
  - D-4 內真正能編譯又改變行為的,大概只有 `flatMapLatest`、`flatMapConcat`、`flatMapMerge` 這幾個。
  - `mapLatest→flatMapLatest` 一個回值、一個回 Flow,編不過。
- 型錄裡真正講「選另一個」的是「例外」欄的正則和「不適用時」欄,不是觸發字欄。
- 後果:形狀檢查(列號加兩個識別字都在觸發字欄)放行大量編不過的配對。要等到跑 clause-kill(約 10 秒到數分鐘)才變成弱證據、rc 2、不記帳。作者只剩免宣告一條路。
- 佐證:`skills/kotlin-idioms/checks-catalog.md:743`(D-4 觸發字欄、例外欄分開寫)。
- 引句:「等價問題在型錄寫列時已經判過;零依賴照守」

## t2 壞法打在哪一行完全由作者的 `--line` 決定,跟條款、跟實作的因果都沒綁
severity: major
blocking: 是。「作者不能挑容易殺的壞法」只有「恰好一行」那條護欄,而它在常見的 Kotlin 檔案裡幾乎不會生效(見 t3)。

- 位置:〈用詞〉壞法、有效紀錄、〈天花板〉4。
- 問題:
  - 工具只要求 `--file` 不是測試檔、該行含原寫法整字。
  - 它不驗這一行是這條條款的實作。
  - 它不驗這一行在這次推送範圍內有被改到。
  - 它不驗綁的測試會走到這一行。
- 推送前只驗 `old` 在推送版本該檔恰好出現一次、`test_name` 還綁著。
- 例子:條款 S2 說「只顯示最新一次查詢」,實作的 `flatMapLatest` 在 `SearchViewModel.kt`。作者把 `--file` 指到同專案另一支也有 `flatMapLatest`、而且綁的測試能殺掉它的檔。
  - 結果:killed 入帳,條款 S2 的真實實作行從頭到尾沒被壞法碰過。
  - 推送前也看不出,因為檢查項目全部對得上。
- `cmd_guard_kill` 只檢查 `old` 在檔內命中恰好一次、不看語意。
  - 佐證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27940`(`cnt != 1` 判 drifted)。
- 建議:要求 `--line` 落在本次推送範圍的 diff hunk 裡,或落在條款綁的測試檔所 import 的實作類別;至少把 `file` 與 `line` 偏離條款 lands_in 的情況列為需核可。
- 引句:「零行或多行 → rc 2,多行時可給 `--line <行號>` 指定(該行要含原寫法)」

## t3 「恰好一行」在有逐一 import 的 Kotlin 檔幾乎必然不成立,default 路徑形同虛設
severity: minor
blocking: 否。會 rc 2 擋下,不會做錯,只是流程設計與 t2 疊加。

- 位置:〈用詞〉壞法。
- 問題:
  - `\b<原寫法>\b` 會命中 `import kotlinx.coroutines.flow.flatMapLatest` 那行,也會命中註解和 KDoc。
  - 只要檔案用逐一 import(spec 自己也承認有這種情況),使用行加 import 行就是兩行,每次都得手給 `--line`。
  - `--line` 變成常態,而不是例外,t2 的唯一護欄就失效。
  - S6 預期表只測「兩行含 flatMapLatest」,沒有測 import 行。
- 另一個盲點:如果作者 `--line` 指到 import 那行,換成 `flatMapConcat` 之後使用行找不到符號,會編不過。這靠 `_kill_attribute` 的歸因判成弱證據,取決於 Gradle 輸出剛好不含測試名,spec 沒有明文要求這一點。
  - 佐證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27736`。
- 建議:排除 import 行和註解行,並補一列 S6 預期表。
- 引句:「找出含原寫法整字(`\b<原寫法>\b`)的行;恰好一行時那一行就是 `old`」

## t4 「適用」以專案有沒有 Kotlin 平台判,不是以條款綁的測試屬哪個平台判
severity: major
blocking: 是。這會讓免宣告在混合專案被迫變多,RETIRE-IF ③ 在上線第一天就失真。

- 位置:〈用詞〉適用的計劃、S10。
- 問題:
  - 只要 `.lumos/config.json` 有任何 kotlin-junit 平台,專案內所有風險高、進行中的計劃,每一條綁測試的條款都要宣告。
  - 其中綁 pytest、shell、iOS 測試的條款,型錄沒有對應列,只能走 `[near:無 …]` 加人核可。
  - 後果一:免宣告占比被非 Kotlin 條款灌水,RETIRE-IF ③「超過一半」會自動觸發,但原因不是「型錄覆蓋不夠」。
  - 後果二:人核可變成固定儀式,等於橡皮圖章。
- 建議:適用性要看條款所綁測試的平台是否為 kotlin-junit。
- 引句:「而且專案有 Kotlin 平台(`.lumos/config.json` 有 profile 是 kotlin-junit 的平台)」

## t5 RETIRE-IF 三個數有兩個照這份設計量不到
severity: major
blocking: 是。RETIRE-IF 寫了但算不出來,等於沒有撤除條件。

- 位置:頭部 RETIRE-IF、〈範圍〉4、S11。
  - ①「第一次跑就殺掉的比例」:`--stats` 印的殺掉率是帳上 killed 筆數對 killed 加 survived 筆數(S11 預期表為 3/4),包含重跑。
    - 作者 survived 後補強測試、再跑 killed,分子分母各加一,結果是第二次跑才殺掉的也算進去。
    - 這個數會偏低,不會偏高,所以「超過九成五」幾乎量不出訊號。
    - 沒有按 (條款, 第幾個) 取第一筆的統計口徑。
  - ②「被擋的次數裡超過一半是工具誤判」:
    - 〈範圍〉4 沒有新增「推送前因缺紀錄被擋」的帳事件,只登記了 `clause-kill`。
    - 「誤判」也沒有定義與記錄欄位。
    - 既有的 `code-loop` `blocked` 事件有先例,這份沒有仿。
  - ③「`[near:無]` 占比」:
    - 分母是「要宣告的條款總數」,帳上只有 waive 事件。
    - S11 預期表印的是「免宣告 1」計數,不是占比,跟〈範圍〉4 的「免宣告占比」自相矛盾。
- 佐證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:20643`(`LOOP_NOT_CLOSE_EVENTS` 含 `("code-loop","blocked")`,有擋人落帳的先例)。
- 引句:「印殺掉率、免宣告占比與存活後改寫次數」

## t6 「存活後改寫」的比對鍵讓改條款編號或拆條款就繞過
severity: minor
blocking: 否。需要刻意多步,但改編號只需一步,而且正好落在 spec 本席要防的「照常操作」範圍。

- 位置:〈用詞〉存活後改寫、S9。
- 問題:觸發條件是同一條款同一標記原文消失。作者在 survived 後,把條款 `S2` 改成 `S2b` 或另開條款搬走綁定,帳上舊 S2 的 survived 紀錄就沒有「現在那一行」可比。
  - spec 沒說條款整行消失算不算改寫。
  - 新條款用新宣告重跑(不同兄弟寫法或不同壞法)即可,不需要 ack-survived。
- 建議:以 (計劃, 測試名) 為鍵,或條款整行消失也要求 ack。
- 引句:「帳上有某條款某個兄弟寫法判 `survived`,而現在那一行已經沒有同一個標記原文(改寫、刪掉、改成免宣告)」

## t7 紀錄只綁測試名,不綁測試本體,「先殺掉再改弱」整條路通
severity: minor
blocking: 否。〈天花板〉2 已明說接受,但補法很便宜(紀錄多記測試檔的 blob sha,推送時比對)。

- 位置:〈天花板〉2、〈實務隱患〉換綁較弱測試。
- 問題:這份設計要解的就是「測試弱」。killed 入帳之後把測試改回只送一次值,帳依然有效。
- 建議:有效紀錄多存測試檔 blob sha;改了就要重跑,不必重跑 Gradle 的判斷,只需換 sha。
- 引句:「測試本體被改弱、周邊程式改了都不會讓紀錄失效」

## t8 免宣告沒有跟型錄「主」正則交叉驗證,作者可以對有對應列的條款敷衍寫 `[near:無 …]`
severity: minor
blocking: 否。單人單機的威脅模型下,人核可是最後一道,這裡只是缺一道便宜的機械提示。

- 位置:〈用詞〉免宣告、〈不做〉。
- 問題:免宣告只要求理由 ≥10 實字加人核可。工具知道 `--file` 與型錄各列的「主」正則,卻不檢查「這條條款綁的實作檔其實命中了某列主正則」。
  - 例子:實作行是 `query.debounce(300).flatMapLatest { … }`,條款卻寫 `[near:無 這條是輸出格式沒有型錄寫法可換]`。
  - 規格閘與推送閘都不會提醒;人核可時沒有任何機械訊息可看。
- 建議:免宣告核可時,在被改的實作檔命中型錄「主」正則,就在 `--waive` 的提示裡列出命中的列號。
- 引句:「型錄沒有的錯誤走免宣告、要人核可;REVISIT 看數字再決定」

## t9 本設計宣稱要解的情境只有手動驗證,自動測試全用假平台
severity: minor
blocking: 否。

- 位置:S12、預期值表 S12。
- 問題:S4、S5 用假平台驗流程。「對真實 Kotlin、真 Gradle,只送一次值的測試會 survived」只有 S12 這一條,而且是 `[manual:]`。
  - 它被標成手動,所以自己也不受 S1 宣告要求約束。
  - 〈依據來源〉那筆人裁實測只證明了零件(`recipes_override`)在真專案能跑,沒有證明壞法產生那一層。
- 引句:「clause-kill 應 回 1 判 survived(抓得到面試題的弱測試)」

## 固定席節點與合約的逐條判定

- `Systems/guard-kill` 的 ★INVARIANT★ rc 優先序:不影響。
  - clause-kill 只讀 `result_out` 的列,不改 `cmd_guard_kill` 的回傳碼判定。
  - `source` 是選用參數,不傳維持原行為。
- `Systems/guard-kill` 的 ★INVARIANT★ `--json` 純度:不影響。
  - clause-kill 呼叫 `cmd_guard_kill` 走非 json 路徑,不碰 `as_json` 分支。
  - 這個合約只管 json 模式成功跑完時的 stdout。
- `Systems/規格閘`:無合約被破壞。但〈範圍〉3 把新一道塞進 `_spec_gate_push_check` 同一圈,要確認預期值表那道的 `ctx` 讀帳不受 `clause-kill` 閘名影響。

## 實務隱患鏡頭

- 資安與命令注入:
  - `--file`、`--line`、`--import`、`--consent` 都是作者輸入。
  - spec 有路徑限制和 `old`/`new` 500 字上限,但沒寫 `--import` 的格式驗證(例如換行或多行字串);`--import` 會被寫進原始檔,應限單行且符合 `import <pkg>.<Name>`。
  - `--file` 的符號連結與 `..` 路徑,spec 說同人裁的 `kfile` 換算,沿用即可。
- 效能:每個宣告一次完整 Gradle,十幾分鐘。條款多的計劃,「不批次」加推送前才補會集中在推送前。spec 只建議放背景。建議在規格閘階段就印預估工時。
- 併發:spec 已排除,單人單機。
- 舊帳相容:`source` 非空就跳過的改法,會讓日後任何寫了 `source` 的新事件都被讀者略過;這是預期行為,但要確保沒有現存事件剛好有非空 `source` 卻應該被讀。
- 其他類(外部呼叫、個資、權限):無。這個功能只讀寫本機治理帳與隔離工作樹。

## 已讀無 finding 的節

〈白話〉〈依據來源〉〈回退〉:已讀,無 finding。〈範圍〉的 S 編號與預期值表、〈天花板〉的互相參照都對得上。

最嚴重:major;blocking 共 4 條
