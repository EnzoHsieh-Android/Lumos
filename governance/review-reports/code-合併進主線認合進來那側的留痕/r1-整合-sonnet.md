severity: minor

整合與知識同步鏡頭。逐項查證結果:(1) 簽名與呼叫端全部跟上;(2) 掛鉤與 CI 範圍和「原始起點」假設一致;(3) skills 沒有句子被打壞但也沒同步;(4) 筆記有三處沒寫到程式實際擋掉的情形;(5) 沒有既有測試或下游依賴被打壞。

## F1 擋下訊息對「非合併提交」的一般推送也一律多接一句「為什麼沒認」,是雜訊且 skills 與掛鉤提示沒同步
severity: minor
blocking: 否 — 不影響放行或擋下的判定,只影響訊息可讀性與說明同步。

引句:「    reason = f"{reason};{why}"」

說明:`_codeloop_review_block` 對每一次高風險缺留痕的擋下都先呼叫 `_codeloop_merge_side_pass`。普通分支推送(目標不是合併提交)會被接上「推送範圍起點…」或「目標不是兩個母的合併提交」這類句子,多數人讀到會以為自己的推送跟合併有關。每次還多付 2 次 rev-parse、1 次淺 clone 檢查、1 次 rev-list 的 git 成本。表態那關同樣:`merge_side` 永遠不是 None,「還沒有表態記錄」的 problems 字串也會被接長(`scripts/lumos:47069`)。

引句:「        echo "逃生路依上面 check 講的原因走:缺表態 → 先表態」

掛鉤 `scripts/hooks/pre-push:474` 的逃生路說明、`skills/lumos-project-notes/commands/06-代碼審與推送.md:36`(只寫「pre-push 自己會算,high 沒留痕就擋」)與 `skills/lumos-code-loop/reference.md:179`(「必須先記 code-loop pass 留痕 → 再交 finishing-a-development-branch 進合併流程」)都沒講「主線合併提交認合進來那側、前提是分支合併前已合過主線且留痕之後才合」。三個月後的人遇到「合併前沒跟上主線」這句擋下,在 skills 裡找不到對應說明。建議:只在判得出目標是兩個母的合併提交時才接「為什麼沒認」,其餘維持原字串;並在 06 與 reference.md 各補一句。

## F2 認合進來那側的整段期限在第一次呼叫時起算,中間隔著新增告警閘,審查那關可能被算成「時間用完」
severity: minor
blocking: 否 — 只會多擋(fail-closed),且我未能實際重現,只從程式順序推得。

引句:「        cache["deadline"] = _t.monotonic() + _DISP_BUDGET」

說明:`cache` 在表態那關(只在表態沒認到時)第一次用到就起算 20 秒;審查那關在 `_codeloop_guard_verdict` 裡排在新增告警閘(`lv = _lint_new_verdict(`)之後,而該閘會跑專案宣告的 linter。若表態那關曾查過合併側、linter 又跑得久,審查那關重用同一個已逾時的 deadline,`_merge_side_git` 在 `left <= 0` 回 None,合法的合併被擋並印「時間用完」。筆記寫「整段一個期限(`_DISP_BUDGET`)」,沒講兩關共用同一個起算點。未能重現,自降。建議:期限改成每關各自起算,或筆記寫明共用。

## F3 筆記新段落漏寫了程式實際會拒認的三種形狀,與下游實務不一致
severity: minor
blocking: 否 — 程式本身保守(判不了一律不認),只是文件讓接手者以為涵蓋範圍比實際大。

引句:「第一個母等於推送範圍原始起點(判定函式改寫全零起點之前存下的值)」

說明:對照 `_merge_side_start`:全零或空樹起點、沒給 `--diff`(本機直接 `code-loop check` 不帶範圍,`raw_range` 為 None)、終點不等於 `--at-sha`,都直接回「不認合進來那一側」。筆記只寫「第一個母等於原始起點」,沒寫這三種拒認。實務上:(a) CI 的 `BEFORE` 在新分支首推是全零,所以 CI 對非主線新分支永遠不會認(目前 `.github/workflows/ci.yml:5` 只對 push main 跑,所以這條不痛);(b) GitHub 的 squash / rebase 合併產生的不是兩個母的提交,PR #28 同型問題在那種合併方式下不會被這次修好,筆記沒講。(c) 程式註解寫「推送前掛鉤對新分支首推已先改寫過,起點形同認了分岔點」,但筆記裡沒有這句,而這是安全論證的一個前提(`scripts/hooks/pre-push:53-65` 的 `pp_block_range_for`)。建議在落點筆記補一句「squash/rebase 合併不適用」與「全零/空樹/無範圍不認」。

引句:「既有行為(本案沒改,測試時發現):目標分支自己名下的舊紀錄,只要之後只動簿記檔就有效」

說明:這句我對 `_codeloop_record_valid_ex`(`scripts/lumos:46852` 用 `git diff --raw rec marker` 比淨差)核過,成立,不是問題。但它是承認風險,卻沒有回頭條件(`REVISIT:` 行),違反專案鐵則四;建議補。

## 逐項查證(無發現)
- (1) 呼叫端:`_codeloop_read_from_ledger` 在 `scripts/lumos:45672`、`scripts/test_lumos.py:6654,6684,41867,41876` 簽名不變、語意只更嚴(head_sha 必須是字串;原本若帳本行是非 dict 的 JSON 會在 `ev.get` 拋 AttributeError 且不被 `except OSError` 接住,現在被濾掉,是順手修正)。`_codeloop_read_dispositions` 在 `scripts/lumos:45310,47199,47046` 與測試 `17142,70663` 等 mock 都沒變。`_dispositions_verdict` 新增 `merge_side=None` 預設值,測試呼叫 `scripts/test_lumos.py:66657,68565,68571,68582` 不傳也合。`_codeloop_guard_verdict` 唯一呼叫端 `scripts/lumos:47790` 簽名沒動。原始碼順序測試 `t_lint_new_gate`(`scripts/test_lumos.py:50399`)找 `dv = _dispositions_verdict(` 這串,多行 lambda 後仍在。
- (2) 掛鉤與 CI:`scripts/hooks/pre-push:456` 傳 `--diff "$_brange" --at-sha "$_lsha"`、`.github/workflows/ci.yml:186` 傳 `"$BEFORE..$SHA" --at-sha "$SHA"`,兩者終點都等於 `--at-sha`,起點在非首推情形都是遠端舊頂端 = 合併提交的第一個母,與設計一致。CI `fetch-depth: 0`,淺 clone 條件不會誤觸。
- (5) reason 字串:`scripts/hooks/pre-push:469` 用 `grep -q "tier=high 且"`、受波及合約用 `grep -m1 '受波及合約的測試沒過'`,都是前綴或子字串比對,後綴不影響;`scripts/test_lumos.py:37967` 的守護測試比對的是 `"tier=high 且無留痕(尚未跑 code-loop pass/skip)"` 子字串,仍成立;`25508` 的測試比對「留痕」「過時」「壓過提交」「code-loop pass」,後綴不影響。`.github/workflows/ci.yml:189` 的 `::error::` 是固定文字,不依賴 reason。`_codeloop_marker_skipped` 會把較長的 reason 寫進治理帳(env 跳過那筆),長度變長但無解析者(grep 全 repo 找不到解析「尚未跑 code-loop」的下游)。

總結:整合面乾淨,沒有被打壞的呼叫端、掛鉤、CI 或測試;只有訊息對一般推送變吵、skills 與落點筆記沒同步講清楚涵蓋範圍(squash 合併不適用、全零/無範圍不認)、兩關共用期限起算點三個 minor。
