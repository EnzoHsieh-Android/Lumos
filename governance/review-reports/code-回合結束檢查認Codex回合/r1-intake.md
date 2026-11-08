# r1 收貨紀錄(code-回合結束檢查認Codex回合)

- 分級 standard(改到鉤子程式):一位審查員加一席架構對齊,兩席交回後一次存檔;quote-check:審查席一句在「查過沒問題」段的引句對不回快照(不是發現),兩條發現的引句都錨得上;架構對齊席 clean、全錨。
- 臨時目錄 /tmp/lumos-seat-work/code-回合結束檢查認Codex回合/ 收貨後刪(架構對齊席沒留東西;審查席另把官方 turn.rs 存在會談暫存區 rv/)。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| f1 | 審查 | major | Codex 回合中途插話以同一個 turn_id 再送一次送出提示,起點時刻被覆寫成插話時刻,插話前改的檔不查 | HIT:新增 ⑤ 修補前紅(起點時刻被蓋成第二次的) | 折:_kept_start 同一個回合編號保留原起點;換回合才換新 |
| f2 | 審查 | minor | Codex 路徑少了同回合同批不重擋、換回合重算的測試 | HIT:新增 ⑥ | 折:補 ⑥ 兩步 |

架構對齊席另提兩處用詞(紀錄鍵名仍叫 prompt_id、檔頭防無限擋那行寫 prompt_id),不算發現;檔頭那行順手改成「回合編號:prompt_id,Codex 用 turn_id」,鍵名照舊(舊紀錄檔相容)。

## 修補後驗證

- 改壞兩種各自翻紅:拿掉保留起點 → ⑤同一個 turn_id 紅;不管回合編號一律保留 → ⑤換 turn_id 紅。-k stop_lint 70 passed。
- 修補差異另派全新席審(r2)。

## 先查世界

- PRIOR-ART:f1——官方 openai/codex 主線 codex-rs/core/src/session/turn.rs(審查席抓的副本):插話(steer)以 TurnInput::UserInput 走 inspect_pending_input,同一個 turn_context;hook_runtime.rs 送出提示事件的 turn_id 取 turn_context.sub_id。做法:起點以回合編號第一次出現為準。
