### arch-f1 新增 decay-state.json 是可版控、未走 gitignore 的 per-machine 執行期狀態檔,另立一套「今天做過沒」判斷機制,與既有慣例兩頭不合
severity: major
引句:「sidecar 狀態檔記上次衰減日,同日重跑不動」
佐證:file: `governance/autonomous_loop/backlog.py:70`
佐證:file: `governance/.gitignore:1`
說明:既有兩個「今天/這週做過沒」先例(run_exam/run_probe)都從既有 append-only 帳回推,不另開狀態檔;「per-machine 執行期狀態」另有明文不版控規則與 code-loop/ 活例。daily_decay 兩頭都沒接:新開獨立 JSON 檔且已隨 commit 帶著真實日期進版控——pull 到別台機器或舊 checkout 該值即與事實脫鉤,正是規則要防的「一提交就自作廢」。

## 對齊良好的面
- _save 的 tmp+os.replace 與 atomic_write_verify/_atomic_write_json 同款慣例。
- --outcome/--usd 沿用「不給不寫鍵」+「擋下:」訊息格式;結構化欄避開 note 散文紅線。
- requeue_pipeline_fail 逐行鏡射 requeue_unconverged。
- run_ledger 純讀側吃既有帳,不建新帳本。
- build_alert 走既有 send()/LINE_TOKEN 傳輸層,非新通道。
- backlog-archive.jsonl 判為觀點總帳一類版控,正確(反顯 decay-state 突兀)。
- 測試沿用 unittest 與 t_+check() 兩家慣例。
