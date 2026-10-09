唯讀核對完成。核心邊界可還原，未發現把 candidate、unsupported 或固定語法樣本冒稱為品質通過，也未宣稱手冊已改善 Agent、完整框架或真實 app 已驗。

還原結果：

- 目的：事後列出值得人工追查的測試寫法；與功能抓錯證據、手冊效果分開。
- 已驗：Python CLI 20 案例；掃描器兩個故障均基準綠／目標斷言紅／還原綠；七種語言 28 語法樣本中 22 個支援規則符合、6 個算法重抄未分析。
- 實際 repo 掃描：1949 個宣告、3 個候選；人工只核對這三項。`scripts/test_lumos.py` 1779 個宣告僅 3 個具已辨識斷言，卷證有保留，沒有冒稱全測試品質已驗。
- 未驗：Agent 兩臂效果、真實 app／裝置、完整框架、非 Python 算法同源、Swift Testing。
- 下一步：固定模型與開發題執行 S5；接入框架前增加合理反例、解析失敗與抓錯驗證。
- 手冊可以操作工具：README 指向 `commands/03-寫回圖譜.md`，提供掃描、來源比對、選配 backend、固定故障與考卷命令，以及 rc、candidate、未分析解讀。
- 掃描器、backend、考卷、故障 runner、CLI tests 與 corpus 的當前 SHA 全部符合保存卷證。

有三個小缺口：

1. **P3：語言數量不一致。** 計劃第 33、40 行寫「六種語言／六語言」，考卷實際為 Python、Kotlin、Java、Swift、C#、JavaScript、TypeScript 七種。建議改成不帶數量的「各語言」。

2. **P3：S5 回頭條件尚是散文。** 計劃第 84 行寫「事件入口是新增手冊兩臂 eval 命令／驗證紀錄時重驗此條」，沒有可被 drift／doctor 讀取的 `REVISIT:`。可理解下一步，但不符合本 repo「回頭條件接電」要求。

3. **P3：文件測試證據名稱較報告窄。** 驗證第 23 行宣稱「文件指路、分類單源與入口一致性子集通過」，列出的 `entry-check.log` 僅保存 `t_claude_block_matches_template` 的 doctor 兩個 check。目前所列卷證足以支持模板一致與 doctor 淨，但讀者不能從該 log 還原另外幾項子集的執行結果；補對應 log，或縮小句子即可。

未修改任何檔。
