# selfaudit-loop r3 架構對齊審查

被審:`/tmp/selfaudit-loop-r3.md`(自足性審計閉環_計劃,150 行)。只判「跟本專案既有做法一不一致」,不找 bug、不評風格。★只審 v4 delta:設計節八步(40-82 行)、測試十一條(99-106 行)★。對照對象:`scripts/scenario_probe.py` 的 `make_sandbox`(沙盒建置/清理/成本三層隔離)、`governance/eval/retrieval_eval.py:251` 的 `pin_snapshot`(worktree+atexit 清理慣例)、`scripts/lumos` 既有 70 餘個子指令的註冊慣例(nested subparser / required-verb positional vs flag)、`about_code_expired` 純函式抽取先例、`covered.jsonl`/`governance/scenarios/history.jsonl`/`docs/.governance-log.jsonl` 三種既有 jsonl 讀寫慣例、`auto-$TODAY`/`auto/spec-...`/`auto-spec:` 既有自動流程前綴慣例、本庫 `git worktree` 既有三處先例(`guard kill`/`mutate`/`pin_snapshot`)有沒有「worktree 內跑 agent」這回事。

---

## 問一:隔離機制——沙盒/worktree 兩軌並用,安全層與清理紀律站不站得住

**FAIL 修復鏈把 agent(帶 Edit+Bash)放進 `git worktree`,但沒有比照 `make_sandbox` 的三層隔離(拔 remote/假 hooksPath/假身分)——不對齊,major。**

spec 設計第 4 條 FAIL 分支:「FAIL → 修復鏈:★修 agent 在 `git worktree`(從 HEAD 建)★內修該篇(allowedTools 加 Edit;範圍刀=`git -C <wt> diff --name-only` 與候選的 repo_rel ★同空間嚴格相等★,越界=丟 worktree 主樹零污染…)→ ★複審 agent 也在該 worktree★」(`/tmp/selfaudit-loop-r3.md:62-65`)。

引句:「★修 agent 在 `git worktree`(從 HEAD 建)★內修該篇(allowedTools 加 Edit」(`/tmp/selfaudit-loop-r3.md:62`)

先看同一步驟的審計/複審派工那半——「照 `scenario_probe.make_sandbox` 三層隔離先例建沙盒副本(無 remote/假身份/pre-push 擋)」(`/tmp/selfaudit-loop-r3.md:52`)——這半段真的照做了:`make_sandbox`(`scripts/scenario_probe.py:83-100`)docstring 明講 2026-08-23 事故(rsync 副本沒拔 remote,被測 AI 真的 push 到了真遠端),所以做了三道:拔 remote、副本專用 `hooksPath` 硬擋 pre-push、假身分 `probe@local`。但第 4 條的 FAIL 修復鏈換了隔離機制——從「rsync 副本」換成「`git worktree`」——卻沒有把這三層搬過去。我實際在本 repo 跑了一次 `git worktree add --detach`,核對結果:`git -C <wt> remote -v` 印出跟主樹一模一樣的 `Lumos → https://github.com/EnzoHsieh-Android/Lumos.git`(push 可用),`git -C <wt> config core.hooksPath` 也回主樹真正的 `scripts/hooks`(不是沙盒的假 hooksPath)。這是 git 的既有行為:worktree 共用同一份 `.git`,remote 設定跟 hooksPath 是 repo 級不是 worktree 級,不會像 rsync 副本一樣天然被切斷。本庫目前僅有的三處 `git worktree` 先例——`guard kill`(`scripts/lumos:5788-5877`)、`mutate`(`scripts/lumos:10473-10537`)、`pin_snapshot`(`governance/eval/retrieval_eval.py:251-276`)——沒有一處給過 agent Bash 執行權,都是固定指令(跑測試/跑既有 python 腳本),所以從沒踩過這個坑;而 spec 這裡是本庫第一次把「帶 Bash 工具、可以自己下指令」的 agent 放進 worktree 內,卻沿用了一個天生不隔離 push 路徑的容器,還沒重建 `make_sandbox` docstring 講的那三層防線。判 major(安全層退化到跟 2026-08-23 事故發生前的 rsync 副本同一等級,而且這次 agent 手上還多了 Edit)。

**worktree 生命週期沒有 `pin_snapshot`/`guard kill`/`mutate` 一致的顯式清理——不對齊,major。**

spec 第 4 條處置只交代了越界時的清理:「範圍刀…越界=丟 worktree 主樹零污染」(`/tmp/selfaudit-loop-r3.md:63-64`),但「複審 PASS=檔案 copy 回主樹+蓋章+commit」(`/tmp/selfaudit-loop-r3.md:66`)與「複審 FAIL=報告落 `governance/pending/selfaudit/<日期>-<stem>.md`」(`/tmp/selfaudit-loop-r3.md:67`)這兩條——也就是絕大多數不越界的正常結束路徑——都沒提 worktree 移除。

引句:「越界=丟 worktree 主樹零污染」(`/tmp/selfaudit-loop-r3.md:63`)

本庫三處既有 worktree 先例的紀律完全一致:`guard kill` 用 `try/finally`,`finally` 裡不管成功失敗都 `git worktree remove --force`+`shutil.rmtree`+`git worktree prune`(`scripts/lumos:5860-5877`);`mutate` 對 baseline worktree 與每個變異 worktree 各自 `try/finally` 立即移除(`scripts/lumos:10495-10499`、`10534-10537`);`pin_snapshot` 因為要跨整個評測流程存活,改用「`worktree add` 一成功就立刻 `atexit.register` 清理」,而且它的程式碼註解明講這條紀律是踩過坑才定下來的:「★worktree add 一成功就註冊清理★(code-r1 bug 席:原重構把註冊搬進 `_sv` 判斷內,『add 成功但該 commit 無 vault』路徑只 rmtree 不 worktree remove → git 登記殘影)」(`governance/eval/retrieval_eval.py:260-262`)。spec 這裡只講了「越界」這一種結束路徑要丟 worktree,PASS 與 FAIL 兩條主線路徑都沒交代要不要移除、什麼時候移除——這正是 `pin_snapshot` 那則註解點名過的同一種漏洞(add 成功但收尾沒清)。測試段落也沒補上這塊:⑥⑦(`/tmp/selfaudit-loop-r3.md:104-105`)只驗「複審 PASS→copy+戳+commit」「複審 FAIL→pending+主樹零污染」跟「越界→丟 worktree、主樹無變化」,沒有一條驗 worktree 本身有沒有被移除。判 major(本庫對 worktree 生命週期只有一種紀律、而且是踩過真事故才定下來的,這裡靜默地不繼承)。

**⚠ 沙盒與 worktree 兩種隔離手法在同一條 pipeline 裡分工並用,而且是本庫第一次讓 agent 在 worktree 內執行——算不算「開了第二種做法」,判不準,不計入下方條數。**

spec 把「唯讀審計/複審」派進 `make_sandbox` 式沙盒(`/tmp/selfaudit-loop-r3.md:52`),把「可寫的修復/複審」派進 `git worktree`(`/tmp/selfaudit-loop-r3.md:62、65`)。單獨看,`make_sandbox` 只在 `scenario_probe.py` 這一支腳本裡用過,`git worktree` 只在 `guard kill`/`mutate`/`pin_snapshot` 這三支跑固定指令的腳本裡用過——兩者都各自有先例,但「同一條治理流程裡,按階段風險不同分別選用兩種不同隔離機制」跟「worktree 裡面站著一個能自己下指令的 agent」這兩件事,本庫都還沒真的做過,無法對照既有做法判出「一致」或「不一致」,只能判不準。

---

## 問二:CLI 介面——`self-audit --candidates` 該不該是新旗標

**在既有必填 `node` 的 `self-audit` 寫入型子指令上疊一個 `--candidates --json` 唯讀列表旗標,跟本庫「同名子指令下多動作」的兩種既有慣例都對不上——不對齊,major。**

spec 設計第 1 條:「新唯讀子指令 `lumos self-audit --candidates --json` 輸出 PR 排序候選(rel、stem、repo_rel 三欄…)」(`/tmp/selfaudit-loop-r3.md:48-49`)。

引句:「新唯讀子指令 `lumos self-audit --candidates --json` 輸出 PR 排序候選」(`/tmp/selfaudit-loop-r3.md:48`)

`self-audit` 現有的 argparse 定義是 `sa = sub.add_parser("self-audit", …)`,`sa.add_argument("node")` 沒有 `nargs="?"`(`scripts/lumos:15608-15611`),對應的 `cmd_self_audit(env, rel, model="sonnet", date=None)` 直接寫 `self_audit: <model>/<date>` 到節點 frontmatter(`scripts/lumos:7578-7593`)——這是一個「必填單一目標節點+會寫檔」的動作。`--candidates` 這個新用法完全不吃 `node`(候選清單本來就沒有單一目標),輸出形狀也整個換成 JSON 陣列(三欄 rel/stem/repo_rel)——本質上是另一種動作,而不是同一動作的參數微調。核對本庫目前 70 餘個子指令,遇到「同一個名字底下有好幾種不同形狀的動作」時,只有兩種既有做法:①巢狀子解析器,例如 `about-code`(`acsub.add_parser("revert"/"restamp"/"migrate-stamp")`,`scripts/lumos:15363-15374`)、`canary`(`second`/`record`,`:15375-15382`)、`guard`(`list`/`scaffold`/`bind`/`audit`/`trace`/`kill-add`/`kill`,`:15474-15517`)、`loop`(`status`/`compress`/`verify-progress`/`next`/`canary-stats`/`capture-counts`,`:15424-15466`);②必填的「動詞」positional 配 `choices`,例如 `rel-cascade`:`p.add_argument("verb", choices=["confirm","prune","list","resume"])`,連唯讀的 `list` 動作也要求先寫出 `verb`,其餘欄位(含另一個 positional `arg`)才依動作各自決定要不要吃(`scripts/lumos:15629-15636`)。這兩種既有做法有一個共同點:呼叫端在指令列上一定要打出一個「不是 `--` 開頭的動作詞」才能選到不同動作,而 `gov --nags`/`stale --candidate`/`query --tag`/`pitfalls --diff` 這種「同一子指令靠旗標切模式」的既有例子(`scripts/lumos:15354-15361`、`15555-15561`、`15563-15577`、`15707-15714`),base positional 全部本來就是 `nargs="?"` 或整個沒有 positional——沒有一個是「原本必填的 positional,靠旗標讓它變不必填、同時換掉輸出形狀」的用法。`--candidates` 用 `--` 開頭,語法上就是旗標而不是動詞,所以也套不進①巢狀子解析器那條路(若真要走①,既有寫法會是 `lumos self-audit candidates --json` 這種裸詞,不會用 `--`)。判 major(現有兩種「同名多動作」的慣例都繞不過去,這是第三種、查無先例的形狀)。

（附帶一提:同一條裡「前置重構抽純函式 `_self_audit_lists(notes) -> (missing, stale)`」(`/tmp/selfaudit-loop-r3.md:46`)這半段本身跟 `about_code_expired(vault, rel, stamp)`(`scripts/lumos:7736-7740`)先例的精神——抽出去的函式不碰 `gov_events`、落帳留在 `run_doctor` 端——是對齊的,而且比 r2 版本「`SourceFileLoader` 拉整個吃 `env` 的函式」更進一步用 subprocess+JSON 邊界解掉了跨層 import 問題,這部分不算不對齊、不計入下方條數。）

---

## 問三:帳本與命名慣例——週帳 jsonl 的欄位形狀、commit trailer 的「既有格式」聲稱

**`governance/selfaudit-week.jsonl` 同一個檔案要塞兩種沒有共同判別欄位的列形狀,連 spec 自己宣告的欄位都自相矛盾——不對齊,major。**

spec 第 4 條:「★週帳 `governance/selfaudit-week.jsonl`…★:每行 `{"week","stem","verdict","ts"}`;配額=`N - 本週行數`…」(`/tmp/selfaudit-loop-r3.md:71-72`),接著:「喊人=…★每檔每週最多喊一次★(同 jsonl 記 `{"week","stem","nagged":true}`,Codex f6)」(`/tmp/selfaudit-loop-r3.md:73`)。

引句:「同 jsonl 記 `{"week","stem","nagged":true}`」(`/tmp/selfaudit-loop-r3.md:73`)

同一段話先宣告「每行」的形狀是 `{week,stem,verdict,ts}`,兩行之後就往同一個檔案寫進另一種形狀 `{week,stem,nagged:true}`——沒有 `verdict`/`ts` 鍵,也沒有任何一個雙方共用、可以拿來分辨「這行是配額列還是喊人列」的判別欄位(既不是額外的 `kind`/`type` 鍵,也不是其中一種形狀的鍵集合包含另一種)。核對本庫既有的三種 jsonl 讀寫慣例:`covered.jsonl`(`governance/covered.jsonl`)跟 `governance/scenarios/history.jsonl`(情境探針健康史,`scripts/scenario_probe.py:238-241` 寫入)都是「整檔單一形狀」——`covered.jsonl` 每行恰一個 `weakness` 鍵,讀取端 `{json.loads(l)["weakness"] for l in …}` 直接假設鍵存在不做分支(`governance/autonomous_loop/gap_select.py:25-31`);`history.jsonl` 每行都是 `ts/seed/passed/total/failed` 一種形狀,一次探針跑一行,沒有第二種形狀混進去。唯一「同檔混多種形狀」的既有先例是 `docs/.governance-log.jsonl`——我實際掃過前 2000 行,抓到三種鍵集合,但三種形狀都固定帶 `gate` 跟 `kind` 兩個鍵,消費端(`_render_gov_nags`,`scripts/lumos:3076-3120`)靠這兩個鍵分辨要不要處理這一行、怎麼處理。`selfaudit-week.jsonl` 的設計比這三種既有慣例都弱:既不是「全檔單一形狀」,混形狀時也沒有 `.governance-log.jsonl` 那種「每行都帶穩定判別鍵」的機制。實際後果不是空談——「配額=`N - 本週行數`」(`/tmp/selfaudit-loop-r3.md:72`)如果照字面「本週行數」去數,`nagged` 列一旦寫進同一週,會被一起算進去,`N=2 寫死`的配額鎖(`/tmp/selfaudit-loop-r3.md:72`「★真正鎖 2/週…★」)就可能被喊人列擠掉一格。測試段落⑨「週帳:中斷後補殘、喊人每檔每週一次」(`/tmp/selfaudit-loop-r3.md:106`)也沒有一條驗證這兩種列不會互相污染對方的計數。判 major(本庫既有三種 jsonl 慣例沒有一種允許「同檔混形狀又不給判別鍵」,而且這裡不只是行文不嚴謹,是會反噬配額鎖本身的具體邏輯洞)。

**「複審 PASS…commit(照既有自動 commit 格式,訊息 trailer 記 audited/fixed/reverified 三 model)」聲稱在照既有格式,但本庫唯一的自動化 commit 先例沒有 trailer——不對齊,non-major。**

spec 第 4 條:「複審 PASS=檔案 copy 回主樹+蓋章+commit(照既有自動 commit 格式,訊息 trailer 記 audited/fixed/reverified 三 model,arch minor)」(`/tmp/selfaudit-loop-r3.md:66`)。

引句:「照既有自動 commit 格式,訊息 trailer 記 audited/fixed/reverified 三 model」(`/tmp/selfaudit-loop-r3.md:66`)

`grep -rn "git commit"` 掃過 `scripts/lumos`、`governance/*.sh`、`governance/*.py`、`governance/autonomous_loop/*.py`,本庫治理層目前唯一真的會自動 commit 的地方只有 `governance/autonomous-loop.sh:380`:`git commit -m "auto-spec: $TOPIC（自主迭代 loop 收斂產出，待人放行）"`——單行訊息,沒有任何 trailer 區塊,前後也找不到第二個自動 commit 的地方。這一條在 r2 審查時就被指出「本庫自動化 commit 目前只有一種慣例,且沒有署名區塊」(`governance/review-reports/selfaudit-loop/r2-arch.md:47-53`);v4 版本把措辭從 r2 的「commit(訊息三 model 署名)」改成「照既有自動 commit 格式,訊息 trailer」,等於明確聲稱這是在延續一個既有格式——但既有那唯一一筆先例仍然是單行、無 trailer,聲稱的「既有格式」查無此物。判 non-major(這不是新開了一種危險的做法,是 v4 在措辭上把「這是新格式」悄悄寫成了「這是照舊格式」,r2 那條發現實質上還沒解決)。

（附帶一提:同一條裡的 `--model auto-<model>`(`/tmp/selfaudit-loop-r3.md:60-61`)已經改成連字號前綴,核對 `auto-$TODAY`(canary loop id,`governance/autonomous-loop.sh:245`)、`auto/spec-$TOPIC-$TODAY`(分支名,`:377`)、`auto-spec:`(commit 訊息/PR 標題,`:380-381`)三個既有「自動流程」前綴先例,以及 `self_audit` 欄位本身沒有 `choices` 限制、Check S 只用正則抓日期不解析前段(`scripts/lumos:834-838`)——這一格已經對齊,是 r1/r2 兩輪連續抓到的「`-auto` 後綴/`auto/` 造成雙斜線」問題在 v4 真的修掉了,不算不對齊、不計入下方條數。）

---

## 結論

不對齊共 **5** 條,其中 major **4** 條:

1.(問一)FAIL 修復鏈把帶 Edit+Bash 的 agent 放進 `git worktree`(`/tmp/selfaudit-loop-r3.md:62`),卻沒有比照 `make_sandbox` 三層隔離(`scripts/scenario_probe.py:83-100`)拔 remote/換 hooksPath/假身分——實測 `git worktree add` 出來的副本 `remote -v`/`core.hooksPath` 跟主樹完全相同,保留了真實 push 路徑,是本庫第一次讓可執行 agent 進 worktree 卻沒繼承 2026-08-23 事故訂下的隔離紀律。**major**。
2.(問一)worktree 生命週期只交代越界那一條路徑要丟棄(`/tmp/selfaudit-loop-r3.md:63-64`),PASS(`:66`)與 FAIL(`:67`)兩條主線路徑都沒提移除,跟 `guard kill`(`scripts/lumos:5860-5877`)、`mutate`(`:10495-10499、10534-10537`)、`pin_snapshot`(`governance/eval/retrieval_eval.py:260-266`,附帶「add 成功就要立刻註冊清理」的既有踩坑教訓)三處既有先例的顯式清理紀律不符,測試段落⑥⑦也沒補這塊。**major**。
3.(問二)在既有必填 `node`、會寫檔的 `self-audit` 子指令上疊一個不吃 `node`、純唯讀的 `--candidates --json` 旗標(`/tmp/selfaudit-loop-r3.md:48`),跟本庫「同名子指令多動作」的兩種既有慣例(巢狀子解析器如 `about-code`/`guard`/`loop`;必填動詞 positional 如 `rel-cascade`)都對不上,也不符合旗標式多模式指令(`gov`/`stale`/`query`/`pitfalls`)一律 base positional 本來就選填的既有前提。**major**。
4.(問三)`governance/selfaudit-week.jsonl` 同檔混寫兩種沒有共同判別欄位的列形狀(`/tmp/selfaudit-loop-r3.md:71、73`),比本庫既有三種 jsonl 慣例(`covered.jsonl`/`history.jsonl` 全檔單一形狀,`.governance-log.jsonl` 混形狀但每行都帶 `gate`+`kind`)都弱,且會讓「本週行數」配額計算把喊人列一起算進去,反噬 `N=2 寫死` 的配額鎖本身。**major**。
5.(問三)「複審 PASS…commit(照既有自動 commit 格式,訊息 trailer…)」(`/tmp/selfaudit-loop-r3.md:66`)聲稱延續既有格式,但本庫唯一的自動化 commit 先例(`governance/autonomous-loop.sh:380`)是單行、無 trailer——這條 r2 已抓過(`r2-arch.md:47-53`),v4 只是把措辭改成「照既有」但實質沒解決。

另有 1 條判不準標 ⚠、不計入以上條數:同一條 pipeline 裡「唯讀審計/複審用 `make_sandbox` 式沙盒、可寫的修復用 `git worktree`」兩種隔離手法分工並用(`/tmp/selfaudit-loop-r3.md:52、62、65`),而且是本庫第一次讓 agent 在 `git worktree` 內執行——兩種手法各自有先例(沙盒僅見於 `scenario_probe.py`;worktree 僅見於跑固定指令的 `guard kill`/`mutate`/`pin_snapshot`),但「按階段風險分流用兩種機制」與「worktree 內站 agent」這兩件事本身都還沒有既有做法可對照,判不準是不是「開了第二種做法」。
