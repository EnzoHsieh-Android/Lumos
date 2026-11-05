severity: blocker

我讀完整份 spec,並對照 `scripts/lumos`、`skills/kotlin-idioms/checks-catalog.md`、`configs/ast-grep/kotlin-android/` 做了驗證。最重的洞在範圍 8 跟既有程式接不上:新增告警閘沒有分流機制,表態核對在沒有適用題時整段早退,而且它吃的資料刻意不跑 lint。範圍 1–7 內部也有兩處會卡死作者。

**1. 範圍 8 要求「命令的告警不進新增告警閘」,程式裡沒有任何可以做到的機制,spec 也沒把機制列進範圍**
severity: blocker
blocking: 是
引句:「命令的告警不進「新增告警就擋」那一道,改進這一道」
- file: `scripts/lumos:40003`(`_lint_new_tools`)與 `scripts/lumos:39155`(`_lint_run_and_parse`)。`_lint_new_run_cmds` 對 `.lumos/lint.json` 的每條命令一視同仁,只靠 `_lint_gate_covers` 判有沒有 `{LINT_FILES}`,沒有「這條命令是覆核級」的標記。
- SARIF 解析不看 `level`,所以 info 級命中全部進 `out["new"]`。`_lint_new_classify` 再把有 `new` 的情況判成 blocked。
- 失敗情境:專案照 spec 在 lint.json 加 `sgconfig-review.yml` 那條命令,第一筆新增的覆核命中就被新增告警閘直接擋下,根本到不了盲判。
- 需要的程式改動(命令分類、`.lumos/lint.json` 格式驗證 `_lintcheck_validate` 怎麼認這個標記、`lumos lint-waive` 能不能放這類命中)都沒列進範圍 8,也沒進 S9 的驗收。
- 目前 `rules-review/` 目錄是空的(沒有任何規則檔),這條路徑沒有任何實作可以對照。

**2. 範圍 8 的核對放不進「表態那一道」:沒有適用題時早退,而且那一道吃的資料刻意不跑 lint**
severity: blocker
blocking: 是
引句:「推送前核對:每個覆核段要有盲判判定;判 `real` → 擋」
- file: `scripts/lumos:70636`(`_dispositions_verdict`)開頭 `if not app or cfg["mode"] == "off" or (cfg["mode"] == "high-only" and tier != "high"): return out`。
- 一個只有覆核級命中、沒有任何情境觸發字的改動,`app` 為空,核對直接早退,S9「沒有判定應擋」不成立。
- 範圍 2 說 `stack_questions.gate` 設 `off` 或 `high-only` 時盲判核對跟著不跑,範圍 8 的 `lint_new.gate` 是另一個設定,兩者哪個管覆核段沒講。
- file: `scripts/lumos:71057` 附近,`disp_data` 由 `pitfalls --diff ... --no-lint --json` 產生。算覆核段需要在改動前後兩份快照各跑一次 ast-grep(新增告警閘的基準比對),這條資料路徑刻意不跑 lint。
- spec 沒說覆核段在哪裡算、放進哪個回傳結構、預算(`_DISP_BUDGET`)與超時放行怎麼算。
- 「這一道」本身也有歧義,也可能被讀成新增告警閘(`_codeloop_lint_new_step`)。

**3. `kt-situation` 在行數超過門檻時會變成「適用但沒有任何段」,而且只收 satisfied,作者無路可走**
severity: major
blocking: 是
引句:「這一題不收 na、todo、tension(那三種會讓作者繞過整套核對)」
- file: `scripts/lumos:38177`(`_stack_applicability`)。`over = len(raw_lines) > threshold` 時,所有非 `shape_only` 的題整棧適用。spec 只把 `kt-situation` 標 `android_only`,沒標 `shape_only`。
- 失敗情境:一個大的 Kotlin 改動沒有任何觸發字,`kt-situation` 照樣適用,`segments` 是空的。作者只能填 satisfied,卻沒有任何一段可引證。這時候不知道是空 `segments` 算過還是算缺證據,全看實作怎麼猜。
- 同函式簽名只收 `lines_by_stack`,沒有 repo 或版本參數,但「切不出段就視同不適用」需要讀被推版本的檔案。spec 沒說這個資料怎麼穿進去。

**4. 新增的事件種類沒有登記:放行事件漏登記,而且 CI 重建時會丟掉放行**
severity: major
blocking: 是
引句:「寫治理帳並併進同一個標記檔的 `waived` 格」
- 範圍 5 寫治理帳,但沒給事件種類名。範圍 4 只登記 `blind-judge` 進 `LOOP_NOT_CLOSE_EVENTS`。
- file: `scripts/lumos:19349` 與 `scripts/test_lumos.py:64576`(`t_loop_close_kinds_classified`)。任何新的 `(gate,kind)` 沒歸類,守衛就翻紅,所以 `situation-waive` 漏登記會紅。
- 讀側重建只說「把這個分支所有 `blind-judge` 事件依行序重建」,沒說也讀放行事件。標記檔(不進版控)被刪,或在 CI 上時,`waived` 格重建不出來。本機放行過的段在 CI 又被擋,跟 spec 自己說的 CI 是後盾矛盾。
- 覆核段的放行走「新增告警既有的放行指令」(waivers 以 claim key 為鍵),跟段身分是兩套鍵。S9 沒有驗證「照放行指令放行後不擋」的鍵對得上,而覆核命中如果不在 `out["new"]`(見第 1 條),那條指令根本找不到它。

**5. `blind-judge` 的寫入與模板只定義了情境段的格式,覆核段(沒有 row)接不上**
severity: major
blocking: 是
引句:「`row` 不在那段的候選列也不是 `none` → 寫入時拒收(rc2)」
- 情境段的結果格式是 `{seg,row,followed,reason}`,覆核段是 `{seg,verdict,reason}`,寫入與驗證要依段種類分流。spec 沒說怎麼分。
- 照字面,覆核結果沒有 `row`,拒收規則會當成缺欄。
- `--template` 的欄位(候選列三欄、前後 10 行)與覆核材料(規則訊息、壞寫法、標準寫法)不同,`--missing`、`--disagreements` 與每份 30 段的上限怎麼算覆核段也沒寫。
- S5 只驗情境段。範圍 8 說「記錄、讀寫、仲裁都跟情境段同一套」,實際是兩套格式。

**6. 停用字表擋不住複合觸發字,實際會讓大部分 Kotlin 改動都出情境段**
severity: major
blocking: 是
引句:「觸發字收了常用字會讓段數暴增——第一批型錄格式檢查用停用字表擋」
- file: `configs/ast-grep/kotlin-android/check.py:79`(`STOP_TRIGGERS`)與 `check.py:147`。檢查是整字精確比對。
- 型錄 D-23 的觸發字有 `suspend fun`,每個新增的 suspend 函式都命中,不在停用字表裡。
- D-5/D-6 有 `StateFlow`,幾乎每個 ViewModel 都有。D-20 有 `withContext`、D-17 有 `viewModelScope`、D-19 有 `GlobalScope`/`Deferred`,都是常見字。
- 失敗情境:每次推送幾乎都要填 `segments`、派盲判(沒有任何 tier 條件,見下一條),成本不會是 spec 所說的偶爾。
- RETIRE-IF ③「整組情境段八週內少於 5 段」的反向風險是段數暴增,spec 沒有對應的退場條件。

**7. 盲判不看 tier,與「在代碼審迴圈裡跑」的說法不一致**
severity: minor
blocking: 否
引句:「推送前沒有盲判記錄就擋,所以不靠人記。」
- 表態核對不看 tier(`scripts/lumos` 約 71040 的註解寫明),手冊卻放在 `lumos-code-loop`(只在 tier: high 才觸發)。
- 低風險推送只要有一個情境段,就要派 sonnet 子代理才能推。「不做」段寫「盲判在代碼審迴圈裡跑」與實際行為不符。

**8. kt-situation 頂層 `evidence` 與既有 satisfied 驗證衝突**
severity: minor
blocking: 否
引句:「`kt-situation` 適用時只收 satisfied,而且多一個欄位 `segments`」
- file: `scripts/lumos:70059`(`_dispositions_validate`)。satisfied 必須附頂層 `evidence`(`path:line` 或 `test:`),`_one` 還會去驗它。
- spec 只定義了每段的 `evidence`,沒說頂層怎麼辦。照字面實作的 `{status:satisfied, segments:[…]}` 會被擋。

**9. 段身分不含位置,內容相同的兩段(複製貼上)會撞身分**
severity: minor
blocking: 否
引句:「`sha256(檔路徑 + "\0" + 段範圍的原文 + "\0" + 候選列編號清單)` 取前 16 碼」
- 同一支檔裡兩個內容相同的段身分相同,證據範圍卻不同(±20 行)。
- 作者的 `segments` 只能有一筆,evidence 只能落在其中一個範圍裡,另一個要靠放行。
- 覆核段的身分(路徑+規則+前後 3 行)有同樣問題。
- 相鄰段的證據範圍也大幅重疊,同一行 `.await()` 可以當相鄰兩段的證據。

**10. 範圍 8 的依據段含未經查證的宣稱**
severity: minor
blocking: 否
引句:「Semgrep 與 Datadog 在固定規則上疊模型判誤報,只在有把握時判、判成誤報的不自動關而是可以複查,準確率底線九成」
- 我實際抓了該 Semgrep 頁面,頁面完全沒提 Datadog。
- 頁面說的是:雜訊過濾「never close a finding」,被濾掉的發現是隱藏起來給資安團隊批次複查。九成準確率底線這句有,也在頁面上。
- 範圍 8 卻讓 `false-positive` 判定直接放行、只計數,沒有複查機制,跟它引用的做法剛好相反,「判定留痕可複查」只做到留痕。
- 另外「第一筆為準」把第一個盲判的誤判鎖死:判錯 `false-positive` 的真問題靜默通過,判錯 `real` 只能改碼或放行。⚠ ZeroFalse 與 Wagner 兩篇我沒去驗「三到四成」這個數字。

**11. 範圍 8 的統計門檻沒有樣本下限的一致性**
severity: minor
blocking: 否
引句:「某條規則判 real 的比例高於九成且命中 ≥ 20 → 提議升成會擋;低於一成 → 提議降提示級。」
- 「低於一成」那一支沒有命中數下限,1 次命中判 false-positive 就會提議降級。範圍 7 的 kappa 有 20 段下限,這裡不一致。
- 命中來自單一盲判(無仲裁),九成與一成其實是盲判代理的偏誤,不是規則品質。

總結:範圍 8 缺三樣東西才能落地,依序是新增告警閘的命令分流機制(blocker)、核對所在位置(早退加 `--no-lint` 資料,blocker)、覆核段的寫入格式與放行事件登記(major)。範圍 1–7 另有兩個會讓作者卡死的洞:行數超門檻時沒有段可答(第 3 條),以及停用字表擋不住 `suspend fun` 這類複合觸發字(第 6 條)。
