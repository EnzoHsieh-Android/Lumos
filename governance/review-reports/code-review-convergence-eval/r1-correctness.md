severity: major

F1 衍生 cohort 證據與同 SHA 的實際輸出不一致。保存值為 225／11／152；照保存的命令重跑得到 224／10／151，因此驗證紀錄不可重現。
severity: major
blocking: 是
引句:「"observed_code_loops": 225,」
file: `governance/research/review-convergence-eval/cohort-smoke.json:3`, `docs/lumos-toolchain-knowledge/Verification/2026-10-07_審查回顧eval補強.md:26`
最小重現（已跑，exit 1）：以 `review_convergence.py cohort docs/.canary-log.jsonl` 重算並斷言保存摘要相等；相同來源 SHA 實得 `(224,10,151)`，保存值為 `(225,11,152)`。

F2 `repair`、`preserve`、`new_defects` 最後只剩 `quality_pass`，相反的修復與退化可產生完全相同摘要，無法按規格分開比較。
severity: major
blocking: 是
引句:「repair、preserve、新缺陷分開；已執行而失敗的產品驗收仍進分母」
file: `governance/eval/review_convergence.py:324`, `governance/eval/review_convergence.py:339`, `governance/eval/review_convergence.py:355`
最小重現（已跑，exit 1）：一組由 baseline `(False,True,0)` 變 candidate `(True,False,0)`；另一組反向並改成 `new_defects=99/1`。斷言兩摘要不同會翻紅；兩者皆只輸出雙臂 `quality_passes=0`、`quality_delta=0.0`。

F3 成本均值以「剩餘有效 receipt」為分母；缺場或 duplicate 讓一個 slot 失效後，仍會輸出非空均值，能把缺掉的高成本 trial 靜默排除。
severity: major
blocking: 是
引句:「成本有完整資料才给均值，另列覆蓋數與split分層。」
file: `governance/eval/review_convergence.py:343`, `governance/eval/review_convergence.py:346`, `governance/eval/review_convergence.py:560`
最小重現（已跑，exit 1）：兩次 repeat；baseline 成本均為 100，candidate 第一次為 1，第二次成本 999 的 slot 重複送兩份。結果 `duplicate_slots=1`、candidate `valid=1`，但仍回 `tokens_mean=1.0`；斷言均值應為 `None` 翻紅。完全缺場亦同樣回非空均值。

F4 cohort 先依 loop 分組才查 token，故同一全域 token 被兩個 loop 衝突使用時，兩筆都計入且兩邊都宣告 `conflicting_tokens=false`。
severity: major
blocking: 是
引句:「重複token相同原件只計一次，有衝突則保留問題與未知。」
file: `governance/eval/review_convergence.py:97`, `governance/eval/review_convergence.py:108`
最小重現（已跑，exit 1）：輸入 `code-a/token=T/tokens=5` 與 `code-b/token=T/tokens=7`；斷言輸出至少有一個 conflict 訊號翻紅，實際得到兩個已知成本總量且皆無 conflict。

F5 新增的 Systems 節點未加入宣告只列 Systems 的總索引；`lumos doctor --verbose` 已把它列入 S6 漏項。
severity: minor
blocking: 否
引句:「responsibility: 負責審查帳衍生資料集、案例來源及試行證據比較與專屬測試」
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:6`, `docs/lumos-toolchain-knowledge/MOC/index.md:75`

F6 Systems 摘要把 `test:` 塞進 `出處:` 同一組括號，機器讀不到 PITFALL 的測試欄位；專篇 lint 已警告缺 test／repro／防回歸。
severity: minor
blocking: 否
引句:「PITFALL:[根因:把較少輪誤當品質改善]較少輪但破壞既有行為不能算改善」
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:19`

資料狀態五問：

- 新舊互讀：歷史 ledger 缺 `round`／`tokens` 時保留未知；manifest 以 `version=1` 拒收其他格式。已讀,無 finding。
- 寫一半：非法或截斷 JSON、雜湊不符、非一般檔均拒收；工具本身只讀。已讀,無 finding。
- 衍生資料：F1–F4。
- 時間：計算不依賴目前時間，也沒有日期／時區比較。已讀,無 finding。
- 不可逆：正式入口只以唯讀旗標開檔並印 stdout，不執行 receipt 內命令或寫回資料。已讀,無 finding。

pitfalls／表態核對：

- `open()` 資源命中為假陽性：`os.open` 取得的 fd 立即交給 `with os.fdopen(...)`，正常、拒收及讀取例外路徑均關閉。已讀,無 finding。
- `py-eventloop`、`py-parallel`、`py-external` 的 `na` 與同步本機 CLI 現況一致。
- `py-memory` 的尺寸上限成立；`py-hotpath` 的成對 lookup 使用字典。表態未涵蓋 F1–F4 的統計語意缺口。
- `py-extcode` 未觸發正確。

圖譜鏡頭未自動附上；回覆中沒有「lumos 自動附加」或備援段。我已實跑 `python3 scripts/lumos impact --diff ce4c30f9..HEAD`，再逐篇跑 `lumos contracts`。角色卡自動段亦未附，五問依派工原文人工完成。

硬合約逐條：

- 測試假綠形態／修 bug 前置斷言：已讀,無 finding。
- bound-tests／受影響合約測試真跑：已讀,無 finding。
- canary-audit／成功必須落盤可讀回：已讀,無 finding。
- canary-audit／second 僅 telemetry：已讀,無 finding。
- guard-kill／rc 優先序：已讀,無 finding。
- guard-kill／成功 JSON 純度：已讀,無 finding。
- slim-get／三支 PowerShell ASCII、無 BOM：已讀,無 finding。
- slim-get／不得使用 `$Args`：已讀,無 finding。
- slim-install／sentinel 外 byte-equal：已讀,無 finding。
- slim-install／重裝冪等：已讀,無 finding。
- slim-install／完整版位元組備份：已讀,無 finding。
- slim-install／manifest 身分證：已讀,無 finding。
- slim-install／三層目標守衛：已讀,無 finding。
- slim-install／Windows 直譯器不寫死：已讀,無 finding。
- slim-install／同時檢查 `lumos` 與 `lumos.cmd`：已讀,無 finding。
- slim-uninstall／移除前內容比對：已讀,無 finding。
- slim-uninstall／清理步驟互不阻擋：已讀,無 finding。
- slim-uninstall／skill 目錄先備份：已讀,無 finding。
- slim-uninstall／CLAUDE.md 精確還原：已讀,無 finding。
- slim-uninstall／孤兒 `lumos.cmd` 獨立處理：已讀,無 finding。
- slim-uninstall／manifest 清理與保留：已讀,無 finding。
- lumos-cli-read／預設排除 superseded：已讀,無 finding。
- lumos-cli-lifecycle／re-inject 保留 sentinel 外內容：已讀,無 finding。
- design-loop／處置閘第五步條款與回退檢查：已讀,無 finding。
- 節點範圍／共用既有抽取器：已讀,無 finding。
- 節點範圍／尊重 MOC 宣告範圍：檢查器正確抓到 F5。
- 節點範圍／無 MOC 必須出聲：已讀,無 finding。
- 節點範圍／只按合約數判過載：已讀,無 finding。
- 節點範圍／doctor 區段順序：已讀,無 finding。
- 節點範圍／已知閘名同步：已讀,無 finding。
- 節點範圍／懸空狀態單一常數：已讀,無 finding。
- 節點範圍／bool 不得當門檻整數：已讀,無 finding。
- 節點範圍／S5–S7 均落治理帳：已讀,無 finding。

驗證：完整讀完 1230 行凍結 patch；專屬 12 tests 通過，正式 runner 4 passed，`git diff --check` 通過。AGENTS 指定的「代碼審修復穩定性試行」與「代碼審改道生效驗證」兩個精確路徑在此 repo 不存在，三組圖譜同義詞搜尋仍未找到精確節點，故其生效／停止狀態材料不可得。

總結：最嚴重 severity major，blocking 4 條。
