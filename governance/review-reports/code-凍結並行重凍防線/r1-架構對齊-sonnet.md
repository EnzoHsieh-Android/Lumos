severity: minor

**問 1:分層與依賴方向——對齊**
- 新函式 `_replay_refreeze_blocked` 放在 `_replay_write_verdict` 前面,屬同一組 `_replay_*` 輔助函式(`scripts/lumos:986`、`scripts/lumos:996`、`scripts/lumos:1033`)。
- 呼叫方向是 `cmd_loop_replay` 呼叫 `_replay_write_verdict`,兩者再呼叫 `_replay_refreeze_blocked`。這是由上往下,沒有跨層直呼。
- 寫入端再判一次是專案既有的做法:`_escape_log_guard`(`scripts/lumos:9266`)和 `scripts/lumos:12017` 的「race 窗」註解都有同樣的前置檢查加寫入端重檢。
- 它們也都用同一種寫法(印訊息、回 rc2),沒有改成丟例外。
- 擋下訊息抽成共用小函式,專案裡已有先例:`_anchor_blocked`(`scripts/lumos:25866`)、`_escape_log_guard`(`scripts/lumos:9259` 附近)。

**問 2:命名與錯誤處理——對齊,只有一處小差異**
- 命名:`_replay_` 前綴加動作,跟鄰居一致。
- 錯誤處理:印到 stderr、開頭寫「擋下:」、回 `(2, None)`。這跟 `_replay_write_verdict` 內既有的「擋下:歸檔目的檔已存在」(`scripts/lumos:1016` 附近)一致。
- 新參數是 `note=None`,放在最後。測試替身 `_fail_after_tmp` 同步補了同樣的簽名。
- 小差異是 `_anchor_blocked` 和 `_escape_log_guard` 只負責「記帳或印訊息」,rc 由呼叫端決定。`_replay_refreeze_blocked` 也是只印訊息、不回 rc,所以結構一致。不一致的是它不回傳值,而 `_escape_log_guard` 回 0 或 2。這屬於 F1 說的那一點。

**問 3:第二種做法——未發現**
- 新測試用 `m._replay_git_blob = _race` 加 `finally` 還原,跟同檔 `t_loop_replay_freeze_leaves_no_tmp` 的 `setattr(m, k, val)` 加 saved 還原是同一種手法(`scripts/test_lumos.py:38271`、`scripts/test_lumos.py:38276`),只是少包了一層 `_inproc`。
- `_replay_git_blob` 當時序鉤子,是用既有的函式替換機制製造「開頭檢查之後、寫入之前」的時間點,沒有引入新機制(沒有執行緒,也沒有 sleep)。
- 把 `vdir` 與 `target` 提前到開頭只組一次,是減少重複,不是新做法。

### F1 新輔助函式只印訊息、沒回傳值,呼叫端各自 return 2
severity: minor
blocking: 否 — 結構正確,兩處呼叫端都 `return 2`;只是跟 `_escape_log_guard` 那種「函式回 rc」的鄰居寫法不同。`_anchor_blocked` 同樣不回 rc,所以專案內兩種都有。
引句:「_replay_refreeze_blocked(target)」
佐證行 file: `scripts/lumos:996`、`scripts/lumos:9259`、`scripts/lumos:25866`

⚠ F1 是否算不一致,交編排者:專案內兩種寫法都有,我傾向不當成缺陷。

總結:不對齊共 1 條,其中 major 0 條
