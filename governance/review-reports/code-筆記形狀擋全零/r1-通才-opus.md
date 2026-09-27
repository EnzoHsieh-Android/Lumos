severity: major

審查範圍:r1-snapshot.patch(e46acb01..8c49a338,scripts/lumos 的 cmd_note_shape、_note_shape_doctor_lines,以及 scripts/test_lumos.py 新增的一支測試)。
已跑:`python3 scripts/test_lumos.py -k all_zero_base` → 2 passed。重現腳本放在 scratchpad/HF/(repro_f1.py、repro_f2.py、repro_f4.py、yaml_check.py),都在 mktemp 開的臨時 repo 裡跑,沒動被審 repo。
已確認沒問題的部分:40 個 0 只認完全相符(39 個 0 或混了別的字元照舊走 rev-parse,找不到就跳過);終點是 40 個 0(刪分支)仍然跳過;起點和終點都是 40 個 0 也跳過;淺層 clone 的判斷排在換成空樹之前,行為沒變;doctor 那段 shell 去掉括號說明後 YAML 解析得了,在 `bash -eo pipefail` 下跑,before 給 40 個 0 或空字串會換成空樹,給一般 sha 則原樣帶入;新測試換回修改前的 lumos 會翻紅(修改前 `0000..tip` 回 rc0「範圍在本機找不到」)。

## F1 新分支如果還沒有任何新提交(或是推 tag),起點是 40 個 0 時會把主線上線點之後的整段歷史當成新增重查,誤擋
severity: major
blocking: 是 —— 使用者的推送沒有新增任何內容,CI 卻翻紅,而且改不了(那些違規在主線上);這也違背了 pre-push 刻意定下的設計:「全部已在遠端就不查」
引句:if re.fullmatch(r"0{40}", a or ""):

執行路徑:起點換成空樹 → `_nodehome_clamp_base` 看到空樹,直接改成上線點(file: `scripts/lumos:22963`)→ `_ns_range_added` 走 `rev-list 上線點..tip --not <主線>`。可是 `_ns_exclusions` 只有在「tip 不是 origin/main 的祖先」時才排除主線(file: `scripts/lumos:23574`)。一個直接開在 main 頂端的新分支、推一個 release 分支,或推一個打在主線提交上的 tag(push 事件的 before 同樣是 40 個 0,workflow 沒過濾分支就會跑),tip 都在 origin/main 裡面,結果什麼都沒排除:主線上線點之後的每一個提交都被當成「這次推送」重查。
主線上本來就可能有這種舊帳。doctor 的第 ③ 項就是專門列「上線點之後、已推上遠端卻違反兩條規則的新增行」(file: `scripts/lumos:23866`);warn 模式時期留下的、還沒貼 CI 這一步之前用 --no-verify 推上去的,都算。會照 doctor 建議去貼這一步的消費專案,正好就是這種情況。
修改前這條路是「範圍在本機找不到、跳過」,rc0。修改後變成 rc1。本機 pre-push 面對同一件事,用的是「不在任何遠端的提交裡最早那一個的上一個提交」,全部都在遠端就不查(file: `scripts/hooks/pre-push:217`)。所以同一次推送,本機放行、CI 擋下,兩邊不一致。
同一個根因的輕一點的版本:新分支開在另一條還沒合進主線的遠端分支上時,排除清單只有主線,那條分支已經查過的提交會再被查一遍(pre-push 用的是 `--not --remotes`)。

最小重現(scratchpad/HF/repro_f1.py):`_ns_repo()`(init 就是上線點)→ 在 main 提交一行 `src/a.py:4` 當舊帳 → 推到 bare 遠端的 main → clone 下來,`git checkout -b release-1`(沒有新提交)→ `note-shape --diff 0000…0000..<tip>`。
實測:`git rev-list tip --not --remotes` 是空的(pre-push 不會查),`note-shape` 回 rc=1,擋下 `docs/kg-knowledge/Systems/A.md:18 程式行號引用 src/a.py:4`。修改前同一個指令回 rc0。
方向:起點是 40 個 0 時,照 pre-push 那套算:tip 已經在主線(或任何遠端)上,就不查;不然就從「不在遠端的最早提交」的上一個提交開始算,不要直接用空樹再截到上線點。

## F2 doctor 給的 CI 步驟漏了 ci.yml 那行「本機找不到起點就換成空樹」,force-push 之後照樣整批放過
severity: major
blocking: 是 —— 這次要修的就是「照 doctor 貼的 CI 步驟,起點找不到就整批放過」這一類問題,同一行還留著一個常見的入口;工具鏈自己的 ci.yml 已經補了這一行,卻沒搬過來
引句:B=4b825dc642cb6eb9a060e54bf8d69288fbee4904;; esac;

ci.yml 在 case 後面還多一行 `git cat-file -e "$BEFORE^{commit}" 2>/dev/null || BEFORE="$EMPTY"`(file: `.github/workflows/ci.yml:134`,code-loop 那步也有,在 `:111`)。doctor 給的步驟只處理 40 個 0 和空字串。
force-push(amend 或 rebase 之後推)時,GitHub 給的 before 是舊的頂端,已經沒有任何 ref 指到它,checkout 時 fetch-depth: 0 也抓不到。lumos 走到 `_lens_full_sha(a)` 拿到 None,印出「範圍 … 在本機找不到,跳過(fail-open)」,回 rc0。結果是「amend 一行違規,然後 `git push --force --no-verify`」就能穩定繞過 CI。pre-push 的註解把這種情況叫做「穩定繞法」,要避免。
最小重現(scratchpad/HF/repro_f2.py):一個含 `src/a.py:4` 的違規提交,拿本機不存在的 sha 當起點 → `note-shape --diff <不存在的sha>..tip` 回 rc=0,並印出 fail-open 那句;doctor 那段 shell 會原樣把 B 保留成那個 sha。換成 ci.yml 的 cat-file 兜底之後,B 變成空樹,回 rc=1。
另外,patch 說明寫的「lumos 本身也認 40 個 0,兩道保險」只涵蓋 40 個 0,force-push 這種情況兩道都沒有。修的時候留意:force-push 補成空樹之後,如果 tip 已經在主線裡,會碰到 F1 的誤擋。

## F3 `&&` 串接改成 `;` 之後,git fetch 失敗不再讓這一步變紅,而且真正的 before 會被丟掉
severity: minor
blocking: 否 —— fetch 失敗很少見,而且會落到「多查」那一側
引句:B=\"${{ github.event.before }}\"; case \"$B\" in

原本整串是 `git fetch … && (…) && python3 …`,fetch 失敗時這一步就紅了,rc128。現在的寫法是 `git fetch … && (…) && B="…"; case …; python3 …`:fetch 失敗時 `B=` 那段根本不會執行,B 沒設定,被 case 當成空字串換成空樹。原本是正常 sha 的 before 被丟掉,範圍放大到上線點,主線推送也會踩到 F1 的重查。GitHub 預設的 `bash -e` 不會因為 `&&` 串中間那一段失敗就結束。
實測(bash --noprofile --norc -eo pipefail,沒有 origin):新寫法印出「python runs with B=EMPTY」,rc=0;舊寫法 rc=128。
方向:把 B 的指定移到 fetch 之前,或整段都用 `&&` / 換行接起來、改用 `set -e` 的寫法。

## F4 新測試對 doctor 步驟只比對字串,對「shell 能不能跑」是假綠;也沒涵蓋有遠端、排除主線的組合
severity: minor
blocking: 否 —— 測試不足,不是行為錯誤
引句:check("doctor 給的那步也把 40 個 0 換成空樹", "0000000000000000000000000000000000000000" in step

第二個 check 只看兩個 sha 字串有沒有出現。把 case 的 `;;` 刪掉、把 B 的引號拿掉,或把指定放到 python 後面,都還是綠的。第一個 check 用的 repo 沒有遠端,`_ns_exclusions` 永遠是空的,所以 F1 那種「tip 已在主線裡」的組合測不到。
建議:第二個 check 改成把 `${{ … }}` 代換掉,實際用 bash 跑一次,確認 40 個 0 和空字串都變成空樹;另外補一支「有 bare 遠端、新分支沒有新提交」的測試,預期 rc0。

## F5 其他收 --diff 的閘也有同樣的洞:home check 遇到 40 個 0 會跳過;code-loop check 則因為 pitfalls rc2 走 fail-open
severity: minor
blocking: 否 —— 題目說只要指出不用修;目前沒有 CI 路徑會把 40 個 0 傳進這兩個閘(pre-push 會先換好,ci.yml 也先換成空樹)
引句:base = a if a == _EMPTY_TREE_SHA else _lens_full_sha(root, a)

home check 的起點解析跟修改前的 note-shape 一模一樣(file: `scripts/lumos:23376-23380`)。實測 `home check --diff 0000…0000..tip`(範圍裡有一支沒有家的新程式檔)回 rc=0,並印出「範圍 … 在本機找不到,跳過(fail-open)」。
code-loop check 把範圍原樣交給 pitfalls;`pitfalls --diff 0000…..tip` 回 rc=2(git 的 Invalid revision range),`_codeloop_guard_verdict` 接到之後走 fail-open,不擋(file: `scripts/lumos:30642` 起那一段)。
哪天 doctor 也給這兩個閘一段 CI 步驟,或有人照 note-shape 那段自己改寫,就會重演同樣的整批放過。

## F6 doctor 印出的步驟,命令和括號說明黏在同一行,整段照貼進 workflow 的話 YAML 解析不了
severity: minor
blocking: 否 —— 修改前就有這個問題,而且出錯時很明顯(workflow 語法錯誤),不會悄悄放行
引句:新分支首推前一版是 40 個 0,換成空樹,lumos 會自己截到上線點

step 字串的結尾直接接著「(checkout 要設 fetch-depth: 0;…)」,裡面的「fetch-depth: 0」帶有冒號加空白。實測用 yaml.safe_load 解析整段照貼的結果,報錯 `mapping values are not allowed here`;去掉括號說明後才解析得了,也跑得動。這次 patch 把括號說明改寫得更長,但還是跟命令黏在一起。建議把說明拆到另一行,或改成 YAML 註解。

最嚴重等級 major,其中 blocking 2 條(F1、F2)。
