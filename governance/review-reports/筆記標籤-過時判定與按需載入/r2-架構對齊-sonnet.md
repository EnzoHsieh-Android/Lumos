severity: major

以下 `scripts/lumos` 與各筆記的行號,都是在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw` 這份唯讀副本上對的。

## 四問回答

**1. 分層與依賴方向**
- 大方向有對齊:判過時掛在存量漂移檢查、寫法提醒掛在筆記形狀檢查、搜尋擴在 `lumos search`。這是 r1 的主要洞,補上了。
- 剩下三處沒講清楚或有衝突:
  - 欄位判定放進 `_drift_check_core` 還是另開一支,計劃沒講。舊句檢查 m1 的先例是另開一支、自己的開關、自己的預算(`scripts/lumos:29866`、`scripts/lumos:29869`),因為核心那支也給考試與歷史重放用。
  - 「新寫的欄位終點不吻合就擋」是新增行的形狀判定,卻放在存量漂移檢查(R2A2)。
  - 「抽成共用函式」沒說資料來源(R2A5)。
- 沒有跨層直呼。

**2. 命名與錯誤處理**
- 對齊的部分:
  - `note_shape.tag_hints` 的 warn/off 與壞值照預設並講一句,跟 `note_shape.negation` 同形(`scripts/lumos:25560`)。
  - `drift_check.fields` 的壞值照預設 block,跟 `drift_check.old_sentence` 同形(`scripts/lumos:29724`)。
  - 單次跳過 `LUMOS_SKIP_DRIFT_CHECK=1` 只認 1、會留帳(`scripts/lumos:29786`)。
- 不一致的有:
  - `drift ack` 的種類是寫死的(R2A4)。
  - `[status:superseded]` 在現有 lint 裡的訊息講的是「整行刪掉」(R2A7)。
  - 搜尋旗標的 `--top` 預設值與 `--prefix` 命名(R2A10、R2A11)。

**3. 第二種做法**
- 有一處:`路徑::名稱` 的切法跟 `_drift_cond_split` 不同(R2A1)。
- 其餘多是「沒講沿用哪支」的小處:W4 沒說要用 `rule_lifecycle_warnings`(R2A8),W2 這類寫死數量的句型比對沒有量測就上線(R2A9)。
- 新的 Python 字面值求值器不算第二種做法。既有的 ast 走訪只取名稱,不取值(`scripts/lumos:28098`、`scripts/lumos:28140`)。

**4. 落點**
- 三篇的分工大致對:判過時進存量漂移守衛,新寫行提醒進筆記內容閘,搜尋旗標與 lint 進 lumos-cli-read。
- 有兩處不對:
  - S4 這類新寫行的擋跟存量漂移守衛自己寫的 responsibility 衝突(R2A2)。
  - doctor N 的重算抽出來,但 `Systems/check-n-recomputable` 沒列進 `lands_in`(R2A6)。

## Findings

**R2A1 `::` 切法是第二套,而且跟計劃說的「沿用同一支」自相矛盾**
severity: major
blocking: 是——引入第二種路徑與名稱的切法,等於回頭條件探針的符號判定拿不到同一個名稱。
引句:「名稱可以再含 `::`(Rust、C++ 的限定名)」
- 既有切法是 `_drift_cond_split`,從最後一個 `::` 切開,名稱只剩最後一段。它的註解寫明,原本四處各自切、點名範圍連三輪對不上,才收成單一實作。
- 計劃改成「第一個帶副檔名路徑之後的 `::`」,名稱可含 `::`。但〈錨點〉那列又說求值「沿用同一支 `_DriftProbeTree`」。
- 該類別的 `_defines` 比的是簡單名稱集合(函式、類別、模組層指派),比不到 `Client::connect` 這種限定名。所以 S6 的限定名案例,沿用既有判定根本接不上。
- `_drift_probe_path_warn` 還專門把 `型別::方法` 當寫錯提醒(`scripts/lumos:28649`),跟新規則直接相反。
- 要嘛沿用 `rsplit` 並承認限定名只取最後一段,要嘛明講改 `_drift_cond_split` 且連帶改探針。現在是兩套並存。

佐證行 file: `scripts/lumos:28241`
佐證行 file: `scripts/lumos:28649`
佐證行 file: `scripts/lumos:28423`

**R2A2 「新寫欄位終點不吻合就擋」是新增行的形狀判定,放進存量漂移檢查,跟自己的邊界和候選篩選都衝突**
severity: major
blocking: 是——新寫行的擋屬於筆記內容閘的職責,存量漂移守衛的 responsibility 明寫不負責;而且計劃自己的候選篩選規則下,這條根本觸發不到。
引句:「這次新寫的欄位在終點就不吻合 → 擋(寫錯了)」
- 存量漂移守衛的 responsibility 寫「不負責新寫句子的形狀(筆記內容閘)」。
- 既有的切法:REVISIT 新寫行的格式錯誤由筆記內容閘擋(該節點的 S10 那條 WHY);「狀態變了」才由存量漂移檢查擋。
- 同一張表的標題寫「只看這次改到 `路徑` 那支檔的欄位」。新寫了一條欄位、但那支程式檔這次沒改的推送,候選篩選根本不會挑到它,S4 不會觸發。這是補丁跟原文銜接處的不一致。
- 要擋「寫錯」,既有零件是筆記形狀檢查的新增行抽取(`_notelines_new`)。要嘛移到筆記內容閘並承認它要讀程式檔,要嘛把 S4 的前提改成「同一次推送也改到那支檔」。

佐證行 file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:8`
佐證行 file: `scripts/lumos:25618`

**R2A3 欄位判定放進 core 還是另開一支、時間預算怎麼算,沒對齊舊句檢查的先例**
severity: minor
blocking: 否——結構上掛在同一道閘,只是沒說沿用哪個形狀;計劃寫的「總時間預算」跟先例的各自預算對不上。
引句:「重算受存量漂移檢查的總時間預算管,不再每個標記各自無上限地掃整個 repo。」
- m1 的先例:判定另開一支,不放 `_drift_check_core`;有自己的開關和 `_drift_m1_guarded`;有自己的 `_DRIFT_M1_BUDGET_SEC = 30`,不吃核心剩下的預算;`cmd_drift_check` 回兩邊較大的 rc。
- 核心和探針用的是 `_DRIFT_BUDGET_SEC = 60`。計劃說「總時間預算」,沒講用哪一個,也沒講欄位結果跟 c1 到 c5、m1 的 rc 怎麼合併。
- `drift_check.gate=off` 時欄位還跑不跑,計劃也沒寫。m1 的先例是各管各的。

佐證行 file: `scripts/lumos:29802`
佐證行 file: `scripts/lumos:29869`
佐證行 file: `scripts/lumos:29864`

**R2A4 逃生口宣稱「`drift ack`(既有)」,但 ack 的種類是寫死的清單,欄位這一種沒接**
severity: minor
blocking: 否——只是錯誤訊息指向的指令用不了,結構上沒新做法。
引句:「加上單次跳過(`LUMOS_SKIP_DRIFT_CHECK=1`,既有)與 `drift ack`(既有)的指令。」
- `cmd_drift_ack` 只收 `_DRIFT_KINDS = ("probe","c1",…,"m1")`(`scripts/lumos:27554`),比對鍵是 `(路徑, 原文, 種類)`。
- m1 為了接進 ack,另做了 `_drift_m1_split_acked` 和 `--name` 的特例。欄位發現要新增一種,同時改 `_DRIFT_KINDS`、種類說明表和比對路徑。
- 欄位擋的是帶欄位的那一行,數字一改原文就變,ack 的「一字不差」比對怎麼綁也沒講。
- 計劃的分期第 1 步沒列這件事,「誤擋的逃生口」目前只有單次跳過和整類關掉。

佐證行 file: `scripts/lumos:28754`
佐證行 file: `scripts/lumos:28860`

**R2A5 「doctor N 與漂移檢查呼叫同一個重算函式」沒講資料來源,容易長出第三條讀檔路徑**
severity: minor
blocking: 否——同一個函式的目標方向對,但缺關鍵的介面約定。
引句:「本案把 doctor N 段裡內嵌的重算抽成共用函式,存量漂移檢查也呼叫它」
- doctor N 用 `os.walk(repo_root)` 掃工作目錄,硬上限 4000 檔、40MB。
- 漂移檢查需要在起點和終點兩棵 git 樹上各算一次。既有的 `_DriftProbeTree` 就是為了讓「提交的樹」和 `'disk'` 走同一個讀法(`scripts/lumos:28297`)。
- 若共用函式吃檔案清單加讀取器,應該明講它吃 `_DriftProbeTree`;若各自傳路徑,會變成 doctor 一套、漂移一套,S7 的合約形同虛設。

佐證行 file: `scripts/lumos:3017`
佐證行 file: `scripts/lumos:28297`

**R2A6 `lands_in` 漏列 doctor N 的家**
severity: minor
blocking: 否——只影響記錄落點,不影響實作結構。
引句:「抽出 doctor N 的重算成共用函式;新寫數量與值的求值器」
- doctor N 段的家是 `Systems/check-n-recomputable`(about_code 列了 `scripts/lumos`)。
- 計劃要動它的重算函式,三篇 `lands_in` 都不是它。改了那段程式卻沒寫進它的家,會踩鐵則 5。
- 另外,三類欄位的語法與解析器(含 `parse_rule_fields` 旁邊的新正則)落在哪一篇,也沒說。

佐證行 file: `docs/lumos-toolchain-knowledge/Systems/check-n-recomputable.md:101`

**R2A7 `[status:superseded]` 擴到 WHY、PITFALL 行,但現有 lint 對它的訊息是「刪掉整行」**
severity: minor
blocking: 否——欄位名沒變,但政策方向跟既有說法衝突。
引句:「既有欄位,擴到 WHY、PITFALL 行」
- 現行 `rule_lifecycle_warnings` 對標了 superseded 的 RULE 行提醒「確定撤掉就把整行刪掉,別留著讓人誤讀」(`scripts/lumos:3336`)。
- 計劃反過來要求標了 superseded 就留著、加指向取代者的連結,搜尋預設藏起來。
- 對 WHY、PITFALL 新規則沒問題,但 RULE 行的提醒訊息、skill 說明和 S18 要一起改成同一個說法,不然同一個欄位在兩種前綴上講的建議相反。
- 計劃的分期沒列修這句訊息。

佐證行 file: `scripts/lumos:3331`

**R2A8 W4 要走新增行路徑,但既有的筆記形狀檢查是刻意不跑 RULE 生命週期的**
severity: minor
blocking: 否——可以沿用既有函式,只是計劃沒寫,容易另寫一份。
引句:「只對新寫的 RULE 行(走新增行那條路,不是整篇 lint)印缺 since、retire、until 過期」
- `context_marker_warnings` 的註解寫「筆記形狀擋傳 `_NOTE_SHAPE_PREFIX_RULES`,只看 FACT/FLOW/DEP;RULE 行的生命週期檢查只在預設時跑」。
- 所以 W4 是推翻這個刻意切分。這沒問題,但要明講沿用 `rule_lifecycle_warnings` 當判定、不另寫。否則會長出兩份缺 since、retire 的判定(lint 一份、提交時一份)。
- 還有一件事:`rule_lifecycle_warnings` 也會講 `until` 過期、`confirmed` 過期、`status` 非法值。W4 只說「缺 since、retire、until 過期」,範圍跟函式不同,要明講是挑一部分還是全套。

佐證行 file: `scripts/lumos:3314`
佐證行 file: `scripts/lumos:3366`

**R2A9 W1 到 W6 套在只為否定現況句寫的提醒管線上,而且 W2 的句型比對沒有量測就上線**
severity: minor
blocking: 否——結構上沿用同一道閘,但上線門檻跟先例不一致。
引句:「只看摘要行;FACT 排除(它寫的是程式答不了的現況)。」
- 現有的 `hints` 容器就是為否定現況句寫的:`{"items": [], "error": None, "seen": 0}`,`_ns_negation_collect`、`_ns_negation_prepare`、`hinted` 帳的 `check: "negation"` 都是專用的(`scripts/lumos:25849`)。
- 要同時承載 W1 到 W6 加欄位寫壞,需要泛化這個容器,計劃沒提。
- 先例是字眼表抄自量測程式、「上線前準度 40%」才決定只提醒(筆記內容閘 2026-09-30 那條 WHY)。W2 的「只有/唯一/恰好 N」句型,正是筆記內容閘 2026-09-27 那條 WHY 說「準度約三分之一、撐不起硬擋」的那一類,現在新做一份提醒,卻沒有量測程式或字眼表釘住。
- 它只提醒不擋,所以不算大問題;但至少要有「字眼表在哪一個測試裡釘住」。

佐證行 file: `scripts/lumos:25496`
佐證行 file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:19`

**R2A10 行模式的 `--top` 預設值跟現有 `--top` 的語意相反**
severity: minor
blocking: 否——同一個旗標在兩種模式下預設不同,但沒有靜默截斷(截掉的行數印 stderr)。
引句:「改用 `--top` 限總行數(行模式預設 80 行,`--top 0` 全給)」
- 現有 `--top` 的 help 是「相關性排序輸出上限(0=全量,預設;圖譜先行不靜默截斷)」(`scripts/lumos:40184`)。
- 行模式預設 80,是同一旗標兩種預設。截掉印 stderr 算有告知,但「圖譜先行不靜默截斷」的原則是預設全量。
- 若要保留 80,建議在 help 和 `search` 的 docstring 講明行模式例外;或改成行模式也預設 0,由 agent 自己帶 `--top`。

佐證行 file: `scripts/lumos:40184`
佐證行 file: `scripts/lumos:3769`

**R2A11 搜尋新旗標的命名和職責,跟既有的 `--path`、`--include-superseded`、「結構化查詢走 query」不一致**
severity: minor
blocking: 否——Enzo 已裁定擴 `search`(已裁第 3 條),這裡只標命名和文件職責。
引句:「- `--prefix WHY,RULE,…`:只要這幾種摘要行。」
- `search` 的 `--path` 已經是「限資料夾前綴」(dest 叫 `path_prefix`)。新的 `--prefix` 指的是摘要行前綴,同一個詞指兩種東西,help 容易讀錯。
- `lumos-cli-read` 的 KEY 寫明 `search` 的職責是自由文字,「結構化查詢走 query(標籤家族 WHERE)/contracts/decisions/stale」。按前綴與按檔篩選比較接近結構化查詢。
- 新旗標 `--include-retired` 跟既有 `--include-superseded` 意思相近、名字不同。〈不收〉那段還拒絕過 `[retired:]`,詞彙又不一致。
- 建議至少把 `lumos-cli-read` 的 KEY 改成「search 現在多一個行模式」,避免兩篇說法打架。

佐證行 file: `scripts/lumos:40170`
佐證行 file: `scripts/lumos:40186`
佐證行 file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:34`

## 舊洞確認

- r1 的第二套數量語法、取代鏈第三套、設定預設 off 加 init 寫入、撤除條件欄位家族(`retire-when-*`)四處,r2 已確實撤掉,改接 HTML 註解標記、`[status:superseded]`、`REVISIT:[when-*]`。
- r1 的落點錯置(新行規則寫進存量漂移守衛)大部分補上,只剩 S4 一條(R2A2)。
- 我沒找到計劃把改檔前提示 hook 當擋點的殘留。`scripts/hooks/claude/impact-hook.py:103` 的 `_is_excluded_path` 仍排除筆記,計劃也沒動它。

不對齊共 11 條,其中 major 2 條
