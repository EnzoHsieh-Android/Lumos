severity: minor

先講結論:這份修補沒有引入第二種做法,也沒有跨層直呼。三處被點名的寫法在 pitfalls 這一帶都對得上既有做法,只有兩條小的不一致,都不擋。

**逐項對照**

- **pitfalls 讀治理帳差異(分級維持不載圖譜)**:`_residual_ask_rows_dropped` 只讀 git diff,不載圖譜,也沒有呼叫 `_gov_vc_gate_events`。後者讀工作目錄裡的帳檔,這裡要看的是範圍內被刪掉的列,所以不能直接用它。
  - 同一帶的 `_range_base`、`_diff_range_ends`、`_test_suite_for_range` 都是直接 `subprocess.run(git…)`,這次的寫法跟它們一致。
  - 篩列的方式(先看列裡有沒有閘名,再解析 JSON,最後比對 `gate`)跟 `_gov_vc_gate_events` 一樣。
  - 這次沒有新造第二套讀帳邏輯,所以沒有判違規。
- **`ls-tree` 分辨路徑不存在**:`git show` 失敗後用 `ls-tree -z` 區分「路徑不在」跟「git 讀不出」。
  - 既有的 `_fix_ls_tree` 把「不在」和「git 失敗」都回成 None,分不開,所以不能直接套用。
  - 同樣「ls-tree 對不存在的路徑回 0 且輸出空」的認知,`_note_reread_tip_names` 和 lens 的 search 證據驗證都用過。
- **索引比對再寫跟 `atomic_write_verify`**:`atomic_write_verify` 管的是筆記開頭欄位的讀、改、寫,索引 JSON 不適用。
  - 索引一直走 `_write_lf`(寫暫存檔再原子換名),這次只在前面加了「內容相同就不寫」的判斷,沒換成別的寫入路徑。
- **日期比對**:這次沒有引入新的日期解析器。
  - 問答日期用 `fullmatch` 擋格式後,以字串比大小。
  - `[audit:]` 的日期另用一條新的正規式抽出。

**minor 條目**

severity: minor
blocking: 否 — 只是重複造了一份日期抽取,不影響行為,也不是跨層
引句:「audit_day = max((m.group(1) for a in invariant_audit_refs(body) for m in [re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", a)] if m), default=None)」
對照:scripts/lumos: `scripts/lumos:18841`(`_RESIDUAL_CHECKER_RE` 已有同樣的 `<模型>/<YYYY-MM-DD>` 日期群組)、`scripts/lumos:3969`(`_rule_date` 負責驗證真日期)
判定理由:同一支 `<模型>/<日期>` 戳記,殘留這一帶現在有兩條各自的日期抽法。這條不驗日期是否為真,只靠字串比大小成立。建議改用 `_RESIDUAL_CHECKER_RE.fullmatch` 取群組,再交給 `_rule_date` 驗證。

severity: minor
blocking: 否 — 只是又多一份相同的路徑組合,沒有第二種行為
引句:「_RESIDUAL_GOV_REL = "docs/" + GOV_LOG_NAME   # residual-ask 問答記在版控治理帳」
對照:scripts/lumos: `scripts/lumos:14579`(`_gov_vc_gate_events` 用 `Path(root)/"docs"/GOV_LOG_NAME` 自己組路徑)、`scripts/lumos:29278`(`_BOOKKEEPING_FILES` 把同一路徑寫成字面值)
判定理由:這個專案本來就沒有共用的治理帳相對路徑常數,這次是新增第三處寫法,並用 `GOV_LOG_NAME` 組出來,算較好的一種。本身不構成第二種做法。

不對齊共 2 條(都是 minor),major 0 條。
