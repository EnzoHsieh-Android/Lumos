severity: major

先核對設計審第二輪架構對齊席的要求,八項都照做:
- 找節切表重用 `_h2_section_lines`、`_expected_table_lines`、`_expected_split_cells`(`scripts/lumos:13865`、`scripts/lumos:14424`、`scripts/lumos:14400`)。
- 出處判法收成一支共用的 `_plan_source_cell_ok`。
- 路徑判存在用 `_validate_repo_ref`(`scripts/lumos:37635`)。
- 節點連結用 `_SINGLE_WIKILINK_RE`(`scripts/lumos:509`)。
- 留帳用 `_gate_event`(`scripts/lumos:1799`)。
- 推送前自己一個標籤 `_SOURCES_PUSH_TAG`,並加在 `_spec_gate_push_bad_head` 的分支裡(`scripts/lumos:16851`)。
- 規格閘那一道的形狀照 `_spec_gate_pending`(`scripts/lumos:15618`,擋回 1、沒事回 None)。
- 生效日常數與環境變數覆寫沒有共用 `_expected_since`(`scripts/lumos:14363`),另寫一組,寫法相同。

**① 模組邊界**
- 規格閘、推送前、健檢三處都走同一組 `_plan_sources_problems` 與 `_plan_source_cell_ok`。
- 規格閘那一道插進 `_spec_gate_front` 的位置在待決問題之後,與 `scripts/lumos:15618` 那道的做法一致。
- 推送前另開一圈 `_spec_gate_push_sources`,取自 `_spec_gate_touched_plans`(`scripts/lumos:15999`),沒有重用 `_spec_gate_push_candidates`,不跨層。
- 唯一越界的是新增第二套首次加入日算法,見 F1。

F1
severity: major
blocking: 是
引句:「def _plan_first_days_batch(rr, vrel):」
這是專案裡已有的「計劃第一次進 git 的日期」算法(`_plan_first_day`,`scripts/lumos:14313`)之外的第二種做法。
- 既有的一支是對單一路徑找 `--diff-filter=A` 的提交,再用 `diff-tree -M` 逐跳追改名,而且刻意不用會追複製的 `--follow`。
- 新的一支改成對整個 `Projects` 目錄跑一次 `log --reverse -M --diff-filter=AR --name-status`,自己用 `first.setdefault` 接改名鏈。
- 兩者對複雜歷史(改名後原路徑又被新增、同一提交多檔改名)可能給出不同日期。
引句:「規則同 _plan_first_day:取提交日期、改名跟得過去(-M,依時間順序把舊路徑的日期接給新路徑)、複製不跟」
docstring 宣稱規則相同,但實作是另一套,沒有機械守衛能保證兩者一致。
- 淺複製判斷又複製一份,`_plan_effective_day` 內已有(`scripts/lumos:14351`),此處再寫一遍。
- 「取較晚者、兩個都讀不到當今天」的合併規則也在 `_doctor_plan_sources_lines` 裡手抄了一份(`_plan_effective_day`,`scripts/lumos:14343`)。
- 取捨:效能理由成立(健檢逐篇呼叫 git 會慢),但專案裡沒有先例允許兩套並存。
- ⚠ 判不準:交編排者裁,是改 `_plan_first_day` 內部支援批次,還是接受並存加一支一致性測試。我依錨點標 major。

**② 命名與錯誤處理**
- 新常數 `_PLAN_SOURCES_SINCE`、`_PLAN_SOURCES_H2_RE`、`_PLAN_SOURCES_HEAD` 與同區的 `_EXPECTED_H2_RE`、`_EXPECTED_HEAD` 同形。
- 治理帳種類 `sources-missing` 與 `expected-unsigned` 同閘同寫法(`scripts/lumos:16843`),擋下時 `hard=True`,並帶 `extra`。
- 讀檔失敗的處理與 `_expected_push_one`(`scripts/lumos:16818`)一致。
- 新健檢段 S22 排在 S21 之後,同樣不計入問題數、不寫帳,fail-open 的 `try/except` 與 S20 一致(`scripts/lumos:3407`)。
- 擋下訊息有統一標籤與標題,與既有格式對齊。

F2
severity: minor
blocking: 否
引句:「def warn_soft(lines, head, advice=None, cap=None):」
S19 的 docstring 明講「原本自己再截 20 條是第二套截斷」,先前的審查席已要求軟段只用 `_SOFT_CAP` 加 `--verbose`(`scripts/lumos:2082`)。
這次改成給共用 `warn_soft` 加 `cap` 參數,S22 傳 20。
引句:「shown = list(lines) if _verbose else list(lines)[:cap or _SOFT_CAP]」
- 結構上算改共用的對,不算第二種做法:預設行為不變,既有各段都沒傳 `cap`。
- 但 S22 預設印 20 條,與其他軟段的 3 條慣例不一致。
- 另外 `cap or` 會把 0 當成沒給。

F3
severity: minor
blocking: 否
引句:「def _plan_sources_is_new(env, rr, rel):」
「新計劃」的判法已有一份在預期值表那邊(`scripts/lumos:14388`,內聯算 `prel`、呼叫 `_plan_effective_day`、與 `_expected_since()` 比)。
這次新增 `_plan_sources_prel` 與 `_plan_sources_is_new`,健檢又再手抄一份。
引句:「return (n is not None and str(rel).startswith("Projects/") and str(rel).endswith("_計劃.md")」
「type: project 且 _計劃.md」的判斷在 `_nl_rule_lands_in`(`scripts/lumos:12903`)已有一份,這裡又多一份。
結構還在同一層,只是重複寫法變多,沒有跨層。

**③ 第二種做法**
- 批次 git log 確實是另一套首次加入日算法(F1)。
- `warn_soft` 加可選參數且預設不變,不算改共用的對,只是 F2 的行數慣例不一致。
- 生效日與覆寫旗標另立一組,沒共用 `_HIGH_RISK_EVIDENCE_SINCE`,這個分立有理由(避免追溯擋照舊寫法的計劃),不算第二種做法。

不對齊共 3 條,其中會擋的 1 條
