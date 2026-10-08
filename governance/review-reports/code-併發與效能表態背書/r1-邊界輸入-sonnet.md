severity: minor

程式本身沒找到 blocker 或 major;4 條 minor:3 條測試守不住的缺口(在臨時 clone 改壞程式後測試照綠),1 條讀 kill-log 少一欄讓整題背書作廢。

**B1 新測試沒守住 `_backing_warn` 的 needs_backing 過濾**
severity: minor
blocking: 否。程式現況正確,只是測試缺口。
刪掉 `_backing_warn` 開頭只放行被標題目的檢查,沒標的 satisfied 題會誤印提醒,但 -k disposition 100 passed、-k contract_ 44 passed;warn_only 與 follows_gate 只用 java-concurrency;marked_questions 說明寫了推送前檢查不多提醒,卻只測 `_contract_backing_apply`。
引句:「if not (spec and spec.get("needs_backing")):」
引句:「沒標的題寫表態時不加 backing、推送前檢查不多提醒。」
file: `scripts/test_lumos.py:58087`

**B2 kill 留痕前補換行的呼叫沒有測試守**
severity: minor
blocking: 否。功能現況正確,只是少了整合層守衛。
刪掉 `_append_repair_partial_line(log)` 那行,-k kill 139 passed;t_kill_log_partial_line_bytes 只直接呼叫輔助函式。
引句:「_append_repair_partial_line(log)」
file: `scripts/test_lumos.py:58087`

**B3 weak 三種來源只有兩種有測**
severity: minor
blocking: 否。測試缺口。
把 m_flaky 從算式拿掉,-k kill 139 passed;weak_sources 沒有 flaky 案例。
引句:「res["weak"] = bool(m_ws or m_flaky or node_dirty)」
file: `scripts/test_lumos.py:58087`

**B4 kill-log 某一行缺 weak,整題背書判成讀取失敗**
severity: minor
blocking: 否。只有手改或別的寫入者留下的半套新欄位行才觸發。
`_backing_kill_rows` 只驗五欄不驗 weak,`_backing_judge_groups` 取 r["weak"] 丟 KeyError,外層 try 接住,所有被標且 satisfied 的題記「讀取失敗:KeyError」,連本來 strong 的也被拖垮;違反說明「欄位型別不對的行略過」。重現腳本 /tmp/cpe_e7.py。另兩個小縫:weak 是字串 "no" 時 is not True 當成不弱;head_sha 只有 7 碼照樣通過版本驗證(皆需手改)。
引句:「if not any(r["verdict"] == "killed" and r["weak"] is not True for r in g):」
file: `scripts/lumos:37975`

檢查過沒問題:--covers 各種輸入全 rc2、重複去重;None 與空字串有區別;cmd_guard_kill_add 只有 main() 一處呼叫;kill-log 其餘形狀略過或當空清單;backing 三個讀者對各種形狀不拋例外;多平台與單平台各 9 種名稱組合兩端一致;cmd_gov 移除 import json 無殘留;follows_gate 把 gate 改 all 確實翻紅;其餘新測試無永遠綠斷言。

圖譜鏡頭:不影響三篇筆記宣稱的行為。

最高嚴重度:minor;blocking 條數:0
