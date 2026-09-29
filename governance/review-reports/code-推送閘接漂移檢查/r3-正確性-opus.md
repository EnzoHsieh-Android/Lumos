severity: minor

# 推送閘接漂移檢查 代碼審 r3 — 正確性席(opus)

實驗環境:`git clone --shared <repo 根> .../82c93a23-.../scratchpad/hk3`(HEAD 74dc5185,含 fc25e1e4)。重現腳本都在 `.../82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/opus3/`,載入 clone 裡的 `scripts/test_lumos.py` 借用它的現場工具(`_dr_push_repo`、`_dr_hook_start`、`_dr_ci_run`、`_dr_ci_bodies`),lumos 是真的。跑法:`cd <clone> && /opt/homebrew/bin/python3 <腳本> <clone>`。本機 git 2.39.2。

總評:三支新函式在「單一主線叫 main/master、遠端只有一個」這種形狀(工具鏈與目前的消費專案都是這樣:工具鏈遠端叫 Lumos、沒有 Lumos/HEAD、main 追 Lumos/main;pos-api/pos-ios/pos-guest 只有 origin/main)下,每條分支都做到宣稱的事;新測試對我試的 10 種還原都會翻紅。找到的三個洞都要「不是單一主線」加上 block 模式才會誤擋,跟 r2 對 git-flow/fork 的定級一致,都定低。

## F1 跳過「被推的那條」只比分支短名、不比遠端,推 fork 的 main 時把另一個遠端的真主線也跳過
severity: minor
blocking: 否
引句:「if pushed is not None and _push_mainline_branch(repo_root, cand, remote) == pushed:」
file: `scripts/lumos:33134`
file: `scripts/lumos:33096`

1. 宣稱是跳過「就是這次被推的那條分支」,也就是 `<推送遠端>/<被推分支>`。但 `_push_mainline_branch` 對 `main@{upstream}` 回的是去掉「那條本地分支自己設定的遠端名」之後的短名,比對時不管那個遠端是不是這次推送的遠端。所以本地 main 追 `upstream/main`(正本)、推到 `origin`(自己的 fork)時,`upstream/main` 短名也是 `main`,會被當成「被推的那條」跳過。
2. 輸入(fork 同步,`opus3/exp_fork.py` 的 E1 段):origin=fork 裸庫(main 停在 M0,設了 origin/HEAD→origin/main),upstream=正本裸庫;本地 main `-u` 追 upstream/main;別人在正本上 U1 settle、預告句留著;本地 main=U1,`git push origin main`,也就是 stdin `refs/heads/main U1 refs/heads/main M0`,參數 `origin <fork>`。
3. 走到:origin/HEAD→main 跳過(對)、main@{upstream}=upstream/main 短名 main 跳過(錯)、origin/main 跳過 → `_no_mainline` → 用遠端舊值 M0 → M0..U1 把正本上別人的轉正算成這次的。
4. 輸出:`E1 同步 fork 的 main(git push origin main):rc= 1 | 存量漂移檢查:起點——找不到主線(…或就是這次推的分支),用遠端舊值 2e3a70e026af 當起點`。同一個輸入給 r2 版掛鉤(dca86f7d 的 pre-push,`opus3/exp_fork_old.py`)是 `E1 r2 掛鉤 rc= 0`,範圍 `U1..U1`,所以這是這一輪引入的。正確答案是 upstream/main 已經包含頂端 → 沒有新東西。
5. 修法方向:候選的遠端跟 `remote` 不同時不跳過,也就是只跳過 `refs/remotes/<remote>/<pushed>`。

## F2 遠端 HEAD 排第一,fork 流程裡蓋過比較新的 main@{upstream}:新功能分支首推把正本上別人的轉正算進來
severity: minor
blocking: 否
引句:「cands = ([f"refs/remotes/{remote}/HEAD"] if remote else []) + ["main@{upstream}", "master@{upstream}"]」
file: `scripts/lumos:33128`
file: `scripts/test_lumos.py:51472`

1. r2 把候選順序改成遠端 HEAD 優先,是為了修 git-flow 和「主線叫 trunk、本地留著過期的 master upstream」這兩種報上來的輸入。fork 流程剛好反過來:推送遠端(fork)的 HEAD 指到 fork 自己沒同步的 main,本地 main 追的正本 main 才是新的。這一輪只修了報上來的那一邊。
2. 輸入(`opus3/exp_fork.py` 的 E2 段,現場同 F1):從最新的 main(=U1)開 feat、只帶一個無關改動,首推到 fork,也就是 stdin `refs/heads/feat F refs/heads/feat 0…0`,參數 `origin <fork>`。
3. 走到:origin/HEAD→origin/main(停在 M0)先命中 → 分岔點 M0 → M0..F 包含 U1。
4. 輸出:`E2 新功能分支首推到 fork:rc= 1 | 存量漂移檢查:起點——新分支首推:從跟主線(refs/remotes/origin/HEAD)的分岔點 2e3a70e026af 算`;對照 `E2 直接 U1..F(正確起點)rc= 0`;r2 版掛鉤同一輸入 `E2 r2 掛鉤 rc= 0`。
5. 固定順序兩頭顧不到。候選逐一算合併基底、取最新的那個(是其他基底後代的那一個),git-flow、trunk、fork 三種都能過。`t_prepush_drift_start_mainline_shapes` 的 ①② 目前釘住的是順序,改法要讓它們照樣綠。

## F3 CI 裡沒有 origin/HEAD,「origin 的預設分支優先」在 Actions 上不成立:預設分支不叫 main/master 的專案,CI 跟掛鉤算出不同的起點
severity: minor
blocking: 否
引句:「跟主線(origin 的預設分支優先、跳過就是這次推的那條)的分岔點與 before 取比較新的」
file: `.github/workflows/ci.yml:152`
file: `scripts/lumos:28462`
file: `scripts/test_lumos.py:51605`

1. ci.yml 和健檢範本(`_DRIFT_CI_STEP` 的註解)都寫主線以「origin 的預設分支優先」。但 actions/checkout 是 `git init` + `remote add` + 帶明確 refspec 的 `git fetch`,不會產生 `refs/remotes/origin/HEAD`。CI 裡候選實際上從 main@{upstream}(只有推 main 時才有本地 main)、origin/main、origin/master 開始算。掛鉤那邊 `git clone` 會設 origin/HEAD,所以同一次推送,掛鉤跟 CI 用的主線不一樣。這跟 commit 說明的「起點跟推送前同一支算」不一致:函式是同一支,輸入不同。
2. 重現方法:用 checkout 的指令序列在本機模擬 CI 工作目錄(`opus3/exp_ci_gitflow.py`、`opus3/exp_ci_trunk.py`),也就是 `git init`、`git remote add origin <bare>`、`git fetch origin +refs/heads/*:refs/remotes/origin/* +refs/tags/*:refs/tags/*`、`git checkout --force -B <br> refs/remotes/origin/<br>`,再用 `_dr_ci_run` 真的跑 ci.yml 那段 shell,裡面叫的是真的 lumos。
   - git-flow(裸庫 HEAD→develop;feat 合過 develop,develop 上 D1 是別人的轉正):`CI 合過 develop 再推: origin/HEAD 存在=False … rc=1 | …一般增量推送:從遠端舊值 914c42d35fd5 算`;新分支首推:`CI 新分支首推: origin/HEAD 存在=False … rc=1 | …從跟主線(refs/remotes/origin/main)的分岔點 09301cd80dc5 算`;對照正確起點 `直接 D1..F2 rc= 0 直接 D1..NB rc= 0`。
   - 預設分支叫 trunk、沒有 main/master:`CI trunk 新分支首推 rc= 1 | …找不到主線…新分支首推:從空樹算(截到上線點)`;同一次推送在本機掛鉤(有 origin/HEAD)是 `rc= 0 …從跟主線(refs/remotes/origin/HEAD)的分岔點 57e4e7e992a3 算`。trunk 這種情況 r2 的 shell 補法只看頂端一個提交,這一輪變成從上線點起全算,新分支首推每次都會把上線以來主線上別人的轉正帶進來。
3. 結果是 block 模式下,本機放行的推送到 CI 被標紅。`t_prepush_drift_start_mainline_shapes` ① 的 git-flow 只測掛鉤,而且是手動 `symbolic-ref` 設的 origin/HEAD;`t_ci_drift_start_shapes` 只測主線叫 main 的情況。所以測試全綠,但 CI 的 git-flow/trunk 沒被驗到。
4. ⚠ 「Actions 上沒有 origin/HEAD」是照 checkout 的指令序列在 git 2.39 上模擬出來的,沒有在真的 Actions 上跑。較新的 git(2.48 起 fetch 會補 remote HEAD)在帶明確 refspec 時補不補,我沒驗到。
5. CI 可以直接拿到預設分支:`${{ github.event.repository.default_branch }}`。交進工具當主線候選,或在呼叫前 `git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/<它>`,就不用靠 origin/HEAD。

## 查過、判成立的分支(沒有 finding)

- `_push_range_start` 三種找不到主線的舊值(真的跑,`t_ci_drift_start_shapes` ⑤ 之外也逐條手驗):舊值找得到用舊值;全 0 用空樹(截到上線點);找不到用 `tip^1`,沒有父提交用空樹。說明都照實講。
- 頂端已在主線上 → None 並記 skipped:tag 指到主線上的提交、分支重設到主線上的提交,都判「沒有新東西」,對。
- `_push_pick_base`:合過主線(基底 M1 不是舊值祖先 → 用 M1)、重定基底 force push(同理)、amend/squash 但主線沒動(基底是舊值祖先 → 用舊值)、交叉合併兩種先後(M1 不是舊值祖先 → 用 M1)、合過主線之後的增量(M1 是舊值祖先 → 用舊值),都對。
- 推主線本身:掛鉤裡 origin/HEAD→main 跳過、main@{upstream} 跳過;CI 裡 main@{upstream}=origin/main 跳過(checkout -B 從遠端追蹤分支建分支,會設 upstream)。兩邊都退到用 before/舊值,轉正照擋。工具鏈的真實設定(遠端叫 Lumos、main 追 Lumos/main、有 Lumos/release)也照這條路走,推 release 用 Lumos/main 當主線。
- 附註標籤:`_lens_full_sha` 會剝到提交。用 `git tag -a` 做的 v1 首推,`_push_range_start(z, <tag 物件>)` 回主線分岔點,掛鉤 rc=1,自己帶進來的轉正照擋(`opus3/exp_tag.py`)。
- 用網址推:`_PP_REMOTE` 是網址,帶遠端名的候選 rev-parse 失敗,自然略過,沒有誤判。
- 刪除分支:掛鉤在 `_lsha` 全 0 時整段 continue;工具端終點全 0 也先回 0。
- `pp_stop_if_signaled` 的五處接法:在 `/bin/bash` 3.2.57 和 homebrew bash 上真的對整個行程群組送 SIGINT(`opus3/sig.py`,模擬 Ctrl-C;掛鉤有 `trap … EXIT INT TERM` 但不離開)。spec-gate 管線的 `PIPESTATUS[0]` 在 trap 跑完後還是 130,code-loop 的 `$(…) || cl_rc=$?` 也拿到 130,兩者都停下。只殺子行程(SIGTERM)的情況,新測試已經涵蓋。
- 新測試的殺傷力(`opus3/mut.py`,每支還原後清 `__pycache__` 再跑四支新測試,十種都翻紅):不跳過被推的那條(ref_shapes ⑤b、ci ④⑤ 紅);upstream 排回遠端 HEAD 前面(mainline ①② 紅);只看第一個基底(mainline ③ 分支先合 紅);分岔也用舊值(ref_shapes ②③、mainline ①③、ci ① 紅);upstream 短名判不出(ref_shapes ⑤b、ci ④ 紅);拿掉「頂端已在主線」(ci ⑤ 紅);全 0 不用空樹(ref_shapes ⑦ 紅);拿掉 spec-gate 那行停下(stop_on_signal 前置計數與 spec-gate 格紅);掛鉤不帶 `--push-remote/--pushed-ref`(ref_shapes 13 格、mainline 4 格紅)。

## 圖譜鏡頭逐條判定

- Issues/code-loop守衛main-direct盲區〔事故〕:不影響。code-loop check 的範圍 `_range` 和 `--branch` 綁法沒動,這次只在它後面加一行 `pp_stop_if_signaled`。main-direct 推送照樣無條件叫 check。
- Systems/存量漂移守衛〔家〕:WHY 行改寫成「起點由 _push_range_start 算」,跟程式一致。但「CI 那步也交給同一支」只在主線叫 main/master 時等價,見 F3。
- Systems/每支檔有家〔家〕:只補一句被中斷時停下,跟程式一致。home check 自己的範圍(`_hrange`)沒動。
- Systems/筆記內容閘〔家〕:note-shape 呼叫的範圍沒動,只加停下,不影響。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要配前置斷言證明現場成立):四支新測試都先證明現場,比如「舊掛鉤被殺掉的閘照放行」「原樣範圍直接交 lumos 會擋」「舊 shell 補法在同一輸入算錯」「兩個合併基底真的存在」,再看修法。我的十種還原全翻紅,符合。
- Systems/anchor-integrity ★RISK★:anchor-baseline 更新了 pre-push 與 test_lumos.py 的指紋和 note,這是正常換版,不影響合約。
- Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 只動 sentinel 之間):這次沒碰 inject/CLAUDE.md,不影響。
- Systems/lumos-cli-read ★INVARIANT★(search 排除 superseded 不排除 stale):這次沒碰 search,不影響。
- 其餘只列名的(bound-tests-gate、canary-audit、design-loop、guard-kill、slim-*、規格落成可驗收條件、雙向門放行、逃逸自動記、lumos-deinit、cochange-guard、節點範圍與索引守衛、check-r-guard):這次對 pre-push 的改動只有「漂移那道改交參數」和「五道加停下」。spec-gate 的 rc1 擋與 fail-open 放行語意沒變,只是 ≥128 從放行改成停下。逃逸自動記在 code-loop rc1 那段,沒動。bound-tests-gate 那篇的 PITFALL/WHY 行跟程式一致,但同樣有 F3 的 CI 前提。

最高等級:minor
