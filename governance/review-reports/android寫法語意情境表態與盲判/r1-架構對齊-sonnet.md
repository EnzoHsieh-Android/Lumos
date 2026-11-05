severity: major

我只讀了材料和既有程式,沒有改任何檔案。結論是:整體方向對齊(推送前不呼叫模型、先寫治理帳再寫標記檔、標記優先退治理帳、事件登記進不算收尾清單、擋的條件併進表態那一道)。有一處引入第二套題目表,屬 major,其餘是命名與細節的 minor。

## 問 1:分層與依賴方向
對齊的部分:
- 推送前只核盲判記錄,不呼叫模型。這跟既有「推送閘不呼叫模型」一致,盲判放在代碼審迴圈裡派。
- 多數決與仲裁的判定寫在 lumos 本體,併進 `_dispositions_verdict` 這一道,沒另開第七道。
  - file: `scripts/lumos:70626`(表態判定函式)
  - file: `scripts/lumos:71032`(check 流程裡「3.5 表態閘」那段)

不對齊的一處(**第二套題目表**):

severity: major
blocking: 是
引句:「另有一張第一次用到才讀型錄的情境題表,在四處各接一次」
- 既有做法是所有題都放在同一張表 `_STACK_QUESTION_SPECS`,載入時編譯成 `_STACK_TRIGGERS`,兩者一一對齊。
  - file: `scripts/lumos:37429`(題目表)
  - file: `scripts/lumos:37667`(編譯觸發字)
  - file: `scripts/lumos:38177`(適用性判定,用 zip 對齊兩張表)
- 這張表「載入時用程式追加題」已有先例,不必另起一張。
  - file: `scripts/lumos:37631`(`_STACK_QUESTION_SPECS["infra"] = [...]`)
  - file: `scripts/lumos:37654`(`.append(...)` 加 extcode 題)
- 計劃拒絕動態加的理由(錯位)站不住:先例就是在載入時追加,並同步編譯。
- 第二張表還會讓觸發字比對語意分叉。既有一律不分大小寫(`re.compile(_p, re.I)`),情境題改成分大小寫。
- 計劃列的「四處」漏了其他直接讀這兩張表的地方。每一處都得另做一份對照,否則情境題會在那裡「找不到題」:
  - file: `scripts/lumos:71583`(`_cmd_codeloop_recall_miss` 呼叫 `_stack_spec_by_id`)
  - file: `scripts/lumos:70803`(`_dispositions_template` 直接讀 `_STACK_QUESTION_SPECS` 取未觸發原因)
  - file: `scripts/lumos:61157`(直接讀 `_STACK_TRIGGERS`)
  - file: `scripts/lumos:37848`(`_STACK_QUESTION_SPECS["kt"]` 的 `android_only` 排除)
- 這些地方會否通通漏掉情境題,我判不準 ⚠。
- 建議改成載入時(或第一次用時)把型錄生成的題併入 `_STACK_QUESTION_SPECS["kt"]` 並一起編譯。不分大小寫的需求用既有的 `when_raw` 或加一個旗標處理。

## 問 2:命名與錯誤處理

severity: minor
blocking: 否
引句:「讀不到或格式壞 → 情境題整組不出題、印一行提醒,不擋、不記帳」
- 既有表態閘對壞設定的處理是退回預設並印警告,偏向「多問」。
  - file: `scripts/lumos:38143`(`stack_questions.gate` 不合法 → 用 all)
  - file: `scripts/lumos:37843`(kt 判不出平台 → 不排除題目)
- 本案是「讀壞就整組靜默放行」,方向相反。
- 只靠本 repo CI 擋型錄壞掉,對消費專案裝到壞版時沒有護欄。
- 建議明寫理由,或至少落一筆非硬性的帳,讓 `gov --stats` 看得到。

severity: minor
blocking: 否
引句:「記錄綁目標版本與材料 sha256」
- 既有的 `dispositions` 寫入有 `--branch` 與 `--at-sha` 處理。推別名分支、或 checkout 不在被推的 sha 時,記錄要綁被推的版本。
  - file: `scripts/lumos:71612`(`--at-sha` 驗證)
  - file: `scripts/lumos:71605`(`--branch` 說明)
- 計劃的 `blind-judge <結果.json>` 沒說同樣支援這兩個旗標。
- 治理帳寫入和標記檔寫入各自是獨立函式。計劃只說「同表態的讀寫慣例」,沒寫明是複用還是新抄一份。
  - file: `scripts/lumos:70145`(`_codeloop_dispositions_gov_log`)
  - file: `scripts/lumos:70166`(`_codeloop_write_dispositions`)
  - file: `scripts/lumos:70188`(`_codeloop_read_dispositions`)

severity: minor
blocking: 否
引句:「**情境題**:從型錄 `skills/kotlin-idioms/checks-catalog.md`〈情境決策表〉每一列自動生成的棧別題」
- repo 裡已有一套叫「情境出題」的機制,是需求風險面,比對的是計劃筆記文字。
  - file: `scripts/lumos:37281`(`_REQUIREMENT_FACETS`)
  - file: `docs/lumos-toolchain-knowledge/Systems/情境出題.md`
- 「情境題」和「情境出題」在字面上撞名。
- 題號 `kt-sit-D-<n>` 沿用 `kt-` 前綴,這點對齊。

## 問 3:第二種做法

severity: minor
blocking: 否 ⚠
引句:「窗裡要有一條符合那列那個 variant 的證據樣式,才算照做」
- 既有的「satisfied 是否真有做」查核,走的是 `needs_backing` 加破壞測試背書(`strong` 才算數)。
  - file: `scripts/lumos:70659`(satisfied 沒有 strong 背書 → 提醒)
  - file: `scripts/lumos:71562`(本機算背書存進記錄)
- 計劃的 PRIOR-ART 有講「驗行號存在」,但沒講為什麼不走既有的背書路。
- 兩者可以並存,因為一個驗「寫法特徵」、一個驗「有測試咬住」。
- 但「證明 satisfied 屬實」現在有兩套規則,建議明寫兩者的分工,否則下一個人會問該用哪套。

severity: minor
blocking: 否 ⚠
引句:「盲判席用 sonnet,一題一份材料;仲裁一律另開新代理」
- 既有審查席的產出走「席報告存進卷證再收貨、記帳」。
- 盲判席的產出是自己的 JSON,用 `blind-judge <結果.json>` 直接寫帳。
- 這是第二條「席產出進治理帳」的路徑。計劃沒說它跟席報告收貨的關係,例如盲判席的原始回覆要不要也存卷證。
- 這跟問 1 引用的「推送前不呼叫模型」不衝突,只是流程另一條。

事件命名本身(`blind-judge` 對 `dispositions`、`recall-miss`)和登記進 `LOOP_NOT_CLOSE_EVENTS` 都對齊:
- file: `scripts/lumos:19349`(登記清單)
- file: `scripts/lumos:19357`(同清單裡 dispositions、recall-miss 的條目)

指令形狀也合理:新種類用 `code-loop blind-judge`,跟 `code-loop dispositions`、`code-loop recall-miss` 同層。

## 問 4:落點

severity: minor
blocking: 否 ⚠
引句:「第二批的改檔前推列也呼叫它——兩案誰先實作誰建,後做的那案直接用」
- `lands_in` 的 `Systems/棧別提問表態閘` 和 `Systems/pitfalls-code-loop` 都已存在,放進去合適。
- 盲判的記錄、核對與統計屬於表態閘的延伸,放表態閘那篇對。
- 「要跑盲判」和手冊那步放 `pitfalls-code-loop` 也對。
- 棧別提問表態閘那篇〈邊界與刻意不做〉有「不用 LLM 判答案」那一句,計劃已寫明要改寫。
  - file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:108`
- `Systems/kotlin規則包` 目前不存在。它是母計劃(`Projects/Android協程與API寫法機械檢查標準_計劃.md:47`)預定新開的節點,所以本案的落點依賴另一份尚未實作的計劃。
- 決策表新增的兩欄屬於型錄資料,本案要寫哪一篇不明確,建議確認 `lands_in` 是指要寫進新節點還是只寫表態閘。
- 表態閘那篇目前「管 3 支檔、沒寫負責範圍」,本案再加進去前先補負責範圍比較好。

不對齊共 7 條,其中 major 1 條
