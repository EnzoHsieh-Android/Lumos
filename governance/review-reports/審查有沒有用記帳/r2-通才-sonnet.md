severity: blocker

# 審查有沒有用記帳 r2 — 通才複驗(對 r1 折入的 16 條逐一驗 + 新寫段落抓洞)

方法:讀 r2-snapshot.md 全文;對照 r1-intake.md 的 a1–a16 與其 HIT 證據;讀 `scripts/lumos` 現況(`_report_severities`/`_SEV_ORDER`/`cmd_canary` 寫側/`_loop_status_disposal`/`cmd_loop_escape`)確認 S1–S3 全部**尚未實作**(`--reported`/`--refuted-set`/`--self-found-set` 在 CLI 裡都查無);用今天真帳(`code-clause-bindings-b` r1,`docs/.canary-log.jsonl:1208-1210`)手算 S3 那一行;逐份開三個真實席報告驗證「檔序第一個宣告=檔級」在 Codex 格式(第一行是 HTML 註解)上站不站得住;對照 r1-snapshot.md 同段落文字,確認「雙向夾」是 r1 折入時新寫的用詞。

## 一、16 條折入逐一驗

**a1(自動數在真實格式上數到 0 → 改必填,解析只當下限守衛)—— 修好,但引入新洞(見 F1/F4)**。
引句:「★不從報告自動數★(r1 五席:標題內嵌、`- [major]` 列表、驗收輪留舊項三種格式今天都在用,自動數會得 0」
用 Codex 席真報告驗算:`governance/review-reports/code-clause-bindings-b/r1-外家否決-codex.md` 第 1 行是 HTML 註解、第 2 行才是 `severity: major`(檔級),之後 findings 1–6 各自一行(第 20/26/32/38/44/50 行),扣掉檔級=6,與帳上 `findings: 6` 一致——HTML 註解不會被 `severity:` fullmatch 命中,不干擾「檔序第一個」判定,這個具體格式站得住。

**a2(報 8 存活 9 算術倒退 → self-found-set)—— 修好,但欄位本身無驗證(見 F1)**。
引句:「載體列再加 `--self-found-set`(選填,⊆ findings-set):編排者自己踩到、沒有任何一席報過的發現」

**a3(駁回清單可灌大、不驗 → 必帶+id對intake+理由)—— 修好,但 id 驗證強度不夠(見 F2)**。
引句:「有 `--findings-set` 就★必帶 `--refuted-set`★(跟 folded/accepted 同一種硬擋慣例),值 `none` 表示這輪 0 條駁回」

**a4(舊帳缺欄位只有「報」印 ?,其他四格偽裝成數字 → 五格各判)—— 修好,但缺「?」與算術檢查交互的規則(見 F3)**。
引句:「不拿散文 note 猜數字(Codex 席 blocker)」

**a5(選填=沒人填 → 必填)—— 修好**。
引句:「選填就是 refute_verdicts 0/1216 那條路」

**a6(`severity: resolved` 不在值域 → 不引入新值)—— 修好**。
引句:「★不要留 `severity:` 行★(嵌在標題或散文裡),不引入新值 `resolved`」

**a7(ci-wait 提醒是噪音 → 不加)—— 修好**。
引句:「★不在 `ci-wait` 紅燈訊息加提醒★:簡化席數了 ci 帳 12 次紅燈 0 次是審查漏網,加了就是噪音。」

**a8(逃逸帳無輪次 → 印「迴圈累計」)—— 修好**。實測 `docs/.escape-log.jsonl` 對 `code-clause-bindings-b` 0 筆,E=0 這個具體值算得出來。
引句:「逃逸帳沒有輪次欄位,E 是整條迴圈累計(簡化席)。」

**a9(「每輪一行」歧義 → 明寫「問閘的這一輪」)—— 修好**。
引句:「尾端(觀測,不進合取;凍結/回放模式照既有慣例不印觀測尾)印★問閘的這一輪★一行」

**a10(「駁回」會被讀成審查員錯 → 一律寫「編排者重現不到」)—— 修好**。
引句:「接手席:不知道流程的人會讀成審查員錯」

**a11(樣本太少也印總數 → K<5 提醒)—— 修好,但這句只在 gov --stats 段,單輪 `--disposal` 尾端沒有等價提醒(K=1 也照印,不算新洞,原設計就分兩層)**。
引句:「全庫 227 個迴圈 45% 兩週內沒新帳,舊帳永遠是 ?」

**a12(段內比率 Σ折/Σ報 → 段首第二句)—— 修好**。
引句:「段首固定兩句;讀側不印任何比率。」

**a13(--findings 仍被 light/gate 依賴 → 明寫不動)—— 修好,且我另外機讀碼驗證屬實**:`scripts/lumos:6876`(light K=1)與 `scripts/lumos:6954/6959`(gate G2)兩處都對 `findings` 欄位 fail-closed,S1 沒有動到這兩處。
引句:「`--findings` 既有語意與必填規則一律不動——`--light`/`--gate` 兩條舊閘仍 fail-closed 依賴它(通才席、簡化席各自核過)。」

**a14(design-loop 逃逸句位置 → 步驟 10 後獨立段)—— 修好**。
引句:「design-loop skill 步驟 10 之後補一段獨立散文(跟 code-loop skill 第 8 步後那段同款)」

**a15(兩本帳分段可行 → 照既有慣例)—— 修好**。
引句:「審查有沒有用(只算有 `reported` 的 K 輪,2026-09-09 起)」

**a16(回放模式觀測尾 → 凍結/回放不印)—— 修好**。
引句:「凍結/回放模式照既有慣例不印觀測尾」

## 二、新 finding(對修訂稿新寫段落逐句查)

### F1 —— severity: blocker,blocking: 是
判準:實務隱患段宣稱下限守衛是「雙向夾」,但 S1 本文自己說「解析只當下限守衛」,兩段自相矛盾,而且我能拿具體反例證明真的只有單向。
證據:對照 r1-snapshot.md 舊稿同段落(`governance/review-reports/審查有沒有用記帳/r1-snapshot.md:66`),舊稿寫的是「機器從席報告數,編排者改不了席報告」——那時真的是雙向(機器全權算,人改不了);r1 把 S1 從「自動數」改成「必填+下限守衛」後,這段被順手改寫成「①報幾條由必填+下限守衛雙向夾」,但下限守衛只擋「填得比宣告行數少」,不擋「填得比宣告行數多」。手算 S1 自己出的例子:一份報告全 `severity: clean`(檔級行本身不算非 clean 宣告,非 clean 宣告數=0)、`--reported 3`——0 不大於 3,不擋,寫側靜默放行一個灌水 3 倍的數字。這個灌高的 N 同時讓 S3 的「N+S < M+R → ⚠ 算術不通」檢查更不容易觸發(N 越大,不等式越不成立),也就是說同一個漏洞同時打穿 S1 自稱的「雙向夾」與 S3 的算術哨兵,直接反證實務隱患段自己寫的「沒有『把數字做好看就能過關』的誘因」。
file: `scripts/lumos:5296`(既有 --report 必附檢查,S1 掛在這條路徑上,不影響本 finding 的論證但確認觸發點)

### F2 —— severity: major,blocking: 否
判準:駁回 id 對 intake 只驗「子字串出現」,沒有詞界錨定,短 id 容易被無關文字巧合命中,削弱 a3 剛加的驗證。
證據:S2 原文只說「子字串」,沒有 `\b` 或「必須是列表項/表格欄」之類的錨定規則;intake 慣例的 id 是「字母+個位數字」(`i1`…`i9`、`a1`…`a16`),這類 2 字元序列在幾十行的中英夾雜散文裡巧合命中的機率不低(例如 `i1` 也會是 `hi10`、`半i1`這類詞的子字串)——驗證形同「只要 intake 夠長,幾乎任何猜的 id 都能通過」,而 S2 自己在別處要求「理由 ≥4 字含實字」,顯示設計者知道要防隨意字串,卻在 id 這關漏了同等強度的防線。
（S2 段落原文無法找到 ≥10 字且不含「」的乾淨子句直接佐證此句,故不引句,以下用 file 佐證改用行為推演)

### F3 —— severity: major,blocking: 是
判準:S3 沒有講清楚「N/S 因缺欄位印 ?」與「N+S < M+R 算術檢查」兩條規則疊在一起時怎麼判,這件事直接影響 `[test:t_gov_stats_review_yield]` 能不能寫成無歧義的測試。
證據:手算 `code-clause-bindings-b` r1 真帳(`docs/.canary-log.jsonl:1208-1210`,三席 `findings` 0/6/2,無 `reported`/`refuted_set`/`self_found_set` 任何欄位,carrier `findings_set` 9 筆、`folded_set` 9 筆、`accepted_set` 0 筆,時戳 `2026-09-08T19:18` 早於 S3 自訂的 2026-09-09 缺欄位分界)——這一輪照 S3 規則,N、S、R 三格必須印「?」,M=9、F=9、A=0 可印實數。此時 `N+S < M+R` 這條不等式左邊是兩個「?」,右邊是 9+?,規格沒說這種情況要跳過算術檢查、當作 0 算,還是直接不比——三種實作互不相容,而且日後(距 2026-09-09 只差一天)絕大多數迴圈在相當一段時間內都會落在這個「部分欄位缺」的狀態,不是稀有邊界。
引句:「N=該輪席位列 `reported` 加總;任何欄位缺(2026-09-09 前的帳)就★該格印」

### F4 —— severity: major,blocking: 否
判準:「檔序第一個宣告=檔級」這條新規則依賴「檔級行永遠是全篇第一個 `severity:` 宣告行」的排版慣例,但這個慣例只在收貨 SOP 的既有文字裡間接看得出來,S1 本文沒有明寫必須擺最前,也沒有機械檢查位置。
證據:實測今天三份真報告(架構對齊/單reviewer/外家否決-codex)都把檔級行放在檔案最前面,規則現在站得住,但這是「大家剛好都這樣寫」而不是「規格要求這樣寫」——`skills/lumos-design-loop/SKILL.md` 第 21 行只講「表頭型嚴重度補一行獨立 severity」,沒講插在哪裡;`skills/lumos-design-loop/templates.md` 第 145–147 行反而描述「最後一行總結 max severity」,如果有人把這句話理解成連機器讀的 `severity:` 行也該放最後,「檔序第一個」就會誤判成把某條真 finding 當檔級、少算一條。
file: `skills/lumos-design-loop/SKILL.md:21`、`skills/lumos-design-loop/templates.md:145`

### F5 —— severity: major,blocking: 否
判準:S1 的必填規則掛在「有 `--report` 的席位列」上,而 `--report` 現在已經是所有 `loop+auditor` 帳列的既有硬性要求(不分 light/gate/panel/disposal),但 S4 明寫只改 design-loop 與 code-loop 兩個 skill 的範本,沒提到 light/gate 這條路常用的「原語」文件也要同步更新。
證據:`scripts/lumos:5296-5297` 顯示「審查席記帳(帶 --loop/--auditor)一定要附 --report」是無條件的既有規則,不分迴圈型態;`skills/lumos-project-notes/reference.md:1274` 目前仍教「`lumos canary record caught|missed --loop … --severity … --findings … --auditor …`」這種不含 `--report` 的舊式寫法(已經跟今天的碼不符,S1 上線後同一份文件教出來的指令會多一層 rc2)。S4 只講「兩個 skill 的 record 範本加 --reported」,沒有把這份仍在教舊寫法的文件納入更新範圍。
引句:「兩個 skill 的 record 範本加 `--reported`、`--refuted-set`、`--self-found-set`」

### F6 —— severity: major,blocking: 否
判準:S4 新加的兩條 REVISIT 裡,至少一半缺乏可直接執行的指令,尤其「算術不通出現的輪數」目前沒有任何彙總管道,只能逐迴圈手動跑 `--disposal` 再人工算次數。
證據:`--disposal` 的算術檢查是**單輪查詢時當場印**,`gov --stats` 新段列出的是 K/Σ報/Σ自找/Σ存活/Σ重現不到/Σ折/Σ放行/逃逸筆數,清單裡沒有「⚠ 算術不通出現次數」這一項,要拿到這個數字得先枚舉全庫所有迴圈編號、逐一跑 `--disposal`、自己數印出幾次警告——沒有一條指令能直接給答案。2026-10-08 那條(抽 20 份人工對「填的 reported」與報告自數)本質上是人工核對,格式上合格,但同樣沒有一條輔助指令(例如比對 `--reported` 與 `_report_severities` 差值的小工具)降低人工量。
引句:「量兩件事——有 findings-set 的輪裡 refuted-set 非 none 的比例」

## 三、S5 範圍刀

沒發現新問題,S5 條列的五個「不做」與實作 diff 描述一致,留給實作時人看即可,凍結快照本身沒有可驗證的機械宣稱。

---

總結:最嚴重 severity=blocker(F1);新 finding 共 6 條(blocker 1、major 5),blocking:是 2 條(F1、F3)、blocking:否 4 條(F2、F4、F5、F6)。
