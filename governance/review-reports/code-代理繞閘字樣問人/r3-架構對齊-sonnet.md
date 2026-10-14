severity: major

我只讀了 patch 和 `scripts/lumos`、鄰居掛鉤的對應段落,沒有載入掛鉤去重現行為。以下三問逐問答,findings 放在第 2、3 問。

## 1. 分層與依賴方向:對齊

- 新掛鉤 `bypass-ask-hook.py` 只往下依賴 `_hookevent`(`guard`、`mark`)。
  - 沒有去呼叫 `scripts/lumos`,`_hookevent` 也沒有反向依賴掛鉤,沒有跨層直呼。
  - 對照 file: `scripts/hooks/claude/impact-hook.py:928` 和 file: `scripts/hooks/claude/dispatch-lens-hook.py:555`,鄰居也是只經 `_guard(...)` 進 `_hookevent`。
  - `_trim` 留在 `_hookevent` 內,沒有搬到掛鉤裡。
- 已知偏離(guard 外預篩、模組頂層載入共用模組、分類邏輯放在掛鉤內)不重報。
- 本輪新增的 `_Redir` 是已記錄的 `_Sep` 無先例做法的同形延伸,不另報。

## 2. 命名與錯誤處理

1. 預算函式出現第二種做法,且還帶不同的預設值。
引句:「return _outer_budget(5.0) * _BUDGET_RATIO - (_tm.monotonic() - _BUDGET_START)」
severity: major
blocking: 是
   - 這支掛鉤逐字複製了 `_inner_budget`,帶 1 秒下限,預設 `default=10.0`。但檔內沒有任何地方呼叫它,只剩定義和 `_remaining_budget` 的 docstring 提到它。
   - 另外新寫 `_remaining_budget`:沒有下限,預設 `_outer_budget(5.0)`,並且讀寫同一個模組全域 `_BUDGET_START`。
   - 鄰居用到預算的地方全走 `_inner_budget(...)`。對照 file: `scripts/hooks/claude/impact-hook.py:810` 的呼叫,以及 file: `scripts/hooks/claude/memory-sweep.py:180`。
   - 結果是同一檔裡有兩套「還剩幾秒」的算法,預設值 5.0 對 10.0 也不一致。複本是為了過「各份一模一樣」的測試才保留,實際上是死碼。
   - 這裡有正當理由:`_git_out` 需要「用完歸零」的語意,1 秒下限會讓預算用完後還跑 git。這個理由我沒有重現,所以標 ⚠。
   - 對齊的做法有兩種:
     - 給 `_inner_budget` 加一個無下限的參數。
     - 或在計劃的偏離清單補一條,承認 `_remaining_budget` 是第二種做法。
   - 此外,`_remaining_budget` 靠 `entry()` 第一行呼叫來起算 `_BUDGET_START`,這個副作用鄰居沒有。
   - 歸因:未判定,我沒有讀修補差異裡這段是否為本輪新增。

2. `_trim` 的權限照抄寫法,跟 `scripts/lumos` 既有的暫存寫入不同。
引句:「mode = _stat.S_IMODE(f.stat().st_mode)」
severity: minor
blocking: 否
   - `_trim` 的做法是 `tempfile.mkstemp`,再 `os.chmod(tmp, S_IMODE(原檔))`,最後 `os.replace`。
   - `_write_lf` 的做法不同:
     - 用 `os.open(..., O_EXCL, 0o666)`,權限受 umask 管。
     - 原檔在就 `shutil.copymode(path, tmp)`。
     - docstring 明寫「不用 mkstemp 再改權限」。
     - 見 file: `scripts/lumos:19474`。
   - `_home_cache_write` 是 mkstemp 加固定 `chmod 0600`,見 file: `scripts/lumos:46067`。所以 mkstemp 加 chmod 在 repo 內有先例,結構是對的。
   - 不一致處是「照原檔權限」本來有 `copymode` 這個既有寫法,`_trim` 另外手刻了一份。
   - 歸因:未判定。

3. `_trim` 的失敗清理只抓 `OSError`,跟既有暫存寫入的清理慣例不同。
引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
severity: minor
blocking: 否
   - 這個函式的清理寫法是 `except OSError: unlink; raise`。
   - `_write_lf` 用 `except BaseException`,`_codeloop_write_dispositions` 用 `finally: unlink`。
   - 見 file: `scripts/lumos:19474` 和 file: `scripts/lumos:48743`。
   - 另外,`_trim` 開頭 `glob("hook-events.*.trim")` 掃一分鐘以上的殘檔,這在 `scripts/lumos` 沒有先例。這個做法有寫在 docstring,結構上沒問題,只是屬於新增的做法。
   - 歸因:未判定。

## 3. 第二種做法

- 上面第 1 條是唯一的第二種做法。
- 其餘的都是已記錄的偏離,或結構對、細節不同的 minor。
- 這個版本我沒有找到自寫的 git 子程序呼叫之外的重複工具。`_git_out` 是帶快取和次數上限的小包裝,鄰居是直接 `subprocess.run(["git","-C",...])`(file: `scripts/hooks/claude/ci-status-hook.py:30`),它的差異屬於預算語意,已併入第 1 條。

## 固定席節點

- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill` 這幾篇的 ★INVARIANT★:本 patch 的程式組沒有碰 search 濾網、re-inject、處置閘、guard kill,不影響。
- `Issues/code-loop守衛main-direct盲區`、`pitfalls-code-loop`、`reversibility-governance-ledger`:牽連的是 `scripts/lumos` 和 `test_lumos.py`,程式組只有 `_hookevent.py` 和新掛鉤,不影響。
- 其餘「只列名」的節點未讀,未判。

不對齊共 3 條,其中 major 1 條。
