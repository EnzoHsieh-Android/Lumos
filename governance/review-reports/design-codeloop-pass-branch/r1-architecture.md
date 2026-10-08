severity: major

severity: major  
blocking: 是  
引句:「新 marker 存原始分支名；`_codeloop_read` 遇到 marker 名碰撞而內存分支不符時，退讀依完整分支名篩出的治理帳。」  
finding: 設計只替 pass marker 核對內存分支，卻要求 dispositions 維持原語意，會在同一目錄形成兩套 marker 身分判準。現有 dispositions marker 已存 `branch`，讀取時卻直接信任 `/`→`__` 的檔名，`a/b` 與 `a__b` 仍可覆寫、借用彼此紀錄；pass 與 dispositions 會對同一組分支得出不同答案。分支輸入亦分裂：新 pass 用 Git 嚴格驗證，dispositions 只拒絕空字串。應抽出共用分支驗證與 marker 身分核對，供兩種紀錄共用；若刻意不改 dispositions，設計必須明列這項張力及隔離方式。  
file: `scripts/lumos:34378`  
file: `scripts/lumos:35344`  
file: `scripts/lumos:35360`  
file: `scripts/lumos:36018`  
重現證據：`_codeloop_branch_filename("a/b")` 與 `_codeloop_branch_filename("a__b")` 都是 `a__b`；第二次寫 dispositions 會覆蓋同一路徑，而讀側未比較 JSON 內的 `branch`。

severity: major  
blocking: 是  
引句:「編排者應先加最小回歸測試並觀察 S1／S2 翻紅，修後跑該子集及原有 code-loop 分支留痕子集」  
finding: 測試承諾沒有釘住原始故障入口。S1 指定直接呼叫 `code-loop check --branch main`，但現有測試早已覆蓋「指定 branch/sha 可讀」；真正事故發生在 pre-push 從遠端目的 ref 取出 `main` 再呼叫 check。現有 pre-push 放行案例只測「checkout 分支＝推送目的分支」，照設計字面完成仍可能完全沒測 `feature HEAD → main`。應在既有 `t_codeloop_guard_prepush` 增加：feature checkout、`pass --branch main`、stdin 目的地 `refs/heads/main`、預期放行，並保留其他目的分支不得借用的反例。  
file: `scripts/hooks/pre-push:397`  
file: `scripts/hooks/pre-push:405`  
file: `scripts/test_lumos.py:15432`  
file: `scripts/test_lumos.py:16735`

圖譜落點本身對齊：`Systems/pitfalls-code-loop` 已是 `scripts/lumos` 的既有系統節點，Issue 也指回該節點；不需另開第二篇 System。快照 SHA-256 已核對吻合。
