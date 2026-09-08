severity: minor
# r1 架構對齊席(sonnet)——棧別提問表態閘


## 問1:分層與依賴方向

對齊。寫側 `code-loop pass --dispositions` 明白限定「只驗形狀、不對照 diff」，讀側 `code-loop check` 才做 diff 命中比對與存在性核對，跟 `cmd_code_loop`（file: `scripts/lumos:20728`）現有的 pass=寫/check=判定分工一致；check 端核對 `Issues/<名>` 也刻意聲明「不載入圖譜」，呼應 `_pitfall_diff_mode`/`--check` 一貫的 vault-free 快路徑（file: `scripts/lumos:16669`）。沒看到跨層直呼——check 不做寫入、pass 不做 diff 掃描。

引句:「pass 不一定知道 diff；「鍵對不對得上命中的問題」是 check 的事」
引句:「只查檔案路徑存不存在、不載入圖譜——check 跑在 pre-push，載入整個圖譜要好幾秒」

## 問2:命名與錯誤處理

### A1 fail-open 事件的 kind 字面值
severity: minor
blocking: 否——只是帳本分桶名對不上，實作者照鄰居寫就對。
不對齊（minor）：「閘自己出內部錯誤 → fail-open 放行但寫治理帳 `warned`」跟本家族既有寫法不符——`_codeloop_guard_verdict` 自己內部出錯時呼叫的是 `_gate_failopen`，寫進帳的 `kind` 字面值是 `"fail-open"`，不是 `"warned"`（file: `scripts/lumos:20562`，`_gate_event_or_warn(repo_root, gate, "fail-open", why, hard=False)`）；`gov --stats` 也把 `"fail-open"` 當獨立分桶統計（file: `scripts/lumos:4537`）。這道閘就活在 code-loop 這個家族裡，最近的鄰居用 `fail-open`，不是 `warned`。

引句:「閘自己出內部錯誤 → fail-open 放行但寫治理帳 `warned`，同其他閘慣例。」

### A2 ⚠ 三值詞彙 vs 處置閘的 folded/accepted
severity: minor
⚠ 判不準，交編排者：`satisfied|na|todo` 三值沒有沿用處置閘既有的 `folded_set`/`accepted_set` 詞彙（file: `scripts/lumos:5167`）。但這可能是合理分岔——findings 的處置只有二元（折/接受），提問的表態需要三元（做到/不適用/待辦），spec 也明白自稱是「把發現換成提問」而非 literal 複用同一詞表，所以不機械判為不一致。

## 問3:第二種做法

對齊，沒看到新機制。存在性核對直接借 `_validate_repo_ref` 的 `path:line` 格式與 ok/missing/line_out_of_range 語意（file: `scripts/lumos:14668`），`test:<名>` 借 `discover_test_methods`（file: `scripts/lumos:3597`），留痕沒開新帳本而是替 `governance/code-loop/<branch>.json` 加 `dispositions` 欄、走既有 `_codeloop_write`/`_codeloop_gov_log`（file: `scripts/lumos:20170`），統計沒開新入口而是在 `_render_gov_stats` 裡加一段（file: `scripts/lumos:4444`，該函式已有 finding_kinds/refute_verdicts 兩段同形先例）。「每問要有表態」的判定邏輯雖不是直接呼叫 `_loop_status_disposal`，但那支處置閘吃的是 canary 輪次的 findings_set/hash 鏈，資料形狀完全不同，spec 也明講是借用「處置閘」這個設計而非搬那份程式碼，屬於家規允許的 borrow-design。

引句:「本案只是把「發現」換成「提問」；錨點借 refcheck(存在性)與 discover_test_methods(測試名);留痕借 code-loop ledger JSON 加欄+治理帳事件」

不對齊共 2 條，其中 major 0 條
