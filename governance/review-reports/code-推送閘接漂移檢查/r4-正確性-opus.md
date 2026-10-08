severity: minor

# r4 正確性席(opus)——推送起點修正驗收

實驗環境:`git clone --shared` 到自己的臨時目錄(HEAD 7adca0f7,含 8bcd45a6 的修正),直譯器 /opt/homebrew/bin/python3(3.14)。重現腳本借用 test_lumos.py 的 `_dr_push_repo`、`_dr_settle`、`_dr_actions_checkout`、`_dr_ci_bodies`、`_dr_ci_run` 造真 git repo 與裸遠端。每一種都拿同一個輸入分別跑修正後的 lumos(NEW)與修正前 74dc5185 的 lumos(PREV)對照。本輪相關的四支測試(`t_prepush_drift_start_mainline_shapes`、`t_ci_drift_default_branch_shapes`、`t_drift_check_push_start_edges`、`t_ci_drift_start_shapes`)在 clone 裡跑都是全綠。

## F1 本地 main 的 upstream 設成本機分支時,推那條分支會整步判成「沒有新東西」(相對修正前退步)
severity: minor
blocking: 否
引句:「完全相同才跳過——遠端與分支都要比(r3 正確性席:只比分支短名時,推 fork 的 main 會把正本的 main 也跳過)。」
file: `scripts/lumos:33136`
file: `scripts/lumos:33174`
file: `scripts/lumos:33212`
1. 情境:本地 main 的 upstream 設成本機另一條分支(`git branch --set-upstream-to=develop main`,也就是 branch.main.remote = .),然後推 develop 本身,develop 上有一次轉正、預告句還留著。
2. 修正後,`main@{upstream}` 用 `--symbolic-full-name` 解出來是 `refs/heads/develop`,永遠不會等於 `refs/remotes/origin/develop`,所以這個候選不會被跳過。它指的正是這次要推的本機頂端,結果「頂端在任一候選上」這條成立,整道檢查判成沒有新東西。
3. 修正前的 `_push_mainline_branch` 有專門處理這種形狀,patch 刪掉的那行寫著「upstream 設成本機另一條分支(branch.X.remote = .)」:它會回本機分支短名,跟被推的那條相同就跳過。這次改成只比 refs/remotes 全名,那個分支就不見了。
4. 重現(在 clone 裡用 test_lumos 的輔助函式跑;d0 是 develop 已推上去的頂端,d1 是轉正那個提交):
   - 前置:`drift check --diff d0..d1` 不帶推送參數時回 1(真的有要處理的)。
   - NEW:`drift check --diff d0..d1 --push-remote origin --pushed-ref refs/heads/develop` 回 rc=0,印「起點——頂端已在主線(main@{upstream})上——沒有新東西」。
   - PREV(74dc5185):同樣的指令回 rc=1,印「起點——一般增量推送:從遠端舊值 … 算」和「擋下:這次推送有 4 處要處理」。
5. 影響範圍:只有 main 或 master 的 upstream 指到本機分支時才會觸發,推那條本機分支(或任何頂端已經包含在它裡面的分支)時推送前完全不查,只記一筆跳過的帳。CI 那邊的 main@{upstream} 是 checkout 建的 origin/main,所以 CI 照查。修法方向:`_push_mainline_full` 解出 refs/heads/X 時也要當成被推的那條處理,或者乾脆不要把本機分支當主線候選。

## F2 分支同時合了兩條互不包含的主線時,取「歷史最長」的那個分岔點,還是會把另一條主線上別人的轉正算成這次的
severity: minor
blocking: 否
引句:「否則在不是舊值祖先的分岔點裡取歷史最長的那個」
file: `scripts/lumos:33216`
file: `scripts/lumos:33255`
1. 情境(git-flow):遠端 HEAD 指到 develop;main 上有一個 hotfix 轉正 H1,還沒合回 develop;功能分支 feat 從 develop 開,後來又合了 main 來拿 hotfix,第一次推送(舊值全 0)。
2. `merge-base --all feat origin/develop origin/main` 回兩個分岔點:develop 的頂端,和 H1。兩個互相都不是祖先。`_push_pick_base` 只能挑一個當起點,挑了 develop 頂端(歷史比較長),於是 `develop..feat` 把 H1 也算了進來。
3. 重現:NEW 回 rc=1,印「從跟主線(…)最近的分岔點 e55b5fc25fa4 算」和「擋下:這次推送有 4 處要處理」。PREV 一樣回 rc=1,所以這不是退步。對照 `git log feat ^origin/develop ^origin/main` 只有這個分支自己的 F1 和那個合併提交,兩個都跟轉正無關,所以這次擋下是誤擋。
4. 用提交數比大小,確實能讓範圍裡的提交最少;但只要有兩個以上分岔點,單一個起點本來就排除不掉另一邊。說明文字與 bound-tests-gate 的 PITFALL 行寫「取離頂端最近的分岔點」,對這種形狀並不成立。實作代理人在 r3 收貨紀錄裡已自報這種情況沒有釘測試;這裡補上實測結果:block 模式下會誤擋。
5. 修法方向:讓核心吃「頂端 ^分岔點一 ^分岔點二」這種多排除的範圍(`_notes_status_flipped` 的 git log 範圍與 `git diff` 的比較基底都要跟著改),不要只挑一個起點。

## F3 GitHub 標準的 fork 佈局(本地 main 追自己 fork 的 origin/main)下,同步 fork 和新分支首推都還會誤擋
severity: minor
blocking: 否
引句:「候選:refs/remotes/<遠端>/HEAD、main@{upstream}、」
file: `scripts/lumos:33161`
file: `scripts/test_lumos.py:51578`
1. 這次修正在 fork 上的兩個測試格(④⑤)都先把本地 main 設成追正本(`push -u upstream main`)。但 GitHub 文件教的佈局是 origin = 自己的 fork、另外加一個 upstream 指正本,本地 main 追的是 origin/main。這種佈局下,候選清單(推送遠端的 HEAD、main/master 的 upstream、推送遠端的 main/master)全部都指到 fork 那個沒同步的 main,正本的 upstream/main 根本不在候選裡。
2. 重現:正本上有別人的轉正 U1,fork 的 main 停在 M0,已經 `git fetch upstream`。
   - 新分支首推:`checkout -b feat upstream/main` 加一個無關提交,再推到 origin。NEW 回 rc=1,印「從跟主線(…origin…)最近的分岔點 b65b7e114d74(=M0)算」和「擋下 4 處」;PREV 也是 rc=1。
   - 同步 fork 的 main:`merge --ff-only upstream/main` 之後 `push origin main`。所有候選都是被推的那條,全被跳過,於是用舊值 M0,範圍 M0..U1 把正本上別人的轉正算了進來。NEW 和 PREV 都回 rc=1。
3. 不是退步,是 r3 fork 那兩條只修到「本地 main 追正本」這種變形。現在改成所有候選一起算、順序已經不影響結果,多加候選的成本很低:把其他遠端的 HEAD/main/master,或被推那條本機分支自己的 upstream(`feat@{upstream}` = upstream/main)也列進候選,這兩種形狀就都能解。這條只影響 block 模式,warn 只印。

## 驗過、沒發現問題的(不列 finding)
- git-flow 的 hotfix 分支首推(遠端 HEAD = develop,另有 origin/main):所有候選一起算以後,從 main 的頂端算起,不再把 main 上以前的 hotfix 算進來。這裡比修正前的「照順序取第一個」正確。
- 推主線本身:本機(遠端 HEAD、main@{upstream}、origin/main 全部指到被推的那條,都被跳過)與 CI(checkout 用 `-B main refs/remotes/origin/main` 建的 upstream 也等於被推的那條)都退回用 before,轉正照擋。Actions 樣子的工作目錄推預設分支 develop 本身,兩段 shell 都 rc=1,印「一般增量推送:從遠端舊值算」。
- tag:`--pushed-ref refs/tags/v1` 不會跳過任何候選;tag 指在預設分支上就判成沒有新東西、rc=0,在 ci.yml 與範本上實測都一樣。
- CI 補 origin/HEAD 那段 shell,用 `_dr_actions_checkout` 造的目錄加 `bash -e` 實測,ci.yml 與範本結果一致:DEFAULT_BRANCH 是空的 → 不補;預設分支不存在 → 不補,也不會讓 -e 中斷;已經有 origin/HEAD(指到 main)→ 保持原樣;origin/HEAD 是懸空的 symref(指到已刪分支)→ 驗證會失敗,就改指到預設分支。這一段本身沒有會讓那步紅的路。
- 判不了:注入 `merge-base --all` 或 `symbolic-ref` 逾時 → block rc=1、warn rc=0,印「判不了」與起點說明。`--is-ancestor` 或 `rev-list --count` 逾時照原本的設計不算判不了,起點照算,不會崩。掛鉤只有 rc=1 才擋,warn 印完就放行;off 在判不了之前就先跳過。
- `--push-remote` 和 `--pushed-ref` 只給一個 → 回 2;掛鉤兩個一定一起給,空字串也不是 None,不會誤觸。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區:這次改的是 drift check 的起點與 CI 的 drift 那一步,code-loop check 的呼叫條件沒動。不影響。
- Systems/存量漂移守衛:WHY 行改成「補 before、補 origin/HEAD、呼叫那幾行逐字相同,只差直譯器名與回傳碼處理」,跟 `_dr_ci_call_lines` 的比對範圍一致,我實跑兩段 shell 行為也一樣。不破壞。
- Systems/每支檔有家、Systems/筆記內容閘:這兩道(以及筆記內容審的四個呼叫點,`scripts/lumos:26014` 等)都不帶 push,`_note_audit_start` 沒帶 push 時照舊走 `_lens_push_base`;判不了那條分支只有帶 push 才會走到。不影響。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言):新的 `t_ci_drift_default_branch_shapes` 先斷言沒有 origin/HEAD 而且不補會擋;`t_drift_check_push_start_edges` 先斷言注入的失敗真的打到那一次查詢,也先斷言範圍裡有要處理的東西。符合。F1 與 F3 的形狀沒有測試格,這是涵蓋率缺口,不算違反這條合約。
- Systems/anchor-integrity:anchor-baseline 跟著 test_lumos.py 更新了雜湊與 note,四支相關測試在 clone 裡都綠。不破壞。
- Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 只動 sentinel 之間)、Systems/lumos-cli-read ★INVARIANT★(search 過濾 superseded):這次沒碰 CLAUDE.md 注入或 search。不影響。
- Systems/bound-tests-gate(只列名):PITFALL 行寫「其餘全部一起算分岔點…取離頂端最近的」。F2 的兩個分岔點形狀、F3 的標準 fork 佈局下這句不成立,屬於筆記說法大於實際行為,修 F2、F3 的時候一起改。
- 其餘只列名的節點(canary-audit、design-loop、guard-kill、slim-*、lumos-deinit、cochange-guard、節點範圍與索引守衛、check-r-guard、規格落成、雙向門、逃逸自動記):這次修正沒有碰到它們宣稱的行為。

最高等級:minor
