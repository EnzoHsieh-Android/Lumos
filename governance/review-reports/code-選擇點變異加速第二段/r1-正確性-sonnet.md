severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/eebcc4fa….json.warming` 不存在,沒有鎖要處理。

我逐 hunk 走了邊界、資源、例外、冪等、新舊互讀、衍生資料、時間數字。在複本裡施兩處改壞後跑 `python3.14 scripts/test_lumos.py -k choice_kill_merge`,結果 191 passed、0 failed。程式行為上沒找到會判錯或損壞資料的輸入,只有下面兩條測試覆蓋缺口。我的複本已用字面絕對路徑刪除。

## Finding 1:中斷時記 `merge_off` 沒有測試守

引句:「        _kill_merge_off(mg, c.plat, "中斷")」

file: `scripts/lumos`(`_kill_merge_iter` 的 `try/except _KillHalt`,即 diff 第 941–945 行)

- 具體改壞:拿掉那個 `except _KillHalt: _kill_merge_off(...); raise` 區塊,改成直接 `raise`。
- 結果:整組 191 支全綠。
- 原因:`t_choice_kill_merge_interrupt` 的合併基準中送 SIGHUP 那案,只斷言 `interrupted` 與 rc 2,沒有斷言 run 事件的 `merge_off == {平台: 中斷}`。
- 這支測試的輸入只改了逐支那兩案,所以偏離 ⑦ 沒有讓它原本要守的東西失守。
- 但「中斷記 `merge_off`」是計劃〈做法〉3 列出的原因,卻沒有任何測試或驗收條款綁它。
- 這個漏洞不在 S10 的條款裡,所以不升 major。

blocking: 否(守的是計劃〈做法〉3 列的原因,不是驗收條款;給不出會做出錯行為的具體輸入)

## Finding 2:「基準量不齊」的時限提示串接沒有測試守

引句:「            return _kill_merge_off(mg, c.plat, "基準量不齊", need=c.merge_need)」

file: `scripts/lumos`(`_kill_merge_base`,diff 第 788–791 行),搭配 `_kill_merge_singles` 設定的 `c.merge_need`

- 具體改壞:改成 `return _kill_merge_off(mg, c.plat, "基準量不齊")`,也就是不帶 `need`。
- 結果:整組仍 191 全綠。
- 缺口:S7 只直接呼叫 `_kill_merge_ready` 驗「時限不夠」的提示。`基準量不齊` 那條路(用已量實測平均估 M、算 X)沒有測試。
- 同樣沒測試的原因字串:`指令形狀不支援`、`平台不穩或筆記未提交`、`讀結果檔的模組不在`、`結果資料夾不在工作樹`。
- 我追過這條路徑的算式,沒找到會算錯的輸入:
  - `c.merge_need` 在 `_kill_merge_singles` 每次迴圈先設好,收手時一定有值,且在 `_kill_merge_base` 開頭先清成 None。
  - X 一律 ≥ 已花秒數 + 約需秒數,所以照提示重跑不會再被同一道門擋下。

blocking: 否(只是覆蓋面可以更完整,提示字串錯了也只多印錯誤文字,不影響判定)

## 其他走過、判對的點

- **先紅順序**:
  - `_kill_merge_failed_first` 在 `how == "single"` 當下就回傳 list,不是延遲求值,下一個壞法清空 `c.merge_failed` 不會影響已交出的順序。
  - 編不過、沒跑乾淨、名單為空都走原順序。
  - `_choice_kill_judge` 用原順序 `order` 判,但同組第一個決定性結果(強殺掉、編不過、逾時)就 finish,rows 裡最多一筆決定性列,不會誤取。
- **`single_runs`**:
  - `_single` 只在 `hk.on` 且真的跑過單支的那條路徑設。
  - 合併判存活交的列、略過列、基準不綠的 abort 列都不帶。
  - `result_out` 的兩個呼叫端(`scripts/lumos` 27697、77195 附近)沒有 hooks,不會看到 `_single`。
  - `--json` 已過濾 `_single`。
  - `kill-log` 逐欄白名單寫入,不會洩出。
- **`merge_kind`**:鍵是 `(平台, group)`,每個平台組至多一筆。同一 group 在 `_kill_merge_chunks` 要「連續且 file、old、new、also 都相同」才併塊,不連續時後者覆蓋前者,屬既有行為。
- **新舊互讀**:
  - 新程式讀舊帳:`or {}` 與 `or 0`。
  - 舊程式讀新帳:`_gov_event_types_ok` 只檢查已知鍵,未知鍵忽略。
  - 別處沒有事件欄位白名單:`merge_tripped` 只在型別表、`_gov_row`、report 三處出現。
- **時間**:
  - S7 數字 (40+2535+60)=2635 進位為 2700,`need` 是精確浮點 2535.0,沒有進位誤差。
  - R 負數取 0。
  - 照提示重跑時 `remaining ≥ need` 成立。
- **資源與例外**:
  - `_kill_merge_off` 只算字串、印 stderr,沒有新子程序或暫存。
  - `_KillHalt` 重新丟出,不吞。
- **偏離 ⑦**:加 `__mfail__ = [alpha, bravo]` 讓逐支仍從 alpha 開始,「alpha 跑到一半收到 SIGINT、bravo 不能開跑」的守法完全保留。
  - 假如不改,名單會只有 [bravo],alpha 永遠不被跑,mark 對不到,測試會失去意義,所以改輸入是必要的。
- **測試時間**:`t_choice_kill_merge_failed_first` 在我這台跑 72 秒,工具提示餘裕只有約 3 倍。負載高時有逾時隨機紅的風險,但我給不出具體失敗輸入,不另列 finding。

## 圖譜固定席

這次沒有附固定席節點,無可逐條判。

我讀了 `Systems/guard-kill` 與 `Systems/規格閘` 的新增行,內容和程式一致:`failed` 參數、`c.merge_failed`、`_single` 與 `single` 的流向、`merge_off`、`unclean` 都對得上。判定規則沒變,所以不破壞「合併不判殺掉」那條既有合約。

最高嚴重度 minor,blocking 0 條。
