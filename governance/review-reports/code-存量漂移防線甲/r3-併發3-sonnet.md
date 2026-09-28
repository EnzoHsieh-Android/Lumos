severity: blocker

白話總覽:這輪改動想解決兩個問題——①存量漂移檢查(drift check)在算「這次推送要不要擋」時,要在 60 秒內跑完,跑不完的路要看剩下的時間再決定敢不敢繼續;②筆記內容審(note-audit)的「計劃收尾」偵測以前遇到批次讀失敗會悄悄當成「沒事發生」,這次改成老實承認「判不了」。動手驗這兩塊時發現:①的「最壞只多一次呼叫的時間」這句話跟實測對不上,單一候選最壞可以多兩次;②的修法把 note-audit 原本只在「git 完全打不開」才會觸發的整段跳過,擴大成「任何一次批次讀失敗」都會觸發,而且會整段放行、不看 block/warn 設定,用一個和被跳過內容完全無關的失敗就能悄悄放行一次不該放行的推送;另外新增的 scan 判不了計數會寫一筆治理帳,跟這個指令自己的說明與圖譜裡「讀指令不寫帳」的既有决定衝突。

## F1 note-audit 的批次讀失敗被放大成整段推送前檢查靜默放行(該擋沒擋)

severity: blocker
blocking: 是 — 完全無關的新寫內容因為另一篇候選筆記的一次批次讀失敗而沒被審到就放行,屬於「該擋沒擋」。

引句:「★不能當成沒有狀態翻轉★(代碼審 r2 外家席:原本批次讀失敗被轉成空序列,推送閘與完成審都靜默放行)。」(`scripts/lumos:24517`)

1. `_note_status_seq`(`scripts/lumos:24515`)這次改成:`_nodehome_cat_blobs` 批次讀任何一次失敗(逾時、subprocess 掛掉、非 0 返回碼、輸出解析不出來)就回 `None`(`scripts/lumos:24529-24531`、`scripts/lumos:24567-24569`)。
2. `_notes_status_flipped`(`scripts/lumos:24484`)在候選迴圈裡「只要有一個候選 `seq is None` 就整支函式回 `None`」(`scripts/lumos:24508-24509`),這段迴圈邏輯本身不是這輪新加的,但這輪把「批次讀失敗」也接進了會觸發它的原因清單。
3. `_note_audit_items`(`scripts/lumos:24573`)呼叫 `_note_audit_closed_plans` 拿到 `None` 就整支函式回 `None`(`scripts/lumos:24581-24582`)——這一步跟「新寫的一般行」的稽核（`_notelines_new`）完全無關,卻會被拖著一起放棄。
4. `cmd_note_audit_check` 拿到 `got is None` 直接印「筆記內容審:git 算不出這次的筆記行,跳過(fail-open)」並回 `0`(`scripts/lumos:25107-25109`),**不管 `note_audit.gate` 是 `block` 還是 `warn`**,也不管這次推送裡有沒有真的沒被判定過的新行。
5. 重現(在乾淨臨時 repo,同一個提交裡①把一份計劃收尾成 done②在完全無關的另一篇筆記新寫一行未判過的內容):
   - 正常情況:`rc=1`,清楚列出 6 行未涵蓋,含 `docs/kg-knowledge/Systems/A.md:18  [沒判過]  這是全新沒判過的一行內容`。
   - 只讓「計劃收尾候選」的第一次批次讀(`_nodehome_cat_blobs`)失敗一次(模擬瞬斷,其餘批次讀照常):`rc=0`,那行「這是全新沒判過的一行內容」完全沒有出現在任何輸出裡,直接被放行。
   - 腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/repro_na_failopen.py`,實跑輸出見上(`rc= 1` → `rc= 0`)。
6. 舊版(這輪改之前)同一種失敗只會讓 `states = [_note_audit_status_of(b)[1] for b in (blobs or [])]` 退化成空序列——那個候選自己的「計劃收尾完成審」偵測不到,但 `_notes_status_flipped` 不會整支回 `None`,`_note_audit_items` 照常跑,新寫的行(包括這次重現裡的 A.md 那一行)照樣會被審到。這輪修法把「壞影響範圍」從「一個候選的完成審偵測失準」擴大成「整段推送前檢查完全跳過」。
7. ⚠ 觸發條件不只是「瞬斷」:`_nodehome_cat_blobs` 本身有一條既有規則——candidate 的 `specs`(`版本:路徑`)裡只要有任何一個路徑含換行字元就直接回 `None`(`scripts/lumos:23061-23062`,不在這次 diff 內、原本就有)。這代表只要範圍裡有一篇「目前是 done/superseded 的 project 筆記」在歷史上任一版本的路徑含換行字元(git 允許檔名含換行),就能穩定重現整段放行,不是只能靠運氣等瞬斷。這一點未在本輪新增測試裡覆蓋,標記待查證,不影響上面第 5 點已經用瞬斷模擬出的具體重現。

## F2 併發席自己的「最壞只多一次呼叫的時間」對不上實測,單一候選最壞多兩次

severity: major
blocking: 是 — 這輪修法的賣點就是把推送前掛鉤的最壞延遲收斂到「預算 + 一次呼叫」,但實測顯示同一位候選裡有兩個不看預算的單次 git 呼叫,文件宣稱的上界是錯的。

引句:「已經開始的那一次 git 呼叫不會被打斷(單次最多 20 秒,批次讀以剩下的預算為上限),所以最壞會比預算多出一次呼叫的時間(代碼審 r2 併發席」(`scripts/lumos:25465-25467`;同一句在 `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:21` 也這麼寫)

1. `_note_status_seq`(`scripts/lumos:24515`)對「有 `base_where`」的候選(也就是一般有明確合併基準的推送,不是文件原本要修的「新分支第一次推送找不到主線」那個特例)依序做:
   - `_ns_git(repo_root, "log", "--follow", ...)`(`scripts/lumos:24524`)——固定 20 秒上限、不看剩餘預算(`_ns_git` 內部經 `_lens_git`,`timeout=20` 寫死,`scripts/lumos:30330-30332`)。
   - 再呼叫 `_note_base_status`(`scripts/lumos:24535`),裡面又有一個**同樣不看剩餘預算**的 `_ns_git(repo_root, "diff", "--name-status", ...)`(`scripts/lumos:24564`,改名偵測),固定 20 秒上限,完全沒有被 `_to()` 算出來的剩餘時間限制或跳過。
   - 之後才是有拿到剩餘預算當 `timeout` 的批次讀(`scripts/lumos:24529`、`scripts/lumos:24567`)。
2. 也就是說單一候選裡有兩個「單次 git 呼叫」不受預算節流,不是文件說的一個。
3. 重現(monkeypatch `_ns_git`,讓 `--follow` 那次呼叫吃掉 0.5 秒、`--name-status` 改名偵測那次呼叫再吃掉 0.5 秒,`deadline` 只給 0.3 秒):
   - 實際耗時 1.021 秒(對 0.3 秒的預算),兩次 git 呼叫都被打下去(`log` 在 t=0.0s,`diff` 在 t=0.511s)。
   - 腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/repro_budget_overrun.py`。
4. 換算到真實 git(單次上限 20 秒):同一位候選在極端情況下可以讓 `_drift_check_core` 超支到接近 40 秒,而不是文件宣稱的「一次呼叫」(≈20 秒)。這條 PITFALL 本身是這輪(代碼審 r2 併發席)剛寫進圖譜的,對不上實測,屬於「筆記跟程式碼對不上、程式碼答得出來」的那種——已按 CLAUDE.md 規則以程式碼實測為準寫這條 finding,而不是拿筆記反過來裁程式碼。
5. `_notes_status_flipped` 對「候選之前的預算檢查」確實有做(`scripts/lumos:24502-24503`,呼叫 `_note_status_seq` 前先看一次 `deadline`),這一步是對的,值得肯定;問題出在 `_note_status_seq` **內部**還藏著上面第 1 點那兩個呼叫。

## F3 `lumos drift scan` 違反自己的說明與既有「讀指令不寫帳」決定

severity: major
blocking: 是 — 文件字面承諾「不寫帳」,程式碼卻在特定情況下寫帳,而且沒有旗標可以關掉這個副作用,跟圖譜裡既有的讀寫分軌決定衝突。

引句:「解不開的筆記列成「判不了」、記一筆 degraded([S2];代碼審 r2 外家席:原本修復清單會靜默漏掉它們)」(`scripts/lumos:25716`)

1. `cmd_drift_scan`(`scripts/lumos:25698`)新增:只要 `bad`(不是 UTF-8 或讀檔失敗的筆記)非空,就呼叫 `_gate_event_or_warn(root, "drift-check", "degraded", ...)`(`scripts/lumos:25719`),寫進 `docs/.governance-log.jsonl`,不看有沒有 `--json`、也沒有任何旗標可以關掉。
2. 但 `HELP_WHEN` 裡這個指令自己的說明沒有改、還是寫「不擋、不寫帳」:`"drift scan": "健檢整份圖譜(或某個提交)跟狀態對不上的地方,產待修清單;不擋、不寫帳。"`(`scripts/lumos:33938`)。
3. 這跟圖譜既有的決定衝突。`Systems/lumos-cli-read.md` 的 d1 決策:「讀寫原語嚴格分軌——14 個讀指令不改圖譜節點檔(2026-08-24 審計統一計數)(context/show 寫 best-effort usage-log 事件帳、doctor --ci 寫 governance-log,其餘純讀……)」(`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:50`)——明確列出「會寫治理帳」的只有兩種例外:`context`/`show`(寫的是 usage-log,不是 governance-log)、`doctor --ci`(寫 governance-log)。`drift scan` 兩者都不是,`lumos-cli-write.md` 也沒有把它列進寫入原語。`Systems/reversibility-governance-ledger.md` 另一段也把 governance-log 的來源記成「governance-log(doctor)」(`docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:29`),同樣沒算進 `drift scan`。
4. 重現:在乾淨臨時 repo 寫一篇非 UTF-8 的 `Verification/Bad.md` 並提交,執行前 `.governance-log.jsonl` 不存在;跑 `lumos --vault docs/kg-knowledge drift scan --at HEAD` 後,`.governance-log.jsonl` 出現一行 `{"gate": "drift-check", "kind": "degraded", ..., "note": "scan 判不了 1 篇(不是 UTF-8 或讀不了)", ...}`。腳本:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/repro_scan_ledger.py`。
5. `_gate_event_or_warn` 寫入端沒有去重(`scripts/lumos:973-980`,去重留給讀時的 `lumos gov`),所以同一批未讀懂的筆記只要重跑 `drift scan` 就會再寫一筆——這個指令原本被定位成「隨時可以健檢一下」的唯讀工具,現在每次隨手跑一次都會在共用治理帳裡多留一行。
6. 這一點不是這條 gate 名沒登記的問題——`"drift-check"` 已經在 `_KNOWN_GATES` 裡(`scripts/lumos:6679`),`Systems/節點範圍與索引守衛.md` 的 ★INVARIANT★(閘名要登記進 `_KNOWN_GATES`)沒有被違反,問題純粹是「這個指令根本不該寫帳」。

## 圖譜鏡頭:LUMOS-IMPACT e72324b8..e415890264bf52f1b1b07247ab65dd5d1ce23a54 逐節點判定

已看,`lumos impact --diff e72324b8..e4158902` 跑出的固定席(26)+top(8)清單逐條判過:

- `Systems/lumos-cli-read.md` ★INVARIANT★ — **有 finding,見 F3**:d1「讀指令純讀,只有 context/show(usage-log)與 doctor --ci(governance-log)例外」被 `drift scan` 打破。
- `Systems/reversibility-governance-ledger.md` ★RISK·守衛面★ — 已看,無新 finding(它是 `lumos gov` 的唯讀彙整規則,不決定誰能寫帳;governance-log 來源被記成「(doctor)」跟 F3 是同一件事的另一個佐證,已併入 F3,不重複開)。
- `Systems/存量漂移守衛.md`(★家★ hop1)— 已看,無 finding 之外多一點:摘要本身的 PITFALL(21 行)已在 F2 指出跟實測不符,但那不是「這份改動破壞了這篇筆記的合約」,是「這篇筆記這次自己寫錯了自己的上界」——依 CLAUDE.md「PITFALL 是線索,程式碼答得出來時以程式碼為準」處理,已在 F2 寫清楚。
- `Systems/guard-kill.md` ★INVARIANT★ — 已看,無 finding:兩條 ★INVARIANT★(guard kill 的 rc 優先序、`--json` 輸出純淨度,`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:20-21`)這輪 diff 完全沒碰;18/19 行記的「整段拿鎖」「做到一半可補完」在這輪的測試(`t_guard_commands_hold_vault_lock`、`t_guard_settle_recovers_half_done`)裡照樣綠,且我自己追過 `_guard_settle_home`(`scripts/lumos:11991`)的兩個新擋點(`scripts/lumos:11999-12007`)都在任何 `atomic_write_verify` 之前 `return False`,擋下時家筆記與守衛紀錄都沒被動過,跟 `t_drift_code_review_r2_regressions ②③` 的斷言一致(已實跑該測試,12 個檢查全過)。
- `Systems/loop-convergence-recording.md`、`Systems/pitfalls-code-loop.md`、`Systems/design-loop.md`、`Systems/授權與歸屬.md`、`Systems/測試假綠形態.md`、`Systems/lumos-cli-lifecycle.md`、`Systems/節點範圍與索引守衛.md`、`Systems/lumos-deinit.md`、`Systems/check-r-guard.md`、`Systems/check-t-sentinel.md`、`Systems/doctor-irreversible-hint.md`、`Systems/cochange-guard.md`、`Systems/lumos-refcheck.md`、`Projects/雙向門放行_計劃.md`、`Systems/slim-uninstall-一行卸載.md`、`Systems/bound-tests-gate.md`、`Systems/canary-audit.md`、`Systems/slim-get-一行安裝.md`、`Systems/slim-install-安裝器.md`、`Projects/規格落成可驗收條件_計劃.md`、`Projects/逃逸自動記_計劃.md`、`Systems/core-invariant-baseline.md`、`Systems/judge-severity-gate.md`、`Projects/公開精簡版_實作計畫.md`、`Projects/code側刪除傳播守衛_實作計畫.md`、`Systems/lumos-cli-write.md`、`Systems/每支檔有家.md` — 已看(逐篇對關鍵字 drift/guard settle/note-audit/governance-log/undecodable/預算 掃過,`Systems/lumos-cli-lifecycle.md`、`Systems/pitfalls-code-loop.md`、`Systems/節點範圍與索引守衛.md` 有命中但命中的段落分別是 vendor 白名單、code-loop 自己的檔案大小逾時預算、check-s5/s7 閘名登記,都是別的機制,跟這輪 drift/note-audit 的改動無關),無 finding:這些節點各自管的是本次 diff 沒有動到的檔案範圍或機制,`scripts/lumos`/`scripts/test_lumos.py` 命中它們只是因為它們是同一支巨檔的「家」而被 impact 掃描的相似度算法帶進來,合約段落本身跟 guard settle / drift check / note-audit closed-plans 三塊都不相交。
- `Projects/存量漂移防線_計劃.md`、`Projects/筆記內容審_計劃.md`、`Systems/筆記內容審.md`(★家★) — 已看,無新 finding:`筆記內容審.md` 的 WHY(`docs/lumos-toolchain-knowledge/Systems/筆記內容審.md` 摘要那行)已經誠實寫了「2026-09-29 起逐提交讀 status 時批次讀失敗回『算不出』……完成審照既有判不了的規矩跳過並印原因」——這篇筆記**準確描述了新行為**,沒有跟程式碼對不上;F1 挑的是這個「新行為本身」的設計風險(放行範圍被放大到跟失敗來源無關的內容),不是「筆記寫錯了」,兩件事分開記,不重複算成圖譜矛盾。

最嚴重等級 blocker,blocking 共 3 條(F1、F2、F3)。
