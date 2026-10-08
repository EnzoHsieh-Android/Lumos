severity: minor

**問 1 分層與依賴方向:對齊。**
- 新增的前置擋下放在 `cmd_loop_replay` 的 `if freeze:` 區塊裡,位置是 `--spec` 檢查之後、`_load_rows()` 之前(`scripts/lumos:1086-1096`)。
- 這跟同函式開頭其他前置擋下的位置和做法一致:路徑字元檢查(`scripts/lumos:1076-1078`)、`--spec` 檢查(`scripts/lumos:1079-1082`)、帳本為空檢查(`scripts/lumos:1100-1102`)。
- 它們都是「先做便宜的判斷、`print(..., file=sys.stderr)` 後 `return 2`」,沒有往下呼叫別層。
- `_replay_write_verdict`(`scripts/lumos:986`)是同檔頂層私有輔助函式,只被 `cmd_loop_replay` 呼叫(`scripts/lumos:1170`)。它的位置和形態跟相鄰的 `_replay_git_blob`(`scripts/lumos:1018`)一樣。
- 它只用 `os`、`json`、`print`,沒有跨到 vault 層或 gov 帳層。治理帳寫入(`_loop_gov_mark`)仍留在呼叫端(`scripts/lumos:1176`)。
- 修補差異把 `import uuid as _uuid` 這行拿掉,改用檔頭已有的 `uuid`(`scripts/lumos:59`)。這比修前更貼近檔內其他用法(`scripts/lumos:9421`、`scripts/lumos:13023`)。

**問 2 命名與錯誤處理:大致對齊,一處小分歧。**
- 擋下訊息都是「擋下:…」開頭走 stderr、回 `return 2`,跟 `scripts/lumos:1077`、`scripts/lumos:1081`、`scripts/lumos:1101` 同款。
- 輔助函式用 `(rc, 值)` 回傳,失敗訊息自己印。這跟 `_replay_git_blob` 回 `(值, err)` 是同一類慣例。
- 暫存檔名 `.verdict.{pid}-{uuid8}.tmp` 對齊 `_write_lf` 的 `{pid}-{uuid8}`(`scripts/lumos:19264`)。
- finally 清理改成 `try: os.unlink(_tmp) except OSError: pass`(`scripts/lumos:1172-1175`),跟 `_write_lf` 的清理寫法一致(`scripts/lumos:19273-19276`)。修補差異把 `Path.unlink(missing_ok=True)` 改掉,是正向對齊。
- 時間戳用 `datetime.datetime.now().astimezone()`(`scripts/lumos:997`),跟同檔 `scripts/lumos:1153`、`scripts/lumos:1622`、`scripts/lumos:9399` 的帶時區寫法一致。
- 測試鄰居:新增斷言 `"GATE PASS" not in r.stdout`,寫法跟其他「某字樣不在 stdout/stderr」的 `check(...)` 一樣,例如 `scripts/test_lumos.py:1119`、`scripts/test_lumos.py:1242`。
- 小分歧見 F1。

**問 3 第二種做法:沒有。**
- 專案裡沒有「讀 golden 取 round」的共用函式。回放模式自己內嵌 `json.loads(Path(golden).read_text(...))`,錯誤是 `except (OSError, ValueError)` 後印「golden 檔讀不了」(`scripts/lumos:1186-1190`)。
- 修前的舊擋下點也是內嵌讀 `target` 取 `.get("round")`,例外集合同樣是 `(OSError, ValueError, AttributeError)`。新的提前檢查只是把這段原樣搬上來,沒有新增讀法。
- 暫存檔唯一命名和 finally 用 `os.unlink` 清理,都是 `_write_lf` 已有的做法。
- `.gitignore` 新增 `governance/replay/*/.verdict*.tmp`,是在既有忽略段落旁加一條,不是新機制。
- 我沒看到第二種做法或跨層直呼。

### F1 verdict.json 路徑在同函式內組了兩次
severity: minor
blocking: 否 — 結構對、行為相同。只是提前檢查用 `_cur_v = root / "governance" / "replay" / loop_id / "verdict.json"` 單獨組一次,後面 `vdir`/`target` 又組一次(`scripts/lumos:1160-1162`)。同函式其他「先算路徑再用」的地方通常只組一次。
引句:「_cur_v = root / "governance" / "replay" / loop_id / "verdict.json"」
佐證行 file: `scripts/lumos:1086`(對照 `scripts/lumos:1160`、`scripts/lumos:1162`)

總結:不對齊共 1 條,其中 major 0 條
