severity: minor

整份 diff 最高只到小問題。新 tty 測試在本機有效,拿掉 `O_NOCTTY` 會翻紅。我找到三條小問題:FIFO 寫入會永久卡住、`--history` 的開跑前檢查漏一種情況、新測試以 root 跑會假紅。

## Finding PLT6-01
severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/scenario_probe.py:64`
- 輸入:`--out` 指到一個沒有讀端的 FIFO。開跑前檢查對 FIFO 直接放行,整批模型跑完才走到這裡。
- 壞在哪:以 `O_WRONLY` 且不帶 `O_NONBLOCK` 開 FIFO,沒有讀端時會永久阻塞。額度已花完,結果寫不出去。
- 重現:`mkfifo ff`,再呼叫 `sp._atomic_write_text('ff','{}')`。
  - 修前版:立刻印出 `done`,FIFO 被換成 0600 的普通檔(這也是修補原本要解的問題)。
  - 修後版:4 秒後仍卡住,必須 kill。
- 歸因:有證據的修復回歸。修前不卡,修後新增了這個行為。

## Finding PLT6-02
severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」
file: `scripts/scenario_probe.py:44`
- 輸入:`--history` 指到唯讀目錄下尚不存在的檔。
- 走到哪一段:`replace=False`,所以略過這行的父目錄可寫檢查,只剩 `path.parent.is_dir()`。
- 壞在哪:開跑前檢查回 None。整批跑完後 `os.open(..., O_CREAT)` 才報 `EACCES`。這與筆記宣稱的「開跑前檢查 `--out` 與 `--history`」不符。
- 重現:`chmod 555 hd`,呼叫 `_output_target_problem('hd/h.jsonl', replace=False)`,回傳 None。同一路徑直接 `os.open` 則報 `[Errno 13] Permission denied`。
- 歸因:有證據的原有漏查。修前一樣在批次結尾才失敗,修補補了檢查但沒補這個情況。

## Finding PLT6-03
severity: minor
blocking: 否
引句:「check("既有唯讀檔照舊拒絕寫入且內容不變", refused and ro.read_text() == "keep")」
file: `scripts/test_lumos.py:38524`
- 輸入:以 root 執行測試,例如 Docker 容器 CI。
- 走到哪一段:`os.access(path, W_OK)` 對 root 在普通檔上恆為真,所以產品碼不拒絕,直接用 `os.replace` 換掉 0444 檔。
- 壞在哪:`refused` 為 False,測試翻紅。這是環境造成的假紅,不是跳過。產品碼在 root 下也會默默覆蓋唯讀檔。
- 重現:我不是 root,沒法直接重現。我用 `patch os.access → True` 模擬,結果是 `NOT refused; content={}`,檔案模式維持 0o444。
- 歸因:有證據的修復回歸。唯讀測試和 `os.access` 判斷都是這次新增的。

## 鏡頭 1:新 tty 測試
- **本機通過**:`-k confirm_tty` 為 8 passed。新測試約 1.9 秒,遠低於 60 秒超時。
- **mutation 翻紅**:把 `O_NOCTTY` 拿掉後,「現場成立」斷言仍綠,「沒收到掛斷」翻紅,子程序 returncode 為 -1。
- **對照組**:同樣拿掉 `O_NOCTTY`,用新 session 啟動執行器再跑舊測試,`t_confirm_tty_unit` 仍六項全綠。這證實舊測試確實不能當防回歸。
- **SourceFileLoader 載入**:載入 `scripts/lumos` 時,在隔離的 HOME 與 cwd 下用 `python3.14 -I` 執行,沒有寫任何檔。檔內沒有網路呼叫。
- **假紅與假綠**:`start_new_session=True` 保證子程序是 session leader 且沒有控制終端,所以現場斷言在各環境都成立。`/dev/tty` 節點不存在也走 `OSError` 分支,結果一樣是 `ctty=False`。測試不會因環境跳過,真有問題時是紅。
- **非 POSIX**:不在上述環境內,這種情況會用 `_SrcOnly` 跳過並明講。
- **沒驗到的部分**:
  - Linux、GitHub Actions 的 ubuntu 與 macOS runner、容器、root 下的實際行為,我都沒跑。
  - Linux 沒有 `O_NOCTTY` 時,session leader 開 pty slave 會取得控制終端,這是 POSIX 通則;我這邊只驗了 macOS。

## 鏡頭 2:探針寫入
- `O_NOFOLLOW` 只影響最後一段路徑是符號連結的情況,對 FIFO 與字元裝置沒有效果。會出問題的是 FIFO 的阻塞(見 PLT6-01)。
- `/dev/null` 能正常寫入。
- 本機先建了符號連結,寫入前再看是否仍是連結,連結目標檔沒被動到。
- `O_NOFOLLOW` 在 Windows 退成 0 時,只有 lstat 判為字元裝置才進裝置分支,不會因此跟隨連結。
- `os.access` 用的是 real uid,`geteuid` 是 effective uid。setuid、ACL、唯讀檔系統下兩者可能不一致,我沒有具體失敗場景可報。
- Windows:新增的 `os.geteuid` 只在覆寫既有普通檔時呼叫,修前沒有這個呼叫,會比修前多一個 `AttributeError` 場景。但探針本身要用 rsync,消融腳本又 `import fcntl`,Windows 本來就跑不起來,所以不單獨列為 finding。`os.fchmod` 在 Windows 自 Python 3.13 起存在,專案最低版本是 3.14,不受影響。
- umask 的 `os.umask(0)` 再還原有短暫的跨執行緒競爭,但探針沒有執行緒(grep 無結果),不列。

## 固定席逐條判定
- **`lumos-cli-lifecycle` ★INVARIANT★ re-inject**:不影響。diff 只動 `_confirm_tty` 的測試與同節點 PITFALL 文字,reinject 路徑與 `t_reinject_preserves_outside` 都沒碰。
- **`codex-harness`**:不影響合約。新增的 PITFALL 與 WHY 描述大致與程式一致,只有「開跑前檢查 `--history`」的說法被 PLT6-02 推翻,裝置與 FIFO「直接寫」被 PLT6-01 限縮。
- **`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`design-loop`**:不影響。diff 沒碰搜尋濾網、綁定測試閘、guard kill、授權檔白名單與設計審處置閘。
- **`測試假綠形態` ★INVARIANT★ 還原翻紅釘須配前置斷言**:符合。新測試有「現場成立」斷言,我的 mutation 實驗證明現場斷言綠、主斷言紅,與筆記敘述一致。
- 其餘「超出上限只列名」的節點:未逐篇判。

## 修補三問
1. **原問題的修復證據**:
   - tty:前面的 mutation 實驗已證明修前版會翻紅、修後版轉綠。
   - 輸出寫入:同一個 `_atomic_write_text`,修前新檔模式為 0600,250 字元檔名報 `errno 63`;修後新檔模式 0644,長檔名可寫。
2. **相鄰路徑**:自己擁有的檔保留權限、輸出符號連結、wait、第四輪報表與正式派工各子集都通過(fifth_round 16、report 14、wait 2、cli_entry 2、ledger_stop 5、fail_closed 10)。消融單元測試 32 個中 31 過,唯一失敗是我的 archive 沒帶 `CLAUDE.md`,是取材造成的缺檔,不是回歸。偏離點就是 PLT6-01 到 PLT6-03。
3. **新發現的同一案例修前與修後**:
   - PLT6-01:修前不卡且產生普通檔,修後永久卡住。
   - PLT6-02:修前與修後都在批次結尾才失敗。
   - PLT6-03:修前沒有這個測試,修後 root 下紅。

## 未驗範圍
- Linux、CI runner、容器、root 的實際執行。
- Windows。
- 全套測試,不准跑。
- `os.access` 在 setuid、ACL、唯讀檔系統下的實際差異。

實驗目錄 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/平台終端6-sonnet/` 已刪除。

總結:最高嚴重度 minor
