---
type: project
status: doing
created: 2026-09-30
updated: 2026-09-30
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
related:
  - "[[Projects/舊句偵測實驗_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
  - "[[Issues/存量筆記漂移三種機制_rtb根因回饋]]"
---
# 舊句檢查_計劃

白話:程式裡某個函式、測試、旗標被刪掉或改名了,筆記裡還寫著它的句子就成了「舊句」,下一個讀筆記的人會照著去找不存在的東西。這份計劃把實驗選出來的判法做進推送前的漂移檢查:推送時把「這次消失的名稱」跟筆記比對,列出還在講它們的句子。先只提醒兩週、每次都記帳量準度,達標才把預設改成擋。

依據:[[Projects/舊句偵測實驗_計劃]]〈實驗結果〉(2026-09-30,判法 P4r:9 題擋到 7 題、rtb 大提交要處理 16 筆、13 題非漂移誤列 0 題;沒拿來調參數的工具鏈對照組 4 筆列出 0 筆真);Enzo 2026-09-30 說「程式改了、筆記舊句還在,我要想辦法解決」,並授權編排者決策。本計劃用的判法是 P4r 再補工具鏈對照組點名的兩個誤報形狀(下稱 P4r2,〈做法〉2)。P4r2 重跑(`governance/eval/drift-exam/old-sentence/report-2026-09-30-p4r2.md`):9 題、rtb 大提交 16/65、rtb 182 個提交、13 題非漂移,跟 P4r 逐筆相同;工具鏈 300 個提交要處理 2→0,多放過的 3 句都是誤報——但那 3 句正是拿來設計這兩處改動的題,證據薄,只能說沒新增風險。**實作的驗收以參考實作 `governance/eval/drift-exam/old-sentence/old_sentence_exp.py` 的候選 P4r3 跑出的數字為準**(P4r3 = P4r2 加本計劃 r1 收窄的撤除節②,設計審 r1 鏡像核對後加進實驗程式;P4r、P4r2 照原樣留著可重跑):9 題擋到 7、rtb 182 個提交 91 筆(要處理 20,b2fc512 16/65)、13 題非漂移誤列 0、工具鏈 300 個提交(頂端 40c1fe0d)1 筆只列出、要處理 0(2026-09-30 重跑,跟 P4r2 逐筆相同;同一次重跑 P4r、P4r2 的數字跟原報告一致);凡是本計劃的字面跟 P4r3 不一樣,以 P4r3 為準、並回頭改計劃。重跑指令:`cd governance/eval/drift-exam/old-sentence && python3.14 old_sentence_exp.py run --rtb <rtb 完整 clone> --tc <工具鏈 clone> --tc-head 40c1fe0d --tc-n 300 --cands P4r,P4r2,P4r3,P4r3s --out <json>`(rtb 那份用實驗報告指的唯讀複製,約 10 分鐘)。

設計審 r1 量的數字(2026-09-30,rtb 用實驗那份唯讀複製、工具鏈頂端 40c1fe0d;撤除節②收窄與形狀過濾兩項後來收進實驗程式成 P4r3、P4r3s 重跑過,另兩項是只替換一處的對照腳本,在編排者暫存區 `osfold/`,正確性席的在 `osr1out/`):
- 撤除節②收窄(引用區塊行要同時含撤除字樣與範圍宣告字):現在的工具鏈圖譜「只因②才不看」的非空行 603 行/10 篇 → 163 行/2 篇;rtb 圖譜 0 → 0。剩下兩篇:`Systems/記憶過期清掃` 107 行(真宣告)、`Projects/主session鏡頭利用率_計劃` 56 行(「…撤掉兩次…本節以下是重寫版」,仍是誤觸發)。對照組誤報第 4 筆(`Systems/記憶過期清掃:171` 的 `--restore`,828a68be 那版第 30 行「下面凡是講…都是寫檔版的歷史紀錄」)照樣放過。9 題、rtb 182、工具鏈 300 重跑跟 P4r2 逐筆相同。
- 形狀過濾拿掉(外家否決席要求;實驗程式的 P4r3s):9 題、13 題非漂移不變;rtb 91 → 134 筆(要處理 20 → 28)、工具鏈 1 → 24 筆(要處理 0 → 2)。多出來的 66 筆逐筆看過,觸發名是 `investigation`、`locked`、`env`、`opener`、`busy`、`pending`、`stamp` 這類被刪的測試輔助函式、資料類別欄位或區域方法,筆記裡講的是同一個英文字或路徑片段(`phase13-investigation-eval`、`database is locked`、`migrate-stamp`),**0 筆真舊句**。所以保留形狀過濾,把漏掉的那一類寫進〈誠實界線〉、兩週後照〈做法〉4 再量一次。
- 程式檔範圍(正確性席量):只用 `_drift_probe_is_py`、不排除 docs/ 與 governance/ 時,工具鏈 300 個提交 1 → 6 筆、要處理 0 → 1;多的 5 筆有 4 筆誤報(`governance/eval/sync-nudge/probe_sync.py` 的 `tool_use`),1 筆真舊句(`governance/eval/retrieval_eval.py` 拿掉的 `_macro_on`)。照參考實作排除,驗收數字維持上面那組。
- 其他程式檔的副檔名清單改用既有 `_nodehome_code_kind`(不另抄參考實作的 `TEXT_EXTS`):9 題、rtb 182、工具鏈 300 重跑跟 P4r2 逐筆相同。

PRIOR-ART: ①判法照實驗的 P4r2(撤除節②在 r1 收窄),參考實作見上;能用既有函式的都用:列檔與內容編號 `_drift_oids`、批次讀 `_nodehome_cat_blobs`、解碼 `_drift_decode`、Python 判定 `_drift_probe_is_py`、抽定義擴充 `_drift_py_names`(加參數,既有呼叫端不變)、剖不動的退路 `_drift_py_def_re`、筆記讀取 `_drift_tree_env`、分區與圍欄 `_notelines_regions`、`_visible_lines`、名稱先篩照 `_DriftNames` 的做法(切詞改 ASCII,〈做法〉2)、印出 `_drift_print_findings`、`_drift_print_hints`、shell 參數 `_drift_sh`;快取照既有 `~/.cache/lumos/<名>/` 那一種(dispatch-lens、bound-filter);②接在既有的 `lumos drift check` 裡當一種新發現(沿用它的起點判法、表態檔、治理帳 gate 名),但判定另開一支函式、不放進 `_drift_check_core`(那支也給考試與歷史重放用,放進去會改掉既有噪音基準);③世界解:Doorstop/Swimm 的「錨點式 suspect」要先埋錨點,本專案筆記沒有錨點,所以走「比對消失的名稱」([[Projects/先問世界_存量掃描裁定]])。
RETIRE-IF: 兩週只提醒期滿(REVISIT 那天)照〈做法〉4 的量法判:①要處理層準度低於 60%、②任一次推送要處理超過 30 筆、③時間到的次數占有判定的 `m1` 帳超過 5%、④被句內字眼過濾放過的句子裡真舊句占三分之一以上——任一條成立就不把預設改成擋、留在提醒(④成立另案收窄字眼表);再兩個月準度仍低於 60% → 整個撤掉。
REVISIT:2026-10-14 照〈做法〉4 量舊句檢查兩週的帳(工具鏈 `grep '"check": "old-sentence"' docs/.governance-log.jsonl`,rtb 那份由本工具鏈的會談用跨會談訊息請 rtb 會談回報同一個 grep 的輸出),跑參考實作的 revisit 子命令(字眼過濾放過的、形狀過濾放過的、撤除節②豁免行數、否定撤除行數四樣);照 RETIRE-IF 四條判轉不轉擋;〈範圍〉的前置那天還沒接上、帳不滿兩週,就把這一行的日期改成接上後滿兩週那天
REVISIT:2026-12-14 看 10-14 之後兩個月的帳,要處理層準度仍低於 60% 就照 RETIRE-IF 整個撤掉 `m1`(10-14 若順延,這天跟著順延兩個月)

## 範圍

- **做**:①`lumos drift check --diff` 多一種發現 `m1`(舊句):這次推送範圍裡被刪或改掉的 Python 定義名、旗標,以及被刪的程式檔路徑,在終點整個 repo 都找不到的,筆記裡還提到的句子;②撤除與歷史過濾(P4r2,撤除節②收窄);③`m1` 的模式獨立一個開關 `drift_check.old_sentence`(warn/block/off,沒寫=warn),跟既有 c1–c5 與 probe 共用的 `drift_check.gate` 分開;④表態綁觸發的名稱;⑤有候選名稱的每次 drift check 都記一筆 `m1` 帳(含零筆;沒有起點也記一筆),兩週後量準度;⑥定義快取以「blob 內容編號、抽法版本、Python 主次版本」為鍵,重複推送不重剖;⑦參考實作的 P4r3 與 `revisit` 子命令(已加進實驗程式),給驗收與 REVISIT 量漏報、豁免用(正式工具不加開關)。
- **不做**:非 Python 程式的定義名與旗標(非 Python 程式檔只看路徑類;印一行「這次有 N 支非 Python 程式檔改動,只看路徑」);`drift scan` 與健檢(doctor)跑舊句檢查(只有一棵樹,判不了消失);考試(`drift exam`,含 `--history`)跑 `m1`(考卷沒有這種題,另案);「新增程式檔喚醒否定句」(W,另案只提醒);常數改值(V)、新寫行提到找不到的名稱(P5/P6)、全歷史定義索引——實驗判定不做。
- **前置**:工具鏈自己的推送前掛鉤與 CI 要先接上 `drift check`([[Projects/存量漂移防線_計劃]]〈做法〉第 4 節,代碼審 `code-推送閘接漂移檢查` 在跑);沒接上,工具鏈這邊兩週沒有帳,REVISIT 只剩 rtb 的數。

## 做法

### 1. 抽「這次消失的名稱」

- **起點與終點**:用 `drift check` 算好的那一對(`_note_audit_resolve` 回的),分三種:
  - `_note_audit_resolve` 第二個值是整數(`_lens_push_base` 判「頂端已在主線上、沒有新東西」、淺層 clone、範圍寫錯等)→ 整支 check 在那裡就回了,`m1` 不跑,帳只有既有那筆 skipped;
  - 起點是空樹 → `_note_audit_resolve` 回的起點是 None。空樹來自 `_lens_push_base` 找不到主線(或範圍起點明寫空樹),而且沒有可截的上線點標記(有標記、而且標記在這條歷史上時,空樹會被截成上線點提交,照判,範圍是上線點以來的整段)。這時 `m1` 不判,印一行「舊句檢查:這次沒有起點版可比,不判」,不論 warn 或 block 都不影響回傳碼——拿空樹當起點,沒有任何名稱能「消失」;帳記 `skipped-no-base`。取捨寫在〈誠實界線〉;
  - 其他 → 照判。
  - 例:沒有上線點標記、也找不到主線的 repo 在新分支首推、old_sentence=block → 印那一行、`m1` 貢獻 rc 0。
- **程式檔範圍**(照參考實作 `Code.kind`,排除清單逐字照它的 `_excluded`):路徑開頭是 `docs/`、`governance/`;開頭或任何 `/` 之後出現 `node_modules/`、`bin/`、`obj/`、`dist/`、`build/`、`__pycache__/`、`.git/`(`_DELGUARD_EXCLUDE_DIRS`);結尾是 `package-lock.json`、`yarn.lock`、`pnpm-lock.yaml`(`_DELGUARD_EXCLUDE_LOCKFILES`);`.md`——這些都不算程式檔。其餘的:Python 檔 = `_drift_probe_is_py`(`.py`,或沒副檔名、首行 `#!` 含 python);其他程式檔 = `_nodehome_code_kind` 回 ext(副檔名在既有程式檔清單裡)或沒副檔名、首行是 `#!`。例:改 `governance/eval/retrieval_eval.py` → 不看;改 `scripts/lumos`(沒副檔名、`#!` 含 python)→ 當 Python 看;刪 `tools/run_all.sh` → 只看路徑。
- **改到的檔**:`git diff --name-status -z --no-renames 起點 終點`(參考實作的 repo 模式,改名看成刪加增)。新增的檔沒有起點版,不抽;刪掉的檔終點那一側是空集合;`.py` 改成別的副檔名 = 刪 `.py` 加一支別的檔。
- **抽定義**(Python 檔的起點版與終點版):`_drift_py_names(txt, m1=True)`——新參數,預設 False 時行為與回傳形狀都不變(probe 照舊);True 時照參考實作 `Code.py` 的 defs 與 flags:
  - 函式、類別(含 async、任何層,`ast.walk`);
  - 指派名照參考實作 `_assigns`:模組層與類別層(含巢狀類別)的 `Assign` 每個目標、`AnnAssign`(有沒有值都算)、tuple/list 拆包的每個名稱;模組層 `if`/`try`(含 else、except、finally)裡的指派遞迴收;函式裡的區域指派不收。例:`A_ONE, B_TWO = 1, 2`、`try: MAX_RETRY = 3` / `except …: MAX_RETRY = 4`、類別裡的 `field_x: int` 都收;
  - 旗標:任何 `add_argument(...)` 呼叫(`p.add_argument` 或裸的 `add_argument`)的位置參數裡、以 `--` 開頭的字串常數;
  - 回 (函式, 類別, 指派, 旗標) 四個集合;剖不動照既有同一組例外(SyntaxError、ValueError、MemoryError、RecursionError)回 None。
  - 讀內容一律 `_drift_decode`(utf-8-sig、解不開的位元組換掉,不丟例外)。例:位元組不是 UTF-8 的舊 latin-1 檔照剖、不會讓整支 check 當掉。
  - **太大不剖**:blob 超過 `_DRIFT_M1_PARSE_MAX_BYTES`(4 MB)不剖,當剖不動(ast 的尖峰記憶體約原始碼的 100–280 倍,併發席量 11.5 MB 的生成檔 3.2 GB;工具鏈主程式現在 2.2 MB、257 MB);印「N 支太大沒剖:<前 3 個路徑>」。
- **路徑類**(照參考實作 `disappeared` 的路徑段):這次被刪的程式檔(Python 與其他程式檔都算;改名因為 `--no-renames` 也算刪)的舊路徑算消失;它的檔名只有在**終點樹任何位置(所有檔,不限程式檔)都沒有同名檔**時才算消失。例:刪 `pkg_a/util.py`、終點還有 `pkg_b/util.py` → 只有 `pkg_a/util.py` 算消失,`util.py` 不算;刪 `tools/run_all.sh`、終點沒有別的 `run_all.sh` → 兩個都算。
- **形狀過濾**(照參考實作 `_shape_ok` 逐字):以 `--` 開頭、含 `/`、或以 `.py` 結尾的直接過;其他要 4 個字以上,而且含底線、或同時有大寫與小寫字母(任一個大寫加任一個小寫)。例:`Result`、`getUser`、`old_name` 過;`main`、`resolve`、`FOO`、`lumos`、`pre-push` 不過——沒副檔名的腳本檔名、沒底線的全小寫函式名都不會成為候選。
- **「消失」**:定義名與旗標 = 起點那支檔有、終點那支檔沒有,**而且終點語料所有 Python 檔的定義與旗標聯集裡也沒有**。終點語料 = 終點樹上照上面範圍判定的所有 Python 檔,**含測試檔**。例:把 `foo_bar` 從 `a.py` 搬到 `b.py` → 不算;搬進 `tests/test_x.py` 裡定義 → 也不算。
- **跟既有 `_DriftProbeTree` 的關係**:問題相近、語料不同,所以不共用那個類別,只共用底下的函式(PRIOR-ART 列的那些)。probe 的 `when-symbol:` 問「產品程式還有沒有定義」,只看非測試檔、只排除 docs/ 與 governance/,讀法是逐名稱在全文找;`m1` 問「筆記還能不能正當提到這個名稱」,任何 Python 檔(含測試)還定義著就不算消失,排除清單照參考實作多排除建置目錄與 lock 檔,而且要整份定義集合才能進快取。驗收數字是照 `m1` 這個語料量的。後果寫在〈誠實界線〉。
- **剖不動(或太大)**:改到的檔起點版或終點版任一邊剖不動 → 那支檔這次不抽候選(不能當成全部消失;參考實作如此),印「N 支剖不動」;終點語料裡剖不動的檔(不論這次有沒有改到)→ 別支檔抽出來的每個候選名稱用既有 `_drift_py_def_re(名稱, False)`(任何縮排的 def、class、async def;不縮排的 `名 =`、`名=1`、`名: 型別 = 值`)在那支檔裡找,旗標用「單引號或雙引號包住的 `--旗標`」找,找到就當還在。例:終點另一支剖不動的檔有 `old_name: Callable = handler` → `old_name` 不算消失;有 `p.add_argument('--foo')` → `--foo` 不算消失;註解裡的 `# def old_name` 不算定義(行首錨定),三引號字串裡行首的 `def old_name` 會被當成還在(寧可多認,漏報方向);反過來,剖不動的檔裡縮排的類別層指派、拆包指派、沒給值的型別標註文字比對認不到,那種名稱會被當成消失(誤報方向;正確性席量工具鏈與 rtb 頂端剖不動的 Python 檔都是 0 支)。
- **讀取**:起點與終點的內容編號從列檔拿(`_drift_oids`,各一次 ls-tree;同一個行程裡 core 列過的終點由 `_drift_list` 的行程內記憶直接給),`.py` 檔快取命中就不讀內容;沒命中的、以及沒副檔名的檔(要看首行才知道是不是 Python,快取不存「不是 Python」,所以每次都讀;工具鏈 14 支、rtb 7 支),一次 `_nodehome_cat_blobs` 照內容編號批次讀。筆記由 `m1` 自己用 `_drift_tree_env` 讀(終點與起點各一次):core 建好的那份在 `_drift_check_core` 裡、不回傳,改它的簽名會動到考試與歷史重放,所以不共用,多讀的一次算在 `m1` 自己的 30 秒裡。一次推送 `m1` 的 git 行程數不隨檔數成長:列檔 0–2、diff 1、程式檔批次讀 1–2、讀筆記 2。
- **定義快取**(照既有 `~/.cache/lumos/<名>/` 那一種持久快取;不用行程內字典,因為推送前掛鉤每次都是新行程):
  - 位置 `~/.cache/lumos/drift-defs/`:建目錄走 `_mkdir_trusted_under_home`,讀寫兩端都過 `_trusted_private_dir`(不過就當沒快取、也不寫;快取內容決定哪些名稱「還在」,被別人改得動就是一條繞過的路)。為什麼不放 git 目錄:專案裡沒有寫進 git 目錄的快取先例;內容編號本身就代表內容,不同 repo、不同工作樹共用同一份是對的。
  - 一個 blob 一支檔,檔名 `sha256("<內容編號>|schema<_DRIFT_M1_DEFS_SCHEMA>|py<主版號>.<次版號>")`,內容是那個 blob 的四個集合。抽法任何一次改動就把 `_DRIFT_M1_DEFS_SCHEMA` 加一,舊快取自然不命中;換 Python 主次版本同理。例:schema 從 1 改成 2 → 同一個 blob 不命中、重剖。
  - 剖不動與太大的不寫快取(記憶體不足、遞迴過深跟當時環境有關,每次重判)。
  - 每剖完一支就寫(同目錄 `mkstemp` 唯一暫存名、chmod 0600、`os.replace`,照 `_lens_cache_write`):時間到之前剖好的都留著,冷快取一次剖不完的 repo 每推一次往前推進。
  - 淘汰:保鮮 14 天看 mtime(照 bound-filter),讀不更新 mtime、讀不寫檔;每次 `m1` 開跑前刪掉目錄裡 mtime 超過 14 天的檔(照 `_note_audit_work_dir` 清舊檔的做法)。不設筆數上限:一支約 1 KB(工具鏈主程式那支二十多 KB),檔數跟 14 天內剖過的 blob 數成正比。
  - 併發:兩個推送同時寫同一支,內容相同、後替換的贏,不壞也不丟;讀到被刪或 JSON 壞的當沒命中、照剖。
  - CI 每次是新機器,永遠冷快取(實驗量冷跑:rtb 剖檔 2.7 秒、工具鏈 2.2 秒,批次讀 0.1 秒以內)。
- **時間**:`m1` 自己一個截止時間,從 `m1` 開始算 `_DRIFT_M1_BUDGET_SEC`(30 秒,模組常數),不吃 c1–c5/probe 剩下的。每次 git 呼叫前、每剖一支前、每掃一篇筆記前、每一批名稱正則前都看;正在跑的那一次不打斷(批次讀以剩下的時間為上限,剖檔最多多一支的時間)。推送前最壞總時間 = 60 + 30 秒,再加兩段各一次不可中斷的呼叫。

### 2. 找筆記裡的舊句(判法 P4r2,細節逐字照參考實作)

- **讀哪份**:被推送終點提交的圖譜,用 `_drift_tree_env`(utf-8-sig 解碼,帶 BOM 的筆記開頭欄位照樣切得出);判「家」要看起點樹的 about_code,起點那份也用它讀。讀不出(不是 UTF-8)的筆記:這次範圍改到的算判不了;沒改到的只印「N 篇筆記讀不出、沒掃」(跟 c1–c5 一樣只把改到的算判不了,不然一篇壞筆記會讓 block 的專案永遠推不動)。所有類型都掃(Projects、Systems、Issues、Verification,含 superseded)。
- **掃哪幾行**:`_notelines_regions` 的 body/summary/decisions;圍欄內(`_visible_lines` 挑掉的行)不掃;開頭欄位(about_code、related…)不掃。
- **名稱先篩**:照既有 `_DriftNames` 的做法(全文先切成集合查;帶 `-` `/` `.` 的名稱看每一段都在集合裡),把筆記裡根本沒出現的候選名稱先拿掉,剩下的才組一條交替正則逐行掃(邊界席量:不先篩時 1000 個名稱 4.8 秒、2 萬個 98 秒;整個模組被刪的那種推送先篩後通常只剩個位數)。**切詞要用 ASCII 的 `[A-Za-z0-9_]+`(參考實作 `Code.words` 同一種),不能直接用 `_DriftNames`**:它切的 `\w+` 在 Python 裡含中文字,「改了foo_bar函式」會切成一整段、`foo_bar` 查不到,先篩就把該列的名稱篩掉了。先篩後還剩超過 200 個名稱時,每 200 個組一條正則分批掃,每批開始前看時間(一篇筆記裡也能在批與批之間停下)。
- **整字**(照參考實作 `_mk_rx`,ASCII 識別字邊界):一般識別字前後不能緊接 ASCII 英數或底線;含 `-`、`/`、`.` 的(旗標、路徑、檔名)前面不能緊接 ASCII 英數、底線、`/`、`.`、`-`,後面不能緊接 ASCII 英數、底線、`-`。中文字緊貼照算提到;反引號內外都算。例:「改了foo_bar函式」→ 提到 `foo_bar`;`get_user_id` 不算提到 `get_user`;`other/foo.py` 不算提到 `foo.py`;`--dry-run-x` 不算提到 `--dry-run`。
- **撤除節不看**:
  - 撤除字樣逐字照參考實作 `RETIRE_WORDS`(12 個,子字串、大小寫照原樣比):撤除、撤掉、作廢、已失效、已過時、不是現況、被取代、已凍結、superseded、已結案、歷史紀錄、Superseded。否定逐字照 `NOT_YET`:`(尚未|還沒|未)(撤除|撤掉|作廢|失效|取代|凍結|結案)`,一行只要命中它,整行就不算撤除行(同一行另有真宣告也一樣)。
  - 撤除行 = 去掉開頭空白後第一個字是 `>`、`(` 或 `（`,含撤除字樣、不命中 NOT_YET。
  - ①節開頭:任何層級的小標題後第一個非空行是撤除行 → 整節連同子節不看。
  - ②節內宣告(r1 收窄):節內任何一行以 `>` 開頭的撤除行,**同一行還含範圍宣告字(下面、以下、本節、這一節、整篇、之後)**,才從那一行到節尾(下一個同層或更高層標題之前,含子節)不看;在一級標題底下就是到整篇尾。例:`> 下面凡是講 --restore 的段落都是寫檔版的歷史紀錄` → 從這行起不看;`> golden 已凍結,…`(沒有範圍宣告字)→ 不觸發,後面照掃;`> 撤除 hook 一刀刪炸掉…` → 不觸發。
- **句內歷史字眼不列**(照參考實作 `_clause_has_hist` 逐字):
  - 「那一句」:名稱落在某對括號(`(` 或 `（` 開、`)` 或 `）` 關)裡 → 只看包住它的最內層那對的內容;行裡有沒關上的 `(` 在名稱前面 → 從那個 `(` 到行尾當括號內容;名稱在括號外 → 先把「裡面沒有括號的括號對」整對遮掉(只遮一層,巢狀的外層留著),再用 `。` `;` `；` `!` `?` `！` `？` 切,取名稱所在那一段。英文句點不切(名稱與路徑常含 `.`)。
  - 例:`現況:foo_bar_x 還在用(含 (內) 曾改過)` → 只遮掉 `(內)`,外層括號的「曾」跟名稱同一段 → 不列(參考實作如此,測試釘住);`old style removed. foo_bar_x is used now` → 英文句點不切,`removed` 同一句 → 不列;`foo_bar_x 還在用。原本叫 x` → 句號切開 → 照列。
  - 字眼表 `_DRIFT_M1_HIST_WORDS` 是一個模組常數,逐字寫出 54 個:符號檢查否定詞 26 個(零命中、已移除、不存在、查無、已刪、從未、已退役、移除、無此、原記、舊名、改名、已改、棄用、不使用、廢棄、停用、未使用、dead、removed、deleted、no longer、renamed、deprecated、unused、obsolete)+ 25 個(撤除、撤掉、拿掉、原寫、原本、原先、不再、舊版、舊的、刪除、刪掉、取代、搬到、搬去、改為、改叫、改成、曾、前身、撤、刪、拔掉、去掉、不帶、沒有)+ 3 個詞組(當時叫、擴成、改名為;不收單字「叫」,知識庫含「呼叫」的行有 748 行)。**不引用 `NEG_LEXICONS["zh"]`**:那份給符號檢查用,日後可能為它自己的理由增減,`m1` 的準度是對這 54 個量的。ASCII 字眼整字比,中文照子字串比。測試逐項釘 54 個。
  - 同一行同一名稱出現好幾次,各判各的,有一次沒被過濾就算提到;一行提到好幾個名稱,名稱集合只帶沒被過濾的那些。
- **一筆 = 一行**,帶名稱集合,每個名稱記著它原本在哪支檔(起點路徑)。
- **分層**(照參考實作 `homes_any`):那一行所在的筆記是「這次改到的任何一支程式檔(Python 與其他程式檔;改名的新舊兩條路徑都算)」的家——起點樹或終點樹任一邊的 about_code 列了它——或那一行在摘要 → 要處理;其他 → 只列出。例:同一個提交刪掉 `a.py`、也順手把家筆記 about_code 裡的 `a.py` 刪掉 → 起點樹還列著 → 那篇仍是家、那行仍是要處理。

### 3. 接進 drift check

- **判定函式** `_drift_old_sentence_check(root, base, tip, vault_rel, deadline)` → 一個 dict:要處理、只列出、判不了的原因、剖不動支數、太大支數、讀不出的筆記篇數、候選名稱數、非 Python 程式檔支數、狀態,值只有五種:`done`(跑完)、`timeout`(時間到)、`git-failed`(git 列檔、diff 或批次讀失敗)、`unreadable`(範圍改到的筆記讀不出)、`no-base`(起點是空樹);另外有起點但沒有候選名稱時回 `no-candidates`(不印、不記帳)。候選名稱 = 過了形狀過濾與「消失」判定之後、筆記先篩之前的名稱;它是空的就是 `no-candidates`。不印、不寫帳;`_drift_check_core`、考試、歷史重放都不動。
- **`cmd_drift_check` 的結構**(既有三個提早回傳改成往下走):
  - `LUMOS_SKIP_DRIFT_CHECK=1`、淺層 clone、範圍解析失敗 → 照舊整支回,`m1` 也不跑(跟著既有那筆跳過帳);
  - 讀 `_drift_config` 拿到 gate 與 old_sentence;
  - gate=off → 印原來那句、不跑 c1–c5/probe,`rc_core` = 0;否則照舊跑 core、印只列出,要處理或判不了有東西才進 `_drift_report_must`(那支不動),其回傳就是 `rc_core`;
  - old_sentence=off → `rc_m1` = 0;否則 `rc_m1` = `m1` 自己印、自己記帳的回傳;
  - 回傳 `max(rc_core, rc_m1)`。
  - 例:c1–c5 乾淨、`m1` 要處理 1 筆、old_sentence=block → rc 1(既有「要處理與判不了都空就回 0」那行不能擋在 `m1` 前面);c1 要處理 1 筆且 gate=block、`m1` 乾淨 → rc 1;gate=off、old_sentence=warn、`m1` 要處理 3 筆 → rc 0。
- **`_drift_config`** 回 (gate, 提醒, explicit, old_sentence)。old_sentence 跟 gate 各自解析、互不牽連,在 gate 的提早回傳之前讀:沒設定檔、JSON 壞、沒有 drift_check、drift_check 不是物件 → warn;有 drift_check 但沒寫 old_sentence 或寫 null → warn;寫了 block/warn/off 以外的值 → warn,並多一句提醒「drift_check.old_sentence 只能是 block/warn/off,你寫的是 'on',照預設 warn」。例:`{"drift_check": {"old_sentence": "block"}}` → gate warn、old_sentence block;`{"drift_check": {"gate": "blcok", "old_sentence": "block"}}` → gate warn 加提醒、old_sentence 照樣 block。兩個呼叫端(`cmd_drift_check`、doctor 的 `_drift_gate_doctor_lines`)與測試裡解包三個值的地方一起改;doctor 講開關的那行多講 old_sentence 的值。
- **印出**(`m1` 自己一支,重用既有印法):
  - 標題:`舊句檢查:這次推送消失了 N 個名稱,筆記裡還在講的——要處理 A 筆、只列出 B 筆(drift_check.old_sentence=warn,不擋)`;
  - 每筆用 `_drift_print_findings`:`[m1 程式改了、筆記還在講舊東西] 路徑:行  原文`,下一行 why =「消失的名稱:`foo_bar`(原本在 a.py)、`--restore`(原本在 scripts/x.py)」;`m1` 的發現不帶 prev_ack、不借 `_drift_old_reason`(那支只比原文與種類,樣板句會借到別篇的理由);
  - 改法經 `_drift_print_hints`:去重鍵 `m1` 用 (種類, 路徑, 行, 名稱集合);`m1` 那條不截在 300 字(上限 4000 字,名稱多到超過就只印「名稱太多,先改寫這一行」);
  - 另印「N 支剖不動、M 支太大沒剖、K 篇筆記讀不出沒掃、這次有 J 支非 Python 程式檔改動(只看路徑)」;
  - 判不了(時間到、git 失敗、範圍改到的筆記讀不出):warn 印「舊句檢查這次沒跑完(時間到)」、不算要處理;block 算要處理,印跟 `_drift_report_must` 同一句(「判不了就放行等於一條繞過的路…`LUMOS_SKIP_DRIFT_CHECK=1 git push`」;那句抽成一支共用函式兩邊呼叫)。
  - `_drift_report_must` 本身不動:`m1` 不進 must,它那行通用表態句本來就碰不到 `m1`。
- **提示**:`_drift_fix_hint(kind, path, line, names=None)`,`m1` 回「改寫或刪掉這句;確定照留就 `lumos drift ack <節點> <行號> --kind m1 --name=<名稱1> --name=<名稱2> --reason "<為什麼照留>"`」。節點照既有 `_drift_sh(…, node=True)`;每個名稱整段 `--name=<名稱>` 過 `_drift_sh`——一律用等號寫法,因為旗標類名稱本身以 `--` 開頭,`--name --restore` 會被 argparse 當成少一個值、回 2。例:名稱 `--restore` → 印 `--name=--restore`,照貼 rc 0;名稱 `src/x;y.py` → 印 `'--name=src/x;y.py'`,shell 不會切參數或執行後半段。
- **種類登記**:`_DRIFT_KINDS`、`_DRIFT_KIND_NAMES` 加 `m1`(名稱「程式改了、筆記還在講舊東西」);新增子集常數 `_DRIFT_SCAN_KINDS`(`_DRIFT_KINDS` 去掉 `m1`,照 `_DRIFT_FIX_KINDS` 的先例),`_drift_scan_print` 的計數、標頭條件、逐種類迴圈改用它,不在各處補 `!= "m1"`;doctor 那段本來就寫死 c1–c5,不動;`_DRIFT_FIX_KINDS`、`_DRIFT_FIX_ALLOWED` 不動(`drift fix … --kind m1` 照既有訊息回 2);ack 的 choices 用全集。
- **表態**:
  - `drift ack --kind m1` 要至少一個 `--name`(可重複);每個值去頭尾空白後 1 到 200 字、過 `_drift_one_line`;別的種類帶 `--name` 回 2;`_drift_ack_args_err` 多一個名稱參數。
  - 寫入:表態檔那一行多一個 `names` 欄(排序去重的清單)。`m1` 不驗那一行現在真的是 `m1`(判定要範圍,ack 只有一棵樹),不走 `_drift_current_finding`、不寫 related;`drift fix --keep` 經 `cmd_drift_ack` 寫 c2 時名稱傳 None。
  - 比對:`_drift_split_acked` 另開一條 `m1` 分支(`m1` 不放進 `_DRIFT_BOUND_KINDS`):同路徑、同原文(去頭尾空白)、kind `m1` 的**所有**表態,names 取聯集;一筆發現的名稱集合是聯集的子集才算已表態。沒有 names 欄或是空清單的 `m1` 表態不涵蓋任何名稱。要處理與只列出兩層都過這條分支。取聯集、不照 c2/c3 只看最新的理由:c2/c3 綁的是「當時連著哪些已收尾計劃」,之後才收尾的計劃要重新表態;`m1` 的名稱一旦為這一句原文表態過就不會變,原文一改鍵就換了。例:一行提到 A、B → 先 `--name=A`、再另一次 `--name=B` → 已表態;之後推送讓 C 也消失、同一行也提到 C → {A,B,C} 不是子集 → 照列。
- **治理帳**(照既有閘的慣例):
  - 有候選名稱、或沒有起點時才記;這次沒改到程式檔、或有起點但沒有任何名稱消失 → 不印、不記(那不是一次判定,記了只會讓每次純文件推送多一行)。有候選名稱就算零筆也記(照 nodehome-check 每次記 passed、delguard 每次記 ok 的先例);沒有起點記一筆 `skipped-no-base`,帳上才看得出 `m1` 那次沒判。
  - gate `drift-check`;kind 用既有結果詞:要處理 0(只列出幾筆都一樣)→ `passed`;要處理有東西、warn → `warned`;block 而且要處理或判不了有東西 → `blocked`、`hard=True`;warn 而且判不了 → `warned`;沒起點 → `skipped-no-base`(`skipped` 開頭,「閘的動作」統計認得)。
  - `head_sha` 明傳終點(不讓 `_gate_event` 自己跑 `git rev-parse HEAD`——多 ref 推送或 `--diff A..B` 時兩者不同);`nodes` = 要處理那幾篇(去掉 .md,最多 50,跟既有 drift-check 同一種寫法;warned 事件因此進得了 `gov --nags` 的空轉偵測);note 一句摘要「舊句檢查:要處理 A、只列出 B、剖不動 K」;`extra` = `{"check": "old-sentence", "state": 上面五種之一, "base_sha": 起點(no-base 時是空字串), "handle": A, "listed": B, "unparsable": K, "rows": […]}`,rows 是要處理全部(最多 200)加只列出前 50,每筆 `{path, line, layer, names, text}`,layer 是 `handle`(要處理)或 `list`(只列出),text 過 `_esc_clean` 取前 200 字。git-failed、unreadable 在 warn 記 `warned`、在 block 記 `blocked`(跟 timeout 同一種「判不了」)。
  - 每次有候選名稱的推送,`docs/.governance-log.jsonl` 會多一行還沒提交的改動——跟既有推送前事件(delguard 的 ok、drift-check 的 acked)同一種性質,下一次提交帶走,不另處理。
- **終端與帳**:筆記路徑、原文、名稱印出與寫帳前過 `_esc_clean`;給人照貼的 shell 參數另過 `_drift_sh`(`_esc_clean` 只換控制字元,管不到 shell)。

### 4. 兩週量準度(REVISIT 那天照做)

- **資料**:工具鏈 `grep '"check": "old-sentence"' docs/.governance-log.jsonl`;rtb 那份請 rtb 會談回報同一個 grep 的輸出。state 是 `done` 的才進準度的分母;`timeout` 進完成率;`git-failed`、`unreadable`、`no-base` 各數一個數、另列。
- **「真」**:那一行在該事件的終點版(`git show <head_sha>:<圖譜>/<path>`)確實把消失的名稱當成現況在講,照著做會去找不存在的東西。歷史說明、新舊名對照、照抄判準的程式片段、只是撞到同一個英文字 → 假。判不出 → 灰色,不進分子也不進分母,另列。
- **單位與分子分母**:要處理層的 rows 對 (路徑, 原文) 去重——同一句沒改、每次推送都會再列,只算一次;準度 = 真 ÷(真 + 假)。只列出層另算一個數給人參考,不進 RETIRE-IF。單次筆數看 `extra.handle`。
- **抽判**:去重後 30 筆以內全判;超過 30 筆用 `random.Random(20261014).sample(sorted(去重後), 30)`。
- **完成率**:時間到的比例 = state 是 timeout 的筆數 ÷(done + timeout)。
- **漏報與豁免**用參考實作量,正式工具不加開關:實驗程式已有子命令——`python3.14 governance/eval/drift-exam/old-sentence/old_sentence_exp.py revisit --repo <repo> --vault <圖譜> --pairs <檔> --out <json>`,`--pairs` 每行一組 `<base_sha>..<head_sha>`(從帳的 `extra.base_sha` 與 `head_sha` 抽;no-base 的不抽),對每一組輸出:P4r3 的命中、把句內字眼過濾關掉多出來的行(P4r3c)、把形狀過濾拿掉多出來的行(P4r3s)、終點圖譜只因撤除節②被豁免的行數與觸發行、帶否定或「撤除條件」字樣的撤除行。字眼過濾多出來的行照上面的抽判法判真假 → RETIRE-IF ④;形狀過濾與②豁免的數字記進計劃,單篇②豁免超過 100 行的逐篇看是不是真宣告。
- 同一個子命令順便數:終點圖譜裡撤除行帶「未被/沒有/沒被 + 撤除字樣」或「撤除條件」的行數(r1 在工具鏈與 rtb 的圖譜量都是 0 行)。

## 條款

(一條一支測試。S1–S7 是 r1 的編號沿用,S1 在 r1 鏡像核對後拆成 S1、S8–S11,另補 S12、S13。)

- [S1] 當推送範圍裡改到的 Python 檔有名稱在起點有、終點語料的所有 Python 檔都沒有定義(終點語料照參考實作的排除清單、含測試檔),工具應把它當成消失;例:`foo_bar` 從 `a.py` 搬到 `b.py` → 不算;搬進 `tests/test_x.py` 定義 → 不算;只剩 `governance/eval/x.py` 或 `build/x.py` 還定義著 → 算(那兩處不在語料裡);改到的只有 `governance/` 底下的檔 → 不抽候選 [test:t_drift_m1_disappeared_names]
- [S2] 當提到消失名稱的行在撤除節(節開頭撤除行;或節內 `>` 開頭、同一行含撤除字樣與範圍宣告字的撤除行之後到節尾),或名稱所在那一句(照參考實作的括號與切句規則)有 54 個字眼之一,工具應不列;例:`> 下面…都是寫檔版的歷史紀錄` 之後的行不列;`> golden 已凍結` 之後的行照列;`> 尚未撤除` 不算撤除;`現況:foo_bar_x 還在用(含 (內) 曾改過)` 不列;`foo_bar_x 還在用。原本叫 x` 照列;含「呼叫」的句子不因此被放過;54 個字眼逐項釘 [test:t_drift_m1_history_filters]
- [S3] 當 `m1` 那一行所在的筆記是改到的程式檔在起點或終點樹上的家,或那一行在摘要,應放要處理層,否則只列出;`m1` 自己的回傳(rc_m1)只看 old_sentence:warn 時要處理也是 0、block 時 1、off 時不跑,gate 是什麼都一樣;整支 check 回 max(既有那段, rc_m1)。固定「c1 要處理 1 筆、`m1` 要處理 1 筆」,四種組合:gate=off、old_sentence=warn → 0;gate=off、old_sentence=block → 1;gate=block、old_sentence=warn → 1(來自 c1);gate=block、old_sentence=off → 1 且 `m1` 沒跑。另外 c1–c5 乾淨、`m1` 要處理 1 筆、old_sentence=block → 1;設定只寫 `{"drift_check": {"old_sentence": "block"}}`、或 gate 寫壞而 old_sentence 寫 block 時照 block;old_sentence 寫壞值時照 warn 並提醒 [test:t_drift_m1_layers_and_mode]
- [S4] 當作者用 `drift ack --kind m1 --name=<名稱>…` 表態,工具應記路徑、原文、種類、名稱清單,同路徑同原文所有 `m1` 表態的名稱聯集涵蓋一筆發現的名稱集合才算已表態;例:先表態 A、再表態 B → {A,B} 已表態;新名稱 C 觸發同一行 → 照列;沒有 names 欄的舊表態不涵蓋;`--kind m1` 不帶 `--name`、`--name=` 空白、或別的種類帶 `--name` 回 2;照 `m1` 提示印出來的指令原樣貼上(名稱是 `--restore` 時)rc 0 [test:t_drift_m1_ack_binds_name]
- [S5] 當同一個 `.py` blob 第二次被剖(同一個 schema、同一個 Python 主次版本),工具應用 `~/.cache/lumos/drift-defs/` 的快取、不重剖也不讀那個 blob 的內容(沒副檔名的檔照讀首行,不在此列);schema 常數改了、或 Python 主次版本不同(版本由一支小函式取,測試換掉它)就不命中;剖不動的不寫快取;時間到之前剖好的已寫進快取(把 `_DRIFT_M1_BUDGET_SEC` 調小來造);快取目錄不可信、檔壞掉、讀寫失敗時當沒有快取照常跑;超過 14 天的檔開跑前刪掉;一次推送的 git 行程數在改到 3 支與 30 支 `.py` 檔時一樣 [test:t_drift_m1_defs_cache]
- [S6] 當 drift check 跑了 `m1` 而且有候選名稱(過了形狀過濾與消失判定、筆記先篩之前的名稱不是空的),或起點是空樹,應在治理帳記一筆(要處理零筆也記):gate `drift-check`、kind 為 passed / warned / blocked(block 帶 hard)/ skipped-no-base、`head_sha` 是被推送的終點、`extra.check` 是 old-sentence、`extra.state` 是 done / timeout / git-failed / unreadable / no-base 之一、帶起點、筆數與 rows(layer 是 handle 或 list);有起點但沒有候選名稱時不記;時間到時 warn 模式印明、不算要處理,block 模式算要處理 [test:t_drift_m1_events_and_budget]
- [S7] 當 `m1` 印改法,每個名稱應寫成過了 `_drift_sh` 的 `--name=<名稱>`,去重鍵帶名稱集合,不截在 300 字;名稱含分號、空白、`$()` 時照貼不會切參數或執行 [test:t_drift_m1_hint_paste_safe]
- [S8] 當 `_drift_py_names(txt, m1=True)` 剖一支 Python 檔,應回函式、類別、指派、旗標四個集合:指派含模組層與類別層的拆包、模組層 if/try(含 else、except、finally)裡的指派、有沒有值的型別標註,不含函式裡的區域指派;旗標是 `add_argument` 位置參數裡以 `--` 開頭的字串常數;例:`A_ONE, B_TWO = 1, 2`、`try: MAX_RETRY = 3`、類別裡 `field_x: int` 都在指派集合裡,`p.add_argument("--foo", dest="x")` 的 `--foo` 在旗標集合裡;`m1=False` 時回傳跟改之前逐字相同 [test:t_drift_m1_extract_defs]
- [S9] 當範圍裡有程式檔被刪(含 `--no-renames` 下的改名),工具應把舊路徑當消失,檔名只在終點樹任何位置都沒有同名檔時才當消失;所有候選名稱要過參考實作的形狀過濾;例:刪 `pkg_a/util.py`、終點還有 `pkg_b/util.py` → `pkg_a/util.py` 列、`util.py` 不列;刪 `tools/run_all.sh` 而沒有別的同名檔 → 兩個都列;`main`、`FOO`、`lumos`、`pre-push` 不成為候選,`Result`、`getUser`、`old_name`、`--restore`、`a/b` 成為候選 [test:t_drift_m1_paths_and_shape]
- [S10] 當筆記的一行提到候選名稱,工具應以 ASCII 識別字邊界判整字,中文緊貼算提到,名稱先篩用 ASCII 切詞,先篩後超過 200 個名稱分批掃;例:「改了foo_bar函式」→ 列(先篩也不能把它篩掉);`get_user_id` 不算提到 `get_user`;`other/foo.py` 不算提到 `foo.py`;`--dry-run-x` 不算提到 `--dry-run`;450 個候選名稱時組 3 批正則,把時間調到第 2 批前用完 → state 是 timeout [test:t_drift_m1_whole_word]
- [S11] 當起點是空樹、程式檔剖不動或太大、或筆記讀不出,工具應:起點空樹 → 不判、印明、rc_m1 為 0、帳記 skipped-no-base;改到的檔任一版剖不動 → 那支不抽候選、印「N 支剖不動」;終點語料裡剖不動的檔 → 用 `_drift_py_def_re` 與引號包住的 `--旗標` 文字比對,找得到就當還在(例:不縮排的 `old_name: Callable = h`、`add_argument('--foo')`);超過 4 MB 的 blob 不剖、印「N 支太大沒剖:<路徑>」;latin-1 位元組的舊檔照剖、check 不當掉;範圍改到的筆記讀不出 → 判不了(block 回 1),沒改到的讀不出 → 只印篇數、不影響 rc [test:t_drift_m1_unparsable_and_no_base]
- [S12] 當跑 `drift scan`、doctor 或 `drift exam`(含 `--history`),輸出與計數應不含 `m1`(scan 的計數與標頭沒有 m1 那一格);`drift fix … --kind m1` 回 2 並照既有訊息列出能用的種類 [test:t_drift_m1_not_in_scan]
- [S13] 當 `m1` 有要處理或只列出,工具應印標題「舊句檢查:這次推送消失了 N 個名稱,筆記裡還在講的——要處理 A 筆、只列出 B 筆(drift_check.old_sentence=<值>…)」,每筆一行 `[m1 程式改了、筆記還在講舊東西] 路徑:行  原文`、下一行「消失的名稱:<名稱>(原本在 <起點路徑>)…」,不印借來的舊表態理由 [test:t_drift_m1_output_text]

## 回退

- `m1` 是 `cmd_drift_check` 裡的一次呼叫加一支判定、一支印出:拿掉它們,並還原 `cmd_drift_check` 的提早回傳、`_drift_config` 的第四個回傳值(兩個呼叫端與測試一起)、`_drift_py_names` 的 `m1` 參數、`_drift_fix_hint` 的名稱參數與 `m1` 分支、`_drift_print_hints` 的 `m1` 去重鍵與長度上限、判不了那句的共用函式、`_DRIFT_KINDS`/`_DRIFT_KIND_NAMES` 的 `m1`、`_DRIFT_SCAN_KINDS` 與改用它的 `_drift_scan_print`(計數、標頭、迴圈還原成原本的寫法)、四個新常數(`_DRIFT_M1_DEFS_SCHEMA`、`_DRIFT_M1_PARSE_MAX_BYTES`、`_DRIFT_M1_BUDGET_SEC`、`_DRIFT_M1_HIST_WORDS`)與取 Python 版本的小函式、doctor 開關那行多講的 old_sentence、`_drift_split_acked` 的 `m1` 分支、`_drift_ack_args_err` 與 `cmd_drift_ack` 的名稱參數、argparse 的 `--name`;其他種類不受影響。參考實作的 P4r3、P4r3c、P4r3s 與 revisit 子命令可留可拿(P4r、P4r2 本來就沒動)。
- 已記的治理帳與表態留著:`_drift_load_acks` 會濾掉不認得的種類,舊版讀到 `m1` 表態行不出錯;治理帳的 kind 都是既有結果詞,`extra` 多的欄位舊版讀取端不看。
- 快取在 `~/.cache/lumos/drift-defs/`,不進版控,刪掉整個目錄即可;舊版完全不讀它。
- 主要路徑是 `git revert --no-commit <功能提交>` 後把共用帳本檔留在現況(同 [[Projects/漂移修法補強_計劃]]〈回退〉的做法),revert 提交照樣過代碼審閘。

## 實務隱患

- 已排除:不可逆:只讀程式與筆記、只印與記帳,不改任何筆記內容;還原提交後外面不用收拾(快取目錄刪掉即可)
- 已排除:金流:本機命令列工具,不碰付款或帳務
- 已排除:對外送出:不寄信、不打外部服務
- 守衛面(碰到):推送前多一種發現,預設只提醒;block 要專案自己設。誤報會讓人練出「看到就 ack」的習慣——兩週量準度就是為了這個;照貼表態會失敗也會把人推向整道略過,所以提示一律 `--name=` 並過 `_drift_sh`([S7])。開關讀被推送頂端的設定,同一個提交把 `old_sentence` 改成 off 就放過自己——跟 `drift_check.gate` 同一條既有取捨([[Systems/存量漂移守衛]] 的 RULE,2026-09-29),CI 那步照樣讀同一份,這條不另防
- 效能(碰到):`m1` 自己 30 秒;整次判定(讀樹、剖檔、掃筆記)冷快取一次推送 3.6–7.4 秒、有快取後約 0.3 秒(實驗量);其中只算剖檔的部分冷跑 rtb 2.7 秒、工具鏈 2.2 秒(併發席量);`m1` 自己再讀一次圖譜也算在這 30 秒裡;推送前最壞 60 + 30 秒再加不可中斷的呼叫。CI 永遠冷快取
- 記憶體(碰到):剖一支檔的尖峰約原始碼 100–280 倍,超過 4 MB 的不剖、改文字比對;推送前掛鉤行程被系統砍掉(接不到的記憶體不足)只可能出在 4 MB 以下的檔
- 併發(碰到):快取一個 blob 一支檔,兩個推送同時寫同一支內容相同、`os.replace` 原子替換、暫存名唯一;讀到壞檔當沒命中
- 資安(碰到):剖的是自己 repo 的程式碼(`ast.parse` 不執行);快取目錄讀寫兩端都驗擁有者與權限;筆記路徑、原文與名稱印到終端與寫進治理帳前過 `_esc_clean`,照貼的參數過 `_drift_sh`;`--name` 走一行檢查

## 誠實界線

- 定義名與旗標只看 Python;其他語言的程式只看被刪的路徑。其他語言的專案這道大半等於沒有;實驗沒量過非 Python 的誤報,不能套這裡的數字。
- 抓不到「數量或行為變了、句子沒寫名稱」的舊句(實驗 A2),也抓不到從沒在任何一版定義過就消失的名稱(A1 的 `held_rule`)。動態產生的定義(`globals()[n] = …`、`setattr`)、不是 `add_argument` 字串常數的旗標(變數、`*names`、click/typer)都不認:起點端不認 → 不會成為候選(漏報);終點改成動態註冊 → 靜態定義消失、名稱其實還在(誤報)。準度抽判時把誤報按原因分類,看這類占多少。
- 形狀過濾讓沒底線的全小寫短名(`main`、`resolve`)、全大寫無底線(`FOO`)、沒副檔名的腳本檔名(`lumos`、`pre-push`)永遠不會被檢查:工具鏈主程式 1185 個函式與類別裡 43 個(3.6%)、連測試檔 3076 個裡 311 個(10.1%)在這一類(外家否決席量)。r1 量拿掉它多出的 66 筆全是撞英文字,所以保留;兩週後用 revisit 子命令再數一次。反過來,「大小寫混合」照參考實作是「任一大寫加任一小寫」,`Result`、`Config` 這種首字大寫的英文單字也算,英文為主的圖譜會多撞名(中文圖譜的兩份資料沒踩到)。
- 排除 `governance/` 與 `docs/` 底下的程式:評測腳本改名或刪定義後的舊句看不到(r1 量到一筆真的:`governance/eval/retrieval_eval.py` 拿掉 `_macro_on`,`Systems/retrieval-ranking` 摘要還寫著)。要納進來就重跑驗收數字、另案。
- 同一個問題兩套語料:probe 的 `when-symbol:` 只看非測試檔,`m1` 含測試檔。只剩測試檔還定義的名稱,同一次推送 probe 判不存在、`m1` 判還在,是刻意的(見〈做法〉1)。
- 字眼表是在同一份考卷上調出來的,準度有樂觀偏差;兩週提醒期就是要量真實準度。中文字眼照子字串比,「沒有、刪、撤」這類短字會放過一些現況句(漏報,外家否決席舉的「沒有參數時呼叫 `old_handler`」就是一例);被放過的句子不進帳,所以 REVISIT 用 revisit 子命令把兩週的每一組範圍都重跑一次「關掉字眼過濾」、抽判多出來的,達 RETIRE-IF ④ 就不轉擋。撤除行的否定只認「尚未/還沒/未」緊接撤除字樣,「未被取代」「沒有作廢」「撤除條件」都會被當成撤除行;r1 在兩份圖譜量到 0 行,REVISIT 再數一次。
- 撤除節②收窄後仍有誤觸發:`Projects/主session鏡頭利用率_計劃` 那行「…撤掉兩次…本節以下是重寫版」讓 56 行不看;反過來,真宣告沒帶範圍宣告字的現在照掃(`Verification/2026-08-22_受波及合約測試真跑閘落地` 的「這篇已失效」,15 行,方向是多列、不是漏)。兩週帳看不到被豁免的句子,REVISIT 用 revisit 子命令數。
- 起點截到 drift check 的上線點:上線點之前刪的名稱看不到;範圍愈大,「先加後刪」在範圍內發生的機會愈多,那種名稱也看不到。有上線點標記的新分支首推,範圍是上線點以來的整段,候選多、最容易時間到。
- `m1` 的表態在 ack 當下不驗那一行真的是 `m1`,可以對任何一行先表態。
- `drift scan`、健檢與考試不跑:只有一棵樹時判不了「消失」;考試成績與噪音基準不含 `m1`。
- warn 模式時間到就放行,是刻意跟既有「判不了算要處理」相反;block 時照既有規矩算要處理,而時間到沒有表態的出路,只能 `LUMOS_SKIP_DRIFT_CHECK=1`(連 c1–c5 一起略過、會留帳)。所以 RETIRE-IF ③ 要求時間到的比例夠低才准把預設改成擋;快取剖到哪存到哪,本機會一次比一次快,但 CI 永遠冷,Python 原始碼大到 30 秒剖不完(約 100 MB 量級、CI 機器慢的話更小)的 repo 在 CI 上永遠跑不完。
- block 模式下兩種「沒判」待遇不同:時間到算要處理(擋),起點是空樹卻放行。空樹起點只出在找不到主線、又沒有可截的上線點標記的推送(例:還沒接遠端的本機 repo 開新分支),拿空樹比沒有任何名稱能「消失」,硬擋只會每次擋、沒有表態出路;代價是這種推送整段歷史裡「先加後刪」的舊句都看不到。CI 的 checkout 有主線可比,同一個範圍在 CI 照判,這是唯一的後盾;帳上 `skipped-no-base` 的次數 REVISIT 那天一起看。
- 預設改成擋的門檻(RETIRE-IF)跟 [[Systems/存量漂移守衛]] 那條「預設改 block 要三條全過」的 RULE 不同:那條管的是 `drift_check.gate`(c1–c5 與 probe,工具自己寫的固定句型、判得準),`m1` 有自己的開關、判的是人寫的散文,實驗 rtb 那 20 筆要處理裡 15 真、3 假、2 灰,要求「每筆都判成真」做不到;那條 RULE 也沒寫 `[confirmed:]`,不約束 `m1`。
- 剖檔上限 4 MB 是照量級定的:工具鏈主程式現在 2.2 MB,長過 4 MB 後,改到它的推送整支不抽候選(它本身的舊句全漏),別支檔的候選在它身上改走文字比對。回頭條件接在 `m1` 自己的輸出上:「N 支太大沒剖」那行帶路徑,工具鏈推送一印出 `scripts/lumos` 就重量剖檔記憶體、調上限。

## 合約候選

(實作後再判。)

## 審計修正紀錄

- 前掃(2026-09-30):首輪前掃查出 24 條(未定義詞 4、壞引用 2、範圍矛盾 6、機械宣稱語意落差 9 等),照改寫成本版;改前改後對照與動到核心裁定的 8 條見 `governance/review-reports/舊句檢查/r1-intake.md`,核心那 8 條交第一輪席位審。
- r1(2026-09-30,7 席):63 條/blocking 24/照字面實作會錯的全折(表態提示改 `--name=`、撤除節②收窄、`m1` 自己的 30 秒、快取改用 `~/.cache/lumos/` 帶版本鍵、範圍與路徑判準逐字照參考實作、治理帳用既有 kind 加 `extra.check`、準度量法寫死),形狀過濾量過拿掉多 66 筆全假而保留(附理由接受),另接受兩條照參考實作的小邊界。
- r1 鏡像核對(2026-09-30,17 條:折入只做一部分 3、前後說法打架 9、條款可測性 5):全補——撤除節②收窄與 revisit 子命令收進實驗程式成 P4r3(驗收改以它為準、重跑確認)、S1 拆成 S1 與 S8–S11 並補 S12、S13、S3 寫明只管 rc_m1 並列四種組合、S5 排除沒副檔名檔、state 值寫死五種、起點三種情況分開寫、補兩個月後的 REVISIT、〈回退〉補齊;逐條見 r1-intake.md〈鏡像核對〉。
- 卷證:`governance/review-reports/舊句檢查/`(r1-snapshot.md、七席報告、r1-intake.md 的〈席位收貨〉〈判讀〉〈機械重現〉〈處置〉〈鏡像核對〉)。
