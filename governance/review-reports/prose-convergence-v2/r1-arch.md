# 架構對齊審查報告 — prose-convergence-v2-r1.md（第 2 版）

範圍：`/tmp/prose-convergence-v2-r1.md`（63 行）三題;對照 repo `/Users/enzo/harness/lumos-toolchain` 現況(scripts/lumos、scripts/test_lumos.py、docs/lumos-toolchain-knowledge/、governance/review-reports/)。

---

## 群組一 — [S1] `lumos prose-lint` 子命令化 + 命令數守衛「全數同步」

**引句**（r1.md:41）：「命令數守衛連動的活文件全數同步列入交付」

**判準句**：承諾「全數」時,背後是「掃描機制」還是「人工列舉清單」——前者才機械,後者重演節點還原案的破口。

**查證**：`t_docs_command_count`（scripts/test_lumos.py:16571-16608）本身就是對全庫 `rglob("*.md")` 掃描,只排除 `governance/external-reviews/`、`governance/golden/`、`governance/l4-audit/`、`-knowledge/`、`.git`、`node_modules`（16592-16593）——這個「掃全部活文件而非清單」的設計,正是 2026-07-29 外審抓到「三檔固定清單」（AGENTS.md/reference.md/ARCHITECTURE.md）同時漂移卻全綠之後換的（16586-16588 註解自述）。也就是說「全數」這個字有掃描機制背書,不需要 [S1] 實作者自己手寫清單去對應「哪些文件連動」。這正好避開了節點還原案「分八類三處」清單失準的同一個坑——那份清單漏列第四處 `scripts/hooks/claude/lumos-entry-hook.py:74`（見 `governance/review-reports/node-restore-sop/r2-s2.md:14-18`,「分八類」實際 4 處只列 3 處）。目前 62→63 的基準也乾淨:`lumos --help` 實測 62,README.md/AGENTS.md/ARCHITECTURE.md/reference.md 現在全部寫 62,無現存漂移。

**判定**：對齊。blocking:否。

⚠ 判不準的殘餘面（不計入不對齊份數）：`t_docs_command_count` 靠三種固定措辭 regex 抓字（「N 個頂層命令」/「N top-level commands」/「N 是頂層命令數」;16600-16602),且該測試自己的註解承認曾被換第四種措辭逃過（ARCHITECTURE.md 曾寫「53 是頂層命令數」躲舊版）。[S1] 新增文件若用第五種措辭描述命令數,一樣會漏檢。這是既有守衛本身的已知天花板,不是本次 delta 新增的不對齊,但 delta 沒提這個殘餘,列⚠供編排者知悉。

---

## 群組二 — d3 治理帳加 `rewrite` 枚舉值

**引句**（r1.md:36）：「帳面收尾枚舉加 `rewrite` 值(**動一行碼,d1 的「不動」明示收窄至此**);重寫不重置攤人義務:連續兩次判重寫→強制攤人,不得三開」

### Finding 2.1 — 枚舉擴值本身有無先例
**判準句**：repo 對「帳面 kind 型枚舉擴值」有無實際做過的前例可對照。
**查證**：有,且不只一次——canary-log 的 `kind` 欄位 2026-08-14（d5）加過 `kind=none`（`docs/lumos-toolchain-knowledge/Systems/canary-audit.md:24,97`）;governance-log 也有 `kind=degraded`（delguard 降級,`scripts/lumos:12136`）。方向本身對齊既有慣例。

**判定**：對齊。blocking:否。

### Finding 2.2 — 「動一行碼」跟 d1「判定邏輯不動」的邊界
**判準句**：新枚舉值若會被既有判定謂詞「主動讀取/計數」（不是被動因不匹配而自然排除),就已經踩進判定邏輯,不能算一行碼。

**查證**：
1. `kind` 欄位在 `scripts/lumos` 裡至少有兩層獨立白名單，不是一處：CLI 層 `cr.add_argument("kind", choices=("caught", "missed", "none"))`（15386）,以及 `_round_valid_m2` 的「未知 kind 使輪無效」判定（3721),其 docstring 明講這條白名單是「gate/fold/定錨/ledger/W 歸屬五處共用」。
2. kind=none 前例自己的落地紀錄寫得很白：「五處閘謂詞納 none,`t_loop_panel_none_kind` 三向釘」（`canary-audit.md:97`）——這 repo 對「擴 kind 枚舉值」的既有做法,從來不是一行,是「逐一走過消費此欄位的謂詞、決定要不要收 + 配一支新測試釘住行為」。
3. 更關鍵的是，d3 同一句話裡自己定義了「連續兩次判重寫→強制攤人,不得三開」——這需要有人或有機制去**數**「rewrite」出現次數並據此下判斷,這本身已經是在消費這個新值做決策,跟「純被動記帳」是兩回事。

**判定**：不對齊。blocking:是。理由：這不是吹毛求疵的用字問題——d1 用「A 軌不動判定邏輯、成本低」當作暫緩 B 軌的正當性依據,如果 `rewrite` 實際上需要比照前例做多處謂詞判斷 + 新測試（或者「連續兩次」規則其實是純人工查帳、機制上完全不碰 code),兩種情況都跟「動一行碼」現在的寫法對不上,而 delta 沒有交代是哪一種。這個模糊直接影響 d1 論證的地基,應在落地前講清楚。

---

## 群組三 — d4 兩行格式 vs 既有「審計修正紀錄」寫法

**引句**（r1.md:37）：「瘦身=該段每輪固定兩行:「rN(日期,席數):N 條/blocking N/一句結論」...舊案 52 篇不回溯」

### Finding 3.1 — 漸進相容 vs 兩制並存
**判準句**：是否套用 repo 已用過的「cutoff+舊帳不回溯」慣例,還是憑空發明第二套並存寫法。
**查證**：`_panel_k2_active` 函式的既有慣例原文寫：「K=2 適用判定...舊帳不回溯(spec 落地面5,借 T6 定錨慣例)」——「新制只管新案、舊案原樣留存」在本 repo 已是被實際用過的模式,不是這次憑空新造。

**判定**：對齊。blocking:否。

### Finding 3.2 — fold-check 鏡像段可查性
**判準句**：delta 聲稱「機械依賴不動」,是否真的跟格式（兩行 vs 整段敘事)無關,而非只是斷言。
**查證**：`_fold_mirror_sections`（scripts/lumos:13453)純靠標題 regex `^##\s+(§\d+\s+)?審計修正紀錄` 偵測,只列出段落供人工複查（`☐ 複查 {s}`),不解析內容結構——兩行或整段敘事一樣被列出來。更進一步：`_fold_value_drift`（13504）與 `_fold_reverse_omission`（13573）兩支才真正做內容比對的函式,都**主動排除**審計修正紀錄段本身的 token 掃描（原文註解：「該段刻意引用歷史/舊值,掃它必假陽」),所以壓縮格式對這兩支函式行為是零影響,比 delta 自己講的「不動」還更穩(兩層機制都與格式無關,不只鏡像列舉一層)。

**判定**：對齊,且查證比宣稱更紮實。blocking:否。

### Finding 3.3 — 「52 篇」這個數字本身
**判準句**：決策文件裡寫死的具體計數,若無機械守衛支撐,依本 repo 自己在 `ARCHITECTURE.md:131` 明講的原則——「分類小計刻意不寫:只有總數有機械守衛,寫了沒守的數字就是新漂移面」——就不該被當穩定事實寫死。

**查證**：用 fold-check 自己偵測用的那支 regex（`_FOLD_AUDIT_RECORD_RE = r"^##\s+(§\d+\s+)?審計修正紀錄.*"`,scripts/lumos:13493-13494）對 `docs/lumos-toolchain-knowledge/` 全庫實測,命中 **47** 篇,不是 52。追出「52」的源頭：`governance/review-reports/prose-convergence/r1-arch.md:17` 架構席 r1 一句「①規模:52 篇筆記在用(非六案)」——沒有附掃描指令或 grep 佐證,v2 delta 原樣沿用、未重查。順帶一提，repo 裡另有一個無關但同樣寫作「52 篇」的數字（2026-07-15 決策：「背包大宗（52 篇有 plan_refs 的驗證）」,`docs/lumos-toolchain-knowledge/Verification/2026-07-15_decision_refs養成_P前置_T1回寫.md:41`)，指的是完全不同的母體（有 plan_refs 的驗證筆記,不是有審計修正紀錄段的筆記）——兩個「52」湊巧同數字，容易被誤認成互相佐證。

**判定**：不對齊。blocking:是。理由：這是同一類數字在本專案第四次失準（使用者記憶索引 `audit-record-count-by-file` 已記錄「審計紀錄條數必逐檔數——抄摘要連錯三次;grep 數標頭、總數寫加法式」)，這次還是用來框定「舊案不回溯」範圍的關鍵數字，若落地時（design-loop skill/reference 文件)原樣抄「52」寫死，馬上又製造一個沒有機械守衛的新漂移面——恰是本案自己在群組一 [S1] 已經花力氣要避免的同一種錯誤模式。應改成「舊案（fold-check 審計修正紀錄 regex 命中的既有筆記,現況 47 篇）不回溯」這種掛機械掃法而非寫死數字的措辭，或至少在落地前重新 grep 核實。

---

## 總結

不對齊共 **2** 條，blocking **2** 條（2.2、3.3）。額外 1 條⚠判不準（[S1] 命令數守衛的措辭逃法殘餘面，不計入不對齊份數，供編排者知悉）。

其餘 4 條（1.1 子命令化本身、2.1 枚舉擴值方向、3.1 漸進相容模式、3.2 fold-check 可查性）查證後與既有做法對齊，不blocking。