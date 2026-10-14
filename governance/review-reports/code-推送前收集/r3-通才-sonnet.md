severity: clean

已讀,無 finding。

**主程式拿掉 summary 與原因表**
- 原因表只被 `_codeloop_kg_finish` 的 `summary` 欄位用。該欄位只出現在帶 `--keep-going` 時 `blocks` 陣列的每筆。
- `check` 不帶旗標時走 `if not keep_going: return v`,不經過這段。輸出文字沒變。
- 帶旗標的文字模式印的是 `reason_kind` 與 `reason`,沒用 `summary`。
- 我在 `scripts/lumos` 與 `scripts/hooks/pre-push` 搜了 `summary` 欄位,沒有其他讀者。
- 掛鉤只解析文字輸出的 `LUMOS-BLOCKS:` 行,不讀 `--json`。
- `--json` 的 `blocks` 少一個欄位,只影響外部機讀者。repo 內沒人讀,屬刻意收窄。
- 我跑了 `-k keep_going`(43 支)與 `-k prepush_cl_reason`(3 支),全綠。

**掛鉤配舊版 lumos**
- `pp_cl_reason` 句子表仍在掛鉤內,不向 lumos 要。
- 舊版 lumos 的 `blocks` 多一個欄位,掛鉤不讀,不影響。

**`impact_once` 與清單檔改成包組**
- 三處:`impact_once`、`pp_touched_file` 的兩處、測試 log 的 `cat`。
- 包成 `{ …; } 2>/dev/null` 後,命令的退出碼不變,後面的 `&& [ -s ]`、`|| return 0`、`|| _ok=0` 照舊。
- 命令本身的 stderr 仍被吞,只多吞掉開檔失敗的訊息。語意沒有退化。
- `bash -n scripts/hooks/pre-push` 通過。

**HUP 陷阱與 `_pp_kill_jobs` 取代自記 pid**
- 我用 `/bin/bash` 3.2.57 照掛鉤結構重現:外層與兩個 `( run_group … ) &` 子殼,每個子殼起三片 `sleep`。
- 對外層送 HUP 後,`EXIT` 陷阱照跑,所有 sleep 都被收掉(存活 0)。
- 子殼裡的 `$(jobs -p)` 在 3.2 正確列出自己起的各片。
- `& 起片` 與記 pid 之間的競態確實消失。後面的 `wait "$_p"` 仍用 `_pids`,只拿來收離開碼,沒有副作用。

最高等級 clean,blocking 0 條。
