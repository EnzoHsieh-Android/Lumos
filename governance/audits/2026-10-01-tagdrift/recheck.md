# 乾淨 agent 用原始問題重查(2026-10-01,sonnet,不給前一份結論)

**調研結果:有接近的前例,但沒找到完整對應的。**

目前沒找到哪個工具同時符合三個條件:句子或段落層級的行內標籤、同一套標籤用來判過時、同一套標籤也用來決定載入哪一段。我找到的都是只做到一半,或兩邊用的標籤是分開的。下面的細節大多來自搜尋摘要和 WebFetch 的小模型整理,不是我逐字讀過原文,表中標「論文未明說」或「摘要」的地方尤其要自己核對。

## 候選清單

| 候選與來源 | 它怎麼做 | (a) 過時判斷 | (b) 按需載入 | 同一套標籤? | 粒度 |
|---|---|---|---|---|---|
| **Fiberplane drift**<br>https://blog.fiberplane.com/blog/drift-documentation-linter/ | 用 frontmatter 或行內註記把文件綁到程式碼,格式是「路徑 #符號 @提交編號」。`drift link` 綁定並蓋上提交編號,CI 的 `drift check` 比對 tree-sitter 抽出的語法樹指紋,只有被綁的符號變了才報過時,縮排改動不報。有提供給 Claude Code、Codex、Cursor 的 agent skill。 | 有 | 只有「教 agent 怎麼用這個工具」的 skill,抓不到「依錨點只載入相關文件」的說明 | 否,錨點只用在過時判斷 | 檔案級或符號級,文件側以區塊為主 |
| **DocGuard**<br>https://github.com/raccioly/docguard | 文件區段可用 `covers=` 指向程式符號,另有 `last-reviewed` 時間戳和 `.docguard-evidence.json`(逐句對應來源)。Freshness 檢查器數「上次審閱後有幾個提交」。對 agent 提供 MCP 唯讀工具、`docguard agent --task` 和 `context-pack.md`。 | 有 | 有,依任務產生精簡的 context pack | 部分。證據檔和 `covers=` 看起來同時服務兩邊,但 README 沒明說 context pack 是靠同一批標籤挑的,需要讀原始碼確認 | 區段級,證據檔可到句子 |
| **Codified Context 論文**<br>https://arxiv.org/html/2602.20478v1 | 三層結構。第一層常駐(約 660 行),第二層用「檔案樣式觸發表」呼叫專家 agent,第三層由 MCP 檢索服務按需查詢(關鍵字子字串比對)。另有「context drift detector」在 session 開頭比對近期提交與「子系統到檔案」的對照,有檔案改了但規格沒更新就注入警告。 | 有 | 有 | 論文未明說。子系統對照表在觸發邏輯和漂移偵測裡都出現,所以架構上共用,但論文沒承認這點 | 子系統或文件級 |
| **ADR 機器可讀化(rjmurillo/ai-agents PR 5209)**<br>https://github.com/rjmurillo/ai-agents/pull/5209 | 只讀 frontmatter 的 `status`、`date`、`superseded-by`、`review-by`,有三道檢查腳本(生命週期、連結、索引)。agent 讀只含 frontmatter 資訊的索引,正文無法影響狀態。PR 寫明原本 98 筆裡有 59 筆沒有機器可讀的狀態。 | 有,靠狀態、取代關係和 `review-by` 日期 | 部分。agent 看索引再決定讀哪份 | 是,同一組 frontmatter 欄位 | 整份文件 |
| **Zep/Graphiti**<br>https://arxiv.org/pdf/2501.13956 | 每條事實(邊)帶 `valid_at`/`invalid_at`,新事實與舊事實矛盾時把舊的標失效而不刪。檢索只取當前或指定時間點有效的切片。 | 有,由新資訊觸發 | 有 | 是,同一組時間欄位 | 單一事實。但對象是對話記憶,不是專案文件 |
| **Temporal Validity in Retrieval Memory**<br>https://arxiv.org/pdf/2606.26511 | 事實層級的有效期間中繼資料,檢索時過濾過期事實並偵測過期。 | 有 | 有 | 摘要看起來是,細節我沒讀原文 | 單一事實,同樣是記憶系統 |
| **Claude Code `.claude/rules/` 的 `paths:`**<br>搜尋結果:https://dev.to/thlandgraf/how-i-use-clauderules-to-give-claude-code-domain-knowledge-about-my-projects-file-structure-47l9 | frontmatter 的 glob 決定規則何時載入。 | 無 | 有 | 否 | 整份規則檔 |
| **Cursor `.mdc` 的 `globs`/`alwaysApply`/`description`**<br>搜尋結果:https://techsy.io/en/blog/cursor-rules-guide | 同上,另有靠 description 讓模型自行判斷是否載入。 | 無。有文章指出 glob 因改目錄名而靜默失效(stale),但那是使用者要自己發現的 | 有 | 否 | 整份規則檔 |
| **agents-lint、ctxlint 等 AGENTS.md linter**<br>https://github.com/giacomo/agents-lint<br>https://github.com/YawLabs/ctxlint | 檢查檔案中提到的路徑、npm script、框架寫法是否還存在;ctxlint 另有 token 用量與冗餘內容偵測。 | 有 | 無。ctxlint 的 token 功能只是報告,不做載入選擇 | 不適用 | 整份檔,靠文中提到的路徑判斷 |
| **docs 新鮮度的 frontmatter 慣例**<br>https://github.com/raccioly/docguard/pull/426、https://github.com/philmea/swarmsync/issues/6 | `last_reviewed` 之類欄位加 CI 報告。 | 有 | 無 | 不適用 | 整份文件 |
| **frontmatter-first 載入模式**<br>https://medium.com/@michael.hannecke/frontmatter-first-is-not-optional-context-window-survival-for-local-llms-in-opencode-15809b207977、https://www.fmind.dev/articles/agent-docs-answer-locally-before-the-web-a-shared-reference-for-every-coding-agent/ | 先讀每份文件前幾行的 `description`/`status`/`date`,判斷相關才讀全文,或用 `docs/_manifest.yaml` 索引。 | 只有宣告年齡,沒有自動判斷 | 有 | 否 | 整份文件 |
| **or1can/claims**<br>https://github.com/or1can/claims | 把文件與 agent 指令中的說法拿去對程式碼執行驗證(跑指令、解析符號、查 git 歷史),有 `stale-claims` 檢查。 | 有 | 無 | 不適用 | 說法(claim)級 |
| **Claude Code 自己的記憶機制**<br>搜尋結果:https://medium.com/@kanavanand8/how-memory-works-in-claude-code-harness-d8b242c114c2 | 超過一天的記憶讀取時動態附上「已 N 天」警告,沒有過期欄位。 | 弱,只有天數提示 | 只有 MEMORY.md 索引 | 不適用 | 單一記憶檔 |

## 結論

- **「同一套標籤同時驅動過時判斷與按需載入」:沒找到完整前例。** 沒找到的句子層級行內標籤,這個範圍我只做了十幾組搜尋。
- **最接近的兩個:**
  - 整份文件粒度:rjmurillo 的 ADR frontmatter(`status`、`superseded-by`、`review-by`)。同一組欄位既讓檢查腳本判斷生命週期,也讓 agent 只看索引就知道哪些是有效的約束。
  - 事實粒度:Zep/Graphiti 的 `valid_at`/`invalid_at`,以及 2606.26511 那篇論文。同一組時間欄位同時管失效和檢索過濾。缺點是它們處理的是對話或事實記憶,不是人寫的專案筆記。
- **「宣告綁定」那一派:** DocGuard 的 `covers=` 與證據檔,以及 Fiberplane drift 的錨點,是文件側細粒度標註加自動過時判斷做得最完整的。DocGuard 另外有給 agent 的 context pack,但標籤是否共用我沒證實。
- **「按需載入」那一派:** Claude Code 的 `paths:` 和 Cursor 的 `globs` 做得很普遍,但完全不碰過時判斷,甚至有 glob 隨目錄改名而靜默失效的抱怨。Codified Context 論文是少數把「觸發表」和「漂移偵測」放在同一個系統裡的,但共用與否論文沒說。
- 所以「文件側細粒度標籤同時驅動兩邊」這件事,現有做法是各做一半再拼起來,沒看到一個明確把它當設計原則寫出來的前例。

## 用過的搜尋詞

1. documentation staleness detection metadata tags AI agent context loading AGENTS.md
2. docs drift detection code docs mismatch tool "stale documentation" CI
3. CLAUDE.md memory entries expiry date "valid_until" OR "expires" staleness agent memory
4. temporal knowledge graph facts valid_from invalid_at stale facts retrieval agent memory Graphiti Zep
5. 文件 過時 偵測 標籤 AI agent 按需載入 context 專案筆記
6. ADR status superseded deprecated machine-readable front matter adr-tools log4brains agent retrieval
7. Cursor rules globs alwaysApply description auto-attached rules scoped context; rule staleness
8. docs-as-code freshness metadata "last_reviewed" "review_by" stale content lint front matter
9. agents-lint AGENTS.md stale paths linter github
10. "applies_to" OR "applies-to" front matter docs agent loads only relevant docs and flags stale when referenced files change
11. claim-level annotations documentation "verified_against" code agent knowledge base freshness retrieval filter
12. Claude Code rules "paths:" frontmatter .claude/rules path-specific rules load conditionally
13. Docusaurus OR Backstage TechDocs OR Mintlify "last_verified" front matter doc owner review cycle stale agent llms.txt
14. Basic Memory OR Obsidian agent memory markdown notes frontmatter status "valid_until" retrieval filter stale notes MCP

另外直接讀過的頁面是 Fiberplane、Codified Context 論文、DocGuard、2606.26511、PR 5209、or1can/claims、ctxlint。
