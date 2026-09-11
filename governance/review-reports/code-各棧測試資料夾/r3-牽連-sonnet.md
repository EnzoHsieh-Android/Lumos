severity: major

### F1 測試資料夾裡「跟該棧副檔名不同」的輔助檔(如 Xcode 橋接標頭 `.h`)沒被涵蓋,仍會被提交前擋下
severity: major
blocking: 是 — 會被 `lumos home check --staged`(pre-commit)當成新違規擋下,不是單純提醒,使用者要另外發現並手動加 `node_home.ignore` 才能繞過
引句:「副檔名屬於貢獻那個結尾的棧,而且頂層的 <X> 資料夾裡有同一種副檔名的檔」
- `_nodehome_in_stack_test_dir` 的頂層(Xcode/.NET)那條錨定,要求檔案副檔名必須落在 `sufs[suf]`——也就是「貢獻那個結尾樣式的棧自己宣告的 `exts`」(swift-xctest 只有 `.swift`、csharp-xunit 只有 `.cs`);不像 Gradle 那條只看「同模組 `src/main` 有沒有同副檔名的檔」、不限定副檔名屬於哪個棧。file: `scripts/lumos:17832` 是這段限定的核心行。
- 這跟計劃節點宣稱的「資料夾裡的輔助檔一起算」不符——那句話是無條件的,但程式只涵蓋「輔助檔副檔名剛好等於該棧宣告的副檔名」這一種情況。file: `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md:83` 是這句宣稱。
- 新測試 `t_nodehome_stack_test_dirs_not_required` 的 not_req 案例全部只用 `.swift`/`.cs`,沒有任何一支跨副檔名輔助檔(如 `.h`/`.hpp`/`.c`)驗過,所以這個缺口兩輪審查都沒被反例抓到。file: `scripts/test_lumos.py:36747` 是漏測的那個斷言範圍。
- 可當場翻紅的最小重現(真的跑了,不是臆測):在乾淨臨時 repo 放 `PosTerminal/App.swift`、`PosTerminalTests/ScreenshotMaker.swift`、`PosTerminalTests/BridgingHeader.h` 三支檔並 `git add -A`,執行 `python3 scripts/lumos home check --staged --repo <repo>`,輸出擋下清單裡 `PosTerminalTests/BridgingHeader.h` 仍列在「沒有家」名單中,而同資料夾的 `ScreenshotMaker.swift`(.swift)正確被排除——同一個資料夾、同一次改動,只因副檔名不同就一支被免家一支被擋,跟這次修的問題是同一型(平板 POS 的 Xcode 測試資料夾在真實專案裡常見橋接標頭 `.h`/ObjC helper,不是罕見組合)。

## 逐項判定(clean / 誤報)

1. **風險掃描指定項——`_NODEHOME_STACK_TEST_DIRS` 模組層級延遲快取沒鎖保護**:判**誤報**。`grep -n "threading\|multiprocessing\|concurrent.futures\|ThreadPoolExecutor" scripts/lumos` 全檔零命中——`lumos` 是每次呼叫獨立行程、單執行緒跑到 `main()` 結束的 CLI,不存在同行程內兩條執行緒同時觸發 `_nodehome_stack_test_dirs()` 的情境。快取的來源資料 `TEST_PROFILES` 執行期間從未被改寫(唯一一次寫入在模組載入時、第 3588 行執行一次;`load_test_profile` 與所有測試都只用 `dict(TEST_PROFILES[name])` 淺拷貝,不動全域字典本身),所以連「快取用到舊資料」這種單執行緒下的邏輯風險都不成立。同檔案早就有同款不上鎖的模組級延遲快取(如 `_TESTMAP_DIR_RE`),這不是本次新引入的風險模式。

2. **牽連與回歸——健檢 S8–S10、home check 兩模式、寫回落點、別人的檔四條路徑逐一核對**:
   - 四個呼叫點(`_nodehome_evaluate` 的 N/B 兩側、`_nodehome_ledger` 的主側與 golive G 側)都各自對自己那一側的 `side.all_paths` 重算 `layout`,沒有跨側共用或用錯層,不影響。
   - 健檢 S8–S10 與 home check 走同一支 `_nodehome_ledger`/`_nodehome_required`,自動吃到新規則:對 `/Users/enzo/harness/pos-ios` 實跑(唯讀,用 `_nodehome_ledger` 直接讀取,沒有寫任何檔案),修前後對比,homeless 清單從 2 支降成 1 支,少掉的正是 `PosTerminalTests/ScreenshotMaker.swift`,跟逃逸帳與 Issue 筆記描述的症狀逐字對得上,不是空案。
   - 「別人的檔」規則:新豁免的測試資料夾檔同時退出 `req` 集合,連帶不再被 `_nodehome_refs` 追蹤成「別人的檔」目標——但這是沿用 test map 既有豁免檔案的既定行為(在這次改動之前,`tests/` 資料夾裡的檔案本來就有同樣效果),不是本次新增的放寬;pos-ios 圖譜目前沒有任何節點用反引號指到受影響的檔,查證是 `grep -rn "ScreenshotMaker" /Users/enzo/harness/pos-ios/docs/pos-ios-knowledge` 零命中,沒有實際回歸案例。
   - 寫回落點規則(規則三/四)建立在同一個 `req` 集合上,測試資料夾本來就不該要求寫回,行為一致,不影響。
   - 效能:對本工具鏈 65 篇圖譜實測 `time python3 scripts/lumos home check --staged` 得 0.535 秒,跟節點宣稱的「提交前 0.65 秒」基準同量級,沒有退化。

3. **「過鬆」已知風險(業務資料夾剛好取名 `<X>Tests` 又剛好有同名同副檔名資料夾,如 `Payment/`+`PaymentTests/`)**:節點已用獨立一行 `REVISIT:2026-10-12` 記下要回頭查三個 POS 與本工具鏈裡被免家的檔,符合鐵則四的「附回頭看條件」,不算未處理的裸風險,不影響本輪判定。

4. **圖譜鏡頭——r3-lens.txt 列出的節點**:改動範圍完全侷限在 `_nodehome_is_test`/`_nodehome_required`/`_nodehome_refs`/新增的 `_nodehome_stack_test_dirs`/`_nodehome_top_dirs`/`_nodehome_layout`/`_nodehome_in_stack_test_dir` 這幾支「每支檔有家」自己的函式(對照完整 diff 逐 hunk 確認),沒有觸及 canary-audit、guard-kill、slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載、授權與歸屬、bound-tests-gate 的任何邏輯——這些節點會被 `impact` 列成「間接相依」純粹因為牽連檔算法是以 `scripts/lumos`/`scripts/test_lumos.py` 這兩支巨型檔為單位,不是真的邏輯相依,逐一判「不影響」。「測試假綠形態」(還原翻紅釘要配前置斷言)這一條:新測試 `t_nodehome_stack_test_dirs_not_required` 用對照表驅動的漂移守衛與大量刻意造的反例(ABTests/、LoadTests/、scriptsTests/ 的 .cs、androidTest 的 .py 等)逐一驗證錨定被拿掉會翻紅,精神上符合這個不變量,不是本次要動的對象,不影響。其餘「超出上限只列名」的 15 篇節點(lumos-cli-read、lumos-cli-lifecycle、design-loop、pitfalls-code-loop、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、reversibility-governance-ledger、lumos-refcheck、doctor-irreversible-hint、core-invariant-baseline、check-r-guard、check-t-sentinel、cochange-guard、judge-severity-gate)同理,僅因共用大檔被列為間接相依,改動未觸及其對應邏輯,批次判「不影響」。

總結:最高 severity major,blocking 共 1 條
