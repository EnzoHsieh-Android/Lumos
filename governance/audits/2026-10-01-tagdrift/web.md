# 前例調研：筆記寫法規則 × 標籤 × 過時檢查 × 精準檢索

調研日期：2026-10-01（WebSearch / WebFetch）。每項都附網址；「機制」盡量取自官方文件或原文。凡只出自第三方文章、或沒查到官方說法的，會當場標註。

---

## A. 文件跟程式碼綁在一起、偵測文件過時

### A1. Swimm：文件裡的程式片段跟程式碼綁定
- 網址：https://swimm.io/blog/how-does-swimm-s-auto-sync-feature-work 、https://swimm.io/blog/keeping-internal-docs-up-to-date-always-with-the-swimm-github-app 、https://docs.swimm.io/ide-integrations/ide-plugins/
- 機制：文件裡嵌入「程式片段、smart token（對某個識別字的引用）、smart path（對某條路徑的引用）」。每次 PR 都拿這些引用去比對最新程式碼。小改動（例如改名、換參數值）自動更新；引用的東西整個刪掉的話，就留一張任務請人重選。判斷時參考行標記、行號、token 引用、改動大小、版本控制歷史等訊號。CI 整合可以擋「會讓文件過時」的合併。IDE 外掛在有文件引用的程式行旁邊顯示圖示，點了就開那篇文件。
- 可借用：(1) 引用要指向一個**能機械驗證的錨點**（識別字、路徑），不能只是散文；(2) 把結果分成「可以自動修」和「要人處理」兩級；(3) 同一條綁定反過來用：從程式碼找到相關文件（IDE 圖示），等於「碰到某檔就推相關筆記」。
- 限制：商業產品，演算法有專利且不公開。只能驗證**片段和識別字還在不在**，驗不了散文裡的數量或行為描述，例如「這個函式會重試三次」。

### A2. Doorstop：可疑連結加指紋
- 網址：https://doorstop.readthedocs.io/en/latest/cli/validation.html 、https://doorstop.readthedocs.io/en/v2.1.2/reference/item/
- 機制：每個需求條目都是一支 YAML 檔。`reviewed` 欄存「上次審過時，這個條目的 SHA256 指紋」。`links` 的每一筆存「父條目 UID 加上當時父條目的指紋」。驗證時，如果父條目現在的指紋跟連結裡記的不一樣，這條連結就判成 **suspect**（可疑）；條目本身的指紋跟 `reviewed` 不一樣，就報「有未審改動」。指紋只算 UID、text、ref/references、link UID 這幾樣，`active`、`level` 這類欄位不算。人看過以後用 `doorstop review` 更新指紋，用 `doorstop clear` 清掉可疑連結。條目可以用 `references` 指向外部檔案或檔案中的某一行。
- 可借用：**最適合拿來在「零依賴、Python、單人維護」的情境下判斷過時**。筆記某一行寫上 `[ref:檔案#函式]`，同時把那個函式本體的雜湊存起來；函式內容一變，這行就變成 suspect，要人重看。這是純機械的判斷，不必理解語意。「哪些欄位算進指紋」這個設計也值得照抄：只改格式不該觸發重審。
- 限制：只能告訴你「依據變了，請重看」，沒辦法告訴你「這句話錯了」。依據改得頻繁時會吵，要調指紋範圍，例如只算函式簽名或去掉空白後的內容。工具本身是 Python，但要裝依賴套件，概念可以借，套件不必裝。

### A3. cog（Ned Batchelder）：讓程式產生文件內容，再用 `--check` 守住
- 網址：https://nedbatchelder.com/code/cog/index 、https://cog.readthedocs.io/en/stable/running.html
- 機制：在檔案裡用 `[[[cog ... ]]]` 和 `[[[end]]]` 圍出一段 Python 產生器，執行後把輸出寫回檔案。3.3.0 版（2021-11）加了 `--check`：如果重跑會改動檔案，就失敗，專門給 CI 用。
- 實例（剛好就是「數量漂移」）：https://github.com/agigante80/forge-kit/issues/201 。CLAUDE.md 裡手寫的 11 個測試套件數量有 3 個過時（寫 25 實際 45、寫 22 實際 81），提案照 cog `--check` 的模式寫一支腳本，解析這些宣稱、實際跑一次取得數字，CI 裡不一致就失敗。
- 可借用：**數量、清單、名稱這類程式碼答得了的內容，根本不該手寫，改成「存查詢不存答案」**。這跟你們「FACT 只准寫程式碼答不了的」方向一致，cog 是更進一步的版本：答得了的可以由查詢產生。產生區塊加上 `--check` 守衛，在零依賴 Python 裡幾十行就做得出來。
- 限制：只適用於「能從程式算出來」的內容。產生區塊會讓筆記變長；如果讀者是 AI，產生出來的值也會吃 context，所以適合放短值（數字、名稱），不適合整段清單。

### A4. embedme / embedmd / markdown-magic：把程式片段嵌進 Markdown，再驗證
- 網址：https://github.com/zakhenry/embedme 、https://github.com/campoy/embedmd 、https://github.com/DavidWells/markdown-magic
- 機制：embedme 在程式碼區塊的第一行寫註解標出來源路徑（可以指定行範圍），執行時把原檔內容嵌進來；`--verify` 用在 CI，確認重跑不會產生改動。markdown-magic 用 `<!-- docs ... -->` 這類註解區塊，按來源或自訂轉換重寫中間的內容。
- 可借用：用「註解標記加 verify 模式」守住複製進來的內容，概念跟 cog 一樣。
- 限制：只處理逐字複製的程式碼。用行號指定範圍本身就是漂移來源，你們現在已經在擋「行號引用」。

### A5. Sphinx `literalinclude :pyobject:` / doctest / rustdoc 的文件測試
- 網址：https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html 、https://doc.rust-lang.org/stable/rust-by-example/meta/doc.html
- 機制：`literalinclude` 的 `:pyobject:` 用**物件名稱**（類別、函式）而不是行號來引用程式碼，前面的程式行數變了也不受影響。doctest 和 rustdoc 會把文件裡的範例當測試實際執行。
- 可借用：**引用用名稱、不用行號**，跟你們「行號改寫成哪支檔的哪個函式」的規則一致，而且有成熟前例背書。
- 限制：只驗證範例跑不跑得動，驗不了描述性語句。

### A6. Concordion / Gauge：把散文斷言變成可執行規格
- 網址：https://concordion.org/instrumenting/java/markdown/ 、https://en.wikipedia.org/wiki/Gauge_(software)
- 機制：Concordion 讓人用一般散文寫規格，再用 Markdown 連結語法 `[值](- "指令")` 標註哪個值要拿去跟程式比對，由測試夾具執行。Gauge 把 Markdown 的 spec 和 scenario 拆成 step，每個 step 綁一個程式實作。
- 可借用：**行內標註「這個值是要驗的」**的語法，跟你們的 `[鍵:值]` 很像。可以想成一種 `[check:查詢名]` 標籤：這句裡的某個值要由某個查詢來驗。
- 限制：要寫測試夾具，屬於重型做法；而且是給需求和驗收用的，用在「描述內部實作的筆記」上成本偏高。

### A7. Google 內部 g3doc 的 freshness 註記（只有書中二手資料）
- 網址：https://abseil.io/resources/swe-book/html/ch10.html （《Software Engineering at Google》第 10 章）
- 機制（原文）：文件裡放 `freshness: { owner: \`username\` reviewed: '2019-02-27' }`；"metadata in the documentation set will send email reminders when the document hasn't been touched in, for example, three months"。文件放在版本控制下時，改這個日期也要過 code review；加上 "Last reviewed by..." 的署名能提高採用率。不再有用的文件要刪掉或標成 obsolete，並指出新資訊在哪。
- 可借用：`[confirmed:日期]` 加上到期提醒，你們已經有了；書裡還指出兩件事：要有負責人，以及改確認日期本身也要過審。
- 限制：**沒查到 g3doc 的公開官方文件**，只有書裡這段描述。這是一種靠時間的提醒，不看程式碼有沒有變，所以會誤報（程式沒變也叫你重審），也會漏報（程式變了，但還沒到期）。

### A8. Microsoft Learn 的 `ms.date`（補充，跟 A7 同一類）
- 網址：https://learn.microsoft.com/en-us/contribute/content/how-to-write-major-edits
- 機制：只有在做過「完整的 freshness review」時才准更新 `ms.date`；只改編輯、配圖、模板這類非技術面的東西時**不准動**。
- 可借用：**「確認日期」要跟「實際重審」綁在一起，不能跟「最後修改時間」混為一談**。這正是你們 `[confirmed:]` 要防的：只修錯字，不該把確認日期刷新。

### A9. Backstage TechDocs
- 網址：https://backstage.io/docs/features/techdocs/ 、https://backstage.io/blog/2020/09/08/announcing-tech-docs/
- 機制：docs-like-code，Markdown 跟程式碼放同一個 repo，走同一個 PR、同一個審查；文件透過 catalog 繼承 owner。
- 可借用：只有「同一個 PR 一起改」這個結構，你們的 pre-commit「改了 code 沒動圖譜」已經更強。
- 限制：**沒查到 TechDocs 內建的過時偵測機制**，它靠流程，不靠檢查。

### A10. Guru / Confluence 的「驗證到期」
- Guru：https://www.getguru.com/features/verification 。每張 Card 有一個驗證者和一個驗證週期，過期就變成 unverified 並通知專家；沒被驗證又沒人用的 Card 會進自動封存佇列。（「關鍵內容 30 天、一般 90 天、參考 180 天」這組數字出自第三方評測文章，**不是官方規定**。）Guru 官方範例建議：重驗時如果什麼都沒變，就**拉長**週期；變很多就**縮短**。
- Confluence：https://community.atlassian.com/forums/Confluence-articles/Verified-Pages-Now-Available-in-Confluence/ba-p/2664827 。2024 年起原生支援 "verified" 頁面狀態；「一年沒更新就改成 needs review、通知 owner」要自己用 Automation 規則組出來。
- 可借用：**週期依變動頻率自己調整**（穩定的拉長、常變的縮短），可以拿來設定 `[confirmed:]` 的有效期，不必全部固定半年。
- 限制：同樣只看時間、不看程式碼。

### A11. ADR 的 superseded 狀態鏈
- 網址：https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions （Nygard 2011 原文）、https://github.com/npryce/adr-tools
- 機制：ADR 的狀態有 proposed、accepted、deprecated、superseded。已接受的 ADR 不重開，而是由新 ADR 取代。`adr new -s 9 ...` 會建立新 ADR，同時把 ADR 9 的狀態改成「Superseded by …」，兩邊互相連結。
- 可借用：**取代關係要雙向寫、由工具一次寫好**（你們的 `decision-add` 加 `[status:superseded]` 已經接近這樣）。舊條目不刪，留作歷史。
- 限制：只管「決策被新決策取代」，不偵測「程式偷偷背離決策」，後者要靠 fitness function（C2）。

### A12. 學術：偵測文件裡過時的程式元素引用
- Tan, Wagner, Treude, "Detecting outdated code element references in software repository documentation"（EMSE 2023）：https://link.springer.com/article/10.1007/s10664-023-10397-6 ；工具版 "Wait, wasn't that code here before?"：https://arxiv.org/abs/2307.04291
  - 機制：從 README 和 wiki 抽出看起來像程式元素的字串，跟原始碼比對；**文件還在提、但程式碼裡所有實例都已刪掉**，就判成過時。做成 GitHub Action，在每個 PR 時掃描。摘要說 GitHub 最熱門的 1000 個專案中，超過四分之一至少有一個過時引用。
- Treude & Baltes, "Context Rot in AI-Assisted Software Development: Repurposing Documentation Consistency for AI Configuration Artifacts"（arXiv 2606.09090，2026-06）：https://arxiv.org/abs/2606.09090
  - 機制：把上面那個 README 一致性檢查器直接拿去跑 CLAUDE.md、.cursorrules 這類給 AI 讀的設定檔；在 356 個 repo 裡，有 23.0% 找到過時的程式元素引用。論文把這個現象命名為 "context rot"。
- Panthaplackel 等人，"Deep Just-In-Time Inconsistency Detection Between Comments and Source Code"（AAAI 2021）：https://arxiv.org/abs/2010.01625 。在程式改動當下判斷註解是不是跟著不一致，用的是學出來的模型。
- 可借用：**反引號裡的識別字或路徑，到程式碼裡已經找不到**，這是最便宜、證據最強的過時判準，而且已經有論文直接套用到 AI 讀的檔案上。
- 限制：只抓「名稱消失」，抓不到「名稱還在、行為變了」。JIT 那類模型需要訓練資料，不適合零依賴的情境。

---

## B. 文件寫法規則的 lint

### B1. Vale（自訂規則）
- 網址：https://github.com/vale-cli/vale 、https://docs.vale.sh/checks/existence 、https://docs.vale.sh/checks/conditional 、https://docs.vale.sh/checks/script
- 機制：每條規則是一支 YAML 檔，`extends` 指定檢查型別：existence、substitution、occurrence、consistency、conditional、capitalization、metric、script 等。
  - `conditional`：「出現 first 就必須也出現 second」，例如縮寫必須有定義。**可以直接對應「寫了 `RULE:` 就必須帶 `[since:]` 和 `[retire:]`」**。
  - `script`：用 Tengo 語言寫自訂邏輯，回傳 `matches`（起訖位置）。
- 時態、絕對語、數量相關的現成規則範例（Google 風格包 https://github.com/vale-cli/Google ）：
  - `Google/Timeless.yml`：對應 https://developers.google.com/style/timeless-documentation 。官方指南列出要避免的詞：as of this writing、currently、does not yet、eventually、existing、future、in the future、latest、new、newer、now、old、older、presently、at present、soon。**但 Vale 規則檔只收了 currently、latest、soon**，檔內註解說 now 和 new 誤報太多：在 950 檔的語料上，命中數從 14 漲到 117。
  - `Google/ExcessiveClaims.yml`：抓 best、simplest、fastest、guarantee(s)。檔內註解說 never、always、ensure 在技術文件裡多半是正當的指令，在那份語料上 142 次命中裡占 125 次，所以拿掉了。
  - `Google/Will.yml`：抓 will（未來式）。
- 可借用：(1) **時間錨詞清單**可以直接翻成中文：「目前、現在、最新、即將、尚未、已經改成、新版、舊版」；(2) **規則檔裡附上誤報量測和撤除理由**，等於你們的 RETIRE-IF；(3) 用 conditional 這種「出現 A 就必須有 B」的檢查型別來驗標籤齊不齊。
- 限制：Vale 是 Go 寫的二進位，不算零依賴；對中文斷詞的支援有限。**沒查到任何「數量宣稱」的現成規則**（例如抓「共 N 個」「三支」），要自己用 regex 或 script 寫。

### B2. textlint 加 prh
- 網址：https://github.com/textlint-rule/textlint-rule-prh （中文和日文社群文章很多，例如 https://zenn.dev/jnxjez/articles/573d87f82c8a06 ）
- 機制：Node.js 外掛式的 lint；prh 用 YAML 的 `expected` 和 `pattern`（可以用正規表示式）統一用詞，並能自動修正。
- 可借用：**CJK 文字的 lint 有成熟生態**；用 expected/pattern 表統一術語，正好可以拿來治「同一個東西換了名字，筆記還用舊名」：舊名列進 pattern，lint 就會提示。
- 限制：要用 Node，不符合零依賴。

### B3. markdownlint / frontmatter schema 工具
- 網址：https://github.com/DavidAnson/markdownlint （自訂規則可以拿到 `params.frontMatterLines`）、https://github.com/JulianCataldo/eslint-plugin-markdown-frontmatter-schema （用 JSON Schema 驗 frontmatter）、https://github.com/hay-kot/flint
- 可借用：用「frontmatter 的 schema」做驗證；你們的 `lumos lint` 已經涵蓋。
- 限制：管的是結構，不管語意新不新。

### B4. proselint / write-good / alex
- 網址：https://github.com/amperser/proselint 、https://github.com/btford/write-good
- 機制：proselint 是 Python，內建一組規則模組（hedging、weasel_words…）；write-good 抓被動語態和 weasel words。
- 限制：規則內容非常窄，例如 proselint 的 weasel_words 據報只抓 "very"；都是英文。**只有「規則模組化、每條可以單獨開關」這個架構值得參考**，規則本身用不到。

### B5. agents-lint（針對 AGENTS.md / CLAUDE.md 的 lint）
- 網址：https://github.com/giacomo/agents-lint
- 機制：檢查引用的路徑存不存在、npm script 和 make target 有沒有定義、依賴是否棄用、框架寫法是否過時、多支 context 檔之間有沒有矛盾、Claude 記憶檔的連結和 frontmatter；還會**把 2024 年以前的年份當成過時訊號**。README 自稱零外部依賴（TypeScript）。**不用檔內的標籤或 metadata**，靠設定檔調整。
- 可借用：檢查清單幾乎可以照搬成 `lumos doctor` 的子項：路徑、指令、腳本名稱存不存在。
- 限制：只抓「引用消失」，不抓語意。

---

## C. 帶有效期限或驗證條件的知識條目

### C1. dbt source freshness：宣告門檻，由工具去查
- 網址：https://docs.getdbt.com/reference/resource-configs/freshness
- 機制：在 YAML 裡宣告 `loaded_at_field` 和 `warn_after` / `error_after`（各要 count 和 period）；`dbt source freshness` 會去查那個欄位的 MAX 值，跟現在時間比，給出 pass、warn 或 error 三態。
- 可借用：**「存查詢不存答案」的標準形狀：要查哪個欄位、警告門檻、錯誤門檻**；另外是**兩段門檻**（先唸、再擋）。你們的 `[confirmed:]` 可以分成「N 天唸、M 天擋」。

### C2. Data Contract（datacontract-cli）
- 網址：https://github.com/datacontract/datacontract-cli 、https://docs.datacontract.com/service-levels
- 機制：YAML 合約宣告 schema、品質檢查（可以用 SodaCL 等 DSL）和 freshness（最新資料的最大年齡）；`datacontract test` 實際連上資料源跑一次。也能 lint 合約本身、偵測破壞性變更。
- 可借用：**資料庫實際值、生產觀測這類程式碼答不了的 FACT，也可以「存查詢」**：把 `[來源:資料庫]` 加上一條查詢存起來，doctor 能連就重跑，連不到就只檢查日期。

### C3. Fitness functions（《Building Evolutionary Architectures》，Ford / Parsons / Kua）與 ArchUnit
- 網址：https://dokumen.pub/building-evolutionary-architectures-automated-software-governance-2nbsped-1492097543-9781492097549.html （第二版書目）；實作範例 https://github.com/thmuch/architecture-fitness-functions
- 定義（書中）："Any mechanism that performs an objective integrity assessment of some architectural characteristic"。實作上是放進 CI 的架構測試，例如用 ArchUnit 驗套件依賴方向。也有文章主張把每篇 ADR 綁一個 fitness function（https://dev.to/alexandreamadocastro/stop-architecture-drift-operationalizing-adrs-with-automated-fitness-functions-22oi ）。
- 可借用：**決策或 RULE 綁一條可執行檢查**，你們的 `[test:]` 和 ★INVARIANT★ 就是這個形狀，有正式名稱和文獻可以引用。

### C4. 會過期的 TODO（todo-or-die、ESLint `unicorn/expiring-todo-comments`）
- 網址：https://github.com/sindresorhus/eslint-plugin-unicorn/blob/main/docs/rules/expiring-todo-comments.md 、https://github.com/davidpdrsn/todo-or-die
- 機制：在 TODO 註解裡寫條件，例如 `[2026-01-01]`、`[>2.0.0]`（套件版本）、`[+dep]`（裝了某套件）；條件成立，lint 就報錯。todo-or-die（Rust）還能用「某個 GitHub issue 關了」或「某個 crate 版本出了」當觸發條件。
- 可借用：**撤除條件不只是日期，還可以是「可機械判定的事件」**：版本、依賴、issue 狀態、某個檔或函式消失。你們的 `[retire:條件]` 現在是自由文字，可以分出一小組**機器讀得懂的條件語法**，例如 `[retire:gone:檔#函式]`、`[retire:after:2027-01-01]`，讓 doctor 能自動判斷到期。
- 限制：條件語法一旦定型就難改，要先收斂到少數幾種。

### C5. Mem0 的 `expires_on` metadata（記憶到期）
- 網址：https://docs.mem0.ai/cookbooks/essentials/memory-expiration-short-and-long-term
- 機制：寫記憶時在 metadata 放 `expires_on`，**由應用程式自己定期清掉過期的**（Mem0 不自動刪）；刪掉後自然不會出現在搜尋結果裡。
- 可借用：證明「同一個到期欄位同時拿來清理和過濾檢索」是業界常見做法。這是 E 類的弱形態。

### C6. 「宣告式檢查」的其他實例
- 你們說的 `verify:`（只存查詢、不存答案、開場重驗）**沒有查到同名的通用標準**。最接近的是：cog `--check`（A3）、dbt freshness（C1）、data contract（C2）、Concordion 的行內指令（A6）。這四個加起來可以當 PRIOR-ART。

---

## D. 用 metadata 或標籤做精準檢索、減少 LLM context

### D1. Claude Code `.claude/rules/` 的 `paths:` frontmatter
- 網址：https://code.claude.com/docs/en/memory
- 機制（官方）：規則檔的 frontmatter 裡寫 `paths:` glob 清單。沒寫 `paths` 的規則在啟動時一律載入；有寫的只在 "Claude reads files matching the pattern" 時才載入（官方原話是 "not on every tool use"）。Claude Code 只讀 `paths` 這一個欄位，其他欄位一律忽略。官方建議 CLAUDE.md 控制在 200 行以內，其餘拆到 path-scoped rules。另外，auto memory 的 frontmatter 會由 Claude Code 自動寫入 `modified` 時間戳，讓讀者知道這筆事實有多新。
- 可借用：**「碰到某檔才載入」是官方背書的做法**；你們的 `about_code` 已經是同一種東西的另一種寫法。`modified` 自動時間戳是「新鮮度給讀者看」的官方先例。
- 限制：只能用路徑觸發，不能用語意或標籤觸發；粒度是整個檔，不是單行。

### D2. Cursor rules（`.mdc`）與 Kiro steering
- Cursor：網址為第三方整理（例如 https://techsy.io/en/blog/cursor-rules-guide ）。**沒抓到 Cursor 官方文件原文**。frontmatter 有 `description`、`globs`、`alwaysApply`，組合成四種模式：Always、Auto Attached（globs 命中）、Agent Requested（agent 讀 description 自己決定要不要載入）、Manual。
- Kiro（官方）：https://kiro.dev/docs/steering/ 。`inclusion: always | fileMatch | manual | auto`；`fileMatch` 搭配 `fileMatchPattern`；`auto` 要求 `name` 和 `description`，「request 符合 description 就自動載入」。官方註明 CLI 不支援 inclusion 模式。
- 可借用：**四種載入模式（一律／路徑命中／描述命中／手動）是業界收斂出來的分類**，可以直接對應到筆記「什麼情況下推給 agent」。

### D3. RAG 的 metadata filtering 與 self-query
- LangChain SelfQueryRetriever：https://js.langchain.com/docs/how_to/self_query/ 。先用 `AttributeInfo`（name、description、type）宣告有哪些 metadata 欄位，由 LLM 把自然語言問題轉成「語意查詢加結構化 filter」，再翻譯成向量庫原生的 filter 語法。
- LlamaIndex Auto-Retrieval：https://developers.llamaindex.ai/python/framework/integrations/vector_stores/chroma_auto_retriever/ 。`VectorStoreInfo` 加 `MetadataInfo`，概念同上。
- Pinecone metadata filter：https://docs.pinecone.io/guides/search/filter-by-metadata 。`$eq`、`$in`、`$gt`、`$and` 這類運算子，在伺服器端先過濾再排序。
- 可借用：**標籤欄位要有一份 schema（名稱、型別、說明）**，agent 才知道能用哪些欄位過濾；這份 schema 本身也能拿來 lint 標籤。
- 限制：讓 LLM 自己產生 filter 有錯誤率；在小型筆記庫上，向量庫是殺雞用牛刀。第三方文章另外提醒：filter 太嚴會讓好文件在檢索前就被濾掉（https://optyxstack.com/rag-reliability/metadata-filters-in-rag-why-good-documents-disappear-before-retrieval-starts ）。

### D4. Anthropic Contextual Retrieval
- 網址：https://www.anthropic.com/news/contextual-retrieval
- 機制：每個 chunk 前面加上一段 50 到 100 token、由 Claude 產生的「這段在整份文件中的脈絡」說明，再做 embedding 和 BM25。數字（原文）：只用 contextual embeddings 時，top-20 檢索失敗率降 35%（5.7% → 3.7%）；再加 BM25 降 49%（→ 2.9%）；再加 rerank 降 67%（→ 1.9%）。**原文也說，知識庫小於約 20 萬 token 時，直接整份放進 prompt 配合 prompt caching 就好。**
- 可借用：(1) **每個片段自帶一行「我屬於哪裡、在講什麼」**，你們的摘要行加前綴已經是同一種形狀；(2) 先估筆記庫總量，如果總量小，精準檢索的價值主要在「別塞進不相關的東西」，而不是「找得到」。
- 限制：要呼叫 LLM 產生脈絡句，維護時會跟著漂移。

### D5. Agent 記憶系統的分類標籤：Letta（MemGPT）、Mem0
- Letta：https://docs.letta.com/api/resources/agents/subresources/passages/methods/search 。分 core memory（帶 label 的區塊，一直在 context 裡）和 archival memory（在 context 外，用語意搜尋）；archival 搜尋可以帶 `tags` 和 `tag_match_mode: any|all`。
- Mem0：https://docs.mem0.ai/platform/features/v2-memory-filters 。可以用 `categories`、`metadata`、`keywords` 過濾，支援 `in`、`eq`、`contains`，也能用 AND、OR、NOT 組合；官方 cookbook 建議只定義 3 到 5 個清楚的分類（https://docs.mem0.ai/cookbooks/essentials/tagging-and-organizing-memories ）。
- 可借用：**分兩層：常駐的小核心，加上按標籤取用的大倉庫**，跟你們「記憶只回答去哪查、圖譜是真相」同構；**分類要少（3 到 5 個）**是有出處的經驗值。
- 限制：兩者都是服務或框架，而且是以對話為中心，不處理「程式碼變了」這件事。

### D6. Obsidian Dataview：frontmatter 加行內欄位查詢
- 網址：https://blacksmithgu.github.io/obsidian-dataview/annotation/add-metadata/
- 機制：同時讀 YAML frontmatter 和行內欄位。行內欄位可以寫成 `[key:: value]`（顯示鍵和值）或 `(key:: value)`（只顯示值）；**寫在清單項目上的方括號欄位，屬於那一個清單項目**。查詢可以寫 `WHERE due < date(today)`、`file.mtime >= date(today) - dur(1 week)`。
- 可借用：**這是跟你們 `[鍵:值]` 最像的成熟語法**，而且有「欄位屬於那一行」的語意，正好對應「摘要行是檢索單位」。它也證明了同一組欄位可以同時用來「列出過期條目」（`WHERE reviewed < date(today) - dur(180 days)`）和「篩選內容」。
- 限制：只是查詢引擎，沒有程式碼比對；Dataview 用雙冒號 `::`，你們用單冒號，兩者不相容（應該無所謂，除非想用 Obsidian 瀏覽）。

---

## E. 有沒有人把 A 到 D 合起來（同一套結構化標籤同時用來偵測過時和精準檢索）

**結論：沒查到一個「同一組行內標籤同時驅動過時偵測和 agent 精準載入」的現成工具或論文。** 查到的都是「兩件事共用一部分底層」的半合一。（照 CLAUDE.md 的規矩，這句「沒有」如果會決定要不要自建，應該另外派一個乾淨的 agent 用原始問題再查一次。）

| 前例 | 共用了什麼 | 缺什麼 |
|---|---|---|
| Swimm | 同一條「文件↔程式碼」綁定，PR 時用來驗過時，IDE 裡用來從程式碼找到文件 | 綁定的是程式片段，不是可查詢的標籤；商業閉源 |
| Graphiti / Zep（https://arxiv.org/abs/2501.13956 、https://help.getzep.com/facts ） | 每條事實邊有 `valid_at`/`invalid_at`（世界時間）和 `created_at`/`expired_at`（系統時間）；新事實跟舊事實矛盾時，**把舊邊標成失效而不是刪掉**，檢索時不會把失效的事實當現況，又能查「某時點時相信什麼」 | 矛盾靠 LLM 抽取判斷，不是對照程式碼；對象是對話記憶 |
| Mem0 `expires_on` | 同一個到期欄位用來清理，也間接用來過濾檢索 | 要自己寫清理；只有時間一個維度 |
| Obsidian Dataview | 同一組行內欄位可以查過期、也可以篩內容 | 純查詢，沒有過時判準 |
| Doorstop | 條目的 links 加指紋判 suspect；條目 YAML 欄位可以拿來做篩選和發佈 | 沒有給 LLM 用的檢索層 |
| Claude Code `paths:` / Kiro `fileMatch` | 用路徑決定載入 | 完全沒有過時判斷 |
| Treude & Baltes 2026（context rot） | 明說要把文件一致性研究拿來治 AI context 檔 | 只做偵測，沒做檢索 |
| claude-drift（https://github.com/marky291/claude-drift ） | 把漂移分成 reference、context、legacy-narration 三類，用 subagent 推理修正 | README 說他們在 40 個 repo 試過確定性掃描器，規則補不完，所以改用推理（自述，未獨立驗證）；不用標籤，也不做檢索 |

可以拼出的合一形狀（從上面借來的部件）：
- 錨點標籤 `[ref:檔#符號]` 只有一份，同時用在三個地方：(1) 過時偵測：符號消失就報 stale（A12）；符號本體雜湊變了就報 suspect（A2）。(2) 檢索：碰到那支檔就推這一行（D1、Swimm IDE）。(3) 撤除：`[retire:gone:檔#符號]` 由機器判斷（C4）。
- 時間標籤 `[confirmed:日期]` 也是一份同時兩用：過了 N 天唸、M 天擋（C1 兩段門檻、A7）；檢索時把過期的行降權，或在結果旁標「未確認」（Mem0、temporal RAG）。
- 狀態標籤 `[status:superseded]`：lint 時查 superseded 的行是否指向取代者（A11）；檢索時預設排除，或只在 `--superseded` 時才給（Graphiti 的失效邊）。

---

## 綜合觀察

**最多人用的做法**（成熟、多家採用）
1. **時間到期加負責人**（Google freshness、Guru、Confluence verified、MS Learn `ms.date`）：最普遍，但只看時間、不看程式碼，誤報和漏報都多。
2. **從程式產生，再用 `--check` 守**（cog、embedme、markdown-magic、doctest、rustdoc）：開發者文件圈最普遍的「零漂移」做法，只適用於程式算得出來的內容。
3. **用名稱引用程式元素，再驗名稱還在不在**（Sphinx `:pyobject:`、Swimm smart token、Tan 等人的 DOCER、agents-lint）：門檻最低、證據最硬。
4. **用路徑或 glob 決定載入**（Claude Code `paths:`、Cursor globs、Kiro fileMatch）：AI 工具圈在 2025 到 2026 年收斂出來的標準。
5. **用 metadata filter 縮小檢索範圍**（Pinecone、LangChain、LlamaIndex、Mem0、Letta tags）：RAG 圈的標配。

**對你們（單人維護、零依賴 Python CLI、讀者是 AI agent）最值得借的**
1. **Doorstop 的指紋加 suspect 模型**：在 `[ref:檔#函式]` 旁存一個雜湊（或由 doctor 維護一份旁表），依據變了就把那一行標成「要重看」。純 stdlib（hashlib、ast）就做得出來，判準完全機械，也不會像純時間到期那樣誤報。
2. **cog `--check` 式的「存查詢不存答案」**：把數量和清單從手寫改成查詢產生，doctor 只比對；forge-kit #201 就是你們要治的同一種病，還附了實作形狀。
3. **符號消失就判過時**（Tan 等人；Treude & Baltes 已經直接套用到 AI context 檔，在 356 個 repo 裡有 23% 中招）：反引號裡的識別字到程式碼裡 grep 不到就報。這是最便宜、最該先做的一刀。
4. **Vale Google 包的「時間錨詞」與「絕對語」清單，連同它的誤報筆記**：翻成中文規則（「目前、現在、最新、即將、尚未、新版」），**只唸不擋**，並照抄它「附語料誤報量、所以拿掉某些詞」的寫法當 RETIRE-IF。
5. **TODO-or-die 式的可機器判定撤除條件**：替 `[retire:]` 定 2 到 3 種機器讀得懂的形式（日期、符號消失、某條決策被取代），其餘仍可寫自由文字但沒有自動效力。
6. **Kiro 和 Cursor 的四種載入模式加 Mem0「分類 3 到 5 個」的經驗**：標籤鍵控制在少數幾個，每個都要同時能驅動檢查或檢索其中至少一件，否則不該存在。
7. **Anthropic 那句「小於 20 萬 token 就整份放進去」**：先量筆記庫總量。如果總量不大，精準檢索的目標應該定成「降低噪音和誤導」（例如排除 superseded、標示未確認），而不是「找得到」。

**看起來好、但不適合的**
- **Swimm**：閉源商業產品，演算法不公開，也依賴 SaaS，只能借概念。
- **Concordion / Gauge**：要寫測試夾具，用在「描述內部實作的筆記」上成本太高；你們的 `[test:]` 綁現有測試已經夠了。
- **向量庫加 self-query retriever**：需要 embedding 和 LLM 產生 filter，違反零依賴，而且在小型筆記庫上沒必要；LLM 產生的 filter 又多一層錯誤來源。
- **只靠時間的 freshness（Guru 式）**：單人維護時，到期提醒會變成例行公事式的「蓋章續期」；MS Learn 特地規定「沒真的重審不准改日期」，正說明這個風險。應該當補位，不能當主力。
- **claude-drift 式全靠 LLM 推理找漂移**：抓得到語意漂移，但沒有機械判準、結果無法重現，不能當 pre-commit 或 CI 的閘，最多當定期巡檢。
- **Vale / textlint 本體**：Go 二進位或 Node 依賴，違反零依賴；把規則清單和檢查型別（existence、conditional）的設計抄進 Python 就好。
- **Graphiti 的雙時間模型完整版**：四個時間戳對單人筆記太重；只借「失效不刪、檢索預設排除失效條目」這一條就夠了。
