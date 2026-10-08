severity: minor

整體判斷:O_NOCTTY 這個修法在本機(macOS)是對症的。產品部分沒有 blocker 或 major,下面三條 minor,其中兩條是修補自己引入的行為變化。

## Finding PLT5-01
severity: minor
blocking: 否
引句:「mode = stat.S_IMODE(old.st_mode) & 0o666」
file: `scripts/scenario_probe.py:20-44`(`_atomic_write_text`,以 after 取出樹為準)
- 輸入:`--out` 指向不存在的路徑,umask 0022。
- 走到哪:`lstat` 拋 FileNotFoundError,`mode` 維持 None,不會呼叫 fchmod。`NamedTemporaryFile` 以 mkstemp 建檔,權限是 0600,之後 `os.replace` 把它換成輸出檔。
- 壞在哪:新建輸出檔從修前的依 umask 的 0644 變成 0600。另外,既有的唯讀(0444)檔原本寫入會 PermissionError,現在被默默換掉,權限仍是 0444。
- 重現(`aw.py` 在 `/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/平台終端5-sonnet/`):
  - `python3.14 aw.py .../before` 輸出 `new file mode 0o644`、`ro err PermissionError`。
  - `python3.14 aw.py .../after` 輸出 `new file mode 0o600`、`ro overwritten ok 0o444`。
- 限制:這個程式庫裡沒有其他使用者讀 `--out` 的證據,影響只在「別的帳號或群組要讀結果檔」時才有。
- 歸因:有證據的修復回歸(兩版行為不同)。

## Finding PLT5-02
severity: minor
blocking: 否
引句:「_atomic_write_text(Path(a.out), json.dumps({"results": results, "passed": p, "total": n,」
file: `scripts/scenario_probe.py:1284-1295`(寫輸出的呼叫)
- 輸入:`--out /dev/stdout` 或 `--out /dev/null` 這類特殊檔。
- 走到哪:`NamedTemporaryFile(dir=path.parent)` 要在 `/dev` 建暫存檔,非 root 會失敗。
- 壞在哪:整批探針跑完才拋例外,位置在輸出寫入。其後的 `--history` append 也因此被跳過,整批結果丟失。
- 重現:
  - after:`_atomic_write_text(Path('/dev/stdout'),'{}')` 得到 `PermissionError: [Errno 1] Operation not permitted: '/dev/stdout.kjwfn6y0'`。
  - before:`Path('/dev/stdout').write_text('{}\n')` 成功。
- 限制:程式庫裡沒有人這樣用 `--out`,是邊角。
- 歸因:有證據的修復回歸。

## Finding PLT5-03
severity: minor
blocking: 否
引句:「fd = os.open(tty_path, os.O_RDWR | getattr(os, "O_NOCTTY", 0))」
file: `scripts/test_lumos.py:9591-9647`(`t_confirm_tty_unit`)
- 問題:這支「還原翻紅」的測試沒有前置斷言證明現場成立,違反固定席 `測試假綠形態` 的 INVARIANT。
- 實測:
  - 拿掉 O_NOCTTY 的變體 `mut/`,在 `start_new_session` 的執行器下:`rc -1 SIGHUP`,會翻紅。
  - 同一個變體在 `pty.fork` 給控制終端的環境下:exit 0,`6 passed, 0 failed`。
- 結論:在開發者終端機裡,這支測試對「拿掉修法」完全不會紅。要靠 CI 或沒有控制終端的執行器,而且紅的方式是整個執行器被殺,不是斷言失敗。
- 歸因:有證據的原有漏查。這支測試的結構在修前已存在,修補沒有補前置條件。

## 平台鏡頭已驗主張
- **O_NOCTTY 對症(macOS,Darwin 25.5 arm64):** `exp.py` 讓 `setsid` 後的子程序 open pty slave。
  - 不帶旗標:`darwin plain ctty: b'yes' status: SIGHUP`。
  - 帶 O_NOCTTY:`darwin noctty ctty: b'no survived' status: 0`。
  - 所以「BSD 系不會因 open 取得控制終端」的推測不成立。Darwin 會取得,rc129 的成因與作者定位一致。
- **翻紅現場是真的:**
  - 修前 `t_confirm_tty_unit`:`rc -1 SIGHUP`。
  - 修後:`6 passed`,rc 0。
  - 拿掉旗標的變體:SIGHUP。
- **使用者情境不變:** 用 `inter.py` 在有控制終端、stdin=/dev/null 的 `pty.fork` 下,修前和修後的輸出完全相同。
  - 答 y:`RESULT True`。
  - 逾時:`(無回應,視為略過)` 加 `RESULT None`。
  - Ctrl-C:`KBINT`。
  - 補充:stdin 是 tty 時走 `input()`,根本不經過這段。
- **getattr 退回:** 沒有 O_NOCTTY 的平台得到 `O_RDWR | 0`,與修前旗標一致。
- **其他 tty 開啟點:** `scripts` 底下只有 `scripts/lumos:18873` 一處開 `/dev/tty`,沒有漏網。
- **os.replace:** 暫存檔與目標同目錄,macOS/Linux 上是原子重新命名。`fchmod` 與 `fsync` 在 POSIX 可用。macOS 的 `fsync` 不保證刷到磁碟快取,但不影響這裡的原子性。
- **等待迴圈:** 迴圈有 `waited < a.wait_on_limit` 守衛,`delay = min(300, ...)` 一律為正數。
- **render_md:** 控制字元與 Markdown 標記的跳脫成立。

## 固定席逐條判定
- **`lumos-cli-lifecycle` INVARIANT(re-inject 只覆蓋 sentinel 內):** 不影響。diff 在 `scripts/lumos` 只動 `_confirm_tty` 的 open 旗標,不碰 re-inject 與 CLAUDE.md 寫入。
- **`lumos-cli-read`(search 排除 superseded):** 不影響,沒碰 search 路徑。
- **`design-loop`(處置閘第五步):** 不影響,沒碰處置閘。
- **`測試假綠形態`(還原翻紅釘要配前置斷言):** 新增的 `t_probe_boundary_fifth_round_output_contracts` 等是新測試。`t_confirm_tty_unit` 是既有測試,被宣稱當作 NOCTTY 的翻紅釘,但沒有前置斷言,見 PLT5-03。
- **`bound-tests-gate`、`guard-kill`、`授權與歸屬`:** 不影響。這些合約綁的測試與檔案集合沒被改動,`scripts/lumos` 檔頭授權區塊未變。
- **`codex-harness`:** 沒有證據顯示被破壞。

## 修補三問
1. **原問題修復效果:** 有行為證據,見上面的 SIGHUP 與非 SIGHUP 對照。限制是全套 rc129 沒有在修後重跑確認,我也不准跑全套。審材自己承認 rc129 原因「未判定」,這裡只證明單測的 SIGHUP 路徑已修。
2. **修補處的相鄰路徑:**
   - tty 確認路徑:正常、逾時、Ctrl-C 都不變。
   - 輸出寫入路徑:新建檔權限與特殊檔目標不同,見 PLT5-01 與 PLT5-02。
3. **同一案例修前修後:** 新建 `--out` 檔,修前 0644,修後 0600。`--out /dev/stdout`,修前成功,修後 PermissionError。兩版命令與輸出都在上面。

## 未驗範圍
- Linux 實機沒有跑。
- Windows 沒有驗,依指示也不擴及。
- 全套測試沒有跑,依規定另有背景執行。
- `t_probe_boundary_*` 與 `TestScenarioProbeAblation` 沒有逐一重跑。
- 圖譜筆記只看了驗證紀錄文字,沒有跑 lint。
- render_md 對裸 URL 自動連結的處理沒有審。

severity: minor
