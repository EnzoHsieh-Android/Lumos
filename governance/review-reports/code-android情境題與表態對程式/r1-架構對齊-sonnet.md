severity: major

這份 diff 有兩處多出第二種做法:型錄決策表的讀法有 lumos 與 check.py 兩套,`-U0` 差異解析多了一套。其餘是剝註解、觸發字比對、表態驗證與測試隔離的對齊情形。我只讀了 patch 與 repo 既有檔,沒有跑任何東西,也沒有改 repo。範圍外的環境提示說算不出固定席節點,所以本審沒有用到目標架構規則。

## ① 分層與依賴方向

**F1** lumos 讀型錄決策表與 check.py 讀型錄決策表是兩套各自實作的讀表程式。
severity: major
blocking: 是
引句:「def _kt_dt_triggers(cell):」
引句:「def dt_evidence(cell):」
- check.py 這邊已有 `_cells`、`_CELL_RE`、`dt_triggers`(`configs/ast-grep/kotlin-android/check.py:89`、`:110`、`:117`),diff 又在同檔新增 `dt_evidence`、`_dt_header`。
- scripts/lumos 的對應物是 `_KT_DT_CELL_RE`、`_kt_dt_cells`、`_kt_dt_norm`、`_kt_dt_triggers`、`_kt_dt_evidence`、`_kt_decision_table`,內容逐段同形。
- 兩邊的註解都承認自己是另一份(「同 check.py 的 _CELL_RE」、「scripts/lumos 的 _kt_decision_table 同一套」),但沒有共用實作,也沒有漂移守衛。
- 表頭必有欄也已經分歧:lumos 是 6 欄 `_KT_DT_COLS`(`scripts/lumos:38128`),check.py 是 8 欄 `_DT_HEADER`。
- 「(停用)」字面量兩邊各寫一次。
- 依賴方向上,lumos 讀的是 `skills/kotlin-idioms/checks-catalog.md`,格式檢查的 owner 是 check.py。lumos 該借用 check.py 的讀法,例如 `scripts/lumos:73288` 的 importlib 匯入別人檔案的既有做法,而不是另寫。

**F2** 情境題的差異解析另寫了一支 `-U0` 解析,沒有走專案已有的解析器。
severity: major
blocking: 是
引句:「def _kt_sit_hunks(repo_root, diff_range):」
- 既有的 `_notelines_parse_hunks`(`scripts/lumos:46896`)照 `@@` 計數走。它處理上下文行計入兩邊行號(對應本機 `diff.interHunkContext`),也處理 `\ No newline` 與被引號的路徑。
- 新函式只認 `+` 與 `-` 行,遇到 `diff.interHunkContext` 夾進來的上下文行,`new_ln` 不會前進,行號會偏。
- 它的 git 呼叫也不走既有的 `_ns_git`(`scripts/lumos:46962`),而是自己 `_sp.run(["git", "-c", "core.quotePath=false", ...])`。
- `_notelines_parse_hunks` 的 docstring 還寫了檔頭誤判的踩坑史。新解析器用 `in_hdr and line.startswith("+++ ")` 判檔頭,是同一個坑的另一種防法。

## ② 命名與錯誤處理

**F3** 命名多數對齊 `_kt_*`、`_KT_*`、`_disp_*` 的既有前綴,只有一處例外。
severity: minor
blocking: 否
引句:「_KT_DT_ROWS, _KT_DT_ERR = _kt_decision_table()」
- 型錄在模組載入時就讀一次,失敗只留 `_KT_DT_ERR` 字串,各處再各印一行提醒。
- 重複印提醒的地方有三處:`_kt_situation_apply`、`_kt_sit_catalog_warnings` 和樣板。這跟 `_stack_questions_config` 的 `warnings` 欄(`cfg["warnings"]`)那條既有路徑不同,後者是統一收進 warnings 再印。
- `_kt_sit_catalog_warnings` 因此在 `_dispositions_verdict` 裡手動併進 `out["warnings"]`。結構上可接受,只是提醒的走法有兩種。

**F4** 表態驗證抽出共用的 `_disp_satisfied_shape`,證據格式仍走既有的 `_dispositions_split_path_line`,這部分是對齊的。
severity: minor
blocking: 否
引句:「def _disp_satisfied_shape(ent, platforms, default_platform):」
- 情境題 `_kt_sit_shape` 與 `_kt_sit_row_shape` 另立一種答案形狀(`segments`,沒有頂層 evidence),錯誤句的句型也跟其他題不同。
- 在 `_dispositions_validate` 裡用 `if qid == _KT_SIT_QID and not ent.get("auto")` 分流,等於題目 id 寫死在驗證主幹裡。
- 這是既有 `_STACK_QUESTION_SPECS` 的 spec 旗標沒有承載的差異,不算第二套,但第三種題型出現時會變成逐題 `if`。

## ③ 第二種做法

**F5** 剝註解的入口維持唯一,但裡面多了第二套掃描器。
severity: major
blocking: 否
⚠ 判不準:入口是同一支,掃描本體分叉,是否算「第二套」請編排者裁。
引句:「掃描本體是 _kt_strip_spans,填法同上三個旗標。」
- `_strip_c_comments` 的 docstring 寫明「全庫只有這一支」「不留兩套掃描」(`scripts/lumos:6820`),掃描本體是 `_C_STRIP_PAT`。
- diff 加 `kotlin=True` 分支後,Kotlin 走自己的堆疊狀態機(`_kt_strip_spans`、`_kt_strip_str_tok`、`_kt_strip_code_tok`),不再經過 `_C_STRIP_PAT`。
- 巢狀區塊註解與 `${}` 樣板確實是 `_C_STRIP_PAT` 做不到的,理由成立。
- 但原 docstring 開頭「掃描本體是 `_C_STRIP_PAT`」那句沒有跟著改,現在對 Kotlin 路徑不成立,文件與程式不一致。

**F6** 觸發字比對有粗判與逐列兩套,詞界寫法是庫裡第 N 次手寫。
severity: minor
blocking: 否
引句:「def _kt_trigger_re(t):」
- 題表的 `when` 清單(`(?-i:…)` 包住,走 `_stack_applicability` 的 `re.I` 路徑)是粗判。
- `_KT_SIT_ROW_RX` 逐列比對剝過的程式碼,是第二套比對。diff 的註解有交代,粗判只供改檔前推播等只有改動行的地方用。
- 詞界 `(?<![A-Za-z0-9_])` 在 `scripts/lumos:6535`、`:22212`、`:58960` 已各自手寫過,`_kt_trigger_re` 是又一份。
- 本庫沒有共用的詞界 helper,所以只標 minor。

**F7** 測試的環境隔離沿用 `LUMOS_KT_CATALOG` 環境變數凍結舊測試,做法對齊,放的位置不同。
severity: minor
blocking: 否
引句:「LUMOS_KT_CATALOG 可指到別份型錄(測試用)。」
- 既有的 `LUMOS_HIGH_RISK_EVIDENCE_SINCE`、`LUMOS_PANEL_RETIRE_CUTOFF` 是在檔頭用 `setdefault` 凍結(`scripts/test_lumos.py:159`)。新的在 `_isolate_environment` 內以覆寫方式寫入(`scripts/test_lumos.py:48737`)。
- 這部分在 repo HEAD 的測試檔裡,不在這份 patch 的甲丙範圍。
- 差別是凍結的是一份型錄檔而不是日期值,放在 `_isolate_environment` 內有道理,沒有第二套隔離機制。不擋。

不對齊共 7 條,其中會擋的 2 條。
