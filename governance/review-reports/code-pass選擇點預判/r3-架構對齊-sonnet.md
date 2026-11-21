severity: minor

## 三問

**1. 分層與依賴方向:部分對齊,有一處待編排者裁。**
- 新函式 `_codeloop_pass_choice` 放在 `_codeloop_pass_mech` 正下方、`_codeloop_pass_gate` 呼叫它(`scripts/lumos:73381`、`73434`),位置與接法跟鄰居一致。
- 鄰居 `_codeloop_pass_mech` 是經 `_codeloop_guard_verdict(mech_only=True)` 取判定(`scripts/lumos:73381`、`79673`)。新碼是 code-loop 層直接呼叫規格閘那一圈的 `_choice_push_round`(`scripts/lumos:73421`)。
- 推送前 `_spec_gate_push_check` 自己就在規格閘層呼叫它(`scripts/lumos:17448`),所以不算跨層直呼。但 `_codeloop_guard_verdict` 本體沒有任何 `_choice_*` 呼叫(已 awk 掃 `79672` 起的函式體),這是 code-loop 層第一次直接進規格閘的選擇點一圈。
- 這是新依賴方向,不是既有做法,我判「結構尚可、方向新」,不升 major。

**2. 命名與錯誤處理:大致對齊,一處輸出通道不同。**
- 事件寫帳用 `_gate_event_or_warn(..., "code-loop-pass", "blocked", hard=True, head_sha, ref, extra={"blocks": [...]})`,與 `scripts/lumos:73391-73393` 同形。
- `site` 事件欄位寫在選擇點事件上走 `_choice_gate_event`,沿用 `scripts/lumos:78221` 的語意。
- 計數寫法 `c["pass_blocked"] += ck.get("site") == "pass"` 與同函式既有的 `stale_blocked += any(...)` 同型。
- git 呼叫回 None 的處理沿用 `_lens_git` 的慣例(`scripts/lumos:70032`)。
- 零遠端與多遠端兩種情況分開講,屬新增行為,不是不一致。
- 不一致處見下面 a1。

**3. 第二種做法:大體沿用鄰居工具,但有一處組合是第二種做法。**
- 分支名用 `_redbase_branch_name`(`scripts/lumos:15391`),遠端用 `_lens_default_remote`(`scripts/lumos:69981`),起點交給 `_push_range_start`(`scripts/lumos:69641`),全零寫成 `"0" * len(tip)`(同 `scripts/lumos:77898` 一帶 `_choice_range` 的做法)。基礎工具都沿用。
- 取遠端清單時再呼叫一次 `_lens_git(rr, "remote")` 並 `split()`,跟 `scripts/lumos:63600` 同樣寫法,專案沒有專用的遠端清單函式可對,不列。
- 「舊值=`refs/remotes/<遠端>/<分支>`,查無就全零」這套範圍取法,跟 `_choice_range`、`_codeloop_default_range` 並存。見 a2。

## a1 pass 預判的原因與出口印到 stdout,同流程鄰居印到 stderr
severity: minor
blocking: 否
引句:「print(f"    • {x}")
    print(f"{P} {_CHOICE_PASS_TAIL}")」
file: `scripts/lumos:73426`(對照 `scripts/lumos:80496` 的 `_cl_say_block`、`_cl_say_lint_block`、`_cl_say_disp_block`)
- 同一條 `code-loop pass` 流程裡,新增告警與表態兩道的擋下訊息全走 `file=sys.stderr`。
- 選擇點這道的原因逐條與 `_CHOICE_PASS_TAIL` 走 stdout,只有最後「代碼審還不能記通過」那兩行走 stderr。
- 另外它沒用 `_spec_gate_push_bad_tail`(`scripts/lumos:17403`),自己手寫 `• {x}` 迴圈。該函式的選擇點尾段是推送前專用說法,所以另寫出口有理由,但印的通道跟鄰居 pass 兩道不一致。
- 推送路徑本身印 stdout(`scripts/lumos:17403`),所以鄰居也有分歧,也可能是刻意沿用推送原樣,我沒法硬判,請編排者裁。
- 歸因:未判定。修前就沒有這段(`826ce8451` 到 `4fa287474` 的修補差異沒動這兩行),也不是修復造成的,兩版都是同樣印法。

## a2 範圍取法在同一次 pass 裡與 `_codeloop_pass_mech` 並存不同的兩套
severity: minor
blocking: 否
引句:「old = _lens_full_sha(rr, f"refs/remotes/{remote}/{name}") or "0" * len(tip)」
file: `scripts/lumos:73420`(對照 `scripts/lumos:77899` 的 `_choice_range`、`scripts/lumos:79550` 的 `_codeloop_default_base`、`scripts/lumos:46725` 的 `refs/remotes/origin/{branch}`)
- 同一次 `pass` 先由 mech 走 merge-base..HEAD,再由這裡走模擬推送。
- `_choice_range` 的註解自稱是「跟推送前那一道同一套」,舊值固定全零。新碼是同一骨架(分支名、頂端、遠端、`_push_range_start`)改成舊值讀本機追蹤分支,約 6 行重複。
- 這可能是第二種做法:選擇點範圍有了第三種取法,卻沒有收斂進 `_choice_range`。
- 但舊值讀 `refs/remotes/...` 在 `scripts/lumos:46725`、`48266` 有先例,基礎工具又都共用,所以我判不準,標 ⚠ 交編排者。
- 歸因:未判定,不是修復造成的。修補只動了「沒有遠端」那段,範圍取法修前修後相同。

## 修補鏡頭核對
- **① 原問題修復效果**:兩版各跑 `python3.14 scripts/test_lumos.py -k t_codeloop_pass_choice_skips`。修前 `826ce8451` 為 8 passed、0 failed,修後 `4fa287474` 為 10 passed、0 failed,多出的兩條就是新案例(沒有遠端放行、兩個遠端沒有 origin 的說明)。
- **② 相鄰路徑**:有 origin 或分支設了上游時 `_lens_default_remote` 照舊回遠端名(`scripts/lumos:69981` 的回傳規則),不進新分支;detached HEAD 與非 Kotlin 專案的早退順序沒動(都在 `remote` 判斷之前)。
- **③ 修前修後同案例**:這是我讀碼推得,沒另跑反例。修前兩個遠端都不是 origin 時 `remote` 為空,會印「沒有遠端」。修後多一次 `_lens_git(rr, "remote")` 計數,改印「有 N 個遠端、沒有 origin、分支也沒設上游」。
- **未驗範圍**:沒有實機多遠端並真的跑 `pass` 寫帳,只靠既有測試與讀碼。`t_prepush_cl_reason_table_matches_lumos` 是否需要列入 `choice` 這個 reason_kind 我沒驗。

不對齊共 2 條,其中 major 0 條
