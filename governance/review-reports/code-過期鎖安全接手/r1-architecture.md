severity: minor

## 1. 分層與依賴方向

file: `scripts/lumos:33839`  
file: `scripts/lumos:33906`  
file: `scripts/hooks/claude/dispatch-lens-hook.py:354`

已讀，無 finding。

鎖的取得、殘留判斷及 JSON 狀態都留在 `scripts/lumos`；hook 只解析 `lock_error`／`lock_uncertain` 並轉成對使用者可見的派工提示，沒有從 hook 直接呼叫鎖原語。這符合既有「hook 是薄殼、機制住在 lumos」的方向。計劃點名的固定席功能邊界也一致：圖譜計算和快取互斥由 lumos 負責，hook 只負責傳送結果。

## 2. 命名、錯誤處理與日誌

### A1：吞掉建鎖失敗後被 telemetry 記成成功

severity: minor  
blocking: no  
file: `scripts/hooks/claude/dispatch-lens-hook.py:367`  
引句:「`_debug("lumos dispatch-lens 鎖無法建立,已附錯誤說明")`」

`lock_error` 分支把錯誤提示附進派工詞後直接 `return 0`，卻沒有像緊接著的 timeout 分支一樣呼叫 `_hookevent.mark(...)`。共用 telemetry 契約明寫：hook 內部吞掉的失敗必須標成 `error`，否則 `guard()` 會在正常返回時記為 `ok`，見 `scripts/hooks/claude/_hookevent.py:111` 與 `scripts/hooks/claude/_hookevent.py:150`。

具體影響是鎖目錄權限錯誤或建檔失敗時，審查席會正確看到「鎖無法建立」，但 governance/runtime/hook-events.jsonl 同一次卻記成 hook 成功；`lumos enforcement` 因而可能把持續失敗的派工鏡頭顯示為近期正常運作。新增測試目前只驗派工詞含錯誤提示，沒有驗事件 kind，見 `scripts/test_lumos.py:54657`。此分支應在返回前標記 `mark("error", ...)`。

其餘命名與錯誤分流已讀，無 finding。`FileExistsError → False`、其他建鎖或寫入錯誤向上傳遞，再由筆記庫與鏡頭各自在邊界轉成自己的錯誤，符合 `python-idioms` 的「邊界才轉換、保留原原因」。CLI 使用 `print` 是既有命令列呈現慣例，不套用長跑服務的 logging 要求。

## 3. 是否引入第二種機制

file: `scripts/lumos:15064`  
file: `scripts/lumos:33904`  
file: `scripts/lumos:33839`

已讀，無 finding。

筆記庫鎖與派工鏡頭仍共用 `_excl_lock_try`；本案移除的是同一原語內的過期接手分支，沒有新增 `flock`、輔助救援鎖或另一套 PID 判活。兩個呼叫端只保留各自的等待和提示政策，沒有複製取鎖演算法。圖譜中的 `Systems/lumos-cli-write`、`Systems/codex-harness` 與計劃的「不增加第二套機制」聲稱和程式一致。

不對齊共 1 條、major 0 條，最重等級 minor。
