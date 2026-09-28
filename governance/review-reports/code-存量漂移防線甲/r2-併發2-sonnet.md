severity: major

## F1 check 的預算:新文件字聲稱「最壞只多一次呼叫」,實測與讀碼都證明至少多 4 次不受 deadline 節制的 git 呼叫

severity: major
blocking: 是 — 這份 diff 新加的 `deadline`/`_left()` 預算機制,是為了修 r1 的「67 秒才判超過 60 秒預算」PITFALL 而加的;但它自己在 docstring 裡對「最壞多久」的新承諾是假的,會誤導往後設定 CI/掛鉤逾時的人,且在真的碰到慢 git(lock 競爭、大 repo、網路掛載)時,推送前檢查會比文件承諾的多卡上百秒,而不是一次呼叫的時間。
引句:「單次 git 呼叫本身最多 20 秒,所以最壞會比預算多出一次呼叫的時間」

1. `_drift_check_core`(`scripts/lumos:25417-25445`)裡真正被 `deadline` 節制的,只有 `_notes_status_flipped` 迴圈裡「每個候選之前」那一次檢查(`scripts/lumos:24486`附近的 `if deadline is not None and _t.monotonic() > deadline: return None`)。在第一次候選檢查之前,下面幾支 git 呼叫全部沒有 deadline 感知,各自吃 `_lens_git` 寫死的 `timeout=20`(`scripts/lumos:30271-30272`):
   - `_drift_tree_env` 裡的 `_nodehome_list(root, where)`(ls-tree)——`scripts/lumos:25347-25358` 附近,只有後面 `_nodehome_cat_blobs` 那一次有把 `timeout=max(1, timeout)` 傳進去,`_nodehome_list` 這次完全沒有。
   - `_drift_range_events` 開頭的 `_ns_git(root, "diff", "--name-only", ...)`(`scripts/lumos:25394`)。
   - 兩次 `_notes_status_flipped` 呼叫(passed 一次、closed 一次)各自開頭那一句 `touched = _ns_git(repo_root, "log", "--format=", "--name-only", ...)`(`scripts/lumos:24476`附近)——這一句在迴圈的 deadline 檢查**之前**執行,而且兩次呼叫用的是同一個 range、彼此互不知道對方已經跑過。
   總共至少 4 次(ls-tree、diff、log×2)可以各自吃滿 20 秒而不會被已經過期的 deadline 攔下來,不是文件說的「一次呼叫」。

2. 重現(deadline 早就過期 1000 秒,量測 `_drift_check_core` 實際跑多久、跑了幾次 git):
```
指令:python3 /private/tmp/.../scratchpad/repro_budget.py
(對 scripts/lumos 的 subprocess.run 做 monkeypatch,每次真呼叫前加 2 秒延遲,計時、記錄呼叫序列;
deadline = time.monotonic() - 1000,直接呼叫 m._drift_check_core(root, "87d43a50", tip_sha, "docs/lumos-toolchain-knowledge", deadline=deadline))
```
輸出:
```
deadline 早就過期(-1000s),_drift_check_core 實際跑了 15.12 秒才回
unknown=['超過 60 秒預算']
git 呼叫次數=8(每次人工延遲 2.0s)
  [  2.05s ~   4.14s] ls-tree
  [  4.15s ~   6.36s] cat-file
  [  6.43s ~   8.47s] rev-parse
  [  8.47s ~  10.53s] diff
  [ 10.53s ~  12.57s] -c ...(log,touched,第一次 _notes_status_flipped)
  [ 12.57s ~  14.93s] -c ...(log,touched,第二次 _notes_status_flipped)
  [ 14.93s ~  17.17s] -c ...
```
即使把 deadline 設成「早就超過 1000 秒」,函式仍然實際跑了 7 次自己的 git 呼叫(扣掉我自己呼叫 `_lens_full_sha` 找 tip 那一次)才回「判不了」,而不是立刻回。把每次人工延遲換成 git 真的卡住 20 秒(例如遠端網路掛載、`.git` 鎖競爭),同一套呼叫序列會讓推送前檢查卡到 60 秒預算 + 至少 80~100 秒(4~5 次 ×20 秒),而不是文件承諾的「多一次呼叫的時間(~20 秒)」。

3. 正常情況(沒有人工延遲)下這支確實有變快:`time python3 scripts/lumos drift check --diff 87d43a50..HEAD --repo .` 實測 25.7 秒(對照 PITFALL 記的「67 秒→28 秒」),所以「先建候選再逐提交讀」這個優化本身有效——問題只在文件對「最壞情況」的新承諾算錯了,漏算了候選篩選前那幾支未受節制的呼叫。

4. 附帶:`_left()`(`scripts/lumos:25424-25425`)在 `deadline is None` 時寫死回 `60`,沒有引用同檔的 `_DRIFT_BUDGET_SEC` 常數(`scripts/lumos:25156`)——目前兩個值剛好都是 60,不影響行為,但這是文件與常數各說各話的伏筆,不單獨算一條 finding。

## 逐條檢查(已指定的其餘四點):已看,已用讀碼+測試驗過,無 finding

**`_notes_status_flipped` 新增的 `only`/`deadline` 對筆記內容審原呼叫端無影響**:`_note_audit_closed_plans`(`scripts/lumos:24466-24471`)呼叫時兩個新參數都不給,預設 `only=None`(迴圈裡 `if only is not None and ...` 恆假,不濾候選)、`deadline=None`(迴圈裡的 deadline 檢查恆不觸發)——跟拆出 `_note_status_seq` 之前的行為在這條呼叫路徑上是等價的重構,不是新邏輯。已跑 `python3 scripts/test_lumos.py -k drift`(123 個案例全過,含 `t_drift_check_state_events_in_range`、`t_set_plan_closed_lists_followups`)與既有的筆記內容審相關測試,無回歸。

**正式行與預告行同時在時,拿掉預告行那一步的鎖與原子寫**:`_guard_settle_home`(`scripts/lumos:11987-12022`)整段包在 `cmd_guard_settle` 外層的 `with _vault_write_lock(env.vault):`(`scripts/lumos:11947`)裡,`_guard_planned_line` 對同一支檔案的第二次讀取(`scripts/lumos:11996`)發生在同一把鎖的臨界區內,鎖持有期間沒有其他寫入者能插進來改這支檔案,兩次讀取之間內容不會漂移。寫入用 `atomic_write_verify` 帶驗證函式(`scripts/lumos:12003-12004`),失敗時印訊息並回 `False`,守衛紀錄本身完全沒被動(仍是 pending),下次重跑會在同一個分支再走一次(`_guard_formal_line` 仍找得到正式行、`_guard_planned_line` 仍找得到預告行)——可重試、不留半殘狀態。已跑 `python3 scripts/test_lumos.py -k guard_settle`(28 案例全過,含新場景③「正式行已在時也要把預告行拿掉、不留兩條」)與 `-k guard_commands_hold_vault_lock`(4 案例全過,驗證 plan/settle/abandon 讀家筆記時都拿著鎖)。

**表態追加改拿筆記庫寫入鎖,是否跟 guard/set 互卡**:`cmd_drift_ack`(`scripts/lumos:25537`)用的是同一把 `_vault_write_lock(env.vault)`,不是新鎖;`_vault_write_lock`(`scripts/lumos:14479-14525`)本身對同一個程序巢狀拿同一把鎖直接放行(`_VAULT_LOCK_HELD`計數器)、跨程序用鎖檔+輪詢+60 秒逾時+過期接手,這套機制沒有被這份 diff 改動,只是多一個呼叫端在用。`drift check`(推送閘讀路徑)本身不拿鎖,不會跟寫入端互卡;`drift ack` 跟 `guard settle`/`set` 之間只是排隊等鎖(設計如此),不是死鎖。沒發現新的巢狀鎖或跨鎖情境。

**doctor 開頭多一次 git 呼叫**:新的 `_drift_gate_doctor_lines`(`scripts/lumos:957-`附近)裡那次 `_lens_git(root, "show", f"HEAD:{_NOTELINES_PREPUSH}")`,是把舊版 `_drift_doctor_lines`(Z 段)裡原本就有的同一次呼叫搬到 doctor 開頭位置,doctor 對「存量漂移檢查」這件事本身的 git 呼叫總數沒有淨增加(搬家,不是新增)。★但這次呼叫的內容(讀推送前掛鉤檔)跟 `_note_audit_doctor_lines` 裡幾乎同一支呼叫(`scripts/lumos:26120`,同樣是 `git show HEAD:<掛鉤檔>`,只是找的標記字串不同)是重複的——這個重複在舊版就存在(舊 drift Z 段本來就獨立讀一次同一支檔),不是這份 diff 新introduce 的,只是這份 diff 沒有順手把它併掉。⚠ 沒有具體失敗場景(只是多一次可省的 fork/exec),不單獨算 finding。

## 圖譜鏡頭:LUMOS-IMPACT b9ca00bb..e72324b8(26 固定席逐條判)

用 `lumos impact --diff b9ca00bb..e72324b8 --repo .` 取得固定席清單,逐條對照這份 r1→r2 diff(不是整個 feature commit)判斷會不會破壞該節點宣稱的行為或合約:

1. **Systems/lumos-cli-read.md** — 不影響:節點講 `search`/`contracts`/`doctor` 框架本身,這份 diff 沒碰這幾支指令的程式碼,新加的 drift 提醒段跟既有 note-shape/note-audit 提醒段同一種「try/except 印一段、失敗不中斷」模式,doctor 對外行為契約沒變。
2. **Systems/guard-kill.md** — 不影響:`guard kill` 的 rc 優先序、JSON 純淨度、guard plan/settle/abandon 的預告轉正/棄置設計都沒被改動語意,只精修了 `_guard_formal_line` 的比對規則與補上「正式行+預告行同時在」邊界。已跑 `-k guard_kill`(50 案例全過)、`-k guard_plan_creates_marker`(11 案例全過)驗證合約仍成立。
3. **Systems/design-loop.md** — 不影響:條款綁測試/處置閘程式碼不在這份 diff 範圍內。
4. **Systems/lumos-cli-lifecycle.md** — 不影響:re-inject sentinel 與 slim 凍結決策跟這份 diff 無關。
5. **Systems/授權與歸屬.md** — 不影響:LICENSE/SPDX vendoring 白名單機制沒被動到。
6. **Systems/測試假綠形態.md** — 不影響(且方向一致):這份 diff 新加的回歸測試 `t_drift_code_review_r1_regressions` docstring 明講「每條先在舊碼上紅」,符合節點講的「翻紅釘要證明現場成立」的教訓,沒有違反。
7. **Systems/loop-convergence-recording.md** — 不影響:跟收斂記錄機制無關,關鍵字掃描沒有交集。
8. **Systems/pitfalls-code-loop.md** — 不影響:跟 UI 層驗收慣例無關。
9. **Systems/reversibility-governance-ledger.md** — 不影響:這份 diff 沒新增不可逆操作;`guard abandon` 留墓碑、`_guard_settle_home` 是改寫既有行而非刪除,可逆性語意不變。
10. **Systems/節點範圍與索引守衛.md** — 不影響:節點裡「新段落必須排在 [E3] 之後、[H] 之前」講的是 doctor 字母段落(`[S]`…`[E3]`…`[H]`)本身的插入順序;新的 drift 閘提醒段放在 doctor 開頭、跟既有 note-shape/note-audit 提醒同一個位置,不在那串字母段落序列裡,不違反這條排序合約。索引覆蓋範圍等其餘各條與這份 diff 無交集。
11. **Systems/lumos-deinit.md** — 不影響:跟 deinit 流程無交集。
12. **Systems/cochange-guard.md** — 不影響:跟 co-change 偵測無交集。
13. **Systems/check-r-guard.md** — 不影響:doctor Check R(可逆性回退)程式碼不在這份 diff 裡。
14. **Systems/check-t-sentinel.md** — 不影響:Check T 對 `★INVARIANT★→[test:]` 的獨立掃描邏輯沒被這份 diff 碰;`_guard_formal_line` 是 guard settle/scan 自己另一套「摘要裡找正式行」邏輯,兩套不共用同一支程式碼,也沒有互相依賴。
15. **Systems/doctor-irreversible-hint.md** — 不影響:跟這份 diff 無交集。
16. **Systems/lumos-refcheck.md** — 不影響:跟這份 diff 無交集。
17. **Systems/bound-tests-gate.md** — 不影響:這份 diff 只加了 `RULE:`/`PITFALL:`/`TEST:` 行到 `Systems/存量漂移守衛.md` 摘要,沒有新增 `★INVARIANT★` 行,不觸發 bound-tests-gate 對 `★INVARIANT★[test:]` 的綁定判定;新測試走既有的 `TEST:` 行登記管道,跟這道閘不衝突。
18. **Systems/canary-audit.md** — 不影響:跟這份 diff 無交集。
19. **Systems/slim-get-一行安裝.md** — 不影響:跟 slim/ 分裝機制無交集。
20. **Systems/slim-install-安裝器.md** — 不影響:同上。
21. **Systems/slim-uninstall-一行卸載.md** — 不影響:同上。
22. **Projects/雙向門放行_計劃.md** — 不影響:這份 diff 動到 `scripts/lumos`/`scripts/test_lumos.py`,本來就不是純文件改動,走既有的 `--suite keys`/全套規則,沒有牴觸雙向門本身的判斷邏輯。
23. **Projects/規格落成可驗收條件_計劃.md** — 不影響:跟 spec-gate 條款判定程式碼無交集。
24. **Projects/逃逸自動記_計劃.md** — 不影響(已核對):這篇計劃的 PRIOR-ART 引用了 `_vault_write_lock`/`_jsonl_append_verified` 當自己的設計依據,這份 diff 沒有改動這兩支的行為語意,只是新增一個呼叫端(`cmd_drift_ack`)用同一把鎖,不影響這篇計劃「寫側整段在 `_vault_write_lock` 裡」的設計假設仍然成立。
25. **Systems/core-invariant-baseline.md** — 不影響:跟這份 diff 無交集。
26. **Systems/judge-severity-gate.md** — 不影響:跟這份 diff 無交集。

沒有一條固定席筆記宣稱的行為或合約被這份 diff 破壞;guard-kill 相關的兩條(#2)額外用測試覆核過,其餘因為程式碼路徑完全不相交,判「不影響」的理由就是關鍵字/函式名掃描沒有交集。

## 總結

最嚴重等級為 major,blocking 共 1 條(F1):新加的 `check` 推送閘預算機制對「最壞會超過多久」的文件承諾不實——deadline 只節制候選迴圈,候選篩選前至少 4 次 git 呼叫(ls-tree、diff、兩次 log)完全不受 deadline 節制,各自可吃滿 20 秒;已用「deadline 早就過期時實測仍跑 8 次 git、耗時 15 秒才回」的可重現腳本證實,正常情況下優化本身(25.7 秒,對照 PITFALL 記的 28 秒)確實有效,問題只在最壞情況的文件承諾算錯。其餘四個指定檢查點(only/deadline 對筆記內容審呼叫端無影響、正式行+預告行同時在的鎖與原子寫、表態追加鎖與 guard/set 不互卡、doctor 多一次 git 呼叫是搬家非新增)讀碼加測試驗證後判無 finding;26 篇固定席筆記逐條核對,判定這份 diff 沒有破壞任何一條宣稱的行為或合約。
