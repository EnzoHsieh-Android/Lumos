severity: minor

## 方法說明

本鏡頭只審「甲」範圍([S3][S4][S5][S6][S7][S8][S19] 全部、[S1][S2][S13][S14] 的甲部分)。除逐字讀兩份凍結 diff 與設計稿外,在唯讀複本 `clone-ns`(已是套用這份 diff 後的快照)跑了：
1. `python3 scripts/test_lumos.py -k drift`(105 passed)、`-k guard_settle`(28 passed)、`-k guard_commands_hold`(4 passed)、`-k set_plan_closed`(7 passed)——本次新增/改動測試全綠。
2. `-k note_audit`(173 passed)、`-k guard_kill`(50 passed)、`-k reversibility`(13 passed)、`-k doctor_s5/s6/s7`、`-k soft_sections`、`-k revisit`——既有合約測試(筆記內容審、guard-kill、reversibility-governance-ledger、節點範圍與索引守衛)全綠,沒有被這次改動壓壞。
3. 對三個關鍵斷言各做一次「複製 repo → 手動還原成 diff 前的行為 → 重跑對應測試」的翻紅釘實測(不是照抄 diff 裡寫的翻紅釘說明,是自己動手拆):
   - 把 c1/settle 共用的行首比對(`s.startswith("為什麼還不做:")`)改成子字串比對 → `t_guard_settle_rewrites_planned_prose` 的④⑤斷言真的翻紅(印出「預告當時為什麼還不做」被 c1 誤判)。
   - 把 `cmd_guard_settle` 的 `with _vault_write_lock(env.vault):` 拿掉 → `t_guard_commands_hold_vault_lock` 的②斷言真的翻紅(`[False, False, False]`)。
   - 把 `_drift_c3_hit` 的 `override` 參數拿掉不用 → `t_set_plan_closed_lists_followups` 的③斷言真的翻紅(V2 混進連帶待辦)。
   三次都成功翻紅,判定這批綁定測試不是假綠、真的驗到條款說的行為。改動過的複本用完即刪,沒有留在任何原始 repo 裡。

## 條款逐條(甲部分)

- [S3][S4][S5][S7][S8][S19]:已看,無 finding。核對 `scripts/lumos` 裡 `cmd_guard_plan`/`_guard_plan_locked`、`cmd_guard_settle`/`_guard_settle_locked`/`_guard_settle_home`/`_guard_settle_record`、`cmd_guard_abandon`/`_guard_abandon_locked`、`_guard_planned_prose`/`_guard_settle_rewrite`/`_drift_guard_findings`、`_drift_state_findings`/`_drift_c3_hit`/`_drift_check_core` 的實作,行為跟條款文字逐項對得上(見上方翻紅釘實測)。
- [S6]:已看,無 finding。`lumos set` 分派處 `rc == 0 and args.key == "status"` 才印連帶待辦、`_drift_print_followups` 只呼叫 `print`,沒有任何寫入呼叫;`_drift_plan_followups` 對 Issue 與 c3 同集合分別收集,測試涵蓋「不是計劃」「不是收尾狀態」兩種不印的情形。
- [S1][S2][S13][S14](甲部分):已看,無 finding。`cmd_drift_check`/`_drift_report_must` 的 block/warn/off/略過/淺層 clone 分支、`_drift_check_core` 對「判不了」回傳算要處理、`cmd_drift_exam`/`_drift_exam_one` 對 commit/status_replay/current_state 三種考法與 mechanism1_experiment 略過、`_drift_doctor_lines` 的全靜默與「只在接線後才印」都跟條款文字一致,且都被對應測試蓋到。

## 存量漂移守衛.md 與改到的既有筆記

已看,無 finding,逐句核對如下:
- `Systems/存量漂移守衛.md` 的「TEST:」清單九支測試,全部存在於 `scripts/test_lumos.py` 且全綠(見上)。
- 「跟設計稿不一樣的兩處」屬實且描述精確:
  1. doctor 的 gate≠block 提醒只在 `wired`(推送前掛鉤裡出現 `drift check` 標記)為真時才印——`_drift_doctor_lines` 裡那段訊息確實包在 `if wired:` 區塊內,不在外層。
  2. exam 的誤報只算「題目那篇以外」的發現——`_drift_exam_one` 的 `others_m`/`others_l` 用 `f["path"] != note` 過濾,跟敘述一致。
- `Systems/guard-kill.md` 新增的 WHY/PITFALL 行:內容(行首前綴比對、含反引號、status 與句子同一次寫入、settle 分兩步可補完、`t_guard_commands_hold_vault_lock`/`t_guard_settle_recovers_half_done`)跟程式行為一致,已用翻紅釘驗過其中兩條。
- `Systems/reversibility-governance-ledger.md` 新增的 WHY 行(閘名單加 `drift-check`、放行不寫帳、doctor Z 段也不寫):`_KNOWN_GATES` 確實多了 `drift-check`(且 `stats: 原始碼 gate 字面值全在 _KNOWN_GATES` 測試綠);`cmd_drift_check` 只在 `must` 或 `unknown` 非空時才呼叫 `_drift_report_must`(才會落帳),純放行路徑沒有呼叫 `_gate_event_or_warn`;`_drift_doctor_lines` 全程只呼叫 `_lens_git`/`print`,沒有任何寫治理帳的呼叫。
- `Systems/筆記內容審.md` 新增的 WHY 行(`_notes_status_flipped` 共用、`_note_audit_resolve` 的 gate/mark 改由呼叫端傳入):核對 `_note_audit_closed_plans` 改寫後對舊呼叫點是純委派、行為不變(靠 173 條既有 note-audit 測試全綠佐證),`_note_audit_resolve` 的新參數都有預設值,舊呼叫點(3 個位置參數)行為不變。
- `Issues/治理帳多個寫入者都沒上鎖.md` 新增的句子(存量漂移守衛多兩個沒共鎖的寫入者:表態檔、drift-check 閘事件):核對 `_jsonl_append_verified`(governance/drift-acks.jsonl 的寫入器)只用 `open(path, "a")` 追加+讀回自驗,沒有任何鎖;`_gate_event`(drift-check 閘事件用的通用寫入器)同樣只是 `open(..., "a")`,跟既有 `.governance-log.jsonl` 的其他閘共用同一個無鎖寫入器——敘述精確。

## 圖譜鏡頭:LUMOS-IMPACT 固定席逐條判

`lumos impact --diff 3ba5eef5..b9ca00bb` 列出的固定席多數是「scripts/lumos 有改動就會列出」的通用治理檢查清單,跟本次改動的具體行為無關;抽核如下,均判「不影響」:
- `Systems/lumos-cli-read.md`(search 排除 superseded 合約):本次沒有碰 `cmd_search`/`_search` 任何路徑,不影響。
- `Systems/lumos-cli-write.md`(`set` 對 valid_under/revalidate_when 等欄位的整欄覆寫合約):`cmd_set` 函式本體一行未改,只在 `main()` 分派處呼叫成功後多印連帶待辦,不影響原合約。
- `Systems/lumos-cli-lifecycle.md`(CLAUDE.md re-inject byte-equal 合約):本次沒有碰任何 reinject/vendor 相關程式碼。
- `Systems/授權與歸屬.md`(★INVARIANT★ 主程式檔頭要有 SPDX+MIT 全文、授權檔不得進 `_VENDORED_TOOLKIT`):核對 `scripts/lumos` 檔頭 SPDX 區塊完整無缺(diff 沒有動這段);本次沒有新增任何檔案進 `_VENDORED_TOOLKIT` 或授權相關清單。
- `Systems/測試假綠形態.md`(bug 修復類翻紅釘要配前置斷言證明現場成立):新測試多半是新功能測試而非「還原修法」型,但 `t_guard_settle_rewrites_planned_prose`/`t_guard_settle_recovers_half_done` 都各自帶「①前置」斷言證明現場成立,精神上有遵守;三次手動翻紅釘也都成功印出具體的失敗現場(不是空紅)。
- `Systems/節點範圍與索引守衛.md`(doctor S5/S6/S7 段位置敏感、插入位置本身是改動):新增的 Check Z 段插在既有 REVISIT 段(check-revisit)與 E3 之間,不在 S5/S6/S7 的區段內;`-k doctor_s5/s6/s7`、`-k soft_sections`、`-k revisit` 全數綠,證實插入沒有波及這些位置敏感的測試。
- `Systems/lumos-deinit.md`、`Systems/check-t-sentinel.md`、`Systems/check-r-guard.md`、`Systems/cochange-guard.md`、`Systems/lumos-refcheck.md`、`Systems/core-invariant-baseline.md`、`Systems/judge-severity-gate.md`、`Systems/每支檔有家.md`、`Systems/規格閘.md`、`Systems/bound-tests-gate.md`、`Systems/canary-audit.md`、`Systems/loop-convergence-recording.md`、`Systems/design-loop.md`、`Systems/pitfalls-code-loop.md`、`Systems/doctor-irreversible-hint.md`:讀過摘要與合約行,本次改動完全沒有碰觸這些節點管的程式路徑(deinit/refcheck/cochange/kill 平台判定/spec-gate/code-loop/canary/loop 收斂帳/不可逆提示),判「不影響」。

## F1 `lumos drift exam --probes` 這個旗標目前是死參數

severity: minor
blocking: 否 — 只是使用者可能誤以為它有作用,不影響推送閘的判定、不影響現有考卷分數,也有配套訊息說明 probe 題目還沒做
引句:「dre.add_argument("--probes", dest="dr_probes", default=None, metavar="改寫檔")」

1. `main()` 把 `--probes` 解析成 `args.dr_probes`,並傳進 `cmd_drift_exam(args.dr_exam, args.dr_repo, probes=args.dr_probes, ...)`(`scripts/lumos` 對應處)。
2. `cmd_drift_exam(exam, repo, probes=None, at=None, history=None, as_json=False)` 的函式本體(到 `_drift_exam_load`/`_drift_exam_history`/逐題呼叫 `_drift_exam_one` 那一段)完全沒有再讀 `probes` 這個區域變數一次——`grep -n "probes" scripts/lumos` 全檔只有 3 處:argparse 定義、dispatch 傳參、函式簽章,函式體內 0 處使用。
3. 設計稿〈做法〉第 0 節把 `--probes <改寫檔>` 列進 `lumos drift exam` 的正式指令形狀,且〈做法〉第 3 節說明它要餵給 A7/B1–B4(乙的題)。由於這份 diff 只做甲,`exam_event == "probe"` 那類題目會在 `_drift_exam_one` 直接落入「略過:考法 probe 還沒做或沒有失效提交」分支——訊息本身有講清楚,所以使用者不會被誤導成「傳了 --probes 就考到乙」;但旗標本身現在是純裝飾,對任何輸入都不報錯、也不做任何事,是一個新寫的、沒被任何測試覆蓋到的死參數。
4. 建議(非阻塞):乙那一批再實作 `--probes` 的讀取與套用時一併補測試即可;目前保留旗標本身不影響甲範圍的任何條款判定。

## 總結

最嚴重等級為本報告唯一一條 F1(不影響判定、只是死參數),blocking 共 0 條。三次獨立翻紅釘實測與既有 173+50+13+105+28+... 條相關測試全數維持綠燈,判定這份「甲」實作與 [S1][S2][S3][S4][S5][S6][S7][S8][S13][S14][S19] 條款、以及改到的五篇既有圖譜筆記與新開的 `Systems/存量漂移守衛.md` 敘述一致,沒有發現會假綠或波及既有合約(guard-kill、筆記內容審、reversibility-governance-ledger)的問題。
