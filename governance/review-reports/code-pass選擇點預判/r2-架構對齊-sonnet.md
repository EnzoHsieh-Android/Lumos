severity: minor

## 三問

**1. 分層與依賴方向:大致對齊,有一處 ⚠。**
- 新函式 `_codeloop_pass_choice` 的命名、位置和接法都跟鄰居一樣。
  - 命名跟 `_codeloop_pass_mech`/`_verify` 同一排,在 `_codeloop_pass_gate` 裡接在 mech 之後、verify 之前。
  - 對照:`scripts/lumos:73376`(mech)、`:73397`(新)。
- 它沒有經過 `_codeloop_guard_verdict`,而是直接呼叫 `_choice_push_round(..., site="pass")`,對照:`scripts/lumos:73415`、`:79666`。
  - 鄰居 mech 走 `_codeloop_guard_verdict(mech_only=True)`。
  - 但 `_codeloop_guard_verdict` 的實作(`:79666-80500`)一個 `_choice_*` 也不呼叫。選擇點本來就不在 code-loop 判定函式裡,只在 `_spec_gate_push_check`(`:17448`)。
  - 所以不存在可繞過的 code-loop 層入口。
  - 原本 `_choice_push_round` 只有 `_spec_gate_push_check` 一個呼叫端,現在多一個 code-loop 層的直呼端。
  - 「模式參數分流」的寫法跟 `mech_only` 同形,這部分對齊。
  - 專案裡沒有可對照的既有做法,我不判定這算不算跨層,標 ⚠ 交編排者。
- 傳 `env=None`:`_choice_push_round` 的 `env` 沒被讀,不影響行為,但跟 `:17448` 傳 `env` 不同。

**2. 命名與錯誤處理:基本對齊,有一條 minor(a2)。**
- 治理帳事件對齊鄰居:`_gate_event_or_warn(..., hard=True, head_sha=, ref=, extra={"blocks":[...]})`,對照 `:73392`/`:73423`。
- `_choice_push_event` 的 `site` 欄位、去重鍵和 `ck` 白名單,做法都跟既有選擇點事件欄位一致。
  - `c["pass_blocked"] += ck.get("site") == "pass"` 的寫法跟 `stale_blocked` 同形,對照 `:17943-17946`。
- 錯誤處理:沒有 try/except,偵測不到分支或遠端就印一行放行,跟 `_choice_push_scan` 的「算不出來就放行」同一路。
- 測試命名(`t_codeloop_pass_*`)、各段自帶 git 小工具(`_nh_git`、`_kr_git`、`_sg_git`…)的慣例都對齊。
- 不一致的只有訊息輸出的形狀,見 a2。

**3. 第二種做法:沒有 major,有一條 ⚠ 的 minor(a1)。**
- 取分支名:改用共用的 `_redbase_branch_name`,不再是第二套。
  - 修前用 `symbolic-ref --short`,修後走 `refs/heads/` 去前綴。
  - 我在臨時 repo 造了一個跟分支同名的 tag(`feat/sit`),`--short` 回 `heads/feat/sit`,去前綴回 `feat/sit`。
- 取遠端:用共用的 `_lens_default_remote`,對照 `:69981`。
- 去重鍵含 site 也不是另開抑制機制。
- 殘留:`_lens_default_remote(rr, None, None)` 內部仍用 `--short`(`:69987`)。那是鄰居自己的實作,不是這份 diff 造成,但在同名 tag 加非 origin 遠端時會取錯,留給編排者知悉。

## a1 pass 預判自己組一套「模擬推送」的範圍輸入,跟專案內其他三種取範圍法並存
severity: minor
blocking: 否
引句:「old = _lens_full_sha(rr, f"refs/remotes/{remote}/{name}") or "0" * len(tip)」
對照:file: `scripts/lumos:77871-77900`(`_choice_range`:同樣是「分支→頂端→遠端→`_push_range_start`」,但舊值固定全零)
對照:file: `scripts/lumos:73376-73395`(同一個 `_codeloop_pass_gate` 裡的 mech 用分岔點..HEAD)
對照:file: `scripts/lumos:57950-57990`(`_note_reread_push_old`,註解寫明「為什麼不用本機追蹤 ref」)

同一個選擇點功能現在有兩份「目前分支算範圍」的組裝,`_choice_range` 和這個新函式,舊值取法不同。同一個 pass 閘裡,mech 和 choice 的範圍口徑也不同。
- 計劃(〈做法〉範圍)和筆記都明講這是刻意的,為了跟推送前掛鉤同一段;結構上仍呼叫同一支 `_push_range_start`,所以不是 major。
- 專案本身就有 `_lens_push_base` 與 `_push_range_start` 兩套並存(`:69647` 註解自述),找不到唯一的既有做法可對。
- 本機追蹤 ref 當舊值,是 `_note_reread_push_old` 明確否決過的方向。pass 沒有掛鉤給的舊值,所以沒有替代。這點留給編排者判斷。

歸因:有證據的原有漏查。
- 兩版範圍組裝逐行一樣,只有取分支名那三行不同:`diff <(sed -n 73397,73424p 修前) <(sed -n 73397,73424p 修後)`。
- 修前 `ccca94927:scripts/lumos:73397`、修後 `826ce8451:scripts/lumos:73397`。

## a2 擋下訊息自己拼、自己印,沒重用推送前那一段,輸出通道也跟 mech 鄰居不同
severity: minor
blocking: 否
引句:「print(f"{P} {_CHOICE_PASS_TAIL}")」
對照:file: `scripts/lumos:17403-17414`(`_spec_gate_push_bad_tail`:條列原因加選擇點專屬尾段,推送前共用的印法)
對照:file: `scripts/lumos:80490-80500`(`_cl_say_block`:mech 擋下訊息全走 stderr)

幾個不一致:
- 條列 `for x in bad: print(f"    • {x}")` 是 `_spec_gate_push_bad_tail` 前兩行的手抄。推送前那段也有選擇點專屬的尾段,內容跟 `_CHOICE_PASS_TAIL` 幾乎同義。所以 pass 這邊並不是「推送前原樣加 pass 出口」,少了標題行,尾段也是另寫的一份。
- 條列、尾句與「沒有分支/沒有遠端」提示都印 stdout,同一函式後面的出口行印 stderr。mech 鄰居整段都走 stderr。
- 新出現 `[code-loop pass 選擇點]` 這個前綴。`_codeloop_pass_*` 其他函式沒有方括號前綴。
- `_CHOICE_PASS_TAIL` 定義在 `_choice_push_*` 區段(`:78809`),離唯一使用處 `:73420` 隔約 5000 行。
- 結構是對的:原因照印、再補出口、再記 `code-loop-pass` 擋下。只是印法沒重用現成的。

歸因:有證據的原有漏查。
- 修前(`ccca94927:scripts/lumos:73419-73421`)已有同樣的手抄條列加 `_CHOICE_PASS_TAIL`。
- 修復只換了尾段內容並拿掉字樣替換表,印法沒變。

## 修補鏡頭(binding:修前 ccca94927 → 修後 826ce8451)

**① 原問題的修復效果**
- G1 分支名:修前 `symbolic-ref -q --short`,修後 `_redbase_branch_name`。
  - 同名 tag 的臨時 repo 實測,修前取到 `heads/feat/sit`,修後取到 `feat/sit`。
  - 這個行為證據是我自己跑的 git 指令,不是整合測試。
- G2 字樣替換表:修後 `_CHOICE_PASS_WORDS`/`_CHOICE_PASS_FIX` 已消失。
  - 修前 `lumos.before` 有:`:78811`、`:78815`、`:78955`、`:78984`。
  - 修後 `site` 只剩帳來源、事件欄位、去重三件事。
  - 這個修法確實消掉了第二種訊息改寫方式。
- G5 筆記:`pitfalls-code-loop.md` 已寫明直呼關係和 `site` 參數。這是文件類,我只核對文字跟程式一致。
- G3、G4(增量案例、測試拆四支):我只在 diff 裡看到 `t_codeloop_pass_choice_range` 含增量案例、四支測試名互不為子字串。
  - 沒有實際執行,因為本席不跑測試。這兩項留未判定。

**② 修補處的相鄰路徑**
- preserve:`site="push"` 預設在 `_choice_push_event` 不寫 site、去重鍵用 `(e.get("site") or "push")`。
  - 舊帳和推送前事件形狀不變,測試 S22 只動了字樣。
- 未驗範圍:
  - 推送前的實際跑法。
  - detached 與無遠端兩條分支只讀了程式,沒實跑。

**③ 新發現的同一案例修前、修後**
- a1:修前修後同結果,所以不算修復回歸。
- a2:修前修後同結果,所以不算修復回歸。

不對齊共 2 條,其中 major 0 條(兩條 minor;另有一項 ⚠ 交編排者:`_codeloop_pass_choice` 直呼 `_choice_push_round` 算不算跨層)

清理:本席臨時目錄 `/tmp/lumos-seat-work/code-pass選擇點預判/架構對齊-sonnet/` 已刪成空目錄,只剩該目錄本身。
