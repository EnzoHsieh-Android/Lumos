severity: blocker

## 標頭/summary(YAML frontmatter 三行 KEY)
已讀,無 finding——三行摘要與後方條款內容一致,沒有獨立宣稱需要查證。

## 緣起
已讀,無 finding——這節是背景動機敘述(治理日報、d5 排除理由、現況盤點),沒有機械可查證的程式碼假設;9 個消費專案派工單的統計數字屬外部資料,refcheck 已判無「路徑:行號」型宣稱。

## 人裁(三問三答)
已讀,無 finding。

## PRIOR-ART
已讀,無 finding——「借用既有處置閘加一步」的最小解定位與後面 [S2] 的實作方式一致。

## 條款 [S1] 編制表加資安席
已讀,無 finding——`_TIER_ROSTER[("code","high")]` 目前確實是 8 席(5 佔 W+3 不佔 W:架構對齊/spec-conformance/外家否決),加一席「資安」（不佔 W、claude 家族、required）與既有 `_rseat` 資料形狀相容。

file: `scripts/lumos:7624-7632` 現況核對:`("code","high")` roster 8 席,与 [S1] 描述的「加一席」基準一致。

## 條款 [S2] 處置閘加資安席步驟

**B1**
severity: blocker
blocking: 是
判準:照這條字面實作,鏡頭比對規則會系統性誤擋已經做過真資安審查的迴圈,逼審查員要嘛被誤擋卡住、要嘛被迫用固定套語繞過,兩者都會讓「一律必派資安席」的機制在第一次真實使用就失靈。
引句:「誤擋:判定輪只派一席、生效日前開的迴圈、席名沒帶模型尾碼、Codex 編排;漏擋:席名亂取」
file: `scripts/lumos:7802-7805` 現有「外家席沒帶模型尾碼」的偵測,做法是 `_roster_family` 的**子字串**比對(`any(k in s for k in KEYS)`,大小寫不敏感),且只印「建議」不擋任何東西;[S2] 卻改用「取最後一個連字號前那段、整段相等」的**精確**比對來擋 `code-loop pass`,比對嚴格度反而比既有機制更硬,執行後果卻更重(exit 1 擋推)。
file: `docs/lumos-toolchain-knowledge/Projects/派工編制資料化_計劃.md:102` 本專案已經把「席名慣例 `<鏡頭>-<模型>` 是慣例非強制,野字串→unknown 列出不判定(不誤喊 external_missing 的前提=分類 fail-open)」寫成合約候選——這正是 2026-08-18 落地時的既有結論,[S2] 的精確比對規則與此結論直接衝突。
file: `docs/lumos-toolchain-knowledge/Projects/收斂閘殘餘估計降級_計劃.md:63` 同一專案 2026-08-14 另一次落地時再次明文:「`--auditor` 席名建議 `<鏡頭>-<模型>`...純慣例無機械檢查(明寫)」。
file: `docs/.canary-log.jsonl`(grep `架構對齊`/`arch`)結構完全相同的既有「架構對齊」席,實際帳面出現至少 9 種寫法:`arch`(純英文縮寫,沒有「架構對齊」四個字)、`arch-align-sonnet`、`arch-sonnet`、`arch-架構`、`arch-架構對齊`、`架構對齊`、`架構對齊-opus`、`架構對齊-sonnet`、`s4-resource-arch`(鏡頭段在最後,不在最前)。以「取最後一個連字號前那段、整段相等於資安」的規則去套,`s4-resource-arch` 這類「鏡頭在尾端」的真實寫法會被判不算,`外家codex-gpt-5.6-terra` 這類「模型名本身帶連字號」的真實命名習慣,套進「資安」情境會變成 `資安-gpt-5.6-terra` → 取最後一個連字號前段 = `資安-gpt-5.6` ≠ `資安`,同樣判不算——這兩種都是本專案帳面上真實出現過的命名形態,不是我掰的極端假設。
[S4] 只在〈承認的限制〉裡承認「席名可以亂取」是**漏擋**風險(遊戲規則、假冒),完全沒有討論**誤擋**風險(真做了資安審查、但沒有精確按 `<資安>-<模型>` 兩段式命名,就被判不算)——這是這份 spec 自己的守衛面小節裡沒看到的另一半。

**B2**
severity: minor
blocking: 否
判準:不影響能否實作,但〈實務隱患〉守衛面小節宣稱「誤擋…前者在 [S2][S3] 處理」過度樂觀——[S2] 的「沒有連字號就整個名字」規則只解決「完全沒帶模型尾碼」(如裸字 `資安`)這一種子情況,對 B1 舉的「鏡頭在尾端」「模型名本身帶連字號」兩類真實命名習慣沒有涵蓋,宣稱的覆蓋範圍比規則實際能擋的範圍大。
引句:「前者在 [S2][S3] 處理,後者寫在〈承認的限制〉附回頭條件」

## 條款 [S2] 續:同一迴圈記兩筆資安席 / 報告被搬走或改過
已讀,無 finding——[S2] 的判準是「至少一筆」存在性檢查,重複記兩筆資安席不會產生誤判(找到一筆合格的就算過);報告檔被搬走或 sha 改過會共用「留痕重驗」既有的 fail-closed 邏輯(讀不到/sha 不符→FAIL),此路已由既有機制覆蓋。

## 條款 [S2] 續:tier 判準與凍結/回放

**B3**
severity: major
blocking: 是
判準:若不修,實作者會照抄「帳裡任一筆 tier=high」這個語意,做出一個跟「tier 一旦定錨就不能中途換」的既有規格互相矛盾的閘,導致某些迴圈永遠卡在「閘要求資安席、但這個迴圈的既有派工/roster 路徑從未被允許長成 high 編制」的死局,除了開新編號沒有解法卻沒人講清楚。
引句:「帳裡任一筆 tier=high、迴圈首筆帳列時間 ≥ 生效日」
file: `scripts/lumos:8122-8125` `cmd_loop_next` 對 tier 是「定錨優先」語意:`anchor = next((r["tier"] for r in rounds if r.get("tier")), None)` 取**第一筆**帶 tier 的值,之後「分級第一筆定下就不能中途換——要換請開新的審查編號」是**寫死擋下**(`return 2`)。
file: `scripts/lumos:8176` 該 `eff_tier`(=anchor)直接餵給 `_roster_next_payload(loop_id, eff_tier)` 決定整個迴圈的 W 與編制表——也就是說一旦第一筆記錄定成 `standard`,這個迴圈終身走 1 席循序編制,永遠不會被派出「資安」這個只在 `("code","high")` 才存在的席。
file: `scripts/lumos:5629-5634` 但**寫入**帳本的 `cmd_canary_record`(`--tier` 參數)完全沒有做「跟既有 anchor 是否一致」的檢查,只驗證值合法(`tier not in LOOP_TIERS`)——代表操作者在第 3 輪 `canary record --tier high ...` 完全不會被擋下,帳面因此可以出現「round1 tier=standard、round3 tier=high」並存的真實資料形狀,和 `loop next` 的「anchor 恆定」假設不一致。
[S2] 用「帳裡任一筆」而非「anchor」去判斷是否要求資安席,等於把一個在**寫側沒有機械保證**成立的假設(tier 全帳一致)當成閘的判準;一旦出現上述並存情況,[S2] 判定要資安席,但這個迴圈從未真正被 `loop next` 派過 high 編制(沒有 W=5、沒有外家finder/否決、當然也沒有資安席位置),操作者除了整編號重開別無他法——這一點 spec 完全沒有討論。

## 條款 [S3] 生效日常數
已讀,無 finding——`_SECURITY_SEAT_SINCE = "2026-09-12T00:00:00+08:00"` 沿用 `_CLAUSE_GATE_SINCE`(`scripts/lumos:4388`)同一種「隔日不隔時」寫法,`_loop_ts_key`(`scripts/lumos:6625-6641`)用 UTC epoch 比較、時區安全,邊界用嚴格 `<` 與既有 `_disposal_clause_step`(`scripts/lumos:14850`)一致,不是本案新開的洞。

## 條款 [S4] 派工範本 §7.8
已讀,無 finding——看什麼/不報什麼/嚴重度錨的內容與 Anthropic claude-code-security-review、OWASP/MASVS 借用清單一致,§7.7 立場表現有「架構對齊 | (已有,見 §7.6) | 判不準標 ⚠ 交編排者」這種「不佔 W 席位改指別節」的先例(`skills/lumos-design-loop/templates.md:300`),資安席比照辦理格式上站得住。

## 條款 [S5] skill 同步

**B4**
severity: minor
blocking: 否
判準:不影響能不能實作,但照 [S5] 字面「以架構對齊出現的每一處為清單逐一對過」去掃,`docs/methodology/圖譜即合約.md` 這種不在 `skills/` 底下、也不在 [S5] 舉例名單裡的「單行機制總覽表」實務上容易被漏掉,之後有人拿它當代碼審對抗編制的權威說明會讀到過期內容。
引句:「(commands/06、code-loop reference.md、design-loop SKILL.md 等),列席位的地方都補上。」
file: `docs/methodology/圖譜即合約.md:150` 該表「代碼對抗審計 lumos-code-loop」列直接寫「對抗審(多席各鏡頭+架構對齊+外家 Codex finder/否決+辯方殺假陽性)」,是另一個「列席位的地方」,[S5] 舉例的三處都不包含它,而它跟 `commands/06`/`reference.md` 一樣都是靠人 grep 才會被巡到。

## 條款 [S6] 決策 d5→d6

**B5**
severity: minor
blocking: 否
判準:不影響能否實作,但下一個讀圖譜的 session 若照決策文字字面去命名新函式或印出訊息,會複製出跟 spec 自己立的規矩相反的稱呼,造成同一件事在圖譜與 spec 兩處講法對不上。
引句:「它對 code 迴圈恆 skip,所以功能不撞,但名字會撞」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:71` d6 決策的 `content` 欄寫「機械擋=處置閘第五條合取」——這正是 [S2] 明文★不叫「第五條」★要避開的名字(因為「第五步」已經是 2026-09-08 的條款綁定步驟);[S6] 用 `lumos decisions` 驗到 d6 valid、d5 superseded 都真(已跑指令核對),但 d6 內文本身踩到 spec 自己剛立的命名禁區。

## 邊界與不做
已讀,無 finding——不改風險掃描觸發、不改 standard/設計編制、不接 linter 進擋推鏈、不動 `code-loop pass` 介面,四條都沒有在條款裡被違反。

## 承認的限制
已於 [S2]/[S3] 段落隨對應條款一併處理(B1、B2、B3);其餘三條(席名可以亂取的漏擋面、`pass` 不回頭驗問閘、消費專案要 `lumos update`)都附了帶日期的 REVISIT,格式符合本專案「回頭條件要接電」的鐵則,已讀無額外 finding。

## 實務隱患

已讀,無 finding 的部分:併發(純讀、不新增寫入,同既有留痕重驗一樣的模式)、效能(幾十筆帳列量級,非熱路徑)、資源(既有讀檔函式,不開連線不拿鎖)、可逆性(純程式與文件改動,帳本不加欄位)、認證/個資/快取/遷移/限流/狀態同步(本案確實不改這些程式)。

金流與對外送出的「不適用」判斷已讀、成立:本案沒有新增任何對外呼叫路徑(Codex 子代理沿用既有派審機制,不是新開的外送管道),也沒有碰任何金流程式;「金流」在文中只是作為未來資安席要審的檔案形狀舉例出現,判斷理由本身站得住。

守衛面小節本身的「誤擋/漏擋」自我盤點,見 B1/B2/B3——已列出的誤擋項(判定輪只派一席、生效日前、席名沒帶模型尾碼、Codex 編排)是真的在 [S2][S3] 被處理到,但盤點本身不完整(遺漏「鏡頭段不在字串最前/最後」「模型名本身帶連字號」「tier 帳面不一致」這三類真實存在的失敗形態)。

## 驗收
已讀,無 finding——條列的 9 種情境涵蓋率本身合理,但其中「席名『資安』(沒帶模型尾碼)算」這條驗收案例只驗證了 B1 指出的問題裡最溫和的一種(完全不帶連字號),沒有一條驗收案例是「鏡頭段在尾端」或「模型名本身帶連字號」的形狀,驗收清單沒有測到 B1 描述的真實失效模式。

## 圖譜鏡頭(固定席節點逐條判)

- **[[Systems/pitfalls-code-loop]]**:不影響——本計劃是在既有的 `_loop_status_disposal` 上「加一步」(比照 2026-09-08 條款綁定的形狀),不改動既有四條合取(G3/處置集合/留痕重驗/quote-check)本身的判定邏輯,也不改 `pitfalls --diff` 的 tier 觸發規則(人裁明文不動);唯一的耦合點是 d5→d6 決策交接,已用 `lumos decisions` 核對成立。
- **[[Systems/hook信任邊界]]**:不影響——該節點的合約是「hook 執行 lumos 時只信任 `_trusted_lumos()` 解出的路徑,絕不執行被打開資料夾自己的 `scripts/lumos`」;本計劃完全不碰三支 hook(`lumos-entry-hook.py`/`check-graph-sync.py`/`impact-hook.py`)或 `_trusted_lumos()` 本身,只是把「hook 會不會執行不可信位置的檔」列進 [S4] 資安席**要審查未來 diff** 的清單裡,屬於被動引用而非修改。
- **[[Systems/arch-alignment-lens]]**:不影響——該節點的合約是「四個席位表各加一席架構對齊(required,不佔人數)」;[S1] 只在 `("code","high")` 這一個 roster 條目**新增**一個平行的「資安」席,不刪除、不修改既有「架構對齊」項的 family/occupies_w/requirement 三個欄位,`("code","high")` 原本 3 個不佔 W 的席位計數會變成 4,這會讓依賴精確計數的既有測試(如 `scripts/test_lumos.py:27731`)需要同步更新,但這已被 spec 自己的〈驗收〉一條「既有測試:...全綠」涵蓋,不算破壞該節點宣稱的行為。

## 總結
最嚴重 severity:blocker(B1)。blocking 共 2 條(B1、B3)。
