severity: major

這份投稿有四個會讓實作者做出壞東西的洞(finding 1 到 4),另有八條小問題。主要風險在三處:依賴一個不存在的檢查、改檔前推列的介面沒定義、自動執行的設定來源不可信。

## 逐節結果

- 開頭、PRIOR-ART、RETIRE-IF:已讀,無 finding。
- 用詞:見 finding 4、6。
- 範圍 1、2:見 finding 5、9、10。
- 範圍 3:見 finding 6、7、11、12。
- 範圍 4:見 finding 1、2、3。
- 範圍 5、6:見 finding 8。
- 不做、開審前的改寫:已讀,無 finding。
- 實務隱患:見 finding 4(資安那條)。
- 驗收條款、回退、天花板:已讀,無新 finding。

## 實務隱患逐類

- **併發**:同工作目錄兩個會談同時收工,各跑一次 lint-new,各自建 `.lumos/lintbase-*`,彼此不衝突。改檔前推列的並行重推,spec 已明講不防。無新增隱患。
- **效能**:每次 lumos 啟動約 0.75 秒(實測),加 `git status -uall`,在 10 秒上限內。熱路徑風險見 finding 6 的預算算式。
- **資源**:逾時殺程序群組後 `finally` 的 `rmtree` 跑不到,殘骸留在 `.lumos/lintbase-*`。spec 已寫「一天後清」,可接受。時間戳檔的目錄未定義,見 finding 7。
- **回滾**:回退節已寫。唯一缺口是鉤子上限 50 秒會留在已註冊的設定裡,見 finding 6。
- **資安**:見 finding 4。

## Findings

### 1.
severity: major
blocking: 是(實作者會照一個不存在的檢查,放出一份帶常用字觸發字的型錄)
- 段落:範圍 4 最後一條。
- 引句:
「型錄的觸發字由第一批的型錄格式檢查把關:不准收一般常用字」
- 問題:spec 說停用字表與檢查在母計劃 S3,但母計劃 S3 沒有這件事。S3 只要求「每列有列編號與觸發字」。凍結提交 0f9263c2 的母計劃全文搜「停用字」是 0 筆。
- 現況與 spec 自己的規則相反:型錄 D-3 的觸發字含 `map`、`forEach`,D-1 含 `suspend`,D-4 含 `cancel`、`collect`。`map` 正是 spec 點名要禁的字。
- 結果:停用字檢查沒人負責實作,改檔前推列會被 `map` 和 `suspend` 幾乎每次命中。
- 佐證:
  - file: `skills/kotlin-idioms/checks-catalog.md:670`(D-3 觸發字欄含 `map、forEach`)
  - file: `skills/kotlin-idioms/checks-catalog.md:671`(D-4 觸發字欄含 `cancel、collect`)
  - file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:105`(S3 條款沒有停用字)

### 2.
severity: major
blocking: 是(「排除已推過的列」由誰做、資料從哪來,spec 沒定義,實作者必須自己發明介面)
- 段落:範圍 4 第 1、2 條。
- 引句:
「payload 多一個鍵 `delta_new`:只放寫入的新內容」
- 引句:
「排除這個會談已經推過的列之後,照命中字數多寡、再照表序取前三列」
- 問題:spec 一方面說「比對在 lumos 本體做,鉤子只印」,一方面說 lumos 要排除這個會談已推過的列。但標記檔 `<會談>.rows` 在鉤子端的目錄,payload 又只新增 `delta_new`,沒有會談編號、也沒有已推列清單。
- 現況:改檔前鉤子送給 lumos 的 payload 只有 `query`、`prospective`、`delta_text`、`delta_truncated`,沒有會談編號。
- 兩條出路都有代價:
  - 如果由鉤子過濾,「取前三」會變成「先取三再過濾」,第四、五名的列永遠推不出來。這與驗收條款 S4「沒印出的列下次還能推」矛盾。
  - 如果由 lumos 過濾,它得知道鉤子的快取目錄與信任檢查規則。這兩樣都沒寫。
- 佐證:file: `scripts/hooks/claude/impact-hook.py:1027`(`stdin_payload` 只有四個鍵)

### 3.
severity: major
blocking: 是(沒有知識圖譜的 Android 專案收不到任何推列,而 spec 在範圍 3 明講要支援這種專案)
- 段落:範圍 4;對照範圍 3「所以沒有圖譜的專案……照樣跑」。
- 引句:
「放在回傳 JSON 的新鍵 `decision_rows`」
- 問題:`decision_rows` 掛在 `lumos impact --stdin-payload` 的回傳上。`cmd_impact` 開頭找不到圖譜(vault)就直接 `return _no_vault_msg()`,連決策表都不會讀。範圍 3 特意讓沒圖譜的專案也跑回合結束檢查,範圍 4 卻沒有對應處理。
- 鉤子端(`impact-hook.py`)在 lumos 不存在時也只對圖譜專案出聲。
- 範圍 4 沒寫要把決策表比對搬到 vault 檢查之前,也沒寫要換成獨立入口。
- 佐證:
  - file: `scripts/lumos:64405`(`vault is None` 時直接 return)
  - file: `scripts/hooks/claude/impact-hook.py:888`(`_has_graph` 才出聲)

### 4.
severity: major
blocking: 是(spec 的資安結論建立在一個不成立的信任假設上)
- 段落:用詞「快工具」「安全形狀」,以及資安那條。
- 引句:
「`.lumos/config.json` 的 `lint_new.worktree_tools`(新增,字串清單,預設 `["ast-grep", "sg"]`)列的執行檔名」
- 引句:
「只限 HEAD 裡被追蹤的宣告、快工具、安全形狀(範圍 2、3),跟同一支鉤子「被打開的資料夾不准指使我們執行指令」的先例對齊」
- 問題:快工具的白名單 `worktree_tools` 存放在被打開的專案自己的 `.lumos/config.json`。被追蹤進 HEAD 只代表它被提交過,不代表可信,惡意倉庫整包 clone 下來就是已提交的。
- 攻擊路徑:攻擊者在倉庫裡提交 `config.json`,寫 `worktree_tools:["bash"]`,再提交 `lint.json` 命令 `bash -c '…' > {LINT_SARIF_OUT}`。
- 為什麼擋不住:安全形狀只禁 `;|&`、反引號、`$(`、`<`、換行,沒禁引號與 `-c`。這條命令第一個詞是白名單內的 `bash`,過得了安全形狀,會在 Stop 時自動執行。
- 現有先例的做法是只用可信來源,不用被打開資料夾自己的碼。`check-graph-sync.py` 的 `_impact_missing` 明講改成只用可信來源。spec 的對齊宣稱因此不成立。
- spec 沒說第一個詞是比對整字串還是比對基底名稱,所以 `./bin/ast-grep` 這類倉庫自帶可執行檔是否放行也未定。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:307`(讀「只用可信來源」那段註解),`_trusted_lumos` 即其實作。

### 5.
severity: minor
blocking: 否(影響只在 `lint-new --worktree` 的輸出,不改實作的主要決定)
- 段落:範圍 2 倒數第三條;範圍 1 的退出碼分類。
- 引句:
「其他宣告命令(含依賴層 `lint-deps.json` 全部)列成「工作樹模式不跑」(不算沒檢查,推送前閘會跑)」
- 問題:既有 `_lint_new_classify` 的收尾是「沒有任何命令跑過且沒有只報不擋的命令」才判 `not-checked`。被工作樹模式略過的命令既不在 `ran` 也不在 `report_only`,所以全被略過時會落到最後一個分支,判成 `clean`、印「沒有新增的告警」。這正是該函式註解禁止的「一條都沒跑卻說乾淨」。
- spec 沒定義這種情況的狀態或退出碼。
- 佐證:file: `scripts/lumos:39823`(`_lint_new_classify` 的 `elif not out["ran"] and out["report_only"]` 與最後的 `else`)

### 6.
severity: minor
blocking: 否(內層預算少 3 秒,且只在註冊表尚未更新時才吃緊)
- 段落:範圍 3「時間」。
- 引句:
「加 10 秒的上限剛好抵掉這道用的時間。」
- 問題:上限從 40 加到 50,內層預算(上限 × 0.7)只多 7 秒,這道最壞用掉 10 秒,不是「剛好抵掉」。既有那道的內層預算從 28 秒降成 25 秒,而 HOOK_BUDGET 註解寫過它實測需要 25 秒,幾乎沒有餘裕。
- 過渡期風險:鉤子腳本是符號連結,更新立刻生效,但 `settings.json` 裡的 `--budget 40` 要重跑安裝才會變。這段期間內層預算只剩 28 − 10 = 18 秒,會回到 2026-09-07 那次「天花板提了等於沒提」的狀況。spec 沒寫過渡期怎麼辦。
- 佐證:
  - file: `scripts/merge-claude-settings.py:121`(`"check-graph-sync.py": 40`)
  - file: `scripts/merge-claude-settings.py:114`(註解:實測需要 25 秒、內層為外層 × 0.7)

### 7.
severity: minor
blocking: 否(實作者可以自行補完,只是兩處敘述互相矛盾)
- 段落:用詞「這一回合碰過的檔」;範圍 3 第 3 條。
- 引句:
「回合結束鉤子每次跑都在自己的標記目錄寫一個這個會談的時間戳檔(新增)」
- 引句:
「逐字稿只從尾端往前讀到這一回合的開頭,最多讀 20 MB」
- 問題一:「自己的標記目錄」沒指明是哪個。既有有 `stop-block`(只准擋過的會談留東西,spec 說該性質不變)與 `stop-printed` 兩個目錄。若落在 `stop-block`,會破壞該性質;若新建第三個目錄,spec 沒寫清理,每個會談都留一個檔,永不收掉。
- 問題二:用詞節說「不用逐字稿最後一則使用者輸入判回合開始」,改用修改時間加時間戳檔,逐字稿只在會談第一次收工時取「第一筆」的時間,那是讀頭不是讀尾。範圍 3 卻還要「從尾端往前讀到這一回合的開頭」,沒說這段讀取用來做什麼。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:804`(`_stop_block_dir` 註解:只有擋過的 session 才留東西)

### 8.
severity: minor
blocking: 否(退出碼與放行條件實作時可以對齊,但 spec 內部不一致)
- 段落:範圍 5、範圍 6。
- 引句:
「任一道擋下就不寫留痕、rc1,印擋下原因與修法。」
- 引句:
「rc0 才派;rc3 代表沒檢查到,不是乾淨」
- 問題一:既有 `pass` 被擋的路徑回 rc 2(`_codeloop_pass_gate` 失敗後 `return 2`),驗收條款 S5 沒寫退出碼,但範圍 5 寫 rc1,與既有慣例不一致。
- 問題二:手冊要求 `lint-new --diff` 在 rc0 才派席,rc3 不算乾淨。但共用函式只在「擋下」時擋 `pass`,`env-unavailable`(工具沒裝)與 `not-checked` 都放行,而且推送前閘把它們當自動放行。沒裝工具時 `pass` 照樣記通過,手冊的規矩只有人看得到,機器不擋。
- 佐證:file: `scripts/lumos:68936`(`_codeloop_pass_gate`);`scripts/lumos:71656`(`return 2`)。

### 9.
severity: minor
blocking: 否(只影響換行轉換設定不同的環境)
- 段落:範圍 2 最後一條;範圍 3 的條件。
- 引句:
「工作樹內容要跟 HEAD 那一版位元組相同才跑」
- 問題:倉庫支援原生 Windows。`core.autocrlf=true` 或 `.gitattributes` 設 `eol=crlf` 時,工作樹檔案的位元組與 blob 永遠不同。這個檢查會永遠判「有沒提交的修改」,整個回合結束檢查靜默關閉,沒有提示。
- spec 沒說比對時是否做換行正規化。

### 10.
severity: minor
blocking: 否(預設值在 Linux 開發機上會誤判,實作者可補)
- 段落:用詞「快工具」。
- 引句:
「預設 `["ast-grep", "sg"]`」
- 問題:`sg` 在多數 Linux 發行版是 shadow-utils 的 `sg`(以另一個群組身分執行命令)。第一個詞是 `sg` 時,在 Linux 開發機上執行的是系統工具,不是 ast-grep。預設值應該只放 `ast-grep`。
- ⚠ 此項依一般 Linux 知識判斷,本機是 macOS,沒有實機重現。

### 11.
severity: minor
blocking: 否(關閉開關的語意不一致)
- 段落:範圍 3 條件。
- 引句:
「`LUMOS_STOP_LINT_OFF`(新增)不是 1」
- 問題:既有開關 `LUMOS_STOP_BLOCK_OFF=1` 的語意是關掉收工擋停。設了它的使用者會預期不再被擋,但新增的寫法檢查只認新環境變數,設了舊開關仍會被擋。spec 沒說兩者關係。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:893`(`LUMOS_STOP_BLOCK_OFF` 判斷)

### 12.
severity: minor
blocking: 否(順序與合流流程可由實作者補齊,但沒寫會出現競態)
- 段落:範圍 3 最後兩條。
- 引句:
「兩道都要擋時兩段原因合成一則,名額各自記。」
- 問題:既有擋停流程是「名額先佔再擋,寫不出 stdout 就退回名額」。新增的 `<會談>.lint.json` 沒寫「先記再印」或「印完才記」。
- 合流的控制流程也沒寫:既有那道有多個提早返回(例如「同批檔已講過」),當它不擋、寫寫法檢查要擋時,誰負責輸出 JSON,spec 沒定義。
- 佐證:file: `scripts/hooks/claude/check-graph-sync.py:1060`(既有擋停流程的名額與輸出順序,寫法見 `stop_block_decision` 之後的 try 區塊)

最嚴重 severity: major,blocking 共 4 條(finding 1、2、3、4)。
