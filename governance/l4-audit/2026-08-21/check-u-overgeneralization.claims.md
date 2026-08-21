C1. lint 只掃 summary 的 `KEY:` 行（FLOW/DEP 等不在合約宣稱範圍），三訊號（分配式量詞+程式實體+義務語氣）同現、且該行無 `[test:]`、非技術債標記時才 warn，提示「若真是通則就編成適應度函數」 | 預期驗證點: lumos-cli-write / Check U 對應的 lint 實作（掃描 KEY: 行的函式、三訊號判定邏輯）

C2. 分配式量詞詞表為：所有｜每個｜每支｜每一｜各個｜凡是｜凡｜一律 | 預期驗證點: Check U lint 實作中的量詞正規表達式/詞表常數

C3. 程式實體詞表為：Service｜Repository｜Controller｜Job｜服務｜排程｜查詢｜端點｜入口｜呼叫點｜實作｜模組｜節點｜欄位 | 預期驗證點: Check U lint 實作中的程式實體正規表達式/詞表常數

C4. 義務語氣詞表為：必須｜都要｜都必須｜皆須｜應該｜一律要｜要寫｜要帶｜不可｜禁止 | 預期驗證點: Check U lint 實作中的義務語氣正規表達式/詞表常數

C5. 消音（silence）路徑有三條：行內含 `[test:]` / 標了 `★DEBT★` / 改寫成限定範圍語氣 | 預期驗證點: Check U lint 實作中的消音判斷分支

C6. 只看單一量詞訊號時，在 LandmarkMember 圖譜（30 篇 Systems / 261 條 KEY 行）的命中率為 17%（45 行） | 預期驗證點: 2026-08-12 噪音實測數據來源（測試 fixture 或 Verification 節點所附統計）

C7. 收緊為三訊號同現後，命中率降到 1%（5 行），其中 3 條為真陽性 | 預期驗證點: 同上噪音實測數據/測試 fixture

C8. Check U 綁有 6 條牙齒測試（unit tests），其中包含「只有量詞不吵」與「缺義務語氣不吵」兩條防噪音斷言 | 預期驗證點: Check U 對應測試檔案，測試案例數=6，且存在上述兩條防噪音測試案例

C9. Check U 的 severity 為 `warn`，不是擋（blocking）機制 | 預期驗證點: Check U lint 實作中回傳/標記的 severity 等級

C10. Check U 有兩個對應的驗證節點：`Verification/2026-08-12_CheckU_過度概化守衛`、`Verification/2026-08-12_通用性修正_profile化與歷史重放` | 預期驗證點: docs/lumos-toolchain-knowledge/Verification/ 目錄下對應檔案是否存在

C11. Check U 依賴（DEP）於 `Systems/lumos-cli-write`，即 lint 邏輯所在的寫入層 | 預期驗證點: lumos-cli-write 節點內容/程式碼是否含 Check U 的 lint 掛載點

C12. Check U 與 `Systems/check-t-sentinel` 的關係為「Check U 是它的前一哩」——check-t-sentinel 是針對 `★INVARIANT★` 的 `[test:]` 存在性檢查 | 預期驗證點: check-t-sentinel 節點內容/對應 lint 實作是否確實檢查 `[test:]` 存在性

C13. 對照表宣稱：Check N 靠使用者自己宣告的語法約定，換圖譜與換語言棧皆「✅ 通用」；Check Y 靠形狀規則＋否定詞表且皆已 profile 化，換圖譜「⚠ 換 lexicon」、換語言棧「⚠ 換 profile」；Check U 靠三張未 profile 化的中文詞表，換圖譜與換語言棧皆「❌」 | 預期驗證點: check-n-recomputable 與 check-y 對應節點/lint 實作，比對是否存在 profile 化機制與語法宣告機制

C14. 實例佐證：`CustTransfer`／`滿額贈` 的「折疊守衛（通則）」規則自稱通則、寫著「凡顯示/計數該表的查詢都必須折疊」、零 `[test:]`，且該規則 2026-06-02 被漏補，一路到 07-21 才被使用者回報 | 預期驗證點: CustTransfer/滿額贈相關圖譜節點的日期記載、對應 commit/issue 記錄

C15. 已知限制自陳：三訊號實測命中的 5 條中有 2 條為誤報（真陽性 3 條） | 預期驗證點: 與 C7 相同的噪音實測數據/測試 fixture 應可交叉核對 5 命中中誤報數
