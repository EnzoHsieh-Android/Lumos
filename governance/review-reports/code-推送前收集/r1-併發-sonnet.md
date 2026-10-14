severity: major

做了什麼:用 `/bin/bash` 3.2.57 實驗新的陷阱,模擬掛鉤被砍(SIGTERM)和 Ctrl-C(對整個行程群組送 SIGINT)。實驗用的暫存已刪,孤兒行程也已清掉。

## finding 1
severity: major
blocking: 是 — `_pp_kill_jobs` 想收掉背景工作,實測收不掉,孫行程(測試片)會成孤兒;這正是這個改動宣稱要解決的事
引句:「trap '_pp_kill_jobs; exit 130' INT」

問題:`_pp_kill_jobs` 只對 `jobs -p` 列出的直接子行程送 TERM。全套測試是 `( run_group ... ) &` 起的子殼,子殼再用 `&` 起 `test_lumos.py` 各片,各片是孫行程,`jobs -p` 看不到。

兩條路徑實測結果:
- **被砍(TERM)**:`jobs=[子殼 pid]`,子殼被殺,EXIT 陷阱照跑,兩個模擬測試片 `sleep 300` 的 ppid 變 1,仍在跑。
- **Ctrl-C(對整個行程群組送 SIGINT)**:掛鉤回傳 130,兩個孫行程一樣存活。非互動 bash 用 `&` 起的背景命令會忽略 SIGINT,所以群組的 SIGINT 也殺不掉它們。

具體失敗情境:
- 推送進入全套測試後按 Ctrl-C,掛鉤退出,約 4 片 `test_lumos.py` 繼續跑到結束,要幾分鐘到八分鐘。
- 這些片的 stdout 指向已被 `rm -rf "$_PP_TMP"` 刪掉的 `shards/*.log`,輸出沒人看。
- 它們還會佔 CPU,並照常使用測試暫存(例如 `gctl-run-*`)。
- 使用者馬上重推,就會有兩批全套同時跑,互相搶資源。

修法方向:孫行程也要被收掉,例如讓 `run_group` 的子殼自己設 TERM 陷阱去 kill `_pids`,或在 `_pp_kill_jobs` 裡用 `pkill -P` 遞迴收子孫。

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:300-303`(陷阱),`:800-829`(`run_group` 與子殼)。

## finding 2
severity: minor
blocking: 否 — 只是暫存檔殘留,不影響擋不擋
引句:「_TESTS_LOG="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-tests-XXXXXX" 2>/dev/null || true)"」

問題:`_AUTOLOOP_LOG` 與 `_TESTS_LOG` 建在 `$_PP_TMP` 之外,EXIT 陷阱只清 `$_PP_TMP`。測試跑到一半被 INT/TERM 中斷時,這兩個空檔會留在 `$TMPDIR`。

這是舊問題,這次改動沒有把它收進 `$_PP_TMP`。測試紅時,訊息指給人看的 log 路徑刻意保留,所以我不把紅的情況算成問題。

佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push:693-694`。

## 已讀,無 finding
- **陷阱拆成 EXIT/INT/TERM**:INT 與 TERM 都會 `exit`,再走 EXIT 陷阱,實測 EXIT 只執行一次,回傳碼 130 與 143 正確。舊版「陷阱結束後照樣往下跑」的毛病確實修掉了。
- **`jobs -p` 放在 `$(...)` 裡**:bash 3.2 能拿到直接子行程的 pid。
- **`$_PP_TMP/blocks` 的生命週期**:建於 `$_PP_TMP` 內,`pp_record_block` 寫入失敗用 `|| true` 吞掉,擋不擋只看記憶體裡的純量。彙總前被中斷時整個目錄由 EXIT 清掉,沒有殘留。
- **中斷清單**:列出刻意不接中斷的 5 支(`loop escape`、`test-layers`、`bound-tests --advisory`、`pitfalls`、`push-summary`),理由合理。`push-summary` 之後一律 `exit 1`,中斷不會變成放行。我只讀了清單,沒逐支驗證。
- **收集模式多跑的時間**:現在擋下後會繼續跑完其餘閘,最多多出約 13 秒加每 ref 漂移檢查的預算;全套測試前有統一判斷點,不會白燒八分鐘。已讀,無 finding。

最高等級 major,blocking 共 1 條。
