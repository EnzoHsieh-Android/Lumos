severity: minor

已驗:讀 gate 預設的地方只有 cmd_drift_check 與 _drift_gate_doctor_lines 兩處,都走 _drift_config(scan/exam 沒有另讀預設);設定寫壞時 _drift_config 回 block 加警告,cmd_drift_check 先印「提醒:…照預設 block」再走 block,訊息與行為一致;python3.14 跑 -k drift 557 通過 0 失敗;把預設改回 warn,新測試 ②③④ 與 ⑥、⑨ 都會紅。沒有 blocker。以下為次要問題。

## F1 被預設擋下的訊息沒告訴消費專案怎麼改回 warn
severity: minor
blocking: 否
引句:「專案要先只提醒或關掉,在 .lumos/config.json 寫 drift_check.gate=warn|off;設定寫壞也照這個預設。」
file: `scripts/lumos:26319`
1. 消費專案沒寫設定、已接線掛鉤,更新後第一次推送若剛好有轉正後留著預告句(或判不了)的發現,會看到 `擋下:…`,rc1。
2. _drift_report_must 印的內容只有改法指令、ack 指令和 LUMOS_SKIP_DRIFT_CHECK=1,完全沒提 `.lumos/config.json` 的 drift_check.gate 可以改 warn/off。
3. 那句說明只寫在程式註解、--help 與 skill 文件裡,被擋的人在終端機看不到;doctor 對沒寫設定的專案又刻意不唸。
4. 建議:預設 block 且沒有 explicit 時,擋下訊息多印一行「這是預設值,要先只提醒:.lumos/config.json 寫 drift_check.gate=warn」。

## F2 設定寫壞照預設 block 的 rc1 沒有測試釘住
severity: minor
blocking: 否
引句:「④設定解析:三種「沒寫」都回 block」
file: `scripts/test_lumos.py:51176`
1. 新測試 ④ 只測 _drift_config 的三種「沒寫」形狀;②③ 只測沒設定檔與沒寫 drift_check 的 check 回傳碼。
2. 「寫壞」(JSON 壞、gate 拼錯、null、drift_check 非物件)在 drift check 的 rc 沒有測試;若有人把壞設定的回傳改成 warn,不會紅。
3. doctor 那行的措辭由 r5 測試涵蓋,但 check 是否真的擋、是否印「提醒:…照預設 block」沒人釘。
4. 建議:對 gate 拼錯或 JSON 壞各加一個 drift check 案例,斷言 rc1 且 stderr 含「照預設 block」。

## F3 舊句檢查計劃的 _drift_config 設計段仍寫沒設定就是 warn
severity: minor
blocking: 否
引句:「沒寫設定時的預設從 warn 改成 block:沒在 .lumos/config.json 寫 drift_check.gate 的專案」
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:114`
1. 本次只改了存量漂移防線計劃與守衛節點;舊句檢查_計劃第 114 行仍寫「沒設定檔、JSON 壞、沒有 drift_check、drift_check 不是物件 → warn」與 `{"drift_check": {"gate": "blcok", ...}}` → gate warn。
2. 依它實作會把 gate 預設寫回 warn,與現行程式衝突。
3. 該計劃第 41 行 old_sentence 預設 warn 是另一個獨立開關,不受影響。
4. 建議:第 114 行 gate 部分改成 block,或註明以存量漂移防線計劃 d1 為準。

最高等級:minor
