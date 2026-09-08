---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-08
aliases:
  - 提問表態閘
  - stack question disposition gate
  - 檢核答案機械化
  - 已滿足或不需要
related:
  - "[[Projects/pitfalls棧別效能追問_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Systems/convergence-evidence-gate]]"
  - "[[Systems/lumos-refcheck]]"
  - "[[Systems/bound-tests-gate]]"
  - "[[Issues/寫下風險當成處理風險]]"
  - "[[Issues/只退場不痛的機制]]"
  - "[[Projects/iOS與Node後端補棧_計劃]]"
  - "[[Systems/finding-refute]]"
tags:
  - type/project
  - status/doing
  - scope/guards-gates
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-08 Enzo:「這些提問,實務上 Agent 進入實作時有在證明已滿足或不需要?」)★——查證答案是沒有:三時機(改檔前 hook/推送前 advisory/終審)全是「推到眼前」;唯一義務在 code-loop reference 一句「留痕**建議**含答案」並自註「工具不驗 note 內容、人工紀律」;留痕帳歷來 0 筆提到檢核;spec 端 pitfalls --check 只驗「實務隱患」節存在。=[[Issues/寫下風險當成處理風險]]形狀
  KEY:★裁定=借設計審處置閘,零新機制類型★——diff 命中某棧時,每一問在蓋章前要有機器可讀的表態:satisfied(附證據 path:line 或 test:名)/na(一句理由)/todo(連 Issue 節點);閘放在 `code-loop check`(pre-push/CI,它本來就算 diff 與 tier),pass 只驗形狀、把表態寫進留痕帳(不對照 diff);tier high 缺任一問=BLOCKED,standard 走既有 advisory 分支多印「未表態」提醒不擋
  KEY:機械錨點只抓最懶的謊:satisfied 的 path:line 要存在(借 refcheck 存在性)、test: 名要被 discover_test_methods 掃到(profile 感知)、todo 的 Issue 檔要存在(vault-free 路徑查)、na 理由 ≥10 字;答錯留給審查席——派工單附上實作者表態讓席位反駁(對稱既有的辯方機制:審查員的發現由獨立辯方拿 file:line 反駁,單源 Systems/finding-refute)
  KEY:副產品=每一問歷來 satisfied/na/todo 比例進 gov --stats;一問長期全 na=死題候選,今天沒有任何辦法知道哪些題在空轉(評測類的料)
  KEY:天花板(向人複述):表態可以敷衍,錨點與審查席只降機率不是證明——同設計審處置閘承認的 GIGO（垃圾進垃圾出：表態寫什麼工具就記什麼）;閘內部錯誤 fail-open 但進治理帳(同其他閘慣例);不做 LLM 判答案對錯
  PRIOR-ART:①最小解在既有機制層——處置閘(每條 finding 折掉或附理由接受,機械數)已是設計審與代碼審的收斂判準,本案只是把「發現」換成「提問」;錨點借 refcheck(存在性)與 discover_test_methods(測試名);留痕借 code-loop ledger JSON 加欄+治理帳事件 ②世界解:PR template 的 checkbox 清單普遍但不擋(GitHub docs);真的擋的是「all review threads resolved 才准 merge」政策(2026-08-26 的世界對照報告 `governance/review-reports/world-benchmark-2026-08-26.md` 已引)——本案=把同一政策套到「機器提的問」;Vercel 實證靠模型自覺 56% 跳過 ③裁定=借用既有設計（家規三選一裡的 borrow-design：借既有／真沒輪子才自建／新依賴幾乎不選），不加依賴
  DEP:scripts/lumos(cmd_code_loop pass/check、_pitfall_diff_collect、_refcheck_scan、discover_test_methods、_codeloop_write、cmd_gov --stats)｜scripts/hooks/pre-push advisory 分支｜skills/lumos-code-loop SKILL.md 步驟 8+reference.md 棧別段｜commands/06-代碼審與推送.md
---
# 棧別提問表態閘（2026-09-08）

> 白話：工具會在改檔前、推送前、終審時把「這個技術棧該問自己的效能問題」推到 agent 眼前，但推到眼前之後沒有任何機制要求它回答。這篇要做的事只有一件：**命中的每一問，蓋章前要留下一個機器讀得懂的交代**——做到了（附證據）、不適用（附理由）、還沒做（連到待辦）——缺一問就不准推。做法完全借設計審已經在用的處置閘，不發明新東西。

## 現況查證（2026-09-08，全部實查）

- 三個時機的實際效果都是「保證被看見」：hook 注入純提醒；推送前的 advisory 分支只印問題；終審蓋章把 note 原樣寫入。
- 唯一寫了義務的地方是代碼審 skill 的參考文件：「終審留痕**建議**含對應檢核問題的答案」，同一句自註「工具不驗 note 內容、人工紀律」。
- 留痕帳（governance/code-loop 與治理帳）歷來 0 筆提到檢核答案；最近的 pass 紀錄全是「幾輪幾席折了幾條」。
- 設計端同形：`pitfalls --check` 只驗「## 實務隱患」節存在，段落寫「無」也過。

## 設計

### 表態的形狀

- 一份 JSON，鍵＝`<棧>-<序號>`（序號＝該棧問題表當下順序；同一個 commit 的 pass 與 check 讀同一張表，所以序號在同一版本內是確定的），值＝`{status, evidence|reason|issue, question}`，其中 `question` 存原文，讓帳本自描述、跨版本統計不靠序號。
- `status` 三值：`satisfied`（必附 `evidence`：`path:line` 或 `test:<名>`）、`na`（必附 `reason` ≥10 字）、`todo`（必附 `issue`：`Issues/<名>`）。
- 樣板由工具產：`lumos pitfalls --diff <範圍> --dispositions-template` 印出命中各問的 JSON 骨架（含原文、status 留空），agent 填完存檔。

### 閘放哪裡

- **`code-loop pass --dispositions <json>`**：只做寫側——驗 JSON **形狀**（status 三值、各 status 的必附欄位、`question` 原文非空），**不對照 diff**（pass 不一定知道 diff；「鍵對不對得上命中的問題」是 check 的事），形狀壞 rc2 不寫帳；形狀好就寫進留痕記錄的 `dispositions` 欄與治理帳事件。沒帶旗標 → 印一句「若這批改動命中棧，check 會要表態」提醒，不擋。
- **`code-loop check`**（pre-push 與 CI 都跑它）：它本來就重算 diff 與 tier。加一段：tier high 且 diff 命中棧 → 讀當前 sha 的 pass 記錄，逐問核對——缺表態、`satisfied` 的 path:line 不存在、`test:` 名掃不到、`todo` 的 Issue 檔不存在、`na` 理由太短 → BLOCKED，訊息三段式列出哪幾問。
- **tier standard**：pre-push 既有的「棧命中 advisory」分支多印一句「這幾問還沒表態」，rc 不變（2026-07-20 已裁 standard 不擋）。
- 閘自己出內部錯誤 → fail-open 放行但寫治理帳 `warned`，同其他閘慣例。

### 錨點怎麼驗（只抓最懶的謊）

- `path:line`：檔案存在且行號在範圍內（借 refcheck 的存在性核對，不驗內容）。
- `test:<名>`：用該 repo 的 test profile 跑 `discover_test_methods`，名字要在集合裡（同 doctor 的 Check T 標準：合約綁的測試名必須是掃得到的真測試，不是散文裡的字面）。
- `Issues/<名>`：任一 `docs/*-knowledge/Issues/<名>.md` 存在（只查檔案路徑存不存在、不載入圖譜——check 跑在 pre-push，載入整個圖譜要好幾秒）。
- 答對答錯不驗：派工鏡頭在 diff 模式把表態附進派工單，審查席可反駁（對稱辯方對發現的做法）。

### 副產品：哪些題在空轉

- `lumos gov --stats` 多一段：按問題原文彙總歷來 `satisfied/na/todo` 次數；某題 ≥10 次表態且 100% `na` → 印「死題候選」。這是評測類第一次能看見提問表本身的效果。

## 驗收條款

- [S1] `lumos pitfalls --diff <範圍> --dispositions-template` 對命中各問各印一條骨架，含 `question` 原文與空 `status`；未命中棧不印 [test:t_dispositions_template]
- [S2] `code-loop pass --dispositions <json>`：形狀壞（未知 status、缺必附欄、question 空）rc2 不寫帳；形狀好寫進留痕記錄 `dispositions` 欄與治理帳；不對照 diff [test:t_codeloop_pass_dispositions_write]
- [S3] `code-loop check`（tier high、命中棧）：鍵對不上命中的問題（少的算缺、多的忽略）、缺一問、`satisfied` 引不存在的 path:line、`test:` 名掃不到、`todo` 的 Issue 檔不存在、`na` 理由 <10 字 → 各自 BLOCKED 並列出該問；全部合法 → 照舊放行 [test:t_codeloop_check_dispositions_gate]
- [S4] tier standard 的 pre-push advisory 分支多印「未表態」提醒且 rc 不變 [manual:對 standard diff 跑 scripts/hooks/pre-push 看輸出與 rc]
- [S5] 派工鏡頭 diff 模式把 pass 記錄裡的表態附進派工單（有才附） [test:t_dispatch_lens_includes_dispositions]
- [S6] `gov --stats` 多一段按問題原文彙總三值次數，100% na 且 ≥10 次印死題候選 [test:t_gov_stats_dispositions]
- [S7] code-loop skill 步驟 8 與 reference 棧別段改寫：「建議」改成「check 會擋」，附樣板指令；commands/06 加一列 [manual:讀改後的 skill 文字對照本節]

## 實務隱患

- **守衛面**：本案改 pre-push/CI 的擋法。已排除誤擋的兩種來源：①只對 tier high 擋，standard 不變；②閘內部錯誤 fail-open 進治理帳，不會因為工具自己壞掉把人擋在外面。
- **不可逆**：無——留痕檔與治理帳都是追加式簿記，可 git 還原。
- **對外送出／金流**：無。
- **既有 pass 記錄**：沒有 `dispositions` 欄的舊記錄，check 只在「當前 sha 的 diff 命中棧」時才要求；留痕本來就綁 sha、改碼即失效，所以不需要日期式 grandfather。

## 刻意不做

- 不用 LLM 判答案對錯（那是審查席的事，而且會回到「驗證層天花板＝oracle 品質」）。
- 不做設計端（spec）的逐問表態——`pitfalls --check` 的節存在性檢查另案。
- 不改問題表本身。

REVISIT:2026-10-08 看留痕帳裡 satisfied/na/todo 的分布：若 na 佔比 >70% 代表表態被敷衍或題目不對，回頭裁「加嚴（na 理由要引檔）」還是「刪題」。
