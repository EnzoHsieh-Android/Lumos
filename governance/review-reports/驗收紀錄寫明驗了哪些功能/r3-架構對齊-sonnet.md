severity: minor

驗收上一輪的 major:單項判法已改成抽共用 `_typed_link_target`,索引與本案共用。結論:通過,「自訂第二套單項規則」這個 major 已解;剩兩條 minor。

## 1. 分層與依賴方向
對。單項判法(`build_typed_index`,scripts/lumos:740-785 的 fullmatch、path 式精確比對、by_stem 唯一候選三段)抽成共用函式,索引與 `_verification_system_targets` 都往它呼叫,依賴方向是「判法零件 → 索引/doctor/sync/new」,沒有跨層直呼 doctor 內部。doctor 3/4(scripts/lumos:1476)與 `sync-verified-by`(scripts/lumos:15843)目前各寫一份推「驗了誰」,改抽 `_verification_system_targets` 且孤兒推薦(scripts/lumos:806-818)一起改用,是收斂成一種做法,方向正確。

## 2. 命名與錯誤處理
大致對。`_typed_link_target`、`_verification_system_targets` 的底線前綴、`(env, ...)` 簽名與鄰居(`_suggest_systems_for_orphan`、`_drift_c3_hit`)一致。寫壞項走「報 issue」照 doctor 4/4 對 plan_refs 斷鏈自己報的先例(scripts/lumos:1514-1523);`new verification` 寫入失敗走 try/except(OSError, ValueError, RuntimeError) 加提醒加 rc2,照 scripts/lumos:19198-19211 既有寫法。兩處不齊見 F1、F2。

## 3. 第二種做法
上一輪的第二種做法(自訂單項判法)已消除。殘留兩處「並存」:
- 宣告了走嚴格單項判法、沒宣告仍走 `n.targets` + `env.resolve` 寬鬆比對(scripts/lumos:1488-1494、15858-15862)。這是計劃明講的相容分支(舊紀錄照舊),且有 RETIRE-IF 管,不算新增的第二種做法。
- 作廢/失效狀態:新增 `_verification_status` 與既有 `status_of`(scripts/lumos:732)並存,見 F1。

## 4. 落點
對。改的都在 `scripts/lumos` 的 doctor、sync、new、LIST_KEYS 既有位置,文件同步清單(lumos-cli-read / lumos-cli-write 與 skills)對應各家,精簡版凍結不同步有理由。`system_refs` 只進 `LIST_KEYS`(scripts/lumos:17105),不進 `LINK_KEYS`(scripts/lumos:17125)、`TYPED_EDGE_FIELDS`(scripts/lumos:737),範圍收窄有明講。

## F1 狀態判斷只統一四處,新增第二個取狀態函式
severity: minor
blocking: 否
引句:「作廢、失效的判法抽成一支 `_verification_status(env, rel)`(status 去空白、轉小寫)」
file: `scripts/lumos:732`
- 既有 `status_of(env, rel)` 是取狀態的鄰居做法;新函式與它並存,且同樣的 `.strip() in ("stale","superseded")` 大小寫敏感判法在 scripts/lumos:1770、1826、2409、2469、2507、2984、4127 還有多處,計劃只改四處(1/4 孤兒、3/4、E1、sync)。改完同一個 status 在不同檢查裡大小寫語意不一致(`Fail` 在 E1 算失效、在 doctor 其他檢查不算)。
- 建議:讓 `_verification_status` 直接成為 `status_of` 的正規化版本或在計劃的〈已知限制〉明記其餘站點不動、附回頭條件(REVISIT)。

## F2 抽出單項判法的介面沒涵蓋索引現有的行為細節
severity: minor
blocking: 否
引句:「從 `build_typed_index` 裡判單項的那段原樣抽出,`build_typed_index` 改呼叫它、行為不變」
file: `scripts/lumos:757-785`
- 計劃寫「四種不合格」,但現有段落還有:`nfc` 正規化、`.md` 後綴剝除、`[[#段落]]` 取出空目標時靜默 `continue`(scripts/lumos:765-766)、去重鍵 `seen`(scripts/lumos:767-770)、ambiguous 要回候選清單與原字面。這些哪些留在呼叫端、哪些進共用函式,計劃沒定;空目標在本案會變成「寫壞」還是跳過也沒寫。條款 S5 只守索引四份清單不變,沒守這個空目標邊界。
- 建議:在做法 1 寫明回傳形狀(落點 rel / 不合格種類 + 原字面 + 候選)與空目標歸屬,並在 S5 的測試加一筆 `[[#x]]`。

不對齊共 2 條,其中 major 0 條
