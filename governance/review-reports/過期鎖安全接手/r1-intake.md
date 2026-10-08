preflight-4: ran

# 首輪前掃與紅燈

前一版未凍結草稿的語意缺口已在派席前改正；本輪只審 r1-snapshot.md。

- HIT：舊句「只有 PID 確認不存在且觀察的鎖仍是同一個檔案，才搬走舊鎖」→ 新句「取消 `_excl_lock_try` 的自動過期接手」。查 `scripts/lumos` 的 `_lens_wait_or_warm`：鎖記派工者 PID，背景工作可在它退出後繼續；PID 死亡不足以證明鎖無持有者。
- HIT：舊草稿僅以同程序 thread 釘 ABA → 新版 S1 用不同 PID 的 subprocess 屏障；`python3.14 scripts/test_lumos.py -k excl_lock_stale_takeover_is_single_owner` 在舊碼得 `parent=True`、`child.acquired=True`，前置兩條皆綠，目標條款翻紅。
- HIT：舊草稿把四條條款綁同一支測試 → 新版 S1–S4 各綁一支；`lumos spec-gate Projects/過期鎖安全接手_計劃` 為高風險、4/4 紅、弱證據 0。
- refcheck：0 claims，missing 0，out_of_range 0；prose-lint 0；pitfalls --check passed。這些機械結果不替代本輪語意審。

## 收貨判讀（同段同質合併）

- f1 HIT（c1、b1、r1）：注入 `os.write` 短寫得 `got=True, content='3'`；注入 ENOSPC 得 `False, exists=True`。折入 S3：補齊短寫、清自己半成品。
- f2 HIT（c2、b3、i1）：原 S1 測試只在 `rename` 建 ready，修後假紅；改攔 `Path.stat`，舊碼前置綠而雙持紅，新碼可直接拒絕。
- f3 HIT（c3、i2、a1）：hook rc 5 固定文案不讀 JSON；折入 S5 hook 端到端驗收，lands_in 加 `Systems/codex-harness`。
- f4 HIT（b2）：`_excl_lock_try` 的其他 OSError 被折成 False；注入 PermissionError 的 S3 翻紅，改由 caller 分流。
- f5 HIT（b5、k2）：`LUMOS_LENS_LOCK_OWNER` 記 foreground PID，`Popen` 背景 PID 未存；復原段禁以鎖內 PID 當背景存活證明，無法確認則留鎖。
- f6 HIT（b4）：Windows 無 symlink 權限時 `symlink_to` 會在準備階段中止；S2 只受控略過該子斷言。
- f7 HIT（i3）：`scripts/lumos` 與進行中計劃仍有自動接手舊說明；完工清單納入同步。
- f8 HIT（k1）：舊碼在新版已持有、mtime 過門檻時仍可搬鎖；S1 收窄同版，S6 加切換前停舊版進程的進場條件。
- f9 HIT（k3）：直接 revert 帶回 rename ABA，回退段改 roll-forward 或暫停入口。

九類均採信折入；refuted 0、accepted 0。原始六席 16 條，合併後九類；沒有把重複席報當九次獨立問題。

## 折入後鏡像核對

- HIT：S1 原本「修後可不進 stat」與「每個子程序必進競態間隙」衝突；已把前者定為永久回歸、後者限定歷史舊碼紅燈，測試也容許修後直接拒絕。
- HIT：建檔 PermissionError 在 lens 只進正文、未進條款；已補 S5 的 rc 2／`lock_error`／hook 端到端斷言。舊碼目前拋例外，測試翻紅。
