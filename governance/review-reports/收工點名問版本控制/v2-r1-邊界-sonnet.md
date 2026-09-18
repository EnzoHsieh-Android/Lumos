severity: blocker

# 邊界與極端輸入審查(第二版):收工點名問版本控制_計劃

審查範圍:docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md(=被審材料 v2-r1-work.md)。對照程式碼:scripts/hooks/claude/check-graph-sync.py(現況仍是工具名列舉,S1–S6 尚未實作、t_sync_nudge_* 測試不存在)、scripts/lumos 裡既有的三處「問版本控制」實作。第一版的邊界審查(見 governance/review-reports/收工點名改量檔案樹/r1-邊界-sonnet.md)全部針對「自存快照」——那個機制整個被撤掉,舊 7 條找不到對應標的,不重複列;本輪找的是新機制(git 查詢)自帶、前一版沒有的邊界問題。

## 核心矛盾:PRIOR-ART 宣稱沿用的「第三種」查不到最常見的新檔案手法

severity: blocker
blocking: 是 — 已實測:`git diff HEAD --name-only` 在有 `newfile.py`(從未 git add 過的全新檔)的工作樹上,輸出完全不含 newfile.py;`git status --porcelain` 同一個工作樹會印出 `?? newfile.py`。PRIOR-ART 段點名「沿用第三種」,第三種明講就是「這支 hook 閘門 3 那條路看工作樹對上次提交」,而該路徑現行實作正是 `lumos impact --diff HEAD --sync-check`,底層就是 `git diff --name-only HEAD`。
引句:「本方案是沿用第三種,不新增第四種」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:600` — `_impact_missing` 呼叫 `lumos impact --diff HEAD --sync-check`;`/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/lumos:25234` 顯示其底層是 `git diff --name-only diff_range`(diff_range="HEAD")。若「問版本控制哪些檔還沒提交」真的照字面沿用這條既有查詢,S1 最常見的情境之一——這一輪用 `echo > new.py` 新建一支從未 add 過的程式碼檔——會繼續被漏報,這正是整份計劃要根除的病。若改用 `git status --porcelain`(能看到 `??`),那就不是「沿用第三種」而是換了一種底層查詢,PRIOR-ART 的立論基礎(不新增第四種做法)不成立,兩者必須擇一並在計劃裡講清楚。

## 全新未追蹤子目錄會被折成一行,不會展開成逐檔

severity: blocker
blocking: 是 — 已實測:未加 `-uall` 時,新增一個未追蹤子目錄(內含兩支 .py)之後,`git status --porcelain` 只印 `?? newdir/` 一行,不會展開成 `newdir/a.py`、`newdir/b.py`;加 `-uall` 之後才會各自列出。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/lumos:28663-28664` — 同一支工具的另一處查詢已經為了同一個坑寫死加 `-uall`,註解明講「不帶 pathspec 時未追蹤目錄會折成一條 `?? dir/`,裡面的檔就對不上」。這份計劃全文沒有提到 `-uall` 或這個坑,若實作時比照別處常見寫法(不加該旗標),一次新增一整個模組(常見手法,例如把一個功能拆成新資料夾)只會被算成「改了 1 支檔」,S1「不得少報」不成立,而且這個坑就寫在同一支工具裡三行之隔。

## Rename 的路徑格式沒有交代,可能把「old -> new」整串塞進清單

severity: major
blocking: 是 — `git status --porcelain`(非 `-z`)對 rename 印的是單行 `R  old.py -> new.py`,特殊字元路徑還會被 C-style 跳脫加引號。S1/S4 條款都沒提到「這一輪把一支程式碼檔重新命名」算不算改了、要顯示成幾支、格式怎麼切。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/lumos:15347-15349` — 同一支工具處理另一個「合併帳本」情境時已明講「porcelain 的 rename 是 `R  old\0new`,含特殊字元的路徑在非 -z 模式會被 C-style 跳脫並加引號,光 strip('"') 解不開」,並選擇「保守拒絕,狀態碼含 R/C 就不自動併」。若新機制的實作對 rename 沒有對應的分支,naive 逐行解析會把整串 `"old.py -> new.py"` 當成一個檔名塞進提醒訊息(`Path(...).suffix` 巧合仍會算出 `.py`,訊息會顯示一個不存在的離譜檔名)。

## 空倉庫(HEAD 未出生)會讓既有查詢直接報錯

severity: major
blocking: 是 — 已實測:在一個 `git init` 但還沒有任何 commit 的倉庫裡執行 `git diff HEAD --name-only`,直接報 `fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree`,非零 rc。這正是題目點名要問的邊界之一(空倉庫還沒有第一個提交),而它剛好命中上面第一條矛盾裡「沿用第三種」那個具體查詢的死角。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:589-609` — `_impact_missing` 對 rc≠0 已有 `return []` 的 fail-open,但那只覆蓋閘門 3 分岔裡的「筆記反查」那一段;S1–S6 全文沒有一條講到「新的『問版本控制』查詢本身在空倉庫上會失敗」時,閘門 2/3 的核心清單要怎麼降級(靜默當作沒有未提交檔?還是印警語?)。

## 專案不是 git repo:新機制把整個「改了哪些檔」綁死在 git 上,舊機制不需要

severity: major
blocking: 是 — 閘門 0(`find_graph_root`)只檢查 `docs/*-knowledge` 存在,不檢查有沒有 `.git`;舊機制(工具名列舉)完全不依賴版本控制,即使專案還沒 `git init` 也能運作(只是列不到 shell 手法)。這份計劃把清單來源整個換成「問版本控制」,若專案尚未 `git init`(例如剛照 SOP 建好圖譜,還沒建 repo)——查詢會直接失敗,而 S1–S6、〈實作時已知的坑〉都沒有交代這個前提是否成立、不成立時怎麼辦。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:80-91` — `find_graph_root` 的判準與 `.git` 完全無關,證明「圖譜存在」與「是 git repo」在這支 hook 的既有假設裡是兩件不相干的事,新方案卻把後者變成前者的隱性前提。

## 被 .gitignore 排除的程式碼檔:新機制天生看不到,舊機制看得到

severity: major
blocking: 是 — `git status --porcelain` 預設不列 `.gitignore` 命中的路徑;舊機制(工具名列舉)完全不看 gitignore,只要是被編輯工具或 rm/mv/cp 動過的路徑就算。若這一輪用 shell 改到一支被忽略但副檔名仍是程式碼(如本機覆寫設定、產生後又被 gitignore 排除的 .py/.ts)的檔案,新機制會安靜地看不到、完全不開口——這是這次改動本身新引入的一種少報型態,且 S1 列出的驗收手法(sed/heredoc/管線寫入/一行 python)測的是「用什麼工具改」,不是「檔案有沒有被忽略」,不會被〈驗收條件〉的 9 個情境之一測到。

## 併發/共用工作目錄:計劃只處理了語意污染,沒處理查詢本身可能失敗

severity: major
blocking: 是 — 〈新方案自帶的一個張力〉一節只講了「清單含別人的未提交檔」這種語意污染,並用改措辭(工作樹語意)解決;但沒有處理「三個 session 同時 Stop、同時各自對同一個工作樹跑 git 查詢」這件事本身可能撞鎖——`git status` 預設會嘗試刷新並寫回索引(取 `.git/index.lock`),多個行程同時跑存在既有的、廣為人知的「Unable to create '.git/index.lock': File exists」風險。
引句:「共用工作目錄下還可能含別人的」
file: 本 repo 目前沒有任何一處 `git status` 呼叫帶 `--no-optional-locks`(已用 `grep -n "no-optional-locks" scripts/lumos scripts/hooks/claude/*.py` 核對,零命中),代表這個風險目前對既有三處查詢也成立,但這份計劃是唯一一份被題目明確問到「三個都去問版本控制會怎樣」卻完全沒提查詢本身可能失敗這個機制層面問題的文件——它把問題窄化成「內容對不對」,漏了「查不查得到」。

## 合併衝突/變基中途:非常規狀態碼(UU/AA/DD)沒有條款覆蓋

severity: major
blocking: 是 — 合併衝突中的檔案在 `git status --porcelain` 是 `UU`/`AA`/`DD` 等狀態碼,不是常見的 ` M`/`??`/` D`。S1–S6 沒有一條講到這個狀態下清單該怎麼算;本 repo 對「不認得的狀態碼」既有的處理慣例是保守跳過。
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/lumos:15349` — 「★保守拒絕★(狀態碼含 R/C 就不自動併),寧可照原路擋下也不要判錯」是同一支工具對另一段程式碼(帳本合併)的既有心態;若新機制的實作沿用同一種保守心態,merge/rebase 中途、用 shell 改過的衝突檔會被跳過不算,回到 S1 要修的少報。

## 這輪對話紀錄檔讀不到或壞掉:等同「沒有動作」,靜默不開口

severity: major
blocking: 是 — 新方案的「要不要開口」(閘門 1)仍完全依賴讀 transcript(表格第一列維持讀對話紀錄,只是放寬判準);transcript 不存在或 JSON 壞掉時 `collect_turn_actions`/`collect_codex_turn_actions` 回 `([], [])`,行為與 S6「這輪真的沒有動作」完全無法區分。
引句:「當這一輪完全沒有跑過任何可能寫檔的動作…收工點名應閉嘴,即使工作樹上有未提交的程式碼檔」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:201-202` — `if not transcript_path.is_file(): return [], []`,以及第 217 行 JSON 解析失敗直接 `continue` 略過壞行。若這一輪其實用 shell 做了大量寫入、但 transcript 剛好寫壞(斷電/行程被砍/磁碟滿),使用者完全不會被提醒——工作樹上明明有未提交的程式碼檔,這正是整份計劃要根除的「少報但看起來正常」,只是換了一個 S1–S6 都沒點名的觸發路徑。

## S5 驗收條件與〈回退〉節對「三類部署位置」的落差

severity: major
blocking: 是 — 〈回退〉節點名三類部署位置要「各自處理」:repo 原始檔還原、家目錄複本要重跑安裝指令、每個接入專案要各自跑更新指令;但〈驗收條件〉#6 只寫「改完跑一次安裝指令,對三類部署位置各比一次 sha256」,沒有講第三類(每個接入專案的複本)要去哪裡跑「更新指令」才會產生可比對的東西——而這份計劃、這個 repo 都沒有真實消費專案可以拿來跑。
引句:「退回原方式…每個接入專案裡各自的複本(每個專案各跑一次更新指令)」對照「改完跑一次安裝指令,對三類部署位置各比一次 sha256(對應 S5)」
file: `/Users/enzo/.claude/jobs/9d19b273/tmp/stopfix/scripts/hooks/claude/check-graph-sync.py:180-182`(計劃第 176-180 行,回退節列出三個獨立步驟)。S5 若照〈驗收條件〉#6 字面執行,第三類部署位置實際上不會被驗到,S5 有可能在零真消費專案的情況下被判過。

## S1–S6 逐條檢查

severity: clean
blocking: 否 — S2(閘門 3 判準改問版本控制)、S3(措辭改口)、S6(唯讀輪靜默)在單純「有沒有查詢到已知檔案」的意義下判準清楚,沒有新增獨有的邊界問題(它們共用的底層查詢邊界已在上面各條列出,不在此重複記)。S4(刪除算不算改了)在 git status 裡刪除永遠是逐檔獨立一行(已實測 `rm` 後 `git status --porcelain` 印出獨立的 ` D tracked.py`,不會像未追蹤目錄那樣被折疊),機制上可達成。

## 檔案清單的其他極端(零個 / 兩百個 / 剛好卡在門檻)

severity: clean
blocking: 否 — 已讀,查無新 finding。既有的顯示上限邏輯(前 10 筆列名、其餘「另 N 個」、整段訊息 1500 字截斷,見 check-graph-sync.py:764-772)不是這次「問版本控制」新增的風險,量級變化只會讓清單變長,不會讓清單算錯。撤除條件裡「清單長度中位數超過 10 支檔」的門檻本身沒有講「中位數」是取多少次觀測的中位數,判準模糊但不影響機制對錯,只計入前面關於這節的一般觀察,不獨立開一條。

## PRIOR-ART / 撤除條件(RETIRE-IF)其餘部分

severity: clean
blocking: 否 — 已讀。撤除條件第一條(情境產生器全綠就撤)本身邏輯自洽,沒有新的邊界輸入問題;第二條「terminal 清單長度中位數」的模糊性已併入上一節,不重複列。

---

總結:整份最高等級 blocker(2 條:PRIOR-ART 宣稱沿用的既有查詢對全新未追蹤檔案結構性看不到,以及未加 `-uall` 時全新未追蹤子目錄會被折成一行);blocking:是 共 10 條(核心矛盾看不到新檔案、未追蹤子目錄折疊、rename 格式未交代、空倉庫查詢報錯、非 git repo 的前提未交代、gitignore 排除的程式碼檔看不到、併發查詢本身可能失敗、合併衝突非常規狀態碼未覆蓋、transcript 讀不到等同無動作、S5 驗收與回退節對第三類部署位置的落差),blocking:否 共 3 條(S1–S6 其餘條款已讀無新 finding、檔案清單量級變化已讀無新 finding、PRIOR-ART/RETIRE-IF 其餘部分已讀無新 finding)。
