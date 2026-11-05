severity: minor

審查範圍:4cc9c425..5b1dcb1b4。修補前後的修前版本沒另外取出比對,所以下面的歸因都是「未判定」。

## Finding 1
severity: minor
blocking: 否

測試抓不到「只改文件的功能分支推送被誤降成 light」。

引句:「if [[ "$_suite_this" == "full" ]]; then」

`scripts/hooks/pre-push`,`_down=""` 之後那個 if。

- **改壞方式:** 我在臨時複本把條件改成 `"$_suite_this" == "full" || "$_suite_this" == "docs"`。
- **結果:** 跑 `python3.14 scripts/test_lumos.py -k prepush_feature_branch` 得到 `22 passed, 0 failed`。未改壞的基線也是 22 passed。
- **為什麼測試沒翻紅:** `t_prepush_feature_branch_old_lumos` 後半有推純文件的功能分支,但用的是舊版 lumos,新欄位 `pushed_mainline` 根本不出現,走不到這個條件。其餘功能分支案例都是改程式。所以「新版 lumos、只改 README 的功能分支推送」沒有案例。
- **改壞後的實際行為:** 純文件推送在 pitfalls 判成 `docs`、`suite_computed` 為 true,功能分支的 `pushed_mainline` 為 false。這時 `_down` 會被設成 `feature_branch`、`_SUITE_BRANCH_DOWN=1`、`_suite_this` 變成 light。結果是 `_SUITE_LIGHT=1`,並且多印一句「推功能分支:…全套由 PR 的 CI 跑」。這句對根本沒打算跑全套的推送是誤導。
- **為什麼降為 minor:** 本機跑的測試子集和 docs 路徑大致相同,沒有少跑東西,只是多一句誤導的話。
- **歸因:** 原有漏查。這個測試缺口跟這輪修補是否造成無關。
- **證據:** 基線與改壞後各跑一次同一條指令,結果如上;只跑了這一個改壞,其他條件沒各自改壞驗證。

## Finding 2
severity: minor
blocking: 否

「判不判主線」在查主線候選失敗時,錯誤方向是少跑測試。

引句:「分支短名在 _note_reread_mainline_names 的集合裡(永遠含 main、master,再加主線候選指到的分支名,不看遠端名)→ true;其他 → false。」

`scripts/lumos:_note_reread_mainline_names`。它的 docstring 寫「查候選失敗、逾時只剩固定名(不擋)」。

- **失敗場景:** 專案的主線叫 `trunk` 或 `develop`、不在固定名 `("main", "master")` 裡,而 `_push_mainlines` 查詢出錯或超過 10 秒。這時推 `refs/heads/trunk` 會得到 `pushed_mainline: false`,被降成 light。
- **為什麼是方向問題:** 在原本的用途(回頭重讀指紋)裡,誤判成功能分支只是「不擋」。放到這裡,誤判變成「推主線少跑全套」,方向正好相反。新函式的 docstring 說「刻意保守」,但這條失敗路徑不保守。
- **為什麼降為 minor:** 本 repo 主線是 `main`,在固定名裡,不會中。
- **歸因:** 未判定。這條只靠讀程式推出,沒有實際讓查詢逾時去重現。

## 已驗與未驗
- **已驗:** 掛鉤與 `scripts/lumos` 的改動全部逐行讀完。`_test_suite_for_range` 的每個回傳都帶了 `computed`,只有兩處讀它,都是 `_pitfall_diff_collect` 裡直接索引。`_ppfb_harness` 回 5 個值,七個呼叫端都照 5 個值解包。基線 22 個測試全綠。
- **`_down` 的讀取點:** 只在同一個迴圈內的 `-n "$_down"` 一處。`_SUITE_BRANCH_DOWN` 只在迴圈後印那句話時讀。混推 main 與功能分支、舊版 lumos 兩條路徑,從邏輯上看沒有洞,且各有測試綁住。
- **未驗:** 修前版本(9918ed76)沒另外取出比對,所以兩條都沒有修前、修後的對照,歸因標未判定。
- **三問的回答:**
  - 問題①:`t_pitfalls_suite_computed`、`t_prepush_feature_branch_failclosed` 在修後綠,但沒跑修前,因果成立與否未判定。
  - 問題②:正常路徑與相鄰路徑(推 main、混推、舊版 lumos)只見修後通過,同樣不能單憑通過證明問題已解決。
  - 問題③:Finding 1 修前未跑,不可比。
- **慣例對照:** 我沒有逐字引出被違反的規則,所以沒有慣例類的 finding。
- **清理:** 臨時目錄已刪,沒有背景程序留著。
