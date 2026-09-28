severity: major

## F1 _guard_formal_line 的測試名比對重新發明了一套平台前綴解析,繞過既有的 resolve_test_refs「不猜」規則

severity: major
blocking: 是 — 這支新寫的比對函式對「未定義平台前綴」不擋、靜默當成命中,跟同檔既有的平台前綴解析函式行為互相矛盾,屬於引入第二種做法。

引句:「any(r == method or r.endswith(":" + method) for r in refs)」

1. `_guard_formal_line`(`scripts/lumos:11809`)裡新寫的比對邏輯在 `scripts/lumos:11824`:當 `method` 有給時,用 `any(r == method or r.endswith(":" + method) for r in refs)` 判「這支正式合約行是不是已經綁了這支測試」。
2. 這支寫死的 `:` 拼接比對,是這個檔案裡**唯一**一處自己做「平台前綴:方法名」比對的地方(`grep -n 'r\.endswith(":"'` 只命中這一行,`file: \`scripts/lumos:11824\``)。而這個檔案早就有一支專門處理「[test:平台:方法] 要不要當成綁定」這件事的既有函式 `resolve_test_refs`(`file: \`scripts/lumos:4315\``),而且它的合約明講:平台前綴沒有在呼叫端定義過的 platforms 集合裡就 `raise ValueError`,理由寫得很白:「不猜,免得綁錯平台」(`file: \`scripts/lumos:4327\``)。`cmd_archive` 就是照這支函式的規矩走(`file: \`scripts/lumos:16215-16221\``:`resolve_test_refs(inv, split, default)`、`except ValueError: continue # 未定義平台前綴:非有效綁定,不護`)。
3. `_guard_formal_line` 的新寫法完全不管 `resolve_test_refs`/`_platform_test_index`(`file: \`scripts/lumos:11263\``)這套既有的平台白名單機制,只要 ref 的尾巴長得像 `:方法名` 就當成同一支測試,不管前綴是不是專案裡真的有定義過的平台——等於把「不猜」的規矩繞過去了。
4. 重現(在 `clone-ns` 唯讀載入模組跑,沒有改任何 repo 檔案):
```
$ python3 - <<'EOF'
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("_lumos_inproc", "scripts/lumos")
spec = importlib.util.spec_from_loader("_lumos_inproc", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
ls = ["---", "summary: |-", "  KEY:★INVARIANT★ 大額退費要人工核可 [test:oops:refund_test]", "---"]
print("endswith match (method=refund_test):", m._guard_formal_line(ls, 3, "大額退費要人工核可", "refund_test"))
try:
    print(m.resolve_test_refs("大額退費要人工核可 [test:oops:refund_test]", {"kotlin", "swift"}, "kotlin"))
except ValueError as e:
    print("resolve_test_refs raises:", e)
EOF
endswith match (method=refund_test): 2
resolve_test_refs raises: [test:oops:refund_test] 的平台前綴 'oops' 未定義於 platforms(kotlin, swift);不猜,免得綁錯平台
```
   同一個 `[test:oops:refund_test]`(`oops` 不是任何專案定義過的平台,可能只是手誤或殘留),`_guard_formal_line` 靜默認成「已經綁了 refund_test」,回傳行索引 2;而檔案裡既有的、專門處理平台前綴的 `resolve_test_refs` 對同一個字串直接擋下不猜。兩支函式對「同一件事」給出相反答案,是同一支檔案裡兩種不同的判準。
5. `guard settle` 本身沒有 `--platform` 參數(`scripts/lumos:34352-34354`,`gst.add_argument("--test", ...)`,沒有 `--platform`),`method` 一定是不含冒號的裸識別字(`IDENT_RE.match(method or "")`,`scripts/lumos:11956`);`_guard_settle_home`(`scripts/lumos:11998`)呼叫 `_guard_formal_line` 時傳的正是這個裸方法名。也就是說這條路徑會真的被 `guard settle` 打到,不是死碼。

## F2 _drift_gate_explicit 另開一條路解析同一把 drift_check.gate 設定,跟 _drift_config 自己講的「每道閘各自一支」互相衝突

severity: major
blocking: 是 — 同一份設定檔的同一個鍵被兩支各自 try/except 的函式分別解讀,對「壞格式但看得出使用者想改」的輸入給出不一致答案,已重現。

引句:「設定檔有沒有自己寫 drift_check.gate(不管寫什麼值)。」

1. `_drift_config`(`scripts/lumos:25630`)的 docstring 自己講明這個檔案的既有慣例:「照 _note_audit_config 的讀法(每道閘各自一支,既有慣例)」(`file: \`scripts/lumos:25631\``)——也就是說一道閘的設定檔解析邏輯只該有一支權威函式。
2. 但這次 diff 為了讓 doctor 開頭知道「使用者是不是自己寫了 drift_check.gate」,另外新開一支 `_drift_gate_explicit(text)`(`scripts/lumos:25651`),自己重新 `_j.loads(...)` 一次同一份 `.lumos/config.json` 內容,對「drift_check 這個鍵有沒有被明著設定」給出獨立判斷,不是從 `_drift_config` 的回傳值衍生出來。這是對同一個設定鍵的第二條解析路徑。
3. 兩條路徑對「格式錯但使用者顯然想設定」的輸入不一致。重現(唯讀,沒有改任何 repo 檔案):
```
$ python3 - <<'EOF'
import importlib.machinery, importlib.util
loader = importlib.machinery.SourceFileLoader("_lumos_inproc", "scripts/lumos")
spec = importlib.util.spec_from_loader("_lumos_inproc", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
txt = b'{"drift_check": "block"}'   # 使用者手誤把 drift_check 寫成字串,不是物件
print("_drift_config:", m._drift_config(txt))
print("_drift_gate_explicit:", m._drift_gate_explicit(txt))
EOF
_drift_config: ('warn', ['設定檔的 drift_check 不是物件(要寫成 {"drift_check": {"gate": "warn"}}),照預設 warn'])
_drift_gate_explicit: False
```
   `_drift_config` 認得出這是使用者「試著設定但格式錯了」,回傳警告字串;`_drift_gate_explicit` 卻因為 `isinstance(cfg.get("drift_check"), dict)` 不成立而判成「沒有明著設定」(`scripts/lumos:25658`)。
4. 這個分歧直接影響 `_drift_gate_doctor_lines`(`scripts/lumos:25803`)的行為:`if mode != "block" and (wired or _drift_gate_explicit(txt)): out.append(...)`。上面這個手誤設定的專案,`mode` 是 `warn`(不是 block),但因為 `_drift_gate_explicit` 判成「沒有明著設定」、且假設專案還沒接線(`wired=False`),doctor 就會整段不印——使用者手誤把閘設壞、實際上正跑在預設 warn,卻拿不到「這個專案的存量漂移檢查是 warn」這行提醒。這正好牴觸了同一輪代碼審自己在筆記裡寫的設計意圖(`docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md`:「代碼審 r1 外家席:關掉了要看得見」)。
5. 對照組:姐妹函式 `_note_shape_doctor_lines`(`scripts/lumos:24251`)完全沒有「explicit」這個概念,只用同一支 `_note_shape_config` 的回傳值(`mode != "block"` 就印),沒有第二支函式重新解析設定檔;`_note_audit_doctor_lines`(`scripts/lumos:26209`)同理。這次 drift 這邊是三支姐妹函式裡唯一一支需要「另一種讀法」的,合理的做法是讓 `_drift_config` 多回一個 `explicit` 欄位(它本來就已經在做同一次 `_j.loads`),而不是另開一支函式重新解析整份 JSON。

## Q1 分層與依賴方向:已看,無 finding(其餘部分)

- `_drift_tree_env`/`_drift_range_events`/`_notes_status_flipped`/`_note_status_seq` 一路都走既有的讀取層(`_nodehome_list`/`_nodehome_cat_blobs`/`_ns_git`/`_lens_git`),沒有繞過去直接呼叫 subprocess 或另開一套 git 包裝(`scripts/lumos:590-648`、`25415-25538`)。
- `guard settle` 改寫預告句(`_guard_settle_rewrite`)與 drift 的 c1 檢查共用同一支 `_guard_planned_prose`(`scripts/lumos:11789`,兩個呼叫端在 `scripts/lumos:11845` 與 `25368`),沒有各寫一份,符合筆記裡「settle 與 c1 共用同一支比對函式」的設計。
- `load_vault` 讀檔失敗與 `Env.from_texts` 解不開的筆記,這次改成共用 `_note_unreadable`/`_READ_FAIL` 這一個管道(`scripts/lumos:130-155`、`412-441`),之前散落的 `env.undecodable` 已經整個拿掉,`grep -rn "undecodable" scripts/ docs/` 只剩測試函式名字裡的 `undecodable` 字樣,沒有殘留的死參照。
- `_drift_c3_hit` 讀 `build_typed_index` 回傳的 `ghosts`/`ambiguous`/`scalars`(`scripts/lumos:25288-25289`)用的欄位索引跟既有兩個呼叫端(`scripts/lumos:15864`、`25403`)的拆法一致(`ghosts`/`ambiguous` 第三個元素都是 `etype`、`scalars` 第二個元素是 `etype`),沒有猜錯欄位順序。

## Q2 命名與錯誤處理:已看,一項 minor

- 現有慣例裡,計時用的區域閉包一律加底線前綴(`_left`,`scripts/lumos:25502`,在 `_drift_check_core` 裡)。但這次新寫的 `_note_status_seq`(`scripts/lumos:24530`)裡,`late`(`scripts/lumos:24536`)沒有加底線,緊接著下面的 `_to`(`scripts/lumos:24539`)卻有底線——同一支函式裡兩顆同類的區域閉包一個有底線一個沒有。`_notes_status_flipped`(`scripts/lumos:24492`)裡的 `late`(`scripts/lumos:24503`)也一樣沒有底線。這是純命名不一致,結構本身沒問題(判斷邏輯、被呼叫的位置都對),定為 minor,不強求非改不可。
- 其餘錯誤處理路徑(`_guard_planned_line`/`_guard_settle_home` 對「好幾條一樣的預告行」統一印同一句錯誤訊息、`_note_base_status` 的 `strict` 分流)跟既有慣例一致,已看,無 finding。

## Q3 第二種做法:F1、F2 已列在上面;其餘已看,無 finding

- `_guard_planned_idx` 把原本兩處各自手寫的「找預告行索引、重複就擋」邏輯收成一支共用函式(`scripts/lumos:11826` 附近,呼叫端 `_guard_planned_line` 與 `_guard_settle_home`),這是收斂掉重複邏輯,不是新增第二種做法。
- `_guard_formal_line` 這次改成跟 `cmd_guard_bind`/`cmd_guard_kill_add`/`cmd_guard_audit` 一樣用 `INV_TAG_RE.sub` 剝標記、用 `invariant_test_refs` 拆測試清單(`scripts/lumos:11809-11826`),對照 `cmd_guard_bind`(`scripts/lumos:12208`起)、`cmd_guard_kill_add`(`scripts/lumos:12298`)、`cmd_guard_audit`(`scripts/lumos:12735`)這幾處既有呼叫端,標記剝除與比對方式是一致的——除了 F1 指出的那個尾端「平台前綴」比對,`_guard_formal_line` 本身的改法確實是把前兩輪自己發明的正規式換回既有共用機制,方向是對齊、不是分裂。

最嚴重 major,blocking 共 2 條。
