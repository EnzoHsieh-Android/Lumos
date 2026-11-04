severity: blocker

**已讀,無 finding 的節**:用詞、分批、舊版初稿的去向、批三的進迴圈條件、回退、天花板。

**固定席節點逐條判**
- `Systems/linter精選目錄`:無合約行。本案只加 Kotlin 宣告範本,不改現有 detekt 範本。但範本裡的 `<toolchain>` 要寫成該節點 detekt 範本已用的 `$HOME/harness/lumos-toolchain`(見 `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:125`)。判不影響。
- `Systems/效能檢核目錄`:無合約行,本案不碰它的題表。判不影響。
- `Systems/棧別提問表態閘`:無合約行。本案範圍 7 只在 `code-loop pass` 前多叫它的判定,沒改判定本身。判不影響。

---

1. 回合結束檢查預設根本不會跑 ast-grep
severity: blocker
blocking: 是(讓範圍 5 整條機制失效)
- spec 段落:範圍 5、範圍 4、實務隱患〈回合結束檢查拖慢每一輪〉。
引句:「預算預設 20 秒,可用 `.lumos/config.json` 的 `lint_new` 區塊新加的 `stop_budget_sec` 調」
- 問題:工作樹檢查沿用既有判定函式。該函式在剩餘預算小於 `per_cmd_floor_sec` 時就不跑那條命令,把它記成「預算不足」。
- 查證:file: `scripts/lumos:38498` 預設 `per_cmd_floor_sec: 30`。file: `scripts/lumos:39125-39130` 在 `left < cfg["per_cmd_floor_sec"]` 時直接 `undone.append(kind: budget)` 並 `continue`。
- 重現:預算 20 秒小於保底 30 秒,第一條命令就被跳過。依範圍 4,沒跑到的命令「只列出不擋」,所以 `ast-grep` 一次都沒被呼叫,回合結束鉤子永遠回 rc0。spec 沒寫工作樹檢查要繞過保底值,也沒寫要把保底降到小於 20。

2. 回合結束鉤子的前置提早返回,會讓新那道在常見情況下不跑
severity: major
blocking: 是
- spec 段落:範圍 5。
引句:「既有鉤子現在只有一道、一則訊息;改成兩道各自判、各自佔各自的名額」
- 問題:spec 只說「各自判」,沒寫新那道插在哪。現有 `main()` 有三個提早返回,新那道若接在後面就繞不過去。
- 查證:file: `scripts/hooks/claude/check-graph-sync.py:998-1000`,`find_graph_root` 為 None 就 `return 0`。這種專案有 `.lumos/lint.json` 卻沒有 `docs/*-knowledge`,新那道不會跑。
- 查證:file: `scripts/hooks/claude/check-graph-sync.py:1038-1050`,筆記有動(`graph_touched`)就 `return 0`。本工具鏈的規矩是改程式同時寫筆記,所以這是常態,這時新那道不跑。
- 查證:file: `scripts/hooks/claude/check-graph-sync.py:1067-1070`,同一批檔案清單第二次就 `return 0`。同一批檔案但內容又改出新告警時,新那道被擋在外面。
- 重現:Android 專案這一輪改了 kt 檔和筆記,有新增告警,收工時什麼都不會發生。S6 的測試只驗「有宣告、有新增告警」的單純情況,抓不到這三條。

3. 兩道合計的時間會超過鉤子天花板
severity: major
blocking: 是
- spec 段落:範圍 5(預算 20 秒)與實務隱患。
- 查證:file: `scripts/merge-claude-settings.py:121` 該鉤子外層天花板是 40 秒,內層 0.7 倍等於 28 秒。同檔註解記了既有圖譜同步檢查實測要 25 秒。
- 重現:20 加 25 等於 45 秒,超過 40 秒時整支鉤子被 SIGKILL。既有擋停是「名額先佔再擋」(file: `scripts/hooks/claude/check-graph-sync.py:889-899`),被殺時名額已用掉、訊息沒送出,後面那輪不再擋。spec 沒寫兩道怎麼分這 28 秒,也沒寫要不要調 `HOOK_BUDGET`。

4. 規則訊息被截到 120 字,「標準寫法」那一半會被切掉
severity: major
blocking: 是
- spec 段落:範圍 5、範圍 2。
引句:「每條規則訊息(訊息裡已有標準寫法與型錄編號)」
- 查證:file: `scripts/lumos:38434` 與 `scripts/lumos:38446`,告警解析把 `message` 截成 `[:120]`。
- 查證:草稿規則包 208 條,其中 41 條訊息超過 120 字,最長 180。「改用…」都放在句尾,例如 `kt-vm-navcontroller` 的 `onXxx: () -> Unit 往上傳`,被截掉的正是修法。
- 重現:把這些規則經 `lumos lint-new --worktree` 或回合結束鉤子印出來,AI 只看到「錯在哪」。spec 的主訴求「寫了但完全沒參考」就是這一點,spec 沒提到截斷。S2 也沒驗訊息長度。

5. hint 級規則不接預設宣告,但型錄仍把它們算成「告警帶寫法」已接電
severity: major
blocking: 是
- spec 段落:範圍 3、用詞〈接電方式〉。
引句:「hint 級規則另放一個 `sgconfig-hints.yml`、範本預設不接」
引句:「每列都要接,沒接電的列不收」
- 查證:型錄形狀類 367 列中,實測狀態欄只靠 hint 規則的有 30 列,其中至少 23 列的接電方式只有「告警帶寫法」,不在〈情境決策表〉的對應檢查裡,也沒有行為測試。例子是 `API-18`(`kt-okhttp-body-string-twice(hint)`)和 `FLOW-10`(`kt-catch-then-collect-lambda(hint)`),在 `skills/kotlin-idioms/checks-catalog.md:165` 與 `:198`。
- 重現:照範本宣告後,這 23 列的規則一條都不會響,也沒有當下推列。S3 只查接電方式欄位字串,所以照樣通過。spec 沒把「只靠 hint」的列另標、不收或補第二種接電。

6. 已提交改動的機械檢查沒有可執行的指令,且 `--worktree` 在凍結後是空檢查
severity: major
blocking: 是
- spec 段落:範圍 8。
引句:「改動已提交就對 merge-base 到 HEAD 跑新增告警閘」
- 問題:範圍 4 只新增了 `lumos lint-new --worktree`,沒有任何指令能對提交範圍單獨跑新增告警閘。
- 查證:file: `scripts/lumos:39031` `_lint_new_verdict` 只被 file: `scripts/lumos:67822` 的 `code-loop check` 流程呼叫,沒有 `lint-new` 子指令。
- 查證:手冊 `skills/lumos-code-loop/SKILL.md:18` 的步驟 1 要求「凍結前先把手上的改動提交」。
- 重現:提交之後工作樹是乾淨的,`lint-new --worktree` 比 HEAD 沒有差異,永遠 rc0。手冊要照做的另一半沒有指令可敲。
- 同段還有一個缺口:`code-loop pass` 沒有範圍參數(file: `scripts/lumos:68542` 起)。範圍 7 寫「對同一版本跑」,沒說 diff 範圍怎麼算,pre-push 的範圍是遠端比對來的。

7. 改檔前推列:決策表沒有列編號,且命中邏輯沒定義
severity: major
blocking: 是
- spec 段落:範圍 6。
引句:「改借既有的「同會談只講一次」標記函式,以列編號為鍵」
- 查證:型錄〈情境決策表〉欄位是「情境|標準寫法|不適用時|觸發字|對應檢查」,21 列都沒有編號欄。file: `scripts/hooks/claude/impact-hook.py:825-838` 的 `_voice_once` 以 `code` 直接組檔名 `voice-{code}`。
- 查證:spec 沒寫觸發字比對方式(大小寫、是否整詞、任一或全部)、也沒寫「最多三列」超過時取哪三列。
- 查證:file: `scripts/hooks/claude/impact-hook.py:870-889`,既有輸出為空(非圖譜專案 `lumos impact` 回 rc3、零命中、`lumos` 找不到)時 `chunks` 為空就 `return 0`。spec 寫「在既有輸出後面加」,沒說輸出為空時是否獨立輸出。
- 重現:沒有 `docs/*-knowledge` 的 Android 消費專案,改 kt 檔不會得到任何決策列,S7 只驗有輸出的單純情況。

8. S3 與型錄對語意類的規定打架,有 3 列會讓測試紅
severity: major
blocking: 是
- spec 段落:驗收條款 S3、用詞〈接電方式〉。
引句:「語意類 應 含「表態對程式」與「盲判席」」
- 查證:`skills/kotlin-idioms/checks-catalog.md:477`(ARCH-54)、`:557`(DATA-62),以及 DATA-68,都是語意類(人裁),接電方式只有「表態對程式」。型錄口徑第 11 行明文允許這個例外,S3 沒寫。
- 重現:照 S3 字面寫測試,這三列直接紅。實作者只能改測試或改型錄,spec 沒指定哪一邊。

9. 規則包樣本與 S1 的條款對不上,且 ast-grep 未裝時 S1 與 S4 靜默通過
severity: major
blocking: 是
- spec 段落:範圍 2、S1、S4。
引句:「沒裝 ast-grep 時測試印略過」
- 查證:我用草稿規則包與 `ast-grep 0.51.1` 掃 `src/*/bad` 與 `src/*/good`。
- 查證:`kt-sequential-independent-await`(API-1,SKILL.md 稱「頭號條款」)沒有任何壞例命中。對 spec 自己的標準例 `val a = api.a(); val b = api.b()`(在 suspend fun 裡)實跑也零輸出。
- 查證:另有 13 條規則壞例只命中 1 次,範圍 2 要求至少兩個壞例。
- 查證:好例資料夾裡有 2 處命中 `kt-value-assign-background`(`src/architecture/good/kt-value-assign-background.kt:8` 與 `src/coroutines/good/kt-bg-dispatcher-touches-view.kt:17`),S1 要求好例零命中。
- 查證:本機 `which ast-grep` 找不到。`intake` 也確認本機未裝。
- 重現:在本機或沒裝 ast-grep 的 CI 跑 `t_kotlin_rulepack_samples` 與 `t_lint_new_astgrep_kotlin_two_files`,都印「略過」並 rc0,[test:] 綁定照樣算過。spec 沒寫 CI 要裝 ast-grep,也沒寫略過要留帳。

10. S2 只驗訊息開頭的編號,「錯在哪;改用…」沒有機械驗
severity: minor
blocking: 否(草稿可修,但 S2 抓不到)
- spec 段落:範圍 2、S2。
引句:「後面一句「錯在哪;改用 <標準寫法>」」
- 查證:草稿 208 條規則中 17 條訊息沒有分號,例如 `kt-statein-in-function`(STATE-3,只寫現象,沒有修法)與 `kt-okhttp-no-calltimeout`(API-5)。126 條完全沒有「改用/改成/改寫」字樣,其中仍有修法的不算,但 STATE-3 與 API-5 這類是真的缺。
- 重現:對這兩條規則的壞例觸發告警,訊息裡沒有標準寫法,S2 仍通過。

11. 決策表觸發字太泛,一般 ViewModel 就會觸發多列
severity: minor
blocking: 否
- spec 段落:範圍 6。
- 查證:我用一段只含 `users.map { }` 加 `viewModelScope.launch { try { } catch {} }` 的 ViewModel 比對,21 列中 7 列命中(多筆同型、只要最新一次、失敗連坐、失敗各自承擔、跨畫面共享、離開畫面後做完、對外 API)。
- 泛字例:`map`、`forEach`、`try`、`catch`、`launch`、`first`、`take`、`flow`、`remember`、`delay`、`suspend`。`suspend` 同時出現在 4 列。
- 重現:第一次改任何含 `suspend fun` 的 repository 檔,就推三列。靠「同列同會談一次」才不吵,但 spec 沒要求觸發字要成對或有最低長度。

12. 手冊對表態時機的說法與 spec 範圍 8 打架
severity: minor
blocking: 否
- spec 段落:範圍 8、範圍 7。
引句:「表態照既有手冊在推送前作答,本案不改」
- 查證:`skills/lumos-code-loop/SKILL.md:21` 寫的是「先表態(派審查員之前做;`skip` 也要先表態)」。
- 影響:範圍 7 讓 `pass` 檢查表態,與手冊「派審查員之前」一致,但 spec 說「推送前作答」讓接手者以為可以 `pass` 之後再答,`pass` 會擋。
- 另一處:spec 說「手冊第一步改成…」,手冊第一步是凍結材料,不是 `code-loop check`,「改成」找不到原文。

13. 型錄統計與規則包現況對不上,且型錄指向不在 repo 的路徑
severity: minor
blocking: 否
- spec 段落:用詞〈型錄〉、驗收條款 S2。
- 查證:`skills/kotlin-idioms/checks-catalog.md:845` 寫「規則包條數:211(error 35、warning 136、hint 40)」。草稿實數是 208(error 35、warning 132、hint 41)。
- 查證:型錄來源縮寫與實測狀態欄仍指向 `scratchpad/cov/all/rules/` 與 `sg/rules/extras.yml`,三個月後這些路徑不在 repo 裡。規則包搬進 `configs/ast-grep/kotlin-android/` 後,這些欄位沒有機械驗。

14. 「沒裝 ast-grep」的提示沒有對應的偵測機制
severity: minor
blocking: 否
- spec 段落:實務隱患〈工具沒裝〉。
引句:「回合結束檢查同樣放行並印一行「沒裝 ast-grep,寫法檢查沒跑」」
- 查證:file: `scripts/lumos:39136-39144`,工具沒裝時 `_lint_run_and_parse` 回 `([], False)`,verdict 只記「這條命令跑不出可解析的結果(工具沒裝/逾時/拉不到規則)」,分不出是哪一種。
- 重現:逾時與工具沒裝會印同一句,spec 沒寫要另外用 `shutil.which` 判斷第一個詞。

---

**風險類逐類**
- 並行與競態:有碰。擋停標記檔與改檔前標記檔是新增檔名,各自用 O_EXCL(file: `scripts/hooks/claude/check-graph-sync.py:910`、`scripts/hooks/claude/impact-hook.py:825`),無新競態;但 finding 3 的 SIGKILL 時序是真問題。
- 效能:有碰,見 finding 1 與 3。每輪都跑工作樹檢查,`lintbase-*` 暫存放在消費專案 `.lumos/` 底下,殘骸 24 小時才清(file: `scripts/lumos:38509`)。
- 暫存清理:有碰。被 SIGKILL 時會留 `.lumos/lintbase-*`,需要確認消費專案的 `.gitignore` 涵蓋它。spec 沒提,屬 minor,未單獨列。
- 資安:有碰,放行。回合結束鉤子現在會自動執行 `.lumos/lint.json` 裡的 shell 命令(`shell=True`,file: `scripts/lumos:38388`)。原本只在 pre-push 與手動 `lint-check` 跑。依單人、AI 依序操作的威脅模型,不攔。
- 相容性:有碰,但規則包只用 `ast-grep 0.51.1` 驗過。spec 沒寫最低版本,消費專案裝舊版時規則語法可能解析失敗,判成環境不可用而放行。minor,未單獨列。
- 金流、對外送出、不可逆:無。spec 已排除,我也沒看到:本案只讀程式碼、不送出任何東西,新增檔與擴充函式可整批退回。

最嚴重 severity: blocker,blocking 共 9 條(finding 1~9)。
