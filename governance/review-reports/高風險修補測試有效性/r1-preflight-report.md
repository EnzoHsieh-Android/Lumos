主計劃的人工判讀邊界清楚；問題集中在它引用的既有指令說明，有 **3 項機械語意不符**。

1. **Medium｜引用節點仍使用過時的狀態與退出碼。**
   [guard 殺傷力計劃第59行](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:59)寫：「`timed_out`（歸 killed 類、註記）✓」及「全 killed（含 timed_out）→ 0」。
   實際 `cmd_guard_kill` 使用 `timed_out_weak`、`killed_unattributed`；全部只有這兩種弱結果時退出碼為 **1**，混有 `killed` 時才可能為 **0**。這個引用可開啟，但不能作為目前結果判讀的可靠說明。主計劃「超時……均未判定」與目前程式方向一致。

2. **Medium｜既有說明將單次綠燈過度推論為測試無效。**
   [引用計劃第49行](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:49)寫：「全綠＝綁定是稻草人（假證據），機械可證」；[速查第24行](/private/tmp/lumos-future-repair-regression-research/skills/lumos-project-notes/commands/06-代碼審與推送.md:24)寫：「沒翻紅=測試是裝飾」。
   實際程式只將挑戰命令退出碼 **0** 判為 `survived`，沒有機械確認目標案例執行、錯誤路徑到達或變動不等價。主計劃第28行反而正確限定：「只證這個案例未偵測這種錯誤」。兩份指路文字的結論超過程式可證範圍。

3. **Medium｜引用節點宣稱能區分錯誤原因，實際只有輸出文字歸因。**
   [引用計劃第59行](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:59)寫：「`error`（套用後 harness 失敗，**不得記 killed**）」；第85行又列「`error`（壞語法）」。
   實際挑戰命令非零時，程式交給 [`_kill_attribute`](/private/tmp/lumos-future-repair-regression-research/scripts/lumos:15789)：在測試名所在行起的五行窗內尋找失敗標記；命中便判 `killed`，否則判 `killed_unattributed`。它沒有語法、載入、收集與行為斷言的原因分類。因此 `killed` 本身不能證明「目標行為斷言因該錯誤失敗」；主計劃要求再讀實際失敗內容是必要的。

其餘三項核對結果：

- **未定義詞：**未見確定缺陷。「共用範本」「兩處指路」「三份技能」可由直接引用的 Systems 節點定位；1800行範圍由直接引用計劃說明為一席全部必讀材料。
- **壞引用：**主計劃的三個圖譜引用均能讀取；上述問題屬引用內容失準。外部網址依限定讀取範圍未連線驗證。
- **範圍矛盾：**未見確定矛盾。人工抽查、新席核對與既有放行分開；隔離副本的挑戰也未被宣稱為 CLI 自動保證。

未改檔、未執行殺傷力命令、未派代理。
