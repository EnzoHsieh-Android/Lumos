severity: minor

我對的是 repo 現況 HEAD(`30ae09fb6`),它已經包含這份 patch,所以下面的行號都是 `/Users/enzo/harness/lumos-spec-snapshot/scripts/lumos` 現況的行號。patch 之前的版本我拿 `3776c7afc` 的 `scripts/lumos` 比對過。

## 問 1 分層與依賴方向

**大致對齊,有一個要請編排者看的依賴(A1)。**

對齊的部分:
- 讀取端放在比對工具那一區,從 `_tg_analyze` 尾端接進去(`scripts/lumos:49592` `_tg_redbase_cands`)。三個呼叫端(`cmd_test_guard`、`_lint_new_guard`、推送前)都自動走同一條路,沒有另開入口。
- 讀取端沒有讀圖譜或計劃,只讀 git 兩版的治理帳和終點那一版的紅燈版檔。治理帳那兩版用 `_gov_rows_delta` 讀(`scripts/lumos:60551` 的 `_gov_rows_at`,殘留問答原本那套讀法抽出來的),紅燈版檔批次讀,沿用 `_tg_read`(`scripts/lumos:49313`)用的 `_nodehome_cat_sizes` 加 `_nodehome_cat_blobs_capped`。
- 沒有反向的依賴:比對工具那一區沒有呼叫任何 `_redbase_*` 或規格閘函式。
- 殘留問答的 `_residual_ask_rows_at/_delta` 抽成共用的 `_gov_rows_at/_delta`,舊名留作薄包裝,沒有多出第三份讀法。
- 分岔點用 `_tg_start`(`scripts/lumos:49343`),跟 `_lint_new_guard`(`scripts/lumos:39290`)是同一支。
- 簿記資料夾加進 `_BOOKKEEPING_DIRS`(`scripts/lumos:37835`),寫法跟 `governance/reread-verdicts/` 那項一樣。

看的段落:
引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」

### A1 ⚠ 規格閘寫入端直接呼叫比對工具的內部函式
severity: minor
blocking: 否 — 依賴是為了讓寫入端和讀取端用同一套函式鍵,沒有另寫一套切函式,但呼叫的是內部函式而不是對外入口;判不準,交編排者。
引句:「fs, ok = _tg_functions(text, rel.endswith(".java"))」

說明:
- 規格閘那一區(`scripts/lumos:14294`)直接用了比對工具的 `_tg_functions`、`_tg_has_long_line`、`_TG_MAX_LINE_CHARS`、`_TG_MAX_BYTES`、`_tg_rb_entry`、`_tg_rb_path_ok`、`_RB_DIR`、`_RB_VERSION`。
- 修改前(`3776c7afc`)比對工具那一區之外,只有 `_lint_new_guard` 呼叫過 `_tg_start` 和 `_tg_analyze`(`scripts/lumos:38982`、`39070`、`39073`)。這是整支引擎的對外入口,沒有人碰過 `_tg_functions` 這種內部函式。
- 反過來看,如果寫入端自己另寫一套切函式,函式鍵就可能跟讀取端對不上,那才是第二種做法。所以我判這個依賴方向可以接受,但跟既有慣例有落差。
- 最近的前例是 `_note_audit_write_verdict`(`scripts/lumos:50940`):讀端的上限由呼叫端以參數傳進去,寫端不直接引用讀端的常數。
- 如果編排者認定「只准經對外入口」,這條要升 major,改法是比對工具那一區提供一支給寫入端用的函式。

## 問 2 命名與錯誤處理

**函式前綴、規則代號和錯誤回傳大致對齊,有三處不一致(A2、A3、A4)。**

對齊的部分:
- 寫入端用 `_redbase_*`,讀取端用 `_tg_redbase_*`/`_tg_rb_*`,規則代號 `tq/redbase-*` 補進 `_TG_WHY`(`scripts/lumos:49267`-`49269`),跟 `tq/unparsable`、`tq/unreadable`(`scripts/lumos:49265`-`49266`)同一個格式。
- 留痕欄位 `redbase_skipped`、`redbase_skipped_n` 跟既有的 `nogo_skipped`、`nogo_skipped_n`(`scripts/lumos:14165` 一帶)同形狀。
- 讀取端對外回 `(None, 錯誤訊息)`,跟 `_tg_analyze` 一致(`scripts/lumos:49378` 一帶)。
- 超過截止時間丟 `TimeoutError`,跟 `_tg_analyze` 一致。
- 寫入端寫不進去就丟 `OSError`,由 `_redbase_attach` 往上接,在 stderr 印 `[spec-gate] ...` 後照舊留痕,跟 `_spec_gate_record` 的 `留痕寫不進審查帳` 同一個做法。
- 事件走 `_gate_event`,`False` 時印一句,跟 `_spec_gate_record` 一致。
- 辨別「物件或原因字串」的 `isinstance(x, str)` 寫法,`cmd_spec_gate` 的 `isinstance(front, int)` 已有前例。

看的段落:
引句:「print(f"[spec-gate] 紅燈版寫不進去({e}),這次沒有紅燈版可比", file=sys.stderr)」

### A2 比對引擎內部直接印訊息
severity: minor
blocking: 否 — 輸出方式跟鄰居不一致,結構沒有錯。
引句:「print("test-guard:起點是空樹(找不到主線),這次不用規格閘紅燈版", file=sys.stderr)」

說明:
- 比對工具那一區(`scripts/lumos:48393`-`49332`)在修改前一個 `print` 都沒有,只有 `cmd_test_guard` 自己印(`scripts/lumos:49339`)。
- 新增這句在 `scripts/lumos:49599`,放在 `_tg_analyze` 呼叫的函式裡面。
- 新增告警閘已經用 `no_baseline` 欄位(`scripts/lumos:39298`)把「沒有起點」回報給呼叫端,由呼叫端決定要不要印(`scripts/lumos:71036`、`71067`)。
- 這句會在新增告警閘裡也印出,而且標頭是 `test-guard:`,不是閘自己的名字。

### A3 寫入端遇到治理帳讀不出時靜默放過,鄰居會出聲或擋下
severity: minor
blocking: 否 — 錯誤處理跟鄰居不一致,結構一樣。
引句:「_d, added, bad = _gov_rows_delta(rr, fork or _EMPTY_TREE_SHA, None, b'"spec-gate-', _redbase_branch_keep)」

說明:
- `_redbase_branch_rows`(`scripts/lumos:14319`)在治理帳讀不出時(`bad` 有值)直接回 `[]`,沒有任何輸出。
- `_redbase_branch_state`(`scripts/lumos:14371`)讀上一份紅燈版失敗也是 `continue` 靜默略過。
- 同一功能裡的 `_redbase_note_green` 和 `_redbase_attach` 都會在 stderr 印 `[spec-gate] ...`。
- 讀取端 `_tg_redbase_records` 遇到同樣情況是回錯誤(`return None, f"git 讀不出{bad}那一版…"`)。
- 專案另有「帳壞就當帳壞、不當成沒有紀錄」的慣例(`_gov_vc_gate_events` 的說明,`scripts/lumos:21929`)。

### A4 常數與測試名前綴跟同區慣例不同
severity: minor
blocking: 否 — 命名跟鄰居不一致。
引句:「_RB_SHA_RE = re.compile(r"[0-9a-f]{64}")」

說明:
- 比對工具那一區的常數全是 `_TG_*`(`scripts/lumos:48395`-`48403`),新增的三個是 `_RB_DIR`、`_RB_VERSION`、`_RB_SHA_RE`(`scripts/lumos:49550`-`49552`)。
- 同一功能的讀取端函式也同時用了 `_tg_redbase_*` 和 `_tg_rb_*` 兩種前綴。
- 比對工具既有測試是 `t_tq_guard_*`(9 支),新增的 8 支是 `t_tg_redbase_*`。

## 問 3 第二種做法

**沒有找到會判 major 的第二種做法,有三處接近(A5、A6、A7)。**

沒有重複的部分:
- 讀治理帳的兩版:共用抽出來的 `_gov_rows_at/_gov_rows_delta`。
- 讀 git 某一版的檔:治理帳用 `_residual_blob_at`(`scripts/lumos:60407`),紅燈版檔用 `_nodehome_cat_blobs_capped`。分工的理由是紅燈版要單檔上限,`_residual_blob_at` 沒有。`_tg_read` 本來就用後者。
- 原子寫:用 `_write_bytes_atomic`(`scripts/lumos:28789`),沒有另寫。
- 上限:`_TG_MAX_BYTES`、`_TG_MAX_TOTAL`、`_TG_MAX_LINE_CHARS` 全部借用,沒有新數字。
- 指紋:走 `_tg_cand` 同一支。
- 紀錄資料夾:`governance/redbase/` 是新種類,沒有既有的資料夾做同樣的事。計劃也交代了它不是 `spec-freeze` 的凍結快照。

⚠ 一處我沒列成 finding,交編排者:
- 規格閘旁邊的 `_spec_gate_gov_index`(`scripts/lumos:15238`)讀規格閘留痕走 `_gov_vc_gate_events`(有路徑守衛)。
- `_redbase_branch_rows` 讀同一種留痕走 `_gov_rows_delta`,因為它要跟分岔點那版做行差。
- 這兩種工作目錄讀法在修改前就並存(`_residual_ask_rows_at(None)` 對上 `_gov_vc_gate_events`),這份 patch 只是多了一個呼叫端,所以我沒算它引入第二種。

### A5 紅燈版資料夾的寫入沒走共用的資料夾安全檢查
severity: minor
blocking: 否 — 原子寫是共用的那一支,只有資料夾安全檢查沒走共用的;而且同樣不檢查的前例有。⚠ 判不準,交編排者。
引句:「target.parent.mkdir(parents=True, exist_ok=True)」

說明:
- `_redbase_write`(`scripts/lumos:14364`)自己 `mkdir` 後直接寫。
- 判定檔和重讀對照紀錄的寫入走 `_note_audit_write_verdict`(`scripts/lumos:50940`),裡面用 `_note_audit_safe_dir`(`scripts/lumos:50922`)擋符號連結與跑出 repo。那段說明講明「原本各寫一套」被架構席抓過,逐層擋符號連結的邏輯「只有這一份」`_repo_path_unsafe`(`scripts/lumos:50889`)。
- 但 `governance/replay/<迴圈>/` 的凍結寫入(`scripts/lumos:1450`)也是自己 `mkdir`,沒有走守衛。新的寫法形狀和 replay 一樣(每個迴圈一個資料夾),所以我降到 minor。
- 迴圈編號含路徑字元時,replay 會拒絕(`scripts/lumos:1371`),`_redbase_write` 把它換成 `_` 照寫。

### A6 寫入端自己再解析一次紅燈版檔
severity: minor
blocking: 否 — 同一份格式有兩處在解析,是重複,不是新做法。
引句:「doc = _json.loads((Path(rr) / path).read_bytes().decode("utf-8"))」

說明:
- `_redbase_branch_state`(`scripts/lumos:14386`)自己讀工作目錄裡上一份紅燈版,只檢查 `tests`、`files` 的型別,不驗 `version`、也不驗 sha256。
- 讀取端有一支專門驗格式的 `_tg_rb_doc`(`scripts/lumos:49664`),驗大小、sha256、JSON、版本、形狀。
- 之後格式升到 v2 時,寫入端會把 v2 檔當 v1 讀。

### A7 補讀測試檔時沒套用比對工具對測試檔的前置處理
severity: minor
blocking: 否 — 同一份函式切法,前置處理不一致,不是另一套做法。
引句:「sides.append(_tg_functions(t, p.endswith(".java"))[0] if t and t not in ("TOOLARGE", "UNREADABLE") else {})」

說明:
- `_tg_rb_fill`(`scripts/lumos:49731`-`49743`)讀「紅燈版記到、但不在改動清單裡」的測試檔,直接餵給 `_tg_functions`。
- `_tg_analyze` 對測試檔會先擋超長行(`scripts/lumos:49377`,理由是函式切法對超長行有平方級風險)。
- `_tg_test_file` 看到括號配不平會列 `tq/unparsable`(`scripts/lumos:49429`),`_tg_rb_fill` 把 `ok` 旗標丟掉。
- 斷言訊息在後的判斷也不同:`_tg_test_file` 是 `_TG_MSG_LAST_RE.search(h + "\n" + b)`(`scripts/lumos:49430`),`_tg_rb_fill` 只看 head 那端(`scripts/lumos:49743`),`_tg_rb_entry` 只看內嵌文字。
- 計劃寫「病態輸入的判法跟比對工具對終點測試檔同一套」,這一條路徑沒有做到。

不對齊共 7 條,其中 major 0 條
