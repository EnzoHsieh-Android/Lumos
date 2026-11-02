---
type: project
status: todo
created: 2026-11-01
updated: 2026-11-01
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/loop-convergence-recording
related:
  - "[[Projects/代碼審收尾強化_計劃]]"
  - "[[Projects/code-loop分支留痕一致_計劃]]"
pending_questions:
  - id: Q1
    text: 沒帶 --loop 的 pass 要直接擋,還是先只印四週?(建議直接擋,skip 當出口)
    class: 範圍
    stage: 架構
    status: 已決
    blocking: true
    decision: Projects/留痕驗過審查_計劃#d1
  - id: Q2
    text: 最後一輪 major 修補沒人看過,第一版只記錄不擋,可以嗎?(建議可以,要擋得先解第三輪上限衝突)
    class: 範圍
    stage: 架構
    status: 待人
decisions:
  - content: 沒帶 --loop 的 pass 在有審查帳的專案直接擋,不先只印
    id: d1
    context: Enzo 2026-11-01 裁。不選:先只印四週;只在 tier=high 要求
    why_chosen: 只提醒的東西沒人回頭;不審有 skip 當出口,照樣留痕被統計;代價是消費專案合入當下還沒凍結的迴圈會被擋一次
    decided: 2026-11-01
    valid: true
---
# 留痕驗過審查_計劃

白話:推送前的「審查通過」紀錄現在像一張自己填的簽到單,寫了就算,工具不看審查到底做完沒。這份計劃讓它在寫下之前先看一眼現成的判定檔:這個審查迴圈有沒有凍結判定、判定是不是過、判定之後帳有沒有再變。沒過就不給寫,真的不審走既有的 `skip`,照樣留痕、照樣被統計。總路線見 [[Projects/代碼審收尾強化_計劃]]。

WHY:`pass` 寫入前讀既有凍結判定檔,不重算處置閘、不新增第二道閘 [出處:2026-11-01 調研報告第 1 條與程式核對] [因:手冊本來就規定留痕前要凍結,判定檔已帶結果與逐列指紋;防的是忘記與順序錯,不是刻意偽造] [不選:pass 內重跑處置閘(要自帶 spec 路徑,還多一條判定入口);code-loop check 讀判定(推送檢查的合併與新分支路徑已很複雜,且 CI 跟著變);golden 回放(帳本長大只列出不紅,抓不到判定後又加輪)]
WHY:沒帶 `--loop` 且專案有審查帳就擋 [出處:2026-11-01 使用者裁,本篇 d1] [因:2026-10-15 起 113 筆留痕有 52 筆備註含已凍結迴圈名,靠自由文字認迴圈不可靠;`skip` 是既有出口] [不選:先只印不擋四週(只提醒的東西沒人回頭);讓 tier=high 才要求(pass 不算 tier,要多一次分級計算)]
PRIOR-ART: 世界解是合併條件綁審查狀態:Anthropic 內部逐條必答才能合併,GitHub 的必要檢查也是同型。本 repo 既有先例是 `check` 綁提交編號的留痕與 `loop replay --freeze` 的判定閉包,這裡借用閉包,不新增帳本。調研依據在 `governance/research/code-review-world-2026-11/report.md`。
RETIRE-IF: 上線滿三個月,`pass` 擋下的事件經人判讀,誤擋多於抓到真漏審,或擋下幾乎全部改走 `skip`,就撤掉判定檔檢查、只留 `--loop` 綁定。
REVISIT:2026-12-15 數上線後帶 `unreviewed_fold` 的留痕筆數與之後逃逸,判斷「最後一輪 major 修補沒人看過」要不要從記錄改成擋;要擋先解決第三輪上限衝突。
REVISIT:2026-12-15 比對高風險推送的算出分級與迴圈帳上分級,判斷 `pass` 要不要驗「帳上分級不低於算出分級」。
REVISIT:2026-12-15 數跑滿上限又沒有合格回顧卻過了 `pass` 的迴圈,判斷 `pass` 要不要連跑滿回顧一起驗。

## 問題與現況

- `cmd_code_loop` 的 pass 分支只寫 marker 與治理帳,`pass` 與 `skip` 共用同一分支;手冊也寫明這是既有天花板。[[Projects/code-loop分支留痕一致_計劃]] 2026-10-04 前掃時把「程式不驗審查完成」列成人工前提,不是否決,那案本身未合入。
- `LOOP_CLOSE_EVENTS_BY_DETAIL` 上方的 REVISIT(2026-11-07)指定的正解就是 `--loop` 參數寫進 `nodes`,本案順帶關掉它。現有 642 筆 code-loop 放行事件的 `nodes` 全是空的,讀側 `_loop_close_stamps` 靠編號在 `detail` 全文做邊界比對。
- 判定檔事實(2026-11-01 讀 `cmd_loop_replay`):結果在 `verdict.json` 的 `verdict.rc`,判定不過也會寫檔(255 個代碼審判定檔有 6 個 rc=1);無輪次與舊 panel 帳的迴圈拒凍;凍結跳過第八步跑滿回顧。重凍要帶 `--note`,卷證要先提交。
- 帳上事實(2026-10-01 起的 code 迴圈,160 個):有判定檔 132 個;高風險 5 個、標準級 9 個沒有,部分可能是棄案,沒逐一確認;輕量 11 個沒有。標準級無輪次 2 個、舊迴圈分級空白且無輪次 7 個,這些凍不了。輕量但有輪次 8 個。

## 做法

1. `lumos code-loop pass` 新增 `--loop <編號>`,`skip` 也收但不驗。
2. 審查帳路徑固定 `<repo 根>/docs/.canary-log.jsonl`,跟 `_codeloop_gov_log` 同根。vault 不在 `docs/` 底下的專案視同沒有帳。不為讀帳建 `Env`。
3. 寫入前判定,依序,任何一條擋下都回 rc2、不寫 marker 與放行事件:
   - 帳檔不存在 → 不驗,行為照舊(這條是 vault-free 專案的相容邊界);帶了 `--loop` 就照寫 `nodes` 並印一句「這個專案沒有審查帳,沒有驗」。
   - 帳檔存在但讀不到 → 擋。
   - 沒帶 `--loop` → 擋,訊息給帶編號的完整指令,並點出不審要走 `skip`。
   - 編號含路徑字元(同 `cmd_loop_replay` 的三種)、不是 `code-` 開頭(同 `_roster_kind`)→ 擋。歷史編號 `codestage`、`code側刪除傳播守衛` 不受理,這兩個都是 2026-08 以前的舊案。
   - 帳上沒有這個編號的列 → 擋。編號比對跟 replay 一樣用字面相等。
   - 分級取 `_loop_anchor_tier`,輪次格式取 `_loop_round_format`。分級 light 且無輪次 → 放行,不要求判定檔(無輪次拒凍是既有行為)。
   - 其他分級但無輪次或混用 → 擋,訊息指向 `skip` 或補輪次,不給凍結指令(照做也凍不成)。
   - 判定檔不存在、不是合法 JSON、不是物件、缺 `verdict` 或 `all_row_shas`、型別不對 → 擋。不存在時訊息給 `loop replay --freeze` 指令:編號用 `_rf_qloop`,`--spec` 取最後一輪列的 `spec_path`。
   - `verdict.rc` 不是 0 → 擋,印前幾條 `fails`。不比 `engine_rev`:這裡只讀結果,不重算。
   - 現帳指紋跟判定檔 `all_row_shas` 以集合比較不同(判定檔有現帳沒有,或現帳有判定檔沒有)→ 擋,訊息說判定之後帳變了,給帶 `--note` 的重凍指令。逐字重複的列不算變,現帳有 5 個迴圈是這樣(同一列出現兩次),用清單比會誤擋。
   - 每次擋下用 `_gate_event_or_warn(repo_root, "code-loop", "blocked", note, hard=True)` 落一筆,note 以 `pass-refused:` 開頭、帶編號與原因。(`code-loop`, `blocked`)已在 `LOOP_NOT_CLOSE_EVENTS` 分類,不新增種類。撤除條件靠這筆資料。
4. 讀帳把 `cmd_loop_replay` 內 `_load_rows` 的篩法抽成模組層函式,吃帳檔路徑(不靠 `env`),兩邊共用;解碼與切行維持 `read_text(utf-8, errors="replace")` 加 `_ledger_lines`,指紋才對得上。
5. 過了才寫:marker 不變;`_codeloop_gov_log` 加有預設值的 loop 參數,`nodes` 寫 `[編號]`;`_loop_close_stamps` 對 code-loop 放行事件 `nodes` 有字串就直接蓋戳,不依賴 known_loops,空的才走現有全文比對。`_STATS_NODE_SEMANTICS` 補 code-loop 的說明。
6. 最後一輪取 `_disposal_round_groups` 最後一組,用 `_cap_hint_round` 算:紀錄完整、`folded` 大於 0、最高嚴重度是 major 或 blocker 時,印一句「這輪修補還沒人看過」,放行事件加 `unreviewed_fold: true`。輕量無輪次與混用不算。理由見〈不做〉。
7. 改提示與手冊:
   - `code-loop check` 那兩處提示與 `.github/workflows/ci.yml` 的文字帶 `--loop`;原因句「tier=high 且」開頭要保留,`scripts/hooks/pre-push` 的逃逸判定靠它。
   - pre-push 的原因句只改 `pp_cl_reason` 那一份,不在 `scripts/lumos` 另存句子表。
   - `skills/lumos-code-loop/SKILL.md` 與 `reference.md` 裡「pass 本身不回頭驗問閘」同一句改寫;兩份加 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的 `pass` 範例都帶 `--loop`。
   - [[Projects/審查跑滿回顧_計劃]] 那句「目前沒有任何程式拿凍結判定當放行依據」改成指向本篇。
8. 測試:`t_codeloop_pass_survives_bookkeeping_commits` 的第二次 `pass` 在有審查帳的 repo,改版後會回 rc2 而測試忽略 rc,變成假綠;要改帶 `--loop` 或調整帳檔時機,並補一句斷言 rc0。`t_loop_list_open_loops` 的 fixture 註解「nodes 永遠是空的」同步改寫。

## 驗收條款

- [S1] 當 repo 有審查帳而 `pass` 沒帶 `--loop` 時,應 回 rc2、不寫 marker 與放行事件,應 落一筆 `kind=blocked` 帳,訊息 應 含帶編號的指令與 `skip` 出口 [test:t_codeloop_pass_requires_loop]
- [S2] 當 repo 沒有審查帳時,`pass` 不帶 `--loop` 應 照舊成功寫入;帶 `--loop` 應 成功、`nodes` 有編號並印「沒有驗」 [test:t_codeloop_pass_no_ledger_unchanged]
- [S3] 當帶的編號含路徑字元、不是 `code-` 開頭、或帳上沒有列時,應 回 rc2 且不寫放行事件;當帳檔存在但讀不到時 應 回 rc2 [test:t_codeloop_pass_rejects_bad_loop]
- [S4] 當 light 無輪次以外的迴圈,判定檔不存在、不是合法 JSON、不是物件、缺欄位、或 `verdict.rc` 非 0 時,應 回 rc2 且不寫放行事件;`verdict.rc` 為 0 且帳沒變時 應 寫入。判定檔不存在時訊息 應 含帶 `--spec` 的凍結指令 [test:t_codeloop_pass_checks_verdict]
- [S5] 當凍結後帳上多一列或少一列審查紀錄時,應 回 rc2 並給帶 `--note` 的重凍指令;只多規格閘留痕、結局帳列,或逐字重複列時 應 放行 [test:t_codeloop_pass_stale_verdict]
- [S6] 當迴圈分級 light 且無輪次時,應 放行且不要求判定檔;當分級 light 但有輪次時 應 跟標準級一樣驗判定檔 [test:t_codeloop_pass_light_loop]
- [S7] 當標準、高風險或分級空白的迴圈無輪次或輪次混用時,應 回 rc2,訊息 應 指向 `skip` 且不含凍結指令 [test:t_codeloop_pass_roundless_dead_end]
- [S8] 當最後一輪紀錄完整、有折入、最高嚴重度是 major 或 blocker 時,放行事件 應 帶 `unreviewed_fold: true` 並印提醒;沒有折入、只有 minor、該輪沒有處置紀錄時 應 不帶且不崩 [test:t_codeloop_pass_unreviewed_fold]
- [S9] 當治理帳的放行事件 `nodes` 有編號時,關門判定 應 認得該迴圈,即使審查帳沒有這個編號;舊事件 `nodes` 為空時 應 照舊用 `detail` 全文比對 [test:t_loop_close_reads_nodes_first]
- [S10] 當 `skip` 帶或不帶 `--loop` 時,行為 應 跟改動前相同,只多寫 `nodes`,即使迴圈沒有判定檔 [test:t_codeloop_skip_unchanged]
- [S11] 當 pre-push 的原因句與 lumos 的種類比對時,既有守衛 應 維持綠,「tier=high 且」開頭 應 保留 [test:t_prepush_cl_reason_table_matches_lumos]
- [S12] 當讀手冊與擋下提示時,三份手冊與 CI 文字的 `pass` 指令 應 都帶 `--loop`,「pass 本身不回頭驗問閘」那句 應 已改寫 [manual:逐處比對 SKILL、reference、commands/06 與 ci.yml]

## 不做

- 不改 `code-loop check` 與 CI 的判定,只改提示文字:舊留痕照認,合併與新分支路徑不動。
- 不重算處置閘,不驗跑滿回顧。凍結本來就跳過第八步,所以 `pass` 這條路上沒有人驗跑滿回顧。
- 最後一輪修補沒人看第一版擋不了:第三輪修完再派席就是第四輪,要 `cap-decision`,直接擋會把人裁變成每次必走。不是不需要擋,解決這個衝突之前只能記錄。
- 不解 `pass --branch`:那是 [[Projects/code-loop分支留痕一致_計劃]] 的範圍,候選碼在實驗分支,本案不併。
- 不擋刻意偽造:判定檔與帳都在同一個 repo,工具鏈威脅模型把這排除在外;消費專案也只防忘記。
- 標準級與輕量級推送本來就不查留痕,這點不變;這道只在有人跑 `pass` 時生效,實際涵蓋高風險級。

## 實務隱患

已排除:金流:不碰金額與付款。
已排除:對外送出:只寫本機 marker 與治理帳,不對外傳送。
不可逆:治理帳只追加,新寫的 `nodes` 與 `unreviewed_fold` 無法撤。閘類讀者不看 `nodes`,回退不用清帳;`cmd_gov` 統計與 `gov --node` 會把 code-loop 事件算進去,同一提交不同編號不再折成一筆,這是統計口徑變動。
守衛面:`pass` 是推送閘的前置,改壞會擋住全部高風險推送。對策是擋下訊息一律給可照貼指令,`skip` 路徑不動當出口。
相容:消費專案共用同一份工具,合入後一起生效,還沒凍結的迴圈會被擋一次,照訊息凍結即可。舊 panel 帳與無輪次迴圈凍不了,只能走 `skip`。消費專案的審查帳預設不進版控,換機器就是沒有帳,落到不驗;這是放行方向,不會誤擋。
測試:`code-loop pass` 實際 19 處呼叫,只有 `t_codeloop_pass_survives_bookkeeping_commits` 的第二次在有審查帳的 repo,見做法第 8 步。`_codeloop_gov_log` 有測試直接帶六個位置參數,新參數要有預設值。
順序:手冊順序是提交後凍結、再 `pass`;判定檔要先提交是凍結本身的規定,本案只讀工作目錄的檔。
邊界:同分支兩個功能各一個迴圈時只綁一個編號;留痕綁的是 HEAD,範圍涵蓋整條分支,所以綁最後一個迴圈,不收多值。輕量無輪次放行是已知缺口:把迴圈標成 light 就不用判定檔,由下面的回頭條件追。
效能:實測讀整本審查帳(5.8 MB、5518 列)加算指紋約 0.08 秒,實作後重量一次寫進驗證紀錄。

## 回退

還原功能提交即可:`pass` 回到只寫留痕,閘類讀者忽略多的欄位,治理帳不用動。只想放寬時把第 3 步「沒帶 `--loop`」那條改成印提醒,其餘保留。提交編號落地後補在這裡。

## 審計修正紀錄

尚未派審。
