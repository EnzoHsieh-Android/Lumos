severity: minor

上一輪四條(另寫 git 包裝、期限另起、逾時例外慣例、同函式 import 寫法)確認已收:git 入口全走 `_lens_git`(`scripts/lumos:43983`,逾時與 OSError 回 None)、淺 clone 判斷走既有 `_git_is_shallow`(`scripts/lumos:6018`)、跳脫走 `_esc_clean`(`scripts/lumos:11057`)、期限沿用 `_DISP_BUDGET`(`scripts/lumos:46491`)、讀帳走同一支 `_codeloop_ledger_events`。剩兩條小的不一致,都不動結構。

## 問 1 分層與依賴方向
乾淨。新函式都在 code-loop 判定那一層,只往下呼叫 `_lens_git`/`_lens_full_sha`/`_lens_range_ok`/`_codeloop_record_valid_ex`/`_git_is_shallow`,沒有反向或跨層直呼;表態閘用 `merge_side` 回呼注入(`_dispositions_verdict` 簽章 `scripts/lumos:47058` 一帶),不直接 import 審查那一關。
引句:「讀「目標分支最後一筆」與合併提交「合進來那一側」兩條路共用這一支,哪些事件算數只寫一次。」

## 問 2 命名與錯誤處理
結構對,細節兩處不一致(F1、F2)。「判不了/時間不夠 → 不認」的訊息措辭在各函式間統一,例外一律收成判不了,符合放寬路徑要保守的方向;期限用盡回 None 的形狀對照 `_lens_git` 回 None,一致。
引句:「★任何例外都收成判不了、不認★(代碼審 r1 三席實測:」

## 問 3 第二種做法
沒有第二套 git 入口、讀帳、期限或跳脫。`_merge_side_left` 是新的小輔助(見 F1 的次要說明),不算另一套。`_disp_record_for` 回四元組、把延後後的期限一路帶回:鄰居 `_codeloop_record_valid_ex` 是三元組(`scripts/lumos:46858`)、`_codeloop_record_valid` 二元組,四元組是新形狀但語意(延後期限)只有這裡需要,且已在 docstring 寫明,不列入。
引句:「表態紀錄 → (紀錄或 None, 有效嗎, 為什麼, 延後過的期限)。」

## F1 期限用盡的處理形狀不一致(淺 clone 判斷用魔術數)
severity: minor
blocking: 否
同檔其他關卡處理「期限用盡」是先判 None 再回明確的一句原因(同函式內 `_codeloop_merge_side` 對 `_codeloop_record_valid_ex` 就是 `if left is None: return None, "時間不夠…"`),唯獨淺 clone 判斷把用盡的期限換成 0.01 秒再交給 git、靠逾時例外被外層 except 收走,原因字串變成「TimeoutExpired」而非「時間不夠」。另外對照 `scripts/lumos:43455` 一帶既有寫法 `min(_disp_git_timeout(), deadline - _t.monotonic())`,新的 `_merge_side_left` 沒有對單次 git 夾 `_disp_git_timeout()` 上限(單次可吃滿整段 20 秒),也算同一件事的第二種寫法。建議:淺 clone 那行比照其他處先判 left、並讓 `_merge_side_left` 回 `min(_disp_git_timeout(), …)`。
引句:「if _git_is_shallow(repo_root, timeout=_merge_side_left(deadline) or 0.01):」

## F2 例外訊息只留類別名、丟掉例外內容
severity: minor
blocking: 否
同檔判不了的訊息慣例是 `{ex.__class__.__name__}: {_kill_esc(ex)}`(`scripts/lumos` 的 doctor/kill 路徑),這裡只印類別名。使用者看到「判不了合進來那一側(OSError),不認」無從知道是哪個 git 或哪個檔;若顧慮控制字元就該套 `_esc_clean`,而不是整段拿掉。
引句:「return None, f"判不了合進來那一側({ex.__class__.__name__}),不認"」

不對齊共 2 條,其中 major 0 條
