severity: minor

我在實驗複本(clone)上對 r4 修補處做了變異測試。`lumos lint` 對計劃、`Systems/loop-convergence-recording`、兩篇 Issue 和 Verification 都是 0 問題。`lumos doctor` 圖譜健康 0 issues。`bound-tests --diff cb832b56..151c65b2 --advisory` 59 支合約測試全綠。`-k quote_full_span` 90 條斷言全綠。

計劃 S1–S8 的字面和各測試斷言對得上,`_quote_rows_legacy` 的函式本體和基線逐行比對只差函式名。Issue 的事實也核對過:判定檔 307 份中 rc1 有 5 份,名單與 Issue 一致;`--freeze` 只擋 rc2;`69d5fddf` 存在。手冊裡的 39/40/47 條與帳上折入數一致,兩份 `cap-retro.json` 都在卷證裡。

只有 minor,沒有 blocking。

1. 計劃說診斷指令那行帶 `[disposal] ` 前綴,程式沒有
severity: minor
blocking: 否
引句:「那行都帶處置閘各行共用的 `[disposal] ` 前綴(r3 規格符合席)」
file: `scripts/lumos:26525`
- 這句是 r4 修補新加進計劃〈判準版本蓋在帳上〉的。
- `_qdiag` 是 `_esc_clean(f"    診斷:lumos quote-check …")`,開頭是 4 個空格,沒有 `[disposal] `。
- 只有「引句判準:」那行(`print(f"[disposal] 引句判準:…")`)帶前綴。
- 變異 `_prov_path` 失敗時的實際輸出也佐證:`'[disposal] quote-check: ✗ …'` 之後接的是 `"    診斷:lumos quote-check …"`。
- r3 規格符合席只點了判準行,折入時把「這一行」也寫成帶前綴,計劃字面與程式不符。測試只比對 `診斷:lumos quote-check '…`,沒釘前綴。
- 該改計劃字面,或給診斷行補前綴並在測試釘住。

2. 比較模式「記憶體不足往外丟」沒有測試能翻紅,但筆記把測試綁上去了
severity: minor
blocking: 否
引句:「記憶體不足照常往外丟(處置閘、寫側、比較模式三處同一規則)」
file: `scripts/lumos:26756`
- 變異:把 `_quote_rows` 那兩行包進 `try/except Exception: cnt["unread"] += 1; continue`。`-k quote_full_span` 仍是 90 passed、0 failed。
- 處置閘有 `gm` 測試,寫側求 kind 有 `bm` 測試(我把 `except MemoryError: raise` 拿掉,它翻紅)。比較模式沒有對應的 MemoryError 測試。
- `Systems/loop-convergence-recording` 新增的 WHY 寫「三處一律照常往外丟」,並把 `t_quote_full_span_compare_and_event` 列為 `[test:]`。
- 這條對比較模式只有程式註解擋著,測試沒釘。

3. 診斷指令外層 `_esc_clean` 沒有測試,而且有損
severity: minor
blocking: 否
引句:「整行再過 _esc_clean(路徑裡的控制字元不印到終端;r3 資安席)」
file: `scripts/lumos:26525`
- 變異:拿掉外層 `_esc_clean(…, 2000)`,90 條斷言全綠。這個 r3 資安修補沒有守著它的斷言。
- 它換成空格會改掉引號裡的路徑。含 tab 或換行的路徑被 `_drift_sh` 加引號後,控制字元變空格,照抄的指令指向另一個不存在的路徑。
- 超過 2000 字時尾端接「…」,指令會壞。
- 只影響診斷提示,不影響判定。

4. 比較模式快照上限沒有測試
severity: minor
blocking: 否
引句:「_QUOTE_COMPARE_MAX_BYTES = 128 * 1024 * 1024」
file: `scripts/lumos:26727`
- 變異:`_read(sp, _QUOTE_COMPARE_MAX_BYTES)` 改成 `_read(sp, 10**12)`,90 條斷言全綠。
- 只有報告上限(`consts={"_QUOTE_COMPARE_REPORT_MAX_BYTES": 8}`)有測試。其餘讀檔相關的變異都能翻紅:報告上限、`_retro_read_bytes` 的 limit、repo 外路徑檢查。
- 計劃把「超過上限算讀不到」寫成快照與報告兩條。

5. Verification 紀錄的數字在 r1–r4 修補後過期
severity: minor
blocking: 否
引句:「八支驗收 78 條全綠」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-13_引句判準第一階段推送前驗證.md`
- 現在 `-k quote_full_span` 是 8 支、90 條。
- 「變異八處」的清單也沒涵蓋 r3、r4 新改的讀檔、診斷指令、片段濾 Cf/Co。這幾處的守衛強弱見第 2、3、4 條。
- 計劃〈量測〉的第一階段實測數字也是舊帳本的值:我在複本上重跑 `quote-check --compare-rules`,是 2639/366/24/43/237,耗時 22.6 秒、尖峰約 1.56 GB。計劃已寫明以指令輸出為準,REVISIT 2026-10-20 會重算,不算錯。
- 若以這份紀錄作為推送依據,數字應更新。

沒有發現的問題:
- 計劃的 `lands_in` 寫了 `Systems/design-loop`,第一階段按計劃本來就不動它,屬預期。
- `impact --sync-check` 列出的其餘「必看」節點是通用牽連,不在這輪合約範圍。
- 實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r4-合約-sonnet/` 已刪除。

總結:最高等級 minor,blocking 共 0 條
