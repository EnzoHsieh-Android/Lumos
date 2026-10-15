severity: major

這是 r2 修訂稿的通才審查。我開了 `scripts/lumos`、`templates.md`、兩份 skill 說明、`06-代碼審與推送.md`、三支測試與圖譜節點逐一核對。機械 refcheck 已驗存在性,下面都是語意問題。

## 固定席:圖譜鏡頭

- `Systems/pitfalls-code-loop`(d6、KEY 行)與 `Systems/bound-tests-gate`:**不影響**。
  - 資安席必派、`required-gated`、處置閘那一步都沒動。
  - spec 明寫「不 supersede d6」,`_TIER_ROSTER` 的 `資安` 席名也不改。
- 審查席唯讀隔離合約(`t_seat_templates_carry_marker`):**不影響**。
  - 只在圍欄第二行加字,第一行 `LUMOS-SEAT:` 不動。
  - `t_templates_security_seat_section` 用 `split("\n## ")` 切段,`###` 小節不會截斷 §7.8,spec 這點說對了。
- 本節點 `Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃` 就是 spec 本身,凍結版沒有另附固定席。

## 逐節結果

「裁定來源」「不改的部分與理由」「不做」「承認的限制」「回退」已讀,無 finding。S3 至 S8 也無 finding。S1 和 S10 有問題,見下。

---

severity: major
blocking: 是 — ②類裡「本機路徑寫進公開卷證」這條,跟 repo 現況和審查流程自己的產出直接矛盾。照寫的話,每輪資安席都會對本流程自己的產出報洞。
引句:「密鑰、使用者信箱或本機路徑寫進會公開的 repo、帳本或卷證」
段落:〈新規則〉第 1 點 ②。
問題:
- 本 repo 公開,已提交的卷證幾乎全帶本機絕對路徑。`git grep -l "/Users/enzo"` 命中 1311 個檔,其中 `governance/` 底下 1308 個。信箱 `8yinpro` 也在 12 個已提交檔案裡。
- 派工範本本身要求席位寫 `file: \`路徑:行號\`` 佐證。`repo 在 {repo 根}` 這行也會填絕對路徑。
- 所以新規則寫成「看到本機路徑進卷證就報」,每輪高風險代碼審都會報自己的卷證。這跟本案「少追沒意義的洞」的目的相反,也沒有任何一段說明這條要怎麼收斂。
建議:限定成「新進程式、範本、公開文件的路徑與信箱」,明寫卷證的 `file:` 佐證與派工單路徑是既有慣例、不報。或者另開決策處理已提交的存量。
佐證:`file: \`governance/review-reports/Claude-mod第二批/r1-整合知識同步-sonnet.md:3\``(絕對路徑已在卷證裡)。`file: \`skills/lumos-design-loop/templates.md:141-146\``(§3 派工詞)。

---

severity: minor
blocking: 否 — 只影響其中一個測試子句怎麼構造,不會做出壞系統。
引句:「兩份輸出拿掉那一行之後完全相同;編制表算不出來」
段落:〈做法〉5 的「位置」、〈驗收條款〉S1。
問題:
- spec 要求編號是 `code-` 開頭,且編制表算不出來時那一行也照印。這兩個條件同時成立是不可達的。
- `_roster_kind("code-…")` 恆回 `"code"`。`_TIER_ROSTER` 的 `("code", light/standard/high)` 三組都有定義,`legacy` 另走單席分支。
- 「目前算不出該派誰」只會出現在 `code` 開頭但沒連字號的編號(`_roster_kind` 回 None)。那種編號又被 S2 明定不印。
- 結果是 S1 最後一個子句,在不 monkeypatch `_TIER_ROSTER` 的前提下不可驗,spec 也沒說要 patch。
佐證:`file: \`scripts/lumos:14035-14042\``、`file: \`scripts/lumos:14011-14033\``、`file: \`scripts/lumos:14350-14360\``。

---

severity: minor
blocking: 否 — 純文件不一致,但會讓實作者不知道該信哪邊。
引句:「保留的兩問照原圍欄字面(重跑、對外重試),拿掉的兩問與 d2 相同;共用圍欄一字不改」
段落:frontmatter d3、〈新規則〉3、〈做法〉10、〈現況〉表第 76 行。
問題:
1. 兩處還寫「(d2)」或「落實 d2」,但 d2 已 `valid: false` 且被 d3 取代。新規則 3 的標題帶「(d2)」。做法 10 標題寫「(落實 d2,新規則 3)」。
2. d3 說保留的兩問「照原圍欄字面」,做法 10 給的替換句卻是改寫版:「同一操作重跑會不會重複寫入;對外送出或扣款的重試會不會送兩次」。
   - 原圍欄是「…會壞嗎?…對外送出或扣款的重試會不會重複生效、收端怎麼去重?」。
   - 替換句丟了「收端怎麼去重」,也換了措辭。
3. d3 說「共用圍欄一字不改」,可是做法 9 要改 §3 圍欄第二行。意思大概是只指第 1 點,但字面互相打架。
佐證:`file: \`skills/lumos-design-loop/templates.md:141-160\``(§3 圍欄第 1 點原文)。

---

severity: minor
blocking: 否 — 漏掉的只是文件同步點,測試守衛也會漏。
引句:「步驟 2 列席位處,以及另外三處抄了」
段落:〈做法〉4。
問題:
- spec 說 `reference.md` 是「步驟 2 列席位處」加「另外三處」,共四處。實際至少五處:
  - 第 74 行:refute framing 的「冪等併發:重跑/同時進來/同次計算讀兩次」。
  - 第 256 行:「鏡頭各異…冪等併發」。
  - 第 293 行:「鏡頭各異(bug/資源例外/冪等併發/…)」。
  - 第 420 行:另一份 framing 的「冪等併發 重跑或同時進來會壞嗎」。
  - 第 587 行:步驟 2 的「併發與資源」。
- 第 255 行和第 507 行是已停用 canary 協議的舊段落,另需決定算不算。
- S6 寫「每一處」,但做法 4 的計數是錯的。實作者照「三處」做會漏,`t_toolchain_lens_scope_doc_sync` 若照 spec 的清單逐處切也會漏。
佐證:`file: \`skills/lumos-code-loop/reference.md:74\``、`file: \`skills/lumos-code-loop/reference.md:256\``、`file: \`skills/lumos-code-loop/reference.md:293\``、`file: \`skills/lumos-code-loop/reference.md:420\``、`file: \`skills/lumos-code-loop/reference.md:587\``。

---

severity: minor
blocking: 否 — 範圍外只是少了一些守衛。
引句:「工具鏈本 repo 沒有這些面):登入與權限、加密與傳輸、行動端」
段落:〈新規則〉1「接受不看」、做法 1 的 `trade_offs`。
問題:
- 「沒有加密與傳輸這個面」的宣稱查證為假。
  - 工具鏈靠 `curl -fsSL https://raw.githubusercontent.com/... | bash`(`get.sh`、`get.ps1`)分發,內含 `git clone "$LUMOS_URL"`,網址可被環境變數覆蓋。
  - `_http_get_text` 也用 `urllib` 對外取檔。
- d6 的 context 自己就寫「README 教一行 curl|bash 安裝」是攻擊面來源,本案「不 supersede d6」。
- 使用者裁的三類是範圍,這個我不重審。但理由應改寫成「使用者裁定不審」,或把安裝腳本的下載與憑證驗證併進 ②。現在寫的「沒有這些面」會在 RULE、決策的 `trade_offs` 裡留下一句假的事實。
佐證:`file: \`get.sh:3\``、`file: \`get.sh:95\``、`file: \`scripts/lumos:31660-31663\``、`file: \`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:109\``。

---

severity: minor
blocking: 否 — 只會讓資安席在 ③類「推論封頂」。
引句:「③非刻意、一步就能繞過的守衛:照平常操作一個指令或一次編輯就意外走過去」
段落:〈新規則〉1 ③ 與〈做法〉2「圍欄內只動這三處」。
問題:
- 圍欄其餘部分逐字不變,仍是「你是資安審查員,站在攻擊者那一邊」。每條發現必附「誰/從哪/送什麼/拿到什麼」四件,缺任一件就標「推論」,severity 最多 minor。
- ③類的主角是「按一次 Ctrl-C、檔名帶空白、新分支首推」的使用者本人,沒有攻擊者。照原文填四件,不是填不出就是硬湊。
- 結果 ③類發現幾乎都被封頂在 minor。處置閘「major 一律折」又不會被觸發,等於 ③類在範圍內卻擋不到事。
- spec 沒說 ③類的四件要怎麼對應,或是否豁免。
佐證:`file: \`skills/lumos-design-loop/templates.md:419-445\``(§7.8 圍欄)。

---

severity: minor
blocking: 否 — 覆蓋面不完整,不會壞系統。
引句:「每一份第一行是 `LUMOS-SEAT:` 的派工詞圍欄」
段落:〈做法〉9、S9。
問題:
- 使用者的裁定是「所有子代理派工詞都要原文寫進這句」,理由是無人看顧的子代理會被刪除保險絲卡住。spec 只覆蓋第一行是 `LUMOS-SEAT:` 的六份圍欄,以下派工都沒有這句:
  - §5 SDD implementer 和 §6 task reviewer(`templates.md:258-300`)。implementer 最可能自己清測試暫存。
  - `06-代碼審與推送.md:56` 和 `:89` 的「派判定者」。
  - Codex 子代理:§3 ④ 寫明選得中 `lumos_reviewer*` 時框架單源是 `_CODEX_AGENT_INSTRUCTIONS`,派工詞只給審材。圍欄第二行補的字傳不到它(`scripts/lumos:26484`)。
- spec 沒說這些是刻意不管,還是漏掉。
佐證:`file: \`skills/lumos-design-loop/templates.md:258\``、`file: \`skills/lumos-project-notes/commands/06-代碼審與推送.md:56\``、`file: \`scripts/lumos:26484\``。

---

severity: minor
blocking: 否 — 主要是文件寫法,但實作者可能放錯位置。
引句:「所以不在圍欄裡寫工具鏈的例外。圍欄之後的說明加一條」
段落:〈做法〉10、S10。
問題:
- §3 現有的編排者說明塊「### §3 編排者派工前須知(不貼進派工詞)」在圍欄之前(`templates.md:110-139`)。
- 圍欄之後緊接的是 `### §3.1 修訂輪的修補鏡頭(僅供 code-loop)`(第 206 行),是另一個主題。
- 「圍欄之後的說明」沒有現成對象。實作者很可能把這條放進前面那個自然的「須知」塊,而 S10 又寫「圍欄之後應有一條」,測試就會對不上。
- 建議明寫放在哪個小節的哪個位置,或改成「§3 圍欄之外、須知塊內」。

---

severity: minor
blocking: 否 — 指令照寫會跑不動,但內容可塞進 `--context`/`--why`。
引句:「四欄:context=上面三句原話;alternatives=①照舊(每輪被偽造類發現拖著加輪)」
段落:〈做法〉1。
問題:
- spec 要用 `lumos decision-add` 寫 `context`、`alternatives`、`why_chosen`、`trade_offs` 四欄。
- 實際 `decision-add` 只有 `--decided`、`--context`、`--why`,沒有 alternatives 和 trade_offs 的旗標。
- 其他計劃的巢狀 `alternatives_considered:` 是手寫進 frontmatter 的。鐵則 2 又說開頭欄位別手改。
- spec 自己的 d1 至 d3 也只有 context 和 why_chosen。
- 實作時要嘛違反鐵則、要嘛丟掉 alternatives 和 trade_offs。需要指定做法,或先給 `decision-add` 補旗標。
佐證:`file: \`scripts/lumos:57512-57517\``、`file: \`skills/lumos-project-notes/SKILL.md:84\``。

---

severity: minor
blocking: 否 — 現行文件已有「修正關卡只提醒不擋」,所以不致卡住迴圈。
引句:「這條路任何時候都走得通,所以不會卡住迴圈」
段落:〈新規則〉1「範圍外發現的處置」。
問題:
- 路徑本身可行,但「不會卡住」不等於「不加輪」。
  - SKILL 步驟 5 規定:修過之後「收斂前仍派全新席掃 delta 回歸」。
  - 同輪有任一席 major 時,範圍外的 minor 不能放行,只能折。於是要多改一個文件,再多一輪。這正是方案「①照舊(每輪被偽造類發現拖著加輪)」要避免的事。
- spec 沒要求記帳時帶 `--finding-kind`。沒帶的話 `_fix_needed` 會把所有折入發現都算成要修正紀錄,文件類折入也要寫測試。修正關卡目前只提醒不擋(`scripts/lumos:14646-14652`、`:14777`),但提醒會一直響。
- 建議在處置段補一句:範圍外折入記為 `--finding-kind id=spec`(或 `process`)。
佐證:`file: \`skills/lumos-code-loop/SKILL.md:49\``、`file: \`scripts/lumos:27976\``。

---

severity: minor
blocking: 否 — 工作方式說明缺漏,語意也有待釐清。
引句:「跨 repo 派工(會談開在 A、審 B 的分支)時 `loop next` 要帶 `--repo <被審 repo>`」
段落:〈新規則〉開頭、〈做法〉4、〈實務隱患〉版本錯位。
問題:
1. 新規則靠編排者帶 `--repo`,但做法 4 補進三份說明的句子,和 §7.8 填空的指示,都沒提這件事。`SKILL.md:28` 的 `loop next <編號> --tier … --orchestrator codex` 範例也沒有 `--repo`。這條規則沒有任何落地處,只在計劃筆記裡。
2. 在 `loop next` 裡 `--repo` 不只是「選範圍」。
   - 它是 `reviewed_spec` 路徑解析根(`scripts/lumos:16379-16391`)。
   - 也是 `_fix_check_status`、`_cap_hint_lines` 的 repo。
   - 把它指向「被審 repo B」,而帳本在 A,`帳上最後記到的審查材料` 會被解析到 B 底下,印成「★這個檔案現在不在了★」。
   - spec 把 `--repo` 當範圍選擇器,卻沒查這些副作用。
佐證:`file: \`scripts/lumos:16379\``、`file: \`skills/lumos-code-loop/SKILL.md:28\``。

---

severity: minor
blocking: 否 — 規則文字有洞,實際影響小。
引句:「規則講的是審查席看什麼,不是推送前要不要表態;表態題是另一道閘,要改另開」
段落:〈不改的部分與理由〉「風險分級與推送前的棧別檢核題」。
問題:
- 這段的理由只對「推送前表態題」成立。
- 但 §3 派工詞第 2 點會把 pitfalls manifest 發給審查席,要求逐條判「真隱患/誤報」,真隱患必答對應提問。manifest 的「併發」類題目照舊,例如「共享狀態有沒有鎖保護?」「寫入有沒有交易包裹?」(`scripts/lumos:30196-30197`)。
- 在工具鏈本 repo,只要 diff 碰到 `threading.`、`global x` 或 `INSERT`,審查席就被要求審「競態」,而新規則 2 說這類不審。
- spec 沒處理這條路徑,也沒說 manifest 的併發題在工具鏈本 repo 要不要略過。

---

severity: minor
blocking: 否 — 屬流程與管理,不影響功能。
引句:「9. **派工詞的刪檔紀律**(2026-10-14 使用者裁,所有專案都適用、不限工具鏈)」
段落:frontmatter `lands_in`、〈現況〉表、〈做法〉9、〈不做〉。
問題:
- 做法 9 的刪檔紀律跟「資安與資源鏡頭範圍」是兩件獨立的事,卻放在同一份計劃、同一次提交(含 §0、六份圍欄與 S9、一支新測試)。專案規則是「一個功能一個提交」。
- `lands_in` 只列 `Systems/pitfalls-code-loop`。但 `templates.md` 的家是 `Systems/design-loop`、`Systems/arch-alignment-lens`、`Systems/每輪修補差異派工`。§0 的單源是 `Projects/審查席唯讀隔離_計劃`。這些都沒進 `lands_in` 或 `related`。
- 改了 `templates.md`、`loop next` 卻只把說明寫進 `pitfalls-code-loop`,跟鐵則 5「說明寫進改到那支檔的家」不完全一致。
佐證:`file: \`skills/lumos-design-loop/templates.md:20\``。

---

## 實務隱患鏡頭

- **守衛面**:已有 finding。
  - 「漏報不誤擋」的論述成立。
  - 缺的是上面這幾條:②類路徑與信箱存量矛盾、③類四件規則衝突、manifest 併發題與新規則 2 的衝突。
- **注入**:無 finding。`loop next` 多印的是固定字串,範本新段落是常數,不讀外部輸入,spec 的論述成立。
- **併發與資源**:無。多一次 `is_file()`,`_vault_repo_root` 不開子程序,查證屬實。
- **版本錯位**:spec 論述成立(新範本配舊工具,是多審不是少審)。但跨 repo 的方向相反且靠 `--repo`,見 `--repo` 那條 finding。
- **刪檔與清理(使用者全域規則)**:有 finding,見刪檔紀律覆蓋面那條。
- **新舊互讀、遷移、金流、認證、個資、快取、限流**:無。本案不碰這些資料或程式,spec「已排除」各條的理由查證屬實。

最高等級 major,blocking 1 條。
