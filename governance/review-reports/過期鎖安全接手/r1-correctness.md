severity: major

# 正確性席

## c1：建鎖內容寫入失敗會留下空鎖

severity: major
blocking: 是
引句:「代價是程序異常結束後可能留下鎖，需要先確認真持有者與背景工作均已停止，再由人移除。」
file: `scripts/lumos:33843`
file: `scripts/lumos:33845`
`os.open` 成功後若 `os.write` 因 ENOSPC 等錯誤失敗，現碼留下空鎖且 fd 未關；停止自動接手後此鎖永久阻斷兩個 caller。審查席注入 `OSError(28)` 實測 `first=False, exists_after_failed_write=True, size=0, second=False`。需只清理由本次成功建立但尚未完成內容寫入的鎖，所有分支關 fd。

## c2：S1 屏障依賴將被刪除的 rename

severity: major
blocking: 是
引句:「跨程序屏障先證明舊碼回 `True/True`。」
file: `scripts/test_lumos.py:54397`
file: `scripts/test_lumos.py:54429`
正確修法不呼叫 `os.rename`，子程序不建 `ready`，修後仍在前置斷言假紅。歷史 `True/True` 證據應另存；正式回歸使用不依賴舊分支的跨程序起跑屏障。

## c3：hook 吞掉新狀態

severity: major
blocking: 是
引句:「若期限到時鎖齡已超過舊過期門檻且仍無快取」
file: `scripts/hooks/claude/dispatch-lens-hook.py:349`
file: `scripts/hooks/claude/dispatch-lens-hook.py:353`
hook 對 rc 5 只用固定超時文案，忽略 `lock_uncertain`，實際派工流程看不到需查鎖狀態。需把此狀態傳到 hook 或以不同返回契約分流，並做端到端測試。

S2、S3、PRIOR-ART、RETIRE-IF、回退、實務隱患其餘已讀，無 finding。

總結：最嚴重 severity: major；blocking 3 條。
