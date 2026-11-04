severity: blocker

我逐節讀完 spec,13 個函式與 `_loop_first_ts_key`、`_codeloop_pass_read_verdict` 都開檔驗過。我沒有改 repo 的任何檔,臨時目錄已刪。

**核心主張的結論:不成立。** 「直接套風險低既有的檢查,只改列出來的幾處」會在風險高計劃上判錯。原因是這些函式裡藏了沒列出來的「風險低」假設,下面 1、2、4、7、8 條是其中最具體的幾處。

1. 推送前讀帳只留白名單欄位,`red_first` 讀不到,先紅模式的核心判定失效。
引句:「當推送範圍碰到最新留痕帶 red_first 的計劃時,推送前檢查應照風險低同一套查」
severity: blocker
blocking: 是,每份先紅計劃在推送前都會被誤擋、測試也不會被跑,破壞 S5/S6 的核心行為。
- file: `scripts/lumos:15792`:`_SPEC_GATE_PUSH_FIELDS` 沒有 `red_first`。`_spec_gate_ledger_index` 在 `scripts/lumos:15818` 對規格閘留痕列只留白名單裡的欄位,註解也寫「要讀新欄位就加進來,不然讀到的永遠是 None」。
- file: `scripts/lumos:15819`、`scripts/lumos:15827`:`_nogo_ctx` 用這張白名單讀本機審查帳。
- file: `scripts/lumos:15531`:`_spec_gate_pick` 在兩本帳時間相同時本機那筆勝。
- 重現:`_spec_gate_record` 同一個 `rec["ts"]` 先寫審查帳(`scripts/lumos:14294`),再寫治理帳。治理帳事件用 `extra` 蓋掉時間,所以兩筆時間一樣(`scripts/lumos:14301`)。
- 結果:合併後取到的是被剝掉 `red_first` 的本機那筆。`_spec_gate_push_scan` 的 `full` 判斷(`scripts/lumos:16278`)為假,S6 判成「最新留痕沒有 red_first」,每份先紅計劃都被擋成 `high-red-missing`。
- spec 的「跟著改」清單(第 5 點)沒有提到這張白名單。

2. 全靠人驗的先紅計劃:規格閘放行,推送前卻套小改動閘,而 spec 的出口通到死路。
引句:「先紅模式放行、留痕照寫(`manual_only`),不套風險低的小改動閘」
severity: major
blocking: 是,把該放行的先紅計劃擋下,而且 spec 給的誤擋出口(改成 `[manual:]`)走不通。
- 輸入:門判風險高、設計審已過的計劃,所有條款都是 `[manual:]`。
- 規格閘:`_spec_gate_twoway_static` 只印一行「推送時走小改動閘」的資訊(`scripts/lumos:14232`),spec 要的是放行。
- 推送前:留痕的 `tests` 為空,`_spec_gate_push_one` 進 `if not tests:` 分支呼叫 `_small_change_check`(`scripts/lumos:16150`)。spec 只改 `_spec_gate_push_scan`、`_spec_gate_push_stale` 兩處,沒碰這個分支。
- 結果:`_sc_history` 只要落點節點掛 `risk/` 標籤就判「不算小改動」(`scripts/lumos:15675`)。先紅計劃能進風險高,多半就是因為連到帶 `risk/` 標籤的節點,所以這類計劃幾乎必擋。
- 擋下訊息還叫人「升成風險高走設計審」,但它本來就是風險高。
- spec 實務隱患「誤擋」那條說的出口是「把條款改成 `[manual:]`」,改完推送時被這個分支擋住。
- 次要後果:全靠人驗、小改動閘剛好過關的先紅計劃,會在 `scripts/lumos:16419` 被印成「改動風險分級:light」,代碼審只派架構對齊席。

3. 混合型計劃拿不到任何紅燈,卻能拿到「先紅已驗」的留痕。
引句:「天花板五:先紅模式的計劃把所有條款寫成 `[manual:]` 就沒有測試要紅」
severity: major
blocking: 是,該擋的放掉,而且留痕與印出的字樣是假的。
- 輸入:S1 寫 `[manual:…]`(新行為),S2…S10 全標 `[keeps]` 並綁既存且綠的測試。
- 靜態檢查:`_spec_gate_twoway_static` 的「至少一條不標 keeps」把 manual 條款也算進去(`scripts/lumos:14228`),過關。
- 跑完判定:`_spec_gate_twoway_run_verdict` 對 manual 條款直接 `continue`(`scripts/lumos:14248`),keeps 條款全綠就過。
- 結果:規格閘寫入 `red_first: true`、印「PASS(風險高,設計審已過、先紅已驗)」,實際 `n_red` 為 0。
- 天花板五只承認「全部」都是 manual,沒有涵蓋混合型。預期值表只對 S1 要列,對最重要的那條新行為沒有任何紅燈證據。

4. 起點已 done 的寬待對先紅計劃失效,和 S5 寫的相反。
引句:「起點已 done 的寬待照舊,門重判是風險高不算過期」
severity: major
blocking: 是,把 S5 說要放寬的情形擋死。
- file: `scripts/lumos:16138`:`if stale and not (done and now is not None and now.get("door") == "low")`。
- 輸入:先紅計劃(門重判永遠是 high)在範圍起點已是 done,這次推送改了條款或已排除理由,條款指紋對不上。
- 結果:`now.get("door")` 是 high,寬待條件不成立,回傳 `stale` 直接擋。風險低同樣情形只印提醒。
- spec 只改了 `_spec_gate_push_stale`(`scripts/lumos:15750`)。`_spec_gate_push_one` 這個第二處硬寫「門重判仍是低」的地方沒列。

5. 設計審判定檔只做形狀檢查,過期的判定檔會讓先紅模式在設計審重開後照樣啟動。
引句:「以設計審判定檔當開關,避免擋到還在設計的計劃」
severity: major
blocking: 是,d1 自己講的「避免擋到還在設計的計劃」做不到。
- spec 要的是 `_codeloop_pass_read_verdict` 的形狀檢查。判定檔還代表不代表現在的帳,是另一支 `_codeloop_pass_check_verdict` 在比(`all_row_shas` 對現帳,`scripts/lumos:68535` 附近),spec 沒借。
- 輸入:設計審通過後凍結,判定檔 `rc=0`,之後在同一個迴圈編號又開 `lumos loop next` 新一輪,新一輪有未處置的 major。
- 結果:判定檔仍是 `rc=0`,S6 照樣擋推送,訊息卻說「設計審已過」。
- 反方向也有洞:重凍沒帶 `--note` 會被擋(`scripts/lumos:1380`),舊的 `rc≠0` 判定檔會留著,先紅模式靜默關掉。
- 判定檔被手改的行為:`rc` 改成 1 或刪檔就關模式。這是單人依序操作的威脅模型,我不另報。

6. 迴圈首筆帳讀的是消費專案預設被忽略的本機帳,「讀不到」該怎麼判沒定義。
引句:「審查帳裡這份計劃的迴圈編號最早一筆非結局帳的時間」
severity: major
blocking: 是,spec 沒定義 None 時的行為,實作任選一邊都會判錯。
- file: `scripts/lumos:14975`:`_loop_first_ts_key` 只讀 `env.vault.parent/.canary-log.jsonl`,沒有就回 None。spec 自己在名詞段說審查帳「消費專案預設被 git 忽略」。
- 輸入:消費專案的新 worktree 或乾淨 clone,判定檔(在 `governance/replay/`)跟著版控,本機審查帳不在。
- 現有用法(`scripts/lumos:14998`)是 `first is None or ...` 當新計劃處理。照這個走,所有生效日之前、判定檔 `rc=0`、狀態還是 doing 的風險高計劃,一被碰到就被誤擋 `high-red-missing`。
- 反過來把 None 當不成立,先紅模式在 worktree 裡整個失效。專案全域規則要求每個任務用獨立 worktree,這就是常態路徑。
- spec 對規格閘留痕用「兩本帳合併讀」,生效基準卻沒有對應的合併讀。

7. 「套風險低同一套」並不成立:規格閘前半把 `door` 傳給 `_clause_check`,高低走不同分支。
引句:「風險高的計劃在設計審過了之後,規格閘與推送前檢查都把它當風險低一樣查」
severity: major
blocking: 是,先紅模式少了風險低的「測試名互不相同」檢查,「各自紅」可以被一支測試灌滿。
- file: `scripts/lumos:14788`:`_clause_check_twoway`(測試要存在、名字互不相同)只在 `door == "low"` 時跑。
- file: `scripts/lumos:15003`:零條款只對低擋。
- 輸入:先紅計劃 S1…S10 全寫 `[test:t_one]`,`t_one` 紅。每條都被 `_spec_gate_twoway_run_verdict` 判紅,規格閘放行。`_clause_check_twoway` 的說明寫得很清楚:「十條全綁同一支也能全部存在,所以擋」。
- spec 自己的驗收條款就犯這條:S1/S2/S4 共用 `t_spec_gate_high_red_first_mode`,S6/S7、S10/S11、S13/S14 也各共用一支。若實作改成把 `door` 當 low 傳進去,這份計劃自己會被擋;若維持 high,就少了這道檢查。
- spec 沒說先紅模式傳給 `_spec_gate_clause_part` 的 `door` 是哪個。

8. 規格閘重跑時,「已做完」的短路只認風險低留痕。
引句:「沒過交給 `_spec_gate_low_not_red` 印同一套補紅燈做法」
severity: major
blocking: 是,有效留痕的計劃重跑規格閘被回 1。
- file: `scripts/lumos:15369`:`rec and _rec_plan_risk(rec) == "low"`。
- 輸入:先紅計劃已有 `red_first` 留痕,實作做綠後再跑一次規格閘。
- 結果:新行為條款綠,`_spec_gate_low_not_red` 的 (a) 條件因留痕是 high 不成立,落到 (b) 回 1,印四步「換回空殼」的補法。風險低同樣情形是 rc0「已做完,不用重跑」。
- spec 只說「訊息裡的風險低改照模式講」,沒提這個條件。
- file: `scripts/lumos:16165`:`_spec_gate_push_one` 裡還有一句寫死的「改成 plan_risk: high 走設計審」沒列入改字串清單。

9. S1 說弱證據也會印補紅燈做法,程式只在「全是已綠」時才印。
引句:「測試是綠或弱證據時,規格閘應擋下並印出補紅燈的做法」
severity: minor
blocking: 否,擋下的判定是對的,只是 S1 的驗收字面對不上輸出。
- file: `scripts/lumos:15362`:`_spec_gate_green_only` 有任何非綠的情形就回 `[]`,補法整段不印。
- 輸入:新行為條款的測試篩選選中 0 支(弱證據)。`_spec_gate_low_not_red` 只印「沒過放行條件」清單就回 1,沒有補法。
- 照 S1 寫的測試 `t_spec_gate_high_red_first_mode` 會紅在這裡。

10. 不做清單略過危險詞的輕量審綁定,也會套到先紅計劃。
引句:「之後同一支 `_spec_gate_push_one`:條款指紋過期要重跑、留痕裡的測試全綠才放」
severity: minor
blocking: 否,有出口(重審),且只在不做清單有危險詞時才發生。
- file: `scripts/lumos:16144`:`_spec_gate_push_one` 不分門別,對 `now["nogo_skipped"]` 都叫 `_spec_gate_push_light`。
- 輸入:先紅計劃的「## 不做」裡有「不做退款…」這類被略過的危險詞行,設計審最後一輪之後(寫回圖譜、折入)改了那一行的字。
- 結果:`_nogo_review_unbound`(`scripts/lumos:16009` 附近)比快照裡被略過的行雜湊,對不上就擋,要求在現在這版上重審。
- 這條路是為沒人審的風險低計劃設計的。spec 沒討論它對已過設計審的計劃是否適用。本計劃自己沒有被略過的行,我實跑確認過。

11. S7 只提醒、S13 卻擋:「碰到」的範圍沒定義。
引句:「當推送範圍碰到先紅模式的計劃,而預期值表檢查不過(含整節刪掉),或現在的表指紋不在這份計劃任何一筆 expected-signed 事件裡時,推送前檢查應擋下」
severity: minor
blocking: 否,⚠ 判不準 S13 是否包含只因落點被拉進來的計劃。
- file: `scripts/lumos:15845`:`_spec_gate_push_candidates` 會把連到被改程式檔的家的 doing 計劃拉進來。
- 若 S13 的「碰到」包含這種計劃:任何人改動 `Systems/規格閘` 管的檔,都會被別人尚未簽表的先紅計劃擋下。S7 對同一類只印提醒。兩條的範圍應寫成一致。

12. 預期值表的「同名節出現兩次」無法靠指定的函式判出。
引句:「找節用 `_h2_section_lines` 找 `## 預期值表`;同名的節出現兩次、或節裡沒有表、或表在程式碼圍欄裡,都算格式錯。」
severity: minor
blocking: 否,是可執行性缺口。實作者必須另寫一套找節,或漏掉重複節。
- file: `scripts/lumos:13774`:`_h2_section_lines` 遇到第二個同名標題時只是重新設 `inside=True`,把兩節的行併成一個清單,不回傳節數。
- 輸入:兩個 `## 預期值表` 節。第二節只放資料列、沒有表頭,併進第一節後被當同一張表,檢查通過。
- 函式說明明寫「找節邏輯不准長出第三套」。

13. `signoff --expected` 幾個未定義的出口。
引句:「沒有互動終端或逾時記 ai 並印記成 AI 簽,答 n 印沒簽而且不寫」
severity: minor
blocking: 否,不影響已定義的放行判定。
- 答 n 的回傳碼沒寫(S11 只定義錯誤回 2),`t_signoff_expected_table` 無法釘。
- 現有 `--by` 是簽的人(`scripts/lumos:72901`),`--expected` 的 `by` 是 human 或 ai,兩者並存時怎麼處理沒寫。
- 計劃不在先紅模式時 `signoff --expected` 允不允許沒寫。
- `--no-run` 是否跳過表格檢查也沒寫:`_spec_gate_front` 在 `scripts/lumos:15282` 就提早 return 0。

14. 效能一條的依據不對。
引句:「推送前多讀治理帳的簽核事件,跟現有的留痕索引同一趟讀(`_spec_gate_gov_index`),不另外整本再讀」
severity: minor
blocking: 否,量級很小。
- file: `scripts/lumos:15492`:`_spec_gate_gov_index` 只讀 gate=`spec-gate`、kind=`spec-gate-record`。`expected-signed` 的閘是 `signoff`,同一趟讀不到,要多讀一次治理帳。
- 實測治理帳 21MB、審查帳 6MB,整本解析 0.06 秒,不構成問題。要改的是說法。

15. 自動記逃逸的語意與副作用沒交代。
引句:「先紅模式計劃的擋下照風險低一樣自動記逃逸(`_auto_escape`)」
severity: minor
blocking: 否,影響統計與別份計劃的小改動閘。
- 風險低的前提是「沒人審,所以推送閘擋下就是下游抓到的洞」。先紅計劃有設計審,測試還沒綠的推送被記成 major 逃逸,會污染 RETIRE-IF 引用的逃逸帳。
- file: `scripts/lumos:15676`:`_sc_history` 讀近期逃逸帳,同落點的別份全靠人驗風險低計劃會因此被判不算小改動。
- `high-red-missing` 和 `expected-unsigned` 兩種擋下是否也自動記逃逸沒寫。`_auto_escape` 對 `push-gate-unreviewed` 有風險高跳過的守衛(`scripts/lumos:20068`),這兩種不在其內。

**固定席節點的判定:**
- `guard-kill`(rc 優先序 INVARIANT 與 `--json` 純度 INVARIANT):第一批不碰 `guard kill`,第二批變異測試也只是「另開計劃」,不影響。
- `test-quality-cli`、`test-quality-evidence`、Verification 測試品質第四輪:第一批不改 `scripts/test_quality.py`(spec 明說只借不改),不影響。
- `lumos-cli-lifecycle` 的 re-inject INVARIANT:spec 第 5 點要改注入範本裡的一句話,但 re-inject 只覆蓋 sentinel 之間的內容,sentinel 之外 byte-equal 保留的行為不受影響。
- `test-guard` 只在凍結提交裡,會談目錄沒有,我沒法比對。

**實務隱患逐類:**
- 併發:無新問題。`_gate_event` 寫版控治理帳沒上寫入鎖,但每筆帶獨立 token、讀側按時間與 token 取最新,簽核按表指紋比對,兩個會談同時簽或同時跑規格閘不會互相覆蓋。
- 效能:無。見第 14 條。
- 資源:無。判定檔最大約 108KB(`governance/replay/code-待決問題改存開頭欄位/verdict.json`),讀取不限長度沒有實際風險。
- 回滾:回退節自述一致。補充一點,常數設遠未來後帶 `red_first` 的舊留痕仍走風險低全套,條款一改就重跑,重跑時已不在先紅模式、照舊只印,行為自洽。

最嚴重 severity: blocker;blocking 條數 8(第 1、2、3、4、5、6、7、8 條)。
