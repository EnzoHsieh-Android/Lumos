severity: minor

# 架構對齊審查 r3(末輪)

審的是 /tmp/code-tail-r3.patch(程式只有 scripts/lumos 一支,其餘為測試、計劃與筆記)。佐證都在審查用的 clone:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw。
末輪火力放在 blocking 級與上輪修法對不對。結論:上輪六個修法的結構都對得上專案既有做法,沒有第二種做法、沒有跨層直呼,所以沒有 major。下面三條都是 minor。

## 三問

### 問 1 分層與依賴方向

- `_ns_nfc_clash_errs` 放在筆記形狀擋那層(`_ns_` 前綴),筆記內容審那層(`_note_audit_items`)去呼叫它。方向是內容審用形狀擋的東西,跟既有的 `_NotelinesPairs`、`_ns_check_line` 被內容審共用是同一個方向,沒有反向。對照:file: `scripts/lumos:29909`(`_note_audit_items` 本來就建 `_NotelinesPairs`)。
- 路徑清單用 `_nodehome_list` 不去重的第二個回傳值,跟 `_note_shape_eval` 開頭取的 `lst` 是同一支、同一個用法。對照:file: `scripts/lumos:28733`。`_note_audit_items` 另起一次 `_nodehome_list`(多一次 git ls-tree),但有 `if items` 擋著,只有真有送審項目才付;不算分層問題。
- `_ns_append_read_blobs` 抽出來後,`_notelines_append_pairs` 只剩判斷與組表,讀取留在另一支,跟鄰居 `_ns_append_same_context` 的切法一致。`_nodehome_cat_sizes` 是既有的批次問大小函式,直接重用,沒自創。對照:file: `scripts/lumos:26467`。
- 去重改讀治理帳:路徑 `repo/docs/.governance-log.jsonl`、讀法 `_gov_tail_bytes` 加 `_drift_jsonl_iter`,跟 doctor 帳增速段與 `_gov_metric_events` 一模一樣。對照:file: `scripts/lumos:3660`、file: `scripts/lumos:2081`。過濾用的欄位 `attempt_id` 也是 `_gate_event_build` 寫的那個欄位(含 `[:64]` 截斷),讀寫兩端對得上。對照:file: `scripts/lumos:1164`。

### 問 2 命名與錯誤處理

- 命名:`_ns_relaxed_recorded`、`_note_audit_dispute_for`、`_ns_nfc_clash_errs`、`_ns_append_read_blobs` 都照所在區段的前綴(`_ns_`、`_note_audit_`)。`_NS_APPEND_MAX_TOTAL_BYTES` 跟同組常數同形。
- 回傳形狀:`_notelines_append_pairs` 的第二個回傳值多一個 `"cap"`,呼叫端用 `capped` 與 `failed` 兩個旗標分開,沒有拿例外或新回傳型別,跟 `(值, 原因)` 的既有形狀一致。
- 錯誤處理有兩處跟鄰居不一樣,見 Z1、Z3。

### 問 3 第二種做法

- 上輪最大的第二種做法(git 目錄裡的 `lumos-relaxed-seen` 記號檔)已經拿掉,改讀治理帳,這輪確認 repo 裡已沒有殘留的讀寫(grep 無命中)。
- 沒有發現新的自創工具函式;`_ns_nfc_clash_errs` 用 `collections.Counter` 是標準庫,函式內 `import collections` 跟 `_ns_append_subtract` 同寫法。
- 剩下的是一條廢碼與說明過期(Z2)。

## 發現

**Z1 「候選太多」提醒印在資料類別的 `table()` 裡,跟鄰居「類別只設旗標、呼叫端印」不一樣**
severity: minor
blocking: 否 — 輸出位置不一致,結構與判定都對;唯一的實際後果是 doctor 路徑會印一句對它不適用的建議
引句:「print(f"提醒:這次舊行尾補括號的候選太多(超過 {_NS_APPEND_MAX_FILES} 篇、{_NS_APPEND_MAX_PAIRS} 對或要讀的檔案總和"」

1. 對照:`_NotelinesNet` 是同形的「用到才算」類別,git 失敗只設 `failed` 旗標,印不印由呼叫端決定。file: `scripts/lumos:27511`(類別說明寫明「用旗標」的理由),呼叫端檢查在 file: `scripts/lumos:27495`。同一個 `_NotelinesPairs` 的「失敗」提醒也是呼叫端 `_note_audit_mark_appended` 印的,file: `scripts/lumos:29921`。
2. 這輪新加的 `capped` 提醒卻直接印在 `_NotelinesPairs.table()` 裡,同一個類別內「失敗」與「超限」兩種原因的輸出位置不一致。
3. 具體壞處:提醒寫死「分幾次提交或推送就能只查補上的那段」。doctor 掃描走同一支 `_note_shape_eval`(file: `scripts/lumos:28721` 的說明),起點是上線點、不是這次提交或推送的起點,對 doctor 來說分幾次推沒有用。上線點之後累積超過 200 篇有補括號的候選時,doctor 會在 stderr 印出這句不適用的建議。結構性修法:`table()` 只設 `capped`,提交前與推送前的呼叫端印(第二層 `_note_audit_mark_appended` 已經有這個位置)。⚠ doctor 路徑沒有實際跑 200 篇的夾具重現,以上是照程式讀出來的。

**Z2 整行層級規則改成不扣之後,`_ns_viol_key` 的回頭條件分支與 `_NS_REVISIT_RULES` 變成只算不比的廢碼,說明與計劃〈做法〉2 的回頭條件那句也沒跟上**
severity: minor
blocking: 否 — 不影響判定,是死碼加兩處過期說明
引句:「        if v[2] not in _NS_FRAG_KEY_RULES:」

1. `_ns_append_subtract` 現在先判 `v[2] not in _NS_FRAG_KEY_RULES` 就整條保留,後面真正比對計數的只剩 `("程式行號引用", "釘版本不合法")` 兩條規則。
2. `_ns_viol_key` 裡 `if rule in _NS_REVISIT_RULES: return (rule, fix)` 與最後的 `return (rule,)` 只剩替 `base` 計數表建鍵用,永遠不會被拿來比對、扣減。對照:file: `scripts/lumos:27697`、file: `scripts/lumos:27725`(舊行違規全算進 `base` 卻只有片段鍵會被讀)。
3. 過期說明一:`_ns_viol_key` 的 docstring 還寫「新規則預設是規則名,要用片段鍵在那條規則自己的計劃寫明」,但新做法是預設不扣、要扣得加進 `_NS_FRAG_KEY_RULES`。
4. 過期說明二:計劃〈做法〉2 末行(diff 的上下文行)還寫「`_ns_revisit_violations` 對 N 與 O 各算……鍵(規則, 改法)……補一個寫錯的條件會照報」,語意是「同樣的條件寫錯會被扣掉、新的才報」。r3 後「條件寫錯」「回頭條件格式不合」跟其他整行規則一樣一律不扣(舊行本來就條件寫錯、補括號照報)。計劃同一節兩句互相矛盾。對照計劃:file: `docs/lumos-toolchain-knowledge/Projects/舊行尾追加不算新寫_計劃.md`〈做法〉2 第二條。
5. 測試 `t_note_audit_append_scope_more` ③ 還釘著 `_NS_FRAG_KEY_RULES + _NS_REVISIT_RULES` 兩張表,是這個廢碼沒被發現的原因之一;要嘛刪掉回頭條件分支與該表,要嘛把「它只用來算 base」寫進說明。

**Z3 放寬帳去重只套在 `done` 事件,而且不管有沒有東西要去重都先讀整段帳尾**
severity: minor
blocking: 否 — 只會多記或多讀,不改任何判定
引句:「seen = _ns_relaxed_recorded(root, os.environ.get("LUMOS_PUSH_ATTEMPT", "").strip())」

1. 同一個函式 `_ns_relaxed_record` 裡三種事件:`git-failed/error`、`capped`、`done`。只有 `done` 走 `seen` 去重;一次推好幾條分支、範圍重疊時,`capped`(以及配對失敗的 `error`)每條分支各記一筆。該函式說明與計劃〈做法〉5 都寫「同一次推送已經記過的行不再記」,只講行,所以不算違反計劃;但同一函式內三種事件的重複規則不一致,RETIRE-IF ② 數「沒機會用」與「壞了」時會被重複的 `capped` 灌水。
2. `seen` 是無條件先算的。有推送編號時,即使 `by_line` 是空的(只有 `capped` 或 `error` 要記)也會讀並逐行解析最多 24 MiB 的帳尾(`_GOV_TAIL_CAP`,file: `scripts/lumos:3527`)。鄰居(doctor 帳增速段、`_gov_metric_events`)都是有東西要看才讀。修法一行:`by_line` 非空才呼叫 `_ns_relaxed_recorded`。
3. ⚠ 推送路徑沒有實測帳尾 24 MiB 的耗時,只能說多讀是白讀;上面是讀程式的結論。

## 固定席節點

逐篇判這份 diff 會不會破壞那篇宣稱的行為或合約。

- reversibility-governance-ledger(★RISK★):這份 diff 新增的治理帳寫入者是 `relaxed` 的 `capped` 事件,走既有的 `_gate_event_or_warn`;去重改成讀帳,沒有新增寫帳路徑、沒有改帳的欄位。不影響那篇說的可逆性與治理帳寫入規則。
- lumos-cli-read(★INVARIANT★ 搜尋預設排除 superseded 不排除 stale):diff 沒動 search 的濾網,也沒碰命中確認與三路分岔。不影響。
- bound-tests-gate(★INVARIANT★ 綁定測試逐支真跑):diff 改了測試函式名的綁定(新增 `t_ns_append_line_rules`、`t_ns_append_ledger_dedupe`、`t_ns_nfc_clash_errs`、`t_note_audit_dispute_scope`;改動 `t_ns_append_caps` 等),計劃的條款也補了 [S47]–[S50] 各綁一支;被改的測試用「前置斷言」修掉假綠,方向是更嚴。不影響閘本身的邏輯。
- guard-kill(★INVARIANT★ rc 優先序與 --json 純度):diff 完全沒有碰 guard kill。不影響。
- 授權與歸屬(★INVARIANT★ 授權檔不進 `_VENDORED_TOOLKIT`、主程式檔頭帶 SPDX 與 MIT 全文):diff 只在 scripts/lumos 中段改函式,檔頭未動,也沒有新增被複製的檔。不影響。
- 測試假綠形態(★INVARIANT★ 還原翻紅釘必須配前置斷言):這是 diff 在落實它,七支配對測試改成「舊行就有的行號引用加帶來源的括號」並補前置斷言(例如 `①a 前提:改一個字配不上時……`)。符合那條合約。牆上時鐘門檻改成數呼叫次數與相對倍數,同方向。
- pitfalls-code-loop(★RISK★):這份 diff 改的是筆記形狀擋與內容審,不動 pitfalls 的分級與風險計算。不影響。
- design-loop(★INVARIANT★ 處置閘第五步:審材必須是 .md 計劃、有 [SN] 條款定義時要綁測試):diff 補的 [S47]–[S50] 都有 [test:…] 綁定,[S43]–[S46] 改字後測試名未變,條款格式照現行。不影響。
- 只列名的節點(lumos-cli-lifecycle、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim-get/install/uninstall、規格落成可驗收條件_計劃、雙向門放行_計劃、逃逸自動記_計劃、core-invariant-baseline、judge-severity-gate):內文沒給我,只能憑名字判斷。diff 沒碰 deinit、slim 安裝與卸載、canary、check-r 等路徑。其中「節點範圍與索引守衛」與 `_ns_nfc_clash_errs` 都處理檔名 NFC 比對,⚠ 沒讀到該篇內文,無法判兩者的 NFC 規則是否一致;`_ns_nfc_clash_errs` 用的是 `_nodehome_list` 已 NFC 化的路徑清單,跟那支函式本身的說明一致。

## 沒問題的項目

- 六個上輪修法逐項對得上既有做法:只扣片段規則(結構對,細節見 Z2)、cap 回傳形狀、`_ns_nfc_clash_errs` 用不去重清單(`_nodehome_list` 第二回傳值確實是不去重的路徑清單,file: `scripts/lumos:26155`)、改讀治理帳去重(讀法跟 doctor 同一套)、申訴分範圍(`_note_audit_dispute_map` 回傳多一層以 tail 為鍵,唯一的讀者 `_note_audit_dispute_for` 是 `_note_audit_fold_scoped` 呼叫,沒有別處還在拿舊形狀)、`_ns_diff` 旗標與 `_ns_deleted_summary_lines` 對齊(兩邊旗標組逐字相同)。
- 測試改動:`_tail_try` 抽成共用輔助,取代各測試自己重複的 note、stage、`_ns`、reset 四步,沒有第二套;`t_ns_append_ledger_dedupe` 用 `_tail_relaxed` 與 `_ns(…, env=…)` 既有輔助。
- 說明文件三篇(計劃、兩篇 Systems 筆記、skill 子檔)互相對得上 cap、整行規則不扣、申訴分範圍這三件事。

最高 severity:minor
