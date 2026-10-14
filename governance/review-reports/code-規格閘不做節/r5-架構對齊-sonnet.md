severity: minor

針對你指定的幾處,對照 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos`(HEAD d1346bf2,不是 d9d97cc)的結果如下。

- **`_hash_chain_check`**:修補沒有另寫鏈驗證。`_nogo_spec_gate_push_light` 照舊呼叫 `_light_gate_fails`,後者內部用 `_hash_chain_check`。新增的 `reviewed_sha256 == snapshot sha` 是新綁定,不是重複。
- **推送範圍檔名清單**:`_spec_gate_touched_plans` 取自同一份 `touched`(來自既有的 `git diff --name-only`)。它還把 `_spec_gate_push_candidates` 原本內嵌的同一段推導抽出來共用,這是收斂,不是新增第二種做法。
- **`RecursionError` 的處理**:壞行與超深巢狀行只跳過那一行,跟第 10649、11396 行等既有寫法一致。
- **`_sh_quote` 的使用**:用法跟既有呼叫一致,沒有直接另用 `shlex`。測試裡直接用 `shlex.split` 是為了驗證印出的指令,不算新做法。

另有三條不對齊,都是 minor。

severity: minor
blocking: 否 — 同一個檢查(快照檔雜湊對帳上雜湊)有現成共用函式,新碼另寫一份;語意差一個「單次讀取」,不會產生兩種結果。
引句:「raw = _at(snp).read_bytes()」
對照:file: `scripts/lumos:26411`(`_prov_check`,帳上 `snapshot_path` 對 `snapshot_sha256` 的共用重驗,處置閘與資安席共用)、file: `scripts/lumos:26716`(`_prov_path` 路徑解析)
判定理由:`_nogo_review_unbound` 內嵌了 `_at`(相對路徑接 repo 根,絕對路徑原樣),等於 `_prov_path` 的第三份;接著又手算 `hashlib.sha256(raw).hexdigest() != snsha`,就是 `_prov_check` 的 `mismatch` 分支。`_prov_check` 接受任意解析函式,可直接 `_prov_check(r, "snapshot_path", _at)`。自寫的理由大概是要一次讀進 bytes 同時雜湊與解碼,避免兩次讀取的 TOCTOU。這個理由成立,但註解沒寫。建議在註解寫明,或讓 `_prov_check` 回傳 bytes。

severity: minor
blocking: 否 — 只影響印出的指令能不能照貼,檔名含空白或引號才出事,是既有行為。
引句:「重跑 lumos spec-gate {Path(prel).stem}」
對照:file: `scripts/lumos:9269`(新碼 `lumos spec-gate {_sh_quote(Path(prel).stem)}`)、file: `scripts/lumos:9140`(同函式 `_spec_gate_push_stale` 上方未加引號)
判定理由:同一個模組裡印給人貼的 `lumos spec-gate <名>`,現在有加引號和沒加引號兩種。9138、9140 兩行是舊碼,但 r4 邊1 修的就是這個缺陷,而且修補正好在這兩行旁邊。這是同族漏掃,建議一併改成 `_sh_quote`。

severity: minor
blocking: 否 — 審查帳逐行讀取已經有好幾份內嵌的讀法,這是再加一份,語意相同;`_canary_ledger_scan` 因為會濾掉規格閘留痕,本來就不能直接用。
引句:「for ln in (_ledger_lines(path.read_text(encoding="utf-8", errors="replace")) if path.exists() else []):」
對照:file: `scripts/lumos:8903`(`_spec_gate_latest_records`,同樣的內嵌讀法)、file: `scripts/lumos:13595`(`_canary_ledger_scan`,先嚴格 UTF-8 解碼並回報 `decode_exc`)
判定理由:`_nogo_light_window` 跟 `_spec_gate_latest_records` 是同類的規格閘專用讀法,都用 `errors="replace"`,風格一致,也都經 `_ledger_lines`。跟 `_canary_ledger_scan` 的差別是後者遇到壞編碼會明確回報,這裡靜默替換。比對用的 `loop`/`kind` 欄位不會因替換字元被誤判,所以不擋。

不對齊 3 條,全部 minor。
