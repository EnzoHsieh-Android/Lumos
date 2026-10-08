severity: blocker

## F1 只驗第二個母:第一個母帶進來的沒審過程式整包放行
severity: blocker
blocking: 是 — 放寬讓「未審程式進主線」成真,major/blocker 必擋

誰:任何有主線推送權的開發者,或被注入的 AI agent。從哪:本機,不需要偽造任何帳本。做什麼:拿未審過的 evil 分支(含後門 backdoor.py)與主線現在的頂端 MAIN(它自己有有效 pass)用 `git commit-tree` 造一個兩個母的合併提交,母的順序是 (evil, MAIN),樹填 `git merge-tree --write-tree evil MAIN` 的結果。因為 MAIN 是第二個母,推上主線是快轉,git 不擋。結果:spec 的規則只拿第二個母(這裡剛好是主線自己)去找有效紀錄,MAIN 的紀錄對 MAIN 同版本有效,放行;evil 的後門整包進主線,從來沒人審。母的順序對調(把主線當成「合進來那側」)正是這條。

實作證據(臨時 repo,依 spec 規則手算,有效性用真的 `_codeloop_record_valid_ex`):
- `git merge-tree --write-tree evil MAIN` rc=0,樹 224ed5d,與假合併提交 6a547e3 的樹相等(tree eq: yes),`git ls-tree` 含 backdoor.py。
- `_codeloop_record_valid_ex(repo, MAIN, MAIN)` 回 `(True, '同版本 3d3031ea', False)` → spec 規則會放行。
- 對照現行規則:`_codeloop_record_valid_ex(repo, 主線舊紀錄, M)` 回 `(False, '記錄 sha edf96bc8 之後動了代碼(非純簿記增量)', False)` → 現在會擋,放寬後變放行。
- 第二個母換成主線更舊的已審提交 X 也成立的話要走非快轉,所以實際用 MAIN;變體是第二個母 = 任何帶有效 pass 的分支頂端,第一個母 = 未審分支,同樣放行。
- 表態那關是同一條規則,同樣被繞。

spec 對應句:
引句:「合併提交恰好兩個母、它的樹等於兩個母自動合併的結果(合併時沒手改任何東西),而合進來那一側的頂端有有效的 pass/skip(表態同理)——就放行」
引句:「目標是上面那種合併提交,改在治理帳裡找「任何分支」的 pass/skip 紀錄」
這兩句只要求「合進來那側」有效,沒要求第一個母也是已驗內容(例如等於推送前的主線頂端、或也有有效紀錄)。「樹等於自動合併」只證明沒手改,不證明兩邊都審過。
建議:要求第一個母 == 這次推送的舊頂端(CI 的 BEFORE / hook 的 remote sha)或對第一個母也找到有效紀錄;兩母都驗;拒絕第一個母不是 push 前主線頂端的合併。
file: `scripts/lumos:46538`(`_codeloop_record_valid_ex` 只比單一 rec/marker 對)
file: `.github/workflows/ci.yml:186`(CI 給的是 `$BEFORE..$SHA`,spec 沒用 BEFORE 去釘第一個母)

## F2 手寫一筆治理帳紀錄在「任何分支」比現在更好用,但不比現在更弱——spec 的「同樣信任」只是對的一半
severity: minor
blocking: 否 — 偽造能力現行就有(寫 branch=main 的一行即可),這條沒新增攻擊面,但會放大 F1
誰:同上。從哪:改 `docs/.governance-log.jsonl`(tracked 純文字,無簽章;`_codeloop_read_from_ledger` 只比 gate/kind/branch/head_sha)。做什麼:加一行 `{"gate":"code-loop","kind":"passed","branch":"任意名","head_sha":"<含後門的 sha>"}`,後面再接一個只動簿記檔的提交,讓該 sha 是祖先且之後只動簿記。結果:現行規則下只要 branch 寫 main 也騙得過,所以不是新洞;但放寬後攻擊者不必猜主線名字、可偽造在任何分支名下,且 spec 把「審過」的證據降為「帳本有一行字」。與 F1 合用不需偽造。spec 的「沒有新的外部輸入」這句成立,但沒有誰核對「那筆 pass 是否真的由 `code-loop pass` 寫的」。
引句:「合進來那側的紀錄寫在同一份治理帳裡(合併請求本來就把帳本提交帶進主線),跟現在信任目標分支紀錄的程度一樣」
file: `scripts/lumos:45517`(`_codeloop_read_from_ledger`)

## F3 簿記資料夾夾帶程式、母對調以外的幾條:現有檢查擋得住,放寬沒有新增缺口
severity: clean
blocking: 否 — 已實查現有判定,未找到繞法
- 在 pass 之後只改「簿記檔」夾帶程式:`_codeloop_record_valid_ex` 對簿記資料夾下的檔案做 `_codeloop_bookkeeping_code`(可執行位元、副檔名、無副檔名 `#!` 首行、控制字元路徑都判成程式),新規則沿用它,不弱化。
- 先合審過的小分支、再在同一個合併提交裡藏改動:樹與 `merge-tree` 不等 → 回 None 照舊擋(假設 merge-tree 的 rc 檢查如 spec 所寫)。
- 合併提交母數 3 以上:spec 明確拒。
- GitHub 實際合併與本地 merge-tree 不同:本地重算的樹與實際合併提交比較不等就擋,屬 fail-closed(只造成誤擋,不造成放行);CI 用 `fetch-depth: 0` 有歷史。誤擋時 spec 的原因訊息要能講清,見 F4。
file: `scripts/lumos:46538`、`scripts/lumos:26540`、`scripts/lumos:26559`

## F4 「最近 50 筆」可被灌帳擠掉合法紀錄,造成誤擋(可用性)
severity: minor
blocking: 否 — 只會多擋、不會多放,且擋下有補審的路
誰:任何能寫帳本的人。做什麼:在合併請求之前後灌 50 筆以上其他分支的 pass/skip,把合進來那側的真紀錄擠出「由新到舊最多 50 筆」。結果:合法合併判成「找不到有效紀錄」被擋;只能在主線補記,這正是 spec 想避免的洗白路徑。另外 `merge.renames`/屬性檔/git 版本不同造成 merge-tree 與 GitHub 合併樹不同時同樣誤擋。
引句:「依帳本行序由新到舊、最多看最近 50 筆」
建議:改成以第二個母為索引找(紀錄的 head_sha 是第二個母或其祖先),不用行數上限。

## 這個放寬讓哪些原本會被擋的情況變成放行(判是否該放)
- 乾淨合併、第二個母有有效紀錄、第一個母 = 推送前主線頂端:該放行(spec 本意)。
- 乾淨合併、第二個母有有效紀錄、第一個母是未審分支(F1):不該放,現在會擋、放寬後放行。
- 第一個母 = 主線舊頂端但第二個母的紀錄是偽造帳本行(F2):現行也放行,維持。
- 手改合併/衝突/三個母:仍擋,該擋。
- 舊合併請求紀錄(之後動過程式):仍擋,該擋。
- 主線直推用 `git commit-tree` 造的假合併:兩母都符合 spec 條件時放行;第一個母未驗即 F1。

severity 總結:最嚴重 blocker;blocking 條數 1(F1),另 F2、F4 為 minor、F3 為 clean。
