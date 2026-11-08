severity: major

我在複本 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查乙三-sonnet/mut` 逐條改壞 check.py 的新檢查,再跑測試。結果是有兩處改壞測試照綠,其中一處對應驗收條款 S4。其餘項目查過都沒問題。

## Findings

### 1. S4 點名的「規則包條數」沒有任何改壞案例,拿掉這項核對測試照綠
severity: major
blocking: 是

- 位置:`configs/ast-grep/kotlin-android/check.py` 的 `_stats_expected`(規則包條數那列),以及 `scripts/test_lumos.py` 的 `_KT_STATS_MUTATIONS`。
- 驗收條款 S4 明列「規則包條數、不接閘條數」要等於重數的值。`_KT_STATS_MUTATIONS` 只改了「不接閘條數」,沒有改「規則包條數」(227)。
- 具體改壞:把 `want += [("規則包條數", r"- 規則包條數:(\d+)", len(rules)),` 那一項刪掉,只留「不接閘條數」。
- 重現:在 mut 複本把該項刪掉,清 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k t_kt_catalog_stats_consistent`,輸出 `29 passed, 0 failed`。
- 後果:之後有人把〈統計〉的 227 改成別的數,自檢不會報,測試也不會紅。
- 對照組:我拿掉「待查證漏列 API-2」那道檢查(`pending_problems` 的 `if any(_pending_need(c)) and rid not in pend`),測試有紅,所以測試機制本身有效,只是漏了這一項。

引句:「want += [("規則包條數", r"- 規則包條數:(\d+)", len(rules)),」

佐證:file: `configs/ast-grep/kotlin-android/check.py`(新增的 `_stats_expected`);file: `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:181`(S4 條款)。

### 2. 各主題與規則包各等級都只改壞一個代表,其餘迴圈項沒人驗
severity: minor
blocking: 否

- 各主題只改了 DATA;`_STAT_TOPICS` 去掉 `"PERF"` 後測試照綠(`29 passed`)。
- 規則包等級只改了 error;把 `for k in ("error", "warning", "info", "hint")` 縮成 `("error",)` 後測試照綠(`29 passed`)。
- 這兩處是覆蓋不夠完整,不是整項檢查失效,所以只列 minor。
- 補法是每個迴圈各補一例,或加一個「每個主題、每個等級各自改壞」的內圈。

引句:「("DATA 列數", lambda t: t.replace("DATA 98、", "DATA 97、", 1)),」

## 修補差異回歸(題目 1)

- **CATALOG 暫時指向暫存檔**
  - `try/finally` 在例外或 check 失敗時都會把 `m.CATALOG` 指回去,`rmtree` 也在 `finally` 裡。
  - 更關鍵的是 `_ktpack()` 每次都載入全新的模組物件,就算沒指回去也不會影響後面的測試。
  - 引句:「m.CATALOG = tmp / "checks-catalog.md"      # 改壞的複本放暫存檔」
- **`_KT_STATS_MUTATIONS` 的各個改壞**
  - 十五個改壞的前置斷言「有套上」都成立。
  - 連帶改統計數的兩個(DATA-27 列著、API-2 漏列)改對了:單獨拿掉 `pending_problems` 的對應檢查,各自會紅。
  - 判定只比 `len(got) > len(base)`,沒驗是哪一道抓到的。找不出具體翻車場景,不列 finding。
  - 引句:「check(f"② 改壞「{label}」型錄自檢多報", len(got) > len(base)」
- **`_kt_batch2_b4_problems`**
  - 七列(DATA-27、DATA-79、DATA-82、DATA-83、DATA-85、ARCH-89、DATA-95)用 `batch4_expected_tags` 都算得出 `['CI 範本:Android Lint']`。
  - 型錄這七列的通電批次都含「批四(CI 範本:Android Lint)」,測試通過。
  - 引句:「elif "批四(" + ";".join(want) + ")" not in cell(rid, 9):」
- **C87~C94 逐條改壞**
  - 我把 `kt-webview-mixed-content-always` 規則逐條件改壞,每個新案例各自會紅:
    - C87:拿掉 `?.setMixedContentMode` 這支 pattern。
    - C88:拿掉不帶接收者的 setter pattern。
    - C89:把左邊的 `mixedContentMode` 條件放寬成任意。
    - C90:拿掉 `\.\s*mixedContentMode$` 那個 `has`。
    - C91:去掉接收者鏈的 `?` 容許。
    - C92:拿掉 `not: in-debug-only-branch`。
    - C93:放寬 `always-const` 的 regex。
    - C94:把 `zero-lit` 放寬成 `0`。
  - 預期值也都符合語意:`setMixedContentMode(0)` 與常數 `MIXED_CONTENT_ALWAYS_ALLOW` 都是「一律允許」。
  - 引句:「("src/main/kotlin/C94.kt", "webView.settings.mixedContentMode = 10", "kt-webview-mixed-content-always", 0),」
- **〈待查證〉17 格改成「—」**
  - 全數正確,沒有改錯、沒有漏改。
  - 17 列主表來源欄都已有〔查證〕,不含「未開頁核對」「搜尋摘要」。
  - 仍保留的 API-31、API-36、PERF-26 主表確實還含「未開頁核對」。
  - 〈統計〉的「51 列、代號待查 48、來源待核對 3」與重數一致。
  - 引句:「| API-9 | 待查(資料層研究的 detekt 候選 GlobalCoroutineUsage) | — |」
- **計劃 REVISIT 的 11 列**
  - 我用 `batch4_expected_tags` 重算,現成規則欄登了 Android Lint 檢查但通電批次沒寫批四的就是這 11 列,與清單逐項相同。
  - 引句:「2026-11-08 量過全型錄有 11 列會被新判法點到(API-9、STATE-5、UI-1」

## 整份改動與圖譜

- **統計數字**
  - 我另外重數了主表與規則檔:總列數 532、情境 426/106/人裁 4、各級組合、被會擋守到 128、逐列查證 519,都對。
  - 引句:「- 被會擋的規則守到的列數(通電批次欄含「告警帶寫法=批一」」
- **測試**
  - 整檔 `-k catalog` 180 passed、`-k kt_`/`-k kotlin` 合計 414 passed、`t_kotlin_rulepack_security_rules` 158 passed,全過。
  - `catalog_problems` 新接的 `pending_problems` 與 `stats_problems`,在其他用 `catalog_problems()`(`rules=None`)的既有測試上沒造成回歸。
- **待查證與統計的口徑**
  - `stats_problems` 的手寫數只核對列表內那些。〈統計〉節說明句也寫明「這幾個數」由自檢核對,與計劃範圍 6 的改寫句一致。
  - 引句:「總列數、各主題、各級、規則包各等級、不接閘、逐列查證、待查證這幾個數由型錄自檢(同一支 check.py 的 stats_problems)核對。」
- **圖譜 `Systems/kotlin規則包` 新增的 WHY**
  - 它宣稱的行為與 check.py 一致。我確認過 `--catalog-only` 的呼叫是 `catalog_problems(load_rules())`,會跑到。
  - 引句:「WHY:型錄〈統計〉〈待查證〉兩節是手寫的,判準住在 check.py 的 stats_problems」
- **角色鏡頭**:改動範圍是型錄、工具鏈自檢與測試,不碰對外 API 欄位,也不新增端點,be-api-compat 與 be-authz 都不適用。

共 2 條 finding,max 等級 major,blocking 1 條。臨時目錄 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查乙三-sonnet/` 留著,沒刪。
