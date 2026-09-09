---
type: project
status: doing
created: 2026-09-09
updated: 2026-09-09
aliases:
  - 張力表態
  - tension disposition
  - 架構對齊席與檢核題衝突的解法
  - 兩席相反
  - 可能撞候選
related:
  - "[[Issues/架構對齊席與棧別檢核題可能相反]]"
  - "[[Systems/arch-alignment-lens]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Projects/棧別提問表態閘_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/finding-refute]]"
  - "[[Systems/pitfalls-code-loop]]"
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-09 Enzo:「遵循既有架構的鏡頭、和棧別技術提問的衝突,我想開始解」)★——[[Issues/架構對齊席與棧別檢核題可能相反]] d2 裁「兩席相反時不挑一邊,端出警告:既有寫法 X/隱患 Y/建議 Z/跟既有 N 檔不一致,人裁」;本案把那條口徑落成機制。查證:衝突今天從兩個洞漏掉——①答題只有 satisfied/na/todo 三種,「看到題目但刻意沿用既有寫法」只能塞進 na(正是裁定禁止的壓掉)②沒有任何東西告訴人「這個檔用了鄰居都沒用的做法」,架構對齊席拿到的只是三個對照檔路徑
  KEY:★裁定(Enzo 2026-09-09,d1)三塊都做★——(一)第四種表態 `tension`:必填 chosen(existing|suggested)/existing(對照檔 path:line 清單,對被推送的樹驗存在)/hazard/suggestion(同 na 理由門檻);選 suggested 要附 evidence path:line;合法的 tension 不擋,check 印成 ⚠ 警告(stderr、rc 不變),進治理帳可數 (二)pitfalls --diff 端出候選:改動檔的增行命中某題觸發字、同層對照檔一個都沒有那個字 → 印「可能撞」並在表態樣板該題帶 hint;只端候選不判 (三)口徑:架構對齊席派工詞(templates §7.6)遇 tension 只查三欄真假不重裁;code-loop skill 步驟 1 講何時用 tension;兩席發現都留、處置理由指向那則表態
  KEY:天花板(向人複述):tension 跟 na 一樣可以敷衍——工具只驗對照檔存在與文字長度,隱患真不真、建議對不對留給審查席反駁;候選只抓「新檔引入鄰居沒有的做法」這個方向,反方向「照舊寫法沒採建議」機械抓不到,只能靠 tension 這個誠實選項;觸發字寬(如 \bContext\b)會有假候選,REVISIT 數
  KEY:帳上現況(2026-09-09 機械數,標記在正文):表態事件 0 筆(本 repo 是 Python 不在題表,閘 9/9 才上)、代碼審留痕提到架構對齊 19 筆、同時提到檢核題 0 筆——零真實案例,本案是先把接住的地方做好
  PRIOR-ART:①最小解在既有機制層——表態閘已有「每題一個機器可讀交代」的形狀,本案只加第四種值與幾個必填欄;候選借 _arch_alignment_hints 的對照組與 _STACK_TRIGGERS 的觸發字,零新機制類型 ②世界解(2026-09-09 派乾淨席網搜):Google eng-practices 把「跟現有一致」列為最後一階、且以「不惡化 code health」封頂(=被作廢的 d1 那條,人裁不採);CodeRabbit learnings 是設定覆寫、不偵測衝突;arXiv 2608.18167 Adversarial Review 把席間分歧分成 evidence-backed/concern-based 逼出證據(同 [[Systems/finding-refute]] 的方向);「分歧就交人、不自裁」在 ML 叫 reject option/selective prediction(Chow's rule),沒人搬進 code review 工具;linter 側「明知故留要附理由」只有 eslint-comments require-description(機械要求自由文字)與 GitHub code scanning dismissal(下拉類別必選)真的擋——本案 tension=類別(chosen)+結構化理由(三欄),比兩者都嚴一點 ③裁定=借用既有設計,不加依賴
  DEP:scripts/lumos(_DISP_STATUSES、_dispositions_validate、_dispositions_verdict、_dispositions_template、_lens_dispositions_lines、_pitfall_diff_collect、_arch_alignment_hints、_STACK_TRIGGERS、_stack_norm_line、cmd_code_loop check 印法、_render_gov_stats 表態段)｜skills/lumos-design-loop/templates.md §7.6｜skills/lumos-code-loop SKILL.md 步驟 1/6/7 + reference.md 棧別段｜skills/lumos-project-notes/commands/06｜Systems/棧別提問表態閘 表格｜Systems/效能檢核目錄 第 145 行｜Systems/arch-alignment-lens｜Issues/架構對齊席與棧別檢核題可能相反 REVISIT
decisions:
  - content: 三塊都做:第四種表態 tension、pitfalls 端出候選、派工詞口徑
    id: d1
    context: 事故筆記 d2 只寫口徑不加機制、並寫「沒有實例不據此加機制」;Enzo 2026-09-09 說要開始解,AI 攤三個範圍(全做/不做候選/只口徑),Enzo 選全做
    why_chosen: 口徑靠人記得,正是裁定說最不喜歡的;沒有記錄的地方,11 月的回頭條件就沒數字可看;候選是唯一不靠人記得的提醒。代價=一個閘多一種值、pitfalls 多讀最多三個對照檔
    decided: 2026-09-09
    valid: true
---
# 兩席相反時端出張力（2026-09-09 立案）

> 白話：兩個審查角度天生會吵——一個說「照這個專案原本的寫法寫」，另一個說「這裡該用比較好的做法」。
> 人已經裁了：撞到時不挑邊，把兩邊都端到人面前（既有怎麼寫、隱患是什麼、建議怎麼改、改了會跟幾個檔不一致）。
> 這篇做的是讓「端上來」不靠人記得：答題時多一個誠實的選項、改動前就有人提醒可能撞、審查席知道撞到時查什麼。

## 現況查證（2026-09-09，全部機械數）

- 兩席還沒撞過：治理帳的表態事件 0 筆 <!--lumos:count=0 re="kind": "dispositions" in=docs/.governance-log.jsonl-->（表態閘 9 月 9 日才上；本 repo 是 Python，不在題表，這裡永遠不會觸發）。
- 代碼審留痕（pass／skip）182 筆 <!--lumos:count=182 re="gate": "code-loop", "kind": "(?:passed|skipped)" in=docs/.governance-log.jsonl-->，提到架構對齊席的 19 筆 <!--lumos:count=19 re="gate": "code-loop", "kind": "(?:passed|skipped)"[^\n]*架構對齊 in=docs/.governance-log.jsonl-->，同時提到檢核題或棧別的 0 筆 <!--lumos:count=0 re="gate": "code-loop", "kind": "(?:passed|skipped)"[^\n]*架構對齊[^\n]*(?:檢核|棧別) in=docs/.governance-log.jsonl-->。
- 所以這不是修事故，是先把接住的地方做好。事故筆記原本寫「沒有實例不據此加機制」，Enzo 2026-09-09 裁三塊都做（d1），那句作廢。

### 衝突今天從哪兩個洞漏掉

1. **答題那一側沒有誠實的選項。** 表態只認 `satisfied`／`na`／`todo`（`_DISP_STATUSES`）。「我看到這題，但刻意沿用專案既有寫法、沒採建議」哪一種都不是，最後被塞進 `na`——工具只驗理由長度，正是裁定禁止的「默默壓掉」。
2. **沒有任何東西會說「這個檔用了鄰居都沒用的做法」。** `_arch_alignment_hints` 只把同層最像的三個既有檔路徑端給架構對齊席；有沒有看出差異全靠那一席，編排者要不要把兩邊併起來講全靠當下記得。

## 設計

### 一、第四種表態 `tension`（張力）

- **形狀**：`{"status":"tension","question":原文,"chosen":"existing"|"suggested","existing":["path:line",…],"hazard":"…","suggestion":"…","evidence":"path:line"}`。`chosen` 講這次改動選了哪邊：`existing`＝沿用既有寫法（隱患留著）、`suggested`＝改用建議做法（跟既有不一致）。`existing` 是既有寫法的位置，一項一個 `path:line`，去重後的路徑數就是「跟既有 N 個檔不一致」的 N。`evidence` 只在 `chosen=suggested` 時必附，指到這份改動裡採新做法的那一行。
- **寫側**（`_dispositions_validate`）：`status` 四值只認小寫，錯誤訊息改成「只認小寫 satisfied/na/todo/tension」；`tension` 缺 `chosen` 或值不在兩者 → 錯；`existing` 要是非空清單，每項用既有 `_dispositions_split_path_line` 切得開（絕對路徑、`..`、缺行號照舊拒收）；`hazard`／`suggestion` 各自過既有 `_dispositions_reason_ok`（去空白標點後 CJK ≥10 或總長 ≥25）；`chosen=suggested` 時 `evidence` 必附且切得開。壞 → rc2 不寫並講原因，跟其他三值同一條路。
- **讀側**（`_dispositions_verdict` 的 `_one`）：`tension` → 每個 `existing` 走既有 `_dispositions_check_path_line`（對被推送 sha 的樹驗存在與行號範圍，不驗內容）；`chosen=suggested` 的 `evidence` 同驗；文字門檻與 `chosen` 值再驗一次（治理帳重建來的紀錄不信形狀：缺欄一律 `str(… or "")` 接住，同 `_lens_dispositions_lines` 的防禦寫法、表態閘 r1 正確性席 f3；`_one` 自己既有的另一道是「任一例外接成該題無法驗證、不整份 fail-open」，r1 正確性席 f1／邊界席 f1，本案沿用）。全過 → `checked+1`，並 append 到新欄 `out["tensions"]`：`{id, chosen, existing, n_files, hazard, suggestion}`。任一不過 → 進 `problems`（擋），訊息帶題目 id 與哪一欄。
- **印法**（`cmd_code_loop check` 人可讀模式）：判定印完（OK 或 BLOCKED 都一樣）之後，`tensions` 非空就在 stderr 多印一段三段式——「⚠ 張力 N 則（兩個審查角度相反，工具只端上來、不裁）」；每則三行：「`<id>` 選了{沿用既有｜改用建議}：既有寫法在 {existing 前 3 項}（共 N 檔）」「隱患：{hazard}」「建議：{suggestion}」；末行「在意的原因：兩邊都留下來才看得見矛盾；誰讓誰由人定，這裡不擋」。`--json` 時放 `verdict.dispositions.tensions`。**rc 不因 tension 改變**：合法 tension＝該題已交代。
- **`--carry`**：`tension` 跟其他人答的值一樣帶過（`_DISP_STATUSES` 判定，不另寫）。
- **派工鏡頭**（`_lens_dispositions_lines`）：`tension` 的尾巴印「選 {chosen}｜既有 {existing 逗號串}｜隱患 {hazard}｜建議 {suggestion}」，同既有 200 字截斷。審查席反駁的就是這四欄。
- **治理帳**：事件形狀不變（`dispositions` 物件整包存，新欄自然在裡面），mapper 白名單不用動。`gov --stats` 表態段的桶加 `tension`，印「張力 N」；死題候選判準不變（只看 na 佔比）。

### 二、`pitfalls --diff` 端出候選（可能撞）

- **母體**：`_pitfall_diff_collect` 走 diff 時另收 `added_lines = {檔: [增行內容…]}`——只收 `+` 行。既有 `changed_lines`（增刪行，給適用性用）不動：候選看的是「新引入」，刪行不算。
- **算法**：對 `arch["files"]` 的每個改動檔 F（＝有對照檔的非測試 code 檔）：`sk = _stack_key_for_file(F, repo_root)`（既有簽名兩個必填參數，`.ts`／`.js` 要看 package.json），`sk` 不在 `_STACK_TRIGGERS` → 跳過。F 的增行逐行 `_stack_norm_line`（剝字串、跳註解）得 `norm`。對該棧每題 `(qid, pats, _)`、每個 `pat`：`pat` 在 `norm` 命中 → 讀三個對照檔（工作樹；讀不到、非 UTF-8 或超過 2 MB 的跳過並記 `unreadable`），逐行 `_stack_norm_line` 後搜 `pat`；**至少一個可讀對照檔、且全部沒命中** → 記候選 `(F, qid, pat.pattern)`。`when_raw`（看字串內容的那幾條）不看：鄰居的字串字面比對沒有意義。
- **輸出**：`arch_alignment["tension_candidates"] = [{"file":F,"question":qid,"patterns":[…],"siblings":[可讀對照檔],"unreadable":[…]}]`，按 (F, qid) 聚合、patterns 去重保序；沒有候選 → 鍵不出現。人可讀：在 `[架構對齊]` 對照檔清單之後每條印一行「可能撞：{F} 新增的 {patterns 用／連} 在對照的 {n} 個檔裡都沒出現（這是 {qid} 那題的做法）——沿用既有或改用新做法都用 tension 表態，審查席會查兩邊」。
- **不變量**：候選的 `qid` 必在 `stack_questions_applicable`——候選來自同一組觸發字命中 F 的增行，增行是增刪行的子集，所以該棧那題必適用（超過門檻全問時更是）。測試釘。
- **樣板**（`_dispositions_template`）：有候選的 qid，其適用題 entry 加 `"hint": "候選張力:{F} 新增 {patterns},對照檔 {siblings} 都沒有——刻意沿用既有寫法或刻意改用新做法,status 填 tension"`。`hint` 是資訊欄，validate／check 不讀、`--carry` 不比。
- **預算**：每個改動檔最多讀 3 個對照檔（沿用 `per_file=3`），單檔 >2 MB 跳過，整次最多讀 60 個對照檔——超過的檔不算候選，JSON 帶 `arch_alignment.candidates_truncated: true`，人可讀印一句「對照檔太多，候選只算了前 N 個檔」。pre-push 熱路徑跑的 `pitfalls --diff --no-lint --json` 也算候選（讀幾十個原始碼檔是毫秒級；上限釘住最壞情況）。

### 三、口徑（派工詞與工作指引）

- **架構對齊席派工詞**（`templates.md` §7.6 加一段）：「表態記錄裡若有 `status=tension` 的題：那是作者已經看見兩邊（既有寫法 X、隱患 Y、建議 Z、選了哪邊）。你的工作是查四欄真假——`existing` 指的檔真的那樣寫嗎（開檔對照）、`hazard` 在這份 diff 裡真的成立嗎、`suggestion` 在這專案可行嗎、`chosen` 跟 diff 實際做的一致嗎——查到假的才報 finding；不重裁誰贏，不因『跟既有不一致』單獨再開一條。若你自己發現『跟既有不一樣』、而該處對應的檢核題答了 `satisfied`，把發現寫成張力形狀：既有 X／隱患 Y／這次 Z／不一致 N 檔，severity 照本席錨（最多 minor，除非引入第二種做法或跨層直呼）。」
- **代碼審指引**（code-loop `SKILL.md`）：步驟 1「先表態」列四值，講何時用 `tension`——pitfalls 印了「可能撞」、或你自己知道這題的做法跟鄰居不同；步驟 6／7：兩席的發現都留，處置理由可寫「張力已在表態 `<id>` 記錄，人裁」——這是 accepted 的合法理由之一、不算壓掉；blocker／major 照舊只能折。
- **其餘文字同步**：`reference.md` 棧別段、`commands/06` 那一列、[[Systems/棧別提問表態閘]]（怎麼用＋「工具驗什麼」表格加 tension 列）、[[Systems/效能檢核目錄]] 推送前那一格、[[Systems/arch-alignment-lens]]（新節「跟檢核題撞到時」＋DEP 連本案）、[[Issues/架構對齊席與棧別檢核題可能相反]]（REVISIT 改成數 tension 與候選；d2 的「目前只寫口徑不新增閘」一句由本案 d1 接手）。
- **漂移守衛**：新測試 `t_tension_doc_sync` 釘 code-loop `SKILL.md`、`templates.md` §7.6、`commands/06` 三處含「tension」（同 `t_marker_doc_sync` 形狀；消費端沒有 skills 目錄時 `_SrcOnly`）。

## 驗收條款

- [S1] 寫側：`code-loop dispositions <檔>` 對 `status=tension` 的題——缺 `chosen`／值不在 existing|suggested、`existing` 缺或空或某項切不開（絕對路徑、`..`、缺行號）、`hazard` 或 `suggestion` 不到門檻、`chosen=suggested` 卻缺 `evidence` 或切不開 → rc2 不寫並逐題講哪一欄；全合法 → 治理帳事件與 marker 都寫入且 `dispositions[id].status=="tension"`；`--carry` 把舊的 tension 答案帶到新樣板；status 錯誤訊息列出四值 [test:t_dispositions_tension_validate]
- [S2] 讀側與印法：`code-loop check`（有適用題）對 tension——`existing` 某項在被推送 sha 的樹不存在或行號超出 → BLOCKED 且訊息帶題目 id；`chosen=suggested` 的 `evidence` 同驗；全過 → 不擋、rc 同沒有 tension 時、`--json` 的 `dispositions.tensions` 列出 `{id, chosen, existing, n_files, hazard, suggestion}` 且 `n_files` 等於去重路徑數；人可讀模式 stderr 印「⚠ 張力」段（每則三行＋在意的原因），判定 OK 與 BLOCKED（因別題）兩種情況都印；治理帳重建來的 tension 紀錄缺欄不炸、判「無法驗證」進 problems [test:t_codeloop_check_tension_warns]
- [S3] 候選：合成 Kotlin repo（同資料夾三個既有 .kt 只有循序 `.await()`／`launch`、沒有 `async`），改動檔增行加 `async {` → `pitfalls --diff --json` 的 `arch_alignment.tension_candidates` 恰一條 `{file, question:"kt-coroutines", patterns 含 "\\basync\\b"}`；把 `async` 加進任一對照檔 → 無候選鍵；只有刪行含 `async` → 無候選；註解行與字串裡的 `async` 不算命中；對照檔讀不到（權限／非 UTF-8）→ 記 `unreadable`、只剩不可讀時不出候選；候選的 qid 必在 `stack_questions_applicable`；人可讀輸出印「可能撞」行；超過 60 個對照檔 → `candidates_truncated: true` 且人可讀印一句 [test:t_pitfalls_tension_candidates]
- [S4] 樣板：`--dispositions-template` 對有候選的題在適用 entry 帶 `hint`（含改動檔、patterns、對照檔名），沒候選的題沒有 `hint`；帶 `hint` 的樣板原樣送進 `dispositions` 不因 `hint` 被拒；`--carry` 帶過來的舊答案不帶舊 `hint` [test:t_dispositions_template_tension_hint]
- [S5] 鏡頭與統計：派工鏡頭表態段對 tension 印四欄（選／既有／隱患／建議）並仍套 200 字截斷；`gov --stats` 表態段每題多印「張力 N」，tension 不算進死題候選的 na 佔比 [test:t_tension_lens_and_gov]
- [S6] 文件與漂移守衛：code-loop `SKILL.md` 步驟 1 與 6／7、`reference.md` 棧別段、`commands/06`、`templates.md` §7.6、Systems/棧別提問表態閘、Systems/效能檢核目錄、Systems/arch-alignment-lens、Issues 筆記 REVISIT 九處改到；`t_tension_doc_sync` 釘三處含「tension」 [test:t_tension_doc_sync]
- [S7] 圖譜寫回：本案計劃筆記記審計修正紀錄；Verification 節點（`lumos new verification … --plan 本案 --systems 棧別提問表態閘,arch-alignment-lens`）記實測；Issues 筆記 REVISIT 行改寫並保留日期 [manual:改後 lumos context 三個節點看 DEP 與 verified_by 對得上]

## 實務隱患

- **守衛面**：本案動 `code-loop check`，但只**加寬**合法答案（第四種值），不新增任何擋的條件——唯一新的 BLOCKED 是「tension 欄位對不上」，跟 `satisfied` 證據對不上同級，而且寫側已經先擋過一次。合法 tension 永遠不擋（合約候選①）。閘內部錯誤仍走既有 `_gate_failopen`。已排除：pre-push 與 CI 讀治理帳重建的路徑不變（新欄在同一個物件裡）；沒有 tension 的表態檔行為逐位元相同。
- **效能**：候選要讀對照檔——每改動檔 ≤3 檔、單檔 ≤2 MB、整次 ≤60 檔，超過只截候選不截其他輸出；跑在 pre-push 熱路徑（`pitfalls --diff --no-lint --json`）上，最壞 60 個原始碼檔的逐行 regex 屬毫秒到百毫秒級（測試釘上限，不釘秒數）。
- **併發**：無新寫入路徑；tension 走既有「先寫治理帳再原子寫 marker」，同 sha 重表態後者覆蓋（既有限制原樣）。
- **不可逆**：無——表態與候選都是可 git 還原的簿記；沒有刪任何既有值。
- **對外送出／金流**：無。
- **假候選**：觸發字有寬的（`\bContext\b`、`\bView\b`），對照檔碰巧沒有那個字就會亮；候選只印一行、不進閘、不進 tier，代價是多讀一行。REVISIT 數「候選幾件、其中真用了 tension 幾件」。
- **敷衍**：tension 可以填四段廢話——工具只驗對照檔存在與文字長度，同 na 的天花板；派工鏡頭把四欄端給審查席反駁是唯一的第二道。
- **反方向抓不到**：「沿用既有寫法沒採建議」在 diff 裡沒有新字，機械無候選；靠人選 tension。這是承認的天花板，不是待辦。
- **本 repo 自己**：Python 不在題表，這三塊在本 repo 只靠合成樣本測試驗證；第一個消費專案（Landmark／KDS 類）碰到候選時要回填實例到 Verification。
- **消費端 skills 未更新**：口徑住在 skills 檔，消費專案要重跑安裝才吃到（既有分發限制，同 [[Projects/棧別提問表態閘_計劃]]）。

## 刻意不做

- 不裁誰讓誰、不擋推送——裁定說工具只把兩邊端上來。
- 不用 AST 或相似度判「像不像」（[[Systems/arch-alignment-lens]] 明文不做），只看觸發字有沒有出現在對照檔。
- 不在改檔前的 hook 算候選——hook 手上只有編輯內容、沒有 diff 的檔案集合與對照組；推送前的候選足以逼出表態。等表態帳出現 tension 實例再看要不要提前。
- 不用 LLM 判 hazard 真不真。
- 不加新的治理帳 kind——tension 住在既有 `dispositions` 事件裡。

## 合約候選（設計審過閘後列，候選≠已標；蓋章走 `guard scaffold → bind → audit`，不確定就不標）

- 合法的 tension 表態不改變 `code-loop check` 的 rc；tension 欄位對不上（對照檔不在被推送的樹、文字不到門檻、chosen 不合法）跟 satisfied 證據對不上同級擋。[test:t_codeloop_check_tension_warns]
- 候選的題目 id 必在 `stack_questions_applicable`。[test:t_pitfalls_tension_candidates]

## 審計修正紀錄

（尚未開審）

REVISIT:2026-11-09 跟事故筆記同一天看：治理帳 tension 表態幾則、候選印過幾次（pitfalls 不留帳，從 code-loop 卷證的 intake 數）、候選裡真用了 tension 的比例；假候選多就收窄觸發字或把候選降成 `--json` 專屬；一則都沒有就維持不動、不再加機制。
