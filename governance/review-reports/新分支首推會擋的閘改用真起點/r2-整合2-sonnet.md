severity: major

鏡頭:整合與知識同步(三個月後接手的人)。對照 repo:/Users/enzo/harness/lumos-firstpush(唯讀,實驗在 mktemp clone)。

圖譜鏡頭說明:派工時 hook 沒有附上合約/事故節點。我自己對照了三個相關節點:Systems/每支檔有家 的 KEY(「兩套刻意不同、別合併」)、Systems/存量漂移守衛 的 PITFALL(「起點只在 `_push_range_start` 算一處」)、Systems/bound-tests-gate 的「新分支首推」那條。本案不合併 `_range` 與 `_hrange`,而是新增 `_brange`,也沒有另寫起點算法,三者都不影響。每支檔有家那條的「新分支從空樹掃」會過期,見 F5。

## F1 空樹在 SHA-256 repo 會被寫死成 SHA-1 的那個
severity: major
blocking: 是——會讓會擋的閘在 SHA-256 repo 靜默失效,且修法只要一句話。
spec 段落:做法第 1 點。
引句:「空樹照本 repo 的雜湊算法」
問題:spec 只規定「判不了」那一支用 `_drift_empty_tree`。但 `_push_range_start` 本身在三處回傳寫死的 SHA-1 空樹常數 `_EMPTY_TREE_SHA`:`scripts/lumos:41801`(舊式主線判法的後備)、`scripts/lumos:41916`(新分支首推找不到主線)、`scripts/lumos:41922`(舊值找不到而且沒有父提交)。cmd_push_range 若照 spec 把「起點」原樣印出,SHA-256 repo 會得到 `4b825dc6…..<64 位頂端>`。
具體例:SHA-256 repo、新分支首推、遠端與本機都沒有主線 → push-range rc0,印 `4b825dc642cb6eb9a060e54bf8d69288fbee4904..<64hex>`。這行符合掛鉤的形狀正則 `^[0-9a-f]{40,64}\.\.[0-9a-f]{40,64}$`,所以被採用。之後 `git diff`、`pitfalls --diff` 都認不得這個物件,而掛鉤對 pitfalls 是 `|| true`,結果 pf_json 為空,分級放行,code-loop check 也算不出範圍。今天的 `pp_range_for` 用 `git hash-object` 算空樹,這個情形是對的。所以改了以後,SHA-256 repo 的新分支首推會從「全掃」變成「靜默不查」,方向反了。存量漂移檢查沒有這個問題,因為 `_note_audit_resolve`(`scripts/lumos:30940` 一帶)在最後把 `_EMPTY_TREE_SHA` 換成 None。
預期:cmd_push_range 對「起點等於 `_EMPTY_TREE_SHA`」一律換成 `_drift_empty_tree(repo)` 再印,不只對判不了那支;S6 加一條 SHA-256 repo 的案例。

## F2 push-range 被訊號中斷時,掛鉤會把 Ctrl-C 當成「退回空樹」往下跑
severity: major
blocking: 是——違反掛鉤已寫明的慣例,而且 spec 沒有對應條款。
spec 段落:範圍(pp_block_range_for)、做法第 2 點。
引句:「其他情況(舊版 lumos 沒有這個指令、失敗、印出怪東西)退回」
問題:掛鉤有明文規矩:`scripts/hooks/pre-push:39` 一帶的 `pp_stop_if_signaled` 註解寫「回傳碼 128 以上是被訊號殺掉——那不是工具錯誤,不能當成放行往下跑」,每支會擋的閘都先過它。`pp_block_range_for` 是在 `$(…)` 裡跑的,spec 把「失敗」一律併成退回空樹,沒有區分 rc≥128。
具體例:新分支首推時使用者在 push-range 執行中按 Ctrl-C。lumos 回 130,掛鉤把它當「失敗」改用空樹。因為 `pp_block_range_for` 在子 shell 裡,整支掛鉤不會停,後面的閘用整個 repo 的範圍照跑。既有測試 `t_prepush_gates_stop_on_signal`(`scripts/test_lumos.py:55755`)用 FAKE_SIG_CMD 逐個閘驗「被殺就停」,新指令不在清單內,spec 的 S1–S7 也沒有「被訊號殺掉」那條。
預期:`pp_block_range_for` 對 rc≥128 要讓呼叫端 `exit`(函式在 `$(…)` 裡,要把 rc 帶出來再由迴圈本體交 `pp_stop_if_signaled`);驗收條款加一條「push-range 被 SIGTERM/SIGINT 殺掉 → 掛鉤停下、不放行」,並把 FAKE_SIG_CMD=push-range 加進 t_prepush_gates_stop_on_signal。

## F3 七個吃 `_brange` 的呼叫端只有一支測試,換回舊範圍時多半不會翻紅
severity: major
blocking: 是——全域規則要求每條相似路徑各一支先紅的測試。
spec 段落:範圍(「吃 `pp_block_range_for` 的」那條)、驗收條款。
引句:「做:吃 `pp_block_range_for` 的:`pp_touched_file`」
問題:掛鉤裡吃範圍而且會擋或影響擋的呼叫是 `pp_touched_file`(doctor `--touched-from`,`scripts/hooks/pre-push:289`)、`impact_once`(`:371`)、pitfalls --json(`:372`)、高風險列命中那次(`:384`)、`spec-gate --push-check`(`:396`)、`code-loop check --diff`(`:423`)、兩處 `loop escape --range`(`:432`、`:438`)。我逐一對過,分類是對的:沒有漏掉會擋的呼叫;`:458` 的 tag 分支 pitfalls、`bound_tests_advisory`(`:462`)、`test-layers`(`:520`)確實只提醒;drift check 與 reread-check 已自帶 `--push-remote/--pushed-ref`,不吃。問題在驗收:S1–S5 全綁同一支 `t_prepush_new_branch_block_range`,條款文字只講「風險分級」和「照擋」。
具體例:實作者只改 pitfalls 那行、漏改 `pp_touched_file`,或把 `spec-gate --push-check` 留在 `$_range`。S1 的新分支夾具裡沒有逾期的預告合約、也沒有雙向門計劃,這兩條路不會翻紅,新分支首推時 doctor 與 spec-gate 仍吃空樹。
預期:夾具各放一個只有空樹範圍才會觸發的誘餌(別人逾期的預告合約給 doctor、一個 doing 且留痕過期的雙向門計劃給 spec-gate、一個會紅的受波及合約測試給 impact_once/code-loop check),每個消費者各一條 [S] 條款,並要求把任一呼叫端改回 `$_range` 時恰好那一條翻紅。

## F4 新增頂層指令會讓兩支既有測試立刻翻紅,寫回清單沒列
severity: major
blocking: 是——不補,第一次跑全套就紅。
spec 段落:做法第 6 點。
引句:「`push-range` 指令的家(`scripts/lumos` 的家,先查是哪篇)」
問題:這句是未完成的占位,沒有定案。而且清單漏了兩件機械守衛會抓的事:
①`t_command_index_complete`(`scripts/test_lumos.py:8127`):`skills/lumos-project-notes/commands/*.md` 必須出現 `lumos push-range`,否則紅。要補進 `commands/06-代碼審與推送.md` 或 `commands/08-自動跑的.md`。後者的 pre-push 那一列正在逐條列掛鉤呼叫的指令,也該加上 push-range。
②`t_docs_command_count`(`scripts/test_lumos.py:26404`):文件寫的「N 個頂層命令」要跟 `--help` 實數一致。現在是 80:`ARCHITECTURE.md:108、112、142`、`skills/lumos-project-notes/reference.md:117`。加一個命令後必須全改 81(`docs/指令參考.md:15` 寫「七十來個」,不用動)。
家的建議:`Systems/存量漂移守衛` 的 about_code 同時列了 `scripts/lumos` 與 `scripts/hooks/pre-push`,而且 `_push_range_start` 的脈絡(起點只算一處、四個坑)全在它那裡,push-range 的說明放那裡最合適。每支檔有家是「改到哪支檔就寫進它的家」,所以放哪篇要在計劃裡寫死,不留「先查」。

## F5 寫回清單缺的過期句子與註解
severity: minor
blocking: 否——都是文字同步,不影響行為;但接手的人會被舊句誤導。
spec 段落:做法第 4、5、6 點。
引句:「`_range` 那段註解改寫:只列真的只提醒的幾道」
問題:實際會變錯的句子不只那一段:
a. `scripts/hooks/pre-push:309-312` 開頭的長註解寫「無基準(新 ref/缺物件)倒向保守掃 empty-tree..local_sha」。改完它描述的是只提醒那幾道,不是會擋的幾道,也要改。`pp_range_for` 上方註解(`:36-38`)「新 ref…保守掃全部引入內容」同理。
b. `Systems/每支檔有家` 的 KEY(第 33 行附近)寫「推送前腳本裡另有一套範圍……新分支從空樹掃」,spec 第 4 點只提註解,圖譜這句沒列。這句會變成事實錯誤。
c. `Systems/bound-tests-gate` 的「新分支首推:起點是空樹時改用主線 tip(`_mainline_ref`)」(約第 74 行)。impact_once 改吃 `_brange` 後,新分支首推幾乎不再收到空樹,這句要改成現況。
d. `Systems/pitfalls-code-loop` 第 32 行的 PITFALL 講「code-loop check --diff 起點是 40 個 0」,現在掛鉤這條路先換了起點才交,要補一句。
e. `_push_range_start` 的 docstring 寫「那三道還沒驗證合過主線時會不會多算」,`_lens_push_base` 的 docstring 寫「推送前掛鉤與 CI 的存量漂移檢查不走這支」,現在掛鉤的會擋閘也走 `_push_range_start`(經 push-range),兩段都要加。
f. 舊單 `Issues/推新分支時風險分級拿空樹當起點` 的 DECISION 行寫「傾向 2(只改訊息)或 3(不做),不傾向 1(改範圍)」,結案時要明改成「採 1,但用 `_push_range_start`」,不然 DECISION 與結案互相矛盾。Issue 摘要裡寫的「新分支首推 tier 判 high」那個數字(1841 vs 25)也可以留作驗收對照。
g. `Issues/推送前其他閘的範圍在合過主線時會多算`:本案是第三個呼叫點(`_brange`),它的收斂路清單要加上這一處,spec 只在每支檔有家註解提到。
預期:寫回清單逐條補上 a 到g。

## F6 `lumos update` 分發:無需另設機制,但要寫明前提
severity: minor
blocking: 否——現況已經成立,只是 spec 沒寫依據。
spec 段落:實務隱患「舊版 lumos」、回退。
引句:「消費專案先拿到新掛鉤、lumos 還是舊版時」
問題:`scripts/hooks/pre-push` 與 `scripts/lumos` 都在 `_VENDORED_TREE_FILES`/`_VENDORED_TOOLKIT`(`scripts/lumos:20687`),`lumos update` 一次整批覆蓋兩支,所以正常更新不會出現「新掛鉤配舊 lumos」。這個情況只會在 `--allow-stale`、手動只換掛鉤、或 update 中途失敗時出現,fallback 到空樹是對的(我用假 lumos 驗過,`t_prepush_computes_impact_once` 的假 lumos 對 push-range 印空、rc0,形狀檢查不過,退回空樹,測試不翻紅)。slim 版沒有 pre-push(`slim/README.md:246`),不受影響。另外 `scripts/hooks/pre-push` 在 ANCHOR_FILES(`scripts/lumos:22302`),改它會牽動錨點基線,收工要照既有流程重鎖。
預期:spec 補一句「兩支同批分發、正常更新沒有版本錯位」並列出錨點重鎖。

## 一致性核對
- 新指令參數與 drift check、reread-check 的規矩一致:兩個旗標必須一起給(`scripts/lumos:35781`、`:31995`、`:32179` 同款訊息、rc2)。已讀,無 finding。
- 掛鉤傳參:`$_PP_REMOTE`(`:58`)、`$_rref` 與 drift check 同一組,一致。注意 `pp_touched_file` 現在讀的是 `read -r _ _lsha _ _rsha`(`:73`),spec 第 3 點要改成多讀 `_rref`,spec 已寫。
- 順序:spec 第 3 點寫「迴圈裡每個 ref 算一次 `_brange`」,實作要放在 `[[ -z "$_EMPTY_TREE" ]] && continue`(`:324`)之後,不然空樹算不出時 fallback 會是 `..頂端`。spec 沒寫順序,實作者容易放到前面;屬可執行性提醒,併入 F3 的實作清單即可。
- 既有 pre-push 測試會不會翻紅:`t_prepush_range_scan`(新 ref 全零、tag)夾具沒有遠端也沒有主線 → push-range 走 `_push_no_mainline` 全零 → 空樹 → 同今天,不翻紅(SHA-1 repo)。`t_prepush_passes_touched_list_to_doctor`、`t_prepush_drift_range_ref_shapes` 都是一般增量或自帶參數,不受影響。假 lumos 類測試(`_dr_hook_fakes`)對未知子指令印空 rc0,走 fallback,不翻紅;但它們的 argv 記錄多一行 push-range,凡是用 `lines[0]` 或精確行數斷言的要檢查,我沒找到這種斷言。
- 空範圍 `頂端..頂端` 實測:我在 clone 裡用 `X..X` 跑 `pitfalls --diff --json`(tier light、suite docs)、`code-loop check`(OK)、`spec-gate --push-check`、`impact`、`test-layers`,全部 rc0、不崩。

## 實務隱患逐類
- 舊版 lumos、標籤、時間:spec 已寫,對照程式成立。
- ⚠ 空範圍時 doctor:`pp_touched_file` 在範圍為空(新分支頂端已在主線、或標籤打在主線上)時 `rm` 掉清單並回空字串(`:77-78`),掛鉤因此不帶 `--touched-from`,doctor 退回「CI 式擋全部」。今天空樹範圍下清單是整個 repo 的檔,所以不會落到這條。判不準這是否算新的誤擋(那些逾期合約在 CI 也會擋),標 ⚠,不列為 finding。建議在標籤與「頂端已在主線」的案例補一條行為宣告。
- 金流、對外送出、不可逆:無,理由同 spec(只改範圍推導與一個唯讀指令),我複核成立。

## 逐節
- 前言/白話:已讀,無 finding。
- 範圍:F2、F3。
- 做法:F1、F4、F5。
- 實務隱患:F6(⚠ 見上)。
- 驗收條款:F3。
- 回退:已讀,無 finding(退回後消費專案要重跑 `lumos update` 一句成立)。
- 天花板:已讀,無 finding。
- 審計修正紀錄:已讀,無 finding。引用的卷證目錄 `governance/review-reports/新分支首推會擋的閘改用真起點/` 我沒有逐一開檔核對。

最嚴重 severity: major;blocking 共 4 條(F1、F2、F3、F4),minor 2 條(F5、F6)。
