severity: major

## design3-architecture-F1

severity: major  
blocking: 是

索引樹雖先固定，但「哪些檔案有變」仍從之後的活動索引讀取，形成兩套版本來源。若索引在 `write-tree` 後暫時加入某測試、算完差異後又還原，結尾樹雜湊仍相同，該未暫存測試卻可能被當成額外寫回證據，錯誤放行 home check。

引句:「額外路由應只用捕獲樹及起點作證；各來源分別驗合法，不借途中內容。」

file: `scripts/lumos:29994`  
file: `scripts/lumos:29996`  
file: `scripts/lumos:30050`  
file: `scripts/lumos:29479`  
file: `scripts/lumos:30068`

具體路徑：

1. `write-tree` 在 29994 固定樹。
2. 29996 隨後以 `"index"` 重新計算 `changes`，仍讀活動索引。
3. 30050 將這批差異轉成 `changed_paths`。
4. 29479 用它決定哪些測試可借作路由證據。
5. 30068 只比較最後索引樹；中途改動後還原的 ABA 時序不會被偵測。

現有 ABA 測試在 `_nodehome_route_tests` 才注入變動，已晚於 `changes` 的取得，因此沒有覆蓋這個窗口。

file: `scripts/test_lumos.py:49171`

修補驗收：正式 home-check 的原有活動索引語意可以保留，但額外路由必須另以 `HEAD → index_tree` 兩個固定端點計算自己的 `route_changed_paths`；新增控制案例，在 `_nodehome_changes` 讀索引期間換入測試再還原，確認注入確實發生且該測試不會被借證。

## 架構四問

1. 分層與依賴方向：不對齊。讀取層原本以固定 Git 版本向判定層交付集合，但此處把固定樹內容與活動索引差異混成同一證據來源；即 design3-architecture-F1。
2. 命名與錯誤處理：對齊，未發現新的命名、錯誤回傳或日誌慣例分叉。
3. 第二種做法：不對齊。額外路由同時使用「不可變樹」與「即時索引」兩種版本語意，且沒有明示邊界；計 1 條 major。
4. 落點：對齊。CLI修補落在既有 `Systems/每支檔有家`，人工流程落在既有 `Systems/每輪修補差異派工`；未發現需另開第二套系統節點的內容。

不對齊共 1 條，其中 major 1 條。

## 三類風險

- 架構與可執行性：有 1 條 blocking，見 F1。其餘五篇人工流程未發現新的跨層直呼或第二套執行框架。
- 來源取回與版本綁定：未發現新的 blocking。增量 bundle 檔案存在，SHA-256 與收據一致；收據記錄的 `clone --bare --single-branch --branch`、`cat-file -e`、`merge-base --is-ancestor`、`bundle verify/list-heads`、`fetch`、`rev-parse ...^{tree}` 均有預期退出碼。計劃亦明定最終功能 HEAD 必須重新綁定，沒有拿 957 的舊結果冒充最終通過。
- 回退與固定合約：未發現新的 blocking。三個主要落點中，實際查得的相關固定合約只有「翻紅釘須有前置斷言」；ABA、索引輸入與捕獲失敗測試都有注入確實發生的斷言。回退保留舊守衛、另在隔離來源重放新增紅燈的分界可執行。

未定義引用人工核對未見缺件；整合計劃十條條款皆可被 `spec-trace` 辨識，無懸空標記。`retro-stats`、`home check`、`loop fix-check`、`canary record --regression-set` 等具體 CLI／旗標也已由現行 help 確認存在。

實際閱讀量：約 1,750 行可見正文與定點程式，另掃描搜尋命中；包含 AGENTS、CLAUDE、design-loop 技能與架構席規則、派工詞、五篇完整計劃、相關 Systems、CLI help、核心實作、測試及冷還原收據。未讀任何席報告。未驗範圍：沒有即時連網重做遠端 cold restore，沒有重跑會建立 Git fixture 的測試；指定的唯一 Git 工作目錄不存在，因此遵守限制未執行 Git。遠端 main 是否自收據後漂移、以及尚未產生的最終功能 HEAD 綁定，保持未判定。