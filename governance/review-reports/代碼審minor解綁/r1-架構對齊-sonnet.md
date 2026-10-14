severity: major

三問都有不對齊,共 4 條,其中 2 條 major。下面先逐問答,再列每條 finding。

## 問 1:數量檢查放進處置閘,合不合乎它的結構

**不合。** 處置閘第 ② 步是只讀帳列的輪級重算,不開檔。第 ③ 步才開報告檔,走共用的 `_prov_check` 驗 sha(file: `scripts/lumos:27155`、`scripts/lumos:27170-27190`、`scripts/lumos:26776-26786`)。要讀報告檔的步驟(條款、資安、落點、回顧)各自是獨立的 `_disposal_*_step`(file: `scripts/lumos:26843`、`scripts/lumos:26929`、`scripts/lumos:26990`、`scripts/lumos:15041`)。設計卻把「去掉檔級行、數 minor 與 clean 宣告行、(auditor, report_sha256) 去重」塞進 ② 的 elif 鏈,和 ③ 的留痕重驗重複,又在 ③ 驗 sha 之前先讀報告。

「報告內宣告了幾條」這件事,現有的做法是寫側 `rec["reported"] = _report_reported_count(...)` 進帳(file: `scripts/lumos:10998`)。讀側由 `_review_yield_round` 以 `(auditor, report_sha256)` 去重加總(file: `scripts/lumos:10258-10272`)。設計給的「載體不一定最後記所以只能在閘讀報告」不成立:各席那一列可以各自帶自己的 minor 與 clean 數,閘再用同一套去重加總。

## 問 2:降級清單是不是第二套 refuted-set

**是,而且兩處重疊。**
- 辯方用證據降級,現有的記法是 `--refute-verdict <id>=evidence`。它要求降到 minor 或 clean 並附 file:line,去向是放行(file: `skills/lumos-design-loop/templates.md:447`、`skills/lumos-code-loop/SKILL.md:45`)。設計另開 `--downgraded-set` 記同一件事,並讓它進閘的分母,等於同一事實兩處記。
- `--downgraded-set` 要「比照」的 `--refuted-set` 檢查,現在是 `cmd_canary` 裡內嵌的一段,沒有共用函式(file: `scripts/lumos:10786-10817`)。照字面做就是再抄一份。
- 兩者語意相反:refuted 的 id 不得在 findings-set(file: `scripts/lumos:10799-10800`),downgraded 的 id 必須在。這一點只能共用「id=理由」解析與 intake 整字比對,不能整段共用。

## 問 3:判準與手冊落點

**手冊拆分對,判準落點錯。**
- 手冊拆分對:SKILL.md 第 7 步放規則一句,reference.md 放細節,和現有分工一致(file: `skills/lumos-code-loop/SKILL.md:54`、`skills/lumos-code-loop/reference.md:178`)。
- 判準落點錯:〈編排者判讀規則〉的標題註明「prompt 之外、skill 正文用」(file: `skills/lumos-design-loop/templates.md:296`)。席看不到它,§3 派工詞「指向」它也傳不到席。各席的嚴重度錨本來寫在 §7.x 席節(file: `skills/lumos-design-loop/templates.md:359-363`、`skills/lumos-design-loop/templates.md:436-441`)。代碼審的 major 定義已在 SKILL.md:45。

## Findings

引句:「同輪各席最新一筆帳(跟處置閘取 `latest` 同一套,含載體自己)的報告,用 `_report_severities` 去掉檔級那行後,數 minor 與 clean 的宣告行;同一席同一份報告只算一次」
severity: major
blocking: 是
照字面,處置閘第 ② 步會自己開報告檔、重解析並去重,等於為「宣告了幾條」開了第二套來源:現有的是寫側進帳的 `reported`,加讀側 `_review_yield_round` 的去重。報告在 ③ 驗 sha 之前就被讀。報告讀不到時,設計又要靠 ③ 判不過,同一個失敗有兩處負責。證據見上文問 1。
應該是:各席列各自帶 minor 與 clean 數、讀側沿用 `_review_yield_round` 去重加總;或做成獨立的 `_disposal_*_step` 並共用 `_prov_check`。

引句:「辯方附證據把某條原報 major 的發現降成 minor 時記。比照既有 `--refuted-set` 的檢查」
severity: major
blocking: 是
這是引入第二種做法:辯方證據降級已有 `--refute-verdict evidence` 記帳。設計再開 `--downgraded-set`,而且讓它改變判閘分母,而 `--refute-verdict` 目前明定是「純記帳不改判閘」。應該是複用 `--refute-verdict` 的 evidence 記錄當降級偏移,或明寫為什麼不能複用。

引句:「每個 id 要在 `findings_set` 裡、逐條嚴重度要標 minor 或 clean、理由至少 4 字含實字、要帶 `--intake` 且 id 在收貨紀錄的重現表同一列出現(整字比對)」
severity: minor
blocking: 否
「比照」refuted-set 但沒說抽出共用函式。現有檢查內嵌在 `cmd_canary`,照字面會複製一份;而且兩者的「id 是否在 findings-set」方向相反。結構方向對,落點不夠明確。應該是計劃寫明抽共用的 id=理由解析與 intake 整字比對 helper。

引句:「`skills/lumos-design-loop/templates.md`〈編排者判讀規則〉的 severity 錨補一段代碼審適用的判準,§3 派工詞的嚴重度一句指向它」
severity: minor
blocking: 否
判準放在席讀不到的編排者節,席的派工詞指過去也看不到。落點應該放進席讀得到的 §3 或 §7.x 文字,或放 SKILL.md:45 代碼審 severity 句的旁邊;編排者節只留判讀用的一句指針。

不對齊共 4 條,其中 major 2 條。
