severity: major

## I1 「批 4a、80 個壞法、3681 秒、平均 46 秒」在圖譜與卷證都查不到出處
severity: major
blocking: 是(實驗的出發點與 S5 的對照基準都建在這個數字上,且依專案規則「沒指到圖譜節點就不得拿來做決定」)
引句:「2026-11-27 實驗專案批 4a 正式重跑 80 個壞法共 3681 秒,平均約 46 秒一個」

1. 我在 repo 的 docs 與 governance 全文搜 `3681`,只中到不相干的雜湊。
2. 「批 4a」在圖譜裡只出現在 `docs/lumos-toolchain-knowledge/Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md`,指的是「分帳本實作批 4a 的版本 4bfa471」。那篇驗證是 11-26 重跑 25 行共 2633 秒、32 個壞法,不是 11-27 的 80 個。
3. 第四段計劃的 FACT(`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:41`)記的是 142 個壞法 14197 秒、平均約 100 秒。
4. 這份 spec 引的 80 個、3681 秒、46 秒沒有 `[[連結]]`,也沒有 `FACT:` 與 `[來源:]`。三個月後接手的人沒法重驗。
5. 開頭說「30 秒降到多少」,正文用 46 秒當現況,兩個數字也對不上。

## I2 「Robolectric 初始化」被當成一次性成本,但引用的官方文件寫的是每支測試前都要初始化
severity: major
blocking: 是(停手條件 50% 的分子與常駐能省多少,都取決於初始化是一次性還是每支測試都付)
引句:「第一支 Robolectric 測試開始前的初始化、測試本身」

1. 〈依據來源〉第四列引 https://robolectric.org/architecture,寫「每支測試前大量初始化」。我抓該頁,原文是「there is also extensive Android environment initialization that occurs before each test」,每支測試結束後還會重置。
2. 拆帳只切「第一支測試開始前」的初始化。每支測試前的環境初始化會被算進「測試本身」。
3. 結果有兩個:
   - 常駐 JVM 只能省 JVM 啟動、Gradle 啟動和沙盒類別載入,省不掉逐測試的環境初始化,所以第二步預期的 5 倍(預期值表 S5 的例子)缺乏依據。
   - 停手條件的分子少算了真正可省的部分,又把省不掉的部分混進分母,50% 門檻失去意義。
4. 拆帳要把「沙盒首次載入」和「逐測試環境初始化」分開量,spec 沒有這一刀。

## I3 同一個 JVM 連跑壞法,逾時或無窮迴圈的壞法會卡死整個常駐程序,spec 完全沒處理
severity: major
blocking: 是(S4「判定與現行相同」在逾時類壞法上做不到,實驗結論會被偏掉)
引句:「寫一支測試入口,在同一個 JVM 裡依序設定開關、用 JUnit 程式化執行那幾支守的測試」

1. 第四段實測(`docs/lumos-toolchain-knowledge/Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md`)32 個壞法裡有 9 個「測試掛住」。11-26 全量 142 個裡 15 個沒跑乾淨,其中逾時 11 個。掛住在這個專案不是罕見事件。
2. 現行做法是靠殺掉子程序處理掛住。常駐 JVM 裡的掛住,JUnit 程式化執行沒有強制中斷手段。PIT 之所以另開子 JVM,就是為了能砍掉它。
3. 〈實務隱患〉只列了靜態狀態污染與記憶體,沒有逾時或掛住。
4. S4 挑的 5 個壞法若不含掛住類,就量不到最貴的那一類;若含,原型會卡住。spec 沒說怎麼挑,也沒說掛住怎麼記。

## I4 對照與平均值的口徑沒定:一次性成本算不算、現行 46 秒含不含合併基準攤提
severity: major
blocking: 是(S5 的比值與 RETIRE-IF「快一倍以上」取決於口徑,口徑不同結論會翻)
引句:「卷證寫明兩個平均值與比值」

1. 常駐原型有一次性成本:整份編譯、Gradle 啟動、Robolectric 沙盒初始化。5 個壞法平均時,這些算不算進分母,spec 沒說。不算會把比值灌水。
2. 現行 choice-kill 的每個壞法時間,包含「合併基準一次攤在多個壞法上」(第四段〈做法〉:一次呼叫跑完,把基準攤在所有壞法上)。同時它有三種路徑:快篩通過約 18 秒、有失敗約 28 秒、編不過約 7 秒,有失敗的之後還會逐支跑(`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:41`)。
3. S1「十列四段加總跟總時間差不到 10%」對逐支路徑不成立。一個壞法會有多次 Gradle 呼叫,「Gradle 設定到測試開始」不是一個值。
4. 「5 個被殺、5 個存活」的取樣跟現行快路徑與慢路徑的比例無關,平均值不能外推到 46 秒那個母體。

## I5 〈不做〉表的位置寫錯,S2 要改的「那列」不在〈不做〉節
severity: minor
blocking: 否(目標句找得到,只是節名不對)
引句:「[[Projects/選擇點變異加速第二段_計劃]] 的〈不做〉表寫「不做 mutant schemata:METFORD 在 Android 上執行只快約 6%」」

1. `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第二段_計劃.md:111-116` 的〈不做〉是條列,沒有 schemata。
2. 那句在 `選擇點變異加速第二段_計劃.md:170` 的〈依據來源〉表,第一欄是「機制」、第三欄是「出處」。同檔第 35 行 PRIOR-ART 也有「排除:mutant schemata」。
3. S2 要寫的「實測啟動佔比」該放表的哪一欄、要不要同步改第 35 行,spec 沒講。

## I6 要寫回的筆記清單不全,其他引到同一個否決的計劃會與結論打架
severity: major
blocking: 是(重開後留下三處互相矛盾的筆記,是三個月後最先撞牆的地方)
引句:「量測結論寫回 [[Systems/guard-kill]](選擇點變異的守檔筆記)一行 FACT 或 WHY;否決就改 [[Projects/選擇點變異加速第二段_計劃]] 那列。」

1. 同一個否決還在這幾處:
   - `選擇點存活回指條款_計劃.md:179`〈不做〉:「不做完整 mutant schemata(壞法改成執行期開關)」。
   - `選擇點存活回指條款_計劃.md:55` 的 WHY 與 `:213` 的依據表。
   - `選擇點變異加速第四段_計劃.md` 的〈不做〉與依據來源。
2. 該計劃 status 是 `todo`,尚未落地。spec 只提「重開」,沒說不管結論如何,這些筆記要不要補「重開、量測中」或「結論」。
3. 反向牽連:`選擇點挑法易混淆寫法優先_計劃.md:60` 把「一行多挑」綁在這個實驗的結論上(status doing),spec 沒列它,結論要通知它。
4. 回寫到 `Systems/guard-kill` 的是「量測結果」(來源:人工的 FACT),不是程式行為,但 spec 沒給 `[來源:] [confirmed:]` 的寫法。
5. 「結論寫在本計劃」與「寫在卷證」的分工,spec 沒定。

## I7 與第四段、覆蓋選測試的關係只引了名字,沒交代誰先誰後、會不會互相污染量測
severity: minor
blocking: 否(第四段與回指條款都在進行中,但這個實驗不改 lumos 程式,碰撞面小)
引句:「([[Projects/選擇點變異加速第四段_計劃]] 的合併快篩與逐測試覆蓋都開著)」

1. 「逐測試覆蓋」是 `選擇點存活回指條款_計劃.md` 的機制,不是第四段的。`選擇點變異加速第四段_計劃.md` 全檔查不到逐測試覆蓋;出處標錯。
2. 第四段 status 是 doing,實驗專案上的 choice-kill 版本會變。拆帳量到的是哪個版本,spec 沒要求記 commit。
3. 回指條款的逐測試覆蓋走 JaCoCo 加獨立 init script,開著會把時間灌進「Gradle 設定到測試開始」。spec 沒說拆帳時是否關掉,拆帳口徑因此不穩。
4. `選擇點變異覆蓋選測試_計劃.md` 已 done,內容是「動測試執行引擎、會改判定口徑要人裁」。第二步在 JVM 裡程式化跑 JUnit 就是動執行引擎,spec 的〈不做〉沒承認這點,也沒說量出值得後要走那份計劃的人裁。

## I8 拆帳「只用自帶 init 腳本」的可執行性:lumos 沒有給使用者腳本與 `--profile` 的入口
severity: minor
blocking: 否(只是量測前置,不影響結論方向;但三個月後的人會卡在第一步)
引句:「實驗自帶一份只在本實驗用的 Gradle 初始化腳本,在編譯任務開始結束、測試任務開始、每支測試開始結束各印一行牆上時間(毫秒)」

1. choice-kill 的合併指令由 `_choice_merge_cmd` 從設定檔的 `run_cmd` 組出,工具自己插 `--init-script`(`scripts/lumos:28964`)。
2. 使用者腳本與 `--profile` 只能寫進 `run_cmd`。這等於改了實驗專案的 lumos 設定,而〈不做〉寫「不改消費專案 Gradle 設定」,只覆蓋到 Gradle 檔,沒覆蓋 `run_cmd`。
3. `run_cmd` 多帶 `--init-script` 後,`_choice_merge_shape` 能不能判出形狀、會不會觸發第四段的「帶腳本沒結果檔就不帶重試」(`選擇點變異加速第四段_計劃.md:62`),我沒實跑。⚠
4. 工作樹用完即刪,`--profile` 報告在 `build/reports/profile` 裡,要保留得帶 `--keep-worktree`,spec 沒寫。

## I9 外部出處核對:METFORD 數字對得上,但「Robolectric 初始化」那條對不上
severity: minor
blocking: 否(數字沒錯,錯的是那一條的引用;已併入 I2)
引句:「METFORD(Android mutant schemata,產生快 8.5%、磁碟省 99.78%、執行快 6.45%;app 只裝一次、每個壞法仍各跑一次測試)」

1. 我抓 https://arxiv.org/html/2501.02875v2:「8.50% less time for mutant generation」「99.78% less disk space」「6.45% faster」,且「push and install the built app only once」,每個壞法仍用 `setprop debug.MUID` 切換後各跑測試。與 spec 一致。
2. mutflow 與 Google 專利兩條我沒抓,未驗。⚠
3. 「執行只快 6%」的差距主要來自 METFORD 是真機,不是 JVM 內本機測試。spec 以 Android 測試的初始化成本類比,但 METFORD 那組是 instrumented 測試。這個對照假設沒寫出來。

## 逐節結論
- 白話:已讀,有 I1 與 I2 兩條。
- 跟舊否決差在哪:已讀,有 I5、I6。
- 做法:已讀,有 I2、I3、I4、I8。
- 驗收條款與預期值表:已讀,有 I4;S4 的「相同判定」見 I3。
- 不做、回退、實務隱患:已讀,有 I3 與 I8。回退節沒問題:不改 lumos、刪分支即還原。
- 落點、依據來源:已讀,有 I6、I9。

## 牽連節點(guard-kill)
判「不影響」。本計劃不改 `scripts/lumos`,所以兩條 ★INVARIANT★ 不受影響:
- rc 優先序(`t_guard_kill_rc_precedence`):不動判定。
- `--json` stdout 純度(`t_guard_kill_json_purity`):不動輸出。

唯一的牽連是 I6:回寫那一行 FACT 是量測數字,要寫 `[來源:人工] [confirmed:]`。

## 實務隱患逐類
- 資源與併發:有。常駐 JVM 掛住無法回收(I3);Gradle 守護程序與別的會談搶記憶體,spec 已寫。
- 外部呼叫、金流、不可逆:無。spec 已排除,我同意。
- 狀態污染:spec 已寫靜態狀態,但沒寫 Robolectric 沙盒內的 `ShadowXxx` 全域與資源快取跨壞法殘留。⚠

最嚴重 severity:major;blocking 共 5 條(I1、I2、I3、I4、I6)。
