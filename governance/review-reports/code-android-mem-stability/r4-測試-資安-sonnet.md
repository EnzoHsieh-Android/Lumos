severity: minor

# 資安席報告:r4-pkg-tests.patch(`scripts/test_lumos.py`,測試包)

## Finding 1:孤兒檢查的樣式比不到驅動底下的 `sleep 30`,「沒有孤兒」的斷言比字面弱
severity: minor
blocking: 否

引句:「left = sp.run(["pgrep", "-f", f"{fake}/(driver|sleeper)"], capture_output=True, text=True).stdout.split()」

- 誰:使用者本人或照常操作的 AI。
- 從哪:日後有人改收集腳本的收尾。
- 送什麼:改動讓 `sh sleeper` 被殺了,但它底下的 `sleep 30` 沒被殺。
- 拿到什麼:`sleep 30` 的命令列沒有假工具目錄,`pgrep -f "{fake}/(driver|sleeper)"` 比不到它。「驅動(連同它底下的 sleep)沒有變成孤兒」的斷言因此照樣綠。測試名與斷言文字說的範圍,比實際查得到的範圍大。
- 同類:`_ms_orphans` 用同一種樣式,所以也有同一個缺口,而且收屍時一樣收不到它。紅的時候最多漏留一個存活 30 秒的 `sleep`。
- 嚴重度:缺口只在「整組殺」被改壞之後才有意義,而且 `sleep` 30 秒自己會結束。
- 歸因:未判定。我沒有跑兩版;這是命令列比對的靜態分析。實跑一次 `-k android_memstab_collect` 通過後,`pgrep -fl 'sleep 30'` 為空。
- 修法建議:讓 sleeper 用 `exec sleep 30`,或讓命令列帶 `{fake}`(例如 `sleep 30 {fake}`),樣式才比得到。

## 逐類結論

### ① 提示注入:已看,無
- 測試輸出只回顯測試自己造的假資料。
- 唯一帶「偽造的一行」的輸入是測試自己造的,而且測的就是換行會被換成空白。
- 假日誌裡的 `SECRET123` 與 `alice@example.com` 只寫進暫存目錄。
- 失敗訊息回顯的是 `r.stdout + r.stderr`,內容來自假工具與收集腳本的 stderr,外部可控文字進不來。

### ② 讀寫與執行越界:已看,無洞(三點已逐項查證)
- **`pgrep -f` 加 `kill` 會不會比到別的會談或別支測試的程序**
  - 樣式一律帶 `{fake}`,也就是 `tempfile.TemporaryDirectory(prefix="gctl-ms-")` 底下的 `fake/`,每個測試路徑各自唯一。
  - 別的會談或別支測試的程序命令列不會含這個路徑。
  - 殘餘風險只有「pgrep 到 kill 之間 pid 被重用」,視窗為毫秒級,單人環境可忽略。
  - 實跑後 `pgrep -fl 'gctl-ms-'` 為空。
- **SIGHUP/SIGQUIT 會不會打到測試程序自己或別的程序**
  - 測試只用 `Popen.send_signal` 打 `sh script` 這一個子程序,沒有送整組,也沒有 `kill 0` 或負 pid。
  - 腳本的 `kill_group` 只殺自己用 `start_new_session=True` 開出來的群組,見 `file: scripts/templates/android-stability-collect.sh:47-60`。
  - 日誌串流那個 Popen 沒有自成群組,但只用 `lc.kill()` 殺單一 pid,見 `file: scripts/templates/android-stability-collect.sh:383,397`。
  - 所以不會打到測試執行器的群組。
- **改到使用者的全域設定**
  - `_ms_collect_env` 設了 `GIT_CONFIG_GLOBAL=os.devnull`、`GIT_CONFIG_NOSYSTEM=1`,並把 `XDG_CONFIG_HOME` 指到不存在的 `fake/xdg-empty`。
  - 這樣既不會讀、也不會寫 `~/.gitconfig` 與 `~/.config/git`。
  - `git init` 也用這份環境跑。
  - 殘餘:git 早於 2.32 時會忽略 `GIT_CONFIG_GLOBAL`,`~/.gitconfig` 的 `core.excludesFile` 仍可能讓「產物目錄沒被忽略」那組誤紅。這是誤紅,不是越界寫入。
- **暫存以外寫刪**
  - 刪檔只發生在暫存目錄裡。
  - 「捷徑指到別處不刪」的兩條測試,把外部檔也建在暫存目錄,且斷言它沒被刪。
  - 測試本身沒有 `rm`,只有針對 pid 的 `kill`。

### ③ 非刻意、一步就能繞過的守衛:已看,有一條(Finding 1);另有兩個無關緊要的弱點,不開槍
- **Big5 守衛在沒有 `zh_TW.BIG5` 語系的機器上整段略過**,只印一行說明。
  - 攻擊路徑:使用者或 AI 在 Linux CI 改了收集腳本的 UTF-8 輸出,這條不會紅。
  - 這是檔內明講的、有意的略過;本機有該語系,這次實際跑了,通過。
  - 因此不列為 finding。
- **「時間對齊」的前置條件**
  - 例如 `_ms_wait_for` 逾時後的回傳值被丟掉,接著 `sleep(0.5)` 再送信號。
  - 實際上後面還有 `check("前置:... p.poll() is None")` 與 `kill -TERM 4321 in log` 的斷言把關。
  - 前置沒成立時最終斷言會紅,不會假綠,所以只是脆弱,不是繞過。

## 實跑證據
- 命令:`cd /Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability && PYTHONDONTWRITEBYTECODE=1 python3.14 scripts/test_lumos.py -k android_memstab_collect`
- 結果:107 passed, 0 failed,約 2 分 03 秒。
- 跑完後 `pgrep -fl 'gctl-ms-'` 與 `pgrep -fl 'sleep 30'` 皆無輸出(rc=1)。
- 工作樹 `git status` 只有既有的 `docs/.governance-log.jsonl` 與審查卷證檔,測試沒有新增改動。
- 這次沒有碰 adb 與實體裝置。

## 修補鏡頭三問(僅限本席範圍)
1. **原問題修復效果**:SIGHUP、SIGQUIT、收尾中再收 SIGTERM、孤兒收尾、Big5 這些測試,修後版本實跑通過。我沒有跑修前版本,所以「修前會紅」未判定。
2. **正常、錯誤與相鄰路徑**:修後版本的 `collect_*` 全組(107 項)通過。
3. **新發現的同一案例兩版結果**:Finding 1 只做了靜態分析,兩版都沒跑,歸因未判定。

## 圖譜鏡頭與殘留合約
- 圖譜鏡頭:固定席節點全是 `scripts/lumos` 或 `scripts/test_lumos.py` 的家。本包只新增測試,沒動 `scripts/lumos`,所以不影響 `lumos-cli-read` 等合約。`測試假綠形態` 的 ★INVARIANT★(還原翻紅釘須配前置斷言)這份測試有照做(多處「前置:」斷言)。
- 殘留合約:派工詞說殘留算不出來。這一包是測試檔,沒有殘留問答可對,未判定。

最嚴重 severity:minor,blocking 共 0 條。
