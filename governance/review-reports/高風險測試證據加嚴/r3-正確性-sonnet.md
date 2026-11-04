severity: blocker

# 高風險測試證據加嚴 r3 正確性席審查報告(sonnet)

整體評價:r2 的主要洞(帳與留痕接縫)確實不在了,但「基準重播」本身在選計劃、取起點、判逾時、建環境這幾處,照字面實作會誤擋或漏放。以下 12 條有 file:line 佐證,其中 9 條 blocking。我寫了幾支探針,跑過 `_spec_gate_verdict`、`_ran_count`、`_nodehome_is_test`、`git diff --name-only` 與 `_gov_vc_gate_events`;探針已刪。

1. 分岔點取「推送範圍起點」,第二次以後的推送會把新測試誤判成「舊程式上就綠」
引句:「分岔點:推送範圍的起點那一版(三點範圍取 merge-base,同推送前檢查現有的 `_range_base`)。」
- 輸入:同一個分支第二次推送。第一次已把實作與測試推到遠端。第二次是審查修補,同時改到計劃檔(例如補審計修正紀錄、status 改 done)和一支程式檔。
- 走到哪:pre-push 對已存在的遠端分支給 `rsha..lsha`,所以 `_range_base` 回的是遠端現在的頂端,不是實作開始前的版本。
- 壞在哪:分岔點那棵已含完整實作,新行為測試必然是綠的,觸發「在舊程式上就綠」,每次後續推送都被擋。
- 出口:只剩 `base_replay_skip`,而且那是永久欄位。
- 其他會中的情況:rebase 或 force-push 後 `rsha` 是舊頂端;`done` 計劃之後又被碰到。
- 只有「新分支首推」(`pp_block_range_for` 改問跟主線的分岔點)語意才對。
- file: `scripts/hooks/pre-push:41`(`pp_range_for`)、`scripts/hooks/pre-push:491`(`_brange`)、`scripts/lumos:61298`(`_range_base`)
severity: blocker
blocking: 是——照字面實作會對後續推送整批誤擋,核心機制失效。

2. 只看「推送範圍改到的計劃檔」,實作單獨推送或先推測試的流程整個繞過
引句:「只看推送範圍改到的計劃檔(`_spec_gate_touched_plans` 給的那份);只因連到同一個系統節點被拉進來的計劃不重播、不查表、不查簽。」
- 輸入(TDD 先推測試):第一次推送是「測試加計劃」,第 1 點排除測試檔,所以沒有程式檔,不重播。第二次推送只有實作程式檔,計劃檔沒動,所以計劃不在選取集合裡。
- 結果:基準重播、預期值表檢查、簽核檢查三道全沒跑。
- 原則上同一個洞:實作提交只動程式檔和 Systems 筆記、不動計劃檔。既有程式的註解已說這是常態(「實作提交常只動程式檔不動筆記(編排者實測 E2)」),所以 `_spec_gate_push_candidates` 才會另外拉進「被改檔的家」連到的計劃。這份規格把這條路整個拿掉,沒有補任何替代。
- 與第 1 條合看:計劃被碰到的推送會誤擋,沒被碰到的推送會漏放。
- file: `scripts/lumos:15534`、`scripts/lumos:15539`、`scripts/lumos:15544`
severity: major
blocking: 是——漏掉該擋的(整個先推測試再推實作的流程不受任何檢查)。

3. 「程式檔」的定義寫不準,設計審期間的推送會被當成在實作
引句:「這次範圍另外改到至少一支程式檔——不算圖譜目錄底下的檔、不算 `_BOOKKEEPING_FILES` 列的帳本、也不算 `_nodehome_is_test` 判成測試的檔。只改計劃與帳本(設計審期間的推送)不重播。」
- 「程式檔」只排除三類,不是 `_is_code_file` 那種正向判定。
- `_BOOKKEEPING_FILES` 不含卷證目錄。`governance/review-reports/`、`governance/code-loop/`、`governance/redbase/` 在 `_BOOKKEEPING_DIRS`,規格沒提。我用探針確認:`governance/review-reports/高風險測試證據加嚴/r2-intake.md` 是 `bk_dir=True`、`bk_file=False`。
- 設計審每輪都把卷證與計劃放同一個提交推送。照字面,這些推送被判成「改到程式檔」,計劃風險高、created 在生效日之後、status 是 doing,所以進入重播。
- 此時條款的測試還沒寫,靜態檢查擋下,設計審每一輪的推送都被擋。這正是規格自己說不該發生的情境。
- 其他同類:`README.md`、`docs/指令參考.md`(不在圖譜目錄)、`.github/workflows/*.yml` 也都被算成程式檔。
- `_nodehome_is_test(path)` 不帶 layout 時有第二個坑。探針結果:
  - `app/src/androidTest/java/x/FooTest.kt`、`AppTests/Helper.swift`、`conftest.py` 都回 False。
  - 後果一:這些測試檔不會被複製進分岔點,新測試在分岔點「不存在」。
  - 後果二:這些測試檔被算成程式檔,Android 專案「只改測試加計劃」的推送會觸發重播。
- 其他呼叫端都傳 `_nodehome_layout(...)`(例如 `scripts/lumos:44423`),規格沒提這個參數。
- file: `scripts/lumos:38108`、`scripts/lumos:38129`、`scripts/lumos:44128`、`scripts/lumos:15579`
severity: major
blocking: 是——照字面實作,設計審的推送被擋,且 Android 的測試檔判錯。

4. 逾時要看的是 `_run_bound_tests` 回傳的 detail 欄,不是 `_spec_gate_judge_items` 的「原因」欄
引句:「分岔點的紅若是逾時(結果原因是逾時),不算紅,當弱證據(同紅燈版「逾時的紅不算」)。」
- `_run_bound_tests` 逾時時回 `("red", "超時(>180s)")`。
- 逾時的輸出沒有摘要行,`_ran_count` 回 None,`_spec_gate_verdict` 走 `n is None` 那支,回傳的 why 是「這棧還讀不出支數,只印有沒有跑過」。探針實測:`('red','這棧還讀不出支數,只印有沒有跑過')`。
- 「超時」只留在 rows 的第 6 欄 detail。若實作者照字面讀 rows 的「原因」欄(第 5 欄),逾時永遠認不出來,會被當成有效的紅,逾時的分岔點被「證實」。
- 另一個陷阱:detail 用子字串比對會誤判。測試斷言訊息含「超時」時,rc!=0 的 detail 是 `rc=1 …超時…`(探針實測),被當成逾時。要用 `startswith("超時")`。
- 規格要寫明讀哪一欄、用 startswith。既有先例是 `_redbase_row_reason` 讀 detail 加 `startswith`。
- file: `scripts/lumos:15057`、`scripts/lumos:15105`、`scripts/lumos:14344`、`scripts/lumos:69151`
severity: major
blocking: 是——照字面實作,S5「逾時不算紅」在所有棧都失效。

5. 隔離工作樹是乾淨檢出,規格沒處理設定檔、依賴資料夾與樹外平台根
引句:「推送範圍裡新增或改過、`_nodehome_is_test` 判成測試的檔,從推送版複製進分岔點那一棵(刪掉的不動);分岔點那一棵其餘檔維持舊版,平台設定用它自己的。」
- 兩棵都只有進版控的檔。修正關卡處理過、這份規格沒有的情形有:
  - `.lumos/config.json` 沒進版控(消費專案常見):樹裡讀不到設定,`load_platforms` 退回預設單一平台、`run_cmd` 空。
  - 全部結果是 `no-cmd`,`_run_bound_tests` 回 `(None, …)`,落入「重播跑不了」被擋。
  - 修正關卡的做法是把主工作目錄那份設定複製進樹。
  - `node_modules`、`.venv` 依賴資料夾:`_lint_link_deps` 負責連回。
  - 平台根在樹外或是子模組:`unpinned` 負責標記。樹外的平台根兩棵跑的是同一份工作目錄程式,分岔點必綠,會被誤報成「舊程式上就綠」。
- `local.properties`、被忽略的 `google-services.json` 等也不在樹裡。
- 結果:這類專案的推送版那棵也不綠,被擋成「推送版不綠」,只能 skip。
- 規格的「誤擋一、二」沒涵蓋這類。「平台設定用它自己的」不等於「樹裡讀得到設定」。
- file: `scripts/lumos:21936`(修正關卡複製設定、處理 unpinned、連依賴)、`scripts/lumos:6359`(`load_platforms` 把 root 解析成 `(repo_root/root_str).resolve()`)、`scripts/lumos:39181`
severity: major
blocking: 是——照字面實作,設定檔不進版控或有依賴資料夾的專案,重播一定擋錯。

6. 平台測試指令沒有 `{method}` 時,新行為測試與對照組共用同一次整套結果,判定矛盾
引句:「兩棵各用 `_platform_test_index` 建測試索引、用 `_spec_gate_judge_items` 跑:新行為條款綁的每一支測試(兩棵都跑)與標 keeps 的條款測試(只在分岔點跑,當對照組)。」
- `run_cmd` 沒有 `{method}` 時,`_run_bound_tests` 以完整指令為去重鍵,同一次整套結果套用到每一支。
- 有 keeps 條款:keeps 要在分岔點綠、新行為要在分岔點紅,但兩者是同一個結果,必然有一邊判錯,永遠被擋成「重播環境不可信」。
- 沒有 keeps 條款:整套裡任何一支既有測試是紅的,就被當成「新行為測試在分岔點紅」而證實。
- 既有的 `_spec_gate_runnable` 與修正關卡都先擋這種平台,規格沒要求。
- file: `scripts/lumos:15089`、`scripts/lumos:69068`、`scripts/lumos:22015`
severity: major
blocking: 是——該擋的放過,不該擋的擋下。

7. 選計劃沒限定計劃筆記或有條款的計劃,零條款計劃與調研筆記會被錯誤訊息擋下
引句:「現場重判門是風險高(`_door_judge`);開頭欄位 `created` 不早於 `_HIGH_RED_SINCE`(讀不懂的日期當成生效日之後);status 是 doing 或 done;」
- `_spec_gate_touched_plans` 回所有 `Projects/*.md`,包含 `*_調研.md`,而且很多是 `type: project`、`status: doing`(例如 `評測設計與爬坡_調研.md`)。
- `_door_judge` 在四行「已排除」缺任一類時判風險高(`missing`)。調研筆記根本沒有那四行。
- 靜態檢查直接呼叫 `_spec_gate_twoway_static`,在零條款時 `not [b for b in clauses if …]` 為真,印「全部條款都標 [keeps]」並擋。規格說「跟風險低擋下的字一樣」,所以這句誤導的訊息會原樣出現。
- 在 `_計劃.md` 裡,依 `^…[S1]` 條款行粗略 grep,332 份只有 193 份有,139 份沒有 `[SN]`(opt-in 未啟用)。新建、風險高的零條款計劃改程式檔後推送會被擋。
- 既有的風險低流程要有規格閘留痕才進推送檢查(`full = _live and rec …`),新道沒有這個前置條件。
- `_nl_rule_lands_in` 對計劃的限定是 `type == project` 且檔名以 `_計劃.md` 結尾,可借。
- file: `scripts/lumos:15534`、`scripts/lumos:14007`、`scripts/lumos:14218`、`scripts/lumos:12807`
severity: major
blocking: 是——照字面實作,零條款計劃與調研筆記被擋,訊息還講錯。

8. 計劃欄位、條款、表與簽核讀工作目錄,測試樹卻是提交,兩邊可以不一致
引句:「這是世界解(devops-cli)「附理由的不適用」出口,給重播在環境上跑不起來的專案用;寫在計劃裡、進版控、設計審與代碼審看得到。」
- 規格說 `base_replay_skip` 進版控,但沒說門檢查讀的是範圍終點那個提交裡的計劃,還是工作目錄的計劃。
- 既有推送檢查全從 `env.notes`(工作目錄)讀,`_spec_gate_push_scan` 就是這樣。
- 實測方式:`lumos set 計劃 base_replay_skip "…"` 直接改工作目錄檔,不提交就 `git push`。
  - 規格閘讀工作目錄,認定有 skip。
  - 實際推送的提交裡沒有這個欄位。
- 反過來:工作目錄的計劃裡改了 `[test:t_new]` 綁定,但還沒提交。
  - 條款項目來自工作目錄,測試樹來自提交。
  - 樹裡找不到那支測試,兩棵都「懸空」判紅,推送版被判不綠。
- 簽核與 `table_sha` 同理:`signoff --expected` 簽的是工作目錄那份表,推送的提交可能是另一份。
- 範圍終點也沒說怎麼取:`_range_base` 只給起點。推送的 ref 不是 HEAD 時,不能用 HEAD。
- file: `scripts/lumos:16248`(`_spec_gate_push_scan` 用 `env.notes`)、`scripts/lumos:15539`
severity: major
blocking: 是——照字面實作,skip 可以不進版控就生效,工作目錄與提交內容不一致會誤判。

9. 測試檔改名或搬移時,舊檔留在分岔點,同名測試變成兩支而被判弱證據
引句:「推送範圍裡新增或改過、`_nodehome_is_test` 判成測試的檔,從推送版複製進分岔點那一棵(刪掉的不動);」
- 推送前取檔用 `git diff --name-only`(未加 `--no-renames`),改名只回新路徑。我實測了改名 `test_a.py`→`test_b.py`,輸出只有 `test_b.py`。
- 舊路徑檔留在分岔點,新路徑檔被複製進來,同名測試變成兩支。
- `_spec_gate_declared` 把宣告數算成 2,`_spec_gate_verdict` 在 `n>=2 and declared != 1` 回 `weak`。新行為與 keeps 的測試都變弱證據而被擋。
- 把測試拆檔重排很常見,這時重播永遠過不了。
- file: `scripts/lumos:15037`、`scripts/lumos:15057`、`scripts/lumos:16316`(`_spec_gate_push_check` 取清單的 `git diff --name-only`)
severity: major
blocking: 是——不該擋的擋下(只有搬檔改名這個輸入)。

10. `created` 可以用 `lumos set` 改,開關靜默失效;缺欄位是 fail-closed
引句:「生效日:程式常數 `_HIGH_RED_SINCE`,純日期,寫法同 `_NOTE_LINT_PLAN_SINCE`(拿計劃開頭欄位 `created` 比,讀不懂的日期當成生效日之後);」
- 缺欄位或日期讀不懂:`_note_date_ok` 為假,當生效日之後,會重播,這個走向對。
- 改成早於生效日:整個機制(重播、表、簽)靜默略過,沒有帳可查。
- `_plan_first_commit` 的註解已寫明「frontmatter 的 created 用 lumos set 就能改,不可信」,同一檔的 `_spec_gate_twoway_static` 也用它的 git 首次進歷史的提交。規格選了不可信的那個欄位當開關,沒說明為什麼不用 git 歷史。
- 按本專案「只顧單人、AI 依序操作」的威脅模型,不防刻意偽造,但「複製舊計劃當範本、created 沒改」這種無意情況也會被略過。
- file: `scripts/lumos:14194`(`_plan_first_commit`)、`scripts/lumos:12807`
severity: minor
blocking: 否——主要是刻意繞過,不是無意輸入就誤判的核心行為。

11. `_range_base` 的行為描述不準
引句:「取不到起點(`_range_base` 回空,例如遠端還沒有這條分支時的首次推送)就判「重播跑不了」,見第 4 點。」
- 新分支首推時,pre-push 的 `pp_block_range_for` 已改問跟主線的分岔點,給的是 `<fork>..<lsha>`,`_range_base` 回的是真提交。
- 空樹範圍(舊版 lumos 或算不出時)的左端是空樹雜湊 `4b825dc…`,不是空字串。`_range_base` 回的是那串字,不是 None,所以走的是 `git worktree add` 失敗的「建樹失敗」路徑,不是「取不到起點」。
- 兩種都擋,結果相同,但訊息與 `base-replay-failed` 的原因分類會分錯,RETIRE-IF 的統計跟著失真。
- file: `scripts/lumos:61298`、`scripts/hooks/pre-push:41`、`scripts/hooks/pre-push:54`
severity: minor
blocking: 否——最終同樣擋下,只有訊息與分類不準。

12. 預設逾時 180 秒對冷樹編譯不夠,以及新道的串接位置沒寫
引句:「效能:每份要重播的計劃多開兩棵工作樹、各跑一次它綁的測試;Android 專案等於多編譯兩次,推送前會多幾分鐘;」
- `LUMOS_TEST_TIMEOUT` 預設 180 秒。Android 在全新工作樹跑 `gradlew test --tests X`,要先編譯整個專案,常超過 180 秒。
- 分岔點逾時是弱證據,被擋;推送版逾時是紅,被擋成「推送版不綠」。
- 只靠 `base_replay_skip` 出口,規格沒提建議的逾時值。
- 另一個小處:新道要放在 `_spec_gate_push_check` 的哪裡沒寫。既有程式在 `_spec_gate_push_scan` 回 `None` 時(平台設定讀不動且沒別的錯)直接 `return 0`。若新道接在它後面,會被跳過;若新道的 fail-closed 與整支「工具壞了就放行」的約定相衝,也要寫清楚。
- file: `scripts/lumos:69041`、`scripts/lumos:16307`
severity: minor
blocking: 否——有 skip 出口,屬環境與串接細節。

## 圖譜鏡頭(固定席節點)

- guard-kill 的 rc 優先序合約:不影響。本計劃沒改 guard kill。共用的 `_isolated_worktree` 簽名不動,只是新呼叫端多傳 `sweep_repo`,guard kill 行為不變。規格「弱證據不放行」的立場與該合約一致。
- guard-kill `--json` 純度:不影響。重播只由 `spec-gate --push-check` 呼叫,不碰 `guard kill` 的輸出。前提是共用函式本身不新增 stdout 輸出。
- lifecycle 的 re-inject 只動 sentinel 內合約:不影響。做法第 8 點的注入範本只加一句,在 sentinel 之內;sentinel 外維持 byte-equal。升小版號是既有前例。
- test-quality 與 `scripts/test_quality.py`:不影響。計劃把改它列在第二批,且明寫「只借不改」,本批不動。
- `Verification/測試品質第四輪修補驗證`:不影響,本批沒碰其驗證範圍。
- `Systems/test-guard`:會議目錄裡沒有這篇,無法逐條核對。第二批提到的「字尾認」做法我沒法驗。

## 實務隱患逐類

- 金流:無。只改推送前檢查與帳,沒有收費流程。
- 對外送出:無。只讀本機 git、寫本機治理帳。
- 不可逆:無。治理帳是追加的,回退常數 `_HIGH_RED_SINCE` 即可。
- 併發:有條件。
  - 清殘骸的時限是 86400 秒,足以避開正在用的樹。
  - 兩個推送同時重播時,兩邊 `worktree add` 與 `prune` 互不衝突。
  - 另一個會談同時跑 `git push` 時,測試用的埠與資料庫若是固定的,兩邊會撞。這是環境條件,規格沒承諾。
- 效能:有。見第 12 條。每份計劃兩棵加兩次整體編譯,多份計劃逐份重建,沒有總預算。
- 資源:有輕微。兩棵樹各一份檢出與建置產物。清理靠 `_isolated_worktree` 收尾與下次清殘骸,被強殺才會留下。Gradle 等常駐程序是否殘留我沒有證據,⚠ 未驗。
- 回滾:無問題。改常數即可關閉,事件留在帳上無害。

## 沒問題或只讀確認的段落

- 預期值表格式(做法 5 拆格與欄位規則)與指紋(做法 6):已讀,無 finding。
- 簽核寫帳流程:`_waive_origin_tty` 的回傳對照、`_e2e_who`、`_gov_vc_gate_events`(實測 21MB 約 0.17 秒,規格的 0.2 秒屬實)與 `_gov_row` 擴欄:已讀,無 finding。
- 驗收條款 S9 到 S16:已讀,無 finding。

總結:最嚴重 severity 為 blocker(第 1 條),blocking 共 9 條(第 1 到 9 條)。
