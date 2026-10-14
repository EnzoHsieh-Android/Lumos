severity: clean

## 資安席第三輪報告(推送前收集)

我用掛鉤自己的假 lumos 測試台,對真的 `scripts/hooks/pre-push` 做了攻擊實驗,沒有找到能讓本該被擋的推送通過的洞。實驗環境放在 scratchpad 的 `cr-ppc3-資安/`,做完已刪。另外跑了 `python3.14 scripts/test_lumos.py -k prepush_interrupt_stops`,結果 30 passed、0 failed。

### 實驗一:任一道擋下,最後 rc 是否一定非零

**暫存目錄與擋下紀錄:**
- 準備:先讓 doctor 擋下,再在 doctor 或 anchor 那一步動手腳。
- 動手腳的做法有五種:
  - 刪掉暫存目錄。
  - 把暫存目錄換成指向別處的符號連結。
  - 把暫存目錄換成指向不存在路徑的符號連結。
  - 把 `blocks` 檔換成目錄。
  - 把暫存目錄改成唯讀。
- 結果:五種全部 rc=1,全套測試沒跑。
- 原因:擋不擋只看記憶體裡的 `_PP_BLOCKED` 和 `_PP_NBLK`。寫檔失敗只讓彙總少列幾筆,會印「其中有 N 筆的原因沒寫進暫存檔」。
- 符號連結的情況:結束時 `rm -rf "$_PP_TMP"` 只刪連結,不刪目標。
- 順帶一提:暫存目錄被換掉時,彙總會顯示「N 筆擋下(0 道閘)」。這是版面小瑕疵,不影響擋不擋。

**偽造或多行的 `LUMOS-BLOCKS:`:**
- 假 lumos 在 code-loop 回 rc=1,並輸出下列幾種形狀。五種全部 rc=1:
  - 空清單。
  - 完全沒有那一行。
  - 種類裡夾 `$(touch …)` 和反引號。
  - 種類是 `,,,, ,*,../..`。
  - 種類含 tab 和換行。
- 命令注入沒有成立,標記檔沒有被建立。
- 在正文裡夾多行偽造的 `LUMOS-BLOCKS:` 也是 rc=1。掛鉤取最後一行,最後一行是空清單時,退回「至少記一筆」。
- 3000 個種類:rc=1,耗時 4.6 秒,有 3000 筆彙總。
- rc=0 時,偽造的 `LUMOS-BLOCKS:` 完全不起作用。擋不擋只看 `cl_rc==1`,那一行只影響原因文字。

**lumos 端判定:**
- 已讀,無 finding:`_codeloop_guard_verdict` 的所有回傳都經過 `_fin`。
- 放行站點、環境變數跳過、合併側留痕通過,都不能蓋掉前面記下的擋下。
- 帶 `--keep-going` 且有擋下時,`cmd_code_loop` 一定回 `1 if blocked`。

### 實驗二:訊號打斷收集途中

- 設定:先讓 doctor 擋下一筆,再對掛鉤送訊號。
- 訊號與位置:
  - 訊號:SIGHUP、SIGINT、SIGTERM、SIGQUIT、SIGUSR1、SIGPIPE、SIGALRM。
  - 位置:每支檔有家、存量漂移、回頭重讀三處。
- 結果:共 21 組,全部非零,全套沒跑。
  - HUP 回 129,INT 回 130,TERM 回 143。
  - 沒接陷阱的訊號,由 bash 預設行為殺掉掛鉤,回報為負的訊號號。
- HUP 陷阱只會 `exit 129`,沒有路徑會回 0。
- 離開碼 129 以上都進 `pp_stop_if_signaled`,整支停下。
- 現有測試⑨ 驗證:只對掛鉤送 HUP 時,全套那一片也被收掉,暫存目錄不留東西。

### 實驗三:包組重導向吞掉錯誤後是否變成放行

- 已讀,無 finding。
- 寫入類:`{ : > touched.txt; } 2>/dev/null || return 0` 失敗時回空,doctor 不帶 `--touched-from`,只會更嚴。
- 寫入類:`{ git diff … >> touched.txt; } 2>/dev/null || _ok=0` 失敗時 `_ok=0`,整份清單作廢,也是更嚴。
- 寫入類:`{ cat … > tests.log; } 2>/dev/null || true` 只影響紅的列表,`_rc` 不受影響。
- 判成放行的路徑:impact 暫存檔失敗時走 `rm -f`,退回自己算,只影響合約測試提醒這條,那條本來就不擋。
- 判成放行的路徑:spec-gate 的 `tee` 失敗時,`sg_rc` 取自 `PIPESTATUS[0]`,而 `grep` 在檔不存在時回非零,所以退回全套,偏嚴。
- 重導向的位置都沒有改變退出碼的語意,只是不再印開檔雜訊。

### 觀察(不成立為 finding)

- **彙總讀檔的資源風險:** 若暫存目錄裡的 `blocks` 被換成指向 `/dev/zero` 或 FIFO 的符號連結,`push-summary` 的 `read_bytes` 和掛鉤的簡版彙總會卡住或吃記憶體。結果是推送卡住,不是放行。做這件事需要先控制 lumos 或暫存目錄,而那個身分本來就能直接讓閘回 0,所以不算新的攻擊面。
- **早擋下後繼續跑後面的閘:** anchor 沒簽名擋下後,後面的 code-loop 和合約測試仍會用沒簽名的測試檔跑。我沒找到任何會留下可被後續推送沿用的綠燈快取。`_bound_tests_check` 只寫治理帳,不寫放行憑證。

最高等級 clean,blocking 0 條。
