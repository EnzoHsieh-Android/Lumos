severity: major

整體判斷:實作的主要路徑是對的,我找不到會做出錯誤紅燈版決定的輸入,只有一條測試漏洞。我跑了新增的五支測試(`t_spec_gate_redbase_green_other_branch`、`t_spec_gate_redbase_green_tracked_unfiltered`、`t_redbase_branch_rows_fallback_keeps`、`t_name_collision_scales`、`t_tq_guard_string_comma_args`),`-k redbase`(181 支)和 `t_tq_guard_cli_contract` 也全綠。`-k spec_gate` 子集我開了但沒等到結果,所以那一批沒驗。

1. 淺複製下「回傳碼 1」的分支沒有測試,拿掉淺複製保護測試照綠。
   - 引句:「verdict[sha] = None if is_shallow() else False」
   - 場景:CI 這類淺複製拿 `--depth 1` 抓 HEAD,再另外抓一個真正是祖先的提交。兩個提交都在,但 HEAD 的歷史被截斷。這時 `git merge-base --is-ancestor` 回傳 1(不是祖先),實際上它是祖先。
   - 我造出的重現:HEAD=c2,`fetch --depth=1` 抓回 c1,`merge-base --is-ancestor c1 HEAD` 回 rc=1,`rev-parse --is-shallow-repository` 回 true。
   - 正確行為是照舊留(驗收條款 S8、做法 1c 寫的「rc 1 → 淺複製留」)。
   - 改壞:把該行改成 `verdict[sha] = False`。我在 `/tmp` 的複製 repo 套用後,`t_redbase_branch_rows_fallback_keeps`(7 項)、`t_spec_gate_redbase_green_other_branch`(10 項)、`t_spec_gate_redbase_green_tracked_unfiltered`(2 項)全綠。
   - 直接呼叫 `_redbase_on_branch`,對上面那個淺複製與 `head_sha=c1`:原版回 1 筆並印「判不了」,改壞版回 0 筆(丟掉真的祖先、不印說明)。
   - 原因:`t_redbase_branch_rows_fallback_keeps` 的淺複製案只用不存在的提交 `"cd"*20`,走的是回傳碼 128 加 `cat-file` 那條路,只覆蓋到 `... or is_shallow()` 那個守衛。
   - 修法方向:補一個淺複製案,用 `--depth=1` 加 `fetch --depth=1 <祖先提交>` 造出 rc 1。
   - 我列為 major,理由是驗收條款 S8 明寫淺複製要照舊算進來,而這條分支沒有紅燈。實際發生機率低:紅燈版只在開發機跑,CI 不存紅燈版。
severity: major
   - blocking: 是

其餘我走過、沒找到錯的點:

- **分離 HEAD、還沒有提交的 HEAD**:分離 HEAD 時分支名為空字串,只剩祖先判斷。沒有 HEAD 時 `head` 為 None,逐筆照舊留。
- **帳裡欄位型別不對**:`ref` 不是字串就跳過分支名比對。`head_sha` 不是字串或不像提交編號就留,而且用 `fullmatch`,尾端換行擋得掉。
- **同一個 head_sha 多筆**:判定結果有快取,只問一次 git。
- **上限與截止時間**:上限剛好 200 個時全都會問。第 201 個起標成判不了照舊留。截止時間用完時 `_lens_git_dl` 回 None,留下並印一句幾筆。
- **git 錯誤路徑**:`_lens_git_dl`、`_gov_ledger_ignored` 回 None 或 unknown 時都退回舊行為,沒有未接的例外。
- **舊帳與新帳互讀**:新程式讀沒有 `ref` 的舊事件時只走祖先判斷。舊版 lumos 讀新帳會忽略多出的 `ref` 欄位。
- **其他讀取端會不會誤讀 `ref`**:
  - `_codeloop_read_from_ledger` 只認 `gate=code-loop` 並讀 `branch` 欄位。
  - `_spec_gate_gov_index` 不用 `ref`。
  - 其餘 `d.get("ref")` 的讀取端各自讀簽核帳與回顧帳,與這批事件無關。
- **推送前比對工具的紅燈版讀取端**:`_tg_redbase_records` 讀的是版控帳(跟分岔點做行差),新過濾只在「帳被忽略」時才動。被忽略的專案推送時本來就是孤兒紅燈版,兩端不會對不上。
- **`t_name_collision_scales`**:子類計數是真的在抓錯。把快取拿掉會讓 `built` 變成 1000;`_join` 不快取會讓串接次數重複。兩種改壞都會翻紅。測試單執行緒依序跑,全域換掉又在 `finally` 換回,不會洩漏給別的測試。
- **`_TG_CONST_PAT` 三引號**:佔有式量詞寫法與 `_TG_LIT_PAT` 相同,是線性的。三處 `fullmatch` 共用同一個常數。`_tg_ident` 註解提到的 `_tg_ws_keep_strings` 傳 `_tg_ws_collapse` 我核對過,屬實。

固定席筆記逐條判定:

- `lumos-cli-read`(search 預設排除 superseded):不影響。diff 沒碰 search 的篩選。
- `測試假綠形態`(還原翻紅釘要配前置斷言):不破壞。新測試多半有前置斷言:S1「判綠紀錄記下分支名」、S7「判綠時的提交已不是祖先」、S9「第一條分支存了紅燈版」、`t_name_collision_scales` 的「有走到撞名判定」。S6 的 gb3 缺少「綠事件確實存在」的前置斷言,但我講不出會因此照綠的具體改壞,所以沒標。
- `design-loop`、`bound-tests-gate`、`guard-kill`、`loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger`:不影響。diff 沒動設計審處置閘、合約綁定測試閘、guard kill 的退出碼或 `--json` 輸出,也沒動代碼審帳。多記的 `ref` 欄位不會被代碼審留痕讀取端當成留痕。
- 超出上限只列名的那批:沒逐條讀。

總結:max severity 是 major,blocking 1 條(共 1 條 finding)。
