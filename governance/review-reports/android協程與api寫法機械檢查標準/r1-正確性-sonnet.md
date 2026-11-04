severity: blocker

我在 `lumos` 和兩支鉤子上逐條核對過。沒裝 ast-grep,所以 SARIF 空輸出與衝突標記的實際反應沒跑過,標 ⚠。

## 逐節結果

- 用詞、分批、不做、裁決紀錄、批三條件、舊版初稿、回退、天花板:已讀,無 finding。
- 範圍 1、2、3:已讀,無 finding。
- 範圍 4、5、6、7、8、實務隱患、驗收條款:有 finding,見下。

## Findings

**1. 回合結束檢查在預設設定下一條命令都不會跑**
severity: blocker
blocking: 是——功能預設完全不作用,放過該擋的。
- spec 段落:範圍 5。
- 引句:「預算預設 20 秒,可用 `.lumos/config.json` 的 `lint_new` 區塊新加的 `stop_budget_sec` 調」
- 問題:既有判定每條命令跑之前會檢查「剩餘預算 < 單條保底」。保底預設 30 秒,預算只給 20 秒。
- 重現:專案宣告 ast-grep 規則包,工作樹新增一處 `body()!!`,用預設預算跑工作樹檢查。第一條命令的剩餘預算是 20 秒,小於 30,被記成「預算不足沒跑到」。
- 後果:範圍 4 又規定這類命令不算擋,所以不會有任何告警。S6 測試把預算調大就會綠,預設值卻是空轉。
- file: `scripts/lumos:38498`(`per_cmd_floor_sec` 預設 30)與 `scripts/lumos:39100-39106`(`left < cfg["per_cmd_floor_sec"]` 就記 budget 並 continue)。

**2. 回合結束鉤子現有的提早離開,會讓新增的那一道常常根本沒機會跑**
severity: major
blocking: 是——放過該擋的。
- spec 段落:範圍 5。
- 引句:「收工點名那支回合結束鉤子多一道:專案有 `.lumos/lint.json`、工作樹上有未提交的程式碼檔時,跑工作樹檢查」
- 問題:spec 只說「多一道」,沒說插在哪。現有 `main()` 在抵達擋停分支之前有四個提早 `return 0`:
  - 找不到圖譜根目錄,即沒有 `docs/*-knowledge` 的專案。
  - 這一輪逐字稿沒有任何檔案動作或 Bash 指令。
  - `graph_touched` 為真,即這輪有動筆記。
  - 同一批檔案「第二次就不再講」的重複判斷。
- 重現:Android 專案這一輪既寫了 kt 又寫了筆記(鐵則 1 要求的正常流程),`graph_touched` 為真,直接 `return 0`,lint 檢查不會被呼叫。
- 後果:沒有圖譜的消費專案永遠沒有這道。
- file: `scripts/hooks/claude/check-graph-sync.py:998-1043`,另見 `1048-1057`(`graph_touched`)與 `1070-1075`(重複判斷)。
- 補充:`code_entries` 是否算 `.kt` 取決於副檔名清單。`.kt` 在清單內,`scripts/hooks/claude/check-graph-sync.py:45`。

**3. 工作樹終點遇到單純 `mv` 的改名,舊告警全變成新增**
severity: major
blocking: 是——擋了不該擋的。
- spec 段落:範圍 4。
- 引句:「基準取 HEAD、現在版讀工作樹的檔(含未追蹤但沒被忽略的檔),其餘(設定檔取現在版、告警身分、放行紀錄)照舊」
- 問題:改名要靠 `git diff --find-renames` 配對。工作樹對 HEAD 的比較只看追蹤中的檔,看不到未追蹤檔。
- 重現:`mv Foo.kt Bar.kt`(未 `git add`),`Foo.kt` 內有 HEAD 已有的三處 `!!` 告警。
  - `Foo.kt` 被記成 D,整支跳過。
  - `Bar.kt` 是未追蹤檔,算 `(Bar.kt, None)`,基準側沒有內容。
  - 告警身分含檔名,三處舊告警全變成「新增」。
- 後果:推送前走提交範圍時改名配得上,同一份改動結果不同。
- file: `scripts/lumos:38720-38743`(D 直接跳過、A 是 `(path, None)`),`scripts/lumos:38859-38875`(身分含檔名 `f`)。

**4. 代碼審 `pass` 沒有版本範圍,跟推送前「同一支判定」對不起來**
severity: major
blocking: 是——兩道判定互相打架。
- spec 段落:範圍 7。
- 引句:「對同一版本跑新增告警與表態兩道判定(就是推送檢查裡那兩道的同一支判定函式)」
- 問題:這兩道判定都要 `diff_range`。推送前給的是「遠端既有 sha..被推 sha」,`cmd_code_loop` 的 `pass` 分支只有 HEAD sha,沒有範圍參數。spec 沒寫範圍怎麼取。
- 重現:分支第一個提交曾用 `LUMOS_SKIP_LINT_NEW=1` 推上遠端,帶一處新告警;第二個提交乾淨。
  - 若 `pass` 取 merge-base 到 HEAD,會把第一個提交的告警算進去,`pass` rc1。
  - 推送前範圍只含第二個提交,同一批改動可以放行。
- 後果:這與實務隱患那句「不新增擋的條件」矛盾。
- file: `scripts/lumos:68594-68603`(`pass` 與 `skip` 共用一段,沒有範圍),`scripts/lumos:67818-67824`(`_codeloop_lint_new_step` 必須傳 `diff_range`)。

**5. 範圍 8 叫人對已提交範圍跑新增告警閘,但沒有對應的指令**
severity: minor
blocking: 否——文件指令缺口,不影響判定正確性。
- spec 段落:範圍 8。
- 引句:「改動已提交就對 merge-base 到 HEAD 跑新增告警閘」
- 問題:現有 CLI 沒有 `lint-new` 子指令,只有 `lint-check`、`lint-waive`、`lint-watch`。spec 新增的 `lumos lint-new` 只定義了 `--worktree` 與 `--budget`。同一段又禁用 `code-loop check`。
- 重現:一個已全部提交的分支,手冊第一步沒有任何指令可以跑「提交範圍」的新增告警。
- file: `scripts/lumos:70485`、`70490`、`70555`(只有這三個 `lint-*` parser)。

**6. 預算沒跑到的命令改成「不算擋」之後,可能印出「沒有新增的告警」**
severity: major
blocking: 是——放過該擋的。
- spec 段落:範圍 4。
- 引句:「時間預算不夠而沒跑到的命令,工作樹檢查只列出來、不算擋」
- 問題:`_lint_new_classify` 目前只有 `ran` 為空且有 `report_only` 時才回 `not-checked`。這是原作者專門為「一條都沒跑不准說乾淨」寫的守則。
- 重現:所有命令都因預算被略過。`new` 為空、`hard_undone` 因 spec 規則排除、`ran` 為空、`report_only` 也為空,落到 `status="clean"`,reason「沒有新增的告警」。
- 後果:`lumos lint-new --worktree` 對 rc0 印「沒有新增的告警」,實際什麼都沒查。
- file: `scripts/lumos:39004-39028`。

**7. 「同一批」用身分集合雜湊,重複相同告警多加幾條也算同一批**
severity: minor
blocking: 否——已被擋過一次的同質告警,推送前閘仍會擋。
- spec 段落:用詞〈告警身分(指紋)〉。
- 引句:「這次工作樹檢查新增告警的身分集合,排序後取雜湊」
- 問題:既有比對用 Counter 算次數,同一指紋基準 0 次、現在 3 次是新增 3 條。
- 重現:批次 A 是一處 `x!!`,被擋後 AI 在同檔又複製兩處完全相同的 `x!!`。指紋相同,集合相同,雜湊相同,視為同一批,不再擋。
- 補充:spec 另一處說「修掉一條」也算新批。同一個機制下,「修一條就再擋一次」與「同一批只擋一次」的保證強度不一致,也沒說標記檔何時清。
- file: `scripts/lumos:38884-38955`(Counter 計次)。

**8. 回合結束鉤子總預算 40 秒,新增 20 秒沒掛進既有的內層預算計算**
severity: minor
blocking: 否——最壞情況是鉤子被截斷,漏一次提醒。
- spec 段落:範圍 5。
- 引句:同 finding 1。
- 問題:該鉤子的外層預算是 40 秒,內層公式是外層乘 0.7,即 28 秒,而且要扣掉「已耗時間」。spec 的 20 秒固定值沒說要不要走 `_inner_budget`。
- 風險:先花了較久的圖譜檢查(例如大專案的 `find_notes_mentioning`),再接 20 秒 lint,有機會超出 40 秒被平台殺掉。
- 殘留問題:`stop_block_decision` 先用 `O_EXCL` 佔了圖譜那道名額,輸出前被殺掉,名額就白用掉,下一輪不會再擋。⚠ 沒量測最壞耗時。
- file: `scripts/merge-claude-settings.py:121`(`check-graph-sync.py` 預算 40),`scripts/hooks/claude/check-graph-sync.py:712-738`(`_inner_budget`),`scripts/hooks/claude/check-graph-sync.py:889-899` 與 `910-925`(名額先佔)。

**9. 工作樹檢查掃整個工作樹,而且原因訊息裡沒有位置**
severity: minor
blocking: 否——共用工作樹才會出事,而且不改判定結果,只是難修。
- spec 段落:範圍 5。
- 引句:「(訊息裡已有標準寫法與型錄編號)」
- 問題:工作樹檢查是「HEAD 對工作樹」,同一工作目錄別的會談的未提交 kt 改動也算進來。
- 重現:別的會談留下含告警的 kt,這個會談收工會被擋,但原因只有「規則訊息」,沒有檔名、行號或放行用的指紋。
- 後果:AI 無從得知哪支檔要改。`lint-waive` 要指紋才能放行,spec 說逃生門是放行,卻沒說原因要帶指紋。
- file: `scripts/hooks/claude/check-graph-sync.py:934-972`(`stop_block_reason` 目前只列檔,沒有 lint 資訊)。

**10. 改檔前推列的觸發字比對沒定義粒度,也沒定義挑哪三列**
severity: minor
blocking: 否——只是多推或少推脈絡,沒有擋人。
- spec 段落:範圍 6。
- 引句:「含〈情境決策表〉某列的觸發字時,在既有輸出後面加最多三列」
- 問題:既有 `extract_delta_text` 把 Edit 的 `old_string` 與 `new_string` 接在一起、不去註解也不去字串。
  - 型錄觸發字大量是常用詞:`map`、`try`、`catch`、`remember`、`launch`、`collect`、`combine`、`enabled`、`async`、`await`、`suspend`。
  - 觸發字用子字串還是整詞沒寫。如果是子字串,`country` 含 `try`、`AsyncImage` 含 `async`、`awaitAll` 含 `await`、`Mapper` 含 `map` 都會中。
  - 刪掉壞寫法的編輯(例如 `old_string` 有 `GlobalScope.launch`)也會推「別用 GlobalScope」那一列。
- 重現:Edit 的 `new_string` 只有註解 `// try again later`,只要 `try` 是觸發字就會命中某列。
- 三列的選法沒寫。型錄表序前幾列的觸發字是 `async`、`await`、`suspend`、`map`,幾乎每次都命中,實際上永遠先佔前三名。
- 「只推一次」若是先對每個命中列呼叫 `_voice_once` 再取前三,第 4 列以後會被標成已講過但從沒顯示,之後永遠不推。⚠ 實作順序 spec 未寫。
- file: `scripts/hooks/claude/impact-hook.py:417-436`(`extract_delta_text`),`scripts/hooks/claude/impact-hook.py:825-838`(`_voice_once`,碰到就建檔)。
- 另一個限制:`main` 在 `lumos` 找不到或沒有圖譜專案時提早回。型錄 `.kts` 在 `CODE_EXTS`,spec 卻只寫 `.kt`,兩邊不一致。

**11. 工作樹終點遇到合併衝突中的檔,spec 沒寫處理**
severity: minor
blocking: 否——⚠ 未能實測,只指出 spec 沒覆蓋。
- spec 段落:範圍 4。
- 引句:同 finding 3。
- 問題:衝突中的檔 `git diff --name-status HEAD` 的狀態碼是 U,現有程式落在 `else` 分支,當成 M 處理。現在版讀工作樹,內容含 `<<<<<<<`、`>>>>>>>` 標記。
- 不確定處:tree-sitter 遇到這些標記時,是報出假告警、整檔無結果,還是整條命令判失敗,取決於 ast-grep 行為,我沒裝沒法判斷。
- 後果:不管哪種,「被判成新增告警」或「靜默漏掉」都沒有在 spec 裡被指定。
- file: `scripts/lumos:38727-38742`(`M/T` 等一律 `(path, path)`)。

**12. 測試檔被新增告警閘整批排除,型錄 TEST 表的告警規則走不到**
severity: major
blocking: 是——放過該擋的,且與 spec 的覆蓋宣稱衝突。
- spec 段落:用詞〈接電方式〉。
- 引句:「形狀類至少有 1 或 4;語意類必有 3 與 5。」
- 問題:`_lint_new_verdict` 用 `_stack_changed_ok` 過濾,而它排除 `_PITFALL_DIFF_TEST_PAT`,涵蓋 `src/test/…` 與 `*_test.*` 之類路徑。
- 重現:`app/src/test/java/…/FooViewModelTest.kt` 含 `runTest { delay(1000) }` 這類型錄 TEST 表的壞寫法。它被判為「沒有要掃的程式碼檔」或被排除,規則包完全沒機會對它報。
- 後果:`src/androidTest` 路徑倒是不被這個正規式擋掉。
- 不影響:TEST 表若全靠「行為測試或正向約束」接電則不受影響,但 spec 對形狀類允許選 1 或 4,沒有保證落在 4。
- file: `scripts/lumos:58374-58397`(`_stack_changed_ok`),`scripts/lumos:37574`(`_PITFALL_DIFF_TEST_PAT`)。

## 對固定席節點的判斷

附在尾端的三個固定席:`Systems/linter精選目錄`、`Systems/效能檢核目錄`、`Systems/棧別提問表態閘`。

- 計劃連結的三篇節點:這份設計沒有修改這些節點宣稱的合約。它們都是「掛 0 條合約」,spec 只是在它們之上新增規則包與宣告範本,所以不破壞既有合約。
- 設計審派的計劃牽連清單裡沒有合約節點。對 `Systems/graph-sync-coverage` 與 `Systems/改檔前推播`,判「不影響」只限它們宣稱的行為。finding 2 和 10 是新增功能與既有鉤子結構的衝突,不是破壞它們原本的宣稱。

## 實務隱患風險類

- 金流:無。只讀程式碼,spec 已排除。
- 對外送出:無。檢查只在本機跑,spec 已排除。
- 不可逆:無。型錄與規則包是新檔,放行檔與治理帳只追加。回退段落成立。
- 併發與共用工作目錄:有,見 finding 9。工作樹檢查看到別的會談的未提交檔,spec 沒界定範圍。
- 時間與預算:有,見 finding 1、6、8。預設預算與保底互相矛盾,預算不足的命令在不擋之外沒有保證回報「未檢查」。
- 擋停迴圈與重複:有,見 finding 7。批次雜湊集合化讓重複告警漏擋,同一機制也讓「修一條就再擋一次」。
- 工具缺失與設定檔路徑:無新增。沒裝 ast-grep 與規則包路徑不存在都判環境不可用並放行,spec 的回退段落寫對了。
- 資安:無新增。spec 的檢查不碰登入、權限、付款、個資、上傳、對外呼叫,不產生新的外來輸入處理面。

最嚴重:blocker,共 1 條 blocker、5 條 major、6 條 minor;blocking: 是共 6 條(finding 1、2、3、4、6、12)。
