severity: major

## 複核

上一輪四件(①刪掉無副檔名 #! 檔磁碟讀不到、②③拆死碼/共用 shebang 判斷、④同②)都已在正式 patch 裡看到對應改動,逐一核對如下,沒有反向錯:

- ①②③④ 共用點 `_head_is_shebang`:定義在 `_spec_gate_push_candidates` 附近,實作 `return bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")`。傳 `None` 時 `bool(None)` 為 False,傳空 bytes `b""` 時 `bool(b"")` 為 False,兩者都直接短路回 False,不會在 `None[:200]` 炸掉。`_nodehome_required` 那處原本內聯的判斷式已經換成呼叫這支共用函式,行為等價(逐字比對過原公式與新函式內容一致)。
- ① `_is_code_file` 磁碟讀不到轉 `git show base:path`:`subprocess.run(["git", "-C", str(rr), "show", f"{base}:{path}"], capture_output=True, errors=None)` 沒有帶 `text=True`,回的 `g.stdout` 是 bytes,直接餵給 `_head_is_shebang` 型別一致;`errors=None` 在非文字模式下是 no-op,不會炸。空樹起點/`A...B` 三點形式:`base = diff_range.split("..")[0]`,對 `"A...B"` 這種字串驗過 python 的 `split("..")` 語意是 `["A", ".B"]`,取第一段仍是正確的起點 `A`,不是壞掉的字串。兩邊都讀不到(base 也沒有,純新增又刪除)時函式尾端 `return True`(保守當程式檔),跟宣稱的一致,沒有走漏。
- ②④ `_spec_gate_push_report` 死碼與圖譜 KEY 不一致:正式 patch 裡已看不到這個函式名,`manual_only` 分支也確認被拆掉(cmd_doctor 那段跟 spec-gate 那段都改讀 `plan_risk`/`_rec_plan_risk`,沒有殘留 `door`/`manual_only` 的舊分支)。

四件複核:clean。引句(逐字取自正式 patch):`return bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")`

## F1 `_is_code_file` 自稱「每支檔有家同一套」但漏掉測試/vendored/glob 三種豁免,會反向誤擋小改動閘

severity: major
blocking: yes

引句:「"""「需要有家的程式檔」判定(每支檔有家同一套):副檔名在清單裡=是;沒副檔名要看首行是不是 #!(.gitignore/Makefile 這種不是)。」(取自 `_is_code_file` docstring 開頭,單行,已去除首尾多餘引號字元後仍完整對應原文)

觀察:真正的「每支檔有家」判定在 `_nodehome_required`(file: `scripts/lumos:20826`)裡,除了 `_nodehome_code_kind` 的副檔名/shebang 分類之外,還疊了三層豁免才會真的要求那支檔有家:
- `_NODEHOME_EXCLUDE_GLOBS`(file: `scripts/lumos:20453`,含 `docs/*`、`*/node_modules/*`、`*/bin/*` 等)
- `_cochange_excluded(p, cfg["ignore"])`
- `_nodehome_is_test(p, layout)`(file: `scripts/lumos:20644`,測試檔——含 `test_*.py`、`*/tests?/*` 目錄、`_test`/`_spec` 結尾等——一律不算「需要有家」)

這批 patch 新增的 `_is_code_file`(供 `_sc_diffusion` 與 `_pitfall_tier` 共用)只搬了 `_nodehome_code_kind` + shebang 判斷這一層,完全沒有套用上面三層豁免。docstring 卻寫「每支檔有家同一套」,等於宣稱兩邊判定完全一致,但實際上不是子集關係的等價,而是少做了三種排除。

重現:一份「全靠人驗」的風險低計劃(小改動閘唯一適用場景,見 `_small_change_check`)如果這次改動裡順手碰了一支既有測試檔(例如 `scripts/test_lumos.py`,`stem.startswith("test_")` 命中 `_nodehome_is_test`),真正的「每支檔有家」系統不會要求這支測試檔有家,但 `_sc_diffusion` 呼叫的是漏掉豁免層的 `_is_code_file`,會把它算進 `code`,進而拿去跟 `allowed`(計劃 `lands_in`/`related` 節點的 `about_code`)比對;測試檔通常不會被任何節點的 `about_code` 列進去(因為它本來就不需要家),於是被判「落點外」擋下——這正是這批改動想修的那個方向(README 誤判落點外)的鏡像版本,只是換成測試檔/`docs/*` 下的程式範例檔/vendored 檔會被誤擋,而不是誤放行。

為什麼是 bug:這批 patch 的動機說明就是「2026-09-18 實測:改 README 被判落點外」要修掉這種誤判,但只堵了「非程式檔不該算」這個方向,沒有堵「程式檔但依 node-home 定義不需要家(測試檔/vendored/glob 排除)也不該算」這個對稱方向。`_pitfall_tier` 也共用同一支 `_is_code_file`(引句:「改動裡沒有任何「需要有家的程式檔」(_is_code_file,每支檔有家同一套定義)→ light」),同樣的落差會讓純測試檔改動被算成「有程式檔」而分到 `standard` 而非 `light`,分級跟著漂。

file: `scripts/lumos:20826`(`_nodehome_required` 的三層豁免,`_is_code_file` 沒有套用)
file: `scripts/lumos:20453`(`_NODEHOME_EXCLUDE_GLOBS`)
file: `scripts/lumos:20644`(`_nodehome_is_test`)

r3-tests-ref.patch 裡沒有任何一支測試名提到 `_nodehome_is_test`、`_NODEHOME_EXCLUDE_GLOBS` 或 `_is_code_file`,這個落差沒有測試接住。

## F2 `_spec_gate_push_scan` 的 quiet/record_escape 參數是死碼,全 repo 沒有任何呼叫點傳 quiet=True

severity: minor
blocking: no

引句:「def _spec_gate_push_scan(env, rr, plans, git_range, quiet=False):」

觀察:`_spec_gate_push_scan` 新增 `quiet` 參數,往下傳給 `_spec_gate_push_one(..., record_escape=not quiet)`,用來在「quiet 模式」下不印 ok_line、不觸發 `_auto_escape`(逃逸自動記)。但全 repo 只有一處呼叫 `_spec_gate_push_scan`(在 `_spec_gate_push_check` 裡,`bad, oks = _spec_gate_push_scan(env, rr, plans, git_range)`),沒有帶 `quiet=True`;`record_escape` 這個參數同理全 repo 只在這條鏈路上出現,沒有第二個呼叫點會傳 `record_escape=False`。目前這條分支完全不可達,是半成品的通用化(可能是為了之後某個「只算 tier 不留痕」的用途預留,但這批 patch 沒有用到它)。不影響現有行為正確性,單純是死碼,建議拆掉或補上呼叫點與說明。

## F3 lint 對 `door` 欄位不再驗值是否合法,只提示「舊寫法」

severity: minor
blocking: no

引句:「if n.fields.get("door") is not None:
+        warns.append("door 是舊寫法(2026-09-17 改名),改成 plan_risk: high(舊值仍讀得懂)")」

觀察:改名前,`door` 欄位有值就會驗 `str(_door).strip() not in ("one-way", "two-way")`,寫錯值(像 `door: maybe`)會被 lint 明確點出「door 只認 one-way / two-way」。改名後,只要 `door` 有值就一律印「舊寫法,改成 plan_risk」,不再檢查值本身合不合法——寫 `door: maybe` 現在只會被提醒「改成 plan_risk」,不會被告知這個值本身工具讀不懂(`_plan_risk_norm` 會把它歸到 `unknown`,靜靜地當作沒設定)。功能上不算擋錯(`unknown` 分支本來就是安全預設),但作者想標記卻打錯字時,舊行為會馬上被抓到、新行為要等下游行為對不上才會發現,是一個小的診斷力倒退。
