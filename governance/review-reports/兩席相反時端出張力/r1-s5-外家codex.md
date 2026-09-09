severity: major

### F1 多行區塊註解會產生假候選
severity: major
blocking: 是—照稿實作會違反 S3「註解不算命中」的驗收行為。
spec: 〈二、`pitfalls --diff` 端出候選〉、[S3]  
引句:「F 的增行逐行 `_stack_norm_line`（剝字串、跳註解）得 `norm`。」  
`file: `scripts/lumos:15294`` 的 `_stack_norm_line` 沒有跨行註解狀態，`/* start` 後的 `async {` 仍回傳 `async {`；最小重現：`python3 -c "..._stack_norm_line('   async { // still comment')..."` 輸出為 `'   async {'` 且 `\basync\b` 命中。  
這會令候選與適用題都把註解當程式碼，必須指定跨行註解的狀態式正規化，並補入 S3。

### F2 `existing` 無上限會拖垮推送前核對
severity: major
blocking: 是—合法輸入可讓 pre-push 熱路徑逐項啟動無上限 git 核對，沒有完成保證。
spec: 〈一、第四種表態〉、〈實務隱患〉  
引句:「`existing` 是既有寫法的位置，一項一個 `path:line`。」  
`file: `scripts/lumos:21498`` 的時間預算只在每題開始前檢查，`file: `scripts/lumos:21464`` 的 `_one` 是單題完整核對入口；稿件要求在其中逐個驗全部 `existing`，卻沒有數量或總字元上限。  
最小重現：一題適用的表態放入數千個合法、重複的 `existing:["src/A.kt:1",…]`；寫側依稿只要求非空清單，讀側會逐項做樹與行號核對，推送可長時間卡住或超時後走既有放行分支。

### F3 九處同步只對三處設漂移守衛
severity: minor
blocking: 否—不改變本次功能判定，但日後可讓派工或圖譜口徑靜默分裂。
spec: 〈三、口徑〉、[S6]  
引句:「`t_tension_doc_sync` 釘三處含「tension」。」  
稿件要求九處文字同步，卻只機械釘住三處；其餘六處可刪除或保留三值口徑而測試仍全綠。  
`file: `scripts/lumos:4833`` 的既有 `t_marker_doc_sync` 是單一文字存在檢查，不能替未列入的文件驗證語意同步。

現況查證：已讀,無 finding。  
設計〈一、第四種表態〉：除 F2 外已讀,無 finding。  
設計〈二、候選〉：除 F1 外已讀,無 finding。  
設計〈三、口徑〉：除 F3 外已讀,無 finding。  
驗收條款：已讀,無 finding。  
刻意不做：已讀,無 finding。  
合約候選：已讀,無 finding。  
審計修正紀錄：已讀,無 finding。

固定席逐條判：

- `Systems/棧別提問表態閘`：有影響；新增值符合其「每題機器可讀交代」方向，但 F2 未解前會破壞推送前熱路徑的可用性。
- `Systems/arch-alignment-lens`：不影響；候選只提示、仍由人判斷，沒有把「像不像」改成機械裁決。
- `Issues/架構對齊席與棧別檢核題可能相反`：有影響且方向相符；稿件保留兩種觀點並交人裁。
- `Systems/效能檢核目錄`：有影響；必須完成 S6 同步，否則題表使用者仍只知道三值口徑。
- `Systems/finding-refute`：不影響；稿件仍把 hazard 與 suggestion 留給審查席反駁。
- `Systems/pitfalls-code-loop`：有影響；F1 的假候選會污染其提供給審查員的注意力訊號。

實務隱患覆核：併發無新增寫入路徑；效能有 F2；資源無新增持久資源但 F2 會放大 git 子程序成本；回滾無，資料僅為可還原簿記；誤擋有 F1 的假候選但其不直接進閘。payment、external-send、prod-irreversible 均無：本案只改本機 CLI 的表態資料與提示輸出，未接觸付款、外送或正式環境不可逆操作；`pitfalls --check` 命中的是文件內風險名稱，不是功能路徑。

最嚴重 severity 是 major、blocking 共 2 條。
