severity: major

# 第 2 版 存量漂移改法 — 資源與併發鏡頭審查

## F1 `guard settle` 對 pass 節點「走同一支」時,git 查詢會落在寫入鎖裡
severity: major
blocking: 是 — 照字面實作,pass 補改句的 git 日期查詢在鎖內跑,違反 spec 自己為 30 秒接手訂的規則,會出現兩個會談同時寫同一篇
引句:「還有預告句就走第 2 節同一支(日期規則、前提檢查、不疊、修復帳 `via: guard settle`)」
file: `scripts/lumos:12195`
1. 現況 `cmd_guard_settle` 一進來就 `with _vault_write_lock(...)`,`_guard_settle_locked` 在鎖內才讀 status、才知道是 pass(`scripts/lumos:12204`)。
2. 第 3 節要求 pass 且有預告句時「走第 2 節同一支」;第 1 節第 1 步則規定 c1 的 git 查詢必須在鎖外,理由是 `_VAULT_LOCK_STALE_SEC` 是 30 秒(`scripts/lumos:14714`),鎖檔過 30 秒就被別人接手。
3. 第 3 節沒寫怎麼把「先讀狀態(要拿鎖才可靠)」與「git 放鎖外」接起來。照字面把第 2 節那支函式掛進 `_guard_settle_locked` 的 pass 分支,`git log -G` 加上「逐筆讀那個提交的那一篇」(每次呼叫上限 20 秒,見 `_lens_git`,`scripts/lumos:32017`)就全部跑在鎖內。
4. 超過 30 秒時另一個程序 rename 接手鎖檔,兩個程序同時進「讀-改-寫」,正是第 1 節要避免的情況。本 repo 實測單次 `git log -G` 0.3 秒,問題只在大 repo 或慢磁碟;但 spec 明確為此設計了鎖外查詢,settle 入口卻漏掉。
5. 缺的是:settle 入口要先在鎖外預讀 status/預告句判斷要不要日期、算日期,再進鎖重讀重判(與 drift fix 同一種兩段式),spec 沒寫。

## F2 c1 的「要不要日期」取決於鎖內才讀得到的內容,與第 1 節第 1 步的「鎖外先查」互相矛盾
severity: major
blocking: 是 — 兩種字面讀法各會做出錯行為(不該擋的擋下,或鎖內跑 git)
引句:「只有這次改寫真的要寫日期時才推——TEST、WHY 兩句與換成「(日期 已轉正)」的 settle 句要日期」
file: `scripts/lumos:12086`
1. 第 2 節:是否要日期取決於改寫內容——有沒有手補的「已轉正」段(下一個非空行比對)、預告句有哪幾種;「推不出也不擋」。
2. 第 1 節第 1 步:git 查詢在鎖外先做,「`--date` 格式錯在這一步就回 2」,c1「推不出」的出口在第 2 節第 3 點是回 2。
3. 鎖外那一步沒有經過鎖內重讀的內容,不知道要不要日期。若無條件先查:只需改「為什麼還不做:」、日期其實用不到的 c1,git 失敗(shallow、改名、20 秒逾時)會被擋下,違反「推不出也不擋」。若鎖外先讀檔決定:那份內容在等鎖(最長 60 秒)期間可能已被別人改過,決定是過期的;鎖內重判後發現要日期卻沒查,只能鎖內補查(回到 F1)。
4. spec 兩條路都沒選。實作者必須自己選,選錯就是「誤擋」或「鎖內跑 git」。

## F3 表態「以最新一筆為準」用檔案內順序判斷,多工作樹合併後順序不等於時間順序
severity: major
blocking: 是 — 多工作樹是 spec 自己承認的場景,合併後可能讓沒帶 `related` 的舊表態變成「最新」,新規則的保護靜默失效
引句:「★以最新一筆為準★(表態檔只追加不改,後寫的蓋前寫的)——最新一筆沒記 `related` 就照舊對得上」
file: `scripts/lumos:27051`
1. 現況 `_drift_load_acks` 回傳檔案原順序;`_drift_old_reason` 用 `reversed(acks)`,也就是靠檔案位置當時間。
2. spec 的前提「只追加不改,後寫的蓋前寫的」只在單一工作樹成立。第 1 節、實務隱患自己寫了「多個工作樹各自追加、合併時兩邊都加了行」。
3. 情境:工作樹 A 補了帶 `related` 的表態(今天);工作樹 B 更早寫過同鍵、沒帶 `related` 的表態,但 B 的分支較晚合進主線(或人手解衝突時把 B 的行排在後面)。合併後檔案順序是 A、B,B 那筆沒 `related` 成了「最新一筆」,就「照舊對得上」,A 的新保護被蓋掉,而且沒有任何提示。
4. 內建的 `date` 欄位只有到日,同一天無法排序;spec 沒說遇到同日或順序與日期相反時怎麼辦(例如排序鍵用 `(date, 檔案位置)`,或只要有一筆帶 `related` 就以那筆為準——但後者又會與 S8「以最新一筆為準」衝突,r1 為了 17 筆補記已經選了「最新」)。
5. 影響面:寫進「自我治理」段的說法「今天那 17 筆也補上(補的那筆是最新一筆)」只在單一序列成立。

## F4 spec 宣稱「照既有的 JSONL 聯集合併做法處理」,但既有做法涵蓋的不是這個場景
severity: major
blocking: 是 — 多會談各在工作樹修筆記,合併修復帳就會檔尾衝突,spec 沒有交代處理方式,卻說已有現成解法
引句:「照既有的 JSONL 聯集合併做法處理(`_pull_source_or_abort` 對簿記 JSONL 取聯集),跟治理帳、表態檔同一種風險與解法」
file: `scripts/lumos:17576`
file: `.gitattributes:1`
1. `_pull_source_or_abort`(`scripts/lumos:17576`)處理的是 `lumos update/install` 時「工具鏈來源 clone 工作目錄髒了簿記帳、要 `pull --ff-only`」,只在該來源 clone 上跑,不管使用者專案(rtb)兩個分支各自提交後的 `git merge`/`rebase`。
2. `.gitattributes` 只有 `*.ps1 text eol=CRLF` 一條,沒有 `merge=union`(我讀了整個檔)。兩個工作樹各往 `governance/drift-fixes.jsonl` 檔尾加行再提交,合併就是檔尾雙邊新增衝突。
3. 修復帳每行還帶「改前整篇原文」,一行數 KB,人手解衝突很容易解壞行(斷行、少行),接著會撞到 F7 的斷行問題。
4. 表態檔也一樣沒有,所以「跟表態檔同一種風險」是對的,但「同一種解法」不存在。spec 要嘛補 `merge=union` 或明寫不處理並附回頭看的條件,不能寫成已有解法。
5. 加進 `_BOOKKEEPING_FILES` 只影響代碼審留痕豁免與 pitfalls 排除,以及上述來源 clone 的聯集;與 rtb 內部合併無關。

## F5 鎖內「重讀重判」只換了目標那一篇,判定用到的其他筆記仍是等鎖前載入的舊 env
severity: major
blocking: 是 — S1/S9 宣稱鎖內重讀後重判擋得住兩個會談,c3 與 c1 前提檢查實際讀到的是等鎖前的舊狀態
引句:「讀檔後用 `_note_from_text` 重建那一篇的筆記物件、換進 env」
file: `scripts/lumos:36810`
file: `scripts/lumos:26031`
1. main 在分派前就 `env = Env(vault)`(`scripts/lumos:36810`),整個筆記庫此時一次載入;等鎖最長 60 秒(`scripts/lumos:14797` 起)。
2. c3 判定 `_drift_c3_hit` 讀的是 `env.notes[plan]` 的 status(`_drift_str(pn, "status")`)與 `build_typed_index(env)` 從 env 現建;只換 verification 那一篇,plans 仍是舊的。若另一個會談在這期間把計劃重開(`lumos set <計劃> status doing`),鎖內重判仍然說「計劃都收尾了」,會把驗證紀錄改成結案狀態並記帳。
3. c1 前提檢查(第 2 節)要看「家節點現在的摘要」;`_drift_guard_findings` 是用 `env.resolve(...)`(舊)找路徑、`env_text` 讀磁碟(新)——新舊混用;家節點若在等鎖期間被 `guard abandon` 或人手改掉正式行,只有讀到磁碟這半是新的。
4. 換進 env 的只有目標那一篇,`env._edges` 是快取(`scripts/lumos:660` 附近);如果之前有任何步驟碰過 `env.edges`,連結圖也是舊的(c2 表態用 `_drift_linked`)。
5. spec 的寫法要嘛改成鎖內整個 `Env(vault)` 重建(本 repo 586 篇實測載入 0.1 秒),要嘛明講哪些輸入允許是舊的。

## F6 `drift ack` 對 c2/c3 的「先確認當下發現、再記 related」沒有規定鎖範圍,現況只鎖 append
severity: minor
blocking: 否 — 競態方向是「多列」(舊清單比實際少一項,下次 check 會重新列出),不會漏擋
引句:「`drift ack --kind c2|c3`:寫入前先用 `_drift_state_findings` 算那一篇當下的發現,指定的行要真的是這一種發現」
file: `scripts/lumos:27138`
1. 現況 `cmd_drift_ack` 的鎖只包住 `_jsonl_append_verified`(`scripts/lumos:27138`);spec 新增的「算當下發現」寫在「寫入前」,沒說在鎖內還是鎖外,也沒說要不要重建 env(見 F5)。
2. 若照現況把新判定放在鎖外:算完到 append 之間別的會談改了計劃狀態,`related` 記的清單比真實少或多。少記的方向在下次 `drift check` 會被當成「多了新計劃」重新列出(安全方向);多記(計劃被重開)則表態涵蓋範圍偏大,`related` 是「現在的清單是它的子集」才算已表態,偏大不影響放行判斷。
3. 但 S9 寫「所有寫入應在筆記庫寫入鎖內、從磁碟重讀後重判」,而 ack 是這份 spec 新增的第二個寫入者,S9 的範圍卻沒把它納進去(S9 的測試只名 fix)。

## F7 修復帳沿用 `_jsonl_append_verified`:出現一行沒有換行結尾的殘行後,之後每次記帳都會驗證失敗,配合「帳失敗就還原筆記」變成 fix 全面卡死
severity: minor
blocking: 否 — 觸發需要殘行(磁碟滿、程序被殺、人手解衝突漏換行),平常不會遇到,但一旦遇到不會自癒
引句:「★帳寫不進去就把筆記還原成改前原文、回 2★:筆記改了、帳上沒有,事後就找不回來」
file: `scripts/lumos:8511`
1. `_jsonl_append_verified` 以 `"a"` 開檔直接寫 `json + "\n"`,不檢查檔尾是否已有換行。
2. 實測(臨時目錄):檔內最後一行 `{"id":"DFIX-bbbb","before":"半截`(無換行),再追加一筆,新內容被黏在殘行後面,讀回時該行 `json.loads` 失敗被跳過,回 2 並印「落盤自驗失敗」;檔案變成 `…半截{"id": "DFIX-cccc", ...}`。
3. 此後每次 fix 的記帳都失敗、每次都把筆記還原,使用者看到的是「帳寫不進去」,卻找不到原因。訊息還印「canary record」字樣(該函式的既有字串),對 drift fix 使用者是誤導。
4. 修復帳每行帶整篇原文(KB 級),比表態檔的一行 200 位元組更容易在寫到一半時出殘行;spec 用「同表態檔」帶過,沒處理。

## F8 「所有寫入在鎖內」不成立:多個改筆記的指令不拿鎖,鎖內還原整篇會蓋掉它們的寫入
severity: minor
blocking: 否 — 需要 drift fix 失敗還原與無鎖寫入者恰好重疊,窗口小;但 S9 的字面「所有寫入」不成立
引句:「所有寫入應在筆記庫寫入鎖內、從磁碟重讀後重判、原子寫入,寫完重讀並確認那一筆發現已不在」
file: `scripts/lumos:15476`
1. 全檔共 12 處 `with _vault_write_lock`,涵蓋 set/append/remove、guard plan/abandon/settle、記帳等;`cmd_decision_add`、`cmd_decision_supersede`、`cmd_new`、`guard bind` 等仍是直接 `atomic_write_verify` 的讀-改-寫、沒鎖(`_write_lf` 的說明也寫著「其他寫入指令仍是 last-write-wins」)。
2. 第 1 節第 5、6 步的還原是把「改前整篇原文」原子寫回。若在 fix 寫入後、重讀驗證前,無鎖的 `decision-add` 對同一篇寫了一筆(那一筆合法成功),失敗還原會整篇覆蓋,無聲丟掉那筆決策。
3. 這是既有限制,不是新缺口,但 spec 用「所有寫入」與「自驗失敗還原」兩句放大了它。至少要把 S9 的範圍限定成「drift fix 與 guard settle 自己的寫入」,或還原前比對磁碟現況是否還是自己剛寫的那份(用 `after_sha256`,回退節已經這樣做,還原路徑沒有)。

## F9 `--dry-run` 在拿著寫入鎖時印出改前改後
severity: minor
blocking: 否 — 只影響鎖的持有時間,結果不會錯
引句:「**算出改後內容**,`--dry-run` 印改前改後就回 0,不寫筆記也不寫帳。」
file: `scripts/lumos:14797`
1. 順序是第 2 步拿鎖、第 4 步 dry-run 印出。dry-run 不寫任何東西,卻仍持有獨占鎖;而「改前改後」是整篇,輸出量大。
2. 輸出接到 pager 或被慢終端擋住時,鎖持有超過 30 秒就被別的程序接手,別人接手後 dry-run 這邊釋放鎖時只刪自己的鎖檔(`scripts/lumos:14808` 起有檢查程序編號),不會刪別人的,所以不致破壞;但等鎖的其他寫入者最長 60 秒後會拋 RuntimeError(第 14797 行)。
3. 修法是 dry-run 先在鎖外算完再印,或印之前釋放鎖;spec 沒寫。

## 已讀,無 finding 的部分

### 第 5 節(結案 Issue 回頭條件)與 E5 標記
已讀,無 finding
引句:「用 `cmd_set` 寫完之後從磁碟重讀的內容算」
原因:`_issue_close_revisits` 在 cmd_set 鎖外、之後重讀磁碟,只印不擋不寫;極端下行號會因別人同時改而位移一兩行,屬提示精度,不影響狀態。

### 效能與預算(git log -S/-G 在大 repo 的成本)
已讀,無 finding(除 F1/F2 已指出的鎖內位置)
引句:「c1 的 git 查詢限定守衛紀錄一支檔,放在鎖外」
原因:實測在本 repo(2283 個提交)`git log --reverse -G "^status: pass" -- <單檔>` 約 0.29 秒、`--diff-filter=A` 0.09 秒;有路徑限定時成本跟該檔的提交數與歷史簡化有關,`_lens_git` 每次呼叫 20 秒逾時(`scripts/lumos:32017`)。`_plan_first_commit`(c4 用)沒有逾時(`scripts/lumos:5843`),但 c4 的查詢在鎖外,最壞是指令卡住、不影響別人。`_drift_state_findings` 全庫實測 6 毫秒、`Env` 全載 0.1 秒,鎖內重判成本可忽略。修復帳每次記帳讀回全檔,以每筆約 10KB、上千筆估算也是毫秒級。

### 不可逆與向後相容(併發面)
已讀,無 finding
引句:「不可逆(碰到,可還原):改的是版控裡的筆記,git 還原得回來;修復帳逐筆存改前原文,不靠 git 也找得回來」
原因:還原靠 `after_sha256` 比對,與併發面無新增缺口(F8 已提出還原路徑本身缺同樣比對);舊版寫表態覆蓋新保護已在 spec 自己列為界線。

最嚴重等級最高;blocking 共 5 條(F1、F2、F3、F4、F5),其餘 4 條為非阻擋。
