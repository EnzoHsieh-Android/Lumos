---
type: project
status: doing
created: 2026-11-01
updated: 2026-11-01
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/Android本機單元測試驗收標準_計劃]]"
  - "[[Systems/test-quality-cli]]"
  - "[[Projects/測試品質工具接線_計劃]]"
lands_in:
  - Systems/test-quality-cli
---
# Android單元測試標準實機演練_計劃

> 白話:測試品質標準剛加了〈Android 本機單元測試的驗收標準〉,但它只被讀過、沒被拿去用過。這份計劃拿一個真的消費專案(mOrangePos)當考場:先寫一份只講「該有什麼行為」的需求書,偷偷在程式裡埋幾個錯,讓一個沒看過程式內部、也不知道埋了什麼的代理照需求書和標準寫測試;另外故意寫幾支「看起來會過、其實什麼都沒驗」的壞測試。再用標準與現有工具去檢查,看每個錯、每支壞測試是被哪一道抓到、還是漏掉;漏掉的就除錯、訂正測試或訂正標準。

## 問題與最小解

立案:Enzo 2026-11-01 說「最後我要跑實機測試,模擬各種情境憑藉需求寫出的測試,能夠被規則檢核、除錯、訂正」;問過三題,答案是用真的消費專案、本機單元測試加平板上的測試、由乾淨代理寫加刻意壞測試;之後指定專案為 mOrangePos(「簽,用orangePos測試」)。

現況(演練前,2026-11-01,標準所在分支 3383ff253,PR #148 未合併):標準的 Android 單元測試節沒在任何專案用過。`lumos test-quality` 對 Kotlin 的靜態掃描要另裝 Semgrep 才會掃,而且只認得 `assertEquals(x, x)` 這種「斷言自己比自己」,Truth 的 `assertThat(x).isEqualTo(x)` 不認;零選中時沒有新報告、`capture` 在讀報告那一步就判無效(前提是跑之前先刪掉舊報告;舊報告還在時 `capture` 在跑之前就拒絕),報告存在時 `capture --target` 再擋只跑到包裝案例;`check` 證「故障版目標斷言紅、還原綠」。其他壞寫法沒有專屬機檢。

名詞:
- **收證、收據**:`lumos test-quality capture` 執行一次測試命令,保存 JUnit 報告、退出碼與原始碼快照的資料夾。一個錯要三份收據:原版、故障版、還原版各跑一次;`check` 核對這三份。
- **判無效**:收證或核對拒收,有三種樣子:`capture` 在跑之前就拒絕(例如舊報告還在,不產生收據)、收據狀態是 invalid(例如零選中沒有報告)、`check` 回拒收碼(例如目標測試的失敗不是斷言失敗)。安全證據閘把這些原因碼記成「invalid:…」。判無效的都不算抓到錯。
- **安全證據閘**:推送前判「登記過的資安護欄有沒有合格證據」的那道閘;它有兩條路用到收證工具的斷言歸因:故障敏感度那條(核對三份故障收據)與 JUnit 宣告那條(直接讀測試報告)。
- **當掉**:測試因為丟了不是斷言的例外而紅,例如假實作(記憶體裡的假資料來源)遇到沒排好的呼叫就丟例外;收證不把這種紅算成抓到錯。
- **靠預設回傳值才綠**:Android 本機測試的 `returnDefaultValues` 設定打開時,框架方法一律回 null、0 或 false,本該失敗的斷言可能變成恆真。
- **Truth、`WithFacts`、`Expect` 規則**:Truth 是 Google 的斷言函式庫,`assertThat` 失敗時丟的型別名結尾是 `WithFacts`;`Expect` 是它的「收集多個失敗、測試結束才一起報」的 JUnit 規則。
- **斷言歸因**:收證工具判一個失敗「是不是斷言失敗」的那段規則;跟 S1 的「歸因」(人判斷錯為什麼沒被抓到)是兩回事。
- **包裝案例**:報告裡只有檔案或類別層級的一筆案例,看不出真正跑了哪支測試。
- **零選中**:測試篩選條件沒選到任何測試。
- **配套指紋表**:主程式 `scripts/lumos` 裡記著三支收證工具檔 sha256 的表,載入時逐檔比對,對不上整個 `test-quality` 拒跑。
- **本機測試、儀器測試**:本機測試放 `src/test`,在電腦的 JVM 上跑;儀器測試放 `src/androidTest`,裝到平板上跑。
- **編排者、會談暫存區**:編排者是主持這次演練的主對話;會談暫存區是這個對話專用的暫存目錄,不在任何 repo 裡。

考場(mOrangePos develop 65f05c0)的實際條件,寫計劃前唯讀查過:
- 被測對象選現金收支「類別管理」的 ViewModel(126 行;公開文件裡代稱 `CategoryVm`):有畫面狀態、用 SharedFlow 送的一次性事件、以「進行中請求數」驅動的 loading、「建議下一個排序號」的計算。
- 它直接依賴資料層的一個具體類別(建構時要 Android 的 Context)和讀全域設定的網址組法,原樣在電腦 JVM 上建不起來,要先開一個可替換的資料來源介面。
- 測試依賴只有 JUnit 4.13.2、Truth、core-testing;沒有 mock 套件、沒有協程測試函式庫、沒有 Robolectric。
- 協程在 build 檔宣告 1.5.1,實際解析是 1.9.0(被其他套件拉高),所以 `kotlinx-coroutines-test:1.9.0` 可用、`runTest` 與 `backgroundScope` 都有,正式程式的版本不用動。
- 平板 SM-X710 已連線;上面沒有裝 mOrangePos,只有另一個專案的 App。

最小解:只在 mOrangePos 的演練分支動手,不併回;工具鏈這邊產出一篇驗證紀錄、標準的修補,以及演練中發現的收證工具缺口修補(見做法第 7 步與 S5)。不新增指令。

PRIOR-ART: 收證與故障證明照 [[Projects/測試品質工具接線_計劃]] 的 Android 原生案例(當時用模擬器、JUnit XML 加 `capture/check`);預埋錯誤的做法借變異測試與 lumos 破壞測試的「拿掉保護、要求測試變紅」;「寫測試的人不知道錯埋在哪」借盲測的做法。裁定:借用,不自建工具。
RETIRE-IF: 演練做完、驗證紀錄寫好、標準缺口都修進標準或開了 Issue,這份計劃就結案;之後標準大改時才重跑 [retire:when-status:Projects/Android單元測試標準實機演練_計劃=done]。

## 做法

1. **考場準備**(mOrangePos 另開的獨立工作樹,分支 `drill/android-unit-test-standard`,不推不併):
   - 替 ViewModel 開一個資料來源介面(三個方法:取清單、新增、作廢),正式實作包住原本的資料層類別與網址組法;ViewModel 只依賴介面。行為不變。
   - 測試依賴加 `kotlinx-coroutines-test:1.9.0`(本機與儀器兩路)。
   - 收證的 `--report` 一次只收一個檔,Gradle 每個測試類別各寫一份 XML,所以收據按類別分開收。
   - 儀器測試跑演練用的 debug 變體(套件名多一個開發用尾碼),不碰任何正式套件。
2. **需求書**:由編排者從程式註解、畫面行為與圖譜整理成「使用者看得到的行為」,不寫實作細節;存在會談暫存區,只給寫測試的代理。
3. **預埋錯誤**:在考場另一份副本裡埋 5–7 個錯,每個對應需求書的一條行為(例如排序號算錯、某種失敗沒提示、loading 提早關掉);寫測試的代理交件前,清單只存在會談暫存區,代理看不到;交件後才套用、收證,結果寫進驗證紀錄與卷證。
4. **乾淨代理寫測試**:只給需求書、資料來源介面與 ViewModel 的公開簽名、標準那一節;寫本機測試(`src/test`)與平板上的儀器測試(`src/androidTest`)。
5. **刻意壞測試**:另外寫一組,每支示範一種壞寫法——只驗呼叫次數不驗結果、靠預設回傳值才綠、事件在測試開始收之前就發掉了(收不到卻沒斷言)、用 `Thread.sleep` 等結果、篩選選不到測試卻回報成功(Gradle 預設零選中會失敗,所以要先示範預設被擋,再模擬專案關掉 `failOnNoMatchingTests` 的情況)、斷言自己比自己;演練中另加了「預期值照抄實作算法」與「協程沒推進就斷言」兩種。
6. **規則檢核**,每支測試、每個錯都記一列「被哪一道抓到」:
   - Gradle 本身(零選中、編譯錯)。
   - `lumos test-quality scan`、`capture --target`、`check`(原版綠;故障版有目標紅、而且紅的全是目標、全是斷言失敗;還原綠)。這次沒帶 `--semgrep`,對照表裡靜態掃描那一欄記「沒跑」。
   - 標準條文逐條對照(審查用)。
   - 平板實跑的 XML 與退出碼。
7. **除錯與訂正**:
   - 錯沒被抓到 → 先判是測試漏、需求書漏、還是標準沒要求;測試漏就補測試再跑一次故障證明。
   - 壞測試沒被任何一道抓到 → 標準補條文,或記成機檢候選。
   - 標準的修補走工具鏈的提交與代碼審,跟這份計劃同一個分支。
   - 演練中發現收證工具不認得 Truth 的斷言失敗(本機報告型別多了 `WithFacts`),在名單上精確加兩個型別;Truth 的 `Expect` 規則丟的 `Truth$SimpleAssertionError` 也會包住不是斷言的例外,不加,另以反例測試釘住。
   - 裝置報告沒有型別欄:原本只認第一行以 `java.lang.AssertionError:` 開頭的文字;平板實跑的樣本顯示字串 `assertEquals` 第一行是 `org.junit.ComparisonFailure: …`、不帶訊息的 `assertTrue` 第一行只有 `java.lang.AssertionError`。改成同一條規則:第一行剛好是這兩個型別之一(可接冒號加訊息),而且要有 JUnit `Assert` 的堆疊。Truth 在裝置上把類別名藏起來,維持不認。
   - 改了 `test_quality.py` 要一併更新主程式裡的配套指紋表。收據裡存著當時的歸因結果,換了收證工具版本之後,如果同一份報告重算的結果跟記錄不同(例如裡面有 Truth 型別的失敗),舊收據核對時會被拒(收據不記工具版本;訊息 `recorded test outcomes differ from raw report`,錯誤碼寫雜湊不符),要重收,不是偽造。
   - 同一個判定函式也被安全證據閘的兩條路用:故障敏感度那條會開始接受 Truth 與裝置字串比較的故障收據(跟一般斷言失敗一樣算抓到錯);JUnit 宣告那條從「無效:不是斷言失敗」變成「失敗:斷言失敗」,兩者都不放行。
   - 靜態掃描這次沒帶 `--semgrep`(這台機器也沒裝 Semgrep),所以是「沒跑」,不是「抓不到」;Kotlin 規則只有 `assertEquals(x, x)`,Truth 寫法的自比本來就不在規則內。
   - 卷證分兩處:公開的工具鏈只放去識別化摘要(類別名、套件名、欄位名換代稱,不放考場原始碼、代理寫的測試、patch 與收據快照);能重跑的完整卷證提交在考場的本機演練分支,不推(Enzo 2026-11-01 裁,因為工具鏈 repo 是公開的、考場是公司私有 repo)。
   - 改到 `test_quality.py` 會碰到兩條掛在它身上的舊回頭條件(要求改歸因時重跑正反例、零選中、編譯錯、還原);這次在 Android 那路實跑了這些,C# 與 iOS 的原生 runner 沒重跑,只靠收證工具的合成測試。消費專案裝的收證工具副本要等下次 `lumos update` 才會更新。

## 驗收條款

- [S1] 當乾淨代理只依需求書與標準寫完本機測試時,這組測試應在考場原版全綠,且每個預埋錯誤都應有至少一支測試在故障版翻紅、還原後翻綠,並有 `lumos test-quality check` 的三份收據(同一類別裡有測試是被假實作丟例外「當掉」紅的,收證時用 `--tests` 縮到用斷言抓到的那支);沒被抓到的錯應記下歸因(測試漏/需求書漏/標準沒要求)與訂正結果。 [manual:看驗證紀錄的故障對照表與收據]
- [S2] 當儀器測試在平板 SM-X710 上跑完時,應保留原始 XML 與退出碼(在考場本機分支的完整卷證;公開卷證放去識別化摘要),裝置型號與 API 等級應記錄在驗證紀錄;判綠只看這次寫的儀器測試,專案原有、跟變體不合的範本測試要在驗證紀錄寫出測試名與紅的原因;本機 JVM 全綠不得當成裝置實跑的證據。 [manual:看驗證紀錄附的平板 XML 與退出碼]
- [S3] 當刻意壞測試逐支送檢時,每一支都應記錄被哪一道抓到或漏掉;漏掉的應有對應的標準修補或機檢候選紀錄。 [manual:看驗證紀錄的壞測試對照表]
- [S4] 演練期間 mOrangePos 的主工作目錄與 develop 分支應保持不變,平板上只應安裝演練變體(開發用尾碼)的套件。 [manual:比對平板演練前後的套件清單、develop 的提交編號;主目錄演練前的狀態沒有記錄,只能證明 develop 沒變、演練指令沒有寫進主目錄]
- [S5] 當收證工具讀到本機 JUnit 報告的失敗型別是 Truth 的 `ComparisonFailureWithFacts` 或 `AssertionErrorWithFacts`,或讀到沒有型別欄、第一行剛好是 `org.junit.ComparisonFailure`(可接冒號加訊息)或 `java.lang.AssertionError` 且有 JUnit `Assert` 堆疊的失敗時,應認定為斷言失敗;沒有型別欄的 Truth 文字、Truth 的 `Truth$SimpleAssertionError`、一般例外訊息裡提到這些型別名、Caused by 包著它們、型別名後面多了字的,都不應認定。 [test:t_test_quality_cli](整份跑收證工具的測試檔,裡面的 test_truth_local_assertion_types_are_attributed、test_truth_device_text_without_type_is_not_attributed、test_truth_expect_rule_type_is_not_attributed、test_runtime_exception_mentioning_truth_type_is_not_attributed、test_device_comparison_failure_and_bare_assertion_are_attributed、test_device_runtime_around_comparison_failure_is_not_attributed、test_truth_lookalike_types_are_not_attributed 七支);安全證據閘故障敏感度那條路另由 `t_secev_fault_truth_assertion_counts_like_assertion` 釘住 [test:t_secev_fault_truth_assertion_counts_like_assertion]
- [S6] 當讀測試品質標準的〈Android 本機單元測試的驗收標準〉時,應寫到演練補進的幾條:加測試函式庫前看實際解析版本、Gradle 跳過測試要 `--rerun`(舊版用 `--rerun-tasks`)、混著當掉紅要縮小篩選、裝置那路認得 `org.junit.ComparisonFailure`、裝置收證用類別篩選、Truth 的 `Expect` 規則收不到、Kotlin 靜態掃描要帶 `--semgrep`、儀器測試等真執行緒用真時間、被「當掉」抓到的錯不算、收據存著當時的歸因結果(換版後重算不同會被拒),而且「機器抓不到」那條應指回演練的驗證紀錄。 [test:t_test_quality_standard_android_drill_lessons]

## 回退

- mOrangePos:刪掉演練工作樹與分支即可,主目錄與 develop 沒有任何提交。
- 平板:解除安裝演練變體(套件名多一個開發用尾碼)與它的測試套件(儀器測試跑完預設也會自己移除)。
- 工具鏈:還原這份計劃、驗證紀錄、標準修補、收證工具那個判斷與指紋表、跟著它的測試(收證工具測試檔的新正反例、測試總檔的兩支新守衛與測試輔助的新失敗型別)、收證工具的家那幾行的提交(同一個提交,一起還原,只還原程式會讓守衛測試紅);還原後 Truth 與裝置字串比較的故障收據回到判無效,這段期間收的這類收據要重收;安全證據閘故障敏感度那條路對這類收據的放行也一起撤掉。

## 實務隱患

- 效能:考場一次本機測試約一兩分鐘、一次儀器測試含安裝約數分鐘;故障證明每個錯要跑三次。
- 已排除:金流:被測的是現金收支類別的管理,不碰付款與刷卡;測試全用假資料來源,不連後端。
- 已排除:對外送出:測試不連網、不連 POS 主機,只在平板本機執行。
- 已排除:不可逆:演練分支不推不併;平板只裝演練變體的套件,可解除安裝。
- 守衛面:收證工具的斷言歸因在本機那路多認 Truth 兩個精確型別名、在裝置那路多認第一行剛好是 `org.junit.ComparisonFailure` 與不帶訊息的 `java.lang.AssertionError`,會讓原本判無效的這幾類故障收據變成有效;安全證據閘的故障敏感度那條路因此也開始接受這類故障收據(新增的放行面),JUnit 宣告那條則從無效變成斷言失敗(兩者都不放行);反例測試釘住沒型別欄的 Truth、`Expect` 規則的型別、訊息提到型別名、Caused by 包著、型別名後面多字這幾種不放行。

## 審計修正紀錄

- 原編號 r1(2026-11-01,三席加架構對齊,全 sonnet 同門):21 條/blocking 5/卡在「收證工具在裝置那路認不得字串比較」與「公開卷證不能重跑」兩件事,全部折入;處置閘過了。之後代碼審的卷證席指出這一輪的快照與席報告含考場真實識別字,Enzo 裁定換編號重審:原編號的證據、凍結判定與四行審查帳移到考場本機卷證 `drill-evidence/design-review-r1-withdrawn/`,公開 repo 不留;重審用 `Android單元測試標準實機演練-std`。
  - 例:平板儀器報告裡字串 `assertEquals("10", "0")` 的失敗文字(第一行 `org.junit.ComparisonFailure: …`、下一行 `at org.junit.Assert.assertEquals`)→ 改前判「不是斷言失敗」、收據拒收;改後判斷言失敗。
  - 收證工具裝置那路改成「第一行剛好是兩型別之一、有 Assert 堆疊」:不加的最小解是只改標準叫人別用字串比較,但被測 ViewModel 的輸出就是字串,照做就沒辦法在裝置那路收證,所以改判定;用的是同一個函式、同一種精確比對,不是新機制。
  - Truth 的 `Expect` 規則不加進名單(它也包非斷言例外),改成反例測試釘住。
  - 卷證照 Enzo 裁定分公開去識別化摘要與本機完整卷證兩處;S2、S4 改成照實寫證據在哪、主目錄演練前狀態沒記錄。
  - 標準補裝置那路收得到哪些斷言、裝置收證用類別篩選、`--rerun` 的版本限制、混著當掉紅時縮小篩選、零選中由誰擋、`--semgrep` 旗標、收據存著當時的歸因結果、換版後重算不同會被拒;新增條款 S6 與守衛測試。
  - 驗證紀錄補:預設回傳值那格的實跑報告、Semgrep 是沒跑不是抓不到、需求書與錯同一人寫所以不能單獨歸功標準、安全證據閘的影響面。
- 代碼審 r1(`code-收證認得Truth與裝置字串比較`,通才、卷證、架構對齊三席):安全證據閘故障敏感度那條路其實會開始接受 Truth 與裝置字串比較的故障收據,原本四處文件寫成「都不放行」,改正並補測試;補近似型別名的反例、守衛測試的 `--rerun` 精確比對、錯誤訊息附英文原句、「Caused by 之前」的說法、刻意收窄的說明;卷證補修補前樣本的註明。
