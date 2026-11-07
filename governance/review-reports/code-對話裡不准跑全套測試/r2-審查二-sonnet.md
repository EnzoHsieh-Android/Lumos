severity: major

## Finding 1:抽出 `_home_cache_append_line` 後,舊的守衛測試翻紅
severity: major
blocking: 是
引句:「+def _drift_m1_ledger_miss(root, tip, state):」
位置:`scripts/test_lumos.py:28950`(`t_private_dir_trust_shared_across_four_sites`)。它用函式名抓出 `_drift_m1_ledger_miss` 的原始碼,要求裡面含 `_trusted_private_dir`。修補把信任檢查搬進 `_home_cache_append_line`,這個函式本體已經沒有該字串。
最小重現:在 post clone 跑 `CLAUDECODE=1 python3.14 scripts/test_lumos.py -k t_private_dir`。
- 修後 c2fdb20:`✗ 私有目錄: _drift_m1_ledger_miss 有走共用的信任檢查`、`17 passed, 1 failed`。
- 修前 9c542ab:`18 passed, 0 failed`。

這條測試是在盯家目錄寫入點是否走信任檢查的守衛。修補沒有更新它,推送前閘與 CI 跑全套時會紅。更麻煩的是,它現在也不再保護新抽出的 `_home_cache_append_line`,守衛清單裡沒有這個名字。
歸因:有證據的修復回歸。

## Finding 2:對話擋全套的計數寫法沒有測試釘住
severity: minor
blocking: 否
引句:「+        _load_lumos_inproc()._home_cache_append_line((".cache", "lumos", "full-suite-guard"), "events.jsonl", line)」
這次修補的重點,是計數檔不能在 `~/.cache/lumos` 被換成 symlink 時寫到別處。我把這一行改回直接 `open(..., "a")` 再跑 `-k t_runner_chat`,結果 `20 passed, 0 failed`,全綠。同一份改壞的程式,我用 `HOME/.cache/lumos` 當 symlink 跑,`full-suite-guard` 目錄建到了 symlink 指向的位置,所以這個漏洞是真的。
現有測試只驗私有 HOME 正常寫入,沒有 symlink 或 `~/.cache` 是檔案的案例。
歸因:有證據的修復回歸,也就是修補宣稱要解的事沒有測試守住。

## 回答三題

**① 修補宣稱的行為證據**
- 計數改走 `_home_cache_append_line`:在 post clone 用 `HOME/.cache/lumos` 是 symlink 跑一次,symlink 目標目錄保持空,沒寫到別處。`~/.cache` 是檔案時回 rc=2 並正常擋下,沒有崩。一般 HOME 下寫出 `{"kind":"block",...}`,目錄權限 `drwx------`。這是手動重現的證據。
- `_drift_m1_ledger_miss` 行為不變:`-k ledger_miss` 與 `-k t_drift_m1_review_r3_ledger_miss_short_write` 的 6 支測試全過,行為成立。但守衛測試翻紅(Finding 1)。
- `t_runner_chat_env_probe` 驗 CLAUDECODE 拿掉:我把進入點的 `pop("CLAUDECODE")` 改成 `pass`,`t_runner_chat_env_probe` 與 `t_runner_chat_full_suite_block_process` 都翻紅(`18 passed, 2 failed`),成立。
- 其他三項(真子程序測試的前置判斷、紅燈超過 10 支、讀 `_FANOUT_CHILD_ENV` 常數)只做了通過性確認,沒逐項變異:`-k t_runner_chat` 20 支、`-k t_prepush_red` 6 支全過。

**② 相鄰路徑**
- 平常啟動(帶 `-k`)不會載入 `scripts/lumos`:`_chat_guard_log` 只在擋下或放行時才叫 `_load_lumos_inproc`。擋下那條路徑耗時約 1.7 秒,可接受。
- 載入失敗時:`_chat_guard_log` 是 `except Exception: pass`,擋下判斷與 rc 2 不受影響。我讀過程式碼確認,沒有實際注入載入失敗。
- `t_runner_chat_env_probe` 在推送前閘與 CI 不會冤枉紅:進入點無條件 pop `CLAUDECODE`,本來沒設也一樣通過。
- 原有呼叫者 `_drift_m1_ledger_miss`:行為成立,守衛測試除外(見 Finding 1)。

**③ 新發現在修前修後各是什麼結果**
- Finding 1:修前綠,修後紅。
- Finding 2:修前的自寫 `open` 同樣無測試,修後換成安全寫法但仍無測試釘住。

未驗範圍:沒跑全套(規定不准),所以 Finding 1 之外是否還有其他引用 `_drift_m1_ledger_miss` 原始碼的測試翻紅,沒有逐一確認。

我製造的暫存(`gctl-run-*` 現場與測試用 HOME)只在 `/tmp/lumos-seat-work/code-對話裡不准跑全套測試/審查二-sonnet/` 下,尚未清除,交給收貨者依派工詞處理。
