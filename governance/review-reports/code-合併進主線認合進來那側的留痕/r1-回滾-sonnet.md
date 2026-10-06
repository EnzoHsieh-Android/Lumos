severity: minor

## F1 放寬與重構綁在同一提交,沒有開關或環境變數只關放寬
severity: minor
blocking: 否 — 退得掉(整個提交 revert 即可),只是粒度粗;重構本身對舊行為等價,連帶退回無害
引句:「def _codeloop_ledger_events(text, kinds):」
file: `scripts/lumos:46694`(新共用讀帳函式;兩支既有讀帳函式已改走它)
file: `scripts/lumos:47447`(現存唯一跳閘是既有的 `LUMOS_SKIP_CODE_LOOP=1`,它是跳整個留痕要求,不是只關合併放寬;且要先跑完 merge-side 判定才輪到它)
說明:查過全檔,沒有 `MERGE_SIDE` 之類開關。要只關放寬,得在 `_codeloop_merge_side_lookup` 開頭自己加一行 return,或 revert。設計稿〈回退〉寫「退回本案的提交即可:只改推送檢查的判定,不寫資料、不改帳本格式」,我核對屬實(見 F2),所以整包退回是安全的。重構後讀帳語意:舊 `_codeloop_read_dispositions` 沒檢查 head_sha 是不是字串,新版多了 `isinstance(..., str)` 與預篩要求同時含 `"code-loop"`,對真實帳行同義、只會更嚴;不構成退回時的差異。

## F2 放寬期間沒有新事件種類或欄位寫進治理帳,只有既有 skipped-env 的 detail 文字變長
severity: minor
blocking: 否 — 舊版讀得懂;無資料遷移
引句:「reason = f"{reason};{why}"」
file: `scripts/lumos:47447`(`_codeloop_marker_skipped` 把 reason 原樣塞進 `skipped-env` 事件的 detail)
說明:merge-side 放行時是 `return ok_v` 直接回,沒有呼叫任何 `_gate_event_or_warn`,所以放行本身不寫帳;放行的依據是既有分支名下的 passed/dispositions 紀錄。唯一的新字串落點:擋下路徑(所有 tier=high 的擋下,不只合併提交)的 reason 現在多接「;為什麼沒認合進來那一側」,若同時設了 `LUMOS_SKIP_CODE_LOOP=1`,這串會進 `skipped-env` 的 detail(只是 detail 字串,kind/gate/欄位不變)。舊版讀帳端只看 kind/gate/branch/head_sha,不解析 detail,故讀得懂。副作用:所有舊版擋下訊息(例如「tier=high 且無留痕(尚未跑 code-loop pass/skip)」)尾端多一段,依賴整句完全相等的外部腳本會變;repo 內只有 `scripts/test_lumos.py:37967` 是子字串包含判斷,不受影響。

## F3 退回後的時序:靠放寬合進主線的提交不會讓舊版之後每次推主線都紅,但混版本會出現「本機綠、CI 紅」
severity: minor
blocking: 否 — 無持久狀態;紅燈是一次性、同 PR #28 的既有形態
引句:「主線的推送檢查只讀 branch=main 的紀錄」
file: `docs/lumos-toolchain-knowledge/Projects/合併進主線認合進來那側的留痕_計劃.md:70`(天花板第 2 點已承認舊版 CI 對那次合併會紅)
說明:推送檢查只看本次範圍 `起點..目標` 的風險與目標名下的紀錄;那個合併提交一旦成為主線頂端,之後的推送範圍起點就是它,不再包含它,所以舊版後續推主線不會因它而紅。會紅的只有:(a) 該合併提交自己那次 push 的 CI 若跑舊版(退回之後才推、或消費專案的 CI 用 vendored 舊 script,本機 hook 卻用 symlink 新版),(b) 之後有人用跨過它的範圍重檢(例如起點更早的 force-push 或首推全零起點,而全零起點本案一律不認)。這兩種都是「本機放行、CI 擋」的時間差,rtb 這類消費專案透過 `lumos update` 升到新版、再退回舊版時,行為就是回到 PR #28 之前的:高風險合併請求一合進主線判留痕過時,補救是在主線補記或 `LUMOS_SKIP_CODE_LOOP=1`(會留 skipped-env 帳)。沒有任何殘留需要清理。

## F4 每次高風險擋下都多跑一輪 merge-side 判定,並新增一個 20 秒預算
severity: minor
blocking: 否 — fail-closed(判不了就不認),只多耗時
引句:「cache["deadline"] = _t.monotonic() + _DISP_BUDGET」
file: `scripts/lumos:46491`(`_DISP_BUDGET = 20.0`)
說明:`_codeloop_review_block` 對所有擋下(含非合併提交、沒有 raw_range)都先進 `_codeloop_merge_side_pass`,雖然前幾步(起點、母數)很快就 return,但要先做 `_lens_full_sha` 兩次與淺 clone 檢查的 git 呼叫。表態關與審查關各自一個 `_DISP_BUDGET`:表態那邊的 deadline 是 20 秒,merge_side lambda 另開自己的 20 秒,最壞單次檢查可到約 40 秒以上(讀約 19 MB 帳本走 `git show`)。逾時一律不認,不會誤放行,只拖慢;退回後這些額外 git 呼叫自然消失。

總結:退得掉,整個提交 revert 即可,沒有新帳本形狀、沒有持久狀態,舊版讀得懂;缺的只是「只關放寬不動重構」的開關,與混版本時本機綠 CI 紅的短暫時差,皆為 minor。
