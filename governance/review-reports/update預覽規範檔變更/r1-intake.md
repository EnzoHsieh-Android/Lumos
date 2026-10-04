# r1 收貨(update預覽規範檔變更,設計審)

standard 分級:通才、邊界、整合三席加架構對齊席,全部 sonnet;收齊才動計劃。首輪前便宜 agent 掃描報兩條,都是把「計劃要新增的旗標與要拆的函式」當成現況宣稱,誤判,不改。report-normalize:邊界席一處「等級後面黏著 ⚠」用 --write 純格式搬移;quote-check 全數錨定。

## 去重後的發現

| id | 來源席 | 一句話 |
|---|---|---|
| A1 | 通才 F1、邊界 F2、整合 F3 | 預覽先拉來源卻用拉之前載入的舊程式算,套用跑新程式,兩邊結果不同 |
| A2 | 通才 F2、邊界 F1、整合 F3 | 結尾的套用指令沒帶預覽用的 --source |
| A3 | 整合 F4、架構對齊 F2 | 預覽拉來源會換掉全機共用的 lumos 與 skills,與既有 --dry-run 零改動語意不同 |
| A4 | 整合 F1 | 手冊、指令說明表、CLI help 都沒寫新旗標 |
| A5 | 整合 F2 | lifecycle 筆記的 update 旗標清單過時,且「update 在來源 repo 回 2」與程式相反 |
| A6 | 整合 F5 | init、init --force、bootstrap 也寫規範檔,沒交代在不在範圍 |
| A7 | 整合 F6 | 預覽印完整差異、套用只印 20 行;[S2] 的「一致」沒說比什麼 |
| A8 | 整合 F7、邊界 F8 | 其餘動作漏列工具指紋檔、py314 提示,全域 hooks 同步沒標成專案外 |
| A9 | 通才 F3、邊界 F6 | 套用會整檔去 BOM、統一換行,預覽只看區塊會少報 |
| A10 | 通才 F4、邊界 F3 | 會新建、會接上兩種狀態沒內容可印,AGENTS 檔接在檔首的位置沒講 |
| A11 | 通才 F5、邊界 F10、邊界 F11 | 回傳碼、標記壞掉、只差版本號、來源 repo 自身那條路沒定 |
| A12 | 通才 F6、邊界 F4 | 來源沒有範本時預覽與套用不同;拆函式不能動到 Check D 的比對 |
| A13 | 邊界 F5 | 非 UTF-8 或讀不了的目標檔會讓預覽崩潰 |
| A14 | 邊界 F7 | Windows 換行專案的工具檔會全部列成會換新 |
| A15 | 邊界 F9 | [S1] 沒定「每一個檔」怎麼比(新增的檔、.git、家目錄) |
| A16 | 架構對齊 F1 | 工具檔比對可能另寫一份迴圈 |
| A17 | 架構對齊 F3 | 預覽輸出開頭沒沿用 deinit 預覽的格式 |

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| A1 | 讀 cmd_update → _vendor_toolchain:pull 在同一個行程裡、之後才算 | HIT |
| A2 | 讀 _lumos_src 的優先序 | HIT |
| A3 | 讀 _pull_source_or_abort 與 lifecycle 筆記「分發=symlink 指向源」 | HIT |
| A4 | grep 手冊與指令參考的 update 列 | HIT |
| A5 | 對照 lifecycle 筆記與 cmd_update 來源 repo 分支 | HIT |
| A6 | 讀 cmd_init、bootstrap 呼叫 _vendor_toolchain 與 _do_reinject | HIT |
| A7 | 讀 _reinject_all 只印前 20 行 | HIT |
| A8 | 讀 _vendor_toolchain 結尾 | HIT |
| A9 | 讀 _reinject_claude_block 讀入正規化與 _write_lf 整檔寫回 | HIT |
| A10 | 讀 created/appended 回傳 diff=None 與 AGENTS 插入位置 | HIT |
| A11 | 讀 cmd_update 來源 repo 分支回傳碼 | HIT |
| A12 | 讀自癒迴圈「來源沒有就跳過」與 _expected_claude_body 的呼叫端 | HIT |
| A13 | 讀 raw.decode("utf-8") 沒有錯誤處理 | HIT |
| A14 | 讀 filecmp 逐位元組比 | HIT(套用時一樣會換掉,預覽照實列,另加說明) |
| A15 | 讀 [S1] 原句 | HIT |
| A16 | 讀 _vendor_toolchain 迴圈 | HIT |
| A17 | 對照 cmd_deinit 預覽輸出 | HIT |

## 處置

全部折入計劃第二版(見計劃〈審計修正紀錄〉r1):預覽一律不拉來源、結尾帶 --source 與 --no-pull;逐種目標檔狀態定輸出;回傳碼照真跑;範本取法照套用順序;非 UTF-8 回 2 不崩潰;其餘動作列齊並標專案外;[S1] 改整棵目錄、家目錄、來源提交編號比對;新增 [S6];手冊、help、lifecycle 筆記同步寫進做法 8;init、bootstrap 列為不做並寫進天花板;比對迴圈抽共用;輸出開頭沿用 deinit 預覽。
