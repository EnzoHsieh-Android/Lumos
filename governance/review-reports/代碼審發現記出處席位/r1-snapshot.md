---
type: project
status: doing
created: 2026-11-20
updated: 2026-11-20
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/loop-convergence-recording
related:
  - "[[Projects/代碼審minor解綁_計劃]]"
---
# 代碼審發現記出處席位_計劃

## 白話

審查帳現在記得住每條發現最後是折入、放行還是重現不到,卻記不住它是哪一席報的。所以「哪一席最常報沒用的東西」只能用很小的樣本猜:2026-11-20 離線統計全帳 19,760 條發現,只有「那一輪恰好只有一席報東西」的輪能歸屬,架構對齊席 42 條裡放行 19 條、正確性席 39 條裡放行 17 條,樣本太小,不夠拿來決定要不要調席位。發現編號的字首也不能當依據:同一個字母在不同迴圈對到不同席(例如 s 只有一半是資安席)。

這份計劃在載體記帳時多記一欄「每條發現是哪一席報的」,代碼審新開的迴圈從生效日起必填;`lumos gov --stats` 多印一段逐席沒用率。純記帳,不改任何閘的判定。

WHY:代碼審載體記帳新增 `--finding-seat`,生效日後新開的代碼審迴圈必填,處置閘判定不動 [出處:2026-11-20 使用者回「好」,同意先做「記帳時每條都記是哪一席報的」;2026-11-21 使用者裁舊否決 canary-audit d4 在這裡不適用、照做] [因:Google Tricorder 以逐檢查的有效誤報率決定哪條檢查該降級,我們要做同樣的事就得逐席有數字;全帳整體沒用率 4.6%,人力主要在每輪條數與修補回歸,調席位前要先有逐席證據] [不選:沿用 `--finding-source`(它綁著「major 輪放行 minor」的核對與「載體最後記」擋法,不適用的輪寫側會擋,硬放寬會動到處置閘第⑨步);規定發現編號字首等於席位(字面慣例,歷史帳已證明守不住);只提醒不擋(選填欄位歷史上帶的比例很低:866 筆代碼審載體只有 52 筆帶逐條來源,資料會缺)]
PRIOR-ART: Google Tricorder 對每支分析器量「有效誤報率」(開發者看到後沒採取行動的比例),超過 10% 的分析器要改或關掉(Sadowski 等,Tricorder: Building a Program Analysis Ecosystem, ICSE 2015,https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/;Lessons from Building Static Analysis Tools at Google, CACM 2018,https://cacm.acm.org/magazines/2018/4/226371-lessons-from-building-static-analysis-tools-at-google/fulltext)。本 repo 既有的 `--finding-kind`(每條發現標在修什麼、全集要對得上、`gov --stats` 算佔比)就是同形狀的純記帳欄位,新旗標照它寫;生效日照 `_CHOICE_SINCE` 的寫法(常數加環境變數覆寫,測試總檔預設停在生效前)。
RETIRE-IF: 必填滿 8 週後,逐席沒用率沒有促成任何一次席位調整(降級、改條件席、改派工詞),或抽查發現編排者填錯席的比例超過一成——就把必填改回選填或整欄撤掉。

## 用詞

- **載體**:一輪裡帶 `--findings-set` 的那一筆帳,彙整全輪每條發現的去向;一輪只准一筆。
- **席名**:帳上 `auditor` 欄的字串,照記帳時給的原樣(例 `正確性-sonnet`,含模型尾碼)。
- **重現不到清單**:載體 `--refuted-set` 的 id;寫側已擋它跟發現清單重疊,所以兩份清單的聯集就是這輪全部發現。
- **結局帳**:迴圈收尾的那一筆(帶 `--outcome`),不算進「首筆帳」。

## 舊否決比對

- [[Systems/canary-audit]] 決策 d4(2026-08-08)否決過「跨期統計/席位信譽」:理由是模型換代、規格各異、植入假 bug 的難度由人拿捏,跨期累積的分數站在流沙上,而且模型變強後抓漏分數會飽和。2026-11-21 問使用者,裁「這次不同,照做」。差別寫在這裡:這次量的是「席位報的東西人有沒有採用」(Tricorder 的有效誤報率),不是對植入題打分;數字只給人看,不進任何閘、不自動調席位;統計只看最近 8 週,同一席不同模型分開列,模型換代不會跟舊數字混在一起。
- [[Projects/審查帳節點映射_計劃]] 決策 d2 停案時寫:沒有讀者的遙測欄位正是 canary 協議被淘汰的死因,重開要有讀者承諾讀新欄。這次的讀者是 `gov --stats` 那一段與 2026-12-11 的回頭檢查(帶數字給使用者裁席位);同一筆也寫「一輪只准一筆處置集合,逐席映射無處合法落帳」——這次欄位掛在那唯一一筆載體上,不新增第二筆處置帳。

## 範圍

- 做:①`canary record` 新增可重複旗標 `--finding-seat <id>=<席名>`,帳上存 `finding_seats: {id: [席名, …]}`;②代碼審載體(帶 `--findings-set`,帶不帶 `--round` 都算)在「這條迴圈首筆帳不早於生效日」時必填,而且要涵蓋發現清單與重現不到清單的每個 id;③席名必須是同輪帳上某一席的 `auditor`(含本筆);④`lumos gov --stats` 印逐席沒用率;⑤`loop next` 代碼審的載體記帳範本帶上這個旗標;⑥治理帳讀側認得這欄:型別檢查(值要是字串清單)與 canary 列的欄位白名單都加上它;⑦手冊與筆記同步。
- 不做:不改處置閘、代碼審留痕或任何推送前閘的判定;不改 `--finding-source` 的語意;不回溯舊迴圈(生效前開的迴圈照舊可以不帶);散文設計審不必填(設計審整體沒用率 1.3%,沒有逐席的需要),但帶了照收;不依沒用率自動調席位,調不調仍由人裁。

## 做法

- **旗標**:`--finding-seat <id>=<席名>` 可重複;同一個 id 可以給多次(多席報了同一件事),存成清單、照給的順序、重複的只留一個。跟其他逐條旗標一樣要跟 `--findings-set` 一起給,單獨給就擋。
- **鍵**:必須在發現清單(`--findings-set`)或重現不到清單(`--refuted-set` 的 id)裡;重現不到的也要記席位,因為它正是「沒用」的一種。
- **值**:必須等於同輪帳上某一筆的 `auditor`,或本筆自己的 `--auditor`(比對前兩邊都做 NFC 正規化);本筆沒帶 `--round` 時只能是本筆自己的 `--auditor`。手冊規定載體最後記,但工具只在帶 `--finding-source` 時強制;載體先記、席名還不在帳上時就擋下,訊息點名那個席名並指路「先記那一席、載體最後記」。讀不到這個迴圈的帳就擋,不猜。檢查放在讀進同迴圈帳之後、寫帳之前。
- **必填條件**:迴圈編號 `code-` 開頭、本筆帶 `--findings-set`(帶不帶 `--round` 都算)、這條迴圈帳上首筆(不算結局帳)的時間不早於生效日(帳上還沒有任何一筆時,本筆就是首筆,算生效後)。必填時,發現清單與重現不到清單的每個 id 都要有席位,缺的逐一點名。
- **生效日**:常數 `_FINDING_SEAT_SINCE`,設成合進主線的隔天;環境變數 `LUMOS_FINDING_SEAT_SINCE` 供測試覆寫,不是 YYYY-MM-DD 就用常數。測試總檔預設設成 9999-12-31,讓既有造帳測試不受影響,新測試自己改。
- **統計**:`lumos gov --stats` 在「發現在修什麼」那段後面加一段「逐席沒用率(最近 8 週)」:只算時間在最近 56 天內、帶 `finding_seats` 的載體(`gov --since-days` 給得比 56 小時,照它給的;窗口取兩者較小);每個 (id, 席) 算一次,id 在折入清單算有用,在放行清單或重現不到清單算沒用;席名照帳上原樣(含模型尾碼,例如 `正確性-sonnet` 與 `正確性-opus` 分開列),不合併不同模型;每席印條數、沒用條數與比例,依條數多到少。一條被兩席報的發現兩席各算一次。段尾固定印一句口徑:放行不一定是雜訊、折入不一定有用,只供人裁。
- **範本**:`loop next` 印的載體記帳範本,迴圈編號 `code-` 開頭時多一段 ` --finding-seat <id=席名>`(每條各一個);設計審的範本不印(設計審不必填,印了反而誤導)。

## 驗收條款

- [S1] 當代碼審迴圈首筆帳不早於生效日、載體帶 `--findings-set` 與 `--round` 卻沒帶 `--finding-seat` 時,`canary record` 應 以 rc 2 擋下、帳本行數不變,訊息含 `--finding-seat` [test:t_canary_record_finding_seat]
- [S2] 當必填情況下有 id(含只在重現不到清單裡的 id)沒有席位時,`canary record` 應 以 rc 2 擋下並點名缺的 id、帳本行數不變 [test:t_canary_record_finding_seat]
- [S3] 當 `--finding-seat` 的席名不是同輪帳上任何一筆的 auditor、也不是本筆的 auditor 時(含載體先記、那一席還沒入帳),`canary record` 應 以 rc 2 擋下、點名那個席名並指路「載體最後記」;本筆沒帶 `--round` 時,席名不是本筆 auditor 就擋 [test:t_canary_record_finding_seat]
- [S4] 當 `--finding-seat` 的 id 不在發現清單也不在重現不到清單、或寫法不是 `id=席名`(沒有等號、id 或席名空白)時,`canary record` 應 以 rc 2 擋下 [test:t_canary_record_finding_seat]
- [S5] 當每個 id 都有合法席位、其中一個 id 給了兩個席、另一個 id 同一席給了兩次時,`canary record` 應 rc 0,帳上 `finding_seats` 是照給的順序、去掉重複的清單 [test:t_canary_record_finding_seat]
- [S6] 當代碼審迴圈首筆帳早於生效日、或迴圈不是 `code-` 開頭時,載體不帶 `--finding-seat` 應 照常 rc 0 [test:t_canary_record_finding_seat]
- [S7] 當帶 `--finding-seat` 卻沒帶 `--findings-set` 時,`canary record` 應 以 rc 2 擋下 [test:t_canary_record_finding_seat]
- [S8] 當帳上有兩輪帶 `finding_seats` 的載體、另有一輪時間早於 56 天前時,`lumos gov --stats` 應 只算近 56 天那兩輪,印出逐席條數與沒用比例,數字跟手算一致,同一席不同模型分開列 [test:t_gov_stats_finding_seat]
- [S9] 當治理帳讀到 `finding_seats` 的值不是字串清單時,`lumos gov` 應 略過那一列;是字串清單時 應 照常收 [test:t_gov_stats_finding_seat]
- [S10] 當同一份帶 `finding_seats` 的帳問處置閘時,判定 應 跟不帶這欄時相同 [test:t_canary_record_finding_seat]
- [S11] 當 `code-` 迴圈在派工階段(plant-canary)跑 `loop next` 時,印出的載體記帳範本 應 含 `--finding-seat`;設計審迴圈的範本 應 不含 [test:t_canary_record_finding_seat]
- [S12] 當讀手冊與筆記時,新旗標的用法與必填條件 應 寫在 lumos-code-loop 手冊第 6 步、06 命令速查的記帳段、`Systems/loop-convergence-recording` [manual:逐處讀,確認三處都講到必填條件、值要是同輪席名、重現不到的也要標]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 新代碼審迴圈 r1 載體 `--findings-set c1`、沒帶 `--finding-seat` | rc 2,帳不變 | 本計劃〈範圍〉②;使用者 2026-11-20「好」 |
| S2 | 發現 `c1,a1`、重現不到 `g1`,只給 `c1=正確性-sonnet`、`a1=架構對齊-sonnet` | rc 2,點名 g1 | 〈做法〉鍵:重現不到也算沒用 |
| S3 | 同輪帳上只有 `正確性-sonnet`、`架構對齊-sonnet`,給 `c1=資安-sonnet` | rc 2,點名 資安-sonnet | 本計劃〈做法〉值那一點 |
| S5 | `c1=正確性-sonnet`、`c1=通才-sonnet`、`a1=架構對齊-sonnet`、`a1=架構對齊-sonnet` | rc 0;帳上 `{"c1": ["正確性-sonnet", "通才-sonnet"], "a1": ["架構對齊-sonnet"]}` | 〈做法〉旗標 |
| S6 | 迴圈首筆帳時間早於生效日,載體不帶 | rc 0 | 本計劃〈範圍〉不回溯舊迴圈 |
| S6 | `design-x` 迴圈載體不帶 | rc 0 | 本計劃〈範圍〉散文設計審不必填 |
| S8 | 第一輪 c1 折入(正確性-sonnet)、a1 放行(架構對齊-sonnet);第二輪 a2 重現不到(架構對齊-sonnet)、c2 折入且正確性-sonnet 與通才-opus 同報;另一輪 60 天前 c9 放行(正確性-sonnet) | 正確性-sonnet 2 條沒用 0;架構對齊-sonnet 2 條沒用 2(100%);通才-opus 1 條沒用 0;60 天前那輪不算 | Tricorder 有效誤報率定義:沒採取行動=沒用;使用者 2026-11-21 裁:只看近期、按模型分開 |
| S4 | `--finding-seat z9=正確性-sonnet`(z9 不在任何清單) | rc 2 | 本計劃〈做法〉鍵那一點 |
| S4 | `--finding-seat c1` 或 `--finding-seat =正確性-sonnet` | rc 2 | 本計劃〈做法〉旗標寫法 |
| S7 | 只帶 `--finding-seat c1=正確性-sonnet`、沒帶 `--findings-set` | rc 2 | 本計劃〈做法〉旗標:跟其他逐條旗標一樣 |
| S9 | 治理帳一列 `finding_seats: {"c1": "正確性"}`(值是字串) | `lumos gov` 不列那一列 | 本計劃〈範圍〉⑥讀側認得型別 |
| S10 | 同一份會判過的帳,一份載體帶 `finding_seats`、一份不帶 | 兩份處置閘都判過 | 本計劃〈範圍〉不改處置閘判定 |
| S11 | 首輪 `loop next code-x --tier high`(派工階段)與首輪 `loop next design-x --tier standard` | code-x 範本含 `--finding-seat`;design-x 範本不含 | 本計劃〈範圍〉⑤範本 |
| S12 | 讀 lumos-code-loop 手冊第 6 步 | 寫到必填條件、值要同輪席名、重現不到也要標 | 本計劃〈範圍〉⑦手冊同步 |

## 回退

- 必填:把 `_FINDING_SEAT_SINCE` 改成 9999-12-31,旗標變回選填;已寫進帳的 `finding_seats` 留著,`gov --stats` 照讀。
- 整欄撤掉:寫側對 `--finding-seat` 改成 rc 2 並指路「已停用」,統計段拿掉,手冊與筆記還原;帳上舊資料不刪(帳只往後加)。
- 處置閘沒有讀這欄,回退不影響任何凍結判定,不用動回放版本。

## 實務隱患

已排除:金流:只改審查帳的記帳欄位,不碰付款
已排除:對外送出:不連網、不寄送
已排除:不可逆:擋下時不寫帳,改正後重記同一輪;寫進去的欄位是純記帳,沒有閘讀它
- 併發與交易:記帳沿用既有的附加寫法,這次不新增寫入路徑
- 守衛面:記帳寫側多一道必填檢查,擋錯了會讓載體記不進帳、整輪卡住。防線:擋下時不寫帳、訊息點名缺哪些 id 或哪個席名;生效前開的迴圈不受影響;席名比對只要求「同輪帳上有這一席」,不要求跟報告內容對得上。
- 天花板:席位是編排者自填的,工具只驗席名存在,不驗那條發現真的出自那一席的報告。填錯會讓逐席數字失真,靠 REVISIT 抽查;要機械驗得從報告逐條對 id,那就是 `--finding-source` 的形狀,這次不做。
- 負擔:每條發現多一個旗標(真帳一輪 1 到 18 條),跟 `--finding-kind` 同量級;編排者在收貨時本來就知道每條是哪一席報的。
- 消費專案:這個工具也被其他專案用;生效日後它們新開的代碼審迴圈一樣要填。擋下訊息直接給寫法,不用查手冊。
- 樣本偏差:「放行」不一定是雜訊(可能是真問題但修的成本太高),「折入」也可能高估有用(major 一律要折)。統計段標明口徑,段裡只印數字與那一句口徑,不印任何調席位的建議。

REVISIT:2026-12-11 (上線約三週)跑 `lumos gov --stats` 看逐席沒用率,樣本夠(每席至少 30 條)就帶數字回報使用者,裁架構對齊席與正確性席要不要調;不夠就延兩週
REVISIT:2026-12-11 抽 10 條帶 `finding_seats` 的發現,對回席報告看席位有沒有填錯,錯超過一成照 RETIRE-IF 處理

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 逐檢查量有效誤報率、超過 10% 要改或關 | Tricorder(ICSE 2015) | https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/ |
| 「開發者沒採取行動」當作誤報的定義 | Lessons from Building Static Analysis Tools at Google(CACM 2018) | https://cacm.acm.org/magazines/2018/4/226371-lessons-from-building-static-analysis-tools-at-google/fulltext |
| 純記帳的逐條欄位、全集要對得上 | 本 repo `--finding-kind` 的既有做法 | [[Systems/loop-convergence-recording]] |

## 審計修正紀錄
