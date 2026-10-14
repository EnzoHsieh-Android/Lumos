severity: major

已實測作者的數字、單行超長的讀法,以及處置閘在推送前重複呼叫的耗時。我跑了真實 CLI(`loop status --disposal`),它寫了兩行治理帳。我已用 `git checkout` 還原,spec-gate-nondo 工作樹現在乾淨。

## Finding 1:單行超長時,64KB 區塊讀法的記憶體和耗時是平方成長

severity: major
blocking: 是 — 逐塊 `buf += blk` 每塊都複製整個已累積的緩衝,一行夠長就吃掉數 GB、數十秒,誠實操作被記憶體與耗時擋下
引句:「        buf += blk」
問題:`_ledger_physical_lines` 的註解與常數寫「一行比它長就照那一行的長度留」,也就是記憶體只跟那一行一樣大。實際上 `bytes` 的 `+=` 每次都新配一份,把前面累積的全部複製過去,所以耗時是 O(行長²/64KB),峰值記憶體是行長的 20 到 65 倍。`scan` 只省了重掃換行的成本,沒省複製。
具體失敗情境:我把該函式從 `scripts/lumos` 原樣取出,餵單行檔實測,數字如下。

| 單行大小 | 耗時 | 峰值 RSS |
|---|---|---|
| 10MB | 0.13 秒 | 364MB |
| 30MB | 1.78 秒 | 1.9GB |
| 100MB | 19.65 秒 | 6.5GB |

- 讀帳核心 `_canary_ledger_rows` 由 loop next、loop status 與推送前檢查共用,任何一條路碰到這種行都會一起卡住或被系統砍掉。
- 帳檔被寫成單行、或換行符掉光時,這是誠實操作會踩到的情境。
- 建議改法:用 `bytearray` 或 list 累積區塊,最後才 `b"".join`。
- 純 `\r` 行尾的 42MB 帳(88 萬行)沒問題:1.0 秒、80MB。作者的「平均行」數字我認,問題只在單行超長。
- 佐證:file: `scripts/lumos:13900-13925`(`_ledger_physical_lines`);file: `/tmp/code-規格閘不做節-r9-repair.patch:1056`

## Finding 2:推送前多份計劃各走處置閘時,每份都重讀整本治理帳

severity: minor
blocking: 否 — 只是重複讀取,每份多 0.3 秒左右,沒有失控,也不會擋下誠實操作
引句:「    (b) 這個編號加 -std(或原編號自己帶輪次)的完整設計審過了處置閘」
問題:第 8 步 `_disposal_retro_step` → `_cap_retro_status` 沒傳 events,所以每次都呼叫 `_retro_gov_events`,把 `docs/.governance-log.jsonl` 整本讀進記憶體再切行。作者省掉的是審查帳的重讀,治理帳沒省。
具體失敗情境:
- 這個 repo 的治理帳是 20MB,單次讀取 0.26 到 0.34 秒、約 117MB RSS。
- 10 份計劃都走 -std 就多約 3 秒。
- 實跑一次 `loop status --disposal`(`design-必要合約清單`),整次 3.8 到 3.9 秒、約 400MB。其中 CLI 啟動就佔 1.6 秒。
- 沒有重複跑測試:處置閘路徑裡沒有 subprocess。
- 每份計劃重讀自己的審材與快照,這是必要的,不算重複。

## 已讀,無 finding

- 推送前 -std 出口從 `ctx["by_loop"]` 取列,沒有再叫 `_loop_status_read` 重讀審查帳。
- `_disposal_judge` 有三處呼叫:
  - `loop status --disposal`:讀一次帳。
  - `loop next`(行 16365-16367):作者說明的第二次讀帳。
  - 推送前出口:不重讀。
  審查帳只有 4.6MB 時,這幾次讀帳的耗時可以忽略。
- 處置閘內的 `_escape_rows_for`、條款綁定、落點、資安席都只讀單一計劃檔,沒有掃整庫。
- `_strip_zero_width`:ASCII 走快路徑;非 ASCII 是逐字元 O(n),沒有資源問題。
- 區塊結尾剛好是 `\r` 時的延後切行邏輯,沒有無限迴圈或漏行。

最高等級 major,blocking 1 條。
