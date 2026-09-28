severity: major

白話總覽:這份 diff 大部分是「照抄鄰居寫法」的教科書範例——`_note_audit_resolve` 加兩個參數就讓存量漂移檢查沿用筆記內容審整套推送閘外殼、guard plan/settle/abandon 補鎖的手法跟 `cmd_set`/`_cmd_set_locked` 一模一樣、`_drift_config` 明講自己照抄 `_note_audit_config` 的讀法。但抓到兩處真的長出「另一套做法」的地方,都附了可以當場重現的指令與輸出。

## 問題一:分層與依賴方向

已看,無 finding。新碼的呼叫方向是單向的:`_drift_*` 家族呼叫既有的 `_guard_planned_prose`/`_guard_formal_line`/`_guard_home_of_fields`(scripts/lumos:11747 一帶)、`_note_audit_closed_plans`/`_notes_status_flipped`(scripts/lumos:24619 一帶重構後的共用函式)、`_lens_*`/`_nodehome_*`/`_ns_git` 這些既有的 git 工具層;反過來查了 `_guard_settle_locked`、`cmd_note_audit_check`、`cmd_set` 這些既有函式,沒有一處回頭呼叫 `_drift_*`。這跟 `_note_audit_closed_plans`/`_notes_status_flipped` 本來就混用 `_ns_git`+`_lens_*`+`_nodehome_*` 三個 git 工具層的既有慣例一致(scripts/lumos:24619-24645),不是新碼另開的混用方式。`cmd_drift_check`/`cmd_drift_exam` 走「不需要本機 Env、只吃 `--repo`」的分派(main() 裡 `args.cmd == "drift" and args.drcmd in ("check","exam")` 那段),`cmd_drift_scan`/`cmd_drift_ack` 走「需要本機 Env」的分派(main() 裡 T1 寫側那段),這個切法跟檔案原本「repo-only 指令在前、env-dependent 指令在 T1 寫側」的既有分區一致,不是新引入的第三種分派方式。

## 問題三:第二種做法(核心 finding)

### F1 doctor 的「閘健檢提醒」新開一種呈現方式,不計入既有統計、也不受既有截斷豁免

severity: major
blocking: 是 — 同一種「這道閘沒開/沒接 CI」的體檢提醒,在同一支 `run_doctor` 裡因為擺放位置不同,會不會被計進收尾統計、會不會被截斷成 3 例,行為不一致,且已用實際指令重現。
引句:「section("Z", "存量漂移(已經寫進去的句子,跟別處的狀態對不上了)")」

1. 既有慣例(三個閘 3/3 一致):`node_home` 的閘模式提醒(scripts/lumos:1032)、`_note_shape_doctor_lines`(scripts/lumos:1035)、`_note_audit_doctor_lines`(scripts/lumos:1040)都是在 `issues = 0`(scripts/lumos:1045)與 `def warn_soft`(scripts/lumos:1076)**都還沒定義之前**,用裸 `print()` 直接輸出、逐行不截斷——這是函式執行順序上的硬事實,不是巧合:這三段程式碼在檔案裡的位置早於 `issues`/`warn`/`warn_soft` 的宣告,物理上不可能去更動這兩個計數器。
2. 這份 diff 的 `_drift_doctor_lines`(存量漂移的 Check Z)反而接到 `section("Z", …)` + `warn_soft(_zl, …)` 這一組——`warn_soft` 內部 `_SOFT_CAP = 3`(scripts/lumos:1072)、`shown = list(lines) if _verbose else list(lines)[:_SOFT_CAP]`(scripts/lumos:1084),而且每次呼叫都會 `_soft["segs"] += 1; _soft["lines"] += len(lines)`,這兩個欄位驅動收尾那行「另有 N 段、共 M 條提醒沒算進上面那個數字」。
3. 實測重現:在乾淨的最小 vault(`docs/kg-knowledge`,3 篇 verification 帶 guards 欄、pass 狀態、留著四種預告句)跑
   ```
   python3 scripts/lumos --vault <vault> doctor
   ```
   輸出尾段:
   ```
   ⚠ 發現 6 個 issue (8 篇)
     ⚠ 另有 5 段、共 7 條提醒沒算進上面那個數字——它們不影響判定,但每一段剛才都印了
     看全部: lumos doctor --verbose
   ```
   其中 `[Z] 存量漂移(已經寫進去的句子,跟別處的狀態對不上了)` 那段(印出「12 筆(例:Verification/G1:18;Verification/G1:19;Verification/G1:25)」)就是被算進這「5 段/7 條」的其中一段;而同一次跑裡若 note-shape/note-audit 有東西要講,依第 1 點的程式順序,結構上不可能出現在這個「5 段/7 條」裡,也不會像 Z 段那樣把明細砍到只剩 3 個例子。
4. 這不是純風格差異:使用者只跑 `lumos doctor`(不加 `--verbose`)時,同樣是「這道閘的健檢細節」,note-shape/note-audit 永遠給全量,Z 給前 3 個例子 + 一句「lumos doctor --verbose 看全部」;而且 Z 段的存在與否會改變收尾那句「共 N 條」的措辭,note-shape/note-audit 不會。這是專案裡第一次出現「同類體檢提醒用第二套呈現規則」,跟同層最相似的兩個鄰居(note-shape、note-audit)不一致。
5. 補充:這個 Z 段的設計出自計劃筆記 [S14](docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md 第144行),明講「doctor 應開一段 Z」「照 doctor 的全靜默慣例」——查證後確認「全靜默」(全部是 0 就整段不印)這條確實跟既有 E5(check-revisit)一致,但「用 section+warn_soft 呈現、而不是用 note-shape/note-audit 那種不截斷的裸 print」這個選擇,計劃筆記裡沒有明講理由,也沒有對照過 note-shape/note-audit 這兩個同類提醒段的呈現方式——屬於程式碼推得出來的既有慣例,不受「RULE 挑戰程式碼」那條保護,以程式碼既有行為為準。

### F2 `_drift_plan_followups` 自己重建了一套 plan_refs 反向查找,繞過既有的 `build_typed_index`,而且踩中後者明講要避開的那個坑

severity: major
blocking: 是 — 已用實際指令+輸出重現:一組同名筆記會讓 `lumos set <計劃> status done` 靜默漏印本來該列的連帶待辦,沒有任何警告或錯誤。
引句:「if rel not in {env.resolve(link_target(x)) for x in as_list(pn.fields.get("plan_refs"))}:」

1. 專案裡已經有一支專門解「哪些筆記透過具名欄位(含 `plan_refs`)指向某節點」的既有反向索引:`build_typed_index(env)`(scripts/lumos:483),回傳 `rev={target_rel:[(source_rel,etype)]}`,而且 docstring 明講「同名無路徑 [[X]] 多篇候選 → ambiguous + 候選清單(**嚴禁靜默指第一篇——不走 env.resolve**,直接查 by_stem 候選數)」(scripts/lumos:489-490)。這支函式在 doctor 的 E3、圖譜渲染等至少 7 處被重複呼叫(scripts/lumos:1870、13361、15483、15515、15695、15810、15903),是專案裡「找誰連到我」的既有慣例入口。
2. 這份 diff 的 `_drift_plan_followups`(scripts/lumos:25248)要找「哪些 `type: verification` 的 `plan_refs` 指到這個計劃」時,沒有用 `build_typed_index(env)["rev"]`,而是自己重新掃一遍全部筆記、對每篇的 `plan_refs` 逐項呼叫 `env.resolve(link_target(x))`(scripts/lumos:25263)——這正是 `build_typed_index` 的 docstring 特別點名要避開的那支函式,原因是 `env.resolve` 對同名筆記會「取第一個」並只印一行 stderr 警告(`make_resolver` 的 `if len(hits) > 1: print(f"⚠ 同名筆記 {len(hits)} 個,取第一個: {hits[0]}", file=sys.stderr)`),不會擋、也不會讓呼叫端知道結果是猜的。
3. 實測重現(乾淨 vault,無 git 依賴):
   - 建三篇筆記:`Projects/退款.md`(`type: project`,要收尾的那篇)、`Issues/退款.md`(`type: issue`,同名但完全無關,資料夾字母序排在 `Projects`之前)、`Verification/V1.md`(`type: verification, status: pending`,`plan_refs: ["[[退款]]"]`,裸 stem 連結)。
   - 直接用 REPL 呼叫本次 diff 加的函式:
     ```
     env.by_stem.get('退款')                      # ['Issues/退款.md', 'Projects/退款.md']
     env.resolve('退款')                           # -> 'Issues/退款.md'  (取到的是無關的 Issue,不是要收尾的計劃)
     build_typed_index(env)['rev'].get('Projects/退款.md')   # -> None(正確:不靜默歸因)
     build_typed_index(env)['ambiguous']           # -> [('Verification/V1.md', '退款', 'plan_refs', ['Issues/退款.md', 'Projects/退款.md'])]  (正確:明確標成模糊)
     _drift_plan_followups(env, 'Projects/退款.md', 'done')   # -> []   ← 應該要列出 Verification/V1.md,卻是空的
     ```
   - CLI 端同一件事也重現:
     ```
     python3 scripts/lumos --vault <vault> doctor            # [G] 段自己就報「有 1 組筆記同檔名:退款: Issues/退款.md , Projects/退款.md」
     python3 scripts/lumos --vault <vault> set Projects/退款 status done
     ```
     第二個指令的實際輸出只有:
     ```
     ✓ set Projects/退款.md: status 已改成 done(狀態標籤 status/* 也同步改了)
     ```
     沒有任何「連帶待辦」提示,也沒有印出同名筆記的模糊警告——`Verification/V1.md` 這篇還 pending、`plan_refs` 真的指著這個計劃的驗證紀錄,就這樣被靜默漏掉。
4. 這不是單純「多繞一步」的效率問題:`build_typed_index` 已經把「同名候選」這個邊界案例用 `ambiguous` 明確標出來、且它的 `rev` 對模糊目標本來就不建索引(所以不會誤歸因),`_drift_plan_followups` 自己重寫的版本兩種保護都沒有,是專案裡第一次在「推送閘/連帶待辦」這種要拿來做判斷的場合(相對於 scripts/lumos:13974 那種純粹給圖形視覺化用、標錯了也只是連錯一條顯示用邊的低風險場合)繞過 `build_typed_index`,直接走它的作者明講要避免的 `env.resolve` 路徑。

## 問題二:命名與錯誤處理

已看,無 finding。`_drift_config`(scripts/lumos 一帶)docstring 直接寫「照 `_note_audit_config` 的讀法(每道閘各自一支,既有慣例)」,且兩者的分支結構、警告文字模板(`"設定檔的 X 不是物件…"`、`"X.gate 只能是 block/warn/off…"`)、回傳形狀 `(gate, warnings)` 逐項比對一致。`cmd_drift_check` 的錯誤前綴「擋下:」/「存量漂移檢查:」、`_gate_event_or_warn(root, "drift-check", "blocked"/"warned", …, hard=True, nodes=…)` 的呼叫形狀,跟 `cmd_note_audit_check` 的「擋下:」/「筆記內容審:」、`_gate_event_or_warn(root, "note-audit", …)`(scripts/lumos:25057-25060)逐項對得上。`cmd_guard_plan`/`cmd_guard_settle`/`cmd_guard_abandon` 改成「公開函式只拿鎖轉呼叫 `_guard_*_locked`」,跟 `cmd_set`/`_cmd_set_locked`(scripts/lumos:14502-14503)是同一種切法,只是前綴用 `_guard_` 不用 `_cmd_guard_`,這跟 guard 家族原本所有私有函式都用 `_guard_` 前綴(`_guard_plan_check`、`_guard_find`、`_guard_touches`)的既有命名一致,不是不一致。argparse 的 `dr_*` dest 前綴跟 `na_*`(note-audit)、`ns_*`(note-shape)、`hm_*`(home)一個模子。`_KNOWN_GATES` 新增 `"drift-check"` 時附的日期註解格式跟上一行 `"note-audit"` 的註解格式相同。

---
最嚴重等級 major,blocking 共 2 條(F1、F2)。
