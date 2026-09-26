severity: major

## F1 撤回紀錄本身(kind=withdraw)沒有被排除在既有讀者的「一般逃逸列」處理之外,會讓 gov --stats、rule-gap 把撤回紀錄誤算成逃逸列
severity: major
blocking: 是,照 spec 字面實作,只要撤回過一筆逃逸,`lumos gov --stats`(S14 段)與 `lumos rule-gap` 的數字就會被撤回紀錄本身(不是被撤回的目標列)污染,操作者看到的「逃逸帳 N 筆」「風險不明 N 筆」「沒標規則 N 筆」都會虛高,而且沒有任何一條 S 條款測到這個情況。
引句:「統計類讀者(問閘尾漏斗、治理帳統計、escape-stats)用預設,**不算**被撤的列。」
file: `scripts/lumos:7397-7414` `_escape_rows_for` 目前逐行 `json.loads` 後原樣塞進 `out`,不看 `kind` 欄;spec 只加 `include_withdrawn` 這個參數來過濾「被撤的列(target)」,通篇沒有一句要求連撤回紀錄本身(`kind=="withdraw"`)也要從一般讀者的輸出裡拿掉。
file: `scripts/lumos:6619-6620` `_render_gov_stats` 對 `escapes=_escape_rows_for(env)` 直接做 `len(escapes)` 與 `max(e.get("severity","minor") for e in escapes)`——撤回紀錄沒有 `severity` 欄,會被 `get(...,"minor")` 補成假的 minor 值一起參與 `max()`,且被算進「逃逸帳 N 筆」的分母。
file: `scripts/lumos:2301-2309` `lumos doctor` S14 段對每個 `_e` 做 `_e.get("plan_risk")/_e.get("door")` 都不存在時,退回 `_door_for_loop(env, str(_e.get("loop","")))`——撤回紀錄沒有 `loop` 欄,`str(None)` 會查到一個叫「None」的迴圈(查不到,回 `unknown`),於是每一筆撤回紀錄都被算進「風險不明」按階段 `?`(`_e.get("stage")` 也不存在)的計數裡,印在 `lumos doctor` 的可見輸出上。
file: `scripts/lumos:20215-20239` `cmd_rule_gap` 完全不走 `_escape_rows_for`,自己逐行 `json.loads` 後直接 `ev.get("rule")`——撤回紀錄沒有 `rule` 欄,會被計進 `unlabeled += 1`(「沒標本來哪條規則該抓」),使 rule-gap 印出的「另有 N 筆沒標」數字含撤回紀錄本身,不是真正的逃逸列。spec §三第五點只講「套同一支『是不是被撤回』的判斷函式後再數」,同樣沒提到要先排除撤回紀錄自己這一種列。
本案 §三第二點(第 51-53 行)定義 `include_withdrawn` 只描述「被撤的列」這個維度,沒有描述「撤回紀錄自己算不算一般逃逸列」這個正交維度;S3 條款(「統計類讀者…都應不再算它」)的「它」讀起來也只指向被撤回的目標,不涵蓋撤回紀錄本身,測試 `t_escape_withdraw_hidden_from_stats_shown_in_list` 因此測不到這個缺口。

## F2 撤回紀錄的 `by` 欄位來源(`git user.name`)沒有規格,且 spec 自己宣稱的守衛(撤回一定要撤回者)沒有對應的擋下條件
severity: major
blocking: 是,repo 裡目前沒有任何一處讀 `git config user.name` 的既有程式碼(`grep -n "user.name" scripts/lumos` 零命中),spec 又沒交代查哪個 repo(`-C` 指到哪)、失敗/未設定時要不要擋下——若照 spec 唯一給出的擋下清單字面實作,`git config user.name` 沒設時 `by` 會靜默寫成空字串,直接違反 spec 自己在實務隱患段宣稱的守衛。
引句:「撤回一定要理由與撤回者」
file: `scripts/lumos:9257-9261` 對照既有慣例 `_git_head(repo_root)`:`subprocess.run` 失敗或非 0 就回 `""`,不擋、不報錯——若撤回的 `by` 欄比照這個慣例實作,`git config user.name` 未設時會直接吃到空字串繼續寫入。
S4 條款(第 82 行)「若撤回的目標不存在、已被撤過、本身是撤回紀錄或理由空白,則應擋下且帳本不變」列了四種擋下條件,沒有第五種「撤回者(by)為空」——但 §實務隱患明確把「撤回者」與「理由」並列為同等重要的守衛(「撤回一定要理由與撤回者」),理由空白有擋、撤回者空白沒擋,兩者在同一句話裡被賦予同等地位,S4 條款卻只落實了一半,是內部不一致,不是措辭問題:字面實作出來的行為(允許撤回者是空字串)直接牴觸 spec 自己宣稱要有的守衛。

## F3 一個迴圈同時有 `cap-reached` 與後來的 `converged` 紀錄時,「放行」判準(有 converged 紀錄)與「未放行迴圈」判準(以 cap-reached/rewrite 收尾)互相沒有排他規則,是本 repo 真的會發生的情況
severity: major
blocking: 是,同一迴圈的同一批逃逸列可能同時被算進「分母裡的已放行迴圈」與「未放行迴圈的逃逸(不進任何類別)」兩套互斥語意,依實作順序不同,結果不是重複計入就是憑空消失,而 spec 的「誠實界線」段落沒有把這種低估/重複來源列進已知清單。
引句:「記在 `cap-reached` 或 `rewrite` 收尾的迴圈(或還開著的)底下的逃逸列」
file: `scripts/lumos:10673-10678` `cmd_loop_next`(disposal gate)第②③步:`rc==0` 才 `_loop_gov_mark(env, loop_id, "converged", ...)`;若當輪沒過且 `rounds_count>=cap` 則先 `_loop_gov_mark(env, loop_id, "cap-reached", ...)` 並 `return`——這兩個標記都直接寫進治理帳,不互斥、不覆蓋舊紀錄(append-only)。一個迴圈完全可能先在某次呼叫撞到 cap 被記 `cap-reached`,之後(擴大 panel、拉高上限、或人工續跑)又被記 `converged`,兩筆治理帳紀錄同時存在。
file: `scripts/lumos:6761` 既有讀者 `capped = sum(1 for k in by.values() if "cap-reached" in k and "converged" not in k and "rewrite" not in k)`——這行本身就是這個 repo 已經在處理「同一迴圈同時有 cap-reached 與 converged」這個真實場景的證據:它明確用「converged 不在裡面」把這種情況從「capped」排除掉。
本案 §四第一點「放行 = 治理帳有這個迴圈 `kind=converged` 的紀錄」是純粹的「存在性」判準(帳上有沒有出現過 converged);同一節第四點「記在 `cap-reached` 或 `rewrite` 收尾的迴圈」用的是「收尾」(終態)這個詞,語意上該是「最後狀態是 cap-reached/rewrite」而非「帳上出現過 cap-reached」——但 spec 全文沒有一句話講「兩者都出現時以哪一個為準」或「未放行判準要看最後一筆而非任一筆」,S6(分母)與 S8(未放行桶)兩條 [test:] 也各自獨立描述,沒有交代互斥規則。若實作者比照分級規則(`_loop_anchor_tier` 取第一筆)的字面直覺,用「kinds 集合裡有沒有出現過」做未放行判準(而非「取最後一筆」),前述迴圈的逃逸列就會同時落進分母(因為 converged 存在)又落進「未放行迴圈的逃逸」桶(因為 cap-reached 也存在)——後者「不進任何類別」的宣告會讓這筆列從分子搜集邏輯中被跳過(如果實作用 elif/continue 順序處理未放行桶在先),導致這個已放行迴圈的真實逃逸從分子消失卻仍算進分母,拉低該類別的率;若順序反過來,則會被雙重計入未放行桶與分子兩處。兩種實作順序都不是 spec 明講的結果。

已看,無:
- 撤回後又手動記一筆同一個 (迴圈, 站名, sha):查過 §三與 S5,「撤回不能再撤;要反悔就重記一列」是 spec 自陳的設計本意——重記出來的是新 token 的新列,不是被撤回目標本身,`_escape_rows_for` 的 `include_withdrawn` 過濾是憑撤回紀錄的 `target`(目標 token)比對,不是憑 (loop,stage,sha) 元組,所以重記的新列不會被誤判成「已撤回」,也不會讓原本被撤的列復活,兩筆各自獨立存在、各自的撤回狀態互不影響,沒有找到會壞掉的行為。
- `_plan_for_loop` 改成內部去 `code-` 前綴:查過 `scripts/lumos:8010`,現存唯一呼叫者 `derived = str(loop)[len("code-"):]` 在呼叫前就已經手動去過前綴,`_plan_for_loop` 內部再去一次前綴對這個呼叫者是重複但無害的操作(除非計劃真的名叫 `code-...`,屬另一種既有邊界,與本案無關);spec 自己描述的新讀者(escape-stats)一樣是「先去前綴、NFC 正規化,再呼叫 `_plan_for_loop`」,兩邊都自己先去過,內部再去一次不會產生錯誤行為,只是「其他呼叫者一起受惠」這句話目前指涉的呼叫者集合是空的(唯一那個呼叫者不需要這個修正),屬措辭層級,不判定為獨立條目。
- 迴圈 `converged` 記兩次(同一迴圈被判過關兩次):`_loop_gov_mark` 是 append-only,不去重;但分母/分子判準都是「這個迴圈有沒有 converged 紀錄」的迴圈級存在性判斷,不是紀錄筆數,重複的 converged 紀錄不會讓同一迴圈被算兩次(除非讀側用列表而非集合累計迴圈,但 spec 用詞「放行了的迴圈數」本身就是以迴圈為單位,不是以紀錄筆數為單位),沒有找到具體會壞掉的路徑。
- 消費專案沒有歷史帳第一次跑:三本帳全空時,`escape-stats` 依 §四規則(「率一定在 0 到 1 之間;某格放行數是 0 就印「—」不算率」「只印有放行數的類別組合」)不會枚舉出任何類別,只印末尾全體皆 0 的統計行;`rule-gap` 對空檔案已有既有的「逃逸帳是空的」分支(`scripts/lumos:20253-20257`);`--withdraw` 在空帳本情境下 `known`/`existing` 集合天然是空集合,S4「目標不存在」的擋下條件自然成立,沒有找到字面實作會噴例外或印出誤導數字的路徑。
- 撤回時拿不到寫入鎖:spec §三「上鎖」段落已明講「照其他寫入指令一樣印『擋下:…』,不讓例外直接冒出來」,對照 `scripts/lumos:13757` 起的 `_vault_write_lock` 既有慣例(`with` 區塊、拿不到鎖逾時的既有處理路徑),這段規格與既有寫入指令(`cmd_loop_escape` 一般路徑、`_auto_escape`)的鎖用法一致,沒有找到新的邊界缺口。

最嚴重 severity:major;blocking 共 3 條(F1、F2、F3)。
