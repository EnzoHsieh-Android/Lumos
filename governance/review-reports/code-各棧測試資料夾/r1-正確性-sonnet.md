severity: major

### F1 頂層資料夾只要「名稱結尾是 Tests」就整支資料夾免家,會把同名的真產品資料夾一起放掉
severity: major
blocking: 是 — 直接繞過「新增沒家的程式檔要擋」這道閘的核心保證,不是邊緣情境
引句:「if sufs and parts[0].endswith(sufs):」
重現:在 `/tmp` 複製 `scripts/` 後執行
`python3 -c "import importlib.machinery,importlib.util; l=importlib.machinery.SourceFileLoader('m','scripts/lumos'); s=importlib.util.spec_from_loader('m',l); m=importlib.util.module_from_spec(s); l.exec_module(m); print(m._nodehome_is_test('ABTests/ExperimentManager.swift'))"`
輸出 `True`(改動前只靠 `_testmap_is_test` 判,這支 `.swift` 副檔名在測試地圖清單裡、目錄名不等於 `test(s)?`,舊邏輯會回 False=仍要家)。另用 `_nh_repo`/`_nh_file` 建暫存 repo、走完整 `_nodehome_required`,`ABTests/ExperimentManager.swift` 直接不進需要家集合(`req == set()`)。
1. `_nodehome_in_stack_test_dir` 對頂層資料夾只比對「名稱結尾」,沒有排除業務功能剛好取名 `XxxTests` 的資料夾——`ABTests`(A/B 測試功能模組,常見業務命名,不是 Xcode 測試 target)、`BetaTests`、`SmokeTests` 這類頂層資料夾都會被整批判成免家。
2. 這是這次 diff 新引入的退化,不是延續既有天花板:改動前副檔名在測試地圖清單裡的檔(swift/kt/cs/…)只由 `_testmap_is_test` 把關,目錄正規表達式要求整段等於 `test(s)?`,「ABTests」不會被舊碼放過;是這次新加的頂層 suffix 分支造成放行。
3. 影響面不只提交前:`_nodehome_required` 是提交前(`_nodehome_evaluate`)、推送前(同一支函式)、健檢 S8 舊帳(`_nodehome_ledger`)共用的唯一判定,三個閘同時失守、且不印任何警告(靜默放行,比 `_detect_test_dir` 命中多個候選時還會印警告更隱蔽)。

佐證:
file: `scripts/lumos:17801` `_nodehome_in_stack_test_dir` 只比對頂層資料夾名稱結尾,不驗證資料夾實際內容或跟該棧慣例是否一致
file: `scripts/lumos:17995` `_nodehome_required` 呼叫鏈起點,`_nodehome_is_test` 在此被套用到每一支候選程式檔
file: `scripts/lumos:18211` 提交前/推送前共用的 `_nodehome_evaluate` 呼叫 `_nodehome_required` 算 reqN/reqB
file: `scripts/lumos:18486` 健檢 S8–S10 用的 `_nodehome_ledger` 呼叫同一支 `_nodehome_required`,舊帳清單同樣看不到這類檔
file: `scripts/hooks/pre-push:198` 推送前掛鉤直接呼叫 `home check --diff`,走的是同一份判定,不是只有提交前受影響

### F2 風險掃描指定項:_NODEHOME_STACK_TEST_DIRS 模組層級快取沒鎖——判誤報
severity: clean
blocking: 否 — 全程式沒有 threading/multiprocessing,lumos 是每次呼叫起一個新行程的 CLI,不存在跨執行緒競爭窗口
引句:「_NODEHOME_STACK_TEST_DIRS = None   # lazy:(頂層資料夾結尾樣式」
1. 對整支 `scripts/lumos` 搜尋 `threading`/`concurrent.futures`/`multiprocessing` 全部零命中,pre-commit/pre-push/健檢都是單一 Python 行程跑到底,不存在兩個執行緒同時把這個全域變數從 `None` 改成 tuple 的窗口。
2. 同一支檔案裡已經有一模一樣的既有寫法在跑,這次只是照抄既有慣例,不是新引入的風險面。

佐證:
file: `scripts/lumos:19848` 既有 `_TESTMAP_DIR_RE = None  # lazy` 用同一種「None→第一次呼叫時算好填回全域」寫法,先例已在同檔案裡跑,沒有鎖

### F3 圖譜鏡頭:附檔列出的牽連節點,這次改動都沒有真的碰到它們的 INVARIANT
severity: clean
blocking: 否 — diff 只新增/修改 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test` 三支函式與對應測試,不碰其餘節點描述的行為
引句:「從測試棧對照表 TEST_PROFILES 推各棧的測試資料夾,不另寫清單」
1. bound-tests-gate、canary-audit、guard-kill 三篇講的是「合約測試真的跑過」「canary record 落盤」「guard kill rc 優先序」——這次 diff 沒有動測試執行、canary 記錄或 guard kill 的任何程式碼路徑,判不影響。
2. slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載、授權與歸屬、測試假綠形態 五篇講的是 Windows `.ps1` 編碼、CLAUDE.md 注入備份、LICENSE vendoring、回歸釘紀律——這次 diff 完全沒有觸碰對應函式,判不影響。
3. 其餘「超出上限只列名」的節點(lumos-cli-lifecycle、lumos-cli-read、design-loop、pitfalls-code-loop、lumos-deinit、loop-convergence-recording、節點範圍與索引守衛、lumos-refcheck、cochange-guard、check-r-guard、doctor-irreversible-hint、reversibility-governance-ledger、check-t-sentinel、core-invariant-baseline、judge-severity-gate)全是因為跟這次改動共用 `scripts/lumos`/`scripts/test_lumos.py` 這兩支大檔被 impact 波及計算收進來,不是真的邏輯相依,同理判不影響。

佐證:
file: `scripts/lumos:17780` 這次新增的函式與全域快取都侷限在 `_nodehome_*` 前綴命名空間,沒有動到 guard kill / canary / slim 安裝器那幾段程式碼

總結:最高 severity major,blocking 共 1 條
