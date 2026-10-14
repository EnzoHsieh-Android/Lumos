severity: minor

severity: minor
blocking: 否 — 跟既有寫法同一種(同一個程序內呼叫 cmd_loop_status、唯讀、輸出收進緩衝),沒有引入新做法,只是同一段呼叫樣板多了第二份。
引句:「rc = cmd_loop_status(env, std_id, spec=str(env.vault / prel), disposal=True, readonly=True)」
對照:既有寫法 scripts/lumos: `scripts/lumos:16190`(cmd_loop_next 用 contextlib.redirect_stdout/stderr 收進 StringIO,再呼叫 `cmd_loop_status(env, loop_id, spec=spec, repo=repo, disposal=True, readonly=True)`,rc==2 才把緩衝寫到 stderr)
判定理由:
- 專案裡沒有一支獨立、可呼叫的處置閘判定函式。處置閘的邏輯就在 `cmd_loop_status` 的 disposal 分支裡(`scripts/lumos:13397`),`loop next` 早就用同一個辦法代問。`_nogo_std_gate` 的做法因此不算跨層直呼。
- 也沒有第二套自寫判法。注釋說明「不另寫判法」,內容屬實。傳入的參數(`disposal=True, readonly=True`)和 `loop next` 完全一致。
- 一點小分歧:`_nogo_std_gate` 另外捕捉 `(OSError, ValueError)`,並從輸出裡找 `DISPOSAL GATE FAIL` 那行當原因;`loop next` 沒有這兩件事。
- 日後想收斂可抽一支「靜默跑處置閘回 (rc, 輸出)」的 helper,兩處共用。現在不抽不算違規。

severity: minor
blocking: 否 — 新核心只供兩個呼叫端共用,另有約十處整本讀帳的舊寫法沒動,屬於原本就存在的分歧。
引句:「def _canary_ledger_rows(path, errors="strict"):」
對照:既有寫法 scripts/lumos: `scripts/lumos:13763`(新核心);`scripts/lumos:12313`、`scripts/lumos:12358`、`scripts/lumos:12518`(其他讀帳函式仍是 `_ledger_lines(path.read_text(...))`)
判定理由:
- 三支分工清楚。`_canary_ledger_rows` 只負責串流逐行解析。`_canary_ledger_scan` 是審查輪那一族,濾掉 spec-gate 留痕並處理 bad 輪次與 decode 例外。`_spec_gate_ledger_index`(`scripts/lumos:9194`)是規格閘那一族,保留留痕、編號用 NFC、可限定欄位。
- r6 的「一支函式帶 spec_gate=True 兩種模式」已經拆開,方向是收斂。
- 串流讀法(`for chunk in f`)是帳目讀法裡的新樣式,其他讀帳函式仍整本讀。這是在原本就存在的分歧上多一種,不是這份 diff 才引入的雙軌。
- `_sha256_bytes` 是 `_sha256_file` 的本體,後者改成呼叫前者,沒有第二套雜湊。`_prov_read` 改用它,對應守衛 `t_door_scan_logic_version_pin` 同一檔裡的 `"hashlib" not in _i.getsource(m._prov_read)` 把關。專案裡另有約 29 處直接 `hashlib.sha256`,這份 diff 沒有新增。

其餘項目檢查結果(不另列 finding):
- `_door_scan_text` 是 `_strip_zero_width`(`scripts/lumos:5000`)加 `unicodedata.normalize("NFKC", …)` 的組合。NFKC 加去零寬的組合在 `scripts/lumos:9365` 也已有先例,零寬的剝除是共用同一支,沒有重寫一份。
- `_DOOR_SCAN_LOGIC_VERSION` 加原始碼雜湊測試的寫法,跟既有的 `_NOGO_SKIP_LOGIC_VERSION` 與 `t_nogo_skip_logic_version_pin`(`scripts/test_lumos.py:60400`)完全同構:`inspect.getsource` 串接後 sha256、版本與雜湊一起釘,並驗證指紋跟版本連動。這是沿用既有守衛樣式,沒有第二種做法。
- `_under_root` 取代 `_prov_read` 裡手寫的 `Path(...).is_absolute() or root is None` 判斷,是往共用 helper 收斂。
- `_light_gate_fails` 拿掉 `ratchet` 開關,讓規格閘跟 `loop status --light` 用同一個判法,同樣是收斂。

最高等級 minor,blocking 0 條。
