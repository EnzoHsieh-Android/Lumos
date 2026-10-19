severity: major

通才鏡頭,八角度走完。共 5 條,其中 2 條 major。

**固定席(圖譜)**
- design-loop(★INVARIANT★ 處置閘第五步):不影響。diff 沒碰審材 .md 與 .patch 的判斷,也沒碰 `[SN]` 綁定判斷。
- guard-kill、bound-tests-gate、lumos-cli-read、lumos-cli-lifecycle 的合約:不影響。diff 沒動 guard kill 的 rc、`--json`、綁定測試閘、search 濾網、re-inject。
- loop-convergence-recording、pitfalls-code-loop、canary-record未落盤事件:有牽連,見下面第 1、2 條。
- 圖譜沒有寫到 `_TIER_ROSTER` 的 mode 欄,程式裡也沒有人讀它。

1. 寫側放行結局帳,但結局帳寫進去就把有輪次的迴圈毒成讀不了的混用帳
severity: major
   - blocking: 是
   - diff 段落:`_round_format_write_block` 的「結局帳(--outcome)由呼叫端整段跳過」,與測試 S14。
   - 問題:新規則的前提是「寫進去會毒到整個迴圈就當場擋」,而且新增的 `_loop_round_format` 把結局帳算成不帶輪次(S15 靠這點)。可是結局帳自己的寫入被整段免檢,它正是最常見的產生混用的那一筆。
   - 重現(我實跑,在 `/tmp` 臨時 repo):
     1. 記 `canary record none --loop code-x --round r1 --tier standard …`,rc0。
     2. 記 `canary record none --loop code-x --auditor auto --outcome converged`,rc0。
     3. `lumos loop next code-x` 回「有的帶輪次、有的不帶」rc2。
     4. `lumos loop status code-x --disposal --spec snap.patch --repo .` 回「有的帶輪次、有的不帶,分不出哪輪是判定輪」。
     5. 再記 `--round r2` 被擋,訊息叫人換新編號。
   - 影響:收尾寫結局帳之後,這個迴圈的處置閘讀不了,也不能再補輪。S14 把「結局帳寫得進」釘成期望,S15 又證明寫完就不能再記,兩條測試等於把這個洞釘住。
   - 修法:要嘛結局帳也走同一條規則(帶輪次的迴圈寫結局帳就擋或補輪次),要嘛三處讀側(`loop next`、`--disposal`、`--panel`)改成不把結局帳算進混用。不能寫側說結局帳照算、卻放它進去。
   - 引句:「結局帳(--outcome,結構上不能帶 --round)寫進每筆帶輪次的迴圈 → 照舊寫得進。」

2. 跑滿回顧「只擋有人裁紀錄的迴圈」這條守衛不再有測試守住,改的那兩條斷言也變弱
severity: major
   - blocking: 是
   - diff 段落:`t_cap_retro_bad_ledger_fail_closed`。
   - 原斷言:迴圈 `cry` 沒有人裁紀錄,帳壞時 `_cr_record(..., loop="cry")` 要 rc0,證明跑滿回顧的 fail-closed 範圍只到有人裁紀錄的迴圈。
   - 現狀:`cry` 自己那列壞了,現在被新的輪次規則(`_loop_records_checked` 回 lerr)擋成 rc2。斷言改成 `rc2 && 還是 1 筆 cap-ledger-bad && "讀不懂"`。
   - 抓不到的改壞:把 `_cap_retro_record_block` 改成對任何迴圈都 fail-closed,這條測試照綠。「範圍只到有人裁紀錄的迴圈」現在沒有任何測試守住,圖譜裡 loop-convergence-recording 的 ★RISK★ 也沒補上對應測試。
   - 範圍變大:`_loop_records_checked` 在整本帳不是 UTF-8 時會回 lerr,所以只要帳壞,任何帶 `--loop` 的記帳都被擋,不只壞掉的那個編號。
   - 出口變難:「`--skip` 之後照常寫帳」改成「`--skip` 加手改帳之後」,出口多了一步手改,測試註解也沒講這是有意的變更。
   - 修法:補一支測試。迴圈 A 的帳壞(含整本非 UTF-8)時,另一個健康的、沒有人裁紀錄的迴圈 B 該怎麼處理,依計劃寫死;若要擋就改斷言為有意擋並註明,若不該擋就把 `lerr` 限縮到本編號。
   - 引句:「S17 沒有人裁紀錄的迴圈不受跑滿回顧影響(不落 cap-ledger-bad;帳壞改由輪次規則擋)」

3. `--regression-set` 的 none 判法沒併進這次統一的 none 規則
severity: minor
   - blocking: 否
   - 輸入:`--regression-set "none,"`,另外帶 `--findings-set f1 --folded-set f1`。
   - 實際:回「`--regression-set` 有 id 不在 `--findings-set` 裡: ['none']」。同一個值給 `--folded-set "none,"` 則被當空集合。
   - 原因:折入和放行走 `_set_or_none`(用 `_ids` 切完比 `casefold`),`--regression-set` 另寫 `strip().lower() == "none"`(整串比)。同一個 diff 內三個旗標兩套判法。
   - 引句:「rg = [] if str(regression_set).strip().lower() == "none" else sorted(set(_ids(regression_set)))」

4. `_loop_round_format` 的註解說「與讀側共用這一支」,實際只有 `loop next` 用
severity: minor
   - blocking: 否
   - 還有兩處自己數:`loop status --panel` 在 `file: scripts/lumos:14029` 附近,`--disposal` 在 `file: scripts/lumos:28375` 附近,各自重數 `"round" in r`。`loop next` 裡 `n_round` 也還單獨算一遍。
   - 風險:日後再調數法(例如結局帳的算法)只會改到一處,讀側仍會判出和寫側不同的結果。第 1 條就是這類漂移。
   - 引句:「loop next 開頭那道混用守衛與 canary record 寫側共用這一支」

5. `_dispositions_tension_shape` 用字串替換去改別處產生的訊息
severity: minor
   - blocking: 否
   - 問題:`_disp_value_type_err` 的措辭一改,這兩個 `.replace()` 就靜默失效,existing 項的錯誤訊息會多出不相關的「test:<名>」和「其餘寫進 reason」。目前測試 S22 只斷言 `"existing 第 2 項 要是一個字串"`,抓不到這個。
   - 修法:讓 `_disp_value_type_err` 收一個「格式說明」參數,不要事後字串手術。
   - 引句:「errs.append(_te.replace("(path:line 或 test:<名>)", "(path:line)").replace(";多個證據挑最直接的一個,其餘寫進 reason", ""))」

已核對、不列為問題:
- 舊循序 `standard`+`code-` 迴圈仍可不帶輪次寫入,`seq` 條件加 `bool(rounds)` 後 `width`、範本與寫側規則一致。
- `mode` 從 `sequential` 改 `single` 沒有程式讀者。
- 範本的 `--snapshot`、`--scope-lines` 新佔位字,repo 內已沒有舊字串殘留。
- 全新帳本(檔案不存在)第一筆能寫進去。
- `evidence`、`existing` 的型別檢查寫讀兩側都覆蓋。
- 資安提示、指紋提醒只多印、不改回傳碼。

臨時目錄 `/private/tmp/lumos-seat-work/code-記帳與迴圈工具小修/通才-sonnet` 已刪。

最嚴重:major;blocking 共 2 條(第 1、2 條)。
