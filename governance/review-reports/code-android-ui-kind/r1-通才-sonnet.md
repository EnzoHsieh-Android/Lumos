severity: major

**1. 新範本的 SPDX 檔頭用 `--` 開頭,授權守衛測試會紅**
severity: major
blocking: 是
引句:「-- SPDX-License-Identifier: MIT」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-ui-kind/scripts/test_lumos.py:53797`(`_spdx` 的樣式是 `^#\s*SPDX-License-Identifier:\s*MIT\s*$`,`_who` 同樣只收 `#`),`:53824` 的 `missing` 檢查
失敗情境:
- `t_license_headers_travel_with_vendored_files` 對 `_VENDORED_ALL` 的每一支檔都要求檔頭有以 `#` 開頭的 SPDX 行。這次把 `scripts/templates/android-ui-attribution.sql` 登記進 `_VENDORED_TREE_FILES`,但它的 SPDX 行是 SQL 註解 `-- `,不符合樣式。
- 我在 f96ffe70 的工作樹跑 `python3.14 scripts/test_lumos.py -k license_headers`,輸出是 `✗ FAILED t_license_headers_travel_with_vendored_files(1 條斷言)`,結果 6 passed、1 failed。
- 這道守衛的目的,依 `授權與歸屬` 節點的 ★INVARIANT★,是確保被複製進消費專案的檔帶得走授權聲明。範本檔頭其實有 SPDX,所以不是授權缺漏,是守衛的樣式只認 `#`。
- 沒有被審查的證據顯示這個測試在推送前閘跑過。
- 這在 `macrobenchmark-adapter` 的 PITFALL(「放檔、登記、檔頭是三件事」)已經寫過,這次仍然踩到。
- 修法二選一:守衛的樣式放寬成 `^(#|--)\s*SPDX…`,或把 `.sql` 檔頭改成守衛認得的寫法。放寬守衛要小心別弱化它。
- 照全域「修審查發現」規則,修的時候要掃同族:`android-receipt-rerun.sh` 是 `#` 所以沒事,以後新增的非 `#` 註解範本都會踩同一處。

**pitfalls manifest 逐條**(5 條都是 `source: pitfalls-builtin`,題目是 N+1,在 `android-ui-attribution.sql` 第 30、46、51、63、72 行)
- 全部判誤報。這支查詢沒有「迴圈裡反覆呼叫查詢」:它是單一一條 `WITH RECURSIVE` 查詢,遞迴那一步 `JOIN slice s ON s.parent_id = t.id` 是集合式展開,不是逐筆呼叫。
- 計劃的 PITFALL 也記了這條查詢先前是平方級,後來修成同資料 0.5 秒。
- manifest 的 `sql-sargable` 觸發字是 `COALESCE(`:它出現在 SELECT 清單(`COALESCE(n.own, t.fam)`),不在 WHERE 欄位側,所以也是誤報。
- `sql-index` 在真實 Trace 上由 trace_processor 處理,測試端的 sqlite 只有假的小表,不構成問題。

**圖譜固定席**
- `授權與歸屬` 的 ★INVARIANT★ 受影響。上面第 1 條就是它的綁定測試跑紅。
- 該節點另一條規則(授權檔不得進白名單)不受影響:新增的是 `.sql`,不是 LICENSE、COPYING 或 NOTICE。
- `lumos-cli-read`、`測試假綠形態`、`design-loop`、`bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`:不影響。diff 只在 `_VENDORED_TREE_FILES` 加一行,並新增 `t_android_ui_attribution_*` 測試與範本。這些節點宣稱的行為(search 濾網、處置閘、綁定測試真跑、guard kill 的 rc、re-inject)都沒被動到。
- 新增的 `t_android_ui_attribution_*` 一律有前置斷言(範本檔存在),符合 `測試假綠形態` 的精神。

**我讀完並確認沒問題的部分**
- SQL 邏輯我逐個手算了測試案例的期望值:innermost、inherit、rv_names、pipeline、compose_fn(含鎖競爭名稱只有一個空白的判斷)、sums。全部對得上。
- 範本裡的註解沒有行尾分號,不會被 `android-receipt-rerun.sh` 的 `(.*?;)\s*$` 提早截斷。
- 其餘沒有能當場講出失敗場景的候選。

max severity: major
