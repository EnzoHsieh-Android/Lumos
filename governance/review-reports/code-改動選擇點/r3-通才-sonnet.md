severity: minor

## g1 推送前掃描回傳的「碰到的計劃時限底線」是死碼,拿掉它測試照綠
severity: minor
blocking: 否。沒有錯的行為,只是多餘複雜度,也沒有測試守它。

引句:「deadline = max(deadline, time.monotonic() + _CHOICE_GUARD_FLOOR)」

- 輸入與路徑:推送前走 `_choice_push_scan`,`_choice_compute` 後多算一個時限,交給 `_choice_push_round` 的 `_choice_guard(..., deadline=deadline, cache=cache)`。
- 為什麼沒用:`_choice_guard` 唯一吃時限的地方是 `_choice_spec_calc`。要走到掃描,前面 `_choice_requirement` 必須已經在 `changed` 非空時用同一個 `cache` 和 `(rng, at_sha)` 算過它。所以這裡一定命中快取,時限不起作用。`_choice_guard` 其餘部分(`_platform_test_index`、`clause_bindings`)都不看時限。
- 代價:多一個常數 `_CHOICE_GUARD_FLOOR`、`_choice_push_scan` 多回一個值,docstring 和計劃筆記都在解釋一個沒作用的保護。
- 佐證:`scripts/lumos:78312`、`scripts/lumos:78536`、`scripts/lumos:78271`(`_choice_requirement`)、`scripts/lumos:77781`(`_choice_spec_calc` 的快取鍵)。
- 歸因:有證據的修復新增。修前版沒有這個符號(`_CHOICE_GUARD_FLOOR` 在 f1be3141 的 `scripts/lumos` 出現 0 次,修後 3 次)。
- 兩版證據:
  - 修後版把該行換成 `pass`,跑 `python3.14 scripts/test_lumos.py -k choice_scan_batch_budget` 得 2 passed,跑 `-k spec_gate_push_choice` 得 42 passed,全綠。
  - 修前版沒有這行,所以沒有可比的結果。

引句:「_CHOICE_GUARD_FLOOR = 5.0」

## 三問

**① 原問題的修復效果有何行為證據**

- **H1(守的測試雜湊)**
  - 修後版跑 `-k choice_kill_test_files` 得 19 passed。
  - 我另外自造輸入驗證:兩個測試名互為前綴(`` `loads data` `` 與 `` `loads data when empty` ``),加一個中文測試名。
  - 修後版:`loads data` 只收到 B.kt 的物件編號,另兩個收到 A.kt 的。
  - 修前版對三個都回同一個檔(A.kt)的物件編號,`loads data` 取錯檔。
- **H2(AI 放的選擇點放行)**
  - `-k lint_waive_choice` 得 4 passed。
  - 小結有選擇點那一行,hint 句也改成說明它出現的位置。
  - 只靜態核對了讀取端,`ai_pending_choice` 只有 `_cl_say_lint_waive_notes` 在用(`grep ai_pending` 確認)。
- **H3(整批掃描)**
  - `-k choice_scan` 得 9 passed,`-k choice_scan_batch_budget` 得 2 passed。
  - 我用 `configs/ast-grep/kotlin-choice/samples/` 的 6 支樣本加一支空檔,各用修前(逐檔)與修後(整批)的 `_choice_scan` 掃一遍。
  - 結果:命中、arid、error 三組完全一致(`mv` 先排序才比;兩版的 `mv` 字典鍵順序不同,只是 JSON 鍵順序),diffs 為 0。
  - 未驗:真 Android 專案的耗時,以及整批輸出超過 64MB 退回逐檔的路徑,我沒有重現。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立**

- 跑過 `-k choice_kill_rerun`(11 passed)、`-k choice_kill_incremental`(6 passed)、`-k gov_stats_choice_dedup`(4 passed)、`-k choice_push_cap_waive_stable`(5 passed)。
- 只改一支測試的內容時雜湊會變、不相關檔案或正式碼裡同名字的檔不影響、兩平台同名各算各的,這幾條都有測試守。
- `_choice_kill_pick` 與 `_choice_push_stale_tests` 對不明標記 `?` 的兩個方向都核對過。
- 兩版對照的限制:修前版只能比 `_choice_test_blobs` 與 `_choice_scan` 這兩支函式,其餘行為修前沒有對應案例,標未判定。

**③ 新發現的同一案例在修前、修後各是什麼結果**

- 只有 g1,見上。修前版沒有該符號,修後把它換成 `pass` 測試照綠。
- 另查 ast-grep 整批掃目錄時會不會被 `.gitignore` 或 `.ignore` 靜默略過檔案(逐檔指定路徑不受影響):
  - 暫存目錄的祖先是 git repo 而且 `.gitignore` 含 `*.kt` 時,整批輸出 0 行,逐檔輸出 61 行。
  - 全域 ignore、祖先 `.ignore`、祖先 `.gitignore` 只寫 `.tmp/` 這三種,整批與逐檔輸出都是 61 行。
  - 要踩到需要 `TMPDIR` 在一個 `.gitignore` 忽略 `.kt` 或 `src` 的 repo 裡,不實際,所以不列為 finding。

## 圖譜鏡頭

這次沒有附固定席節點,下面是依派工詞自己讀到的修補差異判的。

- **選擇點計劃筆記:** 範圍 1 到 5 的敘述與程式一致。核對了 `tests_sha` 以平台與測試名為鍵、`run` 的 `tests` 三元素格式、`choice-points` 與 `choice-kill` 對有檔算不出來的 rc(分別為 3 與 2)。不影響合約。
- **`Systems/規格閘.md`:** 新增與改寫的 PITFALL 和 WHY 都帶 `[出處:]`、`[根因:]` 或 `[因:]`,以及存在的 `[test:]`。判不影響。
- **governance 錨點基準:** `scripts/test_lumos.py` 雜湊與檔案實際的 sha256 一致,判不影響。簽核流程(代簽)是否合規不在本席範圍,未判。
- **skills 手冊 `06-代碼審與推送.md`:** 只更新 rc 說明,與程式一致,不影響。

## 未驗範圍

- 沒跑不帶 `-k` 的全套,也沒做真 Android 端到端。
- 沒驗 `git grep -o -w -F` 在非 UTF-8 路徑、NFD 檔名下的行為。靜態讀法是只會落到「記 `?` 多重跑」,不會漏重跑。
- 磁碟曾滿(剩 403Mi),所以我先把修前版的完整 clone 刪掉,改用 `git show` 取修前檔案。實驗用的臨時目錄 `/tmp/lumos-seat-work/code-改動選擇點/通才-sonnet` 已確認沒有程序開著,用字面路徑整個刪除。

最嚴重:minor;blocking 共 0 條
