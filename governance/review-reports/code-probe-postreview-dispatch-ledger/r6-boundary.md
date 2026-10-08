severity: minor

我只用 `_output_target_problem`、`_atomic_write_bytes`、`main()` 做了實驗,另跑了 `-k probe_boundary_fifth`(16 個全過)。實驗目錄已清掉。ruff 只開 F 規則時兩支檔都乾淨,本次 hunk 沒有 F821。我沒有開全規則比對,因為全規則會報一堆 BLE001,跟這次改動無關。

## Finding BND6-01
severity: minor
blocking: 否
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/scenario_probe.py:64`
- 具體輸入:`--out` 是沒人在讀的具名管線(FIFO)。
- 走到哪一段:`_output_target_problem` 對 FIFO 直接回 None,開跑前放行。批次跑完後 `_atomic_write_bytes` 走 `O_WRONLY` 的 `os.open`。
- 壞在哪:沒有讀端時 `open` 會永遠卡住。模型額度已經花完,結果檔也沒寫出來,程序不會結束。
- 重現:建 `mkfifo f`,`alarm(3)` 後呼叫 `_atomic_write_text(f, "x")`。修後 3 秒仍卡住(rc=142);修前直接寫成功(rc=0)。
- 補充:docstring 的「照舊直接寫入」對 FIFO 不成立。修前 FIFO 是被暫存檔取代成普通檔,從來沒有直接寫。`/dev/null` 這類字元裝置不受影響。
- 歸因:有證據的修復回歸。修前修後兩版都跑過,行為不同。

## Finding BND6-02
severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」
file: `scripts/scenario_probe.py:44`
- 具體輸入一:`--history` 指到唯讀目錄下尚不存在的檔(`ro/h.jsonl`,目錄 0555)。
  - 走到哪一段:`replace=False` 時不檢查父目錄權限,開跑前放行。
  - 壞在哪:`os.open(O_CREAT)` 在批次結束後拋 PermissionError,模型已經叫過 1 次。
- 具體輸入二:`--history` 是 unix socket,或檔名超過 255 bytes。
  - 走到哪一段:同樣開跑前放行。
  - 壞在哪:批次結束後才拋 ENXIO(Errno 102,Operation not supported on socket)或 ENAMETOOLONG,模型已叫過 1 次。
  - 重現:對 main 用 mock 的 `run_one`,修前修後都是「model calls 1」。
- 具體輸入三:`--out` 檔名 300 個 a,或父路徑是普通檔(`file/o.json`)。
  - 走到哪一段:`path.lstat()` 對 NotADirectoryError 與 ENAMETOOLONG 沒接,開跑前直接拋 traceback(rc 1)而不是訊息加 rc 2。
  - 重現:修後兩者都是「model calls 0」且帶 traceback;修前是 1。
  - 為什麼只算半修:這兩種有擋在模型之前,但不是 rc 2 訊息,跟測試宣稱的「擋下」不一致。
- 歸因:有證據的原有漏查。修前修後都能重現,不是這次修補引入的。

## 固定席逐條判定
- lumos-cli-lifecycle:★INVARIANT★ 講的是 re-inject 的 sentinel 外內容保留。這份 diff 沒碰 `scripts/lumos`,寫入路徑與它無關,不影響。
- codex-harness、design-loop、guard-kill、bound-tests-gate、測試假綠形態、lumos-cli-read、授權與歸屬:
  - 牽連只是因為探針、消融腳本與 `test_lumos.py` 被列入,合約內容(guard kill 的 rc 順序、search 的過濾、LICENSE 白名單等)沒被碰到。
  - 測試假綠形態要求「前置斷言證明現場成立」。新增的 `t_confirm_tty_no_ctty_session_survives` 與 edges 測試都有前置斷言,符合。
  - 授權與歸屬的 SPDX 檔頭規則:我沒有逐檔核對這次改動的檔頭,視為未驗。

## 修補三問
1. **原問題修復效果**:
   - 我獨立核對了新檔照 umask(0644)、唯讀檔 PermissionError、250 字元檔名、`/dev/null` 直接寫、輸出連結不改寫受害檔、歷史連結被擋這幾項,都有行為證據。
   - 消融報表 `text()` 逐值核對過。裸網址、email、`www.` 的 `:`、`@`、`.` 都加了反斜線。真 ESC 顯示為 `\\x1b`,字面 `\x1b` 顯示為 `\\\\x1b`,兩者不同。
   - NBSP 與 U+2007 變成空白,`\u200d`、U+FEFF、孤立 surrogate 與 U+2028 都轉成可見碼點。`None` 與數字照字串印。
2. **相鄰路徑**:
   - 自己擁有的既有檔沿用權限的路徑測試通過。
   - 傳入 `/dev/stdout`:macOS 上它是符號連結,新增的開跑前檢查會擋成 rc 2。修前是批次後才失敗,屬改善。
   - 空 `--out` 在 `main` 裡被 `target and ...` 略過,不報錯。
   - 新退化只有 BND6-01。
3. **同案例修前修後**:BND6-01 修前成功、修後卡住。BND6-02 的歷史權限、socket、長名三種修前修後都是 model calls 1;`--out` 兩種是修前 1、修後 0 但仍帶 traceback。

## 未驗範圍
- 沒測 block device(需要 root;推論是會被暫存檔取代成普通檔,與修前相同)。
- 沒測 Linux 的 `/proc/self/fd/1`。
- 沒測 umask 在多執行緒下的競態,探針與消融腳本都沒用執行緒。
- 沒測消融腳本在「既有唯讀檔」下的行為。修前會取代,修後改成拋 PermissionError,屬行為差異,未驗它在實際流程是否會出現。
- 沒跑 `TestScenarioProbeAblation`。
- `$x$` 在 GitHub 上會被當數學式渲染,`text()` 沒轉義,只是外觀問題,未列為 finding。
- 沒跑全套測試。

總結:最高嚴重度 minor
