severity: major

## c1 API 類選擇點的節點起始行規則,讓鏈式呼叫永遠命中不到改動行
severity: major
blocking: 是。照字面實作,預期值表 S1 第一列與條款 S25 的主要案例都會得到「沒有壞法」。
- 位置:〈用詞〉選擇點、API 列(「只認 `navigation_expression` 後接 `call_suffix` 的呼叫」)、預期值表 S1。
- 問題:選擇點的命中條件是節點起始行就是改到的行,但 `navigation_expression`/`call_expression` 的範圍從接收者開始。Kotlin 鏈式寫法把 `.flatMapLatest { … }` 另起一行時,節點起點在上一行的接收者。
- 例:
  ```
  query
      .debounce(300)
      .flatMapLatest { repo.search(it) }   // 只有這行是增行
  ```
  整個 `flatMapLatest` 呼叫節點起始於 `query` 那一行(未改),所以不命中。S1 預期「`.flatMapLatest { repo.search(it) }` 一個 API 壞法」(開頭帶點,就是延續行)與 S25 的 ViewModel 案例都對不上。
- 佐證:grammar.js 的 `navigation_expression` 是 `seq($._expression, $.navigation_suffix)`,範圍涵蓋接收者。
- 建議:API 類改以呼叫名識別字或 `navigation_suffix` 的起始行判斷,只替換那一段;或明講「節點任一行是改到的行即算」。
引句:「語法樹掃描在改到的行上命中的選擇點規則節點(節點起始行是改到的行)」
file: `grammar.js:1218`

## c2 有效處置以 (file, line_sha) 認,同一檔裡內容相同的兩行會互相頂替
severity: major
blocking: 是。第二處相同的行不會被跑,也不會被擋,卻被當成已處置。
- 位置:〈用詞〉有效處置、壞法身分、S11「同一行已有有效處置 應 跳過」、S13 judge。
- 問題:`line_sha` 只雜湊那一行原文,不含脈絡。〈壞法身分〉另用上下各 ≤2 行的脈絡求唯一,但帳的處置鍵沒有帶它。
- 例:同一檔兩個函式各有一行 `if (a > b) value = a`,前後文不同,各自唯一。
  - 第一行 killed 後,第二行因為 (file, line_sha) 相同被「跳過」,從沒跑過。
  - 反過來,兩行各跑一次、一殺一活,同鍵的「最新一筆」決定兩行的狀態,殺掉的那行被誤擋,或存活的那行被放過。
  - `choice-judge` 只寫 line_sha,一次判就蓋掉兩處。
- 建議:處置鍵加上 `row`/脈絡雜湊,或明講同鍵多處的處理規則。
引句:帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed` 而且 `killing_test` 還在現在守的測試裡

## c3 一行一個壞法的挑法與唯一性前後矛盾,「不唯一」會擋推送也可能不擋
severity: major
blocking: 是。兩種字面讀法對同一行的推送閘結果不同。
- 位置:〈用詞〉一行一個壞法對照壞法身分,S3、S15。
- 問題一:挑法寫「依序取第一個類別;在那個類別的節點中取最左邊的一個」,但同一段末尾又說「一個類別都產不出就這一行沒有壞法」。
  - 只取第一個類別、最左一個節點,還是失敗就換下一個節點或下一個類別?論文 Listing 2 與 2.2 明講失敗要換下一個運算子。
  - 例:`val s = "id=" + n; if (x > 0)`,若洗牌後 AOR 排第一,最左的 AOR 節點是字串串接,被型別前提排除。照字面可能整行沒壞法,漏掉 ROR。
- 問題二:同一段把「套上後整個 `old` 在檔裡恰好一次」放進候選的篩選條件,失敗會落到「沒有壞法」,推送不擋。
  - 〈壞法身分〉則說往外各帶 ≤2 行仍不唯一就「標不唯一」,S15 又把「不唯一」列為推送擋下原因。
  - 候選篩選用的是未擴張的 `old`,還是擴張後的,也沒寫。
  - 例:`if (a > b) return` 在兩處的前後各 2 行也相同。篩選條件版讀法是無壞法、不擋;身分版讀法是不唯一、擋下要人判。
  - r2 的 H2 說「唯一性只在身分段定義」,但挑法那段仍留著它。
- 建議:挑法改成明確的迴圈(類別、節點、候選、帶行求唯一,各步失敗往哪走),不唯一只出現一處。
引句:依序取第一個類別;在那個類別的節點中取最左邊的一個,候選壞法依同一種子打亂
引句:整支檔不是恰好一次時依序往上、往下各多帶一行,最多前後各 2 行

## c4 `stop_group_on_kill` 與 `on_row` 在配方迴圈裡拿不到 weak 旗標
severity: major
blocking: 是。照字面在迴圈內實作,弱證據的 killed 會被當成強 killed。
- 位置:〈用詞〉殺掉判定、〈範圍〉2 中斷、S7、S12。
- 問題:spec 要在迴圈內判「已有一支強 killed 就略過其餘」,並由 `on_row` 在每條配方跑完時交出該列。
  - 現行 `cmd_guard_kill` 的 `weak` 是迴圈結束後才統一蓋章的(`res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty or res.get("_mtime_unsure"))`),註解寫明在迴圈裡設會被蓋掉。
  - `_mtime_unsure` 也要等寫檔還原後才知道。迴圈內的列沒有 `weak` 欄,字面實作就是 `row.get("weak")` 為空,當成強證據。
- 後果:
  - 弱證據(修改時間沒錯開、可能吃到舊編譯快取)的 killed 會提早停掉整組,其餘測試不跑。
  - 中斷時 `on_row` 交出的列被記成 `killed`(強)。這正好違反 guard-kill 合約「弱證據不放行」。
- 建議:寫明 `on_row` 與提早停止用的 weak 判法(迴圈內就能算的部分:`mt_ok`、`b_unsure`、`ws`、`flaky`、`node_dirty`),或把蓋章前移。
引句:`on_row` 回呼在每條配方跑完時交出那一列
file: `scripts/lumos:28145`

## c5 回報上限的種子用「壞法身分」,列號或型錄一變就重抽
severity: major
blocking: 是。S16 宣稱的穩定性在 rebase 之類常見操作下不成立。
- 位置:〈用詞〉回報上限、壞法身分、S16、S24。
- 問題:種子是「曾經存活過的行」全部身分排序後的雜湊,而〈壞法身分〉定義為 `file`、`line_sha`、`row`、`new_sha`。
  - 檔案上方任何增減行(rebase 到新主線、同檔別人的改動)都改變 `row`。
  - 型錄改動讓那一行挑到別的壞法會改變 `new_sha`。
  - 兩者都在沒有新存活行的情況下讓抽中的那批重抽。已處置的 14 行仍算,但原本沒抽中的行這時變成必須處置,上限的穩定性就沒了。
  - S24 說「型錄改動不讓舊帳失效」,但種子被它動到。
- 建議:種子只用 (`file`, `line_sha`) 的集合。
引句:處置抽中的行不會讓沒抽中的被重抽,因為種子只看
引句:`file`、`line_sha`(那一行原文的 sha256 前 16 碼)、`row`(列號)、`new_sha`

## c6 ast-grep 的欄位換算、`===`、容量類乾節點:三個小洞
severity: minor
blocking: 否。多數落成 no_result 或過度標記,不會做出錯誤的行為。
- 位置:〈用詞〉語法樹掃描、選擇點表 ROR、乾節點規則。
- 欄位:spec 讀「起訖行列」再用字串切片。含中文字串或 emoji 的行(Android 專案常見)容易把位元組欄與字元欄搞混。建議改用 byteOffset 並以 UTF-8 位元組切。
- `===` 與 `!==`:`equality_expression` 的運算子集合是 `!=`、`!==`、`==`、`===`(grammar.js:1651)。spec 只列 `==`、`!=`,規則要明確排除或涵蓋。
- 乾節點表:
  - `Timber.tag(TAG).d(…)` 的接收者是呼叫、不是 `Timber`,不會被認成 log。
  - `items.size == 0` 是 `equality_expression`,不在「comparison_expression」那條裡。
  - 兩者都會對 log 引數產生壞法,但只是噪音。
file: `grammar.js:1651`

## 語法樹可行性
- **節點名**:comparison_expression、equality_expression、conjunction_expression、disjunction_expression、additive_expression、multiplicative_expression、prefix_expression、call_expression、navigation_expression、statements、lambda_literal、call_suffix 在 grammar.js 都存在,名稱與 spec 一致。
- **沒有欄位**:二元運算式沒有 `field(...)`,只有 `if_expression` 的 `condition`、`consequence`、`alternative` 有。運算元必須用 `pattern: $A > $B` 的後設變數取,不能用欄位。spec 寫的就是後設變數,可行。
- **SBR 的兩個排除條件**:
  - 「無大括號控制句本體」:`control_structure_body` 接的是 `_statement`,不經 `statements`,所以規則自然不命中,這條排除是多餘但無害。
  - 「函式本體只有一個陳述的非 Unit 函式」:語法樹分不出 Unit。但區塊本體的非 Unit 函式必有 `return`,不會是呼叫陳述,所以實務上無需處理。
  - 例外:`val x = if (c) { f() } else { g() }` 的區塊內呼叫會被當 SBR 候選,刪掉後型別不合,落成 no_result。這屬於 spec 已承認的噪音。

## 與論文對照
- **表 1**:AOR、LCR、ROR、UOI 的候選與 spec 一致。
- **Listing 2 與 3.1(取一個運算子失敗就換下一個)**:spec 的挑法沒寫清楚,見 c3。
- **2.3**:上限「檔數 × 7、隨機挑」一致。spec 改成確定性種子,已列於差異⑤,但後果見 c5。
- **3.2.4 冗餘壞法**:論文為 `if (x != nullptr)` 抑制 `x == nullptr`、`false` 這類冗餘壞法。spec 的 UOI 與 ROR(`==` 只換 `!=`)沒有對應抑制。對 Kotlin 的 `x != null` 這類寫法,UOI 的 `!$B` 與 LCR 的 `false` 之間可能出現互相等價的壞法。這是品質問題,不阻擋。

## r2 折入檢查
- **H1(換成語法樹)**:大致到位,但 c1 顯示「節點起始行」這個新規則本身造成新漏洞。
- **H2(唯一性)**:未到位,見 c3。
- **H3(殺傷力批次)**:`stop_group_on_kill`、`on_row`、abort 拿掉、缺結果記 no_result 的語意都寫了。殺掉判定的優先序(強 killed 優先、再看弱證據與缺結果、最後才 survived)與現行 `cmd_guard_kill` 的 rc 序一致。實作面的 weak 時序問題見 c4。
- **H4(帳失效)**:有效處置改行為單位已寫,但鍵不夠細(c2),種子仍依賴會變的欄位(c5)。
- **H5 到 H11**:抽查掛鉤探針與範圍推導,pre-push 現有 `_PF_PR` 探針做法可被沿用,無衝突。

## 實務隱患逐類
- **效能與逾時**:已有 `--max-mutants`、基準只跑一次、殺掉就停。新增一支全新的 500 行 Kotlin 檔會產生數百個壞法,要分多次呼叫,RETIRE-IF ② 已涵蓋。無新增 blocking。
- **併發與交易**:已排除(單人單機),且治理帳逐筆追加。無。
- **資安**:ast-grep 以參數清單呼叫、不開 shell,暫存檔路徑不進指令。無。
- **帳量**:每筆只存雜湊,守的測試對照放 `run` 那筆,S20 釘位元組上限。無。
- **跨版本漂移**:已記 ast-grep 版本。c6 的欄位換算屬此類。

## 圖譜鏡頭(固定席)
- **Systems/guard-kill**:★INVARIANT★ rc 優先序(survived 優先於 drifted、abort、error;弱證據不放行)不受影響,前提是不傳新參數時行為不變,spec 的〈回退〉已承諾這點。
  - 帶 `stop_group_on_kill` 時,略過的列有新 verdict,現行 rc 邏輯對未知 verdict 落入「全 killed 回 0」的分支。choice-kill 自己算 rc,不受影響。實作時建議對略過列在 rc 計算前剔除。
  - ★INVARIANT★ `--json` 成功時 stdout 恰一行 JSON 不受影響:choice-kill 不走 `--json`。強制結束時印工作樹路徑應走 stderr。
  - 另請注意 c4:弱證據被當強證據,會削弱「弱證據不放行」的精神。
- **Systems/規格閘**:不影響其既有行為。新增一圈在 `_spec_gate_push_scan` 之後,「算不出來放行」沿用。唯一偏離是「治理帳在 B 不存在或讀不了就擋」,spec 已明講與預期值表那道同一政策,不違反既有合約。

最嚴重:major;blocking 共 5 條
