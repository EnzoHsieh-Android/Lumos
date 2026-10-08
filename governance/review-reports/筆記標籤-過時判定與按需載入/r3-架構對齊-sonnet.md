severity: major

對照基準是 `scripts/lumos`,範本是 `scripts/templates/note-audit-judge.md`。以下依四問作答。

## 1. 分層與依賴方向

- **筆記內容審**:判定者流程是 prepare 出清單、派工、record 收報告、check 查涵蓋,新行抽取來自筆記內容閘的共用函式。計劃讓這條流程多判一層前綴,沒有跨層直呼。
  - 對照:`scripts/lumos:26600`(prepare)、`scripts/lumos:26659`(record)、`scripts/lumos:26767`(check)。
- **結構性提醒**:放進筆記形狀檢查,走 `hints` 參數接在 `_note_shape_eval` 後面。方向跟否定現況句提醒一致,也沒有跨層直呼。
  - 對照:`scripts/lumos:25835`(讀開關)、`scripts/lumos:25841`(eval)、`scripts/lumos:25846`(印出)。
- **`search --about`**:`cmd_search` 目前只收 `env`,是純讀 vault 的層。算「那支檔的家」要用 repo 根(`_vault_repo_root`,`scripts/lumos:8099`)和檔路徑對照,計劃沒寫這個依賴從哪來(R3A6)。
- **W4**:筆記形狀檢查直接呼叫 `rule_lifecycle_warnings`,方向對。但同一個函式已經被 lint 那條路徑呼叫,等於兩條路徑共用一個產生器(R3A5)。

## 2. 命名與錯誤處理

- **開關**:`note_shape.tag_hints` 取 warn/off、壞值照 warn 並講一句、`note_shape.gate` 是 off 時提醒也不出。這三點都跟 `note_shape.negation` 一致。
  - 對照:`scripts/lumos:25537`(解析)、`scripts/lumos:25818`(gate 為 off 時提前返回)。
- **失敗處理(R3A4)**:否定現況句提醒有「例外全吞、只印一句、不改回傳碼」和 `hinted` 帳。計劃對 H1/H2/H3/W4 沒寫這兩件事。
- **doctor 提示(R3A8)**:既有的閘被關成 off 時,doctor 會講一句。計劃沒有 `tag_hints` 的對應句。
- **搜尋旗標命名(R3A7)**:`--include-retired` 與既有 `--include-superseded` 並列,同一件事兩個詞。
- **`--top` 語意(R3A7)**:既有 `--top` 限的是篇數,計劃讓它在行模式限行數。

## 3. 第二種做法

- **逐行片段格式(R3A1)**:計劃宣稱「沿用」,實際上既有格式會把每行截成 90 字,檢查清單要看的欄位會被截掉。
- **前綴欄位(R3A2)**:既有紀錄是「每個內容編號一列、一個類別」,計劃要「先拆成單類句子再判」,兩邊對不起來。
- **H1 的判法(R3A3)**:另寫了一條「除了連結沒有別的字」的判斷,既有已經有 `_NS_POINTER_ONLY_RE`,而且既有把這種行當作合法指路行放過。
- **改檔前取行(R3A6)**:這條路徑是 `search --about`,既有的是 `impact --file` 與 impact-hook。

## 4. 落點

三篇大方向合理:
- 判定者多判一層前綴,寫進筆記內容審。
- H1/H2/H3/W4 與 `tag_hints`,寫進筆記內容閘。
- 搜尋行模式,寫進 lumos-cli-read。

沒說清楚的缺口列在 R3A9。

## Findings

**R3A1**
severity: major
blocking: 是——照字面「沿用既有逐行片段格式」實作,每行會被截成 90 字,檢查清單要讀的欄位會被截掉,清單做不出來。
引句:「輸出沿用既有逐行片段格式,每行帶篇名;`--json` 在行模式多一個片段文字欄位。」
- 對照:`scripts/lumos:4003-4008`(逐行片段輸出)。命中行用 `hits[:8]` 截行數,每行 `disp = s if len(s) <= 90 else s[:90] + "…"`。
- 影響:RULE 的 `[retire:…]`、`[confirmed:…]`,PITFALL 的 `[test:…]` 常落在 90 字之後。清單要判的正是這些。
- 計劃只寫了「不套每篇 8 行截斷」,沒寫不套 90 字截斷。`--json` 的「片段文字欄位」只在 JSON 才給全文,人看的輸出沒有。

**R3A2**
severity: major
blocking: 是——紀錄是「每個內容編號一列、一個類別」,多一欄前綴撐不起「先拆成單類句子再判」,也沒寫多席或申訴不同意時前綴怎麼合併、提醒印在哪個指令。
引句:「**紀錄格式**:每行判定多一欄前綴;舊格式的紀錄照讀(那一欄空著)。」
- 對照:`scripts/lumos:26475-26486`,`_note_audit_parse_report` 一列只有編號、類別、證據、理由四格。
- 對照:`scripts/lumos:26733`,`keep.append({"id","class","evidence","reason","evidence_ok"})`,一個 id 一個結果。
- 對照:`scripts/lumos:26229`,`_note_audit_fold` 按 `_NOTE_AUDIT_WEIGHT`(`scripts/lumos:25921`)取最重的類別。
- 對照:`scripts/templates/note-audit-judge.md` 規則 5(整句跨多行時整句同一標籤)、規則 7(同一編號只給一個標籤)。
- 計劃要判定者「先把混合句拆成單類句子再判」。拆出的子句沒有內容編號,一列只能放一個前綴,混合行的 WHY 和 PITFALL 沒地方分開記。
- 前綴不是 CODE/MIXED/CONTEXT 的輕重關係,`fold` 的「取最重」套不上去。兩席判不同前綴、申訴推翻前綴時怎麼合併,計劃沒寫。
- 「出口只提醒:列出來讓人改」沒寫在哪個指令印。record 的「還沒被涵蓋」清單(`scripts/lumos:26750`)只看類別,不看前綴。

**R3A3**
severity: minor
blocking: 否——命名與判法跟既有不一致,但結構是對的,不會做錯。
引句:「新寫的 DEP 行除了 `[[連結]]` 沒有別的字 → 提醒「這是相關筆記,寫進 related,不是外部依賴」」
- 對照:`scripts/lumos:25264`,`_NS_POINTER_ONLY_RE` 已經是「只放連結與連接詞的指路行」的單一判法。
- 對照:`scripts/lumos:25315`,`skip = ... m.group(1) in ("FLOW","DEP") and _NS_POINTER_ONLY_RE.match(body)`。既有把這種行當合法指路行放過,H1 要提醒的正是同一批行,方向相反。
- 計劃應寫明是反轉該豁免的理由,並重用 `_NS_POINTER_ONLY_RE`,不要另寫一條「只有連結」的判斷。

**R3A4**
severity: minor
blocking: 否——缺的是跟否定現況句提醒一致的防護與帳,不是結構錯誤。
引句:「提醒全部印出、不設上限(同否定現況句提醒),但同一次提交同一條規則超過 10 行時只印前 10 行加總數。」
- 同一句前半「不設上限」、後半「超過 10 行只印前 10 行」互相矛盾。
- 對照:`scripts/lumos:25513-25516`,否定現況句提醒是「全部印出,不設上限」。要上限就不能說「同否定現況句提醒」。
- 對照:`scripts/lumos:25842-25860`,既有提醒「提醒失敗不能讓閘失敗」:讀設定、判定、印出、記 `hinted` 帳全包在 try 裡。
- 計劃對 H1/H2/H3/W4/已作廢擴大沒寫失敗隔離、沒寫是否記治理帳、帳的 `check` 欄位叫什麼。

**R3A5**
severity: minor
blocking: 否——是提醒路徑重複,不會讓功能做錯。
引句:「沿用既有 `rule_lifecycle_warnings` 判(不另寫),印缺 since、retire 與 until 過期」
- 對照:`scripts/lumos:3371-3372`,`context_marker_warnings` 只在 `rules is None` 時才跑 RULE 生命週期。
- 對照:`scripts/lumos:5389`,lint 已經呼叫它;`scripts/hooks/pre-commit:200-204`,lint rc 為 0 時輸出被丟掉。
- 對照:`scripts/lumos:25317`,筆記形狀檢查傳 `_NOTE_SHAPE_PREFIX_RULES`,刻意不含 RULE。
- 計劃的 W4 是同一個函式的第二個消費者,而且只看新行。S4「tag_hints 是 off 時 W4 不出現」只管得到筆記形狀檢查這條路徑,管不到 lint 那條。
- 改寫 superseded 訊息(`scripts/lumos:3353`)會同時改到 lint 和 W4 兩條路徑。計劃應寫明 lint 路徑保留、W4 與它的分工。

**R3A6**
severity: minor
blocking: 否——是入口分叉與缺依賴說明,結構可以救。⚠ 我判不準它算不算第二種做法。
引句:「`--about <檔>`:那支檔的家筆記(用既有「每支檔有家」的對照算,不是所有 about_code 列了它的筆記)的摘要行。」
- 對照:`scripts/lumos:3769`,`cmd_search(env, term, ...)` 只收 env;`scripts/lumos:24010`,`_home_map_from_notes`。
- 對照:`scripts/lumos:34642-34657`,`impact --file` 已經回傳 `home: True` 的家節點並加 ★家★。CLAUDE.md 的「改這支檔會牽連什麼」入口也是 impact。
- 「改某支檔前取行」於是有兩個入口:impact(家)與 `search --about`(家的某幾類行)。
- 計劃沒寫 repo 根、檔路徑正規化(repo 相對 vs vault 相對)從哪來,`cmd_search` 目前沒有這些。

**R3A7**
severity: minor
blocking: 否——命名不一致,功能可行。
引句:「行模式預設隱藏帶 `[status:superseded]` 的行,`--include-retired` 才給」
- 對照:`scripts/lumos:40186`,既有 `--include-superseded`;`scripts/lumos:4013`,既有提示字樣「作廢結果」。
- 同一概念出現「作廢」(`--include-superseded`)與「retired」(`--include-retired`)兩個詞。`hidden_lines` 並列 `hidden_superseded`,也是兩個詞。
- 對照:`scripts/lumos:40181`,既有 `--top` 是「相關性排序輸出上限」的篇數;計劃讓它在行模式變成「總行數」。同一旗標換單位。
- `--prefix` 與現有 `--path`(內部變數 `path_prefix`,`scripts/lumos:40168`)詞根相近、意思不同。計劃已說 help 寫明,這條只記錄。
- 「只看靜態標記」若是對整行字面比對,筆記裡講解 `[status:superseded]` 的活行(如 lumos-cli-read 的 RULE 說明)會被誤藏。判法應用 `parse_rule_fields`(`scripts/lumos:3282`),不要字面比對。

**R3A8**
severity: minor
blocking: 否——是跟既有閘的對照缺一項,不影響功能。
引句:「**自我治理(誤擋的逃生口)**:本案不新增任何擋;提醒用 `note_shape.tag_hints: off` 關掉。」
- 對照:`scripts/lumos:25582-25591`,否定現況句提醒被關成 off 時,doctor 會講一句;`scripts/lumos:1295-1303`,node_home.gate 被關成 warn/off 時開頭就講。慣例是「關掉要看得見」。
- 計劃的 doctor 只加過期 RULE 清單,沒有 `tag_hints=off` 或壞值的那一句。

**R3A9**
severity: minor
blocking: 否——落點方向對,但改到的檔沒有對應的家。⚠ 我判不準範本與 skill 檔是否算「每支檔有家」的對象。
引句:「規格的單一來源寫在 lumos-project-notes skill 的「寫回圖譜」子檔;紀律範本只加一行指路(範本已超過瘦身基線)。」
- 對照:`docs/lumos-toolchain-knowledge/Systems/診斷迴圈先行.md`、`check-r-guard.md`、`slim-install-安裝器.md` 的 `about_code` 都列了 `scripts/templates/graph-discipline.md`。計劃第 0、1 步要改這支範本,這三篇不在 `lands_in` 裡。
- `skills/lumos-project-notes/commands/03-寫回圖譜.md` 沒有任何 Systems 節點把它列進 `about_code`。
- doctor 過期 RULE 清單、W4 訊息改寫分別落在 lumos-cli-read 與筆記內容閘,計劃沒有逐項對應。`lands_in` 只列篇名,沒寫各部分落哪篇。

不對齊共 9 條,其中 major 2 條
