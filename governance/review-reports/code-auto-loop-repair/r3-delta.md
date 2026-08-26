### e-f1 空 pid 讓行判斷用 stat -f %m,平台不符/失敗時兜底方向反轉成「該接管」
severity: major
引句:「LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCKDIR" 2>/dev/null || echo 0) ))」
佐證:file: `governance/autonomous-loop.sh:27`
說明:stat -f 是 BSD/macOS 專屬(GNU 的 -f 是檔案系統模式),全庫僅此一處新依賴;|| echo 0 兜的是 mtime 不是判斷結果——stat 失敗時 LOCK_AGE≈18 億秒>3600,「量不出」被靜默當「最該接管」,方向與修法初衷(不確定就讓行)完全相反。

## minor 觀察(不逼修,收進驗證誠實邊界)
- chmod 444 重現法在 root/容器環境不成立(root 繞過權限位,測試會為錯誤理由變紅——非假綠)。
- covered 持續寫不進時,gap 反覆退回 backlog 疊計數,兩條既有 LINE 示警都不會觸發(skip 的帳在處置結果前已記,r1 既有時序非本 delta 引入),只有 log ⚠ 累積。

## 逐項查過乾淨
skip 記帳時序屬 context 行非 delta;d-f1 雙呼叫 retry 語意安全無重複持久化;三處「放回成功才刪標記」互相吻合;_stash_bad 空行邊界與去重成本刻意取捨;兩條新斷言真釘住語意;97 測實跑全綠。
