severity: minor

**1. 分層與依賴方向:對齊。**
- 新碼放在 `scripts/lumos` 的 `_replay_write_verdict`,由 `cmd_loop_replay` 的 `--freeze` 分支呼叫。它同層的 `_replay_git_blob`(`scripts/lumos:1107` 附近)是同樣的「前置輔助函式,被同一支指令呼叫」。
- 新函式只碰檔案系統,沒有往上呼叫 `cmd_*`,也沒有跨層直呼。
- `_loop_gov_mark` 寫治理帳這步仍留在呼叫端,順序沒變:先換上位,再留痕。
- 回傳形狀 `(rc, 歸檔檔名)` 跟 `_replay_git_blob` 的 `(blob_id, err)` 同為 tuple。比起修前「int 或 tuple 混用、靠 isinstance 判斷」,現在更像鄰居。
- 測試端 `_replay_fx` 抽成共用準備函式,跟既有的 `_mk_dref_vault` 等 fixture 輔助函式(`scripts/test_lumos.py:38104` 附近)同一個做法。

**2. 命名與錯誤處理:大致對齊,有兩處小差異。**
- 擋下訊息一律用 `擋下:…` 開頭、寫到 stderr、回 rc 2。這跟同函式其他訊息(`scripts/lumos:993`、`:1000`、`:1005`)一致。
- 輔助函式名用 `_replay_` 前綴,暫存檔變數用 `_tmp`、`_refroze`,跟同函式一致。
- 暫存檔的 finally 用 `try: unlink … except OSError: pass`,形狀跟 `_write_lf` 的清理(`scripts/lumos:19269`)一致。
- F1 與 F2 見下。

**3. 第二種做法:大體沒有。**
- 暫存檔名組法是 `.verdict.{os.getpid()}-{uuid4().hex[:8]}.tmp`,跟 `_write_lf` 的 `{name}.{pid}-{uuid4().hex[:8]}.tmp-wlf`(`scripts/lumos:19264`)同一套「行程編號加八碼隨機」,沒有另創。唯一差別是 `_write_lf` 用 `O_EXCL` 獨佔建檔,新碼用 `write_text` 寫入。名字已含隨機碼,不算第二種做法。
- 測試替換手法 `m.os.replace = …` 搭配 try/finally 還原,跟既有的 `rl.os.replace = boom`(`scripts/test_lumos.py:34942`、`:34951`)和 `_os.replace = boom`(`:56915`)同一手法。
- `_inproc` 內的 `setattr(m, k, val)` 搭配還原,跟 `scripts/test_lumos.py:11844`、`:33923` 的 setattr 做法一致。
- 把 `_os_rp` 這個函式內別名改成模組頂層的 `os`(`scripts/lumos:57`),是往專案主流收斂。

### F1 `unlink(missing_ok=True)` 是 scripts/lumos 唯一一處
severity: minor
blocking: 否 — 結構相同(finally 內刪暫存檔、吞 OSError),只是呼叫寫法不同,且功能上等價。
引句:「_tmp.unlink(missing_ok=True)」
佐證行 file: `scripts/lumos:1173`;對照 `_write_lf` 的 `_os.unlink(tmp)` 在 `scripts/lumos:19269`。

### F2 函式內 `import uuid as _uuid` 重複了頂層匯入
severity: minor
blocking: 否 — 局部匯入加底線別名是 `_write_lf` 的既有慣例(`scripts/lumos:19263`),行為無差。
引句:「import uuid as _uuid」
佐證行 file: `scripts/lumos:1167`;頂層已有 `import uuid`(`scripts/lumos:59`),且 `scripts/lumos:9421` 直接用 `uuid.uuid4()`。其他區域匯入慣例是連 `os` 也這樣做(`:9852`、`:22880`)。同一個 diff 把 `_os_rp` 改成頂層 `os`,但 `uuid` 反而新加局部匯入,方向不一致。

總結:不對齊共 2 條,其中 major 0 條
