---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-09
aliases:
  - 提問表態閘
  - stack question disposition gate
  - 檢核答案機械化
  - 已滿足或不需要
  - 觸發式適用性
  - 哪些問要答
related:
  - "[[Projects/pitfalls棧別效能追問_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/lumos-refcheck]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/known-pitfall-refresh-token]]"
  - "[[Issues/寫下風險當成處理風險]]"
  - "[[Issues/只退場不痛的機制]]"
  - "[[Issues/code-loop-pass自失效追尾]]"
  - "[[Projects/iOS與Node後端補棧_計劃]]"
  - "[[Systems/finding-refute]]"
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-08 Enzo:「這些提問,實務上 Agent 進入實作時有在證明已滿足或不需要?」)★——查證答案是沒有:三時機(改檔前 hook/推送前 advisory/終審)全是「推到眼前」;唯一義務在 code-loop reference 一句「留痕**建議**含答案」並自註「工具不驗 note 內容、人工紀律」;治理帳 177 筆 code-loop 事件只有 5 筆帶一句答案;spec 端 pitfalls --check 只驗「實務隱患」節存在。=[[Issues/寫下風險當成處理風險]]形狀
  KEY:★第二題併入(Enzo 同晚:「功能如何判斷該問哪些問題,而不是窮舉出來之後每條都要附答案?耗時也耗 token」)★——每題掛穩定 `id` 與 `when` 觸發 regex,對「這次改動的內容」(推送前=diff 增刪行;改檔前=hook 手上的編輯內容)剝字串與註解後比對,命中才適用;未觸發由工具自動記 na(零 token);某棧改動行數超門檻則全問。世界解=CodeRabbit path_instructions/Danger 條件式留言/已知坑 pitfall_when 同型,Checklist Manifesto 5–9 殺手項,Meta 預測式測試選擇「按改動特徵選、用歷史量 recall」——借觸發與量 recall,不借 ML
  KEY:★裁定=借設計審處置閘+已知坑內容觸發,零新機制類型★——diff 有適用題時,推送前每一問要有機器可讀表態:satisfied(附證據 path:line 或 test:名)/na(理由)/todo(連 Issue+理由);閘條件「有適用題就擋,不看 tier」(r1 邊界席 B1:tier 由 Python 形狀 regex 算,kt/swift/vue 幾乎永遠 standard);supersede 2026-07-20「standard 不擋」(先 decision-add 再 supersede,r2 接手席 H4)
  KEY:★r1/r2 折入的核心形狀★——表態是獨立原語 `code-loop dispositions <檔>`(派席前寫;先寫治理帳事件、失敗 rc2 不寫 marker,再原子寫 marker;事件與 marker 都帶 branch/head_sha/ts);pass/skip 簽章不變、skip 一樣要先表態;check 對「該分支最後一筆 pass/skip」與「該分支最後一筆 dispositions」分別重建、各自套同一套 sha/祖先/簿記豁免規則;改碼後表態過期要重表態(樣板 --carry 帶舊答案);新 kind 登記進 LOOP_NOT_CLOSE_EVENTS(r2 接手席 H1)
  KEY:機械錨點只抓最懶的謊,一律對被推送 commit 的 git 樹驗(不再要求工作樹乾淨,r2 三席一致):path:line=`git cat-file -e`+`git show` 行數;test:=工作樹 discovery(profile 語意)∧ `git grep -F` 在 at_sha 樹的該平台 root 命中(未追蹤/未提交的測試自然不在樹);todo=`git ls-tree` 解析 `*-knowledge` slug 後 cat-file(glob 不展開,r2 正確性席 C4)且 status open/doing;理由門檻=去空白與標點後 CJK ≥10 字或總長 ≥25 字(r2 邊界席 B10)
  KEY:副產品=每題(以 id 為鍵)歷來 satisfied/na/todo/auto-na 比例進 gov --stats(mapper 白名單放行新欄);死題候選(≥10 次人工表態且 100% na)與觸發太窄候選(recall-miss ≥3)
  KEY:天花板(向人複述):表態可以敷衍,錨點與審查席只降機率不是證明——同設計審處置閘承認的 GIGO(垃圾進垃圾出:表態寫什麼工具就記什麼);閘內部錯誤或超預算走既有 `_gate_failopen`(治理帳 kind=fail-open);tag 推送沿既有 advisory 不擋(r2 外家 F7);不做 LLM 判答案、不做 LLM 前置分類
  PRIOR-ART:①最小解在既有機制層——處置閘(每條 finding 折掉或附理由接受,機械數)已是設計審與代碼審的收斂判準,本案只是把「發現」換成「提問」;觸發借已知坑節點的 `pitfall_when: content:<regex>`、`_PITFALL_DIFF_PATTERNS`(含剝字串字面與跳過註解行)與 hook 的 `extract_delta_query`;錨點借 refcheck 存在性、`_platform_test_index`、`resolve_test_refs`、dispatch-lens 的 `*-knowledge` slug 解析;留痕借 code-loop 留痕座標與治理帳事件;設定讀法借 `_ci_config`/`load_test_profile` 的 `Path(repo_root)/.lumos/config.json` 直讀(vault-free,r2 架構對齊席 A4) ②世界解:CodeRabbit path_instructions(docs.coderabbit.ai/guides/review-instructions)、Danger.js 條件式規則、reviewdog 只對改到的行出聲、Checklist Manifesto 5–9 殺手項、Meta Predictive Test Selection(arXiv 1810.05286)、Meta RADAR 2026(列未來層);PR template checkbox 普遍但不擋,真的擋的是「all review threads resolved 才准 merge」政策(`governance/review-reports/world-benchmark-2026-08-26.md` 已引);Vercel 實證靠模型自覺 56% 跳過 ③裁定=借用既有設計(家規三選一裡的 borrow-design),不加依賴
  DEP:scripts/lumos(_STACK_PERF_QUESTIONS 形狀與 _compile_stack_triggers、_stack_applicability、_pitfall_diff_collect、_stack_key_for_file、cmd_pitfalls --dispositions-template、cmd_impact --file 的 stack_questions_applicable、cmd_code_loop dispositions/check/recall-miss、_codeloop_guard_verdict、_codeloop_read_from_ledger、_codeloop_gov_log、_codeloop_write、LOOP_NOT_CLOSE_EVENTS、_validate_repo_ref、_platform_test_index、resolve_test_refs、cmd_dispatch_lens 與 _lens_cache_path、cmd_gov load mapper 與 _render_gov_stats、_stack_questions_config)｜scripts/hooks/claude/impact-hook.py(只格式化,讀 stack_questions_applicable)｜scripts/hooks/pre-push(表態閘獨立步驟+逃生文字)｜.github/workflows/ci.yml(錯誤訊息)｜skills/lumos-code-loop SKILL.md 步驟 1 後+reference.md 棧別段｜commands/02 pitfalls 列+commands/06｜ARCHITECTURE.md 第 4 節流程圖標籤｜Systems/pitfalls-code-loop FLOW 行｜Systems/效能檢核目錄 KEY 行③與第 142 行表格｜Projects/pitfalls棧別效能追問_計劃 決策
---
# 棧別提問表態閘（2026-09-08 立案；2026-09-09 r3 修訂稿——折入 r1 34 條 + r2 46 條）

> 白話：工具會在改檔前、推送前、終審時把「這個技術棧該問自己的效能問題」推到 agent 眼前，但推到眼前之後沒有任何機制要求它回答。這篇做兩件事：**（一）命中的每一問，推送前要留下一個機器讀得懂的交代**——做到了（附證據）、不適用（附理由）、還沒做（連到待辦）——缺一問就不准推；**（二）「命中」不是整棧全問，而是靠改動內容觸發**——沒碰到的題由工具自動記「未觸發」，零 token。做法全借既有機制：設計審的處置閘、已知坑的內容觸發、refcheck 的存在性核對、code-loop 的留痕座標。

## 現況查證（2026-09-08，全部實查；r1 正確性席訂正數字）

- 三個時機的實際效果都是「保證被看見」：hook 注入純提醒；推送前的 advisory 分支只印問題；終審蓋章把 note 原樣寫入。
- 唯一寫了義務的地方是代碼審 skill 的參考文件：「終審留痕**建議**含對應檢核問題的答案」，同一句自註「工具不驗 note 內容、人工紀律」。
- 治理帳裡 code-loop 的 pass／skip 事件 177 筆，其中 5 筆的 note 帶了一句檢核答案，其餘沒有。
- 設計端同形：`pitfalls --check` 只驗「## 實務隱患」節存在，段落寫「無」也過。
- 風險分級的來源跟棧命中無關：tier 由一組 Python 形狀的 regex 算，Compose／協程／SwiftUI／Vue 的典型改動幾乎不會命中，所以 kt／swift／vue 的 diff 幾乎永遠是 standard（r1 邊界席 B1）。
- pre-push 現在是「tier=high 才呼叫 check、否則 elif 印棧問題」的互斥結構（r2 正確性席 C1／邊界席 B8）；CI 的 workflow 無條件呼叫 check，但擋下訊息寫死「tier=high」（r2 正確性席 C2）。

## 設計

### 一、哪些問要答：觸發式適用性

- **題表形狀**：`_STACK_PERF_QUESTIONS` 每題從字串改成 `{"id": 穩定代號, "q": 原文, "when": [regex, …]}`。`id` 是短 slug（例 `kt-compose`），改措辭不改 id、改語意才換 id；表態與統計都以 id 為鍵（r2 接手席 H6／外家 F5：既防換序套錯題，又不因措辭微調擋在途分支）。regex 在模組載入時一次編譯（壞 regex＝啟動即錯，測試釘；r2 外家 F9）；`when` 為空的題測試翻紅（r2 邊界席 B13）。
- **比對母體與正規化**：對「改動內容的每一行」跑 `when`，不分大小寫；先剝字串字面、跳過註解開頭行（`#`／`//`／`--`／`/*`／`*`），跟 `_PITFALL_DIFF_PATTERNS` 同一套正規化（r2 架構對齊席 A5／邊界席 B15）。推送前的母體＝diff 的**增行與刪行**（刪掉 CancellationToken／timeout／key 也要觸發；r2 外家 F5／正確性席 C9），測試檔排除同既有規則。改檔前的母體＝hook 手上的編輯內容（Write 全文、Edit 的 old_string＋new_string，即既有 `extract_delta_query` 那份；r2 邊界席 B1／接手席 H3），**不是磁碟上的檔案內容**。兩個母體天生不同（提醒 vs 判定），spec 只宣稱「同一組 when、同一套正規化」，不宣稱結果相同（r2 外家 F4）。
- **誰算**：一律 lumos 算——`pitfalls --diff --json` 與 `impact --file --json` 各自產出 `stack_questions_applicable`；hook 只格式化（r2 架構對齊席 A1／正確性席 C7，同既有單源慣例）。
- **輸出形狀**：`stack_questions` 保持既有語意（命中棧的整組題，`{棧: [題…]}`），不改；新增 `stack_questions_applicable`（`{棧: [題…]}`，只列適用題）與 `stack_questions_meta`（`{棧: [{id, question, applicable, triggered_by}]}`，全表）。hook 與 pre-push 有 applicable 就用 applicable（r2 架構對齊席 A2／外家 F6）；既有數量守衛測試不動（r2 正確性席 C8／接手席 H5）。
- **棧判定補一刀**：`.ts`／`.js` 在 package.json 判為前端時歸 `vue` 棧（原本回 None＝零覆蓋零稽核；r2 邊界席 B4），後端歸 `node`，沒 package.json 維持舊行為。
- **大改動全問**：同一棧在這次 diff 裡所有檔案的**增刪行加總** > 門檻 → 該棧全表適用（r2 邊界席 B5）。門檻讀 `.lumos/config.json` 的 `stack_questions.ask_all_over_lines`，預設 300；不是正整數（0、負數、字串）→ 用預設並印一行「設定檔的 ask_all_over_lines 不合法，已用 300」（r2 邊界席 B6）。
- **未觸發題**：樣板自動填 `{"status":"na","reason":"未觸發:<regex 清單>","auto":true}`；check 重算適用性，適用題若 `auto:true` → BLOCKED（工具判適用但沒人答）。
- **recall 帳**：審查席若抓到「對得上某未觸發題」的問題，`lumos code-loop recall-miss <id> --note "<一句>"` 寫一筆治理帳事件；同一題累積 3 次印「觸發太窄候選」。
- **效能預算**（r2 外家 F9）：改檔前的 delta 掃描上限 2 MB（超過只掃前 2 MB 並註記）；推送前的表態核對整段有時間預算（同派工鏡頭 `_LENS_SPEC_BUDGET` 慣例，預設 20 秒），超時走既有 fail-open 進治理帳。

### 二、表態的形狀

- 一份 JSON **檔案**，以裸位置參數傳入（`lumos code-loop dispositions <檔.json>`，同 `refcheck <md>`／`lint-md <path>`「這個檔就是操作主體」的慣例；r2 架構對齊席 A3 裁定，取代 r1 H9 的旗標說法），鍵＝題目 `id`，值＝`{status, question, evidence|reason|issue, auto?}`。`question` 存原文供人讀；check 以 id 對照，原文不同只印「題目措辭已改，重看一眼」不擋。
- `status` 三值只認小寫 `satisfied`／`na`／`todo`，大小寫不對的錯誤訊息明講「只認小寫」。`satisfied` 必附 `evidence`：`path:line` 或 `test:<名>`／`test:<平台>:<名>`；`na` 必附 `reason`；`todo` 必附 `issue`（`Issues/<名>`）與 `reason`。
- 理由門檻（r2 邊界席 B10）：去掉空白與標點後，CJK 字元 ≥10 個，或總字元 ≥25 個；標點不算 CJK，所以加一個句號繞不過。
- `path:line` 切分：最後一個冒號之後是行號（純數字或 `a-b`），之前是 repo 相對 POSIX 路徑；反斜線先正規化成 `/`；絕對路徑與含 `..` 一律拒收並明講原因。
- `test:` 切分：借 `resolve_test_refs` 的規則（含冒號＝平台前綴、裸名歸 default_platform；r2 架構對齊席 A6）；legacy 單平台設定卻帶平台前綴 → 明講「這個專案沒開多平台，不支援平台前綴」而不是「找不到」（r2 邊界席 B11）。
- 樣板：`lumos pitfalls --diff <範圍> --dispositions-template [--carry]` 印出 JSON（適用題 status 留空、未觸發題自動 na）；`--carry` 從該分支最後一筆表態記錄把「id 相同且仍適用」的舊答案帶過來（改碼後重表態的成本降到只答新題；r2 正確性席 C6）；零命中印 `{}` 並在 stderr 說明；`gate=off` 時同樣印 `{}`（r2 邊界席 B7）。

### 三、表態何時寫、閘放哪裡

- **寫側原語 `lumos code-loop dispositions <檔.json>`**：驗形狀（三值、必附欄、question 非空、理由門檻、evidence 切分）；壞 → rc2 不寫並講原因。好 → **先追加治理帳事件**（追加失敗 → rc2、不寫 marker、明講「治理帳寫不進去」；r2 外家 F2），事件形狀 `{"ts","gate":"code-loop","kind":"dispositions","branch","head_sha","commit","dispositions":{…}}`（跟讀側 `ev.get("branch")==branch` 與 `head_sha` 配對；r2 正確性席 C3／接手席 H2／邊界席 B3）；**再原子寫 marker** `governance/code-loop/<branch>.dispositions.json`（暫存＋`os.replace`），marker 同樣帶 `head_sha`／`branch`／`ts`。**在派審查員之前做**（code-loop 步驟 1 算完 pitfalls 就填），派工鏡頭附得到、審查席反駁得到。`gate=off` 時寫入照常允許、不強制。
- **新 kind 登記**：`("code-loop","dispositions")` 與 `("code-loop","recall-miss")` 加進 `LOOP_NOT_CLOSE_EVENTS`（不是關門事件；r2 接手席 H1，否則 `t_loop_close_kinds_classified` 掃真帳翻紅）。
- **`pass`／`skip` 簽章不變**，`skip` 一樣要先表態；pre-push 印的逃生路徑加一句「先 `lumos code-loop dispositions <檔>`」。
- **座標與過期**（r2 正確性席 C6）：表態綁寫入當下的 head_sha；有效性規則跟 pass 留痕**同一套**——目標 sha 等於表態 sha、或表態 sha 是目標 sha 的祖先且中間只動簿記檔（`governance/code-loop/` 整目錄在簿記白名單，含新 marker；r1 接手席 H8）。**改了碼就要重表態**（用 `--carry` 只答新題），這是刻意的：表態是對「這份改動」的陳述。
- **讀側**（r2 外家 F1／邊界席 B9）：`_codeloop_read_from_ledger` 改成按 kind 分別重建——「該分支最後一筆 pass/skip」與「該分支最後一筆 dispositions」各取檔案行序的最後一筆（不是 ts；r2 外家 F8）；同 sha 重複事件後者覆蓋。本機有 marker 讀 marker，沒有才退治理帳，跟 pass 相同。
- **閘條件：diff 有適用題就擋，不看 tier**（r1 邊界席 B1；`.lumos/config.json` 的 `stack_questions.gate` 可設 `all`（預設）／`high-only`／`off`，值不合法 → 用 `all` 並印一行）。設定檔一律 `Path(repo_root)/.lumos/config.json` 直讀，不走載 vault 的 helper（r2 架構對齊席 A4）。這一條 supersede 2026-07-20「standard 只提醒不擋」的裁定：該節點沒有 `decisions:` 欄，先 `decision-add` 把當年裁定補成一條、再 `decision-supersede` 指向本案（r2 接手席 H4）。
- **閘放哪裡**（r2 正確性席 C1／邊界席 B8）：表態核對放在 `code-loop check` 裡，跟「tier high 缺留痕」是**兩個獨立判定**、各自出各自的三段式訊息（缺表態≠缺審查，不混用「先跑一輪代碼審」那句）；pre-push 對每個分支 ref **無條件**呼叫 check（拆掉 tier=high 才呼叫的 if／elif），rc1 的原因由 check 印；tag 等非分支 ref 維持既有 advisory（r2 外家 F7）。CI 的 workflow 已無條件呼叫 check，只改錯誤訊息不再寫死 tier=high（r2 正確性席 C2）。
- **BLOCKED 訊息**：三段式，最多列 10 問，其餘一句「另有 N 問，全量看 `lumos code-loop check --diff <範圍> --json`」（r2 邊界席 B12）；沒有適用題 → 不多印一個字。
- **沒有 `docs/` 目錄的專案**：治理帳寫不進去（既有行為）→ `dispositions` 直接 rc2 明講「這個專案沒有 docs/，表態進不了治理帳、CI 端讀不到」（跟 pass 留痕今天的限制相同）。
- **`.lumos/config.json` 壞掉時**：`test:` 證據一律判「無法驗證：設定檔解析失敗」→ BLOCKED 並印修法，不拿 csharp 預設 profile 去比。
- 閘內部錯誤或超預算 → 走既有 `_gate_failopen`，治理帳 kind 為 `fail-open`。
- 誤擋時怎麼退：修表態重跑 check；真的要硬推走既有 `--no-verify`（本機不留痕、CI 標紅），同其他閘。

### 四、錨點怎麼驗（只抓最懶的謊；一律對「被推送的 commit」的 git 樹驗，不要求工作樹乾淨——r2 三席一致）

- `path:line`：`git cat-file -e <at_sha>:<path>` 存在、`git show <at_sha>:<path> | wc -l` 涵蓋該行（不驗內容）。沒有 at_sha（本機直接叫 check）退回工作樹（借 `_validate_repo_ref`）。
- `test:<名>`／`test:<平台>:<名>`：兩道都要過——①工作樹 discovery（`_platform_test_index`，profile 語意、多平台感知）名字在集合裡；②`git grep -F -q -- "<名>" <at_sha> -- <該平台 root>` 在被推送的樹命中（限該 profile 的測試副檔名）。未追蹤、未提交的測試檔自然過不了②（r2 外家 F3），而工作樹有其他 WIP 檔完全無妨（r2 正確性席 C5／邊界席 B2）。
- `Issues/<名>`：先 `git ls-tree --name-only <at_sha> docs/` 解析出 `*-knowledge` 的實際 slug（同 dispatch-lens 既有做法；`git cat-file` 不展開 glob，r2 正確性席 C4），再 `git cat-file -e <at_sha>:docs/<slug>-knowledge/Issues/<名>.md`，且 `git show` 出來的開頭 `status:` 是 open／doing（純文字讀，不載入圖譜）。
- 答對答錯不驗：留給審查席。派工鏡頭 diff 模式讀表態記錄附進派工單；快取 key 加表態記錄的 sha256。

### 五、副產品：哪些題在空轉

- `gov --stats` 多一段：按題目 `id` 彙總歷來 satisfied／na／todo／auto-na 次數；某題 ≥10 次人工表態且 100% na → 印「死題候選」；`recall-miss` 累積 ≥3 → 印「觸發太窄候選」。治理帳讀側的 mapper 白名單放行 `dispositions`、`recall_miss` 欄。

## 驗收條款

- [S1] `lumos pitfalls --diff <範圍> --dispositions-template [--carry]`：適用題留空 status、未觸發題自動 na（含 `auto:true` 與觸發清單）、含 id 與原文；`--carry` 帶入該分支最後一筆表態中 id 相同且仍適用的舊答案；零命中或 `gate=off` 印 `{}`；某棧增刪行加總 > 門檻時該棧全表適用；門檻不合法時用預設並印一行 [test:t_dispositions_template]
- [S2] `_STACK_PERF_QUESTIONS` 每題有唯一 `id` 與非空 `when`（模組載入時編譯；空 when 或壞 regex 測試翻紅）；`pitfalls --diff --json` 的 `stack_questions` 語意不變、新增 `stack_questions_applicable` 與 `stack_questions_meta`；比對對增行與刪行、剝字串、跳註解行；每棧至少一題有「命中樣本／不命中樣本／註解假命中」測試；前端 .ts 歸 vue 棧 [test:t_stack_question_triggers]
- [S3] `impact --file --json` 依 stdin 的編輯內容（Write 全文／Edit old+new）產 `stack_questions_applicable`；hook 只格式化，有 applicable 就只印 applicable；零命中不注入棧段；delta 超過 2 MB 只掃前 2 MB 並註記 [test:t_impact_hook_stack_questions_filtered]
- [S4] `code-loop dispositions <檔>`：形狀壞（未知或大小寫錯的 status、缺必附欄、question 空、理由不到門檻、evidence 切分失敗、legacy 帶平台前綴）rc2 不寫並講原因；好 → 先寫治理帳事件（含 branch/head_sha/commit/ts）再原子寫 marker；治理帳寫不進去 rc2 不寫 marker；沒有 docs/ 明講 [test:t_codeloop_dispositions_write]
- [S5] `code-loop check`（有適用題，不看 tier）：缺 id、適用題卻 `auto:true`、`satisfied` 的 path:line 在 at_sha 樹不存在、`test:` 名在該平台索引掃不到或在 at_sha 樹 git grep 不到、`todo` 的 Issue 在 at_sha 樹不存在或非 open/doing → 各自 BLOCKED 並列出該問（最多 10，附全量指令）；全部合法 → 照舊；skip 留痕一樣要表態；`gate=off` 不擋、`high-only` 只在 tier high 擋；工作樹有其他未提交檔不影響；表態核對超預算走 fail-open 進治理帳 [test:t_codeloop_check_dispositions_gate]
- [S6] 讀側：marker 不在時 `_codeloop_read_from_ledger` 按 kind 各取該分支檔案行序最後一筆重建（pass/skip 與 dispositions 互不擠掉）；簿記豁免（祖先 sha 之後只動簿記檔）下 check 仍認得表態；改碼後表態過期 → BLOCKED 訊息指向 `--carry` 重表態；新 kind 在 LOOP_NOT_CLOSE_EVENTS（`t_loop_close_kinds_classified` 不翻紅）；config 壞掉時 `test:` 證據 BLOCKED 並說明是設定檔問題 [test:t_codeloop_dispositions_ledger_fallback]
- [S7] pre-push：對每個分支 ref 無條件呼叫 `code-loop check`（拆 if/elif），缺表態與缺審查各自出各自的訊息；逃生路徑文字加「先表態」；tag 維持 advisory；ci.yml 錯誤訊息不寫死 tier=high [manual:對 kt 樣本 diff（有適用題、tier standard）與純 python diff（零適用）各跑一次 scripts/hooks/pre-push 看輸出與 rc]
- [S8] 派工鏡頭 diff 模式附表態記錄（有才附），快取 key 含表態記錄 sha256 [test:t_dispatch_lens_includes_dispositions]
- [S9] `gov --stats` 多一段按 id 彙總四值，死題候選與觸發太窄候選；mapper 放行新欄；`code-loop recall-miss <id> --note` 寫事件 [test:t_gov_stats_dispositions]
- [S10] 文件：code-loop SKILL 步驟 1 之後加「表態」步驟；reference.md 棧別段改成「有適用題：check 會擋；tier 不再是條件」；commands/06 加一列；commands/02 的 pitfalls 列改掉「tier:high 才觸發」；ARCHITECTURE.md 第 4 節流程圖 `(tier=high)` 標籤改成「留痕／表態」；Systems/pitfalls-code-loop FLOW 行的三分支改寫；效能檢核目錄 KEY 行③與第 142 行表格改成「適用題」；pitfalls棧別效能追問_計劃 先 decision-add 再 decision-supersede [manual:讀改後的八份文字對照本節]

## 實務隱患

- **守衛面**：本案改 pre-push／CI 的擋法，而且擋的範圍比原設計寬（不看 tier）。已排除誤擋的來源：①適用性讓沒碰到的題不用答；②閘內部錯誤或超預算走既有 fail-open 進治理帳；③CI 讀治理帳重建，跟 pass 留痕同一條路（本來就要「pass 後提交帳本再推」，表態事件走同一流程）；④錨點對被推送 commit 的 git 樹驗，工作樹有 WIP 完全無妨；⑤設定檔壞掉或值不合法明講是設定檔；⑥消費專案可用 `stack_questions.gate` 過渡；⑦tag 推送沿既有 advisory，不在「不准推」的範圍內。
- **併發**：同 sha 兩次 `dispositions` 寫入＝治理帳兩筆、marker 原子覆寫；讀側取檔案行序最後一筆；不加跨程序鎖（同 pass 留痕既有限制），加一條兩程序交錯寫入的測試釘行為。pre-push 與 CI 同時跑 check 只讀不寫。
- **效能**：表態核對有時間預算；delta 掃描有大小上限；多平台索引仍是單次 CLI 內惰性快取（既有）。
- **不可逆**：無——marker 與治理帳都是可 git 還原的簿記。
- **對外送出／金流**：無。
- **既有 pass 記錄**：沒有表態記錄的舊 sha，只在「當前 diff 有適用題」時才被要求。
- **本 repo 自己**：Python 不在棧問題表，這道閘對 scripts/lumos 的改動不會觸發（r1 邊界席 B10，另案）。
- **題目換 id**：改語意才換 id，換了在途分支要重表態——這是刻意的，跟改碼過期同一條規則。

## 刻意不做

- 不用 LLM 判答案對錯，也不用 LLM 前置分類決定適用性（RADAR 型；花 token，跟動機相反）——等 auto-na 比例與 recall-miss 帳告訴我們 regex 不夠再開。
- 不做設計端（spec）的逐問表態——`pitfalls --check` 的節存在性檢查另案。
- 不做路徑 glob 觸發（棧靠副檔名／package.json 認；glob 留給消費專案 config 覆寫，未來）。
- 不加 Python 題組（B10，另案）。
- 不處理分支名扁平化撞名（r2 邊界席 B14，既有風險原樣繼承）。
- 不擋 tag 推送（r2 外家 F7）。

## 審計修正紀錄

- r1（2026-09-08，5 席：正確性／邊界／接手／架構對齊／外家 Codex）：34 條（blocker 5 全折）；折入：表態改成獨立原語在派席前寫、閘不看 tier、CI 從治理帳重建、錨點對 at_sha 驗、多平台索引、原文對照、原子寫入、鏡頭快取 key、gov mapper 放行、fail-open kind、S7 保留 standard 語意、todo 門檻、理由門檻分 ASCII、path:line 切分、status 小寫訊息、零命中印 `{}`、BLOCKED 截斷、docs/ 缺席訊息、config 壞掉判法、效能檢核目錄 KEY 行、旗標吃路徑；數字訂正 0→5/177。卷證 `governance/review-reports/棧別提問表態閘/r1-*`。
- r2（2026-09-09 凌晨，同 5 席，修訂稿驗收）：46 條（外家 9／正確性 9／接手 7／邊界 15／架構對齊 6；blocker 12 全折）；折入：治理帳事件帶 branch/head_sha 並先寫帳再寫 marker、讀側按 kind 各取最後一筆、新 kind 登記 LOOP_NOT_CLOSE_EVENTS、pre-push 拆 if/elif 改無條件呼叫 check 且缺表態≠缺審查、ci.yml 訊息、hook 用編輯內容且由 lumos 算 hook 只格式化、比對對增刪行並剝字串跳註解、`stack_questions` 語意不變另加 applicable/meta、前端 .ts 歸 vue、門檻為該棧增刪行加總且值域驗證、`gate=off` 語意、theory 門檻改 CJK 計數、test: 證據改 git grep 對樹不要求工作樹乾淨、Issues 先解析 slug、legacy 平台前綴訊息、題目改穩定 id、`--carry` 重表態、config 直讀 repo_root、裸位置參數、effect 預算、tag 不擋、八份文件補列、decision-add 前置。卷證 `governance/review-reports/棧別提問表態閘/r2-*`。

REVISIT:2026-10-09 看留痕帳裡 satisfied/na/todo/auto-na 的分布：人工表態 na 佔比 >70% 代表被敷衍或題目不對，回頭裁「加嚴」還是「刪題」；auto-na >90% 且 recall-miss 有帳代表觸發太窄，修 when；同時看有沒有 `--no-verify` 因表態閘而增加（治理帳 bypass 事件對比 9 月前）。
