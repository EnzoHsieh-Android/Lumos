# code-選擇點變異加速第二段 第 2 輪收貨(2026-11-25,8 席)

材料:修補差異 r2-repair.patch(a95e650 → c4ed34e,1136 行)給六席;完整快照 r2-snapshot.patch(dd8729f..95977c1,2092 行,超過 1800 行建議上限,資安席照規定看最後一版全部檔不拆)給資安席與圖譜席。來源綁定 r2-repair-binding.json;派工單 r2-dispatch.json。配對案例:r1-fix.json 各組列的測試當 repair 案例,preserve 由席位從修補函式的呼叫者與 Systems/guard-kill 兩條 ★INVARIANT★ 自選。席報告從各席執行紀錄最後一則回覆原樣存檔。

圖譜鏡頭:r1、r2 七席派工時 hook 都沒附上固定席(快取 20 分鐘過期;多席同時派、第一席建鎖背景重算其餘席看到鎖直接回逾時,hook 事件 13:45:17–13:46:01 連記逾時)。r2 另補派一席「圖譜-sonnet」,派工時 hook 有附固定席段,逐節點判 guard-kill、lumos-cli-read、bound-tests-gate、loop-convergence-recording、pitfalls-code-loop、測試假綠形態、design-loop、lumos-cli-lifecycle,實跑 t_guard_kill_rc_precedence(4)、t_guard_kill_json_purity(6)、t_choice_guard_kill_new_params(5)全綠,判 clean;只列名的兩篇沒逐篇開。

## 機械收貨

| 席 | 檔級 | 條數 | 引句 |
|---|---|---|---|
| 正確性 | clean | 0 | 零條發現無引句;總結行寫 max severity,退回該席只改那行後重交 |
| 資源 | clean | 0 | 零條發現無引句 |
| 邊界 | minor | 1 | 全錨;總結行寫 max severity,退回該席只改那行後重交 |
| 整合 | minor | 4 | 全錨;`report-normalize --write` 補檔級行 |
| 通才 | minor | 2 | 全錨;第一份最後一則只有補充,請該席重交完整版並改總結行 |
| 架構對齊 | minor | 2 | 全錨;第一份有一條缺獨立等級行,退回該席補一行並刪掉一句不成立的註記後重交;`report-normalize --write` 把縮排的等級行移到行首 |
| 資安 | clean | 0 | 零條發現無引句;看完 r2-snapshot 全部檔 |
| 圖譜 | clean | 0 | 零條發現無引句;總結行寫 max severity,退回該席只改那行後重交 |

審查席暫存目錄收齊後已刪。

## 發現與處置

| id | 席 | 等級 | 一句 | 處置 |
|---|---|---|---|---|
| e1 | 邊界 | minor | 總時限用完時 `_KillHalt` 也記成「中斷」,run.interrupted 卻是 False,帳面矛盾 | 折:時限用完記「時限到」,收到訊號才記「中斷」 |
| a1 | 架構對齊 | minor | 帳欄位叫 single_runs、執行期叫 ran_solo,同一個數兩套名字 | 放行:帳欄位名照計劃 S9 條款與已綁的測試定;執行期改名是為避開判法 single 計數,兩者語意同為逐支次數,再改帳欄位名要動條款、預期值表與測試,成本大於好處 |
| a2 | 架構對齊 | minor | merge_off 過濾與斷路器寫入各寫一次字面「斷路器」 | 折:抽成常數,兩處共用 |
| g1 | 通才 | minor | 同 a2 | 折(與 a2 同修) |
| g2 | 通才 | minor | cmd_guard_kill docstring 的 on_row 欄位清單沒列 ran_solo | 折 |
| i1 | 整合 | minor | Systems/guard-kill WHY 仍寫 n_mutants 只剩簽名相容(參數已拿掉) | 折 |
| i2 | 整合 | minor | 計劃 WHY「不論原因都印一行」與「中斷只記不印」衝突 | 折 |
| i3 | 整合 | minor | `_kill_merge_iter` docstring 仍寫 off 記中斷 | 折 |
| i4 | 整合 | minor | 計劃 S7、S10 條款與預期值表沒收進 r1 修補新增的 8 個測試案例 | 折 |

## 歸因(修補鏡頭)

- e1:有證據的原有漏查(修前 `mg.off[plat] = "中斷"` 同樣不分時限到,邊界席讀碼)。
- a1、a2、g1、g2、i1、i3、i4:修補新引入或改名只改一半(兩版差異可見)。
- i2:原有漏查(第一輪就有的句子)。
- 程式行為面:正確性、資源、資安、圖譜四席判 clean;正確性席改壞 `--json` 剔除項 `-k choice_kill` 306 支照綠,判生產路徑走不到(choice-kill 不帶 --json),不立發現。沒有任何一席做修前實跑對照。
- regression_set:不帶(修補因果未全數以兩版實跑證實)。

## 先查世界

- e1、a2:專案內記帳與常數寫法,沿用 `_CHOICE_MERGE_BASE_WHY` 集中原因字串的既有做法,不另查。
- 其餘文件同步,不另查。
- 方向:這輪沒有上一輪同組根因帶 major,不查方向。
