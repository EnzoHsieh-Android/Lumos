---
type: project
status: done
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/done
  - scope/platform
lands_in:
  - Systems/lumos-cli-lifecycle
related:
  - "[[Projects/交接2026-10-03_計劃]]"
  - "[[Systems/lumos-deinit]]"
summary: |-
  WHY:`lumos update` 加 `--dry-run`:用目前這份工具來源,先印這次會改哪些規範檔(CLAUDE.md、AGENTS.md 或 AGENTS.override.md 的紀律區塊)與工具檔,專案與工具來源一個檔都不動 [出處:Projects/交接2026-10-03_計劃 第 5 項,rtb 建議] [因:rtb 規定規範檔改動要使用者同意,現在 update 一跑就套用,只能事後看] [不選:每次 update 都停下來問(非互動環境與 CI 會卡住);只把套用後印的差異加長(還是事後)]
  WHY:預覽不拉工具來源,結尾教人帶 `--source` 與 `--no-pull` 套用同一份 [出處:設計審 r1 通才、邊界、整合三席] [因:拉了之後預覽仍跑拉之前載入的舊程式,套用卻跑新程式,兩邊會算出不同結果;而且拉來源會換掉整台機器共用的 lumos 與 skills,等於預覽一個專案就改了所有專案的工具] [不選:預覽時拉來源再算(上述兩個問題);預覽時只 fetch、從遠端版本讀檔(區塊算法本身也在新版程式裡,舊程式算不準)]
---
# update預覽規範檔變更_計劃

白話:`lumos update` 會把工具的新版裝進專案,順手改寫 CLAUDE.md 和 AGENTS 指示檔裡的紀律區塊。rtb 的規矩是規範檔要改得先問使用者,可是現在 update 一跑就改完了,只能事後補問。這次加一個只看不改的 `--dry-run`:用目前這份工具來源,先把「這次會改規範檔哪幾行、會換掉哪些工具檔、還會動到哪些地方」印出來;使用者看過、同意了,再照它印的指令套用同一份來源。

依據:[[Projects/交接2026-10-03_計劃]] 第 5 項(rtb 2026-10-04 建議)。

PRIOR-ART: 同專案的 `lumos deinit --dry-run`(只印會動到什麼、零改動,開頭一行「lumos deinit --dry-run(僅預演,不改動):」);外部是 terraform 的 plan/apply、`apt-get -s`——先算出計畫印給人看,確認後套用同一份。
RETIRE-IF: 紀律區塊不再由 update 寫進消費專案(例如改成使用者自己引用一份共用檔),規範檔的改動就不經過 update,這個旗標就沒有存在理由。

## 範圍

- 做:`lumos update --dry-run`,預覽三件事——每個紀律區塊目標檔(CLAUDE.md、AGENTS.md 或 AGENTS.override.md)會怎麼變、哪些工具檔會被換新或新增、其餘會做的動作(含專案外的)。
- 做:手冊、指令說明表、CLI help 與圖譜筆記跟著寫上這個旗標(〈做法〉8)。
- 不做:互動式「要套用嗎?」問答;只套用部分檔案的選擇;改變不帶 `--dry-run` 時的任何行為。
- 不做:`lumos init`(既有 vault 只從專案裡的範本重新注入、範本沒變就不會改)、`lumos init --force` 與 `lumos bootstrap`(第一次安裝或明說要重裝)的預覽。這三條也會寫規範檔,要先看的話,已有 vault 的專案用 `lumos update --dry-run` 就看得到同一份範本會怎麼改(〈天花板〉1)。

## 做法

1. **預覽不拉工具來源**:`--dry-run` 一律等同帶了 `--no-pull`,不跑 `git pull`,專案與工具來源都不動。預覽用的是目前這份來源,開頭印來源路徑與它目前的提交編號(`git rev-parse --short HEAD`,拿不到就寫「不是 git 來源」)。結尾印要套用就跑的指令,★明確帶上 `--source <預覽用的來源絕對路徑>` 與 `--no-pull`★——同一份來源、不再拉,套用跑的就是預覽時那份程式與範本。想預覽最新版就先自己更新工具來源(`git -C <來源> pull --ff-only`),再預覽一次;這句也印在結尾。`--dry-run` 跟 `--allow-stale` 一起給時,`--allow-stale` 沒有作用(不拉就沒有過期判斷),照常預覽。
2. **紀律區塊的新內容照套用時的算法算**:套用時是先把來源的工具檔複製進專案、再從專案裡的範本組區塊。預覽要算出一樣的結果,範本取法照抄這個順序:來源有 `scripts/templates/graph-discipline.md` 就用來源那份;來源沒有(套用時會跳過不複製)就用專案裡那份。把 `_reinject_claude_block` 拆成「算出新的整檔內容」與「寫回去」兩段:預覽只呼叫前一段;套用走同一段算法再寫回,兩邊不會算出不同結果。`_expected_claude_body(root, slug)` 的意思不變(doctor Check D 也用它),預覽另外給它來源的根目錄當參數即可,不改它本身。
3. **每個目標檔怎麼印**(開頭沿用既有預覽的格式:「lumos update --dry-run(僅預演,不改動):」,下面縮排兩格逐項):
   - 會更新:印區塊的完整差異(不截斷);只差 START 行的版本號時,標「只更新版本號」並印那一行的前後。
   - 會新建(檔不存在):印「會新建 <檔名>」加整段要寫入的內容。
   - 會接上(有檔沒有區塊):印接的位置(CLAUDE.md 接檔尾;AGENTS 檔插在第一個 # 標題行之後,沒有標題行就插檔首)加整段要寫入的內容。
   - 不變:印「不變」。
   - 標記壞掉:印「區塊標記壞掉,套用時不會自動改,請手動檢查」。
   - 讀不了(不是 UTF-8、是資料夾、沒權限):印原因,不崩潰。
   - 另外,只要會寫回且原檔有 BOM 或 CRLF/CR 換行,多印一句「套用時整檔會統一成 LF 換行、去掉 BOM(不只區塊)」——套用本來就這樣做,預覽要講出來。
4. **工具檔清單**:把套用時「逐檔比對、決定要不要複製」那段抽成一支共用函式,預覽與套用都呼叫它(同一份清單 `_VENDORED_TOOLKIT` 加 `_VENDORED_TREE_FILES`、同一種逐位元組比法),預覽只列出會換新與會新增的檔。只差換行的檔也會列(套用時一樣會整檔換掉)。
5. **其餘會做的動作**,逐項列名(不細算):專案裡——補設定骨架與 `governance/.gitignore`、補 `docs/.gitignore` 的本機帳兩行、寫 `.lumos/vendored.json` 工具指紋、設定 `git config core.hooksPath`;★專案外★——同步全域 hooks 到 `~/.claude/`(會影響這台機器上其他專案的 Claude Code hooks)。pre-commit 會被換新而且這次是 Python 3.14 升級的那一版時,照套用時的提示多印那一段。
6. **來源 repo 自身**:套用在來源 repo 只刷新紀律區塊;`--dry-run` 就只預覽紀律區塊(第 3 點),不印工具檔清單與其餘動作,結尾印「套用:`lumos update`」(這條路本來就不拉)。
7. **回傳碼**:預覽的回傳碼 = 同樣條件下真的套用會回的碼。消費專案:來源無效回 2,其餘回 0(標記壞掉只印警告,跟套用時一樣不擋);來源 repo 自身:任一目標是標記壞掉或沒有範本就回 2,跟套用時一樣。預覽遇到讀不了的目標檔一律回 2(套用時那種檔會讓程式崩潰,預覽要先講清楚)。
8. **同步文件**:CLI 的 update help 加 `--dry-run`(說明寫明「用目前的工具來源預覽,不拉、不改動」);`skills/lumos-project-notes/reference.md` 指令表、`skills/lumos-project-notes/commands/07-安裝維運.md`「工具組舊了」那列、`docs/command-reference.md` 與 `docs/指令參考.md` 的 update 列加這個旗標;[[Systems/lumos-cli-lifecycle]] 的 update 旗標清單補上 `--allow-stale` 與 `--dry-run`,並修掉「update/deinit 偵測 root==_lumos_src() 即 return 2」那句(程式現況:update 在來源 repo 只刷新紀律區塊、回 0)。

## 實務隱患

- **預覽跟套用對不上**:兩次之間有人更新了工具來源,或專案裡的檔被改了。來源那半靠結尾印的指令帶 `--source` 與 `--no-pull`;專案那半不擋,套用時照常印差異。
- **預覽不小心寫檔**:新增的唯一寫入點在「寫回去」那段,預覽路徑不呼叫它,也不呼叫補忽略規則、寫指紋、設定 hooks 路徑、同步全域 hooks;驗收條款 [S1] 用整棵目錄與家目錄的位元組比對守。
- 已排除:金流:本案只讀寫工具檔與規範檔,不碰任何付款或帳務
- 已排除:對外送出:預覽只印在終端、不連網(不拉來源)
- 已排除:不可逆:預覽路徑不寫任何檔;拆函式後真的 update 的寫入行為不變,由既有紀律區塊注入測試守
- 已排除:守衛面:不改任何閘的判定,只新增一個唯讀旗標

## 驗收條款

- [S1] 當在消費專案跑 `lumos update --dry-run` 時,專案工作目錄(不含 `.git/` 底下)的檔案集合與每個檔的位元組 應 都不變(含不得新建 `.lumos/vendored.json` 或 `docs/.gitignore`),`git config core.hooksPath` 應 不變,隔離的家目錄底下 應 一個檔都不變,工具來源的提交編號 應 不變 [test:t_update_dry_run_writes_nothing]
- [S2] 當來源的紀律範本跟專案現有的區塊不同時(含會更新、會新建、會接上三種),預覽算出的每個目標檔新內容 應 跟接著照它印的指令真的套用後該檔的位元組一模一樣,預覽 應 對會更新的檔印出完整區塊差異 [test:t_update_dry_run_rule_diff_matches_apply]
- [S3] 當來源的工具檔跟專案裡的不同或專案裡沒有時,預覽 應 列出這些檔,清單 應 跟接著真跑時「結尾自癒」補的檔一致 [test:t_update_dry_run_lists_vendored_changes]
- [S4] 當每個目標檔都是「不變」時,預覽 應 印「這次 update 不會改規範檔」;只差版本號時 應 標「只更新版本號」而不是印這句 [test:t_update_dry_run_no_rule_change]
- [S5] 當在工具來源 repo 自身跑 `lumos update --dry-run` 時,應 只預覽紀律區塊,CLAUDE.md 與 AGENTS 檔 應 一個位元組都不變;目標檔標記壞掉時 應 回 2,跟真的套用一致 [test:t_update_dry_run_source_repo]
- [S6] 當目標檔不是 UTF-8 時,預覽 應 印出「讀不了」與原因、回 2,不崩潰;結尾印的套用指令 應 帶上預覽用的 `--source` 絕對路徑與 `--no-pull` [test:t_update_dry_run_edges]

## 回退

還原本案的提交即可:只新增一個旗標、一條預覽路徑和兩支抽出來的共用函式,不帶旗標時行為不變,沒有資料要搬。

## 天花板

1. `lumos init`(既有 vault)、`init --force`、`bootstrap` 也會寫規範檔,但沒有自己的預覽;已有 vault 的專案可先跑 `lumos update --dry-run` 看同一份範本會怎麼改。
2. 預覽細算規範檔與工具檔;其餘動作(補忽略規則、寫指紋、設定 hooks 路徑、同步全域 hooks)只列名不細算。
3. 預覽與套用之間的變動(有人更新工具來源、專案檔被改)只靠結尾指令帶 `--source`、`--no-pull` 與套用時照常印差異兜住,沒有鎖定機制。

## 合約候選(設計審收斂後列出,未蓋章)

下游代碼審要驗這幾條有沒有兌現;蓋章仍走 guard scaffold、bind、audit,不確定就不標。

1. 預覽路徑不寫任何檔、不拉來源、不碰家目錄——改壞了預覽本身就違反 rtb 的規矩。守它的是 [S1]。
2. 預覽算出的新內容跟套用寫進去的一模一樣(同一段算法)——改壞了使用者同意的跟實際寫的會不一樣。守它的是 [S2]。

## 審計修正紀錄

- r1(2026-10-04,4 席:通才、邊界、整合 sonnet 加架構對齊 sonnet):去重 17 條/blocking 12 條/預覽改成不拉來源,補齊各種目標檔狀態的輸出、回傳碼、文件同步與範圍外的指令。卷證 governance/review-reports/update預覽規範檔變更/r1-*。
- r1 主要折入:預覽拉來源後仍跑舊程式、且會換掉全機共用工具(三席一致)→ 預覽一律不拉,結尾帶 `--source` 與 `--no-pull`;新建與接上要印內容與位置;整檔換行正規化要講;回傳碼照真跑;來源缺範本時沿用專案那份;非 UTF-8 不崩潰;專案外動作要列;手冊與 lifecycle 筆記錯句要改;init、bootstrap 明列不在範圍;比對迴圈抽共用、輸出開頭沿用 deinit 預覽格式。

## 實作紀錄

- 2026-10-04:`_reinject_claude_block` 拆成 `_reinject_compute`(算出新整檔內容,不寫)與寫回兩段;新增 `_vendored_pending`(套用的結尾自癒與預覽共用)、`_update_rule_plan`(照套用順序取範本、逐目標算)、`_update_preview`(印預覽、回傳碼照真跑)、`_toolchain_src_ok`(來源探針與擋下訊息,套用與預覽共用);`cmd_update` 加 `dry_run`,CLI 加 `--dry-run`。手冊、兩份指令參考、指令說明表與 [[Systems/lumos-cli-lifecycle]] 已同步,lifecycle 那句「update 在來源 repo 回 2」已改成現況。六條驗收測試先紅後綠;既有紀律區塊注入、update、init、deinit、文件一致性測試全綠。
- 推送前新增告警閘抓到 `_update_preview` 複雜度 22:拆成 `_preview_rule_target`(印一個目標檔)、`_preview_vendored`(工具檔與其餘動作)與主流程,不放行;來源提交編號改走既有的 `_sp_run_text`,沒有 git 指令時當成不是 git 來源。
- 代碼審 r1(正確性、架構對齊 sonnet):正確性席抓到區塊差異「刪掉的最後一行」與「新加的第一行」黏成一行(difflib 不補結尾換行;舊版套用時印的差異也有同樣毛病,寫回內容不受影響),兩邊輸入補結尾換行,S2 測試改成逐行比對、先紅後綠。架構對齊席:開頭標籤改用 deinit 預覽的 `root:`、加引號改用既有 `_sh_quote`;讀目標檔維持只接「讀不了」兩種例外(寬接會把程式錯誤藏成讀不了),理由補在那一行。
- 推送前全套測試抓到:全檔掃「取差異內容的 git 呼叫要帶防外部驅動器旗標」那支資安測試(t_lumos_content_diffs_all_disable_external_drivers)只認字面 `"diff"`,把 `_reinject_compute` 回傳字典的差異鍵也當成 git 呼叫。鍵名改成 `block_diff`,不放寬那支測試(它刻意寬、寧可誤報也不漏呼叫點)。
