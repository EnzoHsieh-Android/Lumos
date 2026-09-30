severity: minor

## F1 doctor 閘提醒多了一條「設定沒讀懂」分支,鄰居只講開關值
severity: minor
blocking: 否
引句:「存量漂移檢查的設定沒讀懂({cfg_warns[0]})——轉正後留著預告句的推送會被擋」
佐證行 file: `scripts/lumos:25304-25307`(_note_shape_doctor_lines:`mode, _w = _note_shape_config(txt)` 丟掉警告,只判 `mode != "block"`)、`scripts/lumos:29073-29075`(_note_audit_doctor_lines 同寫法)
1. 兩個鄰居的 doctor 開頭提醒都只判 `mode != "block"` 就講一句,設定寫壞的警告(`_w`)直接丟掉;預設是 block,寫壞照擋,不唸。
2. 本 patch 預設改 block 後,drift 的 doctor 在 `explicit and cfg_warns` 時多唸一句,等於在同一類提醒裡引入第二種呈現。
3. 這是刻意的(patch 註解引代碼審 r5 正確性席,drift 的 _drift_config 本來就回 explicit 與 warns,鄰居沒有),沒有跨層直呼、也沒有第二套讀設定的路徑,仍走 `_drift_config` 一支;所以只列 minor,不擋。若要完全對齊就丟掉 warns,但那會讓寫壞設定的人看不到原因,取捨由作者定。

## 其他對照結果(無 finding)
- 預設值常數:`_DRIFT_DEFAULT_GATE` 是既有常數(patch 只改值),鄰居 `_note_shape_config`、`_note_audit_config`(`scripts/lumos:24714`、`25488`)寫字面 "block";兩種寫法早就並存,不是本 patch 引入。
- 讀設定:仍走 `_drift_config(txt)` 快照讀法與 `.lumos` 捷徑檢查,跟鄰居 doctor 同一段(`scripts/lumos:28540` 附近對 `25292`、`29064`)。
- 決策紀錄:`decisions:` 條目 id d1、decided、valid 與 content/context/alternatives_considered/why_chosen/trade_offs 齊全,跟 `Projects/指令索引與情境測試_計劃.md:12-16`、`Projects/一句話層供糧_計劃.md:12` 的形狀一致。
- 筆記:撤掉 RULE 改寫成 WHY 並附出處與 [test:],合專案「WHY 要出處」慣例(對照 `Systems/筆記內容審.md:16` 的 WHY 寫法)。

最高等級:minor
