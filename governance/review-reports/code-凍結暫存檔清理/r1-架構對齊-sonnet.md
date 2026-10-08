severity: minor

**問 1 分層與依賴方向:對齊。**
- 新函式 `_replay_write_verdict` 放在 `_replay_git_blob` 之前,跟其他 `_replay_*` 輔助函式同層(`scripts/lumos:1000` 附近的 `_replay_git_blob`)。
- 只有 `cmd_loop_replay` 呼叫它,它只用 `json`、`Path` 與標準庫,沒有跨層直呼。
- 呼叫端 `try/finally` 清暫存檔,跟 `scripts/lumos:47428` 的 `try: os.replace … finally: os.unlink` 同形。
- 測試端 `_replay_fx` 是抽出共用準備的 `_xxx_repo()` 做法(`scripts/test_lumos.py:11060` 的 `_mk_anchor_repo`、`:20486` 的 `_mk_cochange_repo`)。
- 替身測試用 `_load_lumos_inproc()` 換掉函式(`scripts/test_lumos.py:1849`、`:2130` 同用法)。

**問 2 命名與錯誤處理:大體對齊,有兩處偏離。**
- 擋下時印一句到 stderr、回 `2`,跟同函式其他擋下路徑一致。
- 命名用 `_replay_` 前綴,跟鄰居一致。
- 時間戳改成 `now().astimezone()`,跟 `scripts/lumos:1141`、`:1306`、`:1615` 一致。
- 偏離一:`_replay_write_verdict` 失敗回 `int`、成功回 `(refroze,)` 這種 tuple,呼叫端靠 `isinstance(rc_w, int)` 分辨。鄰居 `_replay_git_blob` 回的是固定形狀 `(值, err)`。
- 偏離二:`import os as _os_rp` 搬進新函式,但 `scripts/lumos:57` 已有頂層 `import os`,多餘。這是原樣搬過來,不算新做法。

**問 3 第二種做法:沒有新增,只有一個舊做法被保留下來。**
- 暫存檔清理走 `try/finally` + `unlink`,專案裡已有同樣寫法(`scripts/lumos:21360`、`:47428`)。
- 暫存檔沿用固定名 `.verdict.tmp`,是舊有行為,不是這份 diff 新造的。專案另有兩種做法:帶 pid 加隨機字串(`scripts/lumos:19257`)和 mkstemp(`scripts/lumos:47423`)。`scripts/lumos:47421` 的註解還寫明固定名併發會互搶。
- 這份 diff 的新交互:現在無論成功失敗,finally 都會 `unlink(".verdict.tmp")`。若兩個重凍同時跑,一方可能刪掉另一方的暫存檔。重凍擋下訊息本來就提到「同秒有另一個重凍在跑」,這個情境是已知的。
- 專案已有 `_write_lf` 等共用原子寫入,但它們各自針對不同需求,沒有一個能直接套到「先寫暫存檔、歸檔舊檔、再 replace」這三步。所以抽成專用 helper 不算自創第二套原子寫入。
- `.gitignore` 的 `governance/replay/*/.verdict.tmp` 放在既有 `governance/` 規則區,格式與註解風格一致。

### F1 輔助函式回傳 int 或 tuple 兩種形狀
severity: minor
blocking: 否 — 結構正確,只是回傳形狀與鄰居 `_replay_git_blob` 的固定 tuple 不同。
引句:「→ 失敗回 rc(int,已印原因)/成功回 (歸檔檔名或 None,)。」
佐證行 file: `scripts/lumos:1168`(呼叫端 `isinstance(rc_w, int)`)對照 `scripts/lumos:1018`(`_replay_git_blob` 回固定形狀 `(blob_id, err)`)

### F2 新 helper 內多餘的區域 import os
severity: minor
blocking: 否 — 無功能影響,頂層已有 `os`。
引句:「import os as _os_rp」
佐證行 file: `scripts/lumos:57`(頂層 `import os`)

### F3 固定暫存檔名加上無條件清理,併發時會互刪
severity: minor
blocking: 否 — 舊行為沿用,併發重凍屬已知情境。這裡標 ⚠ 交編排者:是否要改成專案已有的「帶 pid 加隨機」命名。
引句:「_tmp = vdir / ".verdict.tmp"」
佐證行 file: `scripts/lumos:47421`(註解明說固定名會互搶)、`scripts/lumos:19257`(`_write_lf` 的唯一暫存名做法)

總結:不對齊共 3 條,其中 major 0 條
