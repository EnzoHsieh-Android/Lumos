severity: major

審的是 `規則包語意覆核級命中走盲判` 的 r1 快照。我讀完整份 spec,並對照 `scripts/lumos` 的相關函式查證。以下行號都以 `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos` 為準。

## Findings

### F1(範圍 2、4、5)`--template` 重跑與 check 當下用的不是同一個改動範圍,會出現「擋下卻無材料可判」的死局
severity: major
blocking: 是(判準:會讓推送擋下後走不出去,只剩 `lint-waive` 這條逃生門)
- 問題:spec 說 `--template` 用「同一個改動範圍」重跑,但沒說是哪個範圍。
  - check 的新增告警閘用的是原始推送範圍 `diff_range`。
  - 盲判用的是 `_codeloop_disp_range` 重算的範圍,也就是主線把分岔點併進來後的 `merge-base..sha`。
  - 兩者在「把主線合進分支再推」時不同。
  - 結果是 check 說有新增覆核命中、要盲判,`--template` 卻算出 0 筆,印出空材料。
  - 結果檔寫入時的驗證又要第三次重跑。一次推送最少重跑 4 次(check、template、record、再 check),有 `unsure` 還要加 2 次,每次都要重新取出兩份快照。
- 同一類洞已經在情境題出現過。`_codeloop_disp_range` 的註解寫著「code-loop check 與盲判共用這一支……兩邊範圍一對不上盲判就核不到」。
- spec 的覆核命中沒走這支共用函式。
- 引句:「資料來源是 `--template` 當下用同一個改動範圍重跑覆核命令(呼叫範圍 2 那支,不從上一次 check 取)」
- file: `scripts/lumos:73997`(`_codeloop_disp_range`)
- file: `scripts/lumos:74160`(盲判取範圍)
- file: `scripts/lumos:74556`(check 的 `_codeloop_lint_new_step` 傳的是 `diff_range`)

### F2(範圍 2、5)判定查詢缺管線:新增告警閘那一步沒有 branch、at_sha,也沒有合併側處理
severity: major
blocking: 是(判準:主線合併推送必然擋下)
- 問題:盲判紀錄是依「分支名」折出來的,合併提交走 `_disp_bj_source` / `merge_ledger` 改讀合進來那一側。
  - 但 `_codeloop_lint_new_step(repo_root, diff_range, tier)` 與 `_lint_new_verdict` 都沒有 branch、at_sha、merge_side 參數。
  - spec 要在這條路上把 `review_new` 對照規則判定,卻完全沒寫這些怎麼傳。
  - 若照字面實作成讀 `branch=main`,PR 分支上判完的覆核命中,合併進主線時會一律當成「還沒判」而擋下。
  - 這正是 `Projects/合併進主線認合進來那側的留痕` 當年在 PR #28 踩過的洞。
- 引句:「覆核命中放在判定結果的 `review_new`,`_lint_new_classify` 的「有新增就擋」只看一般段。」
- file: `scripts/lumos:74556`
- file: `scripts/lumos:74237`(`_disp_bj_source`)

### F3(範圍 2)新路徑掛在 `_codeloop_lint_new_step` 的 `except Exception` fail-open 之下,覆核程式一出例外,整道新增告警閘連一般段一起放行
severity: major
blocking: 是(判準:新程式的任何 bug 會讓既有的守衛靜默失效)
- 問題:`_codeloop_lint_new_step` 整段包在 `except Exception → _gate_failopen → lv=None`,也就是整道閘放行。
  - 覆核路徑新增了幾處容易丟例外的操作:importlib 借 `check.py` 的 `main_rows`、讀型錄、第二次呼叫 `_lint_new_diff_claims`、對帳查判定。
  - 其中任何一處丟例外,放行的就是整道閘,連原本會擋的一般段命中都放掉。
  - spec 沒要求把覆核分支自己 try/except 隔離。
  - 作弊比對那條路已經刻意「自己包住例外」,就是為了不漏到外層。
- 引句:「覆核命令沒跑到(預算用完、工具沒裝、逾時)記進 `review_undone`,只講出來、不擋(見範圍 6)。」
- file: `scripts/lumos:74562`
- file: `scripts/lumos:74564`

### F4(範圍 2、6)覆核沒跑只印一行、不記治理帳,而且預算用盡不擋,與本閘對預算用盡「擋」的既有立場相反
severity: major
blocking: 是(判準:新增一條可被靜默繞過的路,而且沒有可統計的痕跡)
- 問題:
  - 既有 `_lint_new_run_cmds` 在預算用完時記 `undone`,並明寫「判定跟檔太大同類(擋),不歸自動放行」。
  - 環境不可用的自動放行會進治理帳,由 `_lint_new_autopass_count` 統計,註解稱它是「帳是可以統計的」的兌現。
  - 本案的覆核預算用完、工具沒裝、逾時,只印一行、不擋、也不記帳。
  - 一般段吃掉 270 秒以上、剩不到單條保底 30 秒時,覆核整個跳過,而且沒有任何事後可查的紀錄。
  - 專案越大越常發生,「實務隱患」只寫「推送前那一行會講」。
  - 推送前那一行是事後看不到的臨時輸出,REVISIT 也沒有計數項。
  - CI 在沒有 ast-grep 或時間不足時同樣略過,等於 `real` 判定在 CI 端不被執行。
- 引句:「一般段吃光時覆核記成「沒跑」不擋,所以專案很大時覆核可能常常沒跑。推送前那一行會講,doctor 不另唸。」
- file: `scripts/lumos:42674`(預算用完記 undone 並擋)
- file: `scripts/lumos:42749`(自動放行計數)

### F5(範圍 4、5)記帳兩步不原子,一步失敗後重試永遠補不上放行
severity: major
blocking: 是(判準:部分失敗後無法自癒)
- 問題:記帳要先寫治理帳(`_codeloop_gov_append`),再逐筆寫放行檔(`_lint_waivers_add`)。spec 沒訂順序,也沒訂失敗時怎麼處理。
  - 若帳寫成功、放行檔寫失敗(放行檔壞掉、鎖逾時、`_lint_waivers_add` 回「已放行過了」),重試同一份結果檔會撞到 `len(skipped) == n`。這條路會回 2、不寫帳,放行也補不上。
  - 結果是判誤報的命中永遠進不了「AI 放行複查清單」,與 S4 與 d3「判成誤報的不直接消失」直接矛盾。
  - 反過來若先寫放行、帳失敗,放行存在、判定不存在,統計對不上。
  - 一份檔最多 30 筆、逐筆各寫一次放行檔(每次整檔改寫),中途失敗也是半套狀態。
- 引句:「記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行:origin 是 ai、理由是「盲判判誤報:<判定理由>」」
- file: `scripts/lumos:74217`(整份都已有紀錄就擋下、不寫帳)
- file: `scripts/lumos:42297`(`_lint_waivers_add` 遇到已存在的鍵回 False)
- file: `scripts/lumos:73202`(`_codeloop_gov_append`)

### F6(範圍 3、5、天花板 1)覆核級的前提是「同一段文字可真可假」,卻讓一個判定與放行覆蓋同檔同片段的所有處,放行還是永久、不分分支
severity: major
blocking: 是(判準:這一級最典型的案例會漏判真問題)
- 問題:材料取檔內最後一處。判 `false` 就寫一筆以指紋為鍵的放行。
  - 放行鍵是 (規則, 檔名, 命中行片段) 的雜湊,在放行檔裡全域生效。
  - 同一檔內 `x.setValue(v)` 前面一處是 Firebase、後面一處是 LiveData 是這類規則的典型情況,後者的真問題因此永遠不再被判。
  - 之後同指紋的新增命中,在 `kept = [c for c in new if c.get("key") not in waivers]` 就被濾掉,根本到不了盲判。
  - spec 只把它列為天花板 1,沒有緩解。
  - 另外,情境段的段身分綁材料內容,所以「程式改過就要用新材料重判」。覆核命中的 `seg` 不綁上下文,判定因此不會失效,也無法重判。
  - `_kt_bj_cells_add` 的「同一格只認第一筆」又讓錯判無法覆蓋。
  - 人複查若判 `overturn`,spec 也沒說放行要撤掉,真問題照樣放行。
- 引句:「同檔同片段的多處共用同一個身分與同一個判定。」
- file: `scripts/lumos:42219`(`_lint_new_key`)
- file: `scripts/lumos:42244`(`_lint_new_diff_claims`)
- file: `scripts/lumos:42628`(`kept` 以放行鍵過濾)

### F7(範圍 4)盲判入口與結果驗證寫死綁情境題,沒有規劃覆核命中單獨走的路
severity: major
blocking: 是(判準:照 spec 字面實作會直接跑不通)
- 問題:
  - `_cmd_codeloop_blind_judge` 一開頭,型錄決策表有錯(`_KT_DT_ERR`)就整個擋下。接著 `_kt_bj_segments` 先算情境段,算不出來就回 2。
  - 情境題的前置條件壞掉時,覆核命中也無法判,而 d2 又要求沒判就擋推送,等於無出口。
  - `_kt_bj_validate` 的 `lst` 為空會直接回「要有 segments 清單」。只有 `rule_hits` 的結果檔(spec 說「可以單獨一份」)會被拒收。
  - spec 只寫「擴充認這個鍵」,沒提空 `segments` 這條。
  - 材料份數 `parts` 是照情境段算的,spec 沒說 `rule_hits` 的份數、`--part` 編號、stdout 怎麼區分。
- 引句:「結果檔:頂層多一個鍵 `rule_hits: [{"seg": <指紋>, "verdict": "real|false|unsure", "reason": "…"}]`,可以跟 `segments` 同檔或單獨一份」
- file: `scripts/lumos:74188`
- file: `scripts/lumos:74070`
- file: `scripts/lumos:74075`

### F8(實務隱患:盲判成本、帳膨脹)上千筆命中沒有硬上限,帳與放行檔跟著膨脹
severity: minor
blocking: 否(判準:給得出具體數字,但屬規模問題,上線前量測可補)
- 問題:每份最多 30 筆(`_KT_BJ_PART_MAX`),上千筆命中就是約 34 份,每份派一個全新代理。
  - 檔案改名會讓整個檔案的舊命中以新檔名重新算成新增。
  - 每次推送重派,上限沒寫。
  - 每筆理由最長 2000 字,一份最多約 60KB,寫進已有 22MB 的版控治理帳。
  - 放行檔每筆放行整檔改寫。
- spec 只寫「上線前量一次」,沒有超過 N 筆就停手或改人判的退路。
- 引句:「命中多時材料分份(每份 30 筆)。」
- file: `scripts/lumos:73815`
- 帳大小:`docs/.governance-log.jsonl` 約 22MB(`ls -la` 實測)

### F9(用詞、範圍 7)不帶 `--verdict` 的 `--ack --all` 會讓準確率分母永遠是 0
severity: minor
blocking: 否(判準:只影響統計與撤除條件,不影響擋停)
- 問題:現有人複查那 62 筆待看清單的常態動作是 `--ack --all`。spec 規定沒帶 `--verdict` 就「只記看過、不進準確率」,而 RETIRE-IF 與 S8 的建議都靠這個數字。
  - 批次 ack 之後這些筆永遠不進統計,RETIRE-IF 永遠無法判。
  - spec 沒說批次 ack 要不要帶或拒絕這個旗標。
- 引句:「不帶 `--verdict` 的 ack 照舊只記看過、不進準確率。」
- file: `scripts/lumos:41192`(`_lint_waive_ack` 只有 `--all` 或單鍵,沒有 verdict 欄)

## 逐節結論
- 前言、狀態、用詞:已讀。除 F9 外無 finding。
- 範圍「做」1(分流、`review` 段):已讀,無 finding。S9 的工作樹模式不跑,與 `_lint_new_verdict(worktree=True)` 的分流相容。
- 範圍 2:F1、F2、F3、F4。
- 範圍 3:F6。
- 範圍 4:F1、F5、F7。
- 範圍 5:F2、F5、F6。「unsure 的 `--template --unsure` 與 `--arbiter`」沒有衝突,但跟現有 `--missing/--disagreements` 模式的互斥關係沒寫,不另列。
- 範圍 6:F4。
- 範圍 7:F9。
- 範圍 8、不做、實務隱患:F8。
- 依據來源、驗收條款、預期值表、回退、天花板、審計修正紀錄:已讀。
  - 驗收條款缺 F1、F2、F3、F5 對應的條款,沒有任何 `[S*]` 涵蓋「template 與 check 結果一致」、「合併提交認合進來那一側」、「覆核例外不拖垮一般段」、「記帳半途失敗可重試」。
  - 交叉引用的目標都存在(`#d1`~`#d3`、〈範圍〉各項、`Systems/*` 節點)。

## 固定席節點判:這份設計會不會破壞宣稱的行為或合約
- `Systems/pitfalls-code-loop`:有影響,但不是破壞節點宣稱的合約,三個節點都沒有掛合約行。這份設計動到「新增告警閘」那條路,風險在 F3(出例外時全閘放行)與 F2(合併推送)。該節點的 KEY 行提到「linter 那隻手……fail-closed」的精神,與 F3 的做法相反,建議在落地時對齊。
- `Systems/kotlin規則包`:不影響合約,但有張力。該節點的 RULE 說「規則在真專案誤報超過命中的一成就降提示級或改形狀」,覆核級把這類規則留在原級,靠盲判消化。spec 的撤除條件(準確率九成)與它是同一條線的不同量法,沒矛盾,但要寫清楚誰優先。
- `Systems/linter精選目錄`:不影響。範圍 8 只改範本與「提示級預設不接」那一句。

最嚴重 severity:major;blocking:是 7 條(F1–F7),blocking:否 2 條(F8、F9)。
