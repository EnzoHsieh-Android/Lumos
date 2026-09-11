severity: major

### F1 頂層 `*Tests`/`*IntegrationTests`/`*UITests` 資料夾的豁免不分技術棧、不看副檔名,任何語言的真程式檔都會被靜默排除在「需要家」外
severity: major
blocking: 是 — 這正是牽連鏡頭要抓的「拓寬後原本會擋的違規不再擋」,而且是新引入、計劃決策裡沒承認過的缺口
引句:「if sufs and parts[0].endswith(sufs):」
1. `_nodehome_in_stack_test_dir` 只比對頂層資料夾名稱字串,完全不檢查裡面檔案的副檔名或所屬棧;它跟 `_nodehome_is_test` 是 `_nodehome_required` 判「需要家」的唯一入口(我逐一 grep 過,`_nodehome_is_test` 全檔只有這一個呼叫點,`_nodehome_required` 只有 4 個呼叫點,對應提交前/推送前/健檢共用同一套邏輯),所以缺口一次擴散到提交前、推送前、健檢 S8–S10 三段。
2. 最小重現(在 /tmp 分別 checkout 改動前 631d7e3b 與改動後 bd0a8f26 的 scripts/lumos,in-process 載入後直接呼叫同一支函式):
```
PaymentGatewayTests/reconciliation.py  old_is_test=False new_is_test=True
CheckoutIntegrationTests/pricing_engine.go  old_is_test=False new_is_test=True
RefundUITests/refund_flow.js  old_is_test=False new_is_test=True
```
這三個路徑是 Python/Go/JS 的一般業務檔,跟 Xcode/.NET/Gradle 完全無關,純粹因資料夾名字尾巧合撞上 Swift/C# 的測試資料夾樣式(`Tests`/`IntegrationTests`/`UITests`),就從「需要家」變成不需要。
3. 佐證:file: `scripts/lumos:17809` `_nodehome_in_stack_test_dir` 的比對邏輯;file: `scripts/lumos:17814` `_nodehome_is_test` 把它接進判定鏈。我也用真實消費專案 pos-ios(只讀)驗過:120 支受版控檔裡只有 1 支分類改變(`PosTerminalTests/ScreenshotMaker.swift`,正是回報的那個 bug),目前沒有爆更大範圍——但這代表缺口是「潛伏」而非「已發作」,下一個把測試資料夾取名為 `XxxIntegrationTests`/`XxxUITests` 的非 Swift/C# 專案就會踩到,而且不會有任何錯誤訊息,純粹靜默放行。

### F2 模組層級延遲快取 `_NODEHOME_STACK_TEST_DIRS` 無鎖 → 判定:誤報,不是真隱患
severity: minor
blocking: 否 — 全工具鏈沒有 threading/multiprocessing,來源 `TEST_PROFILES` 全程不被改寫,寫法跟既有兩處同款單例一致
引句:「_NODEHOME_STACK_TEST_DIRS = None   # lazy:(頂層資料夾結尾樣式, src/ 底下的測試資料夾名)」
1. `grep -n "threading\|concurrent\|multiprocessing" scripts/lumos` 全檔零命中,CLI 是單一程序跑完就結束的一次性腳本,不存在兩個呼叫者同時觸發第一次惰性初始化的視窗。
2. 佐證:file: `scripts/lumos:14015` `_STACK_GUESS_CACHE = None` 是既有同款模組級單例(該行註解自己就寫「同 _TESTMAP_DIR_RE 的既有寫法」);file: `scripts/lumos:19848` `_TESTMAP_DIR_RE = None` 也是同款。這次新增只是照抄已經在生產路徑上用了一段時間的既有慣例,不是新風險。
3. `TEST_PROFILES` 全程只被 `dict(TEST_PROFILES[...])` 複製使用(`load_test_profile`/`load_platforms`),原字典本身不曾被寫入,所以快取一旦算出就恆對,沒有「值算到一半被別的呼叫看到髒資料」的問題。

### F3 圖譜鏡頭——固定席逐條判不影響(分組摘要)
severity: clean
blocking: 否 — diff 範圍限定在測試檔判定與新增測試/文件,沒有一篇列出的節點宣稱的機制被真正動到
引句:「測試地圖的規格刻意只認 test/tests 資料夾與檔名,不動它」
1. bound-tests-gate / canary-audit / guard-kill / slim-get-一行安裝 / slim-install-安裝器 / slim-uninstall-一行卸載 / 授權與歸屬:七篇各自講 code-loop 綁定測試真跑、canary 落盤驗證、guard kill rc 優先序、`.ps1` 編碼與保留名、CLAUDE.md 注入與備份、SPDX 授權表——這支 diff 完全沒碰這些函式,只是因整支 `scripts/lumos`/`scripts/test_lumos.py` 被改到才被 impact 列成間接相依,判定不影響。
2. 測試假綠形態(還原翻紅釘):已實測驗證合規,不是空殼——把 `_nodehome_is_test` 換回改動前 631d7e3b 版本,重跑新測試(file: `scripts/test_lumos.py:249` 的 `not_req` 清單)裡的 7 組路徑,6 組從「不算測試」變回「算測試」(即修前會被誤判需要家、測試會真的翻紅),滿足該節點要求的前置斷言。
3. 其餘只列名的 15 篇(lumos-cli-lifecycle、lumos-cli-read、design-loop、pitfalls-code-loop、lumos-deinit、loop-convergence-recording、節點範圍與索引守衛、lumos-refcheck、cochange-guard、check-r-guard、doctor-irreversible-hint、reversibility-governance-ledger、check-t-sentinel、core-invariant-baseline、judge-severity-gate):各自機制(CLI 生命週期、設計審迴圈、pitfalls 綁定、deinit、loop 收斂記錄、節點範圍守衛、refcheck、cochange、check-r、doctor 不可逆提示、治理帳、check-t、核心不變量基線、severity 閘)一律沒被這支 diff 觸及,同樣是同檔被列成間接相依,判定不影響。

總結:最高 severity major,blocking 共 1 條
