severity: major

# 架構對齊席

分層與依賴方向：不對齊，見 a1。

命名與錯誤處理：`lock_uncertain` 在 hook 邊界遺失，見 a1。

第二種做法：已讀，無 finding；共用 `_excl_lock_try`，未引入另一套鎖。

lands_in 落點：不對齊，漏派工 hook 的 home，見 a1。

## a1：狀態未知訊息未穿過 hook 邊界

severity: major
blocking: 是
引句:「若期限到時鎖齡已超過舊過期門檻且仍無快取，回「狀態未知、需檢查鎖」，不能宣稱確有背景工作在算。」
file: `scripts/hooks/claude/dispatch-lens-hook.py:349`
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:6`
設計保留 rc 5，但 hook 對所有 rc 5 固定改寫成一般超時說明，不解析新欄；S4 只測底層仍可綠，實際派工詞失去需查鎖語意。hook 檔的 home 是 `Systems/codex-harness`，目前 lands_in 漏列。審查席 mock rc 5 + `lock_uncertain=true`，派工詞斷言「狀態未知」「檢查鎖」翻紅。

其餘已讀，無 finding。

總結：最嚴重 severity: major；blocking 1 條。
