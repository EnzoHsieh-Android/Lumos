severity: major

圖譜鏡頭(固定席節點):派工尾端沒有附固定席節點,這條不適用。spec 自己點名的 `t_prepush_gates_stop_on_signal` 和 `t_prepush_cheap_gates_run_before_expensive_suite` 我有逐條判,結論在 F2。

1. 預演(push-preview)會跑會寫帳的閘,污染治理帳、逃逸帳和版控檔
   - spec 段落:「做法 5」、「實務隱患」的「已排除:對外送出」
   - 問題:預演帶 `LUMOS_PUSH_PREVIEW=1` 跑整支掛鉤到統一判斷為止。這段路上的閘大多會寫帳,spec 沒提。寫帳的程式見下面的 file 行。
   - 污染方式一:預演擋下時,`blocked` 事件(`hard=True`)落進進版控的 `docs/.governance-log.jsonl`。一次沒推出去的預演就讓工作目錄多一個已修改的追蹤檔,和 `Backend_improve` 現在 `git status` 的 `M docs/.governance-log.jsonl` 同型。
   - 污染方式二:預演帶了 `LUMOS_PUSH_ATTEMPT`(掛鉤匯出),事件裡沒有任何「預演」標記,`lumos gov` 的統計把它當成真推送被擋。
   - 污染方式三:逃逸自動記帳(`loop escape --auto --stage push-gate`)寫在掛鉤本體裡,預演會照跑。逃逸帳的語意是「下游推送閘抓到洞」,但預演沒推送。去重鍵是 loop、stage、sha,預演先記一筆,同 sha 的真推送再被擋時印「已經記過,不重複」,真事件被預演吃掉。
   - 污染方式四:預演時若設了 `LUMOS_SKIP_DRIFT_CHECK` 或 `LUMOS_SKIP_REREAD_CHECK`,會寫 `skipped-env` 事件。
   - 具體時序:使用者連跑三次 push-preview,每次圖譜健檢都擋。治理帳多出三份 `doctor`/`anchor` 的 blocked 事件,追蹤檔變髒。同一 sha 若是「受波及合約的測試沒過」,逃逸帳也多一筆。
   - spec 的 S5 只驗「不推送、不跑測試」,沒有任何條款驗預演不寫帳。
   - 引句:「預演不推送;只有真推送才連遠端,行為照舊。」
   - file: `scripts/lumos:1639`(`_append_governance_log` 的寫者=doctor --ci)
   - file: `scripts/lumos:27538`(anchor verify 失敗時寫 `anchor` `blocked`)
   - file: `scripts/lumos:37113`(reread-check 寫 `note-reread` 事件)
   - file: `scripts/lumos:40808`(drift-check 的 `skipped-env` 事件)
   - file: `scripts/lumos:1341`(事件帶 `LUMOS_PUSH_ATTEMPT`)
   - file: `scripts/hooks/pre-push:462`(逃逸自動記帳的 `loop escape --auto`)
severity: major
   - blocking: 是 — 預演的核心承諾是無副作用,卻會寫真推送才該寫的帳,而且沒有條款或測試驗

2. 收集模式下 Ctrl-C 或被 kill 打在 anchor verify 或 doctor 上,不會停下,而且暫存目錄已被刪光
   - spec 段落:「做法 1」、「做法 3」、S3、S6
   - 問題:spec 說「每一處原本的 `exit 1` 都換成同一個呼叫」,又說中斷「維持立刻結束」。但「立刻結束」只靠 `pp_stop_if_signaled`,而掛鉤裡只有 home check、note-shape、spec-gate、code-loop、drift、reread 這六處接了它。`anchor verify` 和 `doctor --ci` 是 `if ! "$PY" ...` 的寫法,沒有取 rc,也沒接 `pp_stop_if_signaled`。現況下它們被 Ctrl-C 殺掉會落到 `exit 1`,等於停下。改成「記下、繼續」後,rc=130 被當成一筆普通擋下,掛鉤繼續往下跑。
   - 更糟的是 `trap '...' EXIT INT TERM` 掛了 INT/TERM。我用 bash 實測:子行程被 SIGINT 殺掉時,trap 執行完會繼續往下跑,不會結束。所以流程是 trap 先 `rm -rf "$_PP_TMP"`,然後繼續進入 home check、spec-gate 等閘。
   - spec-gate 的 `tee "$_PP_TMP/sg-$RANDOM.log"` 寫進已不存在的目錄,`pp_touched_file` 的 touched.txt 也沒了。後面的閘在殘缺環境下跑,結果不可信。
   - 具體時序:使用者看到 doctor 跑很久,按 Ctrl-C。doctor 回 130,被記成一筆「擋下」。掛鉤繼續跑 home check、drift(最壞 60 秒)、reread。使用者得再按一次,最後印出「共有 N 道擋下」的彙總,其中有一條是 Ctrl-C 偽造的 doctor 擋下。
   - 這違反 S3 的精神。S3 只驗找不到 Python 3.14,沒有驗 anchor 或 doctor 被訊號殺掉。
   - 對 `t_prepush_gates_stop_on_signal` 的判斷:spec 說它「斷言照舊要綠」。它只覆蓋已接 `pp_stop_if_signaled` 的閘,所以會繼續綠,但抓不到這個缺口。
   - 引句:「使用者中斷(`pp_stop_if_signaled`,回傳碼 128 以上)——這幾種後面什麼都跑不了或不該再跑,維持立刻結束。」
   - file: `scripts/hooks/pre-push:217`(`if ! "$PY" "$GRAPHCTL" anchor verify` 沒有 rc 與訊號判斷)
   - file: `scripts/hooks/pre-push:316`(`doctor --ci` 的判斷同樣沒有訊號判斷)
   - file: `scripts/hooks/pre-push:230`(`trap 'impact_done; rm -rf "$_PP_TMP"' EXIT INT TERM`)
severity: major
   - blocking: 是 — 中斷會被記成擋下並繼續跑,暫存目錄也已被刪,和 spec 自己的「中斷立刻結束」衝突

3. 「時間」一節的數字漏算,多 ref 時最壞耗時與全套測試同量級
   - spec 段落:「實務隱患」的「時間」
   - 問題:spec 把多出來的時間算成「十幾秒、漂移最壞每個分支 60 秒」。但逐 ref 迴圈裡每個 ref 還要跑下面這些:
     - 漂移之前算範圍的 git 呼叫,每次最多 20 秒逾時。
     - 回頭重讀的軟上限約 30 秒。
     - `spec-gate --push-check`(要跑條款測試,耗時 ⚠ 沒有逾時上限可查)。
     - code-loop `--collect` 在合約測試先紅時,還要照樣算分級再判第四道。
   - 以前第一個 ref 的 anchor、doctor 或 home check 一擋就結束。現在擋下後仍會跑完所有 ref 的所有閘。
   - 最壞算式(不含 spec-gate):每個 ref 最壞 60+20+30=110 秒,5 個 ref 約 550 秒,約 9 分鐘,超過 spec 想省下的全套測試(約 8 分鐘)。
   - 以前 anchor 只花 0.2 秒就能擋下的推送,現在最壞要等 9 分鐘以上才看到原因。
   - spec 沒有整體時間預算或單道逾時上限,也沒說多 ref 時是否先處理能擋下的 ref 就收手。
   - 引句:「多跑的只有本來就要跑的便宜閘(全部約十幾秒、漂移最壞每個分支 60 秒)」
   - file: `scripts/hooks/pre-push:505`(漂移註解寫明預算外的 git 呼叫每次最多 20 秒、一次推多個 ref 會相加)
   - file: `scripts/hooks/pre-push:535`(reread 註解寫明最多約 30 秒、逐 ref 各跑一次)
severity: minor
   - blocking: 否 — 只是時間估算錯,不會讓擋下變放行,補上預算數字就能收

4. push-preview 查不到遠端時,把網路失敗當成「新分支」
   - spec 段落:「做法 5」
   - 問題:「遠端查不到那個分支就當新分支,遠端提交填全零」沒有區分兩種情況。一種是遠端確實沒有這個分支,另一種是離線、認證失敗或逾時。後者也會被當成新分支,範圍改從合併基底或空樹算,多掃一大段歷史,預演可能報出真推送不會有的擋下。
   - spec 也沒說連遠端的查詢有沒有逾時。離線時 `git ls-remote` 可能卡很久,Ctrl-C 時預演的回傳碼是什麼也沒定義。
   - 這點是預演「結果可信」的前提,目前沒有任何條款覆蓋(S5 只驗遠端沒有該分支的情況)。
   - 引句:「遠端查不到那個分支就當新分支,遠端提交填全零」
severity: minor
   - blocking: 否 — 只影響預演的準確度,不影響真推送的把關

已讀,無 finding 的部分:
- 多 ref 共用暫存檔會不會互相蓋:沒問題。`_PP_TMP` 每次 `mktemp -d`,兩個 push 同時跑各用各的目錄;spec-gate 的 log 在目錄內再加 `$RANDOM`;`impact_once` 的暫存檔是獨立的 `mktemp`。多個 ref 共用 `_PP_BLOCKS` 陣列只在同一支 shell 內,不跨行程。
- `pp_record_block` 若被呼叫在子 shell 內會丟失累積:spec 沒有要求這樣用,現有各閘的 rc 判斷都在主 shell,已讀,無 finding。
- 找不到 `scripts/lumos` 仍 `exit 0`、找不到 Python 3.14 立刻 `exit 1`、暫存目錄建不起來 `exit 1`:與程式現況一致,已讀,無 finding。
- 對 `t_prepush_cheap_gates_run_before_expensive_suite` 的判斷:不影響。擋下時仍不跑全套,只是擋下前多跑便宜的閘。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
