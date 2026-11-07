severity: major

審查範圍是 `/Users/enzo/orca/workspaces/lumos-toolchain/android-situation-evidence`(HEAD `0ea5f2e2d`)。我用 Python 3.14 直接呼叫 `scripts/lumos`,在 `/private/tmp/lumos-seat-work/code-android情境題與表態對程式/資源-sonnet/` 建合成 repo 實測,沒有改被審 repo。實測用的兩個 repo 已用字面絕對路徑刪掉,該資料夾剩 620K 腳本和輸出。

圖譜鏡頭:`Systems/hook逾時預算.md` 的內外層原則是內層逾時要明顯小於外層。情境段落在 `_DISP_BUDGET`(20 秒)之外,也不在任何 hook 外層天花板之內。

**F1 切情境段的耗時跟增行數成正比,而且沒有任何預算管它,一次推送會重算好幾遍**
severity: major
blocking: 否
引句:「        segs = _kt_situation_segments(repo_root, diff_range, _diff_range_ends(repo_root, diff_range)[1], skip=skip) or []」

- **重現**:合成 repo,300 支 .kt 檔,每支 300 行(共 9 萬增行),觸發字命中率 3%。
  - 切段本體 `_kt_situation_segments` 單次 21.7 秒。拆開看是 `git show` 逐檔 300 次 5.9 秒,加上切段運算 15.8 秒。
  - `python3.14 scripts/lumos pitfalls --diff B..H --no-lint --json` 有型錄 48.0 秒。`LUMOS_KT_CATALOG=/nonexistent` 關掉情境題是 8.6 秒。**單次多出約 39 秒。**
  - 極端案例:300 支各約 8.5k 行,命中率 30%,單次 357 秒、450072 段、最大記憶體 1.34GB。`situation_segments` 序列化成 JSON 有 73.5MB。
- **根因**:`_kt_sit_hits` 對每一條增行逐列跑 `rx.search`,共 56 列。cProfile 顯示 527 萬次 `search` 佔 15.4 秒,約 0.14 到 0.17 毫秒一行。每支檔另外開一個 `git show` 子程序,每次約 20 毫秒。
- **為什麼會拖過預算**:
  - `_dispositions_verdict` 的 `deadline` 只在題目迴圈頂端檢查。`_kt_sit_verdict_one` 是一整支同步算下去,中途不看 deadline。
  - `_kt_situation_apply`(`pitfalls --diff` 收集時)完全沒有預算。
  - `scripts/lumos:72042` 的 `_codeloop_pitfalls_tier` 開 `pitfalls` 子程序也沒有 timeout。這是既有行為,但現在每次都要等重算。
- **一次推送會算幾遍**:
  1. `scripts/hooks/pre-push:548` 先跑 `pitfalls --json`。
  2. `code-loop check` 再叫一次 `pitfalls`,也就是 `_codeloop_pitfalls_tier`。
  3. 非主線分支且範圍不同時,再叫第三次(`scripts/lumos` 約 72185 行)。
  4. 最後 verdict 內的 `_kt_sit_verdict_one` 再算一次。
  - 用 F1 的 300 檔案例估,最多約 3×39+22,大約 2 分 20 秒的額外耗時;我沒有端到端跑完整個 pre-push。pre-push 註解自己寫「最壞每個 ref 判定本體 60 秒」(`scripts/hooks/pre-push:422`)。
- **最小修法**(我只實測了前面兩項的效果):
  - 逐行先做字面子字串預篩。對同樣 9.1 萬增行,255 個觸發字面 `any(x in line ...)` 只要 0.83 秒,現在約 15 秒。預篩之後才跑 56 列的 regex。
  - 把 `git show` 換成一個 `git cat-file --batch`,省掉逐檔開子程序的 5.9 秒。
  - 切段結果存起來,同一個 `diff_range` 加 `at_sha` 只算一次。
  - 在 `_kt_sit_verdict_one` 或檔案迴圈內檢查 deadline。

**F2 `D-47` 主證據樣式的第一條在長行上是二次方回溯**
severity: minor
blocking: 否
引句:「    if not re.search(pats[0], sg["_code"].get(ln, "")):」

- **重現**:`\bval\s+\w+\s*:[^=,)]*=` 是 `D-47` main 的第一條,會套在表態者選的那一行上。
  - 輸入 `"val a: b "*n`,18KB 耗時 0.18 秒,72KB 耗時 2.2 秒,180KB 耗時 13.7 秒。
  - 這個量測跟背景任務同時跑,所以是偏高的上界,但成長趨勢確定是平方。
- **範圍**:只有被選為 evidence 的那一行很長、又沒有 `= , )` 時才會中。字串內容已經被 blank 掉,所以要有一條壓縮過的 .kt 行。
- **其他樣式**:我把型錄全部證據樣式拿去對六種病態輸入(空白、括號、`a`、點、`val a:`、`fun f(a: B = c, d) {` 重複),只有 `D-47` 超過 0.1 秒(2.29 秒),其餘最慢 0.065 秒。
- **另外檢查的**:`D-34` 的 `\.clickable\s*\((?:[^()]|\([^()]*\))*\)` 因為分支互斥,沒有指數回溯。`_KT_SIT_DECL_RE` 在 14 萬字元輸入上都是毫秒級。
- **建議**:給 `D-47` 的 `[^=,)]*` 加上長度上限,例如 `{0,200}`。

**F3 新測試在 180 秒單支上限下餘裕只有約 4 倍**
severity: minor
blocking: 否
引句:「def t_kt_situation_segments():」

- **數字**:`python3.14 scripts/test_lumos.py -k <名>` 實測:
  - `t_kt_situation_segments` 50.1 秒(餘裕 4x)
  - `t_dispositions_situation_evidence_pattern` 40.5 秒(餘裕 4x)
  - `t_kt_catalog_evidence_patterns` 0.6 秒
  - `t_strip_c_comments_kotlin` 0.3 秒
- **原因**:這兩支每案開一個 `lumos` 子程序,單次載入約 4 秒。
- **負載風險**:推送前閘切四片同時跑,CPU 被搶時這兩支可能超過 180 秒。
- **建議**:把 `t_kt_situation_segments` 的子程序案例合併,或用 `LUMOS_TEST_TIMEOUT` 加 override。
- **殘留暫存**:跑完前後 `gctl-` 目錄數都是 175,沒有新增。

**確認沒問題的項目**
- **型錄讀取**:模組載入時讀一次(`_KT_DT_ROWS`),解析約 6 毫秒,沒有逐次重讀。
- **子程序收尾**:`subprocess.run(..., timeout=_disp_git_timeout())` 逾時和 KeyboardInterrupt 都會先 kill 子程序再往上拋。`_kt_situation_apply` 接 `TimeoutExpired`,verdict 路徑由外層 `except Exception` 判「無法驗證」並擋下。
- **`_kt_strip_spans`**:用明確堆疊,不遞迴,新增的 Kotlin 剝法沒有爆炸;測試涵蓋 10 萬層巢狀。

總結:最嚴重是 F1(切情境段沒有預算、一次推送重算多遍,300 檔 × 300 行單次多 39 秒),會擋 0 條。
