severity: major

## I1 步驟 1 的「3 次取中位數」會被 Gradle 的 UP-TO-DATE 吃掉,量到的不是冷的一次呼叫
severity: major
blocking: 是(量法會產出失真的 T 與 Σt,而整個停手判定都建在這兩個數上)
引句:「每個壞法各做 3 次一次呼叫,取 T 的中位數那一次」
1. 輸入:同一個壞法套上後連跑 3 次 `./gradlew :app:testDebugUnitTest --tests <守的測試>`,來源與測試輸入都沒變。
2. 走到:第 2、3 次時編譯任務是 UP-TO-DATE,不再編譯。已知存活的壞法測試全綠,測試任務也會 UP-TO-DATE 直接跳過,Σt = 0,T 只剩 Gradle 設定時間。已知被殺的壞法失敗,測試任務會重跑,但編譯仍被跳過。
3. 壞在哪:全文沒有寫 `--rerun-tasks`、`cleanTest` 或關閉建置快取。中位數因此多半挑到「被快取過的」那一次。這樣會(a)把〈白話〉列為可省的「編譯」整項量掉,(b)讓存活壞法的 Σt 為 0,使 s 趨近 1,而這 4 個以上的存活壞法占了樣本近半。S1 的「30 次都有數字」也擋不住這個問題。
4. 反過來,如果每次都強制重編,量到的又不是原型要比較的狀態,文中也沒有定義哪一個才是對照基準。

## I2 s 的定義內部矛盾:「第一次沙盒初始化」同時被算成可省和省不掉
severity: major
blocking: 是(停手門檻 0.6 的判定值因此偏低)
引句:「第一次 Robolectric 沙盒初始化;省不掉的是每支測試自己花的時間(含 Robolectric 每支測試前的環境初始化」
1. 〈白話〉把「第一次沙盒初始化」列在可省項。〈用詞〉的 Σt 又說 afterTest 的 `endTime - startTime` 含 Robolectric 每支測試前的初始化。
2. 第一次沙盒初始化(載入 android-all jar、建沙盒)發生在第一支測試執行期間,會落進 Σt 的第一支測試時間,而不是 T−Σt。
3. 所以 s 的分子漏掉這一項,s 被系統性低估。0.6 的門檻是用「最多快 2.5 倍」推出來的,這個偏差可能讓真正值得做的方案在第一步就被停掉。〈做法〉第 2 步把「第一次沙盒初始化」另列為一次性成本,與第 1 步的拆法對不上。
4. 文中沒有說明要用哪個量(第一支測試 vs. 其餘測試的時間差)把這項拆出來。

## I3 步驟 1 沒有逾時規則,而最花時間的正是會掛住的壞法
severity: major
blocking: 是(實驗答的問題與動機數字對不上)
引句:「2026-11-26 在實驗專案量到 142 個壞法共 14197 秒、平均約 100 秒一個」
1. 動機引用的 14197 秒,依 file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:22` 與 `:85`,約四分之三花在 25 個慢壞法上(逾時 11 個、斷路器停用期間 10 個)。其餘 117 個走快路,平均只有 7–28 秒。
2. 步驟 1 的 10 個壞法只取「已知被殺或已知存活」,沒定義單次呼叫的逾時上限。已知被殺的壞法可能就是逾時被判殺掉的(該 FACT 寫逾時 11 個裡 10 個判殺掉)。一旦掛住,T 就是整個逾時時限。
3. 即使不掛住,常駐程序省不掉掛住的等待,第 2 步遇到逾時就結束整個原型。實驗量的 s 因此不能回答「14197 秒能省多少」。〈白話〉把「平均約 100 秒一個」寫成每個壞法都重編、重開 Gradle 的代價,與該 FACT 的拆帳不符:合併快篩已經攤掉了一部分。
4. 另外,`平均約 100 秒一個` 出自該計劃 `:22` 的敘述,不在 `:41` 那條標了 `[來源:人工]` 的 FACT 裡。〈白話〉卻稱它為「實測 FACT」,引用不精確。

## I4 「已知被殺/存活」的來源在筆記裡查不到
severity: major
blocking: 是(步驟 1 的樣本和 S4 的判定對照無處可挑)
引句:「其中至少 4 個已知被殺、至少 4 個已知存活」
1. 在 repo 的 `docs/lumos-toolchain-knowledge/` 與 `governance/` 全文搜過,`domain/settlement` 只出現在本計劃與它的快照。
2. 在 Projects/Verification/Systems 裡也找不到「批 4a」的紀錄(`Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md` 沒有逐壞法判定)。「批 4a」只在使用者記憶 `overnight-2026-11-26-delegation.md` 裡有,按家規那不算依據。
3. 三個月後照做的人無法重建「4 個已知被殺、4 個已知存活」的候選清單。這個清單需要存成可查的紀錄,位置沒有寫。

## I5 常駐原型怎麼拿到 Gradle 測試的設定,沒有說
severity: major
blocking: 是(S3、S4 的對照口徑可能不成立)
引句:「寫一支測試入口:一個 JVM 裡依序設定開關、用 JUnit 程式化執行那幾支守的測試」
1. 這支入口脫離 Gradle 跑。Gradle 的測試任務設了 classpath、`jvmArgs`、系統屬性、Robolectric 的 `includeAndroidResources` 與 mergedAssets 等,全文都沒寫程式化入口如何取得。
2. 缺了這些設定,S3(開關全關要與原樹相同)與 S4 的判定可能因設定不同而錯,結果可能是環境落差而不是常駐的差別。
3. 〈不做〉已承認這是換測試執行引擎、會改判定口徑,但只推給「之後另開計劃」。第 2 步的原型自己就用了這個引擎,並以它決定值不值得。文中沒有規定在原型裡如何確認口徑同等。

## I6 PIT 與 METFORD 的引用,逐項核對
severity: minor
blocking: 否(結論方向沒錯,只是措辭過頭)
引句:「PIT 另開子 JVM 跑測試,不必重開 JVM 但能砍掉」
1. 已查 https://pitest.org/faq/ :「壞法保存在記憶體、不寫磁碟」成立。該頁也說 PIT 另開 child JVM,且靜態初始化段寫到逾時「需要起新 JVM」。依據來源表的「不必重開 JVM」與「逾時需另起 JVM」不一致。FAQ 沒有明寫「掛住會砍掉並重開」,這句是推論,不是出處原文。
2. METFORD(https://arxiv.org/html/2501.02875v2)的數字已核對:產生快 8.50%、磁碟省 99.78%、執行快 6.45%,在模擬器上跑儀器測試、app 只裝一次,與引句相符。
3. Gradle afterTest 與 Robolectric architecture 兩個出處我沒有逐字核對(Robolectric 那頁在 robolectric.org/architecture,沒有抓)。⚠ 判不準。

## I7 第 2 步失敗時沒有對應的寫回條款
severity: minor
blocking: 否(不影響第一步的正確性,但三個月後會漏寫回)
引句:「十次合計比小於 0.6 時,本計劃 應 寫「照舊否決」結論」
1. S2 只涵蓋第一步 <0.6 時的寫回。RETIRE-IF 還包含第二步邊際比值中位數不小於 0.5、或靜態狀態清不乾淨、或正控制不過。這幾種情形沒有對應的驗收條款。
2. 〈落點〉「否決:改〔第二段〕…那列」只寫了一次,沒有說第二步失敗的結論要不要也補實測值。
3. 另外,停手條件「達不到 RETIRE-IF 的 2 倍」把第一步的 0.6(2.5 倍上限)與第二步的 0.5(2 倍)混用,而 RETIRE-IF 第一句沒有寫 2 倍。

## I8 落點與舊否決比對
severity: minor
blocking: 否
引句:「回指條款那條不動(理由不同、本實驗沒碰)」
1. 已核對:第二段〈依據來源〉表那列與 PRIOR-ART「排除:mutant schemata」存在(file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:35` 與 `:170`)。回指條款〈不做〉那句存在(file: `docs/lumos-toolchain-knowledge/Projects/選擇點存活回指條款_計劃.md:179`)。
2. 回指條款自己的 WHY 與 PRIOR-ART(`:55`、`:59`、`:213`)還把 mutant schemata 與 METFORD 當作「合批編譯」的依據,且該計劃第 35 行說合批編譯是「mutant schemata 的輕量做法」。本計劃說「回指條款那條不動」,卻沒說明這幾處引用若本實驗重開會不會連動。
3. `lumos new verification ... --plan ... --systems ...` 旗標存在且符合 file: `scripts/lumos:85892`-`85895`。`Systems/guard-kill` 存在,其 responsibility 明文涵蓋 choice-kill 準備物件。FACT 的 `[來源:人工]` 是合法值。這幾處已讀,無 finding。
4. 〈落點〉要通知 `選擇點挑法易混淆寫法優先_計劃`:該篇 `:67` 把「一行多挑」留給「量出單個壞法夠快之後再議」,判準與本計劃的 s≥0.6 並不相同,文中沒說明兩者怎麼銜接。

## 其他節
〈做法〉第 0 步、〈回退〉、〈實務隱患〉、〈不做〉其餘項、已排除各行:已讀,無 finding。

## 固定席節點(Systems/guard-kill)
本計劃不改任何程式與 `run_cmd`,不碰 `t_guard_kill_rc_precedence` 與 `t_guard_kill_json_purity` 兩條 INVARIANT 的行為:量測不經 guard kill,所以 rc 優先序與 `--json` 單行輸出都不受影響。唯一落點是在 guard-kill 補一行 FACT,不改既有 KEY。

最嚴重 severity:major
blocking 條數:5(I1、I2、I3、I4、I5)
