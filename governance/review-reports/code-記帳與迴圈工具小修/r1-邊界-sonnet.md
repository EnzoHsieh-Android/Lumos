severity: minor

我的鏡頭是邊界與輸入。這份 diff 在我試的極端輸入上都沒做出壞帳,只找到 4 條 minor 和一組固定席回答。沒有 blocker 或 major。實驗都在我自己的臨時目錄跑,已刪除。

**finding**

1. 全空白的 `--regression-set` 被當成 `none` 收下,舊版是擋的。
severity: minor
   - blocking: 否
   - 輸入:`canary record none --loop code-x --round r1 --findings-set f1 --folded-set f1 --accepted-set "" --refuted-set none --regression-set $'\t'`
   - 預期:rc2「--regression-set 是空的」。舊版 `_ids` 切完得空串列,走 `if not rg` 擋下。
   - 實際:rc0,帳上寫成 `regression_set: []`。`" , ,\t"` 同樣放行。
   - 原因:新的空值檢查只用 `strip(" ,")`,不處理 Tab 等空白,之後 `rg` 是 `[]` 就直接放行。空字串、單一空格、`,,` 都還擋得住。
   - 是否影響:沒有測試覆蓋這個輸入。`t_canary_record_regression_set_code_only` 只測 `none`。
   - 引句:「if not str(regression_set).strip(" ,"):」

2. 表態 tension 的 `chosen=suggested` 型別錯誤,拿掉實作測試也照綠。
severity: minor
   - blocking: 否
   - 計劃第 4 節明寫三處:satisfied、tension 的 evidence 與 existing、讀側。S20、S21、S22 的測試沒涵蓋 tension 的 evidence。
   - 我在臨時副本刪掉那段型別檢查,跑 `-k dispositions`,結果 124 passed、0 failed。
   - 行為目前是對的:evidence 給 `[]`、`{}`、`0`、`True`、`1.5` 都回「要是一個字串…」。但沒有測試守著。
   - 引句:「_te = _disp_type_err(ent, "evidence") if ch == "suggested" else None」

3. `existing` 的某一項是 `null` 時,講的仍是「切不開」,不是型別錯。
severity: minor
   - blocking: 否
   - 輸入:`existing: [null]` 的 tension 表態。
   - 實際:`existing 第 1 項 'None' 切不開——缺行號(格式 path:line)`。`0`、`{}`、`[]`、`true` 都正確講型別。
   - 原因:`_disp_value_type_err` 對 `None` 直接放行,這對頂層 evidence 是對的(`null` 等於沒附),對清單內的一項就不對。
   - 引句:「if v is None or isinstance(v, str):」

4. 輪次規則的 docstring 與程式碼不一致,另外 `--round` 的值不驗內容。
severity: minor
   - blocking: 否
   - docstring 規則③說「帳上定錨 standard/high 而這筆沒帶 `--round` 就擋」。程式碼條件是 `(not rows or anchor is None)`,所以定錨了、既有列都不帶輪次的迴圈,再記一筆不帶輪次的照樣放行。
   - 重現:先在帳上放 `loop=prose-anch`、`tier=high`、無 round 的一列,再記一筆不帶 `--round` 的 → rc0。計劃第 88 行寫的是「零筆、或既有列沒有任何定錨時」,所以程式碼符合計劃,是 docstring 寫過頭。
   - `--round "  "`(純空白)是真值,能滿足「standard 每筆要帶 `--round`」,帳上寫成 `round: "  "`。規則的目的是要有輪次,這個輸入能繞過。`--round ""` 則正確當成沒帶。
   - 引句:「③有效分級(帳上定錨,沒有就取這筆 --tier)是 standard/high 而這筆沒帶 --round 就擋」

**其他邊界(都是小問題,不單獨成條)**
- 帳不是 UTF-8 時,任何帶 `--loop` 的新記錄都被擋,連無關編號和 light 也一樣。訊息說「這個審查編號的帳讀不懂」,把整本帳壞了講成該編號壞了。不帶 `--loop` 的照寫。可算預期行為。
- 編號含 ESC 或換行時,「第一筆沒帶輪次」那則訊息的範例指令把編號原樣印到 stderr。同函式另一則訊息已用 `_esc_clean` 清過,兩處不一致。治理帳是 JSON 跳脫,沒問題。
- 提示範例只改尾端數字:`r01` 給 `r2`(不補零),`r1a` 給空字串。
- `--folded-set None` 搭配 `--findings-set none`(大小寫不同)會被當空集合,最後報「還沒處置: ['none']」。結果是擋下,但訊息繞。
- 壞行、超深巢狀行、空帳、帳不存在都正常。45 MB、30 萬列的帳記一筆約 2 秒,真帳 5 MB 不構成負擔。
- 編號 `Code-X` 和 `code`(不帶連字號)照設計審處理,和現有 `startswith("code-")` 判法一致。

**圖譜固定席(逐條判是否影響)**
- `canary-record未落盤事件`、`loop-convergence-recording`:不影響已記錄的行為。新規則(輪次、none 集合、`--regression-set`)在寫入前擋,擋下時帳不變(S5–S19 的測試與我的實驗一致)。
- `design-loop` 的 ★INVARIANT★ 處置閘第五步:不影響。diff 沒碰判種類或審材格式的程式。
- `pitfalls-code-loop`:不影響。新增行只在人可讀輸出、`--json` 鍵不變。
- `lumos-cli-read`、`guard-kill`、`bound-tests-gate`、`lumos-cli-lifecycle`:不影響。diff 沒碰 search、guard kill、code-loop check 的跑測邏輯和 re-inject,我也沒看到相關改動。
- 讀側 `_loop_round_format` 與 `loop next` 的混用守衛共用同一個數法,沒有寫側放行、讀側判不了的缺口(結局帳的情形我實跑過)。

**驗收條款能否寫成會紅的測試**
S5–S19 都能照字面寫成會紅的測試,各測試的 mutation 看起來合理(S6 避開了其他守衛代打,S9 靠 `round=5` 造壞帳)。S20–S22 缺 tension evidence(見 finding 2)。S24 的「--json 不含新欄位」只擋鍵名同時含 `review` 和 `seat` 的欄位,擋不了其他命名,屬測試較弱但目前行為正確。

最嚴重 severity: minor;blocking 共 0 條。
