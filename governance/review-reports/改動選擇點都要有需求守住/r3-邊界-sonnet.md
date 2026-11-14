severity: major

## b1 乾節點的複合規則在 ast-grep 與 scan 輸出下做不出來,而且「旗標」列的字面跟自己的預期值表打架
severity: major
blocking: 是——照字面實作,條款 S4「複合節點只有所有子節點都乾才算乾」沒有任何可行做法,實作者只能默默退化成「落在某個乾節點範圍內」。
- 位置:〈用詞〉乾節點規則(「複合節點照公式 1」)、〈用詞〉語法樹掃描(只讀命中的規則編號、節點範圍、節點原文與後設變數)、S4、預期值表 S4 最後兩列。
- 問題一:公式 1 是遞迴(所有子節點都乾,整個才乾)。
  - ast-grep 規則不能遞迴。`matches` 互相引用會被判循環依賴,所以最多只能寫固定深度。
  - 掃描輸出只有「命中的節點」,沒有該複合節點的子節點清單,lumos 無從判斷「子節點是否都乾」。
  - spec 也沒定義「子節點」是只算具名節點,還是連 `if`、`(`、`&&` 這些符號都算(`grammar.js` 裡運算子是匿名 token)。
  - 例:`val x = BuildConfig.DEBUG && items.size > 0`。兩個運算元都乾,整個 `&&` 應該乾(LCR 不產生)。但掃描輸出只有兩個子節點各自的範圍,沒有任何規則命中「整個 `&&` 節點」,所以 LCR 照常產生。
  - 這個缺口 spec 沒承認。第一輪審查的 b2、b5 已經指過乾節點範圍問題,這次換成語法樹後還是沒補。
- 問題二:「旗標」列寫「含 `BuildConfig.DEBUG` 的條件節點」,字面就是整個條件含它就整個乾。
  - 照這個寫法,`if (BuildConfig.DEBUG && x > 1)` 的整個條件都乾,`x > 1` 不可挑。
  - 但預期值表 S4 明寫 `x > 1` 照常可挑,兩者矛盾。
  - 預期值表另一列「整個 if 沒有壞法」只是因為裡面沒有任何選擇點,測不出複合規則有沒有做出來。
- 佐證:
  - `grammar.js` 的 `if_expression` 只有 `condition`、`consequence`、`alternative` 三個 field,`conjunction_expression` 等沒有 field。
  - 既有規則包的寫法也都是固定深度的 `has`/`inside`。
- 引句:「複合節點照公式 1:只有所有子節點都乾才整個乾」
- 引句:「讀每個命中的規則編號、節點範圍(起訖行列)、節點原文與後設變數(運算元)」
- file: `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/abe4deee-64ee-43ea-85c3-2a647e0b825a/scratchpad/tsk/grammar.js:1496`

## b2 鏈式呼叫的「節點起始行」不是改到的那一行,S1 第一列與 S25 照字面做不出來
severity: major
blocking: 是——Kotlin 慣用的「`.flatMapLatest { … }` 另起一行」寫法,照字面實作會挑不到 API 壞法,驗收條款 S25 也會是 0 個壞法。
- 位置:〈用詞〉選擇點(「節點起始行是改到的行」)、API 列(「只認 navigation_expression 後接 call_suffix 的呼叫」)、〈用詞〉壞法身分(`old` 含到節點最後一行)、預期值表 S1 第一列、S25。
- 問題:在 `grammar.js` 裡 `call_expression` 是 `seq(_expression, call_suffix)`,`navigation_expression` 是 `seq(_expression, navigation_suffix)`。
  - 所以鏈 `query⏎.debounce(300)⏎.flatMapLatest { … }` 的最外層 `call_expression` 起點在 `query` 那行,不在 `.flatMapLatest` 那行。
  - 只改 `.flatMapLatest` 那行時,這個節點的起始行不是改到的行,API 壞法不出現。
  - 若改以 `navigation_suffix` 或識別字當被報的節點,spec 沒寫。
  - 而且 `.distinctUntilChanged()` 拿掉要用整個 call 節點(取接收者),起點又回到鏈頭。
  - `old` 也會變成整條鏈到結尾 lambda 的所有行,而不是改到的那行。
- 同族:LCR 的 `&&` 放在下一行開頭(Kotlin 允許)。`conjunction_expression` 起點在上一行,只改 `&& b` 那行也挑不到。
- 既有規則包也是用節點起始行(`check.py:1518`),所以這不是工具特性造成的誤會,是 spec 沒指定「被報的是哪個節點」。
- 引句:「語法樹掃描在改到的行上命中的選擇點規則節點(節點起始行是改到的行),扣掉落在乾節點範圍內的。」
- file: `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/abe4deee-64ee-43ea-85c3-2a647e0b825a/scratchpad/tsk/grammar.js:1204`
- file: `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/abe4deee-64ee-43ea-85c3-2a647e0b825a/scratchpad/tsk/grammar.js:1218`

## b3 ast-grep 不在時推送閘一律擋,跟生效日、回退、S21、規格閘放行先例、〈舊否決比對〉都矛盾
severity: major
blocking: 是——字面實作後,沒裝 ast-grep 的機器,只要改一支 `.kt` 就被擋,連回退開關也關不掉。
- 位置:〈用詞〉語法樹掃描、〈範圍〉4 算不出來與條件、〈舊否決比對〉、〈回退〉第一條、S6、S21。
- 問題一:
  - 〈範圍〉4「算不出來」寫「ast-grep 不在而範圍有 `.kt` 正式碼改動 → 擋」。
  - 〈條件〉卻要求「至少一行有壞法、有 kotlin-junit 平台、生效日之後」。
  - 沒裝 ast-grep 就算不出「至少一行有壞法」,所以兩者的先後順序沒定。
  - 兩個條件在 spec 裡互相衝突:
    - S21「專案沒有 kotlin-junit 平台」與「改動只有 log 與 import」都要求不擋;
    - 〈回退〉要求 `_CHOICE_SINCE` 設成遠期就整個不要求。
  - 按「先擋 ast-grep」實作,這三條都破功。
- 問題二:這跟自己的〈舊否決比對〉矛盾,也跟既有先例矛盾。
  - spec 自己寫「掃描算不出來只提醒不擋;只有治理帳讀不到才擋」。
  - `scripts/lumos:39320` 的先例是新增告警閘「工具沒裝 → 自動放行並記帳」,而 spec 引這個先例用的是 rc 3 語意。
  - 同一個工具缺失,choice-points 回 3(沒檢查到),推送卻擋,沒有任何翻案理由或出路(例如 CI 映像沒裝)。
- 問題三:其他會用到掃描的指令,沒 ast-grep 時的行為 spec 沒寫。
  - `choice-judge` 要判「是不是有壞法的改到的行、乾節點」。
  - `situation-rule --point` 要「定位在目前範圍算得出壞法」。
  - 兩者都需要掃描,沒寫 rc、沒寫訊息。
- 引句:「這份照它,掃描算不出來只提醒不擋;只有治理帳讀不到才擋(同預期值表那道)。」
- 引句:「改動只有 log 與 import」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39320`

## b4 有效處置只認 (file, line_sha),同內容的第二處免跑、免處置
severity: major
blocking: 是——字面實作下,同一支檔裡複製貼上的同內容選擇點,只要一處被殺掉或被判,另一處完全沒驗就視為已處置,「每個選擇點有需求守住」的合約被放掉。
- 位置:〈用詞〉有效處置、壞法身分(`row`、`new_sha` 另記)、S11(跳過有效處置的行)。
- 問題:
  - 內容相同的行在 Kotlin 很常見,例如 `if (x == null) return`、`.distinctUntilChanged()`、`val ok = a > b`。
  - 兩處內容相同、前後各 2 行不同時,各有唯一的 `old`,是兩個不同壞法。
  - 但帳的有效處置鍵是 `(file, line_sha)`,不含 `row` 與壞法身分。
  - A 處 killed 後,B 處不被 choice-kill 再跑(只跑還沒有有效處置的行),推送閘也當作已處置。
  - 殺掉 A 處的測試完全可能碰不到 B 處。
  - `killed` 與 `judged` 兩種處置都有這個洞。
- 反例:同一檔兩個函式各有 `if (items.size < limit) {`,A 處綁測試殺掉。B 處新增後 choice-kill 回報 0 個待跑,推送放行。
- 引句:「帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed` 而且 `killing_test` 還在現在守的測試裡,或是 `judged`。」

## b5 「提早 return」乾節點丟掉論文的「回傳空容器」條件
severity: major
blocking: 是——字面實作會讓守衛式提早回傳整個靜默放過,選擇點表原本要管的行為差異反而不被檢查。
- 位置:〈用詞〉乾節點規則「提早 return」(引 A.1.22)。
- 問題:
  - 論文 A.1.22 的例子與觸發條件,是「檢查空容器、回傳空容器」(`ImmutableMap.of()`)。論文還明講這個啟發式「not sound」。
  - spec 寫成 `if ($X.isEmpty()) return …`,任何 return 值都算乾,範圍整個 if。
  - 例:`if (token.isEmpty()) return AuthError.Missing` 或 `return null` 或 `return -1`,回傳值是需求決定的,卻整個被當乾節點。
  - 這類守衛是行為而不是優化,單元測試與需求都該守。
  - 這是 spec 引論文時漏掉的條件,不是列在「跟論文不同的地方」的差異。
- 引句:「提早 return(`if ($X.isEmpty()) return …` 整個 if;A.1.22)」

## b6 第二輪折入核對
severity: minor
blocking: 否——折入到位處多,未到位處是下列細節。
- 到位:
  - 運算元用後設變數;SBR 限 `statements` 直接子節點。「不在 `value_arguments`」與「無大括號本體」在 Kotlin 文法下自動成立,因為無大括號本體是 `control_structure_body > _statement`,不經 `statements`,S5 第三列成立。
  - 乾節點以節點為單位。
  - 論文表 1 的候選(AOR、LCR、ROR)與 UOI、SBR 對得上論文 Table 1。
  - 回報上限「檔數×7」「從存活隨機挑」對得上論文 2.3。
  - 每行取一個、先洗運算子類別,對得上 Listing 2。
- 未到位:
  - 〈一行一個壞法〉寫「取第一個『套上後整個 old 在檔裡恰好一次…』的候選」,而 `old` 對所有候選相同。字面讀成「過濾沒有唯一 `old` 的候選」,重複行會變成「這一行沒有壞法」而不是 S3 要的「標不唯一」,靜默漏掉。
  - 「取最左邊的一個」遇到同起點的巢狀節點沒有定義,例如 `a && b && c` 的內外兩個 `&&`,實作各取一個,帳會對不上。
  - 「往上、往下各多帶一行,最多各 2 行」的先後次序沒寫。
- 引句:「在那個類別的節點中取最左邊的一個,候選壞法依同一種子打亂,取第一個」

## b7 「時間」乾節點比論文窄:`delay(...)` 這個陳述本身仍會被 SBR 刪
severity: minor
blocking: 否——結果是多出必然存活的雜訊(用 runTest 虛擬時間時刪掉 `delay` 測試看不出來),不是錯行為。
- 位置:〈用詞〉乾節點規則「時間」,引論文 A.1.4。
- 論文 A.1.4 的第一個例子是把 `SleepFor(...)` 整個陳述當乾節點(圖裡紅色的刪除)。
- spec 只把 `delay`、`withTimeout` 的引數節點當乾。
- 結果:`delay(300)` 這一行的 SBR 照挑。Kotlin 協程程式碼裡這種行很多。
- 同族:論文 A.1.5 的 `e.printStackTrace()` 也被當乾,spec 沒收。
- 引句:「時間(`delay`、`withTimeout`、`withTimeoutOrNull` 呼叫的引數節點;A.1.4)」

## b8 Kotlin 的空值檢查換成相反運算子,會破壞智慧轉型而編不過,落成會擋推送的 no_result
severity: minor
blocking: 否——spec 的天花板 2 承認過型別前提不夠,但這個形狀太常見,值得單獨點名。
- 位置:〈用詞〉ROR(`==` 只換 `!=`,`!=` 只換 `==`)、型別前提、判定(no_result 擋推送且不受上限)。
- 例:`if (user != null) { show(user.name) }` 只有一個候選 `==`。換完 `user.name` 因為失去智慧轉型而編不過,記成 no_result「壞法編不過」。
- 因為只有一個候選,沒有別的壞法可退,只能人工 `choice-judge --as not-applicable`。
- 這類行在 Android 程式碼很多,會把 RETIRE-IF ③ 的被擋筆數推高。
- 論文 3.2.1 的做法是用規則事前擋,不是事後記錄。
- 同族:AOR 的 `$A`、`$B` 單邊候選在 Int 與 Long 混算時也常編不過。
- 引句:「`equality_expression` 的 `==` 只換 `!=`(附錄 A.1.23);`!=` 只換 `==`(本計劃比照)。」

## b9 ast-grep 呼叫細節 spec 沒指定,漏掉會靜默變成「沒有選擇點」
severity: minor
blocking: 否——都是實作時會踩的坑,但漏了會讓推送閘悄悄放行或誤報。
- 暫存檔副檔名:ast-grep 靠副檔名認語言。
  - 暫存檔若不以 `.kt` 結尾,掃描零命中,推送閘會靜默放行整批改動。
  - 引句:「交 ast-grep 的是暫存檔,掃完刪」
- 退出碼:`ast-grep scan` 遇到 `severity: error` 的命中會回 rc 1。
  - 既有 `check.py:1537` 已把 rc 0 與 1 都收。
  - spec 沒寫規則該用什麼嚴重度、rc 1 怎麼處理。實作者若用 `check=True` 就會把正常命中當失敗。
- ERROR 節點:ast-grep 遇到文法版本不認得的新語法(Kotlin 2.x)會留 ERROR 節點。
  - ERROR 附近的命中可能偽造選擇點或範圍錯位。
  - spec 沒寫「命中跟 ERROR 節點重疊就略過」。
- 套件版本:`grammar.js` 是 fwcd 主線(有 `_delegate_end_hint` 等新節點),ast-grep 內建的 Kotlin 文法版本可能較舊。
  - spec 只記版本、用樣本檔自檢,沒鎖節點名。
  - 節點名(`navigation_expression`、`call_suffix` 等)我只能對 `grammar.js` 驗證,沒法對真正的 ast-grep 內建版驗證。

## b10 實務隱患鏡頭
severity: minor
blocking: 否——其餘風險類已讀,無 blocking。
- 輸入邊界(空、全形冒號、`]`、換行、超長):
  - 定位從右切最後一個 `:`,行號要求正整數,有處理。
  - 空字串定位、全形冒號 `：`(不是 `:`)、多行貼上的定位沒寫,會落到 rc 2 的寬泛訊息。
  - `--reason` 要求「至少 10 實字」,但「實字」沒有定義,全形空白或零寬字元算不算沒寫。
  - 這個專案是單人、AI 依序操作的威脅模型,記為 minor。
- 資源:一次呼叫一棵工作樹、基準每支測試指令只跑一次、`--max-mutants` 30、`stop_group_on_kill`,spec 已處理。ast-grep 對全檔各跑一次,每檔一次子程序,有 `_KT_SIT_BUDGET` 時限,無 finding。
- 帳量:每筆 ≤4096 位元組(S20),守的測試對照每次呼叫只記一次,無 finding。
- 併發:spec 已寫明排除(單人單機),不報。

## 固定席逐條判(Systems/guard-kill 兩條合約)
severity: clean
blocking: 否——兩條都不受影響。
- 合約 1:rc 優先序(survived→rc1、drifted/abort/error→rc2、弱證據不放行執行錯誤)。
  - 不影響:新增的 `source`、`stop_group_on_kill`、`on_row` 都是選用參數。〈回退〉明寫「不傳維持原行為」,預設路徑不動。
  - 啟用 `stop_group_on_kill` 時,被略過的配方記成「略過」,只要不被計成 error/drifted/survived,rc 優先序就不變。實作時要確認這一點。
- 合約 2:`--json` 成功跑完時 stdout 恰一行 JSON。
  - 不影響:`choice-kill` 不走 `--json`,而「強制結束印工作樹路徑」只發生在 rc 2 的中斷路徑,明文不在合約範圍內。
  - 實作時建議這行印到 stderr,spec 沒寫。
- 規格閘節點沒有 INVARIANT。〈範圍〉4 在 `_spec_gate_push_check` 另起一圈,不改既有圈。「算不出範圍放行」那一句,新增的兩個擋(沒有 ast-grep、帳不在)是明文例外,但沒有翻案依據(見 b3)。

最嚴重:major;blocking 共 5 條
