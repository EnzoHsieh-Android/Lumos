severity: major

# r1 審查報告(鏡頭:資源與併發)

## F1 轉正日期的 `git log -S` 做法在正常情況下永遠找不到「正式行第一次出現」的提交
severity: major
blocking: 是 — 照字面實作,c1 的日期推算在最常見的轉正方式(同一提交把預告行換成正式行)下永遠推不出來,--date 變成必填,[S2] 的「從 git 推」等於沒有
引句:「所以做法是:取 `git log -S` 列出的提交(舊到新),逐一讀那個提交的家節點,用 `_guard_formal_line` 判正式行在不在,第一個在的那筆就是轉正日。」
file: `scripts/lumos:12086`(`_guard_settle_rewrite`)、`scripts/lumos:4067`(`PLANNED_RE`)、`scripts/lumos:4124`(`INV_TAG_RE`)
1. `git log -S<字串>` 只列出「該字串出現次數有增減」的提交。預告行(`KEY: ★INVARIANT-PLANNED★ <合約> [watch:][due:]`)換成正式行(`★INVARIANT★ <合約> [test:…]`)時,合約文字各出現一次,次數沒變,所以轉正那個提交不會出現在 `-S` 的清單裡。
2. 實驗(臨時目錄 git 倉):提交 1 寫預告行、提交 2 把同一句換成正式行(日期 09-23)、提交 3 改別處。`git log -S"合約甲乙丙" -- h.md` 只回提交 1。
3. 所以「逐一讀清單裡的提交、第一個有正式行的就是轉正日」:清單裡只有預告行的提交,沒有任何一個有正式行,結果永遠是「推不出來」,回頭擋下。只有「正式行是在別的提交、預告行已先被刪掉」這種少見順序才會命中,而且命中的是預告行被刪那筆,不是轉正那筆。
4. spec 認定「-S 會連預告行一起命中」是對的,但漏了另一半:它會漏掉轉正提交本身。〈實務隱患〉「取最早一筆」與〈誠實界線〉「推出來的是改寫那天」都沒有處理這個。
5. 改法要換成不靠次數增減的方式(例:`git log --format=%H --reverse -- <家節點>`,逐筆讀,第一個 `_guard_formal_line` 判為有的);同一支檔的路徑限定成本實測約 0.2 秒,不是問題。⚠ 這是實作者要選的做法,審查員只確認 -S 的字面做法不成立。

## F2 「先判定再上鎖」:判定用的筆記欄位是指令開頭載入的舊資料,兩個會談同修一篇會重複寫或蓋掉
severity: major
blocking: 是 — 照 §1 的順序(先確認是這種發現、再拿鎖寫)實作,第二個會談會在鎖外用舊快照過關,拿到鎖後對已被改過的筆記再改一次
引句:「先用跟 `drift scan` 同一支判定(`_drift_state_findings`,c1 在 `_drift_guard_findings`)確認「這一行現在確實是這一種發現」」
file: `scripts/lumos:26078`(`_drift_state_findings` 吃 `env.notes` 的欄位)、`scripts/lumos:12195`(`cmd_guard_settle`「狀態從磁碟重讀」的既有做法)、`scripts/lumos:37036`(main 分派時 env 已載入)
1. `_drift_state_findings` 的 status/type/plan_refs/valid_under 判斷讀 `env.notes[..].fields`,那是指令開頭 `Env` 載入的記憶體快照;`env_text` 雖然從磁碟讀全文,但欄位不是。所以 c3(要 status=pending)、c4(valid_under)、c2 的關係都是舊資料。
2. §1 把「確認種類」寫在「寫入一律拿鎖」之前,〈實務隱患·併發〉才說「鎖內重讀狀態(同 settle)」,兩處沒對起來;S9 的測試只釘 dry-run 與鎖存在,沒有「兩個程序同修一篇」的案例。
3. 重現:會談 A、B 同時對同一篇 c3 驗證紀錄跑 `drift fix --kind c3`(A 給 `--status superseded --by X`,B 給 `--status pass`)。兩者開頭都判成「現在是 c3」;A 先寫完,B 拿到鎖後若沿用舊判定,就把 status 改成 pass 並在正文再加一行「狀態改為 pass」,A 的決定被蓋、正文出現兩行互相矛盾的狀態說明,修復帳兩筆都記成功。c1 同理會重複補改(對已改寫的行是空操作,但帳照寫一筆「改前=改後」)。
4. 連帶的第二個洞:§1「寫完另外重讀整篇,再跑一次同一支判定,確認那一筆發現已經不在」——同一個 `env` 的 `notes` 欄位還是舊的,c3/c4 改的是欄位,重跑判定會永遠還看得到,c1 讀全文才看得到差別。spec 沒寫要重建 Env(或只重讀那一篇)。
5. 該補的合約:拿鎖後先從磁碟重讀那一篇、在鎖內重新判定「行號與種類仍成立」,不成立回 2(不寫、不寫帳);寫完後用重載的 Env 驗。⚠ `drift ack`(§6 要新增的 related 計算)有同一個順序問題:related 要在鎖內用重載的計劃狀態算,否則會記下已過期的清單。

## F3 整段(含 git)放在寫入鎖裡,鎖只有 30 秒過期、沒有心跳,也沒有 git 的期限
severity: major
blocking: 是 — 鎖被過期接手後兩個會談會同時做「讀—改—寫」,正是 S9 要防的事,而 spec 沒規定 git 動作放鎖外或設期限
引句:「寫入一律拿筆記庫寫入鎖(`_vault_write_lock`,可重入)、用 `atomic_write_verify` 寫;」
file: `scripts/lumos:14765`(`_vault_write_lock`,`_VAULT_LOCK_STALE_SEC = 30`)、`scripts/lumos:32781`(`_excl_lock_try`:只看鎖檔 mtime,沒有續租)
1. 鎖規則:別人拿著、鎖檔 mtime 不到 30 秒就等(每 0.05 秒重試,最多 60 秒後拋 RuntimeError);超過 30 秒就被原子接手,原持有者的 `finally` 只在鎖檔還是自己的程序編號時才刪,不會擋住接手者,也不會通知原持有者。持有期間沒有續租。
2. 鎖的設計前提是「一次筆記寫入不到一秒」(程式註解原話)。spec 把 c1 的日期推算(`git log` 加逐筆讀 blob)、c4 的證據搜尋(`git log --diff-filter=A`、掃 `governance/review-reports/` 目錄)、以及判定本身(`build_typed_index` 全圖譜)都沒指定放鎖內或鎖外,而 §2 的「repo 是 shallow 就擋」只是不算,沒有給 git 呼叫設 timeout;`drift scan` 自己有 `_DRIFT_BUDGET_SEC = 60` 的預算與「判不了」的處置,`drift fix` 沒有對應。
3. 兩種會踩到:①部分複製(partial clone、`--filter=blob:none`)時逐提交讀家節點會逐個向遠端補抓 blob,可以超過 30 秒;②git 卡在 `index.lock` 或慢速磁碟。任一種發生時,持鎖的 fix 還在跑,另一個 `lumos set/append/guard settle` 已經接手鎖並寫入同一篇,然後 fix 醒來寫入 → 後寫蓋先寫,而且訊息不會提醒。
4. 反過來,fix 持鎖超過 60 秒,其他會談的 set/append 會以 RuntimeError 失敗(所有筆記庫寫入者共用同一把鎖),spec 也沒說 `drift fix` 自己遇到 RuntimeError 怎麼收尾(既有 cmd_set 分派處有接,新的分支沒寫)。
5. 該補的合約:唯讀的證據與日期推算在鎖外做完(或給總預算與 git timeout,逾時當「推不出來」擋下),進鎖後只做「重讀、重判、改寫、記帳」;鎖內重判是 F2 的一部分。

## F4 筆記寫入與修復帳是兩次寫入,沒有規定順序與失敗處置;帳可能漏記而「事後找得回來」失效
severity: minor
blocking: 否 — 只在磁碟滿或 rc2 這類少見失敗時漏帳,筆記本身仍在 git 裡可還原,不會做出壞系統
引句:「每改一筆,往 `governance/drift-fixes.jsonl` 追加一行(借 `_jsonl_append_verified`,跟表態檔同一種寫法):」
file: `scripts/lumos:8511`(`_jsonl_append_verified`:寫不進或讀不回鍵都回 rc2)
1. 若先寫筆記、後追加帳:帳寫失敗時指令回 2,但筆記已改。重跑時判定已不是該種發現,依 §1 回 2「不是這一種」,帳永遠缺那筆,違背「事後找得回來」。
2. 若先追加帳、後寫筆記:筆記寫入失敗會留下一行「改了」的帳而筆記沒改,帳裡的紀錄是假的。
3. `_jsonl_append_verified` 需要一個唯一鍵,spec 只寫「id」,沒說怎麼產生(`drift ack` 用 `DACK-`+`secrets.token_hex(4)`);沒規定就可能有人用序號,兩個會談就撞鍵。
4. 帳檔放在 `governance/` 是否要提交、不同分支/工作樹各追加一行時合併衝突怎麼辦(既有 `drift-acks.jsonl` 沒有 merge=union 設定),spec 沒寫;多個會談各在自己的工作樹修 rtb 那 24 筆時會碰到。
5. 建議寫明:先寫筆記、後記帳,帳失敗時印出「筆記已改、帳沒記成」並附改前改後整段讓人補記;id 用 token。⚠ 是否設 merge=union 屬決策,審查員只指出 spec 沒交代。

## F5 `lumos set <Issue> status <結案>` 的回頭條件列出,用的是鎖外的舊 env,行號可能對不上
severity: minor
blocking: 否 — 只印不改,列錯行號的代價是人多看一眼
引句:「接在 main 分派處 `cmd_set` 成功之後(同計劃收尾時呼叫 `_drift_print_followups` 的位置;」
file: `scripts/lumos:37036`(main 分派 set 的位置)、`scripts/lumos:26193`(`_drift_print_followups` 吃指令開頭的 env)
1. 分派處的 `env` 在 `cmd_set` 拿鎖之前載入,列出時 `env_text` 從磁碟讀當下全文,但 `env.notes` 的欄位與 status 是舊的;另一會談在這段時間插了行,印出的「行號加原文」是新檔案的行號,但判斷「這篇是 Issue」用的是舊資料(此時對象若同時被改型別就會誤列,極少見)。
2. 列出發生在鎖外,兩次 `set` 連續下去時輸出交錯,但不影響寫入正確性。
3. 影響很小,列出來是因為 [S7] 的 test 只驗「列出行」,沒有驗行號與磁碟一致。

## F6 c2/c3 表態的 `related` 比對:同一發現有多筆表態時的語意沒定義
severity: minor
blocking: 否 — 只影響「重新列出」的時機;預設實作不會漏擋新情況,最多多列
引句:「表態帶 `related` 的,要現在的清單是它的子集才算對得上;現在多出新的收尾計劃就重新列出」
file: `scripts/lumos:27079`(`_drift_split_acked` 用集合、以 (路徑,原文,種類) 為鍵)
1. 現行 `_drift_split_acked` 把 acks 收成 key 集合,同鍵多筆(舊的沒 related、後來重新表態帶 related)會被合併。spec 沒寫多筆時是「任一筆對得上就算」還是「以最後一筆為準」。
2. 若「任一筆」:17 筆沒帶 `related` 的舊表態一旦與新表態同鍵,舊筆永遠對得上,重新列出的機制對該行永久失效(重新表態也救不回來)。若「最後一筆」:要新寫依檔案順序取最後一筆的邏輯,而 `_drift_load_acks` 讀 git 某提交的樹時順序是檔案順序,可行但要寫明。
3. 兩個會談同時對同一行 ack(鎖內序列化,兩筆都寫入)時同樣會產生同鍵多筆,語意要先定。

## 各節結論

### 範圍
已讀,無 finding。
引句:「⑦`drift fix` 每改一筆寫一行修復帳(改前改後),事後找得回來。」

### 做法 §1(入口)
見 F2、F3、F4。

### 做法 §2(c1)
見 F1;另 `_guard_settle_rewrite` 改成可刪行之後,`_guard_settle_record` 是先算好 `glines[:1]+fm+glines[ge:]` 再交給它、拿回整份 `new` 寫入,沒有任何後續依賴 1:1 行序的索引,所以刪行本身在併發面無問題。
引句:「`_guard_settle_rewrite` 現在是逐行一對一輸出,要改成可以刪行;settle 與 fix 共用這一支。」

### 做法 §3(c3)
已讀,無獨立 finding(併發面併入 F2:重複加一行狀態說明)。
引句:「正文最後加一行「YYYY-MM-DD 狀態改為 <值>(存量漂移 c3)」」

### 做法 §4(c4)
已讀,無獨立 finding。證據搜尋的成本:`git log --diff-filter=A -- <單檔>` 與目錄名比對都是單檔、單目錄操作,實測同量級約 0.2 秒;併入 F3 的期限問題。
引句:「不自動寫入:前提是人寫的判斷,工具只找證據。」

### 做法 §5(結案 Issue)
見 F5。E5 標記本身是純讀、多印一段字,無併發問題。
引句:「照樣列、照樣計數。標記對所有類型都做(計劃、驗證紀錄也會標),不只 Issue。」

### 做法 §6(表態綁關係)
見 F2 末句、F6。向後相容:`_drift_load_acks` 整行原樣回傳、只驗 path 與 kind(已核對 `scripts/lumos:27051`),舊版讀新欄位不會壞,〈實務隱患〉的宣稱屬實。
引句:「沒帶 `related` 的舊表態照舊只比路徑、原文、種類(2026-09-29 已寫的 17 筆不失效)。」

### 條款、回退、實務隱患、誠實界線
已讀。〈實務隱患·效能〉「一次只修一篇,git log -S 限定家節點一支檔」:單檔路徑限定成本實測約 0.2 秒(不限定時約 6 秒),宣稱在成本上屬實,但做法本身見 F1。不可逆、金流、對外送出:無,原因是只改版控裡的筆記與本機表態/帳檔。
引句:「併發(碰到)**:多個會談同時修同一篇。防法:寫入鎖、鎖內重讀狀態(同 settle)。」

最嚴重等級為需先修再實作;需改動才能實作的共 3 條,其餘不擋的共 3 條。
