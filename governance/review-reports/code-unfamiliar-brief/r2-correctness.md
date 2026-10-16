severity: clean

helpers、tests、runner adapter：已讀,無 finding。

U4 全版本與 README：已讀,無 finding。

驗證紀錄：

- 固定版本：before `e3f92904ba93c37fcd417e14fce70148f7855e3e`，helper blob `91cf3d748e449cee072893d55299f714f4f7fedb`；after `75a922f8e304e983cf01fb3aa1659e4c16f23cda`，helper blob `0f2042dd299c97572222f92948057eb4977bcc90`。repair patch SHA、兩端 tree 與 ancestry 均符合 binding。
- Runner：兩棵隔離樹執行 `python3 scripts/test_lumos.py -k unfamiliar_stack_brief`；before `3 passed`，after `4 passed`，新增 U4 oracle 轉接成功。
- G1／S4：同一 inline harness 呼叫 `preflight_run`。兩臂共用相同材料時 before `ACCEPT`、after `REJECT session materials must match the frozen arm allowlist`；合法 common＋Brief 配對在 after `ACCEPT`。比較界線只含本階段已實作的材料、model、effort 預檢，不含尚待凍結的正式模型參數。
- G2／S5：同一 receipts 將 `primary_hit` 設成字串 `"false"`；before 為 `proceed-to-historical / invalid=0`，after 為 `incomplete / invalid=1`，符合無效資料只能 incomplete。
- G3／U4：before 無 v2；after 執行 `node .../cases/U4/{buggy,fixed}-v2.js {target,normal}`，回傳碼依序為 `1,0,0,0`。v1 在兩端皆為 `1,0,0,0`，確認歷史版本未覆寫。比較界線為版本化新增，不宣稱 v1 已補齊回傳值驗證。
- 未呼叫外部 API。

撤回觀察：

- 額外 session 欄位會被忽略，但目前 helper 不消費它們，正式 temperature／工具／上限也尚待後續凍結；無實際錯誤路徑，不列 finding。
- 改動 qualification-v1 metadata 後測試仍綠，但該實驗同時改了判準 manifest；沒有外部可信 digest／簽章或本階段自驗承諾，不能據此判 helper 有錯，不列 finding。

殘留問答：範圍內 governance/residual-index.json 無差異，治理帳新增列亦無 residual-ask；因此沒有題號、文字、checker、ts 可核對是否換號或改字重問；第二代理身分不適用，未冒稱完成雙代理核對。

總結：最嚴重 severity clean；blocking 0 條。
