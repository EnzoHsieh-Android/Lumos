severity: minor

三問都沒有 major。新碼的位置、依賴方向、機制都沿用鄰居。有三處寫法跟鄰居不完全一致，都屬 minor。

**1. 分層與依賴方向**

- 規則放哪裡沒有偏離：會擋的放 `rules/`（API-2 在 `api.yml`，ARCH-59 在 `architecture.yml`），不接閘的放 `rules-unwired/`（UI-33、ARCH-62）。`_KTSEC_PLACE` 新增四筆照舊格式，`t_kotlin_rulepack_security_rules` 的 S4 照舊逐筆驗目錄、訊息編號與 `ignores` 八項。
- 共用判斷抽到 `utils/has-registration-call.yml`，作法與 `utils/debug-only.yml` 一致：頂層 `id` 加 `language: kotlin`，規則用 `matches:` 引用，四份 `sgconfig*.yml` 都掛了 `utilDirs: utils`。
  - 對照 `` file: `configs/ast-grep/kotlin-android/utils/debug-only.yml:1` ``。
  - 圖譜 `about_code` 也加了這支檔，符合「每支檔有家」的要求。
- `scan()` 的呼叫端只有三處：`check.py` 的 `check()` 兩處和 `test_lumos.py` 的 `t_kotlin_rulepack_security_rules`（`` file: `scripts/test_lumos.py:127194` ``），三處都已改成解三元組。
  - 另一個 `m.scan` 在 `` file: `scripts/test_lumos.py:66910` ``，那是別的模組。
  - 沒有其他讀 ast-grep JSON 的地方：`ruleId` 在 `scripts/*.py` 與 `configs` 下只出現在 `check.py`。
  - 沒有跨層直呼。型錄的主表讀法也走 `main_rows()`（`` file: `configs/ast-grep/kotlin-android/check.py:765` ``），沒有另抄一套。

**2. 命名與錯誤處理**

- 規則 id 都是 `kt-` 加小寫連字號。訊息格式為「[編號]錯在哪;改用…」，檔頭註解也沿用「[[Projects/…]] 範圍 N:會擋／不接閘(樣本外 N 處…)」的句式。
  - 對照 `` file: `configs/ast-grep/kotlin-android/rules/api.yml:273` ``。
  - `ignores` 八項與鄰居相同，樣本路徑 `samples/{bad,good}/<id>/src/main/kotlin/<id>.kt` 與 `// BAD`、`// 容易誤報` 的標法也一致。
  - 嚴重度（`hint`、`warning`、`error`）和放置位置的搭配，在鄰居裡都找得到。
- `scan` 讀 JSON 的錯誤處理沒變，仍是 `except (ValueError, KeyError, TypeError)` 回 `None`。新取的 `d["range"]["start"]["line"]` 被同一個 except 涵蓋。
- 有三處跟鄰居寫法略有不同：

severity: minor
blocking: 否
引句:「+    # (不包進 fun case,Kotlin 不准在函式裡宣告 interface);ast-grep 報節點起始行,ARCH-59 報在函式第一個註解那行。」
`_KTSEC_CASES` 新增第五欄預期行號，並且「有第五欄 = 本體是完整 kt 檔、不包 `fun case`」。這是隱含的模式切換，沒有明寫成欄位。
- 對照的 `_KTSEC_PLACE` 選填欄（`*extra`，`` file: `scripts/test_lumos.py:127161` ``）只放「覆寫值」（路徑排除），不改變處理流程。
- 表裡既有 C01~C126 全部由測試包成 `fun case(...)`，新列是第二種寫法。
- 同一個函式的三項輸出文字也順手改了：`報一次/不報` 變成 `報 {n} 次`，標頭改取第一個非空且非 package 的行。
- 結構相同，只是表達方式比鄰居隱晦。要不要改交編排者判斷。⚠

severity: minor
blocking: 否
引句:「+| UI-18 | remember 漏 key,參數變了還用舊值 |」
型錄「實測狀態」欄對沒做規則的列，原本一律寫「未測」，這輪改成「2026-11-09 不寫規則:…」的自由文字。
- 這是型錄裡原本沒有的狀態詞，改了 UI-18、UI-51、ARCH-43、ARCH-58、DATA-8、DATA-9、DATA-23、DATA-34、TEST-38、PERF-8 十列。
- 我查了 `check.py` 裡沒有引用「未測」的地方，所以自檢不會因此壞。
- 但這個欄位的寫法詞彙多了一種，之前是「未測」或「規則 …:…」兩種。⚠

severity: minor
blocking: 否
引句:「+    ("src/main/kotlin/C132.kt"」
這是第三處風格差異。這輪的 `_KTSEC_CASES` 說明註解和 docstring 改把測試編號對應寫進 docstring 的「翻紅釘」長段。
- 這和鄰居（第二、三批）的寫法一致，不是第二種做法。
- 但 C127~C157 的註解分散在表內三行，而鄰居是集中在表上方或 docstring。純風格，不另計。

**3. 第二種做法**

- **constraints 寫法：** `kt-map-await-deferred` 用 `constraints: L: not: regex: '\.asFlow\(\)$'`。
  - 鄰居已有同型的 `not: regex` 寫在 constraints 底下，見 `` file: `configs/ast-grep/kotlin-android/rules-unwired/flow.yml:11` ``，其餘 `constraints` 多為直接 `regex:`。
  - 所以不是新做法。
- **scan 三元組：** 前面第 1 問已確認呼叫端只有三處，沒有另一種讀 JSON 的方式，也沒有並存兩種回傳形狀。
- **第五欄與 `_KTSEC_PLACE` 選填欄的比較：** 兩者都用 `*extra` 式的選填尾欄，語法相同。
  - 差別如第 2 問所述：`_KTSEC_PLACE` 的尾欄是資料覆寫，新的第五欄還會切換「是否包 `fun case`」。
  - 我不把它算成第二種機制，所以不列 major。
- **其餘：** 沒有自創工具函式。型錄現成規則欄的比對走 `main_rows()`，註冊判斷走 `utils/`。圖譜新增的 WHY 行帶 `[出處:] [因:] [不選:] [test:]`，符合格式。

不對齊共 3 條,其中 major 0 條

我沒有在 `/tmp/lumos-seat-work/code-android形狀列補規則/架構對齊二-sonnet/` 建任何路徑。
