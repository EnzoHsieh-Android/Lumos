severity: major

## F1 drift check 的 60 秒預算不是端到端保證,實測單一分支已超過 67 秒才判「超過預算」
severity: major
blocking: 是 — block 模式下這個「判不了」直接讓 rc=1 擋下推送(而且是真實可觸發的「新分支首推/force-push 找不到主線」場景,不是人造邊界)
引句:「_DRIFT_BUDGET_SEC = 60」

1. `cmd_drift_check` 把 `deadline=_t.monotonic() + _DRIFT_BUDGET_SEC` 傳進 `_drift_check_core`,但 `_drift_check_core` 只在**一個**位置檢查這個 deadline:先跑完 `_drift_range_events(root, base, tip, vault_rel, reader)`(這是整段流程裡最貴的部分——見下)之後、開始建整份圖譜的樹(`_drift_tree_env`)之前。`_drift_range_events` 本身完全不吃 `deadline` 參數,跑多久都不會被這個檢查點打斷。
2. `_drift_range_events` 對 c1 以外的每一種狀態轉換各呼叫一次 `_notes_status_flipped`(passed 一次、closed 一次,經 `_note_audit_closed_plans`),而 `_notes_status_flipped` 內部對**每一篇通過型別/狀態篩選的候選筆記**各起 1–3 個 `git` 子行程(`reader(p)`=`git show`、`git log --follow`、視改名而定的 `git diff --name-status`),外加一個小型 `_nodehome_cat_blobs` 呼叫——這些呼叫次數隨這次推送範圍裡「碰過的筆記數」線性成長,每個呼叫各自有自己的 20 秒逾時(`_lens_git`),不受外層 `deadline` 節制。
3. 就算撐過第 2 步,`_drift_tree_env`(建整份圖譜的樹)呼叫 `_nodehome_cat_blobs`,那支自己內部又是獨立的 `timeout=60`(`subprocess.run(..., timeout=60)`)——跟外層 `_DRIFT_BUDGET_SEC=60` 完全脫鉤;如果第 1、2 步已經用掉了 55 秒,理論上這一步還能再吃到 60 秒,總時間逼近兩倍預算。
4. 實測重現(在被審 repo 自己的 573 篇圖譜上跑,base 取全庫第一個提交,模擬 `_lens_push_base` 對「新分支首推、找不到主線」時真的會退回的空樹起點):
   ```
   cd <clone-ns>
   time python3 scripts/lumos drift check --diff 87d43a50..b9ca00bbda322504c612f9301afe9c903086cabb --repo .
   ```
   輸出:
   ```
   python3 scripts/lumos drift check ... 25.10s user 39.33s system 95% cpu 1:07.62 total
   提醒(drift_check.gate=warn,不擋):這次推送有 0 處要處理(存量漂移檢查)——
     判不了:超過 60 秒預算——判不了就放行等於一條繞過的路,所以算要處理;真的要推就單次略過(會留帳):
       LUMOS_SKIP_DRIFT_CHECK=1 git push
   ```
   實際牆鐘時間 67.62 秒,超過設計文件寫定的「check 總預算 60 秒」「每個分支各自一個 60 秒預算」(`Projects/存量漂移防線_計劃.md:62`、`:165`)約 13%,而且是先把 60 秒燒完才印出「判不了」,不是在 60 秒那一刻就攔下來。
5. 這不是人為構造的邊界:`_lens_push_base`(scripts/lumos:30106)對「新分支首推」(`_ZERO_SHA_RE` 命中)或「起點在本機找不到」(force-push)且找不到主線追蹤時,明文退回 `_EMPTY_TREE_SHA`(從空樹算,等同全歷史 diff)。drift-check 透過 `_note_audit_resolve` 共用同一支起點判法。這正是本次改動的上一個提交要修的同一類場景(`a2316395 fix: 新分支第一次推送或 force-push 後,推送前的檢查不再整批放過`)——note-audit/home-check 那條線已經處理過「首推=全歷史」的代價問題,但 drift-check 沿用了起點判法卻沒有繼承對應的時間界限。
6. 對照:設計文件〈做法〉第 0 節本身明寫「check 只評估這次推送可能改變結果的行…git 呼叫次數不隨條件數成長」(`Projects/存量漂移防線_計劃.md:164`),且 r1/r2 設計審已把「判不了與超時的回傳語意…總預算」列為「併發」「外家」席折入的項目(`Projects/存量漂移防線_計劃.md:191`、`:194`)——即這個問題在設計審已經被點名過、據稱已處理,但目前實作的 deadline 檢查點放置位置沒有真正把總時間夾在 60 秒內,是設計意圖與實作之間的落差,不是未審過的新洞。
7. 對照:`_nodehome_cat_blobs` 本身的設計初衷是用一次批次行程取代逐檔 `git show`(200 支衝突檔實測從 13.5 秒降到一次行程,見 scripts/lumos:23014-23020 的說明),所以真正貴的地方不在建整份樹這一步,而在 `_notes_status_flipped` 對每篇候選筆記逐篇起多個 git 子行程這段——這段完全不受 60 秒預算保護。

file: `scripts/lumos:30135`(`_lens_git` 單次 `timeout=20`)
file: `scripts/lumos:23014`(`_nodehome_cat_blobs` 內部獨立 `timeout=60`,不吃外層 deadline)
file: `scripts/lumos:30106`(`_lens_push_base` 找不到主線時退回 `_EMPTY_TREE_SHA`)
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:62`(「check 總預算 60 秒」)


## F2 表態檔(drift-acks.jsonl)追加沒有跟其他治理帳寫入者共用鎖——已知風險,已在本次改動裡揭露並定了回頭條件,非新增盲點
severity: minor
blocking: 否 — 風險已被本次改動自己寫進既有 Issue 並掛了日期回頭條件,不是靜默引入;且沿用專案既有的「append + 讀回自驗」慣例(`_jsonl_append_verified`),不是這次才出現的新寫法
引句:「又多兩個寫入者:表態檔(一行一筆,追加後讀回自驗,但沒跟別的寫入者共用鎖)」

1. `cmd_drift_ack`(scripts/lumos)直接對 `governance/drift-acks.jsonl` 呼叫 `_jsonl_append_verified`(open "a" 追加 + 重開檔讀回驗證有沒有那個 token),沒有拿 `_vault_write_lock` 或任何鎖;`_gate_event_or_warn(root, "drift-check", "acked", ...)` 走的是治理帳既有的通用寫入器,同樣不共用鎖。這點跟брief點名的疑慮一致。
2. 但這不是本次改動遺漏、事後才被我發現的問題:這次改動本身把它寫進既有的 `Issues/治理帳多個寫入者都沒上鎖.md`〈現在怎麼繞〉段,新增一句「2026-09-28 [[Systems/存量漂移守衛]] 又多兩個寫入者:表態檔(一行一筆,追加後讀回自驗,但沒跟別的寫入者共用鎖)與 drift-check 閘事件(走通用寫入器);2026-10-11 回頭看時一起算。」——文字精確對到程式碼行為(追加後讀回自驗=`_jsonl_append_verified` 的實作;沒共用鎖=真的沒共用鎖),而且那篇 Issue 本來就有 `REVISIT:2026-10-11` 一行,符合 CLAUDE.md 鐵則 4「承認風險要附回頭看的條件」的格式。
3. 併發後果本身也偏低:`_jsonl_append_verified` 靠 `open(path,"a")` 的 O_APPEND 語意加上寫後讀回驗證(不是靠鎖),兩個表態同時追加最壞情況是各自一行都寫進去、彼此不覆蓋(append 模式下不是 read-modify-write);`cmd_drift_check` 讀表態檔一律讀「被推送頂端提交裡」已提交的版本(`_drift_load_acks(root, tip)` 用 `_nodehome_cat_blobs` 讀 git blob),不是讀工作目錄檔案,所以 `drift ack` 寫入中的工作目錄檔案跟同時跑的 `drift check` 之間沒有交互作用;唯一會讀工作目錄表態檔的是 `lumos drift scan`(手動健檢指令,不擋、不寫帳),就算讀到部分寫入的行,壞行會被 JSON parse 失敗擋掉、直接跳過,結果只是這次健檢少列一筆已表態,不會誤判成「已表態」而蓋過真發現。

file: `scripts/lumos:8257`(`_jsonl_append_verified` 定義,open "a" + 讀回驗證)
file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md`(本次改動新增那句 + 既有 `REVISIT:2026-10-11`)


## 已看,無 finding 的部分

- **guard plan/settle/abandon 拿寫入鎖的範圍**:三支都是「外層 `with _vault_write_lock(env.vault): return _xxx_locked(...)`」,而且 `_guard_plan_locked`/`_guard_settle_locked`/`_guard_abandon_locked` 內部所有實際寫入都用 `load_raw_for_edit`/`atomic_write_verify` 對磁碟現讀現寫(不是拿鎖之前就快取好的 `env.notes`),`cmd_guard_settle` 更明講「★狀態從磁碟重讀★:env 是指令開頭載入的,拿到鎖之前可能已經被另一個程序轉正了」並真的重讀 `gfields`。從讀到寫整段確實在鎖裡。新測試 `t_guard_commands_hold_vault_lock` 用 monkeypatch 在 `load_raw_for_edit` 讀家筆記那一刻斷言 `_VAULT_LOCK_HELD` 非空,涵蓋三支指令,這個結構性斷言足以在拿掉任一支的 `with` 時翻紅。
- **env 是鎖外載入的舊資料會不會被拿來做決定**:三支寫入函式裡「會被寫進檔案的內容」全部改成鎖內現讀,env 只用來做路徑解析(`env.find`),不影響寫入內容正確性。唯一例外是 `main()` 裡 `cmd_set` 改 status 成功後印「連帶待辦」那段(`_drift_print_followups(env, rel, ...)`),那段用的是鎖外載入的舊 `env`,但它只印一段建議文字、不寫檔、不擋(程式碼自己註明「只多印、不擋、不寫」),就算列出的待辦因為別的並發寫入而輕微過期,後果只是提示不夠新,不影響任何機械判定。
- **settle 兩步中間失敗與重跑**:`_guard_settle_home` 失敗會讓函式在第一步就回傳、不進第二步;第一步成功、第二步(`_guard_settle_record`)失敗時錯誤訊息明講「這次只補這一步」,重跑時 `_guard_formal_line` 偵測到家筆記已經是正式行就跳過第一步直接補第二步。新測試 `t_guard_settle_recovers_half_done` 手動把家筆記改成正式行、守衛紀錄留 `pending`,驗證重跑「只補守衛紀錄」且家筆記不再被動,並且已經 `pass` 時重跑印「已轉正,不用再做」回 0——這條路徑有測試覆蓋、行為符合宣稱。
- **兩個 settle 同時跑**:被 `_vault_write_lock` 序列化,先拿到鎖的做完轉正,後拿到鎖的重新從磁碟讀到 `status: pass` 便直接印「已轉正,不用再做」回 0,不會重複改寫或報錯。沒有找到真正雙行程同時起跑的整合測試(`t_guard_commands_hold_vault_lock` 是單行程用 monkeypatch 驗鎖持有,不是雙行程賽跑),但這條「讀到 pass 就提早返回」的邏輯不依賴行程身分,跟專案裡 `_excl_lock_try` 過期接手的既有模式同構,沒有具體會失敗的路徑可指,不升等成 finding。
- **doctor Z 段在大圖譜上的成本**:`_drift_doctor_lines` 只在已經載入記憶體的 `env.notes` 上跑迴圈(不額外起 git),對 guard 型驗證紀錄呼叫 `env_text`/`_notelines_regions` 純字串處理;唯一的 git 呼叫是 `_lens_git(root, "show", f"HEAD:{_NOTELINES_PREPUSH}")` 一次,判斷有沒有接線。這跟設計文件〈做法〉第 0 節「doctor Z 段:不評估條件…只讀筆記…唯一的 git 呼叫是判斷『有沒有接線』」的宣稱一致(`Projects/存量漂移防線_計劃.md`),沒有隨圖譜篇數額外增加 git 呼叫。
- **cat-file 批次讀的逾時與失敗路徑**:`_nodehome_cat_blobs` 逾時或子行程失敗時回 `None`,`_drift_tree_env` 據此回 `None`,`_drift_check_core` 把它算成「git 讀不出被推送頂端的筆記」歸進判不了(fail-closed,不會靜默放行)。這個失敗路徑本身正確,只是它跟 F1 共用同一顆「總預算沒有真正被夾住」的根因,所以計入 F1、不重複開一條。

## 圖譜鏡頭:LUMOS-IMPACT 固定席逐條判(3ba5eef5..b9ca00bb)

跑 `lumos impact --diff 3ba5eef5f17b5ffe8700bb9904966145ac2eea0c..b9ca00bbda322504c612f9301afe9c903086cabb` 列出 27 固定席 + top8,逐篇對照這份 diff:

- **Systems/guard-kill.md**(★家★,直接,★INVARIANT★):本次新增的 PITFALL 行「plan、settle、abandon 原本改家筆記都在寫入鎖外…現在三支各自從讀到寫整段拿鎖」與程式碼行為完全吻合(見上面「已看,無 finding」第一條的驗證);同一篇的 WHY 行描述 settle 改寫四種預告句、status/標籤/句子同一次寫入,也跟 `_guard_settle_record` 的實作一致。**不影響**——這篇原有的 ★INVARIANT★(guard kill rc 優先序、--json 模式輸出純淨)這次完全沒被碰到,本次只是替這篇補上準確描述新行為的段落。
- **Systems/lumos-cli-write.md**(★家★,直接,★INVARIANT★):這篇管的是 `set/append/remove/decision-*` 等八個寫入原語與 `_vault_write_lock` 本身;本次改動沒有動 `_vault_write_lock`、`atomic_write_verify`、`load_raw_for_edit` 的實作,只是新增呼叫端(`cmd_guard_plan/settle/abandon` 改成整段拿鎖、`cmd_set` 內部在 status 分支後掛一段印待辦)。**不影響**——這篇宣稱的「8 個寫入原語是專案層圖譜寫入的唯一安全路徑」「T1 寫後自驗 atomic」等合約沒有被改動,新呼叫端遵守既有介面(`with _vault_write_lock`、`atomic_write_verify`),沒有繞過。
- **Systems/lumos-cli-read.md**(★家★,直接,★INVARIANT★):管讀指令「零副作用」與 `load_vault`/`Env`。本次新增 `Env.from_texts`/`env_text`/`_note_from_text` 都是新增的記憶體讀取路徑,不改磁碟、不改既有 `load_vault` 對外行為(把原本內聯的解析邏輯抽成 `_note_from_text` 後原路徑呼叫結果不變)。**不影響**——`drift scan`/`drift check`/`drift exam` 都是唯讀指令,沒有新增寫入,符合這篇「14 個讀指令不改圖譜節點檔」的合約範圍(drift 系列不在那 14 個裡,但新指令同樣遵守零寫入慣例)。
- **Systems/reversibility-governance-ledger.md**(直接,★RISK·守衛面★):管治理帳與閘名單。本次把 `"drift-check"` 加進 `_KNOWN_GATES`,新增的 WHY 行明講這件事,而且這篇原有 KEY 行「lumos gov 唯讀彙整器,不合併寫入路徑(避 bash+python 多寫者搶檔 race)…dedup 在讀時做」——drift-check 的閘事件走既有 `_gate_event_or_warn` 通用寫入器,沒有另開一條寫入路徑。**不影響**,且與 F2 提到的表態檔議題一致收斂進既有 Issue,沒有繞過這篇的彙整器合約。
- **Systems/存量漂移守衛.md**(hop1,這次新開的家節點):`responsibility` 寫明管 `lumos drift` 家族、五種狀態一致檢查、`lumos set` 連帶待辦與 doctor Z 段,`about_code` 指到 `scripts/lumos`;內文提到「轉正預告句的比對跟 [[Systems/guard-kill]] 的 settle 改寫共用同一支,兩邊不能各寫一份」——程式碼裡 `_guard_planned_prose` 確實是 `_guard_settle_rewrite`(guard-kill 側)與 `_drift_guard_findings`(drift 側 c1)共用的唯一實作(scripts/lumos)。**不影響/相符**——這篇是本次改動自己的落點,內容與程式碼一致,唯一要指出的落差就是 F1(60 秒預算沒有被這篇或計劃文件的效能段完全兌現)。
- **Systems/測試假綠形態.md**(hop1,★INVARIANT★:「還原翻紅釘」必須配前置斷言證明現場成立):本次新測試 `t_guard_settle_recovers_half_done` 有明確「①前置:家筆記已是正式行、守衛紀錄還是 pending」斷言在修法斷言之前,`t_guard_commands_hold_vault_lock` 的 docstring 明寫「翻紅釘:把任一支的 `with _vault_write_lock` 拿掉 → 對應那條紅」。**不影響**——新測試遵守這篇的紀律,沒有落入清單裡列的假綠形態。
- 其餘 hop1/一般命中的節點(Systems/授權與歸屬、loop-convergence-recording、design-loop、pitfalls-code-loop、lumos-cli-lifecycle、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、doctor-irreversible-hint、check-r-guard、cochange-guard、lumos-refcheck、bound-tests-gate、canary-audit、slim-get-一行安裝、slim-install-安裝器、slim-uninstall-一行卸載、Projects/雙向門放行_計劃、Projects/規格落成可驗收條件_計劃、Projects/逃逸自動記_計劃、Systems/core-invariant-baseline、Systems/judge-severity-gate、Projects/公開精簡版_實作計畫、Projects/code側刪除傳播守衛_實作計畫、Projects/test-layers軟提醒_實作計畫、Systems/每支檔有家、Systems/規格閘):這些節點管的是安裝腳本、測試框架掃描、代碼審迴圈、可逆性標記、cochange 提醒等跟本次改的鎖/併發/預算邏輯不相交的子系統,只是因為 `about_code` 都指到同一支巨大的 `scripts/lumos` 檔而被 impact 掃進固定席(它們的合約段落沒有一條提到 `_vault_write_lock`、guard settle、`drift check` 或 `_notes_status_flipped`)。**批次判定:不影響**——本次改動沒有碰觸它們各自負責的程式區塊,逐篇檢查過摘要沒有跟併發/資源相關的合約被牽動。

## 總結

最高等級 major,blocking 共 1 條(F1);另有 1 條 minor 不 blocking(F2,屬本次改動自行揭露並掛了回頭條件的已知風險)。
