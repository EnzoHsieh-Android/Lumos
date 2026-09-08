severity: blocker

# r3 通才複驗——審查有沒有用記帳_計劃(上限輪,終審)

方法:讀 `r3-snapshot.md` 全文,對照 `r2-intake.md` 的 b1–b13 HIT 紀錄與五份 r2 席報告逐條驗折入;工作樹 `scripts/lumos` 對 HEAD 有一份尚未提交的 [S1]/[S2]/[S3] 實作(`git diff HEAD -- scripts/lumos` 可見 `_report_normalize_issues`/`_report_reported_count`/`_review_yield_round`/`cmd_canary` 的 `--refuted-set` 段),用 `SourceFileLoader` 原地載入這份 WIP 實作,對六份以上真實席報告(`code-batch20` 三份、`code-clause-bindings-b` 的架構對齊/外家否決/單reviewer 三種席位、外加 `code-clause-bindings`/`-b` 的驗收輪架構席)實際跑 `_report_normalize_issues`/`_report_reported_count`,而不是憑 spec 散文推演;另用真實 `docs/.canary-log.jsonl`(1208–1216 列)核對 carrier 與非 carrier 席位是否同列。★下列 file: 出處除註明外皆為工作樹未提交狀態,不是 HEAD——用來驗證「照 spec 字面實作」的具體行為,不代表已上線★。

## 一、13 條折入逐一驗(b1–b13,r2→r3)

**b1(下限守衛單向、列表格式填 1 就過)—— 修好**。第三版整條刪掉「人填 reported」與「下限守衛」,改成機器從已正規化報告數、無覆蓋旗標,原本被列表格式繞過的那個守衛已不存在。
引句:「機器寫進帳,沒有旗標可覆蓋」

**b2(「檔序第一個宣告=檔級」吞掉無檔級報告)—— 修好**。改成明文規則:檔首跳過 HTML 註解與空行後,第一個非空行「必須」是檔級宣告,不是「順位第一個宣告就當檔級」,不吞任何一種格式。
引句:「①檔首(跳過開頭的 HTML 註解與空行)第一個非空行必須是檔級」

**b3(子字串 a1 被 a10 命中)—— 修好**,WIP 實作已實測驗證:用真實 `r1-intake.md`(a1 出現 10 次)跑 `(?<![A-Za-z0-9])a1(?![A-Za-z0-9])` 詞界正則,只命中 a1 自己那一列(1 筆),a10 那列不再誤觸。
引句:「★對 intake 驗,整字不是子字串★」

**b4(self-found 變口袋)—— 修好**。整個欄位砍掉,S 完全由讀側算式 `max(0, M+R−N)` 推出,沒有任何輸入管道可以把「席位報了但不想折」的項目改標成自找。
引句:「★不加 `--self-found-set`★」

**b5(多席 N 與載體 M/R 粒度不同,漏併查不到)—— 明寫成既有邊界,不是機械關死**。這條沒有機械修法,r3 做的是把「intake 逐席對映表是唯一稽核線」寫進段首,跟前兩輪一致判定「不在本案機械關死範圍內」。
引句:「多席同輪時 M/R 只來自唯一載體,席位漏併進載體集合的機器查不到」

**b6(帳上分不出守衛咬過與純自報)—— 隨 b1 一併解決**。舊的「守衛咬過/沒咬過」區分本身建立在「有一支寬鬆下限守衛」之上,r3 直接不讓任何未正規化報告過關,不再有「守衛沒咬到但放行」這種中間態需要分辨。
引句:「★殘留的其他寫法一律擋★」

**b7(K<5 門檻拍腦袋)—— 部分修好**,加了第二判準與「暫用值」但 5 這個數字仍未解釋來源;上一輪(簡化守護者)已判定這是低成本、非阻塞的殘留武斷常數,這輪同意維持不擋。
引句:「K < 5 或近 30 天不到 3 輪時多印」

**b8(R 用詞三處不一致、免責句只在 gov --stats)—— 修好**。三處統一成同一句「編排者重現不到」,且明寫 disposal 那一行也印縮短版,不再是只有 `gov --stats` 才揭露 R 是人填的。
引句:「★段首固定兩句★(disposal 那一行也印縮短版)」

**b9(兩條 REVISIT 沒指令可量)—— 修好**。兩條 REVISIT 都改成點名 `lumos gov --stats` 加上具體要看的欄位名,不再是純散文提醒。
引句:「REVISIT:2026-10-08 跑 `lumos gov --stats` 看」

**b10(N/M/R 是 ? 時算式沒定義)—— 修好**,而且隨 b4 的設計改動(self-found 欄位整個砍掉、S 改公式推導)一併解決:不再有「⚠ 算術不通」這種需要额外定義的中間狀態,`?` 只有兩個結局(不算 S / 算出實數)。
引句:「★N/M/R 任一是 ? 就不算 S,印」

**b11(commands/05 教舊語法)—— 修好**。S4 明寫兩份速查表都要加 `--refuted-set`。
引句:「兩個 skill 的 record 範本、`lumos-project-notes` 的 commands/05 與 06 速查表都加 `--refuted-set`」

**b12(簡化席 (d)(e) 判保留)—— 維持保留,無變動**。雙層印法(單輪一行 + 全庫一段)與改名/K<5/段首兩句三項的保留判斷在 r3 沒有被推翻,理由與 r2 一致。
引句:「K、Σ報、Σ存活、Σ重現不到、Σ折、Σ放行」

**b13(檔序慣例沒寫進 SOP)—— 修好**。三條 SOP 規則(檔首檔級行、每條 finding 恰一行獨立 severity、驗收輪不留 severity 字樣)已寫進 [S4]。
引句:「收貨 SOP 補三條:檔首一行檔級 severity、每條 finding 恰一行獨立 `severity:`」

## 二、深挖 [S1] 拒收偵測:對六份以上真實報告實測(WIP 實作)

用 WIP 的 `_SEV_RESIDUE_RE = re.compile(r"(?i)(?:\bsev(?:erity)?\s*[:：]|嚴重度\s*[:：]|\[(?:clean|minor|major|blocker)\])")` 與 `_report_normalize_issues` 實跑七份真實檔案(`code-batch20/r1-{通才,架構對齊,外家否決}.md`、`code-clause-bindings-b/r1-{架構對齊-sonnet,外家否決-codex,單reviewer-sonnet}.md`、`code-clause-bindings-b/r3-架構對齊-sonnet.md`):**七份全數會被拒收或悄悄算出 0**,無一份能直接照現有格式過關。

### Finding A
severity: blocker
blocking: 是
判準:spec 自己舉的殘留範例格式,在 WIP 實作裡完全沒被偵測到,悄悄算出 0——這正是三輪重寫要根治的原始症狀,重演在 r3 自己身上。
`_SEV_RESIDUE_RE` 只認 `severity:`/`嚴重度:`/方括號等級三種字面,spec 第③條自己舉的「`## F1 — BLOCKER`」不含這三種字面中任何一種,實測 `_SEV_RESIDUE_RE.search("## F1 — BLOCKER")` 回 `None`。真實檔案 `code-batch20/r1-架構對齊.md`、`code-batch20/r1-通才.md`(兩份都有真實 major/blocker 發現)跑 `_report_normalize_issues` 皆回傳 0 個 issue(判定「已正規化」),但 `_report_reported_count` 算出 **0**——兩份有真內容的報告會被寫進帳「報了 0 條」,不是拒收、是靜默錯帳。
file: `scripts/lumos:4958`(`_SEV_RESIDUE_RE` 定義,工作樹未提交)
file: `governance/review-reports/code-batch20/r1-架構對齊.md`、`governance/review-reports/code-batch20/r1-通才.md`(兩份真實報告皆有具體 major 發現,WIP 實測 `reported=0`)

### Finding B
severity: blocker
blocking: 是
判準:一個現行活躍、本審查鏈自己五席之一的既有格式,被 spec 自己舉的例句字面命中並拒收,S4 沒有替這個席位的方法論規劃過渡。
「架構對齊」席固定用「五題固定架構、每題聚合一個 `- severity: X`」的既有寫法(不是逐條 finding 各自獨立宣告),`- severity: clean`/`- severity: minor` 正是 spec 第③條列的第一個例子。WIP 實測 `code-clause-bindings-b/r1-架構對齊-sonnet.md`(3 處)與 `code-clause-bindings-b/r3-架構對齊-sonnet.md`(驗收輪,3 處)全被 `_report_normalize_issues` 判定要 rc2,`code-clause-bindings/r1-架構對齊-sonnet.md` 同款寫法在 r1/r2/r3 三輪一致重現。改法不只是拿掉 `- `——這席目前是「一題可能聚合多條 finding、只印一個聚合嚴重度」,要符合「每條 finding 恰一行獨立宣告」得整個重寫回報方法論,S4 沒提到這件事。
引句:「行內 `severity:`(如 `- severity: minor`」
file: `governance/review-reports/code-clause-bindings-b/r1-架構對齊-sonnet.md:27,48,76`、`governance/review-reports/code-clause-bindings-b/r3-架構對齊-sonnet.md:27,50,85`

### Finding C
severity: blocker
blocking: 是
判準:本審查鏈自己派工用的收尾慣例句式(本次任務指示本身也要求「最後一行總結最嚴重 severity 與 blocking 條數」)會被同一支拒收偵測擋下,不是罕見寫法而是全庫慣例。
`governance/review-reports/` 底下有 330 個檔案含「(最嚴重|總結最嚴重|最高) severity」這種收尾句式。WIP 實測 `code-clause-bindings-b/r1-外家否決-codex.md`(「最嚴重 severity: major；blocking 4 條。」)與 `r1-單reviewer-sonnet.md`(「最嚴重 severity:blocker(Finding 1)。」)都被判定要 rc2——兩份報告本體的 finding 宣告格式完全合規,單純因為結尾總結句含 `severity:` 字樣就整份被擋。這條規則若照字面上線,今天所有仍在用這句收尾慣例的席位(含這次任務本身的派工指示)都需要先改掉收尾句才能記帳,S1/S4 都沒提到這個成本。
引句:「報告有一行 `- severity: major` 殘留 → record rc2 並印行號」
file: `governance/review-reports/code-clause-bindings-b/r1-外家否決-codex.md:55`、`governance/review-reports/code-clause-bindings-b/r1-單reviewer-sonnet.md:47`

## 三、深挖 [S2] intake 重現表列格式

### Finding D
severity: major
blocking: 是
判準:S2 假設每份 intake 都用同一套「HIT/MISS」字面詞彙標重現結果,但真實 intake 文件的用詞是編排者自訂的,不是定死格式;WIP 的整字驗證是「同一行含整字 id 與字面 `HIT`/`MISS`」,對不用這兩個字的 intake 會誤擋合法駁回。
grep 全庫 intake 檔:`code-clause-bindings*` 系列一致用「**HIT**」/「HIT」/「MISS」;但 `接手視圖/r1-intake.md` 用「— HIT,折」與「— 觀察對,判準不採(accepted)」並存(後者完全沒有 HIT/MISS 字樣)、`Codex完全支援/r1-intake.md` 用「→ MISS(不採信)」與「→ **部分 MISS**」、`probe-retire-v2/r1-intake.md` 用「2 MISS」比例句式——同一專案內至少四種措辭並存。若編排者沿用「accepted/不採信/判準不採」這類既有措辭記錄一筆重現不到,WIP 的 `("HIT" in ln or "MISS" in ln)` 檢查會找不到字面 HIT/MISS 而 rc2,即使那一列已經是編排者親自重現過、寫得很清楚的判決。
引句:「機械重現表那一列」
file: `governance/review-reports/接手視圖/r1-intake.md:19`(「觀察對,判準不採(accepted)」無 HIT/MISS 字樣)、`scripts/lumos:5346`(WIP 檢查訊息點名「含 HIT/MISS」)

## 四、深挖 [S3] N 去重與 S 公式邊界

### Finding E
severity: major
blocking: 是
判準:「同席報告先留痕、後當載體會不會 N 重複計數」這個問題,WIP 程式碼已經用 `(auditor, report_sha256)` 去重防住,但 r3-snapshot.md 本文完全沒寫這條規則——照 spec 文字字面實作(只講「N=該輪席位列 reported 加總」)不會想到要去重,會在同席兩筆的情境下重複計 N。
WIP `_review_yield_round` docstring 明寫「★同席同報告只算一次★(同一席會先留痕一筆、再當載體一筆;以 (auditor, report_sha256) 去重)」,但 spec 正文只有一句「N=該輪席位列 `reported` 加總」,沒提去重、也沒提這個去重鍵是 `report_sha256`(意味著兩筆記帳之間報告檔內容必須逐位元組相同,若中途改過一個字,sha 不同、去重會失效,一樣重複計)。查真實帳(`docs/.canary-log.jsonl` 1208–1216)目前每個 (loop,round,auditor) 只有一列,載體的 `findings_set` 跟自己的 `report_path`/`severity` 同列——今天的資料沒有踩到這個坑,但那是因為今天所有記帳都一次到位,不是 spec 規則保證的。
引句:「多席同輪時 M/R 只來自唯一載體」
file: `scripts/lumos:4993`(WIP `_review_yield_round` docstring 與去重鍵,工作樹未提交,spec 正文未提及)

## 五、已核對、無 finding 的項目

- **[S1] 檔首檔級行規則對今天格式的相容性**:抽查 `code-batch20`、`code-clause-bindings`、`code-clause-bindings-b` 全部 r1–r3 共 23 份真實席報告(排除 intake/snapshot),**沒有一份**以 `# ` 標題開頭、跳過檔級 severity 行;所有樣本第一個非空行(跳過 HTML 註解後)都已經是合法檔級宣告——今天沒有「標題開頭」這一種違規在流通,跟為什麼段講的「今天早上 8 份標題破折號嵌等級」是完全不同的另一個問題(見 Finding A/C)。
- **[S3] S=max(0,M+R−N) 在「去重折損為正」(N 大於 M+R,審查冗餘的正常情況)時 S=0**:WIP `_review_yield_line` 明確印「存活多於席位報的 0 條(編排者自找或漏併)」,跟「缺欄位」的「算不了(缺欄位)」是兩條不同分支,不會混淆,漏斗行本身已經同時印出 N 與 M 讓讀者自己看出折損量。file: `scripts/lumos:5019`

## 總結

最嚴重 severity:blocker(Finding A/B/C)。新 finding 共 5 條(blocker 3、major 2);blocking 條數:5(A/B/C/D/E 全部 blocking:是)。13 條折入 12 條確認修好、1 條(b7)判定殘留但沿用上輪「非阻塞」的判定;b1 的核心機制修好,但同一顆「拒收偵測」在自己舉的範例格式(`## F1 — BLOCKER`)上失靈,對兩份真實報告悄悄算出 0——這正是三輪重寫想根治、卻仍在 r3 自己身上重演的症狀。
