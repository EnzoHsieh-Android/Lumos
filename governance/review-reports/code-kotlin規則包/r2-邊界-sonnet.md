severity: minor

# 第 2 輪邊界與輸入席報告(code-kotlin規則包/r2/邊界-sonnet)

我把規則包用 `git archive 73276ca7b` 複製到路徑含空白與中文的 `/tmp/lumos-seat-work/code-kotlin規則包/邊界-sonnet/a b/中文/` 實跑,用 ast-grep 0.51.x。基線全過:`規則 207 條,問題 0 個`。
沒有 blocker 或 major。報告寫完後我已刪除臨時目錄。

**實測後沒問題的項目**
- `files:` 寫成單行流式清單、縮排的多行清單、跨行 `[ … ]`、CRLF、`files:` 放在最後一個 key,都判對。
- 祖先目錄叫 `good/bad` 時樣本歸屬照樣正確。含空白與中文路徑也正確。
- `--sg` 缺值回 2。`--sg` 指到目錄時,會被 `except OSError` 接住,回報「跑不起來」。
- 逾時的 `subprocess.run` 不會被殘留子程序卡住。我用 `sleep 8` 的 wrapper 驗過,1 秒就回 `None`。
- `rules-review/` 整個不存在時,報 4 條問題,不會誤判通過。
- `review-fp-` 檔放在非語意覆核級規則的好例裡,該規則命中時仍報「好例誤報 2 處」。
- `include_test_paths` 的新警告:`""`、`tar.gz`、`..kt`、空清單都判對。
- `_RULEPACK_SAMPLE_RE` 只認 `.kt` 與 `.kts`。`configs/ast-grep/` 底下目前只有 `kotlin-android` 一包,樣本全是 `.kt`,所以目前不構成回歸。

---

severity: minor
blocking: 否
類別:修補引入
`_files_block_is_test_only` 遇到「第 0 欄的 YAML 區塊清單」或「區塊內第 0 欄的註解」會靜默回 `False`。該規則就不被當成「只掃測試碼」,祖先目錄樣本的檢查被悄悄跳過。目前真規則全用單行流式清單,所以現在沒觸發。
引句:「m = re.search(r"^files:(.*?)(?=^\S)", doc + "\nz", re.M | re.S)」
重現(`_files_block_is_test_only("id: a\nfiles:\n- '**/src/test/**'\nrule:\n  pattern: x\n")`)輸出 `False`。把 `-` 縮排兩格後輸出 `True`。`files:\n# c\n  - '**/src/test/**'` 也輸出 `False`。
建議:結束條件改成「下一個 `^[A-Za-z_"'][^\n]*:`」這種頂層 key,或直接用 YAML 解析。

---

severity: minor
blocking: 否
類別:修補引入
`〈來源縮寫〉` 節不存在時,`abbrs` 變空集合,每一條沒有網址的來源都報同一句「來源沒有網址或來源縮寫」,完全不提節不見了。實測刪掉該節後出現 `規則 207 條,問題 324 個`,根因被淹沒。對照:缺 `情境決策表` 或 `待查證` 時有專屬的早退訊息。
引句:「abbrs = set(re.findall(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|", text[i_src:i_src_end], re.M)) if i_src >= 0 else set()」
建議:`i_src < 0` 時比照 `<catalog>` 早退,回「找不到〈來源縮寫〉節」。
附帶一個極小的角落:`〈來源縮寫〉` 若是檔案最後一節,`i_src_end` 為 -1,`text[i_src:-1]` 會少一個字元。

---

severity: minor
blocking: 否
類別:修補引入
`SCAN_TIMEOUT` 是「每次呼叫」的上限,不是整體上限。ast-grep 卡住時,`check()` 會依序吃滿 12 次逾時:`loaded_count` 3 次、掃樣本 6 次、掃祖先目錄樣本 3 次,最壞 12×120 秒,約 24 分鐘。測試 `t_kotlin_rulepack_samples` 還連續呼叫 `check` 約 5 次,會更久。註解寫的目的是「不要拖到外層測試逾時」,這個目的沒達成。
引句:「SCAN_TIMEOUT = 120     # 一次掃描的上限(秒);正常不到一秒,卡住時不要拖到外層測試逾時」
重現:`SCAN_TIMEOUT=1` 搭配一支 `sleep 8` 的假 `sg`,`check()` 跑了 12.2 秒,回 219 條問題。
建議:第一次逾時就中止後續掃描,或改成整體 deadline。

---

severity: minor
blocking: 否
類別:修補引入
`review-fp-` 豁免有兩個弱點。第一,它只看檔名開頭與命中的規則是否屬於覆核級,不驗證該檔真的會命中。把任何好例改名成 `review-fp-…` 就能躲過好例誤報。第二,`good_cases` 把 `review-fp-` 檔也算進「好例至少要兩段」。實測把 `kt-livedata-setvalue-background` 的真好例改成只剩一段 `fun onlyOneGood() = 1`,再靠 `review-fp-firebase-setvalue.kt` 湊數,`check.py` 仍回 `規則 207 條,問題 0 個`。
引句:「if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and review_ids and rule_id in review_ids:」
建議:`good_cases` 排除 `review-fp-` 檔。另可要求 `review-fp-` 檔必須放在該規則自己的好例目錄(`owner == rule_id`)。

---

總結:邊界與輸入面沒有比 minor 更高的等級。共 4 條 minor,都不擋,全屬「修補引入」:YAML 區塊清單解析、缺節時的訊息、逾時沒有整體上限,以及 `review-fp-` 豁免會讓好例計數失真。「上輪沒看的角落」類別沒有發現。
