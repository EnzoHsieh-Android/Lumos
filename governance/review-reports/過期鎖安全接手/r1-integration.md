severity: major

# 整合席

## i1：S1 依賴將刪除的分支

severity: major
blocking: 是
引句:「跨程序屏障先證明舊碼回 `True/True`。」
file: `scripts/test_lumos.py:54429`
子程序只有執行舊 rename 才建 ready，取消接手後無法完成前置條件，修後測試假紅。舊碼競態重現與新碼驗收應分開。

## i2：hook 丟失不確定狀態

severity: major
blocking: 是
引句:「回「狀態未知、需檢查鎖」，不能宣稱確有背景工作在算。」
file: `scripts/hooks/claude/dispatch-lens-hook.py:349`
file: `scripts/hooks/claude/dispatch-lens-hook.py:353`
mock `subprocess.run` 回 rc 5 與 `lock_uncertain=true`，hook 仍只輸出通用超時文案；真正使用者看不到鎖需查核。需定義傳遞方式並加 hook 整合測試。

## i3：舊說明與新行為會衝突

severity: minor
blocking: 否
引句:「取消 `_excl_lock_try` 的自動過期接手」
file: `scripts/lumos:14979`
file: `scripts/lumos:15034`
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移改法_計劃.md:43`
舊註解及進行中計劃仍宣稱過期會自動接手；完工時需同步，避免下個接手者依錯誤前提修改。

Issue 結構、Systems 落點、Spec 範圍與回退其餘已讀，無 finding。

總結：最嚴重 severity: major；blocking 2 條。
