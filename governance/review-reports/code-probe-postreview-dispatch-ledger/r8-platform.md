severity: minor

## Finding PLT8-01
severity: minor
blocking: 否
引句:「check("沒有控制終端時 --out /dev/tty 開跑前就擋下", "PRE_TTY True" in out, out)」
file: `scripts/test_lumos.py:43610`
- 輸入:以 root 身分、`/dev/tty` 這個節點不存在的環境(最小化容器或 chroot)跑 `t_probe_boundary_char_device_session`。
- 走到哪一段:子程序呼叫 `_output_target_problem('/dev/tty')`。`lstat` 回 FileNotFoundError,`st` 為 None,不進字元裝置的試開分支。接著 `/dev` 對 root 可寫,函式回傳 None。
- 壞在哪:測試期望「擋下」,實際沒擋,於是假紅。非 root 時 `/dev` 不可寫,函式回傳「不可寫」,測試因為錯的原因綠。兩種情況都沒有真的驗到「試開字元裝置失敗」。
- 重現:我是非 root,用「父目錄可寫、節點不存在」的路徑模擬 root 加缺節點。修前 67b1dea2 與修後 e5ce8675 都回 `None`(輸出 `missing-node problem: None`)。實機 Docker 與 Linux 沒驗。
- 補充:Docker 和 podman 預設都會建 `/dev/tty`,所以只有極簡 sandbox 會碰到。
- 歸因:有證據的原有漏查。`_output_target_problem` 對不存在節點放行是修前就有的行為,新測試的前提沒把它排除。

## Finding PLT8-02
severity: minor
blocking: 否
引句:「check("終端讀得慢時大量輸出照樣寫完", pty_err is None and len(got) >= 300_000, (pty_err, len(got)))」
file: `scripts/test_lumos.py:43471`
- 問題:這條還原翻紅釘沒有前置斷言,證明「沒改回阻塞時,這個 pty 寫入真的會丟 BlockingIOError」。固定席 `測試假綠形態` 的 ★INVARIANT★ 要求每個釘子都配這種前置斷言。
- 現況:斷言只量「寫完且收到 300KB」。能不能翻紅,完全靠 pty 緩衝小於 300KB 且讀端比寫端慢,這是環境假設,沒有被斷言出來。
- 已驗(macOS):把 `os.set_blocking(fd, True)` 換成 `pass`,`t_probe_boundary_fifth_round_output_edges` 變成 36 passed、1 failed,所以 macOS 上不是假綠。
- 未驗:Linux(ubuntu-latest)的 pty 緩衝大小與 EAGAIN 行為。⚠ 這裡可能假綠,我沒辦法在本機證實。
- 副作用:若寫端失敗,讀端執行緒還卡在阻塞的 `os.read`。`reader.join(20)` 會讓紅的那一輪多等 20 秒。它是 daemon 執行緒,不會拖住執行器,我實測紅燈總共 24 秒。
- 歸因:未判定。這是 r7 新增的測試,修前沒有對照。

## 固定席逐條判定
- `codex-harness.md`、`ablation-lumos-first.md` 的敘述與 e5ce8675 程式一致:
  - 試開 char device、三處共用開檔函式、tmp 以 keep_mode 建立、迴圈上限 100,都對得上。
  - `visible` 的類別集合與主程式的 `_PATH_SPECIAL_CATS` 完全相同,格式都是 `\uXXXX`。
  - 兩邊對 U+E0001 都寫成 5 位的 `\ue0001`,有歧義但兩邊相同,與敘述一致。
- 「字面 `\u001b` 與真 ESC 呈現相同」是 r5 當時修掉的碰撞,r7 改用主程式寫法後又回來,筆記已把它列為 `[代價:]`。我視為已記錄的取捨,不列 finding。
- `測試假綠形態` ★INVARIANT★:除 PLT8-02 外,其餘新測試都有「現場成立」前置斷言(`SCENE leader=True ctty=False`、tmp 建立數、nlink==2、FIFO 種類)。
- `lumos-cli-lifecycle.md` 的 ★INVARIANT★ 沒被碰到:`t_reinject_preserves_outside` 不受影響。新增的 `t_confirm_tty_no_ctty_session_survives` 存在(`scripts/test_lumos.py:10255`)。「下方 PITFALL」指的條目在同檔 156 行,存在。
- 其餘固定席(`autonomous-iteration-loop`、`lumos-cli-read`、`design-loop`、`bound-tests-gate`、`canary-audit`)沒有被審材動到合約。
- 表態記錄(py-eventloop na):整份 diff 沒有 `async def`,宣稱成立。

## 修補三問
**repair 與 preserve 分開報**
- G-ESC repair:`t_probe_boundary_fourth_round_report_and_provenance` 26 passed。preserve:自動連結、HTML 與反斜線只轉一次的斷言仍綠。
- G-CHR repair:`t_probe_boundary_char_device_session` 4 passed,1.1 秒。
  - 拿掉 `_NOCTTY` 後,子程序輸出 `AFTER_WRITE ctty=True`,rc -1(被 SIGHUP),測試翻紅。
  - 拿掉 `set_blocking` 後,測試翻紅。
  - preserve:/dev/null 照寫、FIFO 換成普通檔,`fifth_round_output` 39 passed。
- G-TMPMODE repair:修前 67b1dea2 沿用 0600 時,tmp 建立權限是 `0o644`。修後是 `0o600`,命令見下。preserve:新檔照 umask、自己擁有的 0640 保留,測試綠。
- G-HIST repair:歷史檔是硬連結時,修前 `_output_target_problem(h, replace=False)` 回 None,修後回「有多個名字」。FIFO 有讀者、無讀者、硬連結三種跑中替換,測試綠。
- G-TESTALARM repair:`_guard_hang` 借 SIGALRM 後還回執行器原本的逾時。我讀了程式,並跑了 `借鬧鐘抓卡住之後,測試執行器原本的逾時還在` 那條斷言,綠。

**修補處的正常、錯誤與相鄰路徑**
- `/dev/tty` 在互動 shell(pty.fork 造出控制終端)裡:
  - 試開加寫入前後,`termios` 完全相同。
  - 輸出只有 `HELLO`,沒有額外的可見副作用。
  - 歷史檔路徑 `_open_history('/dev/tty')` 加 `fdopen(..,"a")` 也能寫進去。
- 共用 open file description:
  - macOS 的 `/dev/fd/0` 是 char device,開它會 dup 同一個 description。
  - 我先把 fd0 設成 O_NONBLOCK,再呼叫 `_output_target_problem('/dev/fd/0')`,之後 fd0 的 O_NONBLOCK 被清掉。
  - 修前的寫入路徑也有 `set_blocking(True)`,效果相同,只是現在提早到開跑前檢查。
  - 沒有找到會壞事的具體場景,所以不列 finding。
  - Linux 的 `/dev/fd/N` 是符號連結,走取代分支,不受影響。
- 暫存檔迴圈、`os.close` 的錯誤路徑和 `BaseException` 清理,我逐行讀過,沒有發現洞。

**新發現同一案例,修前與修後**
- PLT8-01:修前 67b1dea2 與修後 e5ce8675 都回 `None`,同一個結果。

重現命令(兩版 scenario_probe 並排比較,實驗檔已刪):

```
python3.14 e3.py
```

輸出:
```
before missing-node problem: None | hist hardlink: None
after missing-node problem: None | hist hardlink: …/h-after 有多個名字(硬連結),追加會寫進別的名字指向的內容
before tmp mode at create: ['0o644']
after tmp mode at create: ['0o600']
```

## 未驗範圍
- 沒驗:Linux、GitHub Actions ubuntu-latest、macOS runner、root 與容器,以及真的沒有 `/dev/tty` 節點的環境。
- 沒驗:Linux 的 pty 緩衝大小與 EAGAIN 行為,所以 PLT8-02 的假綠風險沒有被證實。
- 沒驗:序列埠這類開了會有硬體副作用的字元裝置。開跑前多一次開關,理論上多一次 DTR 切換,但我沒有裝置可測。
- 沒驗:Windows(本輪排除)。
- 已驗(本機 macOS 加 Python 3.14,在我自己的解出副本裡跑):
  - 三組測試子集通過,沒有拖住執行器:`char_device_session` 1.1 秒、`fifth_round_output_edges` 約 6.6 秒、`fourth_round_report` 約 3 秒。
  - 兩個還原翻紅(拿掉 `_NOCTTY`、拿掉 `set_blocking`)都確實翻紅。

總結:最高嚴重度 minor
