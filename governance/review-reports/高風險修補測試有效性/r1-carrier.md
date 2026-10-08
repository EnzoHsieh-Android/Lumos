severity: major

彙總載體，非新增審查席。六項由四份原報告彙整，severity及引句不變。


來源：r1-通才.md
ID: g1
severity: major
blocking: 是
引句:「留原文／改文、指紋、命令與輸出，確認錯誤真的被載入」
file: `governance/review-reports/高風險修補測試有效性/r1-snapshot.md:26`
具體輸入: 挑戰案例的測試命令在失敗時把測試環境中的憑證、連線字串或帶個資的請求內容印到 stdout/stderr；範本依設計保留完整命令與輸出作卷證。
錯誤結果: 秘密或個資會被原樣寫入治理卷證並隨 repo 提交；「無對外副作用」不會防止本機輸出外洩，現有設計也沒有要求輸出最小化、遮罩或提交前秘密掃描。
最小重現:
```sh
TOKEN=fake-secret-123 sh -c 'echo "request failed token=$TOKEN" >&2; exit 1' > r1-mutation.log 2>&1
rg -n 'fake-secret-123' r1-mutation.log
```
結果會命中 `request failed token=fake-secret-123`；若照設計保留該輸出，敏感值即進入卷證。最低修正是規定只保存判定所需節錄，保存前遮罩秘密與個資，並把未能安全節錄的案例列為未判定。

覆蓋: 已完整讀 `r1-snapshot.md` 57 行及 `r1-graph-lens.txt` 12 行。摘要與退場條件已讀，無其他 finding；〈範圍與方法〉除 g1 外已讀，無其他 finding；〈條款〉已讀，無 finding；〈實務隱患〉已讀，但未涵蓋 g1 的卷證輸出洩漏；〈回退〉已讀，無 finding；〈接手〉已讀，無 finding；〈前掃界線〉已讀，無 finding；圖譜鏡頭兩條 `guard kill` invariant、落點與證據天花板已逐項核對，並查閱 `cmd_guard_kill`／`_kill_attribute` 指令語意，無其他 finding。

總結 severity: major；blocking: 1 條。


來源：r1-證據品質.md
ID: e1
severity: major
blocking: 是
引句:「每條讀結果狀態、弱證據與實際失敗內容，總退出碼不能代替逐條判讀」
file: `governance/review-reports/高風險修補測試有效性/r1-snapshot.md:30`
file: `scripts/lumos:16037`
具體失敗案例：某配方回傳 `verdict=killed, weak=true`；`weak` 可能來自 whole-suite、flaky、筆記未提交或修改時間無法證明錯誤版已載入，但規劃只要求「讀」weak，沒有規定 `weak=true` 必須判未定或補強後重驗。現行 rc 又只看 verdict：批次只要含一筆 `killed` 且沒有 survived/error，即可回 0，因此逐條抄下 weak 仍可能宣告有效偵測。
最小重現：
```sh
python3.14 scripts/test_lumos.py -k guard_kill_mtime_unsure_is_weak
```
觀測：案例通過並證明結果列可同時是 `weak=true`；`scripts/lumos:16086-16108` 的 rc 判定不讀 `weak`。
判準：符合 [S2] 的流程必須明定每種 `weak=true` 的處置；至少不能把它直接算成「目標行為斷言已因錯誤翻紅」。目前文字容許記錄 weak 後仍判有效，會破壞本案核心目的。

ID: e2
severity: major
blocking: 是
引句:「判定killed也仍須檢視真正斷言，輸出文字歸因不保證語法、收集或載入成功」
file: `governance/review-reports/高風險修補測試有效性/r1-snapshot.md:30`
file: `scripts/lumos:15789`
具體失敗案例：既有 `_kill_attribute` 只要測試名後五行內出現 `FAILED` 或 `AssertionError` 就歸因成功；收集期語法錯或 fixture 載入錯也能得到 `killed`。但規劃沒有指定取得完整失敗內容的證據通道；一般文字輸出不印 `attr_excerpt`，JSON 也只保留最多 200 字，kill-log 更未保存它。照目前指路執行時，審查者可能只拿到 `✓ killed`，無從完成規劃自己要求的「真正斷言」核對。
最小重現：
```sh
python3.14 - <<'PY'
import runpy
m = runpy.run_path("scripts/lumos")
print(m["_kill_attribute"](
    "TestLimitFive\nFAILED during collection: SyntaxError: invalid syntax\n",
    "TestLimitFive"))
PY
```
觀測：回傳 `(True, 'TestLimitFive\nFAILED during collection: SyntaxError: invalid syntax')`；若挑戰命令 rc 非零，`scripts/lumos:16011-16015` 會判 `killed`。
判準：要落實 [S1]/[S2]，共用範本須指定可重放且足以看出 assertion、collection、load 差異的完整證據來源；證據取得不到時必須判未定，不能讓 `killed` 或 rc0 代替。

其餘覆蓋：錯誤等價、無效錯誤、未到達路徑、未執行、基線未綠、錯誤載入、超時、不穩定、無關紅燈與總 rc 的文字界線均已逐項核對，除上述 weak 處置與失敗內容通道外無其他 finding。圖譜鏡頭已完整核對；其中 invariant 只保證 rc 優先序與 JSON 純度，沒有補上上述兩個證據缺口。

總結 severity: major；blocking: 2。


來源：r1-可執行性.md
ID: x1
severity: major
blocking: 是
引句:「只在無對外副作用的隔離副本修改一處相關行為，留原文／改文、指紋、命令與輸出，確認錯誤真的被載入。」
問題：設計把「程式碼副本隔離」直接當成「沒有對外副作用」，但實際 `cmd_guard_kill` 的隔離單位只是 Git worktree；技能來源也明載沙盒不隔離資料庫，只適用於能自行清理的測試。計劃沒有要求斷開真實端點、改用測試憑證／假身分、確認資料可重置，亦未要求留下這些隔離條件的證據。「不能安全隔離者不執行」只是結論，沒有可操作的判定門檻。
具體失敗案例：高風險案例的測試沿用本機環境變數，指向共享 staging 資料庫與真 webhook。程式碼確實只在 worktree 中被改壞，但基線與挑戰各建立一次正式訂單、發出通知；審查仍可能依計劃把「無對外送出」列為已排除。應把外部端點斷線、測試身分及資料重置能力列為執行前證據，缺一即未判定、不執行。

ID: x2
severity: major
blocking: 是
引句:「有效偵測須是目標行為斷言因該錯誤失敗；語法錯、載入／收集失敗、超時、未執行或不穩定均未判定，不能把非零退出當成功。」
問題：流程只有一次原版綠與一次錯誤版紅，卻沒有要求固定亂數種子、時間、測試資料與執行順序，也沒有在判定 killed 前還原原版再跑一次。看到「目標斷言紅」仍不足以證明是植入錯誤造成；`_kill_attribute` 也只是以測試名附近出現失敗標記做歸因。計劃只在「補案例／斷言後」要求原版綠、同錯誤紅，初次判定有效時缺少同等的因果對照。
具體失敗案例：案例含隨機資料，基線 seed A 通過；植錯後 seed B 剛好觸發原本就存在的邊界失敗，而且失敗位置正是目標斷言。依現稿會判定測試成功抓錯，實際上錯誤版即使不植錯也會在 seed B 失敗。至少應固定所有可控輸入，並以同一隔離狀態完成原版綠→錯誤版紅→還原原版綠；任一步不一致即未判定。這是必要對照，不是「反覆重跑洗綠」。

覆蓋：已完整逐節核對 `r1-snapshot.md` 的開頭欄位、白話目標、WHY／PRIOR-ART／RETIRE-IF／REVISIT、範圍與方法、S1–S3、四類實務隱患、回退、接手及前掃界線；亦完整讀取 `r1-graph-lens.txt`，核對其中兩條 guard-kill 合約、測試綁定狀態與 `Systems/每輪修補差異派工` 落點。另核實技能來源及實際 `cmd_guard_kill`／`_kill_attribute`。除上述兩項外，未發現此鏡頭下其他 blocking 問題；完整版本固定、逐條弱證據判讀、結論範圍收窄與成本退場條件本身已有交代。


來源：r1-架構對齊.md
ID: a1
severity: major
blocking: 是
引句:「每條讀結果狀態、弱證據與實際失敗內容，總退出碼不能代替逐條判讀」
具體失敗案例：現行 `_kill_attribute` 只找「測試名後五行內的失敗標記」，並把摘錄截成 200 字；一般文字輸出只印 verdict/detail，治理帳也不保存該摘錄。假設 pytest 先印 `test_limit FAILED`，真正的 assertion traceback 在稍後數百字之外，`guard kill` 會判 `killed`，但審查者拿不到足以確認「目標行為斷言因該錯誤失敗」的內容。此時設計只有兩條路：直接相信 `killed`，違反 S1/S3；或另行重建突變並重跑測試，形成沒有與原配方執行逐筆綁定的第二套做法。快照同時宣告「不修改CLI」，因此核心證據要求目前沒有可執行的既有入口。應擴充既有 `guard kill` 的診斷輸出，讓每列提供足以核對斷言原因的受限輸出或可重放證據，並維持既有七態、退出碼與背書算法不變。

覆蓋：已完整讀取 `/private/tmp/lumos-future-repair-regression-research/governance/review-reports/高風險修補測試有效性/r1-snapshot.md` 與 `/private/tmp/lumos-future-repair-regression-research/governance/review-reports/高風險修補測試有效性/r1-graph-lens.txt`。逐節核對了來源與退場條件、範圍與方法、S1–S3、實務隱患、回退、接手及前掃界線；並核對實際 `cmd_guard_kill`、`_kill_attribute`、共用 `templates.md §3.1` 及現有兩處指路。除 a1 外，既有模組分工、`guard-kill` 七態及兩條圖譜合約、人工抽查不得冒充背書、單一共用範本加兩處指路、既有 `Systems/每輪修補差異派工` 落點均未發現另立衝突來源或破壞現行放行合約。
