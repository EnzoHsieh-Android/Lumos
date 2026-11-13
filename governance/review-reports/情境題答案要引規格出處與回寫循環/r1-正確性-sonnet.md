severity: major

這份投稿的主幹是對的,但 spec 裡有 8 個會讓實作者做錯或卡死的洞,另有 5 條小問題。

**節點判讀:** 只附到 `Systems/guard-kill`,它宣稱兩條 ★INVARIANT★:rc 優先序,以及 `--json` 成功時 stdout 恰一行 JSON。這份設計**不影響**它們,條件是範圍 4 抽共用函式時不動 rc 判定與 JSON 輸出。`cmd_guard_kill` 已有 `result_out` 參數,`kill-add --try` 也用它,所以抽取不大。既有綁定測試 `t_guard_kill_rc_precedence` 與 `t_guard_kill_json_purity` 會抓到抽壞的情形。其餘三個計劃連結節點(規格閘、棧別提問表態閘、pitfalls-code-loop)沒附內容,我直接讀了 `Systems/規格閘.md`。結論在 finding 1。

---

1. 人裁寫回的條款在風險低計劃上過不了規格閘
severity: major
- blocking: 是。實作者照做會做出一條寫回後永遠過不了規格閘的條款。
- 出處:範圍 4 的殺傷力驗證與寫回,以及「改了計劃要重跑規格閘留痕」。
- 引句:「這份計劃的規格閘留痕(條款雜湊變了)與預期值表簽核(表指紋變了)要重跑」
- 問題:殺傷力驗證要求綁定測試的基準先綠,所以寫回的 `[S<n>] … [test:名]` 條款,測試必然已經是綠的。
  - 規格閘對風險低計劃要求「沒標 keeps 的新行為條款,測試現在就該紅」。
  - 想用 `[keeps]` 逃,又要「測試在計劃第一次進 git 的提交之前就存在」,事後補的測試做不到。
  - 結果:重跑規格閘會判「綠——沒標 keeps 的是新行為」而擋下。推送前的指紋比對也會因條款指紋變了而擋「過期,重跑」。
  - 風險高計劃只是半套(紅綠只印不擋),不受影響。
- 查證:
  - file: `scripts/lumos:15132-15150`(`_spec_gate_twoway_run_verdict`)
  - file: `scripts/lumos:15103-15129`(`_spec_gate_twoway_static`、`_test_exists_before`)
  - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md`(KEY「放行條件」:t_spec_gate_green_new_clause_rejected、t_spec_gate_keeps_bypass_rejected)
- 缺口:spec 沒講寫回的條款對風險低計劃該怎麼過這一關。

2. 「段放行是出口」與程式現況相反
severity: major
- blocking: 是。沒有測試平台,或規格沒寫的專案,在生效日後完全沒有出口。
- 出處:範圍 4,以及 RETIRE-IF ③。
- 引句:「專案沒有宣告測試平台(`run_cmd`)時拒絕,訊息指出出口只剩既有的段放行」
- 問題:既有的段放行(`lint-waive kt-situation:`)只略過證據提醒與多數決提醒,缺段缺列照擋。spec 的「不改段放行」也沒讓它放行新的出處擋。
  - 所以無平台專案、找不到對應計劃的專案、人裁拒絕的情形,擋下後只剩把整列改答「不適用」,或把生效日調到未來。
  - RETIRE-IF ③ 拿「段放行次數超過人裁兩倍」判人們繞過,前提也不成立。
- 查證:
  - file: `scripts/lumos:73721-73748`(`_kt_sit_check` 的 waived 只擋 evidence 提醒)
  - file: `scripts/lumos:74580`(`_kt_bj_check` waived 只計數)
  - file: `scripts/lumos:74297`(docstring 寫「有段放行的段只略過證據提醒與多數決提醒」)

3. 出處不同但票面相同時,仲裁根本取不到材料
severity: major
- blocking: 是。S8、S9 的情境在實作後會永遠卡在「要仲裁」。
- 出處:範圍 5 比對。
- 引句:「第一盲判判適用而且出處跟作者不同(含一邊是 `未寫`)→ 要仲裁;票面相同也要」
- 問題:仲裁材料由 `_kt_bj_pick_rows(mode="disagreements")` 挑列,它只在作者票與第一盲判票不同時才挑。
  - spec 只列了 `_kt_bj_check`、`_kt_bj_arbitrate`,沒提 `_kt_bj_pick_rows`。
  - 出處不同但都判適用且都照做時,`--disagreements` 印出「沒有要仲裁的格」,擋下訊息叫人去派仲裁,卻派不出去。
  - `_kt_bj_check` 的 `disagree` 提示句也只講票面不同。
- 查證:file: `scripts/lumos:74631-74645`、file: `scripts/lumos:74572-74579`

4. 人裁寫回後盲判冷凍,新條款永遠得不到附和
severity: major
- blocking: 是
- 出處:〈用詞〉生效日與範圍 2、5,以及驗收條款 S9。
- 引句:「作者與盲判引的不一樣要仲裁,仲裁後作者的出處仍沒有任何盲判附和就交人裁」
- 問題:
  - 盲判格子「每格只認第一筆」(first、arbiter 各一次),段身分綁程式碼、不綁計劃。
  - 人裁寫出新條款 S13 後,舊的第一盲判與仲裁都是在 S13 存在之前投的,引的是別條或 `未寫`。
  - 作者重答引 S13 時,若仲裁格已有值就不能重投,「至少一位盲判填了一樣的值」永遠不成立。人裁指令骨架會再被印出,形成無限循環。
  - 作者只能改回引盲判引的那條。
  - 另外,「作者引 S3、仲裁與第一盲判都引 S5」是在爭哪一條適用,補救卻是寫一條新條款加殺傷力證明,補救與病因不符。
- 查證:file: `scripts/lumos:74461-74472`(`_kt_bj_cells_add`,「每格只認第一筆」)
- 缺口:spec 沒定義盲判格子如何重投或作廢。

5. 人裁指令缺 variant 參數,預期值表列寫不出來
severity: major
- blocking: 是。實作者只能猜 main 或 alt。
- 出處:範圍 4 指令簽名與寫回列。
- 引句:「| S<號> | <段的檔:起訖行> | <適用,照 main 或 alt> |」
- 問題:指令參數只有 `--seg --row --plan --clause --test --kill-file --kill-old --kill-new [--consent]`,沒有 `--variant`。
  - 預期格要寫 main 還是 alt,資料來源不存在。從 `--kill-old`、`--kill-new` 推不出確定值。
  - 同一格也沒說「不適用」的人裁怎麼寫。
- 查證:spec 範圍 4 全文只出現這一組參數。

6. 重用 `_spec_gate_push_candidates` 搭記憶體 Env,實際讀的是工作目錄
severity: major
- blocking: 是。spec 宣稱「對被推版本判」,重用後做不到。
- 出處:〈用詞〉對應計劃名單。
- 引句:「用 `_drift_tree_env` 從被推版本(`at_sha`)的樹建一份只在記憶體裡的圖譜」
- 問題:`_spec_gate_push_candidates` 內部用 `(env.vault / prel).read_text(...)` 直接讀磁碟,不是 `env_text`。
  - 記憶體 Env 的 vault 路徑是 `Path(root)/vault_rel`,磁碟上讀到的是工作目錄那份。
  - 工作目錄有未提交的計劃改動(人裁流程正是如此),正文連結會用工作目錄版判。檔不存在時 `ptxt=""`,正文連結全漏。
  - `_impact_home_map` 用 `str(env.vault)` 當行程內快取鍵,記憶體 Env 與真實 Env 同鍵。同一行程建兩份不同 sha 的樹 Env(例如合併側與本側)會拿到第一份的家對照表。
- 查證:
  - file: `scripts/lumos:16452-16478`
  - file: `scripts/lumos:67347-67359`
  - file: `scripts/lumos:1034`(`env_text` 才是記憶體友善讀法)
- 缺口:spec 需要先改這兩處,再重用。

7. 人裁條款文字的禁字表不夠,寫回後條款會被讀壞
severity: major
- blocking: 是
- 出處:範圍 4 條款文字。
- 引句:「條款文字:不准有 `[S`、`[test:`、`[manual:`、`|`、換行」
- 問題:
  - 實測 `--clause` 含單一未閉合反引號時,`_clause_grammar` 判合格。
  - 但寫成 `- [S2] 當搜尋,系統 應 用 `flatMapLatest 只顯示最後一次 [test:t_x]` 之後,`clause_bindings` 把 `[test:]` 當成被截掉。S2 變 `untagged`、refs 為空。
  - 殺傷力驗證與寫回都過,規格閘卻讀不到測試。
  - 同理漏掉 `[keeps]`:帶了會讓該條不進預期值表,預期值表檢查報「標了 keeps,不用寫」,整張表失敗。
  - HTML 註解起手 `<!--` 也沒禁。
- 查證:我跑了 `clause_bindings` 探針,輸出 `('S2','untagged',[])`(有閉合反引號時為 `dangling`,即 `[test:]` 讀得到)。
- 缺口:寫回前沒有「把寫完的整份文字再跑 `clause_bindings` 與 `_expected_table`,確認新條款是 defined 且綁到測試」這一步。

8. 「下一個號」沒定義,且算在殺傷力驗證之前
severity: major
- blocking: 是
- 出處:範圍 4 配方身分與寫回。
- 引句:「條款編號是寫回時會拿到的下一個號」
- 問題:
  - 沒說怎麼算:全文 `max(defined)+1`、驗收條款節內最大號加一、條款個數加一,三者在有缺號或散文裡提到 `[S9]` 時不同。
  - 殺傷力驗證在 Gradle 專案可能數分鐘,spec 自己也這麼說。期間別的會談若也寫回,兩邊拿到同一號,產生「條款編號重複定義」,規格閘整份失敗。
  - 配方身分又用這個預先取的號進治理帳。拿鎖後重算,身分就跟帳對不上。
- 查證:
  - file: `scripts/lumos:15702-15760`(`clause_bindings` 的 duplicate 狀態)
  - file: `scripts/lumos:15632-15644`(`_clause_structure_verdict`,重複編號直接 fail)
- 缺口:全 repo 沒有「驗收條款節」的找節函式(grep 無 `_ACCEPT` 之類的 H2 regex),spec 要新增一個,也沒講。

9. 生效日:讀側與寫側共用形狀函式,日期沒有傳到該傳的地方
severity: minor
- blocking: 否。S11 測試會立刻抓到,實作者改得動。
- 出處:〈用詞〉生效日與範圍 1。
- 引句:「`_codeloop_disp_from_event` 現在只回 `head_sha, branch, ts, dispositions`、把 `written_at` 丟掉」
- 問題:
  - `_kt_sit_row_shape`、`_kt_sit_shape` 寫側與讀側共用,讀側經 `_kt_sit_check` → `_kt_sit_row_verdict` → `_kt_sit_row_shape`。若形狀規則直接要求 spec 欄,生效日前的舊表態在讀側就被擋,S11 不成立。spec 只說日期傳到 `_kt_sit_verdict_one`,沒說傳進 check 與形狀函式。
  - 事件缺 `written_at` 時預設值未定義。早期事件可能沒有,比較會當掉或誤判為新制。
  - 日期與帶時區的 `written_at` 比較的口徑也未定。
  - 生效日前寫的表態(舊制),其盲判在生效日後新寫時帶 spec 欄,舊制是否略過未定義。
- 查證:file: `scripts/lumos:72163-72166`、file: `scripts/lumos:73643-73720`

10. `#預期<k>` 是位置編號,列號位移時舊引用可能無聲指到別列
severity: minor
- blocking: 否。引句仍須逐字在被指到的列裡,不會憑空多出內容。
- 出處:〈用詞〉出處。
- 引句:「那份計劃〈預期值表〉的第 k 列(從 1 起算,不含表頭與分隔列)」
- 問題:
  - 預期值表同一條款常有多列,不能用條款欄當穩定鍵,只能用位置。人裁寫回追加在表尾,不位移。但任何人在表中間插列,後面的 k 全部位移。
  - 引句只比對整列文字,若兩列共有同一段字(例如本 spec 預期值表 S3 第一列與 S9 第一列的預期格都是「擋,印人裁指令骨架」),位移後舊引用照樣通過、卻指到另一列。
  - 計數口徑含糊:「四格而且第一格是 `S<n>`」的列才算,畸形列是否佔號未定。
  - 讀列不用 `_expected_table_lines`(只取第一段連續的表格),所以「節出現兩次」時 `_h2_section_lines` 會把兩節的列併起來,k 再位移。
  - `spec` 欄的字串比對沒定義正規化。`#S3` 與 `#S03` 同一條,卻會被當成不同值而無法「附和」。
- 查證:
  - file: `scripts/lumos:13945-13965`(`_h2_section_lines` 對重複標題併節)
  - file: `scripts/lumos:14576-14590`

11. 盲判材料會洩出人裁紀錄與判斷,與 S10 矛盾
severity: minor
- blocking: 否。實作者要選一邊,兩邊都不致壞。
- 出處:範圍 5 材料。
- 引句:「不放作者的答案(作者選的 `spec`、`quote`)、不放人裁紀錄」
- 問題:`specs` 要附預期值表列的出處本文,而人裁寫回的預期值表列正是「段的檔:起訖行 | 適用,照 main 或 alt | 人裁 日期 origin:「原話前 40 字」」。
  - 這一列直接告訴盲判這一段的答案,也帶出使用者原話,材料頂層的 `specs` 裡就有人裁紀錄。
  - 盲判的獨立性在人裁後的情形被破壞。S10 只測不含作者答案,抓不到。

12. 統計與撤除條件對不上,另有兩個懸空引用
severity: minor
- blocking: 否。文件層面的問題,不影響程式行為。
- 出處:範圍 6、RETIRE-IF、預期值表 S3 與 S12 的來源格。
- 引句:「出處對不上而仲裁的次數」
- 問題:
  - RETIRE-IF ① 要「盲判與作者引到同一條的比例」與「仲裁後交人裁的比例」,統計只給四個計數,分母與「仲裁後被擋」的次數沒有。
  - S12 的來源格寫「前掃④:新欄不加白名單會整筆消失」,本文沒有「前掃」這個定義。
  - S3 來源寫的使用者引文「規格沒寫的一律擋下交人裁」,依據來源表只收了另一句「照擋,沒規格…」。

13. 兩處宣稱比實況強
severity: minor
- blocking: 否。屬措辭與記帳,不改程式行為。
- (a) 範圍 1 的取捨:
  - 引句:「盲判判適用、作者判不適用就照既有規則要仲裁」
  - 既有規則下,仲裁後兩位盲判一致判適用且照做是 `blind_agree`,不擋,不要求任何出處;判適用但沒照做也只是多數決提醒。作者把該適用的列答成不適用,即使被盲判抓到仍不擋。〈天花板〉5 只承認「兩位盲判都答不適用抓不到」,太樂觀。
- (b) 人裁證明「用測試守住」:
  - 殺傷力是臨時配方、一次性,沒有存成 kill-add 配方,也沒綁 ★INVARIANT★。之後測試被弱化沒有任何機制發現。
  - 範圍 4 改動 `cmd_guard_kill`,但 `lands_in` 沒有 `Systems/guard-kill`(只在 `related`),違反「改到的每支檔要有家」的寫法。

---

已讀無 finding 的部分:〈範圍〉1 的收件形狀(三種寫法加引句 10 字)、範圍 2 的未寫擋下邏輯、`clause_bindings` 與 `_expected_split_cells` 的呼叫簽名(spec 引用的四個空參數與函式簽名核對相符)、`_h2_section_lines` 取節、PRIOR-ART 與舊否決比對、回退節、文件內部交叉引用(範圍 1 到 6、〈用詞〉、〈回退〉、〈天花板〉)。

守衛面逐類:
- 出處比對的作者出處要有盲判附和:見 3、4、13(a)。
- 票面與出處兩道並存時的優先序:「擋優先」本身沒矛盾,但出處「擋」在 `_kt_bj_check` 目前只有 `disagree` 與 `missing` 兩種訊息通道,實作需新增。
- 未寫加人裁:見 1、2、5、7、8。
- 生效日判法:見 9。
- 寫回條款編號:見 8。
- 預期值表列號位移:見 10。

最嚴重 severity:major,blocking 共 8 條(finding 1 到 8)。
