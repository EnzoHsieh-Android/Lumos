severity: major

〈開頭:白話/依據/PRIOR-ART/RETIRE-IF/REVISIT〉已讀,無 finding。PRIOR-ART 對「代碼審留痕綁提交祖先鏈」與「2026-09-22 事故」的描述,對照 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:23-24` 查證屬實(壓提交/rebase 會讓祖先鏈綁定失效);對「新增告警閘用內容指紋不用版本」的描述,對照 `scripts/lumos:20492`(`cmd_lint_waive`)與其 `--waive_key` 用法查證屬實。對 `[[Systems/外部對照-code衍生wiki]]` 的定位描述與該節點原文一致。

〈判定者能不能用:小實驗〉已讀,無 finding。

## F1 派審查員的預設模型與「同家不派外家席」規則在 Codex 編排的專案沒有解法

severity: major
blocking: 是 —— 不改,Codex 編排的消費專案落地這條時會不知道該派哪個模型,要嘛違反「同家」規則派 Opus,要嘛無所適從

引句:「預設 opus;★判定者跟編排會談用同一家模型提供者,不派外家席★(內容只送到會談本來就在用的那一家)。」

1. 這句把兩件事疊在一起卻沒接軌:「預設 opus」是具體模型名(Anthropic 家),「跟編排會談同一家」是家族規則。本 repo 已有的編排家族只有 claude/codex 兩種——file: `scripts/lumos:10354` `LOOP_ORCHESTRATORS = ("claude", "codex")`,且 `cmd_loop_next`(`scripts/lumos:10850`)明文擋下「沒指定 --orchestrator 就不給預設」,理由寫在同一段:file: `scripts/lumos:10852` `工具不預設 claude——Codex 編排時漏了會靜默套錯家族`。這正是本計劃想套用的「同家」邏輯的原型,而原型早就承認「猜家族」這件事本身就是事故來源,才會強制人工每次明講。
2. 本計劃通篇(做法第 2 點、實務隱患〈對外送出〉)只重複「同家、不派外家」這句原則,沒有交代:當編排會談是 codex 家時,「預設」的判定者是哪一個模型?沒有等同 opus 的具名預設,也沒有旗標(如既有 `--orchestrator`)讓 `note-audit prepare`/派工那一步知道現在是哪一家在編排。
3. 具體會撞牆的場景:一個以 Codex 當編排者的消費專案(依附帶參考資料與使用者記憶,這類專案確實存在)跑到「推送前的筆記內容審」,編排會談照這句話的字面「預設 opus」派了一位 Claude Opus 判定者——這正是同一句話後半段禁止的「外家席」;或者編排者發現矛盾、自己找了個 codex 模型頂替,但這個決定沒有任何條款(S1–S15)去驗證派的判定者是不是真的跟編排家族一致,record/check 也不檢查判定者的家族欄位,所以兩種走法都不會被機械擋下,矛盾只會悄悄發生。

## F2 判定者派工詞唯一的可沿用範本(judge_prompt.md)寫死了 rtb 專案的路徑與語言,S14 沒有交代要怎麼套用到別的專案

severity: major
blocking: 是 —— 不改,實作者會把這份寫死路徑與語言的範本直接複製給每個消費專案用,審查員拿到的派工詞會指向不存在的目錄、假設錯的語言

引句:「的分類定義並加上本計劃的四句;改動它要重跑那 68 句的小實驗」

1. 這是條款 [S14] 的內容(緊接在「應沿用 `.../judge_prompt.md`」之後),要求判定者派工詞「沿用」該檔的分類定義。實際讀那支檔:file: `governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md:3` 開頭第一句就是 `The project's code is at /Users/enzo/rtb-mainwt (Python, source under src/rtb/, tests under tests/).`,第 9 行再度把路徑寫死:`For CODE and MIXED you must cite at least one file:line in /Users/enzo/rtb-mainwt`。
2. 整份計劃(做法第 2 點:「派工詞=`judge_prompt.md` 的分類定義,加四句」)與 [S14] 都只講「沿用分類定義」「加四句」,沒有第三句交代「路徑與語言要換成被審那個 repo 自己的」。如果實作者依照字面沿用整份檔案(包含那句寫死路徑的開場白)當作派工詞骨架,對每一個不是 `/Users/enzo/rtb-mainwt` 的專案(包括本 repo 自己,以及消費專案清單裡的 Java/Kotlin/Swift/C#/Dart/Node 各種棧),審查員會被指去讀一個不存在的目錄、且被告知「這是 Python 專案」——這不是臆測,是這份檔案目前逐字的內容。
3. 這一條直接命中「整合/知識同步」鏡頭:12 個消費專案裡只有 rtb 是 Python;其餘按既有補棧紀錄涵蓋 Java、Kotlin、Swift、C#、Dart、Node/Flutter 多種語言,若判定者派工詞的專案路徑與語言段落沒有機制化模板化(例如用被審 repo 的實際根目錄與偵測到的語言取代那兩句),`note-audit prepare` 產出的 `judge_prompt.md` 複本在除了原始實驗以外的地方全部是錯的,而 S14 目前的驗收判準只盯著「48 句小實驗抓到數與誤判數不得變差」,不會測到這個模板替換有沒有做。

## F3 `.lumos/note-audit/<集合指紋>.md` 清單檔沒有對應的 .gitignore 規則,也沒有清掃機制

severity: minor
blocking: 否 —— 不改只會讓 git status 一直出現雜訊檔案、不會讓人做錯決策或做出壞系統

引句:「不進版控);集合指紋=所有(路徑, 行文字)排序後的雜湊,所以兩個會談同時跑不會互蓋、同一批內容重跑得到同一檔」

1. `.lumos/` 目錄在本 repo 不是整批被 忽略——file: `.gitignore:9,30,36` 只個別排除 `.lumos/testmap.json`、`.lumos/test-cache*.json`、`.lumos/lintbase-*/`;`.lumos/config.json`、`.lumos/lint-waivers.json`、`.lumos/lint.json` 都在 `git ls-files` 裡(實跑 `git -C /Users/enzo/harness/lumos-toolchain ls-files .lumos` 查證屬實)。
2. 計劃明講清單檔「不進版控」,但條款(S1–S15)與〈回退〉〈實務隱患〉都沒有一條要求同時在 `.gitignore` 加一行 `.lumos/note-audit/`;照現況實作,這些每次 `prepare` 都會新增的指紋檔會被 git 當成未追蹤檔案列出來,每一次 `git status` 都會看到,長期累積且沒有任何條款提到要清掃舊指紋檔(對照既有 `.lumos/lintbase-*/` 已經有前例被明確排除,這裡漏了同款處理)。
3. 這件事本身不會讓任何人做錯判斷或讓系統壞掉(功能不受影響),所以定為 minor、不擋。

## F4 「decisions 的文字欄」列出的欄位名跟目前 decision-add 實際寫得出來的欄位對不上

severity: minor
blocking: 否 —— 名稱誤植不影響 parse_decisions 的通用鍵值解析,不會讓判定漏掉真實存在的欄位,只是文件寫得不準

引句:「每條的文字欄(content / context / why_chosen / alternatives / trade_offs)」

1. `lumos decision-add` 目前只支援寫入 `content`/`context`/`why_chosen` 三個文字欄(CLI 參數是 `--context`、`--why`)——file: `scripts/lumos:14899-14929`(`cmd_decision_add` 函式簽名與寫入邏輯,只認 `content`/`context`/`why`/`decided`/`valid`)。
2. `alternatives`、`trade_offs` 這兩個欄位名目前在本 repo 從沒被實際使用過:全庫 `grep -rn "alternatives_considered\|trade_off" docs/ scripts/` 只在一處程式註解(`scripts/lumos:4999`,講縮排解析要吃 `alternatives_considered` 這種巢狀清單,不是 `alternatives`)提到過近似名稱,`trade_offs`(或 trade-off 任何寫法)完全沒有出現在任何既有筆記或程式碼裡。
3. 因為 `parse_decisions`(`scripts/lumos:12904`)本身是通用鍵值解析、沒有欄位白名單,實作只要用「掃描每條決策所有字串型子欄位」而不是硬寫這五個名字,就不會漏判;但計劃文字把這五個名字當成完整清單寫出來,容易讓實作者照抄成硬編碼欄位清單,漏掉真實可能出現的 `alternatives_considered` 或任何自訂欄位名。

〈第一層:提交時擋形狀固定的東西〉已讀,除 F 系列外無新 finding——「每支檔有家那套程式檔判定(認得沒有副檔名、開頭是 #! 的主程式)」對照 `scripts/lumos:6176-6210`(`_head_is_shebang`/`_is_code_file`)查證屬實,且該函式確實排除測試檔(`_nodehome_is_test`),與計劃「再把排除掉的測試檔加回來」的描述一致;「不擋 .md」「圍欄一律用既有 `_visible_lines`」查證屬實(`scripts/lumos:3218`);「新分支首推空樹起算會把整庫舊筆記當新增」對照 `scripts/hooks/pre-push:41`(`printf '%s..%s' "$_EMPTY_TREE" "$2"`)查證屬實,與 `_bound_tests_range`(`scripts/lumos:29168-29198`)既有同款分岔點改法一致(計劃沒直接說要重用這支函式,但描述的行為與它一致,不算矛盾)。

〈第二層:推送前的筆記內容審〉除 F1、F2、F3 外無新 finding——「治理帳寫入走 `_jsonl_append_verified` 並拿既有寫入鎖」對照 `scripts/lumos:8187`(`_jsonl_append_verified`)與 `scripts/lumos:9527`/`9604`(`_vault_write_lock` 包住 `_jsonl_append_verified` 呼叫)查證屬實,確有這個既有組合模式;`.lumos/config.json` 沒有全域鍵白名單會拒絕未知頂層鍵(每個功能各自讀自己的區塊,例如 `_lint_load_config`、`_ci_config` 都是各自 try/except 讀取),所以新增 `note_audit` 鍵不會被既有驗證機制擋下。

〈上線前校準〉已讀,無 finding。

〈規範文字跟著改〉已讀,無 finding——`scripts/templates/graph-discipline.md:44` 目前的 FACT/FLOW/DEP 那列文字與 CLAUDE.md 現行版本逐字一致(`diff scripts/templates/graph-discipline.md CLAUDE.md` 只在包裹用的頭尾標記與知識庫路徑變數上有差異),確認範本是唯一來源、目前尚未套用 d3 收窄說法,與計劃描述的「現況」相符。

〈條款 S1–S15〉除已在 F1/F2/F4 指出的部分外,已讀,無新增 finding。

〈回退〉已讀——步驟順序(先手改 CI、消費專案關開關、拿掉 hook 呼叫、治理帳舊筆數留著)內部一致;唯一補充見 F3(回退清單沒提到清 `.lumos/note-audit/` 殘留檔或補 .gitignore,屬同一個洞,不重複開新 finding)。

〈實務隱患〉已讀——「對外送出」段落重複 F1 指出的同一句規則,不重複計分;「資源併發」「可用性」「已排除」三段內部自洽,無新 finding。

〈誠實界線〉已讀,無 finding。

〈審計修正紀錄〉已讀,無 finding(歷史記錄,r1 折入內容與本輪 delta 逐項比對一致)。

---
總結:最嚴重 severity 為 major;blocking 共 2 條(F1、F2)。
