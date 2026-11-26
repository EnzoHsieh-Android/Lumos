---
type: project
status: doing
created: 2026-11-26
updated: 2026-11-26
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/guard-kill
related:
  - "[[Projects/選擇點變異加速第三段_計劃]]"
  - "[[Projects/選擇點變異加速第二段_計劃]]"
  - "[[Projects/選擇點變異加速_計劃]]"
---
# 選擇點變異加速第四段_計劃

## 白話

[[Projects/選擇點變異加速第三段_計劃]] 上線後在實驗專案重跑 142 個壞法:14197 秒,平均 100 秒一個(舊做法約 360 秒),快 3.6 倍,但沒達到預估的 1.5–2.5 小時。拆帳後:117 個走快路(快篩通過 45、有失敗 66、編不過 6);慢的 25 個吃掉約四分之三的時間——15 個是快篩沒跑乾淨(逾時 11、結果檔零案例 4)後逐支盲找,10 個落在斷路器停用期間(斷路器被逾時連 5 次跳開)。快篩逾時的 11 個裡 10 個逐支後判殺掉、1 個跑不出結果:逾時多半是壞法讓某支測試掛住,不是工具壞了。

這份改三件事:

1. **合併呼叫讓 Gradle 印出每支測試的開始與結束。** 工具帶一份 Gradle 初始化腳本,打開測試事件的輸出;不改消費專案。
2. **快篩沒跑乾淨時,照這些事件排逐支順序。** 合併呼叫裡已經紅的先跑、沒跑到的其次、合併裡通過的再其次、掛住的最後。
3. **逾時而且已經跑到測試的,不計斷路器。** 這種逾時是壞法的錯;連一支測試都沒開始就逾時的(卡在編譯或設定),照舊計數。

好比一排人接力時有人倒下:原本只知道「沒跑完」,只好從第一棒重問一遍;現在每一棒交棒都喊一聲,倒下的那棒、已經喊出「犯規」的那棒一目了然。

WHY:合併呼叫帶工具寫的 Gradle 初始化腳本,打開 `testLogging` 的 started/passed/failed/skipped 事件;快篩沒跑乾淨時,從合併呼叫的輸出讀事件排逐支順序 [出處:2026-11-26 實驗專案重跑 142 個壞法 14197 秒,快篩沒跑乾淨的 15 個平均 340–948 秒] [因:Gradle 的 JUnit 結果檔要到測試任務結束才寫,逾時被收掉就一份都沒有;輸出在逾時時工具本來就留著] [不選:讀部分結果檔(Gradle 不會留,見〈依據來源〉);JUnit 全域逾時(實驗專案是 JUnit 4 加 Robolectric,沒有全域設定,Robolectric 的逾時規則要逐類別寫,等於改消費專案);二分快篩(要多跑最多約 8 次合併,事件已經答得出來)] [代價:合併呼叫的輸出每支測試多兩行;專案自己的建置腳本也設了 testLogging 時可能蓋掉事件,這時退回第三段的原順序] [test:t_choice_kill_merge_events_order]
WHY:快篩逾時而且輸出裡至少一支測試開始了,不計斷路器;每個壞法那筆的 `merge_why` 記成「逾時(跑到測試後掛住)」 [出處:同上,快篩逾時的 11 個裡 10 個逐支後判殺掉、1 個跑不出結果;斷路器被逾時連 5 次跳開,停用期間 10 個壞法平均 378 秒] [因:Stryker 官方把逾時算「已偵測」、Infection 預設算殺掉——逾時是壞法造成的;已經跑到測試代表合併呼叫與 Gradle 本身是好的] [不選:所有逾時都不計(連一支測試都沒開始的逾時多半是工具或環境的問題,斷路器正是要管這種);逾時直接判殺掉(這個工具要的是「哪一支測試守著這條規格」,只知道有測試掛住不夠)] [代價:機器過載讓每個壞法都逾時、而且都跑到了測試時,斷路器不再跳開,每個壞法多付一次快篩逾時上限(實驗專案約 90 秒)] [test:t_choice_kill_merge_hang_breaker]

PRIOR-ART: ①逾時歸因:Stryker〈mutant states and metrics〉把 Timeout 算 detected,理由是 CI 上測試永遠跑不完(https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/);Infection 0.32.3 說明逾時預設算殺掉、另加旗標可改算逃逸(https://infection.github.io/2026/01/14/whats-new-in-0.32.3)。採用「逾時是壞法的錯」這半,不採用「直接算殺掉」。②Gradle 結果檔時機:Gradle 論壇多個回答指出結果先存內部檔、任務結束才產 XML,逾時後沒有 XML(https://discuss.gradle.org/t/real-time-test-reports-for-junit/10783 、https://discuss.gradle.org/t/stop-tests-after-period-of-time/39817)→ 排除「讀部分結果檔」。③全域逾時:JUnit 5 有 `junit.jupiter.execution.timeout.default`(https://docs.junit.org/6.1.2/writing-tests/timeouts.html),JUnit 4 沒有,Robolectric 的 TimeoutRule 要逐類別宣告(https://robolectric.org/javadoc/4.13/org/robolectric/junit/rules/TimeoutRule.html)→ 不採。④測試重排讓壞法更快死:FaMT(ISSTA 2013)照預測重排測試,執行數約減半(https://personal.utdallas.edu/~lxz144130/publications/issta2013a.pdf)。採用「先跑最可能紅的」,依據換成同一個壞法合併呼叫的實際事件。
RETIRE-IF: ①上線後同專案累計 20 次快篩沒跑乾淨,事件排序後逐支跑到第一支紅的次數中位數沒有比第三段同類(實驗專案 11-26 那次,沒跑乾淨又判殺掉的 13 個)低一半以上 → 事件排序沒省到,拿掉初始化腳本與事件排序。②上線後同專案出現「斷路器沒跳開、但連續 10 個以上壞法都是『逾時(跑到測試後掛住)』」的呼叫累計 3 次 → 這類逾時其實是環境問題,改回照舊計數。
REVISIT:2026-12-31 讀治理帳每個壞法那筆的 `merge_why`、`single_runs` 與 run 那筆的 `merge_tripped`,照 RETIRE-IF 判。

## 實測(來源)

FACT:實驗專案 11-26 重跑 142 個壞法 14197 秒;快篩通過 45 個、有失敗 66 個、編不過 6 個(三類平均 18、28、7 秒);沒跑乾淨 15 個:逾時 11 個裡 10 個判殺掉、1 個跑不出結果,結果檔讀不出來(zero_cases) 4 個裡 3 個判殺掉、1 個存活;斷路器跳開 1 次、試探恢復 1 次,停用期間 10 個平均 378 秒 [來源:人工] [confirmed:2026-11-26]
FACT:實驗專案(JUnit 4.13.2、Robolectric 4.16)帶事件初始化腳本跑一支掛住的探針測試,90 秒逾時收掉後輸出最後是「HangProbeTest > b_hangs STARTED」、沒有對應的 PASSED;不帶腳本的對照組輸出看不出跑到哪一支;收掉後沒有殘留的測試執行程序 [來源:人工] [confirmed:2026-11-26]
FACT:逐支流程遇到單支逾時就判「跑不出結果:測試掛住」並停在那個壞法(`t_choice_kill_merge_failed_first` S1 案 5 釘住),所以掛住的那支排最前面會讓本來殺得掉的壞法變成跑不出結果 [來源:人工] [confirmed:2026-11-26]

## 用詞

- **沒跑乾淨**:沿用 [[Projects/選擇點變異加速_計劃]] 的快篩結果四類,快篩結果是 `unclean`。
- **事件行**:合併呼叫輸出裡一行(去掉行尾空白)符合 `<誰> > <測試名> <事件>`,事件是 `STARTED`、`PASSED`、`FAILED`、`SKIPPED` 之一。以 ` > ` 切開:最後一段是「測試名 事件」,倒數第二段是類別;類別先把 `$` 換成 `.`、再取最後一個 `.` 之後的字;測試名去掉參數尾巴(第一個 `(` 或 `[` 起);組成 `<類別>.<測試名>`。例:`com.x.FooTest > bar[1] FAILED` → `FooTest.bar`;`Outer$Inner > c STARTED` → `Inner.c`;`Outer > Inner > c STARTED` → `Inner.c`(後兩種寫法 11-26 探針沒測到,照字面處理;對不到就落未知層,只影響順序)。
- **合併道**、**快篩結果四類**:沿用 [[Projects/選擇點變異加速_計劃]]〈用詞〉。
- **斷路器停用**:沿用 [[Projects/選擇點變異加速第三段_計劃]]〈用詞〉。
- **對到**:合併道的測試名 m 對到事件的 `<類別>.<測試名>` f:f 等於 m、f 以「. 加 m」結尾,或 m 以「. 加 f」結尾。
- **四層**:合併道每個測試名照對到的事件分一層,一個名字只進一層、優先序由上而下:有 `FAILED` → 紅層;有 `STARTED` 而它之後沒有同一支的 `PASSED`/`FAILED`/`SKIPPED` → 掛住層;有 `PASSED` 或 `SKIPPED` → 通過層;都沒有 → 未知層。
- **跑到測試**:輸出裡至少一行 `STARTED` 事件行。

## 做法

1. **初始化腳本**(`_kill_merge_ready`、`_choice_merge_cmd`):
   - 常數 `_CHOICE_MERGE_INIT` 是腳本內容:`allprojects { tasks.withType(Test).configureEach { testLogging { events "started", "passed", "failed", "skipped" } } }`(Groovy 寫法,Kotlin 建置腳本的專案也吃)。
   - 路徑是 `os.path.join(os.path.dirname(c.wt), "lumos-merge-events.init.gradle")`:隔離工作樹的上層暫存資料夾(`_isolated_worktree` 用 mkdtemp 建、收尾整個刪掉;帶 `--keep-worktree` 時跟現場一起留下),不弄髒工作樹。
   - `_kill_merge_ready` 先算路徑(不寫檔)拿去做指令過長判斷;其餘條件都過、時限門之前才寫檔;寫入失敗(OSError)→ `sh["init"]` 是 None、照常合併(指令變短,過長判斷仍成立)。
   - `_choice_merge_cmd` 加選用參數 `init=None`:有給時在接好的 `--tests` 段之後、原字串其餘部分(`cmd[shape["e"]:]`)之前插 ` --init-script <路徑>`(路徑照 `_IS_WIN` 用雙引號或 `shlex.quote`)。兩個呼叫點都傳:`_kill_merge_ready` 的過長判斷、`_kill_merge_base` 組合併指令(取 `sh.get("init")`;既有測試直接給的 shape 沒有這個鍵)。合併基準與快篩都用 `_kill_merge_base` 組出的那個指令;逐支呼叫不帶。
2. **事件排序**(`_choice_merge_events`、`_kill_merge_screen`、`_kill_merge_failed_first`):
   - `_choice_merge_events(tail, names)` → {"failed": […], "hung": […], "passed": […], "started": bool},每層照 names 原排序。
   - `_kill_merge_screen` 一開頭把 `c.merge_failed`、`c.merge_back` 都清空(套不上壞法而提早回 single 時,不沿用上一個壞法的名單);classify 結果是 `unclean`(不分原因)時呼叫它:`c.merge_failed` 換成紅層、`c.merge_back` 設成通過層全部在前、掛住層在後(各層內照 names 原排序)。其他結果 `c.merge_back` 維持空(`c.merge_failed` 照第二段)。
   - `_kill_merge_failed_first`(照舊回傳 list):前面 `merge_failed`、中間其餘(照原排序)、最後 `merge_back`(照它自己的順序);兩份名單都空 → 原順序。只改順序、不判任何事。
3. **斷路器**(`_kill_merge_screen`):classify 回 `unclean`、原因「逾時」、而且事件「跑到測試」→ 交斷路器時計數改成不計、原因改成「逾時(跑到測試後掛住)」(`mg.whys` 與 `merge_why` 記這個字樣;不進 `merge_unclean`,它只記計數的那幾種)。啟用中不計也不歸零 `streak`(同第三段「其餘不計不歸零」);斷路器停用中的試探也照這條:不計、不恢復。合併基準那條路(`_kill_merge_base`)不改。

## 落點

- [[Systems/guard-kill]]:合併呼叫帶事件初始化腳本、沒跑乾淨照事件排序、跑到測試的逾時不計斷路器。
- 同一提交改的既有測試:假 Gradle(`_CKM_GRADLE`)加 `__events__`({狀態: [[測試名, 事件]…]}),只在合併呼叫而且帶 `--init-script` 時照順序印 `x.VmTest > <名> <事件>`,在逾時睡眠之前印;沒有這個鍵的既有案例輸出不變,所以既有的逾時、斷路器測試(`t_choice_kill_merge_breaker`、`t_choice_kill_merge_unclean_reasons`、`t_choice_kill_merge_half_open`、`t_choice_kill_merge_failed_first` S2)語意不變。直接用 `SimpleNamespace(wt=<暫存>)` 呼叫 `_kill_merge_ready` 的既有測試,`wt` 改成 `<暫存>/wt` 的形狀,初始化腳本才寫進那支測試自己的暫存資料夾。

## 預期效益(估算,待 S5 實測)

- 實驗專案 11-26 那次的 25 個慢壞法原本共約 10760 秒:沒跑乾淨的 15 個改成先跑紅層,多半一兩支就殺掉,約 2 分鐘一個;斷路器不再被這種逾時跳開,停用期間那 10 個回到平均 30 秒以內。這 25 個估計共約 30–40 分鐘;142 個整體從 3.9 小時估到約 1.5 小時。

## 不做

- 不調快篩逾時倍數(合併基準 × 5):實驗專案合併基準約 15–20 秒,上限約 90 秒,11 次逾時多等的總共約 10 分鐘;調低會讓機器忙時正常的壞法也逾時。
- 不查 `zero_cases` 的根因:4 次,這份的事件排序對它一樣有用(輸出裡有 FAILED 就先跑);累積更多 `merge_why` 再說。
- 不把逾時直接判殺掉、不改逐支遇到掛住就停的行為。

## 驗收條款

- [S1] 當平台組能合併、隔離工作樹上層資料夾可寫時,合併指令 應 在接好的 `--tests` 段之後帶 ` --init-script <上層資料夾>/lumos-merge-events.init.gradle`、檔案內容含 `events "started", "passed", "failed", "skipped"`,逐支指令 應 不帶;上層資料夾不可寫時 應 不帶 `--init-script`、照常合併;原字串 `--tests` 段後面還有其他參數時,`--init-script` 應 插在那些參數之前 [test:t_choice_kill_merge_events_cmd]
- [S2] 當快篩逾時、輸出依序是 a PASSED、b FAILED、c STARTED(沒有結束)、d 沒出現時,逐支順序 應 是 b、d、a、c,單支 b 紅時 應 只跑 b、判 killed by b;`b[1] FAILED` 這種帶參數的事件 應 對到 b;`Outer > Inner > c STARTED` 應 對到 c;快篩逾時、輸出依序是 c STARTED(沒有結束)、a PASSED、守的原排序是 c、a、b 時 應 是 b、a、c(通過層在掛住層之前);快篩結果檔零案例、輸出有 b FAILED 時 應 先跑 b;快篩逾時、輸出沒有事件行時 應 照原順序(同第二段 S2);前一個壞法照事件排過、下一個壞法套不上而交逐支時 應 照原順序;快篩有失敗時 應 照第二段的結果檔名單 [test:t_choice_kill_merge_events_order]
- [S3] 當連續 5 個壞法快篩逾時、每次輸出都有 STARTED 事件行時,choice-kill 應 不跳開斷路器、run 那筆 `merge_tripped` 假、`merge_unclean` 沒有「逾時」,每個壞法那筆 `merge_why` 是 {平台: 逾時(跑到測試後掛住)};連續 5 個快篩逾時、輸出沒有事件行時 應 照舊跳開、`merge_unclean` 的「逾時」是 5 [test:t_choice_kill_merge_hang_breaker]
- [S4] 當帶 `--no-merge` 時,choice-kill 的呼叫數與順序 應 跟現在相同 [test:t_choice_kill_no_merge_unchanged]
- [S5] 當在實驗專案強制重跑 11-26 那次的 25 個慢壞法時,總秒數、斷路器有沒有跳開、每個壞法的 `merge_why` 與 `single_runs` 應 記下來跟〈預期效益〉對照 [manual:在 Android 實驗專案用可重跑已殺掉行的腳本重跑那 25 個壞法,讀治理帳寫進驗證紀錄]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 能合併、上層可寫;另案上層不可寫;另案 `--tests` 段後還有參數 | 一:合併指令帶 --init-script、檔案含四種事件、逐支不帶;二:不帶、照常合併;三:插在其他參數前 | 本計劃第一條 WHY;11-26 探針實驗 |
| S2 | 快篩逾時,事件 a 通過、b 紅、c 開始沒結束、d 沒出現;另案帶參數、巢狀;另案原排序 c、a、b,c 開始沒結束、a 通過;另案零案例帶 b 紅;另案沒有事件行;另案前一個壞法排過、下一個套不上;另案有失敗 | 一:b、d、a、c,b 紅就停、killed by b;二:對到 b、c;三:b、a、c;四:先跑 b;五、六:原順序;七:照結果檔名單 | 本計劃第一條 WHY;第二段 S1、S2 |
| S3 | 連續 5 次逾時有 STARTED;另案沒有事件行 | 一:不跳開、merge_tripped 假、merge_unclean 無逾時、merge_why 逾時(跑到測試後掛住);二:跳開、merge_unclean 逾時 5 | 本計劃第二條 WHY;Stryker、Infection 逾時歸因 |
| S4 | `--no-merge` | 呼叫數與順序不變 | [[Projects/選擇點變異加速_計劃]] S13 |
| S5 | 實驗專案 25 個慢壞法 | 記下總秒數、跳開、merge_why、single_runs | 本計劃〈預期效益〉 |

## 回退

- 先關不還原:`LUMOS_SKIP_CHOICE_MERGE=1` 或 `--no-merge`,合併整個不開(事件與排序跟著不用)。
- 只想關事件:沒有單獨開關;還原功能提交。`merge_why` 的新字樣是既有欄位的新值,讀者照字串讀。

## 實務隱患

- 專案建置腳本自己設了 `testLogging.events`:初始化腳本先註冊、專案後設,可能蓋掉事件;這時事件行沒有,退回原順序、逾時照舊計數,跟第三段一樣。
- 平行測試(`maxParallelForks` > 1):可能同時有幾支「開始沒結束」,都進掛住層;只影響順序。
- 輸出很大:工具保留上限 256KB、超過取頭尾,中段的事件會丟,丟掉的名字進未知層;只影響順序。
- 已排除:金流:只在本機跑測試,不碰付款
- 已排除:對外送出:不連網、不寄送
- 已排除:不可逆:初始化腳本寫在隔離工作樹的上層暫存資料夾,收尾整個刪掉(`--keep-worktree` 時跟現場一起留,那是人要看的現場);治理帳只多一種 `merge_why` 字樣
- 併發與交易:同 [[Projects/選擇點變異加速_計劃]],一次呼叫一棵工作樹一條執行緒

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 逾時是壞法的錯 | Stryker 把 Timeout 算 detected;Infection 預設算殺掉 | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ 、https://infection.github.io/2026/01/14/whats-new-in-0.32.3 |
| 逾時後沒有結果檔 | Gradle 論壇:XML 在任務結束才產 | https://discuss.gradle.org/t/real-time-test-reports-for-junit/10783 、https://discuss.gradle.org/t/stop-tests-after-period-of-time/39817 |
| 不用全域逾時 | JUnit 5 全域屬性;Robolectric TimeoutRule 逐類別 | https://docs.junit.org/6.1.2/writing-tests/timeouts.html 、https://robolectric.org/javadoc/4.13/org/robolectric/junit/rules/TimeoutRule.html |
| 先跑最可能紅的 | FaMT 重排測試讓壞法更快死 | https://personal.utdallas.edu/~lxz144130/publications/issta2013a.pdf |
| 事件看得出誰掛住 | 實驗專案探針實測 | 實測 2026-11-26:實驗專案加一支掛住的探針測試,帶與不帶事件初始化腳本各跑一次 90 秒逾時 |

## 人裁紀錄

- 使用者 2026-11-26:「上網調研一下」;看完調研結論後:「照這個結論試試看」。

## 審計修正紀錄
