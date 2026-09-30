severity: minor

## F1 共用的新建層改成「建完必須 chmod 成功」,Windows 上第一次建目錄必失敗,鄰居第一次退路
severity: minor
blocking: 否
引句:「    return _chmod_no_follow(cur, 0o700)」
file: `scripts/lumos:34935`(_mkdir_private_layer 尾行)、`scripts/lumos:34984-35002`(_chmod_no_follow:os.open 目錄 + os.fchmod)、`scripts/lumos:66`(_IS_WIN,工具有 Windows 路徑)
1. 改前新建層只要 mkdir 成功就過;改後 mkdir 成功還要 `_chmod_no_follow` 回 True 才過,而它靠「os.open 開目錄再 os.fchmod」。
2. Windows 上 os.open 開目錄一般丟 PermissionError(被 except OSError 吞成 False),fchmod 也不存在;所以新建的那一層回 False,`_mkdir_trusted_under_home` 整支回 False(目錄其實已建出來)。第二次起走 FileExistsError 分支就過了。
3. 受影響的鄰居:vault-lock 第一次改退到筆記庫內鎖檔並印「放寫入鎖的資料夾用不了」提醒,同時間後啟動的行程用 home 鎖,兩個行程各拿不同鎖檔,互斥落空(僅首次建目錄那個窗口);dispatch-lens、bound-filter、drift-defs/m1 首次不寫快取或留痕。
4. ⚠ 未能重現:本機無 Windows,Python 在 Windows 開目錄失敗是已知行為但這裡沒跑到;程式碼自己也寫「本機沒有 Windows 可驗」。macOS/Linux 上不受影響。若專案不承諾 Windows 上這幾個快取/鎖可用,可忽略。

## 其餘查過、未成 finding 的點
- 兩行程同建同一層:實測 16 個行程並行建 `.cache/lumos/vault-lock`,umask 002 與 277 下 16/16 都回 True、最終 0700;敗方走 FileExistsError 只查不 chmod,不會有第二次 chmod 打在別人剛建的層。
- 既有目錄權限:只有「這次自己 mkdir 成功」的層才 chmod,舊的 0755/0775 目錄不被改;舊 0775 上層仍照舊判不信(改前就這樣)。副作用僅:家目錄下原本不存在的 `~/.cache` 現在會是 0700 而非 0755。
- 留痕檔 O_NONBLOCK:實測 200 次執行緒並行追加 200 行全在(小於 PIPE_BUF 的單次 O_APPEND write);FIFO 無讀端 → False 且 0.00 秒不卡;FIFO 有讀端 → S_ISREG 擋下、沒寫入(讀端 b'')。對一般檔 O_NONBLOCK 無作用。
- 每 256 個名稱看時間:`_drift_m1_ticker` 只是計數加取模,成本可忽略;`_drift_m1_line_names` 每行新建計數器,小桶(<256)不會 tick,但每行工作量上限是名稱總數×一行子字串比對,行與行之間仍有每行前的檢查,超時最多多一行,不成問題。
- 回退 89884251:`group_ok` 參數與 `_mkdir_private_layer` 一起消失,鄰居呼叫都沒傳 group_ok,簽名回到 r1 狀態且自洽;m1 與鄰居回到「umask 002 建不起」的 r1 已知狀態,沒有半套狀態。

## 圖譜鏡頭逐條判定
- Systems/lumos-cli-read.md(search 濾網 INVARIANT)、bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-lifecycle、design-loop:不影響——diff 沒動 search、綁定測試閘、guard kill、授權白名單、re-inject、處置閘的邏輯。
- pitfalls-code-loop(RISK)與其餘只列名節點(vault-lock、dispatch-lens、bound-filter 相關):共用的 `_mkdir_private_layer` 對它們只多做「新建層 0700」,判準未放寬;唯一新增風險見 F1(Windows 首次)。
最高等級:minor
