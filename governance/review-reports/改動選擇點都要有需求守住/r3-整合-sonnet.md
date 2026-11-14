severity: major

## i1 S4「複合節點全乾才乾」用 ast-grep 扁平命中做不出來,又跟旗標列的寫法衝突
severity: major
blocking: 是——S4 後半句與預期值表照字面實作,在 ast-grep 規則加「落在乾範圍內就扣掉」的機制下做不出來,實作者只能自己發明遞迴。

- 〈乾節點規則〉說「複合節點照公式 1:只有所有子節點都乾才整個乾」。
- 〈用詞〉語法樹掃描只拿命中節點的起訖行列、原文、後設變數,〈選擇點〉只做「落在乾節點範圍內就扣掉」。
- ast-grep 規則是逐節點、不遞迴的,沒有任何一個欄位能表達「所有子節點都乾」。子節點清單也沒有交給 lumos。
- 旗標列寫「含 `BuildConfig.DEBUG` 的條件節點」。若乾範圍取整個條件節點,`if (BuildConfig.DEBUG && x > 1)` 裡的 `x > 1` 落在範圍內被扣掉,違反 S4 預期值表「`x > 1` 照常可挑」。
- 若乾範圍只取 `BuildConfig.DEBUG` 本身,預期值表過得了,但「複合節點全乾才乾」永遠不成立。
- 具體例:`if (a.size > 0 && b.size > 0)`。依論文公式 1 兩個子節點都乾(A.1.20),整個 `&&` 應乾。扁平範圍法會照樣對 `&&` 產生 LCR 壞法。
- 要修的是二選一:拿掉「複合節點」那句、改成「乾範圍就是規則命中節點整個」;或另外規定 lumos 怎麼拿到子節點樹(例如 `--debug-query` 輸出)。

引句:「複合節點照公式 1:只有所有子節點都乾才整個乾」
引句:「旗標(含 `BuildConfig.DEBUG` 的條件節點;A.1.13、A.1.16)」

## i2 r2 的 H2 沒折乾淨:〈一行一個壞法〉仍要求候選「恰好一次」,跟「不唯一標不唯一」矛盾
severity: major
blocking: 是——照〈一行一個壞法〉字面,重複行得到「沒有壞法」(靜默免擋);照〈壞法身分〉與 S3,重複行得到「標不唯一、可判」。兩者不能同時成立。

- 〈一行一個壞法〉要候選套上後 old 在檔裡恰好一次,並說「一個類別都產不出就這一行沒有壞法」。
- 〈壞法身分〉另說整支檔不唯一時往外帶上下各 2 行,仍不唯一才標「不唯一」。
- 例:同檔有兩行完全相同、前後各 2 行也相同的 `if (x > limit) return`。
  - 依〈一行一個壞法〉:每個候選都不唯一 → 這行沒有壞法,推送閘不要求,洞很安靜。
  - 依〈壞法身分〉與 S3 預期值表:這行標「不唯一」,可判、不跑。
- r2 的 i8 就是這條矛盾,收貨紀錄寫「唯一性只在身分段定義」,但〈一行一個壞法〉那句沒刪。
- 修法是從〈一行一個壞法〉拿掉「恰好一次」,只留型別前提。

引句:一個類別都產不出就這一行沒有壞法
引句:應 往外帶行求唯一,仍不唯一標不唯一

## i3 有效處置以 (file, line_sha) 為鍵,同檔內文字相同、上下文不同的兩行共用一筆處置
severity: major
blocking: 是——第二個重複行不會被 choice-kill 跑,也不會被推送閘要求,選擇點沒有需求守住卻放行,違反本計劃的合約。

- 〈有效處置〉鍵是 (`file`, `line_sha`),`line_sha` 只是行內容的 sha256,不含行號或上下文。
- S3 只處理「前後各兩行也相同」。這種上下文不同、本行相同的重複行,各自有唯一的 `old`(帶上下文),身分不同,但處置鍵相同。
- 例:同一支 ViewModel 的兩處 `if (state.isLoading) return`,上下文不同。第一處 killed 後,choice-kill「對還沒有有效處置的行」跳過第二處。第二處的壞法沒被跑,推送閘也看到「已 killed」放行。
- 反方向也成立。第二處若 survived,帳上同鍵「最新一筆」變 survived,第一處看起來又要處置,兩處互相覆蓋。
- Kotlin 裡 `return`/空判斷這類重複行很常見。
- 修法是處置鍵加上 `new_sha` 與外帶上下文的雜湊(身分裡的 old 範圍),或把鍵改成壞法身分而非行內容。

引句:帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed`
引句:對還沒有有效處置的行,依〈用詞〉殺掉判定批次跑

## i4 S6 與 S21 在同一個輸入上互斥:沒有 ast-grep 的機器,舊計劃的 Kotlin 推送照擋
severity: major
blocking: 是——S6 和 S21 的預期值表在同一個輸入上給相反結果,測試必有一條錯。

- 輸入:消費專案、碰到的計劃日期早於 `_CHOICE_SINCE`(或專案沒有 kotlin-junit 平台),改了 `Vm.kt`,機器沒有 ast-grep。
- S21 說不要求。S6 與〈算不出來〉說「ast-grep 不在而範圍有 `.kt` 正式碼改動 → 擋」。
- 〈條件〉把「至少一行有壞法」放在生效日與平台之前,但「有壞法」要靠 ast-grep 才知道,所以沒 ast-grep 時只能保守擋。
- 平台是否為 kotlin-junit、生效日、碰到的計劃,都不需要 ast-grep 就能算(用 `_drift_tree_env` 的記憶體圖譜)。
- 要明寫順序:先判平台、生效日,再查 ast-grep。

引句:推送前那一道遇到 .kt 正式碼改動 應 擋下並印安裝指令
引句:當計劃日期早於生效日、專案沒有 kotlin-junit 平台、或改到的行沒有壞法,推送前那一道 應 不要求

## i5 推送範圍的「主線分岔點」只指到 `_push_mainlines`,沒指單一來源 `_push_range_start`;「被推的 ref 是主線」的判法也沒指定
severity: major
blocking: 是——多主線(git-flow 的 develop 加 main、fork 加正本)時,字面實作會重現 `_push_range_start` 註解寫明已打穿的老問題。

- `_push_range_start`(`scripts/lumos:69101`)的註解寫「起點只在這裡算一處」。
- 它對多主線用 `merge-base --all` 再 `_push_pick_base` 選,r3 已證明固定取第一個候選會錯。
- 本 spec 只寫「用主線與 B 的分岔點..B」。對 `_push_mainlines` 回傳的多個候選,取誰的分岔點沒說。
- 結果:取到過期 main 的分岔點,範圍多算整段 develop,滿滿的「缺紀錄」誤擋。
- 「被推的 ref 本身是主線」目前有三種既有判法:
  - `_push_mainlines` 的跳過規則。
  - `_pitfalls_pushed_mainline`,走 `_note_reread_mainline_names`,永遠含 main/master。
  - `_push_range_start` 的「頂端已在主線」。
- 它們對 fork 或名字不是 main 的主線,答案不同。
- 要明寫:用 `_push_range_start`(`old` 帶全零)取起點,並說明「是主線」就等於它回 None 或候選全被跳過。

引句:否則用主線與 B 的分岔點..B;算不出 → 用推送範圍本身
引句:主線照 `_push_mainlines`(跳過被推的那條)

file: `scripts/lumos:69101`
file: `scripts/lumos:65605`

## i6 ast-grep 呼叫只寫「參數清單、不開 shell」,沒承接 `_lint_wt_allow` 的其餘安全做法,也沒定義掃描失敗的出口
severity: minor
blocking: 否——核心(不開 shell)已寫,缺的是可補的細節,但失敗出口不補會讓實作者自選擋或放。

查證 `scripts/lumos:41561` 的 `_lint_wt_allow` 做法,本 spec 沒提:
- 設定檔路徑限定在工具鏈 `configs/ast-grep/` 底下:realpath 加 commonpath 檢查、不准讓 ast-grep 往上找專案設定。
- 禁 `-U`、`--update-all`、`-i`、`--custom-languages`。
- 行程群組登記加 SIGTERM 處理器,收掉孤兒行程與快照目錄(`_lint_wt_begin`、`_lint_wt_reap`)。
- 暫存檔命名:repo 路徑來自被審分支,可能以 `-` 開頭或含 `..`,spec 只寫「交 ast-grep 的是暫存檔,掃完刪」。

掃描失敗時沒有出口:
- 失敗包括 ast-grep rc 非 0、`--json=stream` 輸出剖不了、檔裡有 ERROR 節點(fwcd 文法不認的新語法,部分樹照樣命中規則)。
- 〈算不出來〉只涵蓋整體逾時、讀不到檔、單檔超過讀檔上限。
- 要補:rc 非 0 與輸出壞掉歸 unverified;命中在 ERROR 節點子樹內的節點不產生壞法。

引句:lumos 以參數清單(不開 shell)執行 `ast-grep scan --config <那份設定> --json=stream <檔>`

file: `scripts/lumos:41561`

## i7 `--point` 的冪等鍵要讀自己的事件,但 `_spec_gate_ruled_events` 被規定濾掉 point 事件
severity: minor
blocking: 否——spec 已寫「條款文字與測試相同時改成對這個壞法跑殺傷力」,繞開了主要路徑;缺的是重跑冪等那條的讀法。

- 現有 `_situation_rule_already`(`scripts/lumos:75714`)的 `ruled()` 就是 `_spec_gate_ruled_events`。
- spec 規定它不拿 point 事件免預期值表列。若實作成直接濾掉 point 事件,`--point` 路徑就讀不到自己的事件。
- 重跑同一個 `--point`(上次寫了計劃、帳沒記到)時,會落到「帳沒有對得上、先刪條款」那句拒絕,不是冪等。
- 若不濾、只在 seg/row 比對:point 事件沒有 seg/row,`e.get("seg") == seg` 在兩邊都是 None 時對任何 point 事件都成立,第二個不同的 `--point` 會被當成「已完成,什麼都不用做」,不跑殺傷力,違反 S14 預期值表第二列。
- 要明寫:point 路徑用壞法身分(`file`、`line_sha`、`new_sha`)比事件,並給它自己的讀帳函式。
- 對照:`_gov_situation_spec_counts` 只數 `origin` human/ai,point 事件不算的寫法容易做,沒問題。

引句:`_spec_gate_ruled_events` 不拿它免預期值表列

file: `scripts/lumos:75714`
file: `scripts/lumos:14556`

## i8 中斷語意與現有 `_situation_rule_signals` 不符,`on_row` 的列也沒說是蓋章前還是蓋章後
severity: minor
blocking: 否——S12 的預期結果(記已完成判定的壞法、interrupted、rc 2)做得到,只是描述的過程不真實。

- `_situation_rule_signals`(`scripts/lumos:76015`)第一個訊號直接 `raise KeyboardInterrupt`,收掉測試程序群組與工作樹,不是「讓正在跑的那條配方收尾」。
- 進行中那一條的結果必丟,實作者以為能留。
- `cmd_guard_kill` 的 `weak`、`recipe_id`、`_weak_why` 是整圈跑完之後才蓋章(`scripts/lumos:28100` 附近)。
- 判定要「強 killed 且非弱證據」,`on_row` 若在配方剛跑完就交列,沒有 `weak` 欄,判定做不了。
- 要寫明:`on_row` 的列必須帶蓋章後欄位,蓋章邏輯提前到每條配方結束時。

引句:第一個訊號:讓正在跑的那條配方收尾

file: `scripts/lumos:76015`
file: `scripts/lumos:27902`

## i9 choice-judge 的類比有誤,可判的狀態沒列「沒跑」,AI 判的處置也沒走待確認的先例
severity: minor
blocking: 否——只影響指令形狀與可用性,推送閘讀 `judged` 的語意不變。

- spec 說「同 guard 的 kill-add 那種只寫帳的指令形狀」。
- 查證:`cmd_guard_kill_add`(`scripts/lumos:27215`)是把配方寫進筆記開頭欄位,不是寫帳。比較貼的先例是 `lint-waive` 或 `signoff`。
- 「那一行是存活、no_result 或不唯一都能判」沒列「沒跑」(帳上無紀錄)。
  - 先判再跑,還是必須先跑,沒說。
  - 若必須先跑,「缺紀錄」的行就沒有只靠判定的出口。
- `origin: ai` 的 `judged` 直接算有效處置。既有先例(`_lint_waiver_ai_unacked`、`lint-waive --ack`)是 AI 放行要人事後確認。
- 這屬已接受的威脅模型(AI 偽造 consent 不防),只提醒不要求。

引句:獨立子指令,同 guard 的 kill-add 那種

file: `scripts/lumos:27215`

## i10 對照論文:自稱「只對有覆蓋的行」但沒做,以及未列入「跟論文不同」的收窄
severity: minor
blocking: 否——都是設計取捨,規格內自洽,但差異清單不全、論文對應節有一處對錯。

- PRIOR-ART 說主依據是論文的「只對改動且有覆蓋的行產生變異」(2.2),差異①只列「覆蓋率挑最小測試集」。論文 2.2 明講變異只對「affected 且 covered」的行產生,A.1.7 還用覆蓋率排除沒被覆蓋的分支。
- 本設計對所有改到的行產生壞法。沒被守的測試跑到的行必然 survived,這點只在天花板 3 提到,差異清單沒寫。
- 論文表 1 的 ROR 一律含 `true`、`false`。spec 限定布林情境才給(S2 預期值表第 5 列 `val ok = a > b`)。comparison_expression 型別必為 Boolean,這個前提沒有編譯理由,屬於未列的差異。
- 論文 SBR 對任何陳述;spec 限 `call_expression` 陳述,指派、`+=`、`return` 前的運算永遠不被刪。未列為差異。
- 論文 A.1.23:`===` 只換 `!==`。Kotlin 文法 `equality_expression` 含 `!=`、`!==`、`==`、`===` 四個運算子,spec 只寫了 `==` 與 `!=`,`===` 與 `!==` 的處理沒定義。
- 論文對應節:旗標列的 `BuildConfig.DEBUG` 對到 A.1.13(命令列旗標 DEFINE_*)與 A.1.16(類別欄位常數開關)。比較貼的是 A.1.5(除錯與追蹤程式碼,release 建置會排除)。

引句:只對改動且有覆蓋的行產生變異

## i11 帳量:`run` 事件帶物件欄位,`_gate_event_fit` 縮不了;S20 只量 choice-kill 那筆
severity: minor
blocking: 否——4096 是政策值,超過照寫;只是帳長得快。

- `run` 那筆放「守的測試對各自所在檔物件編號的對照」,是物件(dict)。
- `_gate_event_fit_drop`(`scripts/lumos:1908`)只對清單 `rows[:]` 切片,物件欄位不能縮。
- 守的測試是碰到的計劃的聯集,不只 30 支。每支約 80 位元組,100 支就是約 8KB。
- S20 只量一筆 `choice-kill` 事件。
- 推送閘只掛在 pre-push 掛鉤,CI 沒接。`--no-verify` 與 CI 都繞得過去。Room 守衛的先例會寫「CI 不接,回頭條件在 …」,本 spec 的天花板沒寫這一條。

引句:`run` 那筆放守的測試對照(一次呼叫一筆)

file: `scripts/lumos:1908`

## i12 讀 B 版檔的範圍沒限定「有增行的檔」;新一圈接進 `bad` 的位置也沒定
severity: minor
blocking: 否——前者有簡單的讀法限定,後者影響的是輸出文案順序。

- `_kt_sit_read_many`(`scripts/lumos:40114`)遇到 B 版沒有的檔直接 raise `_KtSitUnverifiable`。
- 範圍有任何一支被刪的 `.kt`,若實作者把「改到的檔」當成 `git diff --name-only` 全部,整圈就掉成 unverified 放行,等於刪一支檔就能繞過這道閘。
- 要寫明只讀有增行的檔(情境題做法是 `_kt_sit_hunks` 篩出的 `rel`)。回報上限的「檔數(所有種類)」是否含刪除檔也一併定。
- 新一圈的擋下原因要在「印 light 分級」那段(`scripts/lumos:17440` 附近的 `if not bad and oks`)之前併進 `bad`。放在之後的話,掛鉤 grep 到 `改動風險分級:light` 會誤降測試範圍,同一輸出又顯示被擋。

引句:改到的檔用 `_kt_sit_read_many` 讀 B 版

file: `scripts/lumos:40114`
file: `scripts/lumos:17387`

## 第二輪折入驗收(只讀 r2-intake.md,重點是接線)
- 到位:
  - 掛鉤探 dest 字樣:`scripts/hooks/pre-push:504` 有 `dest="pf_pushed_ref"` 先例,spec 寫法一致,S18 有測舊 lumos。
  - `_drift_tree_env` 建 B 版圖譜交 `_spec_gate_push_candidates`:`_kt_sit_spec_names_calc`(`scripts/lumos:74823`)已是同一套。記憶體圖譜的家對照表有專屬分支(`_impact_home_map` 認 `env._texts`),查證可行。
  - 算不出來放行加 unverified、帳不在才擋:與 `規格閘` 的 PITFALL「審查帳讀不到就擋」一致。
  - `_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS` 的登記方式對得上現有守衛。
  - 九本帳逐欄掃過,`reason`、`row`(str 或 None,「C-n」是字串)等新欄位與現有型別不衝突。
  - 新 gate `choice-kill` 不在 `_GOV_LOCAL_PAIRS`,會進版控帳,正是 spec 要的。
- 沒到位:i2(H2 唯一性)、i5(`_push_mainlines` 兩端一致只做了一半,沒用單一來源 `_push_range_start`)。
- ast-grep 節點名對 `grammar.js` 逐一查過:`comparison_expression`、`equality_expression`、`conjunction_expression`、`disjunction_expression`、`additive_expression`、`multiplicative_expression`、`prefix_expression`、`call_expression`、`navigation_expression`、`statements`、`lambda_literal`、`value_arguments`、`function_body`、`call_suffix`、`string_literal` 都存在。
- 注意兩處:
  - `if_expression` 才有 `condition` 欄位;`while_statement` 與 `do_while_statement` 沒有欄位名,要用 `kind`+位置寫。
  - 無大括號本體是 `control_structure_body` 直接帶 `_statement`、不經 `statements`,所以「statements 的直接子節點」本身就排除了它,spec 明列的那條是多餘但無害。
- 論文對照其餘都對:表 1 候選、Listing 2(類別洗牌、第一個產得出的就停)、2.3 的「檔數 × 7」且從存活中隨機挑、3.1 公式 1 的語意、A.1.12、A.1.23、A.1.20 的說法。

## 固定席節點判定
- `Systems/guard-kill`:
  - INVARIANT 1(rc 優先序 survived→1、drifted/abort/error→2、弱證據不放行):不影響。
    - 新增的 `source`、`stop_group_on_kill`、`on_row` 都不傳時走原路徑。
    - 被略過的配方若記成新 verdict 字串(例如「略過」),在 `cmd_guard_kill` 尾端的 `verdicts` 判斷裡不會進 `survived`/`drifted`/`abort`/`error`,rc 不變。
    - choice-kill 自己的 rc「取最大」(2 壓過 1)和 guard kill 的 survived 優先相反,但那是另一個指令的 rc,不碰 INVARIANT。
  - INVARIANT 2(`--json` 成功跑完 stdout 恰一行 JSON):不影響。
    - choice-kill 不走 `--json`。
    - 「強制結束印工作樹路徑」要寫 stderr,別混進 stdout。
- `Systems/規格閘`:
  - 不破壞。新一圈沿用「算不出來放行、帳讀不到擋」。
  - 預期值表那圈照舊讀工作目錄。
  - 唯一接線風險是 i12 的 `bad` 併入位置,會影響輸出順序,不改判定。
- `Systems/kotlin規則包`:
  - 不影響。新增的 `configs/ast-grep/kotlin-choice/` 與 `kotlin-android/` 並列。
  - `_lint_wt_allow` 的白名單是「`configs/ast-grep/` 底下」,新目錄在範圍內。
  - `check.py` 的 `dt_table` 一般化須保持「情境決策表行為不變」,這點 spec 已寫。

最嚴重:major;blocking 共 5 條(i1、i2、i3、i4、i5)
