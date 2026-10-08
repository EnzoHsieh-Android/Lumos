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
  - Systems/lumos-cli-write
  - Systems/guard-kill
  - Systems/delguard
related:
  - "[[Projects/存量漂移改法_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
  - "[[Projects/code側刪除傳播守衛_計劃]]"
---
# 漂移修法補強_計劃

白話:rtb 2026-09-30 用 `lumos drift fix` 把 26 筆漂移修到 0,回報五個工具不順的地方。這份計劃把它們補掉:c4 的卷證目錄找不到、c4 改完修復帳上沒紀錄、c1 的訊息把「已經改好」講得像出錯、c3 沒辦法寫理由、提交時刪除守衛把工具自己的檔當成專案程式而誤報。

依據:rtb 會談 2026-09-30 回報(跨會談訊息,逐條附了 rtb 的實際案例);Enzo 同日裁「照順序做」(先重新表態、再補這五條、再接推送閘)。★這份計劃翻掉同日較早的一條決定★:存量漂移改法代碼審 r4 後 Enzo 裁「c4 不自己寫檔、改走 lumos set」(記在 [[Systems/存量漂移守衛]] 的 PITFALL);rtb 實際用下來,走 set 修復帳沒有紀錄。這裡改成「c4 由 drift fix 寫,但寫法借 set 那套」,語法仍全由既有寫法決定、不回到自己判讀原文——實作時用 `lumos decision-add` 記這條翻案,並把那條 PITFALL 標成被取代。

PRIOR-ART: 全部借工具鏈裡現成的東西,不另起做法。①卷證目錄:專案規矩「程式、圖譜筆記、審查卷證放同一個提交」(過代碼審多一個只動帳本的提交,卷證仍在功能提交),所以驗證紀錄第一次被提交的那個提交裡一起加進來的卷證目錄是強線索;git 查詢借既有 `_plan_first_commit`、`_nodehome_git`、`_nodehome_split_z`。②c4 寫入:`lumos set` 整欄換掉那段拆成「驗值」與「算新開頭欄位」兩支不寫檔的共用函式,drift fix 用它們算改後內容,再走 drift fix 原本的乾淨檢查、鎖內寫入、寫後驗證、修復帳。③工具自己的檔:借既有 `_vendored_state`(讀索引時傳 `ref=""`,同筆記形狀擋的用法)與 `_is_toolchain_repo`。④佔位字與理由規則借既有 `_drift_placeholder_err`、`_drift_fix_reason_ok`。
RETIRE-IF: 上線兩個月後(以 REVISIT 那天為準):①工具鏈與 rtb 合計 c4 修復帳 ≥5 筆,而「同提交找到、計劃名比對找不到」的目錄一筆都沒有(帳上每筆記 `reports_same` 與 `reports_name` 兩份清單)→ 同提交找法沒帶來計劃名以外的東西,撤掉;②刪除守衛的治理事件裡「因工具檔跳過」累計 ≥20 次,而抽樣 5 次被跳過的名稱裡有任一個在圖譜裡確實指到已過期的舊說法 → 改回全比對、另找降噪法。
REVISIT:2026-11-30 量上面兩個數:①在工具鏈與 rtb 各跑 `python3 -c "import json;r=[json.loads(l) for l in open('governance/drift-fixes.jsonl') if l.strip()];c=[x for x in r if x.get('kind')=='c4'];print(len(c),sum(1 for x in c if set(x.get('reports_same',[]))-set(x.get('reports_name',[]))))"`(rtb 的帳由本工具鏈的會談用跨會談訊息請 rtb 會談回報);②`grep '"gate": "delguard"' docs/.governance-log.jsonl` 看跳過事件,抽 5 次被跳過的名稱用 `lumos search` 查

## 範圍

- **做**:①c4 證據頁的卷證目錄改成兩份來源(同提交、計劃名比對)都列、各自標來源,範本只自動填兩份都有的目錄;②`drift fix --kind c4 --values <各項…>`:用 set 的驗值與整欄算法算出改後內容,寫入前先擋會失敗的輸入,走 drift fix 的寫入流程並記修復帳;證據頁印的指令改成這一條;③c1 與 guard settle 把「已經是轉正後的說法」跟「真的找不到預告句」分開講;④c3 收 `--reason`,寫進補的那一行;⑤刪除守衛在消費專案跳過跟安裝清單一致的工具自裝檔,並記下跳過了幾支。
- **不做**:c4 的判定規則;`lumos set` 本身的行為(拆函式後照舊,訊息與檢查順序一字不變);把漂移檢查接進推送閘(另案,[[Projects/存量漂移防線_計劃]]〈做法〉第 4 節第 4 點);機制①(舊句偵測,[[Projects/舊句偵測實驗_計劃]])。

## 做法

### 1. c4 卷證目錄

- 取驗證紀錄第一次被提交的提交(`_plan_first_commit`;shallow 先由 `_git_is_shallow` 擋,既有);列那個提交加進來的檔:`_nodehome_git(root, "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)`,用 `_nodehome_split_z` 拆(`-z` 輸出不跳脫中文;`--format=` 去掉提交標頭;同每支檔有家那一段既有的「提交加了哪些檔」寫法)。只收路徑至少四段、形如 `governance/review-reports/<目錄>/<檔>` 的第三段目錄名,去重。這是「同提交」清單。
- 驗證紀錄改過名時 `_plan_first_commit` 回的是改名那個提交(`git log` 不跟改名),那個提交加進來的卷證目錄多半跟它無關——它們只會標「同提交」、不會被自動填進範本(範本只填兩者都有的)。
- 「計劃名」清單照舊用 `_drift_c4_key` 比對。
- 證據頁全部列出、每個標來源(兩者、同提交、計劃名),排序:兩者 → `code-` 開頭 → 其他,同級照字母。
- 範本句「代碼審見 …」只自動填標「兩者」的目錄;一個都沒有就放 `<卷證>`(照貼會被 `--values` 的佔位字檢查擋下,由人從清單挑)。同提交清單超過 3 個時另標「同提交,可能含別的計劃的卷證(整批匯入或壓成一個的提交)」。
- git 查詢在鎖外、判定步驟做完(同 drift fix 其他 git 查詢);git 失敗或逾時,同提交清單當空。
- 目錄名印到終端前過 `_esc_clean`;範本句與預填指令裡的各項都是整段交給 `_drift_sh` 當一個參數(不把範本句放進雙引號裡印),所以目錄名含 `$(…)`、反引號、空白時照貼也不會被 shell 展開或拆開。

### 2. c4 走 drift fix 寫入

- 拆 `_set_conditions_locked`(不改 set 的行為、訊息、檢查順序):
  - `_conditions_vals_err(key, vals, how) → (去空白後的 vals, 錯誤訊息)`:照原順序做佔位字(`_SET_COND_SLOT`)→ 空值 → 多行三道,不讀檔;錯誤訊息不帶「擋下:」前綴(呼叫端印),多行那句教人「要寫多條就給多個值」時用 `how` 帶入該用的指令(set 傳原本的 `lumos set <筆記> <欄位>`,drift fix 傳 `drift fix … --kind c4 --values`),其餘字一字不變。
  - `_conditions_rewrite(lines, e, key, vals) → (改後行, 錯誤訊息)`:算新開頭欄位那段;`fmt_scalar` 丟的 ValueError(同時有單雙引號或反斜線)轉成錯誤訊息回傳。
  - `_set_conditions_locked`:先 `_conditions_vals_err` → 讀檔 → `_conditions_rewrite` → 有錯就印「擋下:<訊息>」回 2 → 沒錯才 `atomic_write_verify`。印出來的字與順序跟拆前一樣(S3 用黃金字串比對)。
- `drift fix --kind c4` 接線:argparse 加 `--values`(`nargs="+"`)、`cmd_drift_fix` 的參數組裝加 `values`、`_DRIFT_FIX_OPTS` 加 `values`、`_DRIFT_FIX_ALLOWED["c4"] = {"values"}`、`_drift_fix_load` 的「c4 不做乾淨檢查」改成「c4 且沒帶 `--values`」、`_drift_fix_c4` 有 `--values` 時回 `res`(沒有時照舊回 `(None, None)`)、`_drift_fix_hint` 的 c4 說明改成指到 `--values`。
- 不帶 `--values`:只列證據與預填指令。各項用 `_conds` 展開(區塊寫法的多行值拆成各項,不併成一項);含三個關鍵詞的項放 `<整項新內容>`,其他照抄。指令不截斷;整條超過 2000 字或任一項含控制字元時,不印可照貼的指令,改逐項列出並說「請自己組指令」。最後加一行「筆記不乾淨或另一台是舊版工具:也可以用 `lumos set <節點> valid_under …`(不記修復帳)」。
- 帶 `--values`,寫入前依序擋(任一不過回 2、檔案不動,`--dry-run` 也照擋):①`_conditions_vals_err`;②每一項再過 `_drift_placeholder_err`(擋 `<卷證>`、`<sha>` 這類範本佔位字——不放進 `_conditions_vals_err`,否則 set 行為會變)與 `_drift_one_line`;③每一項不能含 `_DRIFT_UNCOMMITTED_WORDS`,訊息點名是第幾項、哪個詞(改寫成歷史說法時請避開這三個詞);④現在 valid_under 裡不含那三個詞的每一項,都要原文一字不差出現在 `--values` 裡——少了就擋,訊息列出少了哪幾項,說「要刪項目或有人剛改過這一欄:看過之後用 lumos set 整欄改」(避免整欄覆蓋把別人剛加的、或區塊寫法被拆開的項目靜默刪掉);⑤`_conditions_rewrite` 的錯誤。
- 過了才組 `res`:`check=lambda f: _conds(f.get("valid_under")) == vals`(用去空白後的 vals)、`handled=_drift_no_kind("c4")`、`extra={"template_used": 任一項等於範本句(去空白後), "reports_same": [...], "reports_name": [...]}`、`texts=[]`(開頭欄位不送筆記形狀擋,存量漂移改法設計時已定;上面①到③已擋空值、多行、分行字元、佔位字)。之後照 drift fix 原流程:乾淨檢查(帶 `--dry-run` 時不做,同既有慣例)→ `--dry-run` 到此 → 鎖內比指紋寫入 → 驗證磁碟內容等於算出的內容且 c4 消失 → 修復帳。
- `lumos set <節點> valid_under …` 照舊可用,不記修復帳。
- `--values` 的單一項以 `-` 開頭時 argparse 會當成選項:寫成 `--values=-x` 的形式;寫進誠實界線與指令文件。

### 3. c1 與 settle 的「找不到」訊息

- 不另設第二支判定:辨認式跟寫入端(`_guard_settle_rewrite` 寫出的轉正後字樣)用同一組字樣常數、放在同一段;settle 那一種的手補段落重用既有 `_GUARD_MANUAL_SETTLED_RE`。在 guard 區段 `_guard_settle_rewrite` 既有的「已處理」(seen)判定上,多認三種「轉正後說法」並另外回傳「已是轉正後說法」的種類集合——TEST:摘要區有 `TEST:[YYYY-MM-DD] 預告已轉正` 開頭的行;whynot:正文有「預告當時為什麼還不做:」開頭的行;settle:正文有「(YYYY-MM-DD 已轉正)」那一行,或正文任一行符合既有 `_GUARD_MANUAL_SETTLED_RE`(手補的已轉正段)。WHY 與 settle-del 既有判定已算 seen,不重寫。
- `_drift_fix_c1` 與 `guard settle` 印訊息時:已是轉正後說法的種類講「〈那一種〉已經是轉正後的說法,不用改」;真的找不到的才講「找不到〈那一種〉,可能被手改過,看一下」。兩處用同一支組字函式,「找不到」的字樣只留一處。

### 4. c3 的理由

- 接線:`_DRIFT_FIX_ALLOWED["c3"]` 加 `"reason"`;argparse `--reason` 的說明改成「c2、c3」。
- 規則沿用既有:長度與單行由 `_drift_fix_reason_ok`(`_drift_fix_args_err` 已對所有種類套用);佔位字由既有 `_drift_placeholder_err`(現在 c2 與 drift ack 在用),c3 也呼叫,不另包函式。理由先去頭尾空白。
- 補的那一行三種寫法(有 `--by` 且是 pass:「由 [[X]] 解決」;有 `--by` 其他狀態:「參考 [[X]]」;沒 `--by`)都一樣:有給理由就在最後接「;理由:<理由>」,沒給照舊。理由裡的 [[連結]] 不驗存在(同 c2 的 --reason)。

### 5. 刪除守衛跳過工具自裝檔

- 抽一支小函式 `_vendored_intact(root, ref)`:`frozenset() if _is_toolchain_repo(root) else _vendored_state(root, ref)[0]`——這個內嵌寫法已有三處(推送前小改動判定、筆記形狀擋兩處),一起改成呼叫它,行為不變。
- `cmd_delguard_check` 在取得 staged diff 之後、而且 diff 至少碰到一支 `_VENDORED_ALL` 裡的路徑時才做:在既有的剩餘時間判定(`_over()`)內取 `_vendored_intact(root, "")`(讀索引裡的檔與 `.lumos/vendored.json`;工具鏈本身回空集合),得到「跟安裝清單一致」的工具檔集合;超時或出錯照既有的降級路徑,不跳。
- `_delguard_parse_diff` 加 `skip` 參數(預設空集合),抽 `-` 行名稱與收 `+` 行回收表的兩遍都跳過它;`skip` 跟既有的 `_DELGUARD_*` 排除清單是兩回事,不併進去(那份清單有 `t_precommit_whitelist_drift_guard` 釘著)。
- 跳過了哪幾支、少抽了哪些名稱(最多列 20 個,超過寫總數),記在既有的 delguard 治理事件的 detail 裡(RETIRE-IF ② 要抽樣這些名稱)。
- 被改過的工具檔(跟清單不一致)、清單沒一起暫存(只 `git add scripts/`)照舊抽,寧可誤報不漏。

### 6. 文件與測試同步

- 文件:[[Systems/存量漂移守衛]] 的 c4 用法與那條「c4 不寫檔、改走 lumos set」的 PITFALL(標成被取代,補新說法)、[[Systems/lumos-cli-write]](拆函式、多行提示帶指令)、[[Systems/guard-kill]](settle 訊息)、[[Systems/delguard]](工具檔跳過與已知殘項)、lumos-project-notes 的 commands/04 c4 那一列。翻案用 `lumos decision-add` 記在存量漂移守衛。
- 既有測試 `t_drift_fix_c4_evidence_then_replace` 改寫:證據頁印的指令改成 `--values`;它同時釘著「set 擋 `<整項新內容>`」(lumos-cli-write 那條 WHY 綁它),那一段保留。

## 條款

- [S1] 當 c4 證據要列卷證目錄,工具應把同提交找到的與計劃名比對到的目錄都列出並標來源(兩者、同提交、計劃名),排序兩者、code- 開頭、其他;範本只自動填兩者都有的目錄,沒有就放 `<卷證>`;中文目錄名照原樣 [test:t_drift_c4_reports_from_first_commit]
- [S2] 當 `drift fix --kind c4` 帶 `--values`,工具應在寫入前擋下:set 的三道值檢查不過、含範本佔位字或分行字元、任一項還含「未提交/還沒提交/uncommitted」(點名第幾項哪個詞)、現有不含那三個詞的項沒有原文出現在 `--values` 裡(列出少了哪幾項)、整欄算法算不出來(例:同時有單雙引號)——都回 2 不寫檔,`--dry-run` 也照擋;過了才做乾淨檢查、鎖內寫入、寫後驗證、記一筆帶 reports_same、reports_name 的修復帳 [test:t_drift_fix_c4_values_writes_via_set_rewrite]
- [S7] 當 c4 證據頁印預填指令,工具應用 `_conds` 展開各項(區塊寫法的多行值拆成各項)、不截斷;整條超過 2000 字或任一項含控制字元時改逐項列出、不印可照貼的指令 [test:t_drift_c4_evidence_items_and_long]
- [S8] 當 `drift fix --kind c4` 帶 `--values` 而那一篇有不是 drift fix 留下的未提交改動,工具應被乾淨檢查擋下、不寫檔;`--values` 從命令列到 `cmd_drift_fix` 的參數要真的接上(帶了卻被當成只列證據就算錯) [test:t_drift_fix_c4_values_writes_via_set_rewrite]
- [S3] 當 `lumos set` 整欄改 valid_under/revalidate_when,各種錯誤輸入(含值錯又讀檔錯)印出的訊息與檢查順序應與拆函式前完全相同 [test:t_set_conditions_messages_unchanged]
- [S4] 當 c1 或 guard settle 找不到某種預告句而那一種已經是轉正後的說法,訊息應講「已經是轉正後的說法」;真的找不到時才講「找不到」 [test:t_drift_fix_c1_already_settled_message]
- [S5] 當 `drift fix --kind c3` 帶 `--reason`,補的那一行應以「;理由:<去頭尾空白的理由>」收尾(三種寫法都一樣);理由的長度、單行、佔位字規則與 c2 相同 [test:t_drift_fix_c3_reason]
- [S6] 當消費專案提交時 diff 碰到工具自裝檔、而且它跟索引裡的安裝清單一致,刪除守衛不應從它抽被刪名稱,並在治理事件記下跳過幾支;被改過的工具檔、清單沒暫存、工具鏈來源 repo 照舊抽 [test:t_delguard_skips_vendored_toolkit]

## 回退

- 卷證目錄:`_drift_c4_evidence` 改回只用計劃名比對;修復帳多出的 `reports_same`、`reports_name` 舊版會忽略。
- c4 寫入:拿掉 argparse 的 `--values`、參數組裝的 `values`、`_DRIFT_FIX_OPTS` 與 `_DRIFT_FIX_ALLOWED["c4"]`、`_drift_fix_load` 的條件改回 `kind != "c4"`、`_drift_fix_c4` 改回只回 `(None, None)`、`_drift_c4_print` 的指令改回 `lumos set`、`_drift_fix_hint` 的 c4 說明改回;`_conditions_vals_err`、`_conditions_rewrite` 可以留著(set 行為不變)。
- c1 與 settle 的訊息:`_guard_settle_rewrite` 多回的集合與組字函式拿掉,兩處訊息改回原字串。
- c3:`_DRIFT_FIX_ALLOWED["c3"]` 拿掉 `reason`、argparse 說明、`_drift_fix_c3` 的接法與佔位字呼叫。
- 刪除守衛:`skip` 參數預設空集合,呼叫端不傳即回到原行為;`_vendored_intact` 可以留著(三處既有呼叫行為不變);治理事件的 detail 欄位多的字拿掉。
- 測試:新測試一起拿掉;`t_drift_fix_c4_evidence_then_replace` 改回證據頁印 `lumos set` 的斷言(它同時釘 set 擋 `<整項新內容>`,那一段一直保留)。
- 文件:[[Systems/存量漂移守衛]] 的 c4 說明與那條被取代的 PITFALL、[[Systems/lumos-cli-write]]、[[Systems/guard-kill]]、[[Systems/delguard]] 的新句子、lumos-project-notes 的 commands/04 c4 那一列,一起改回;翻案決策用 `lumos decision-supersede` 撤。
- 已經用 `--values` 改過的筆記是一般筆記改動,修復帳上有紀錄;要退用 git 還原那些提交。

## 實務隱患

- 已排除:不可逆:只改本機筆記與修復帳,寫入前擋掉會失敗的輸入、乾淨檢查保證 git 退得回來,還原提交後外面不用收拾
- 已排除:金流:這是本機命令列工具,不碰任何付款或帳務
- 已排除:對外送出:不寄信、不打外部服務,git 指令只印給人看
- 守衛面(碰到):刪除守衛(只提醒不擋)在消費專案少抽工具自裝檔,跳過數記進治理事件;c1 與 settle 的訊息判定放在 guard 區段。被改過的工具檔照舊抽,寧可誤報不漏
- 資安(碰到):c4 的值走 set 既有的安全寫法;卷證目錄名印到終端前過 `_esc_clean`,印成照貼指令的參數走 `_drift_sh`
- 效能(碰到):卷證目錄要 `git log`(找第一次提交)加 `git show` 兩次 git 查詢,只在 c4 證據頁與 `--values` 寫入時跑,在鎖外、有逾時;刪除守衛的工具檔判定只在 diff 碰到工具檔時做,而且受既有剩餘時間限制
- 併發(碰到):c4 寫入走 drift fix 既有的鎖與指紋比對;證據頁到寫入之間有人改過 valid_under,由做法第 2 節第④道擋下

## 誠實界線

- 卷證目錄的同提交找法,前提是「程式、筆記、卷證放同一個提交」這條規矩有被遵守;驗證紀錄另外提交時同提交清單是空的,只剩計劃名比對。整批匯入或壓成一個的提交會帶出別的計劃的卷證,證據頁會標明,範本不會自動填它們。
- `lumos set` 直接改 valid_under 不記修復帳(set 是通用指令,不綁漂移);要記帳就走 drift fix 那條。先用 set 改了同一篇、沒提交,再對它跑別的 drift fix 會被乾淨檢查擋(檔跟 HEAD 不同、又不是修復帳留下的),要先提交。
- `--values` 的單一項以 `-` 開頭時要寫成 `--values=-x`(argparse 的限制)。
- 刪除守衛跳過工具檔,前提是安裝清單正確而且跟工具檔一起暫存;只暫存工具檔、沒暫存清單時照舊抽(誤報,不漏)。拆除工具鏈(把工具檔刪掉)的那個提交,索引裡已經沒有那些檔,不會跳過,照舊可能誤報。
REVISIT:2026-11-30 看有沒有拆除工具鏈或只暫存工具檔的提交被刪除守衛誤報的回報;有就改成也認「起點跟清單一致、這次被刪或改」的工具檔

## 合約候選

(實作後再判。)

## 審計修正紀錄

- 前置掃描(2026-09-30,便宜席):四項清單命中未定義 4、壞引用 0(2 條註記)、範圍矛盾 4、語意對不上 6;全部折入,對照表在 `governance/review-reports/漂移修法補強/r1-intake.md`。
- r1(2026-09-30,7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex):卷證在 `governance/review-reports/漂移修法補強/r1-*`,條數與處置見 r1-intake.md。
  - 結論:c4 寫入路徑的問題都在「寫完才驗」,改成寫入前擋五道(三個關鍵詞還在、範本佔位字、原本的項目不見、set 的值檢查、整欄算法算不出來),寫後驗證只剩把關(正確性 F2 F3 F4 F6、邊界 F1 F2 F3 F8、接手 F1 F2 F8、併發 F1 F2、回滾 F1);卷證目錄從「交集過濾」改成「全列標來源、範本只填兩者都有」(正確性 F1、外家否決 F1、邊界 F4);set 拆成先驗值、再讀檔、再算行,訊息與順序不變、前綴由呼叫端印、多行提示帶對的指令(正確性 F5、邊界 F9、架構對齊 F4)。
  - 其餘折入:接線點列全(參數組裝、c3 允許表、`_drift_fix_hint`、`_drift_fix_load` 條件;正確性 F7、接手 F3、邊界 F12、併發 F4);證據頁用 `_conds` 展開、不截斷(正確性 F8、邊界 F5 F6);c1 改成擴充 `_guard_settle_rewrite` 既有判定、辨認式收緊並限定區域、認手補段落(回滾 F5、接手 F9、邊界 F10、架構對齊 F3);c3 理由去空白、連結不驗(邊界 F11;佔位字不另包函式:架構對齊 F2);刪除守衛只在碰到工具檔時判、受剩餘時間限制、記跳過數、清單沒暫存寫進界線(併發 F5 F6、接手 F10、回滾 F6);lands_in 補 delguard(架構對齊 F1、正確性 F9、接手 F4、邊界 F13);翻案寫進依據、實作記決策(接手 F4);回退列全(回滾 F2、接手 F5);RETIRE-IF 改量得出來並附量法(回滾 F4、接手 F6);混版與 set 退路寫進證據頁與界線(回滾 F3、接手 F7);卷證目錄只收四段路徑(邊界 F7);git 查詢在鎖外(併發 F3);範本句與指令各項整段走 `_drift_sh`(邊界 F7);列提交檔案照既有寫法(架構對齊 F5);工具檔跳過抽成 `_vendored_intact`、三處既有內嵌一起收(架構對齊 F6)。
  - 鏡像核對(便宜席,材料含席報告目錄):51 條已處理 47、部分 4、未處理 0、相反 0;新矛盾 5、覆蓋缺口 2、引錯 1。已補:改名提交寫進找法(邊界 F4)、範本句整段走 `_drift_sh`(邊界 F7)、文件與測試同步另開第 6 節(接手 F4 F5)、dry-run 不做乾淨檢查、刪除守衛記被跳過的名稱、WHY 說法統一、回退補 `_vendored_intact`、佔位字函式現況說法、效能改成兩次 git 查詢、條款補 [S7][S8]、引錯改正。卷證 `governance/review-reports/漂移修法補強/r1-mirror.md`。
