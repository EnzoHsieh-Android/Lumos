severity: minor

## Finding CON5-01
severity: minor
blocking: 否
引句:「with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,」
file: `scripts/scenario_probe.py:36-41`(修後 4d765d5c 的 `_atomic_write_text`)

- 輸入:`--out` 指到一個還不存在的新路徑,或指到符號連結(連結被換成普通檔時也一樣)。
- 走到哪一段:`_atomic_write_text` 只有在目標原本是普通檔時才取 `mode`。其他情況不呼叫 `fchmod`,暫存檔維持 `NamedTemporaryFile` 的 0600,`os.replace` 後最終檔也是 0600。
- 壞在哪:舊寫法 `write_text` 遵守 umask,新檔是 0644。現在新建的結果檔只有擁有者讀得到。同一份結果在第二次寫入同一路徑時又保留原權限,所以行為不一致,也沒有測試涵蓋權限。
  - 在這個 repo 內,結果檔由同一使用者的 `ablation_lumos_first.py` 讀取,沒有發現其他讀者受影響。
  - 只有跨使用者讀取才會壞,例如 sudo/容器產出後由 CI 帳號讀取。我沒有證據這種用法存在,所以停在 minor。
- 重現(umask 022,各跑一次 `python3.14 t.py <before|after>`,對新檔寫入後印出權限):
  - 修前:`new file mode 0o644`
  - 修後:`new file mode 0o600`
  - 目標原為 0664 的既有檔,兩版都保持 `0o664`。
- 歸因:有證據的修復回歸。修前的 `write_text` 是 0644,修後是 0600,命令與輸出如上。

## Finding CON5-02
severity: minor
blocking: 否
引句:「os.replace(tmp_path, path)」
file: `scripts/scenario_probe.py:30-47`;呼叫點在 `scripts/scenario_probe.py:1316` 附近(`if a.out:`)

- 輸入:`--out /dev/null` 或 `--out /dev/stdout`。前者是丟棄結果的常見用法,後者是想把結果導到標準輸出。
- 走到哪一段:一輪探針全部跑完之後才進入 `_atomic_write_text`。它要在 `/dev` 建暫存檔,非 root 會拋 `PermissionError`。
- 壞在哪:結果檔沒寫出,例外往上傳,不是 rc 0/1/3。這是整輪跑完後才炸,耗掉的模型額度白費。
- 重現(同一支 `t2.py`,分別對修前與修後取出的 `scenario_probe.py` 呼叫寫入):
  - 修前:`/dev/null ok`、`/dev/stdout ok`
  - 修後:`/dev/null PermissionError [Errno 1] Operation not permitted: '/dev/null._wu4iybo'`;`/dev/stdout` 同樣是 PermissionError
- 補充:若以 root 執行,`os.replace` 會把 `/dev/null` 換成普通檔。我沒有跑 root,這句不算已驗證。
- 歸因:有證據的修復回歸。兩版對照如上,但屬非常規用法,所以標 minor。

## 固定席逐條判定
- **codex-harness**:不影響。`_atomic_write_text` 沒有改變 JSON 內容與欄位。`ablation_lumos_first.py` 的 `candidate`(`.candidate`)經 `os.replace` 轉成 `out`(第 329 行),暫存檔名是 `X.candidate.<隨機>`,不符合 `*.json`、`*.pending`、`*.candidate` 這幾個 glob(第 161、170、193、194 行),不會被誤收。
  - SIGKILL 時暫存檔會殘留,`recovery_paths` 不會清它,只是垃圾檔。若要保證不留垃圾,清理要另寫;目前沒看到會造成錯誤行為。
- **lumos-cli-lifecycle ★INVARIANT★**:不影響。該合約只涉及 re-inject 的 sentinel 外內容 byte-equal,與 `_confirm_tty` 無關。`O_NOCTTY` 只改開 tty 的旗標,fd 在 `finally` 的 `os.close(fd)` 一律關閉。`getattr(os,"O_NOCTTY",0)` 在缺該旗標的平台退回原行為。`t_confirm_tty_unit` 6 項通過,`t_reinject_preserves_outside` 我沒跑。
- **lumos-cli-read、design-loop、測試假綠形態、bound-tests-gate、guard-kill、授權與歸屬**:不影響。沒有改到 search 濾網、處置閘、`guard kill` 或授權檔白名單。
  - 新增的測試檢查先用 claim 把持久帳最後一格花掉,再讓 `run_one` 回傳上限,最後斷言 `sleep` 為 0。這符合「前置斷言證明現場成立」。我沒有做還原翻紅的變異實驗。
- 其餘「超出上限只列名」的節點:未逐篇讀,未判定。

## 修補三問
1. **原問題的修復效果有何行為證據**
   - 符號連結(G-OUT-SYMLINK):`t_probe_boundary_fifth_round_output_contracts` 在修後通過(`-k t_probe_boundary_fifth`:2 passed)。`os.replace` 只替換連結本身,這是 POSIX 語意。我沒有在修前跑該測試。
   - 等待上限(G-WAIT-CAP):進入條件是 `waited < a.wait_on_limit`,`wait_on_limit` 的型別是 `int`。所以 `delay = min(300, 剩餘)` 恆為正整數,不會有 0 或負值造成的無限 `continue`,總等待不超過上限。這是讀碼推得,沒有跑修前。
   - 另外兩組(G-MD-LITERAL、G-TTY-NOCTTY):`t_confirm_tty_unit` 通過;報表那一組(`t_probe_boundary_fourth_round_report_and_provenance`)我沒有跑,未判定。
2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 正常路徑:既有普通檔保留權限,同目錄不同檔與同 `--out` 的兩程序併發都不會互相覆蓋暫存檔,最終檔不會是半檔,比修前改善。
   - 錯誤路徑:各步驟拋例外時 `finally` 清掉暫存檔。成功 `replace` 後 `unlink(missing_ok=True)` 打到的是已不存在的檔名,隨機名不會刪到別人的檔。
   - 相鄰路徑:新檔權限(CON5-01)和特殊檔路徑(CON5-02)有回歸。
   - 其他:沒有 `fsync` 目錄,斷電後可能回到舊檔,對結果檔可再產生,不報。`NamedTemporaryFile` 的 `with` 先於 `os.replace` 關閉檔案,順序正確。
3. **新發現同一案例在修前與修後的結果**:CON5-01 修前 0644、修後 0600;CON5-02 修前 ok、修後 PermissionError。兩條都已雙版實測。

## 未驗範圍
- 沒有跑全套測試,也沒有跑報表跳脫那一組(G-MD-LITERAL)的測試。
- 沒有以 root 執行,沒有模擬 SIGKILL 或斷電。
- 沒有逐篇讀「超出上限只列名」的圖譜節點。
- `ruff check` 對整個檔案報了 26 項,多是既有程式碼的規則(如 BLE001、S112、FURB167)。我沒有逐項對到本次 hunk,不能保證本次新增行零告警。
- 等待 `≥300` 時的正常分段等待,以及既有普通檔權限保留,都沒有獨立測試案例。後者我用手寫腳本驗了。

max severity: minor
