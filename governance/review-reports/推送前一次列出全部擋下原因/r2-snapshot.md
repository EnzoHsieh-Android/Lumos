---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/guards-gates
  - risk/守衛面
lands_in:
  - Systems/bound-tests-gate
  - Systems/pitfalls-code-loop
---
# 推送前一次列出全部擋下原因_計劃

> 白話:推送前的閘現在是「遇到第一道擋下就結束」,一次只看得到一個原因;修好、重推(每次掛鉤要跑幾分鐘)才看到下一道。改成:全套測試之前那些便宜的閘全部跑完、把擋下原因收集起來,跑到全套之前只要有任何一道擋下,就一次列出全部原因並結束(不跑全套)。另外加一個預演指令,包住 `git push --dry-run`:不推送、不跑全套測試,只跑那些閘給你看結果(代碼審那一道本來就會跑的受波及合約測試照跑)。

## 緣起

- 2026-10-13 推 qo-frontmatter 那批時被依序擋了四次(新增告警、漂移檢查、回頭重讀、測試紅),每次修完重推才看到下一道;10-14 推示範回饋小修又被擋兩次(裁判簽名、新增告警)。出處是使用者 2026-10-14 的口述(問「這次有什麼 lumos 可以改進」時列為第一條);[[Verification/2026-10-13_後端示範交付]] 的改進候選當時沒收這一條,收工時補進去。
- 推送前掛鉤 `scripts/hooks/pre-push` 有十幾處擋下就 `exit 1`;`lumos code-loop check` 內部四道判定(合約測試、表態、新增告警、代碼審留痕)也是第一道沒過就停。2026-09-06 全 repo 審視 #12 只調了順序(便宜的先跑),沒做「一次列出全部」。

- 舊裁定:[[Projects/全repo審視_計劃]] #12 的 PRIOR-ART 全句是「裁定=borrow-design(fail_fast 不借——本 repo 已裁每道閘本來就 exit 1)」。那句的語境是不用另外借工具的遇錯就停開關,沒有評估過「一次列出全部」;F52 講的是測試第一支紅就停,是另一層。使用者 2026-10-14 聽完「推送前的閘一次只報一個原因」後明確要求修這一條——推翻該句;實作時在 #12 那段旁註記被本計劃取代。

PRIOR-ART: 外部:Git 生態最常用的 pre-commit 框架預設 `fail_fast: false`——每個 hook 都跑、最後一次列出全部失敗;`make -k`(keep going)同理。本 repo 內:pre-commit 掛鉤的 Gate L 已經是「旗標記下、迴圈繼續、各自印擋下說明、迴圈後統一 `exit 1`」——本計劃是同一種做法的跨閘版本,承襲它,不另造。預演借 git 自己的 `git push --dry-run`(它會照常呼叫推送前掛鉤、由 git 組出掛鉤要讀的推送行、保證不送出物件),不在 lumos 裡重算推送範圍。
RETIRE-IF: 上線 8 週內,版控治理帳裡真推送(不含預演)的 `prepush-summary` 事件中「兩道以上不同的閘」那幾筆為 0——撤掉收集邏輯、回到遇錯就停。
REVISIT:2026-12-15 數一次 `prepush-summary` 事件裡兩道以上不同閘的筆數,照 RETIRE-IF 判要不要撤。

## 做法

1. **掛鉤收集擋下原因**:掛鉤裡全套測試之前的每一道會擋的閘——裁判簽名(`anchor verify`)、簽名檔沒提交(`governance/anchor-baseline.json` 有未提交改動)、圖譜健檢(`doctor --ci`)、每支檔有家(`home check`)、筆記形狀(`note-shape`)、雙向門放行(`spec-gate --push-check`)、代碼審判定(`code-loop check`)、存量漂移(`drift check`)、回頭重讀(`note-audit reread-check --gate`),共 9 道——擋下時不再 `exit 1`,改呼叫共用函式 `pp_record_block <閘名> <ref 或空> <一句原因>`,照原樣把該道的完整說明印出來,然後繼續下一道。同一道被多個 ref 擋下時各記一筆。
   - **記在暫存檔,不用陣列**:`pp_record_block` 用 `printf '%s\t%s\t%s\n'` 追加一行到 `$_PP_TMP/blocks`(閘名、ref、原因,以 tab 分隔)。原因一律是掛鉤裡寫死的一句(不放工具輸出),ref 名照 git 規則不能含控制字元,所以 tab 與換行不會出現在欄位裡;函式仍先把三個欄位裡的 tab、換行換成空白再寫。筆數用 `wc -l` 算。這樣整類避開 bash 3.2 在 `set -u` 下展開空陣列會崩潰的問題(macOS 內建 bash 3.2.57 實測 `for x in "${A[@]}"` 對空陣列報 unbound variable),不用另記展開寫法。
   - **裁判簽名也收集,不再立刻停**:裁判簽名管的是測試檔與掛鉤(錨點清單),不管 `scripts/lumos`。被改的若是掛鉤本身,它在這一刻已經在跑,停不停都由它決定,提早結束換不到可信度。後面的閘大多是 `scripts/lumos` 在判,不經過測試檔;例外是代碼審那一道的受波及合約測試與雙向門放行,它們會在全套之前跑 `scripts/test_lumos.py` 裡的測試——這兩道的綠燈這次用的是沒簽名的測試檔。不論結果,這次推送都已經因為裁判簽名被擋,所以不會變成放行;彙總裡有裁判簽名那筆時,最前面加一行「裁判檔沒簽名:代碼審與雙向門放行這次跑的測試用的是沒簽名的測試檔,它們的綠燈不算數;簽名後重推會重跑」。
   - **刪除與 tag 照舊**:逐 ref 迴圈遇到刪除照舊跳過、tag 照舊不跑代碼審判定,只把原本的擋下換成記下。
   - **跟 pre-commit 的關係**:pre-commit 的 Gate PY、Gate H、Gate NS 之間仍是遇錯就停,本計劃不改。理由:那幾道合計幾秒,修完重提交的代價是幾秒;推送這邊每重推一次要幾分鐘,這才是要解的痛。
2. **中斷一律結束**:
   - 9 道裡每一支 lumos 呼叫都先取回傳碼、再過 `pp_stop_if_signaled`——包括現在用 `if ! …` 寫、沒取回傳碼的裁判簽名與圖譜健檢兩道。規則是「判斷點之前每一行 `"$PY" "$GRAPHCTL"` 呼叫,緊接著都要有 `pp_stop_if_signaled`」,守衛測試照這條規則逐行驗,不數總行數。
   - 收拾暫存的陷阱拆開:`EXIT` 只負責 `impact_done` 與刪 `$_PP_TMP`;`INT` 改成 `exit 130`、`TERM` 改成 `exit 143`(結束時再走 `EXIT` 那支收拾)。現在 `trap … EXIT INT TERM` 共用一支、裡面不結束,掛鉤自己收到中斷時會刪掉暫存目錄後繼續往下跑(`/bin/bash` 3.2.57 實測:陷阱跑完印出下一行);這是現有的缺陷,收集模式會讓它更常踩到,一起修。
3. **全套測試之前統一判**:判斷點放在建 `_AUTOLOOP_LOG`、`_TESTS_LOG` 那兩個暫存檔的 `mktemp` 之前(這樣擋下時不會留下兩個 `$_PP_TMP` 以外的空檔)。
   - `$_PP_TMP/blocks` 有任何一行,就呼叫 `lumos push-summary --blocks-file "$_PP_TMP/blocks"`:由它印「這次推送共有 N 筆擋下(M 道閘)」的彙總(N 是筆數,同一道被多個 ref 擋或代碼審內部擋兩個原因都各算一筆;M 是不同閘名的個數),逐筆一行:閘名、ref、原因,詳細處理方式看上面那一段。ref 欄只在這次推送有兩個以上非刪除的推送行時印。它同時落一筆治理帳(閘名 `prepush-summary`、kind `blocked`、hard、帶 `LUMOS_PUSH_ATTEMPT`、`extra` 裡放 N、M 與不同閘名的清單)。
   - 不論 `push-summary` 成不成功,掛鉤接著一律 `exit 1`,不跑自主迴圈測試與全套測試。`push-summary` 回非零或不存在(舊版 lumos)時,掛鉤自己用 `while read` 逐行印一份簡版彙總——觀測失效不得改變擋下。
   - 沒有任何一行才照舊往下跑測試。
   - 為什麼彙總交給 lumos:專案慣例是「做判定的那一方順便落帳」,掛鉤不直接寫帳;印彙總正是 `push-summary` 這支子命令自己的工作,記帳是它的副作用,不是給外部腳本的記帳入口。
   - 連帶擋下照實列:圖譜健檢擋下時,依賴圖譜索引的閘(每支檔有家、雙向門放行、回頭重讀)可能跟著擋。彙總照實列出,不去猜哪道是連帶;這會讓 RETIRE-IF 的筆數偏多,方向是「更不容易撤」,可以接受。
4. **前提壞掉的照舊立刻停**:找不到 Python 3.14、暫存目錄建不起來(掛鉤開頭的總暫存目錄,與測試前建 log 檔那一步)、使用者中斷(第 2 點)——這幾種後面什麼都跑不了或不該再跑,維持立刻結束。找不到 `scripts/lumos` 照舊是「提醒後放行」(`exit 0`),不在收集範圍。
5. **代碼審判定內部也全部判完**:`lumos code-loop check` 新增 `--keep-going`(名字照 PRIOR-ART 的 `make -k`):
   - 四道判定(合約測試、表態、新增告警、代碼審留痕)都跑完,每道擋下各印各的訊息(原本的擋下句一字不改),最後只要有一道擋下就 rc1。
   - **一處判**:判定函式在這個模式下把擋下累積進一個清單,每個原本 `return {"blocked": False, …}` 的地方(pitfalls 失敗、pitfalls 沒有 JSON、pitfalls 例外、tier 不是 high、留痕有效、留痕要求被環境變數跳過、合併側放行)改成經過同一個收尾函式:清單非空就回擋下,清單是空的才照原樣回放行。放行站點的意思變成「這一道過了」,不能蓋掉前面記下的擋下。
   - pitfalls 失敗時,需要 tier 的後幾道照現在的 fail-open 不判,前面記下的擋下照算。
   - 合約測試先紅時照樣算風險分級,後面幾道照判。合約測試那筆的 `reason_kind` 是 `bound_tests`(現在那個回傳值沒有這個欄位)。
   - 帶 `--json` 時多一個 `blocks` 清單(每筆 `reason_kind` 與 `reason`);`blocked`、`reason`(放第一筆)照舊;`tier` 在這個模式下一律是算出來的分級,pitfalls 失敗時是 `unknown`。不帶 `--keep-going` 時行為與輸出一字不變(其他呼叫者如 CI 不受影響)。
   - 印合約測試狀態的那幾句照「合約測試有沒有記成擋下」選,不照第一個擋下原因選:記成擋下就不印「低風險只提醒不擋」那類句子。
   - 治理帳照舊一次判定一筆 `code-loop` `blocked` 事件(現有統計的筆數意義不變),`extra` 多放 `blocks` 的 `reason_kind` 清單。
   - 這個模式最後多印一行 `LUMOS-BLOCKS: <reason_kind 以逗號分隔>`,掛鉤讀它,替每個 `reason_kind` 各記一筆:閘名一律是 `code-loop`(所以 M 只算一道),原因用對照表寫死的一句,例如表態那筆是「棧別檢核題表態不完整」。掛鉤把這一行從要印給人看的輸出裡濾掉。
   - 逃逸自動記帳照現在的判斷(掛鉤認「受波及合約的測試沒過」與「tier=high 且」兩句;兩句同時印出時各記一筆)。
6. **新舊版本混用不能變成放行**:掛鉤與 `scripts/lumos` 分開複製到消費專案,而且 `core.hooksPath` 會讓好幾個工作樹共用同一份掛鉤(本 repo 的工作樹現在就指到本機安裝的那份),所以兩邊版本會錯開。
   - 新掛鉤配舊 lumos:掛鉤在逐 ref 迴圈之前探測一次 `code-loop check --help` 的輸出有沒有 `--keep-going`,沒有就不帶這個旗標,也不讀 `LUMOS-BLOCKS:` 行,代碼審那一道照舊只記第一個原因——不會因為舊版不認得旗標回 2 而被 fail-open 放行。`push-summary` 不存在時走第 3 點的簡版彙總。
   - 舊掛鉤配新 lumos:舊掛鉤不帶新旗標,行為照舊;`push-preview` 會先檢查掛鉤(見第 7 點)。
7. **預演指令** `lumos push-preview [git push 的參數…]`:包住 `git push --dry-run`。
   - **怎麼跑**:先確認會被呼叫的掛鉤支援預演——用 `git rev-parse --git-path hooks/pre-push` 找到那支檔(照 `core.hooksPath` 走),檔裡要有一行 `# lumos-hook-cap: push-preview`;沒有就回 2,說「掛鉤是舊版,先 `lumos update`」,不跑(免得舊掛鉤跑完 8 分鐘全套)。接著建一次性票(下面),帶著它跑 `git push --dry-run <參數>`。推送行、遠端名(掛鉤第一個參數)、遠端有沒有這個分支,全部由 git 自己決定,lumos 不另算——跟真推送同一條路。
   - **沒給參數時**:分支有追蹤的遠端分支,就照 git 的預設;沒有追蹤時,只有一個遠端就用它,多個遠端時用主線所在的那個(主線候選與 `push-range` 共用同一份);都判不了,回 2 並請人帶參數,例如:
     `lumos push-preview Lumos HEAD:refs/heads/<分支>`
     detached HEAD 又沒給參數,回 2。
   - **一次性票**:`push-preview` 在 `git rev-parse --git-common-dir` 底下的 `lumos/` 建一個檔 `push-preview.<隨機值>`,內容是同一個隨機值,並帶環境變數 `LUMOS_PUSH_PREVIEW=<隨機值>` 跑 git。掛鉤只有在「環境變數有值、對應的檔存在、內容相符、建立不到 10 分鐘」時才進預演模式;任何一項不符,印一句「忽略 LUMOS_PUSH_PREVIEW(不是預演指令叫的),這次照真推送跑」,並把變數清掉後照常跑完整掛鉤。掛鉤結束時刪票,`push-preview` 收尾也刪一次。所以把這個變數寫進 shell 設定、或從別的程序漏進來,都不會讓真推送跳過測試。
   - **預演模式下掛鉤做什麼**:跑完 9 道與統一判斷,在判斷點停:把結果(擋下幾筆)寫進票旁邊的結果檔 `push-preview.<隨機值>.result`,有擋下回 1,沒有回 0 並印「便宜的閘都過了;全套測試沒跑(預演不跑),真推送時還會跑」。回 0 不代表全套測試綠。git 照 `--dry-run` 不送出任何物件。
   - **檔案誰刪**:掛鉤結束時只刪票(結果檔要留給 `push-preview` 讀);`push-preview` 讀完結果後刪票與結果檔;`push-preview` 每次開始時先刪掉那個資料夾裡超過 10 分鐘的票與結果檔(收拾上一次被中斷的殘檔)。
   - **為什麼是新子命令、不是 `--dry-run` 旗標**:專案慣例的 `--dry-run` 都是加在「會做事的那個 lumos 指令」上;推送不是 lumos 指令,對應的旗標就是 git 自己的 `git push --dry-run`。`push-preview` 只是替它加上票與結果檔的薄包裝,名稱對齊既有的 `push-range`。
   - **回傳碼**:0=閘全過、1=有擋下、2=預演沒跑成(掛鉤舊版、判不出推去哪、git 連不上遠端或其他錯誤——結果檔不在就是這一類,`push-preview` 附上 git 的訊息)。這樣「被擋」與「沒跑成」分得開。
   - **工作目錄有未提交改動時**先印一句:圖譜健檢與簽名檔那兩道看工作目錄、其他道看提交,預演結果可能跟提交之後不一樣。
8. **預演不寫版控帳**:
   - 掛鉤在預演模式下不呼叫 `loop escape --auto`(逃逸帳的筆數被其他機制拿來當退回門檻,預演沒推送,不算逃逸)。
   - lumos 的兩支治理帳寫入器在分流之前,看到有效的預演票(同一條驗法:環境變數有值、票檔存在且相符)就替事件標上 `preview: true`;分流判定(現在決定哪些事件進本機帳的那一支)把帶 `preview` 的一律分到本機帳 `docs/.governance-local.jsonl`。預演照樣留觀測,但不弄髒版控檔,也不混進真推送的統計。驗法跟掛鉤用同一張票,漏出來的變數沒有票就不生效。
   - 實作第一步先盤點:9 道閘跑起來會寫到哪些版控檔(治理帳、逃逸帳以外若還有,一併處理),盤點表寫進本節。

## 驗收條款

- [S1] 當兩道彼此獨立的便宜閘同時擋下(例:圖譜健檢有壞連結,且 `governance/anchor-baseline.json` 改過沒提交)時,推送前掛鉤應回 1,彙總裡兩道都列出,而且全套測試沒有被跑到。[test: t_prepush_collects_all_blocks]
- [S2] 當只有一道擋下時,應回 1、印出那一道原本的完整說明加彙總,全套測試沒有被跑到;當沒有任何一道擋下時,應照舊跑到全套測試。[test: t_prepush_collects_all_blocks]
- [S3] 當找不到 Python 3.14 時,掛鉤應立刻結束(不收集、不往下跑)。這條守的是既有行為不被改壞,改動前就是綠的。[test: t_prepush_stops_without_python]
- [S4] 當 `lumos code-loop check --keep-going` 遇到表態不完整且有新增告警時,兩個原因都應印出、回 1;合約測試紅且 tier=high 又沒有代碼審留痕時,兩個原因也都應印出;不帶 `--keep-going` 時應照舊只印第一個,輸出與現在一字不差。[test: t_code_loop_check_keep_going]
- [S5] 當執行 `lumos push-preview` 時,不應推送、不應跑全套與自主迴圈測試,應印出各道結果;有擋下時回 1、全過時回 0 並說明全套測試沒跑;遠端沒有這個分支時,照 git 給的推送行當成新分支首推處理。[test: t_push_preview_runs_gates_without_suite]
- [S6] 9 道閘逐道各讓它單獨擋一次,掛鉤每次都應回 1、全套沒被跑到、彙總列出那一道。[test: t_prepush_each_gate_blocks_alone]
- [S13] `code-loop check --keep-going` 已記下一筆擋下之後,走到每一個放行站點(pitfalls 失敗、沒有 JSON、例外、tier 不是 high、留痕有效、留痕被環境變數跳過、合併側放行)都應仍回 1。[test: t_code_loop_keep_going_pass_sites_keep_blocks]
- [S14] 一次推兩個 ref、兩個都被同一道擋下時,彙總應列兩筆(ref 欄有值)、閘數算 1;推的是刪除時照舊跳過、推 tag 時照舊不跑代碼審判定,不應因此多記或漏記。[test: t_prepush_multi_ref_blocks]
- [S7] 當新掛鉤配上不認得 `--keep-going`、也沒有 `push-summary` 的舊 lumos,而代碼審判定會擋時,掛鉤應回 1(不是放行),並印簡版彙總。[test: t_prepush_mixed_versions]
- [S8] 當環境裡有 `LUMOS_PUSH_PREVIEW` 但沒有對應的票(或票過期、內容不符)時,真推送應照常跑到全套測試,並印那句「忽略」;`push-preview` 遇到沒有預演標記的掛鉤時應回 2 且不跑掛鉤。[test: t_push_preview_token_required]
- [S9] 預演擋下時,版控治理帳與逃逸帳的內容都不應改變,本機帳應多出帶 `preview: true` 的事件。[test: t_push_preview_no_tracked_ledger_writes]
- [S10] 判斷點之前任何一支 lumos 呼叫(9 道裡除了簽名檔沒提交那道以外的 8 道,加上 pitfalls、impact 等輔助呼叫)被訊號中斷(回傳碼 128 以上)時,掛鉤應以該回傳碼立刻結束、不再跑後面的閘;掛鉤自己收到中斷時也應結束,不應刪掉暫存目錄後繼續跑。[test: t_prepush_interrupt_stops_every_gate]
- [S11] `push-preview` 在 detached HEAD 沒給參數、多個遠端判不出主線、git 連不上遠端時,都應回 2 並說明原因,不應回 0 或 1。[test: t_push_preview_edges]
- [S12] 有擋下時,版控治理帳應多一筆 `prepush-summary` 事件,帶筆數、閘名清單與這次推送的識別碼;`push-summary` 失敗時掛鉤仍回 1。[test: t_prepush_summary_records_event]

- 測試怎麼搭:S6、S7、S10 用一支假的 `scripts/lumos`(小 Python 腳本,照子命令與環境變數決定回傳碼與輸出;`--help` 輸出可選擇帶不帶 `--keep-going`),放進測試搭的假 repo,讓每一道都能單獨擋、單獨被中斷;S1、S2 用真的 lumos(圖譜健檢壞連結加簽名檔改過沒提交,沿用 `t_prepush_cheap_gates_run_before_expensive_suite` 的搭法)。現有範本餵的推送行是假的提交編號,逐 ref 那幾道走不到,所以逐道驗一律用假 lumos。
- 既有守衛要一起更新:`t_prepush_cheap_gates_run_before_expensive_suite`(便宜的閘擋下時不跑全套)行為不變、照舊要綠;`t_prepush_gates_stop_on_signal` 現在數 `pp_stop_if_signaled` 的行數(8 行),改成第 2 點的逐行規則,併進 S10 那支。

## 實作清單(照順序)

1. 盤點斷言「某道擋下後,後面的閘沒被叫」的既有接線測試(漂移檢查、雙向門放行、回頭重讀各自的接線測試等),收集模式下這類斷言會翻紅,逐支改成「擋下時全套沒跑」。
2. 先寫第 S1–S14 的紅測試,再改掛鉤與 `scripts/lumos`。
3. 改掛鉤時不能動兩串上線標記註解 `# lumos drift check`、`# lumos note-audit reread-check`(工具用 `git log -S` 靠它們找上線點);回頭重讀那一行呼叫要保留 `--gate` 在同一行(檢查「推送前掛鉤有沒有接線」的那支逐行找含 `note-audit reread-check` 的非註解行並要求同行有 `--gate`,包進 `pp_record_block` 時別讓它掉到別行)。
4. 掛鉤加一行 `# lumos-hook-cap: push-preview`(第 7 點靠它判)。
5. 改了 `scripts/hooks/pre-push` 與 `scripts/test_lumos.py`(兩支都在錨點清單),提交前跑 `lumos anchor approve --note "<為什麼改>"`,把 `governance/anchor-baseline.json` 併進同一個功能提交。
6. 文件同步:
   - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 講 `code-loop check` 四道判定「序列早退」那一列,補 `--keep-going` 與掛鉤的用法;新增 `push-preview` 一列。
   - `skills/lumos-code-loop/SKILL.md` 講 pre-push 對每個分支 ref 叫 `code-loop check` 那段,補一句掛鉤改帶 `--keep-going`、可先用 `lumos push-preview` 預演。
   - `scripts/lumos` 判定函式裡「序列早退,先中的先報」那句註解改成兩種模式的說明。
   - [[Systems/棧別提問表態閘]] 與 [[Projects/棧別提問表態閘_計劃]] 講「序列早退」的那兩句。
   - [[Systems/bound-tests-gate]]:講「六道閘都先過 pp_stop_if_signaled、擋下後不跑全套」那句改成第 2 點的規則加收集語意;講回頭重讀排序的那句照新流程改。
   - [[Systems/存量漂移守衛]]、[[Systems/筆記內容閘]] 各自記錄的掛鉤掛接段,補「擋下改成記下」。
   - [[Projects/全repo審視_計劃]] #12 那段旁註記被本計劃取代。
7. 說明落點:掛鉤的收集、`push-preview`、`push-summary` 寫進 [[Systems/bound-tests-gate]](它管 `scripts/hooks/pre-push` 與 `scripts/lumos`,其他提到掛鉤的節點只放連結);`code-loop check --keep-going` 寫進 [[Systems/pitfalls-code-loop]](它管 `scripts/lumos`)。實作時用 `lumos home check` 覆核改到的每支檔都有家。

## 實務隱患

- 守衛面:這是推送閘本身。最大的風險是「收集」寫錯讓某道擋下被吞掉、變成放行。對策:掛鉤只用一個共用函式記、一處判;`code-loop check` 只用一個收尾函式判;版本混用先探測;預演要票。S6 逐道、S13 逐放行站點各驗一次,S7 驗混用,S8 驗漏出來的變數。
- 已排除:金流:不碰任何付款或點數。
- 對外連線:預演跑 `git push --dry-run`,會連遠端讀它有哪些分支(唯讀),不送出任何物件;連不上時回 2(第 7 點)。真推送照舊。
- 已排除:不可逆:只改掛鉤的判斷流程與兩個子命令,還原提交即可;擋下的情況不會變少。
- 輸出變長:一次列出全部之後,被擋時的訊息會比現在多;彙總段放在最後、逐道一行,讓人一眼看到總數。
- 時間:預演與真推送一樣會跑代碼審那一道的受波及合約測試(有自己的秒數預算),這不算在「全套測試」裡。收集模式的最壞時間,等於「今天一次便宜閘全過的推送」跑到全套之前的最壞時間——同樣那幾道,今天全過時本來就全部要跑。逐 ref 的大項:漂移判定本體每個 ref 最壞 60 秒、它之前算範圍的 git 呼叫每次最多 20 秒、回頭重讀約 30 秒、新增告警閘最多 300 秒(代碼審判定在表態先擋下時,今天不會跑到它,收集模式會跑),一次推多個 ref 會相加。跟今天比,多出來的只是「第一道擋下之後那幾道」的時間;而這些時間在修完第一個原因重推時本來就要花,再加上那次重推的等待。所以不另設總時限。

## 回退

- 還原提交,lumos 本身即回到遇錯就停;`code-loop check` 不帶 `--keep-going` 的行為沒變,CI 與其他呼叫者不受影響。
- 消費專案:掛鉤是 `lumos update` 逐位元組複製過去的,也在錨點清單裡。回退(或上線)之後,每個消費專案要跑 `lumos update`,再 `lumos anchor approve --note "<為什麼>"` 並提交簽名檔,否則下一次推送會被裁判簽名擋下。本機安裝那份(`core.hooksPath` 指向的)要 `git pull` 更新。
- 版本錯開的中間狀態都安全:新掛鉤配舊 lumos 走第 6 點的探測與簡版彙總;舊掛鉤配新 lumos 等於沒有這個功能;`push-preview` 遇到舊掛鉤回 2 不跑。
- 撤除時一併改回:掛鉤的收集與預演段、`code-loop check --keep-going`、`push-preview`、`push-summary`、第 8 點的預演分流、實作清單第 6 點列的每一份文件,以及 [[Projects/全repo審視_計劃]] #12 旁的註記。

## 審計修正紀錄

- r1(2026-10-14,6 席):35 條/blocking 23/預演開關、版本混用、預演寫帳、代碼審內部放行蓋掉擋下、中斷與暫存、撤除條件量不到、測試只驗兩道是主要缺口,全數折入,做法改寫成 8 點。席報告在 `governance/review-reports/推送前一次列出全部擋下原因/`。
- 依根因分組折入(每組一條統一規則,不逐點補):
  - 版本混用(正確性 2、整合 1、回滾 1、回滾 2 前半、邊界 3)→ 第 6 點探測、第 7 點掛鉤標記、S7、S8。行為例:新掛鉤配舊 lumos 且表態不完整 → 掛鉤不帶 `--keep-going`、舊 lumos 回 1 → 掛鉤回 1。
  - 預演開關可被漏出來的變數觸發(正確性 3、整合 2、回滾 2 後半、邊界 1)→ 第 7 點一次性票、S8。行為例:`export LUMOS_PUSH_PREVIEW=1` 後真 `git push` → 印「忽略」、全套照跑。
  - 預演寫帳(正確性 4、併發 1、回滾 3、邊界 2)→ 第 8 點、S9。行為例:預演兩次都被圖譜健檢擋 → `git status` 不出現版控帳改動,本機帳多兩筆帶 `preview`。
  - 代碼審內部放行蓋掉擋下與輸出契約(正確性 1、邊界 7)→ 第 5 點一處判、`bound_tests`、`LUMOS-BLOCKS:` 行、單筆事件、S13。行為例:合約測試紅後 pitfalls 失敗 → 回 1。
  - 中斷與暫存(併發 2、邊界 5)→ 第 2 點逐行規則與陷阱拆開、第 3 點判斷點改用「mktemp 之前」描述、S10。行為例:圖譜健檢跑到一半按 Ctrl-C → 掛鉤以 130 結束,不跑每支檔有家。
  - bash 細節(整合 3、邊界 8)→ 第 1 點改記暫存檔、不用陣列。
  - 預演邊界(邊界 6、併發 4、整合 5 的第二個問題、架構對齊 B、架構對齊 C)→ 第 7 點改包 `git push --dry-run`,推送行與遠端判斷交給 git;名稱 `--collect` 改 `--keep-going`;回傳碼分三種;S11。
  - 撤除條件量不到與連帶擋下(回滾 4、邊界 9)→ 第 3 點 `push-summary` 落帳、RETIRE-IF 改數事件、REVISIT、連帶照實列、S12。
  - 測試覆蓋(回滾 5、邊界 10)→ S6 逐道、S13 逐放行站點、假 lumos 搭法、S3 註明是保留既有行為。
  - 回退與殘留(回滾 6、回滾 7)→ 回退節改寫。
  - 時間(邊界 4、併發 3)→ 時間那條改成跟「今天全過的推送」比的算法,列出新增告警閘 300 秒。
  - 實作與文件同步(整合 4、整合 5 的第一個問題、架構對齊 D)→ 新增〈實作清單〉。
  - 第二種做法(架構對齊 A)→ PRIOR-ART 寫明承襲 pre-commit 的 Gate L;第 1 點寫明 pre-commit 其他閘不改的理由。
  - 裁判擋下後繼續跑的副作用(正確性 5)→ 重新判:裁判簽名不管 `scripts/lumos`,後面便宜的閘照常可信,改成收集、拿掉「只供參考」那行;寫帳副作用由第 8 點(預演)與照常記帳(真推送)處理。
- r1 折入核對(2026-10-14,1 席):35 條裡 32 條已落地、3 條部分(邊8 的 ref 欄判準、邊10 的多 ref/刪除/tag 測試、架C 為何不用 `--dry-run` 旗標),另報 6 處小問題(預演其實會跑合約測試、裁判簽名理由的前提、結果檔誰刪、代碼審多筆的閘名與 N/M 算法、`LUMOS-BLOCKS:` 行要濾掉、S10 的範圍);全數補進本文,新增 S14。
