severity: major

# 推送閘接漂移檢查 代碼審 r1:正確性-opus 席

實驗都在我自己的 `git clone --shared` 臨時目錄(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/rc`,頂端 5a496daa)裡跑,直譯器 /opt/homebrew/bin/python3(3.14)。重現腳本:同一個 scratchpad 下的 `expA.py`、`expB.py`、`expB2.py`,用法是 `python3 <腳本> <clone 路徑>`;它們借用 test_lumos 裡的 `_dr_repo`、`_dr_guard_text`,傳給 lumos 的參數跟掛鉤那一行一模一樣。

## F1 功能分支合併或重定基底主線後推送,主線上別人的轉正被算成這次推送的「要處理」
severity: major
blocking: 是
引句:「"$PY" "$GRAPHCTL" drift check --diff "$_rsha..$_lsha" --repo "$REPO_ROOT" || dr_rc=$?」
file: `scripts/lumos:25488`(`_notes_status_flipped` 逐提交讀的範圍是 `git log 起點..頂端`)
file: `scripts/lumos:33039`(`_lens_push_base`:起點在本機找得到就原樣用,不算分岔點)

1. 遠端舊值在本機找得到時,lumos 直接把它當起點,不算跟主線的分岔點(`_lens_push_base` 第一個分支)。只有 40 個 0 或本機找不到時,才走「跟主線的分岔點」那條路。掛鉤註解與 bound-tests-gate 的 WHY 只講了新分支那一種情況。
2. 輸入(block 模式):主線上有一筆「守衛紀錄 pending→pass、預告句還留著」的提交,是 warn 期間或用 LUMOS_SKIP 推上去的。功能分支 feat 已經推過一次。之後 `git merge main`(不用 force,一般推送),或 `git rebase main` 再 force push。
3. 掛鉤交出 `<舊 feat>..<新 feat>`,`git log 舊..新` 把主線那筆轉正也包進來,所以 c1 判成要處理,rc1,推送被擋。訊息還叫推的人去 `lumos drift fix Verification/G 18 --kind c1` 改別人的筆記。
4. 重現輸出:merge 的情況(`expB2.py`)是 `== merge main 進 feat 後一般推送,掛鉤交 remote_sha..local_sha rc = 1`,同一個頂端改從主線分岔點算則是 `rc = 0`。rebase 加 force push 的情況(`expB.py`)是 `rc = 1`(印出 4 筆 c1),從分岔點算是 `rc = 0`。
5. 現在是 warn 模式,所以結果是誤報:每次合併主線的推送都印出一串別人的 c1 與改法,還記一筆 `warned` 帳。這也會汙染計劃 REVISIT:2026-11-28「看 drift-check 閘的擋下與表態」要數的那份帳。改成 block 後就是誤擋。★門檻②量不到這個問題★:門檻②重放的是主線上的單一提交 `<父>..<提交>`,從來不會出現「一段範圍裡夾著主線的提交」,所以三條門檻全過、切成 block 之後才會碰到。
6. 同一支掛鉤的每支檔有家與筆記形狀擋,在起點找得到時也用 `$_rsha..$_lsha`,是同一個形狀,這次沒有處理。但存量漂移看的是「狀態事件」,主線上別人轉正的機率比「新寫的形狀違規」高得多,所以放在這裡講。

## F2 本地主分支沒設 upstream 時,新分支首推照樣把上線後主線的舊帳算進來——跟註解宣稱要避免的誤擋是同一種
severity: major
blocking: 是
引句:「lumos 用共用的推送起點判法(跟主線的分岔點;頂端已在主線就不查)——CI 那步也是原樣交。頂端就是要推的 local_sha。」
file: `scripts/lumos:33090`(`_mainline_ref(remote_only=True)` 只認 `main@{upstream}`、`master@{upstream}`)
file: `scripts/lumos:24138`(`_nodehome_clamp_base`:空樹起點截到上線點)

1. 掛鉤不用 `_range` 的理由(引句前一行)是:「新分支會把主線上線後別人的轉正算成這次帶進來的而誤擋」。原樣交過去後,lumos 要找得到 `main@{upstream}` 或 `master@{upstream}` 才會算分岔點。找不到時,`_lens_push_base` 回空樹,再截到上線點。這正是 `_range` 的行為,註解說要避免的誤擋又回來了。
2. 會碰到的專案:用 `git init` 建、`git push origin main` 沒加 `-u` 的;主分支叫 develop 或 trunk 的。這支掛鉤會裝進所有消費專案(工具鏈與 rtb 我查過都有 upstream,這兩個目前不中)。
3. 同一支掛鉤裡,每支檔有家與筆記形狀擋那段(`_hrange`,用 `git rev-list <頂端> --not --remotes`)不依賴 upstream,同一個情境是放行的。
4. 重現(`expA.py`,block 模式,主線推上去時沒加 `-u`,feat 只加一個無關的檔):
   - `main@{upstream}: ''`
   - 掛鉤交的原樣範圍 `0000..feat`:`rc = 1`、`存量漂移檢查:新分支首推:找不到主線,從空樹算(截到上線點)`、`擋下:這次推送有 4 處要處理`
   - 同一個 feat 用 `_hrange` 的算法:`rc = 0`
   - 補上 `git branch -u origin/main main` 之後,同一個原樣範圍:`rc = 0`
5. ⚠ 目前沒有專案開 block,已知的兩個消費專案也都有 upstream,所以現在的影響是 warn 模式下的誤報。等級照「開 block 後會誤擋、門檻量不到」來定。

## F3 新測試走不到「新分支、原樣交範圍」與「tag 也查」這兩條被測分支,換成 `_range`、或只查分支都照樣綠
severity: minor
blocking: 否
引句:「check("③範圍跟這個 ref 同一段(remote_sha..local_sha)、頂端是要推的提交", f"--diff {base}..{_na_head(root)}" in dr_line, dr_line)」
file: `scripts/test_lumos.py:51070`(`pp()` 餵的 stdin 固定是 `refs/heads/main <頂端> refs/heads/main <base>`,base 在本機找得到)

1. 測試只餵一種 ref:分支,遠端舊值在本機找得到。這時 `_range` 的值剛好也是 `base..頂端`,所以斷言③分不出「原樣交」跟「交 `_range`」。bound-tests-gate 新加的 WHY 把「範圍刻意交原樣的 remote_sha..local_sha、不用 _range」綁在 `[test:t_prepush_and_ci_wire_drift_check]` 上,但這支測試沒有走到新分支(40 個 0)的情境,等於綁了一條證不出這件事的測試。這是測試假綠形態 ★INVARIANT★ 說的第④型:現場走不到被測分支。
2. 翻紅檢查一:把掛鉤那行改成 `drift check --diff "$_range"`,清掉 __pycache__ 後重跑 `-k t_prepush_and_ci_wire_drift_check`,結果 `12 passed, 0 failed`。
3. 翻紅檢查二:包成 `[[ "$_rref" == refs/heads/* ]] && { … }`(tag 不查,推翻註解「分支與 tag 都查」),結果一樣是 `12 passed, 0 failed`。
4. 補法:加一個 `0000… refs/heads/feat` 的新分支情境,並且先斷言現場成立(主線上線後有別人的轉正、新分支只帶無關改動,block 模式下期待 rc0)。再加一行 `refs/tags/…`,斷言 argv.log 裡有 drift check。

## F4「只有 rc1 讓 CI 紅」跟測試⑧、CI 實作對不上:rc2 也讓 CI 紅
severity: minor
blocking: 否
引句:「工具鏈 CI 在 code-loop gate 之後有一步 drift check,範圍是 before..sha,只有 rc1 讓 CI 紅。」
file: `.github/workflows/ci.yml:168`(`exit "$rc"`:非 0 非 1 照原值退出,CI 一樣紅)

1. 同一支測試的⑧斷言 `got == {"0": 0, "1": 1, "2": 2}`,也就是 lumos 回 2 時那一步退出 2,CI 會紅。bound-tests-gate 新 WHY 寫「rc1 才讓 CI 紅」,docstring 寫「只有 rc1 讓 CI 紅」,都跟實作與⑧矛盾。
2. 行為本身照 note-shape 那步的前例(參數錯要看得見),我判是對的。錯的是這兩處說明:該改成「rc1 印擋下訊息;其他非 0 照原值紅」。另外推送前掛鉤對 rc2 是放行的,兩邊處理不一樣,也該在同一句講清楚,免得下一個人照文字把 CI 改成「rc2 放行」。

## 走過但沒出問題的輸入(照抑噪紀律,不列成 finding)
- 刪除 ref(local 全 0):迴圈開頭 `continue`,不叫 drift。
- annotated tag:local_sha 是 tag 物件,lumos `_lens_full_sha` 用 `^{commit}` 剝成提交。
- tag 或新分支開在主線頂端:lumos 回「沒有新東西」、rc0。
- 淺層 clone:lumos 記一筆 skipped-env、rc0。
- `LUMOS_SKIP_DRIFT_CHECK=1`:判範圍前就放行並記帳。
- 找不到 PY:掛鉤前面已經擋下。找不到 GRAPHCTL:掛鉤前面已經 exit 0。
- `set -u` 下 `dr_rc` 有先初始化。drift 那一步 `exit 1` 時,trap 會清掉 `_PP_TMP` 與波及暫存檔。
- CI 殼是 `bash -e`,`python … || { rc=$?; … }` 在 `||` 右側拿得到原本的 rc(測試⑧用 `bash -e -c` 驗過)。
- CI 的 BEFORE 是空的(手動觸發):那一步本來就被 `if: push` 擋掉;補 40 個 0 是多一層保險。
- CI force push 使 BEFORE 不存在:lumos 判「頂端已在主線」,跳過並記帳,這是 lumos 既有、明寫在範圍外的決定。
- 設定檔的各種壞值(gate 寫成整數、status 寫成清單、related 是字串或巢狀、REVISIT 條件寫壞)在 warn 模式下都回 0,沒有噴出 traceback 變成 rc1(`expC.py`)。
- 錨點:clone 裡 `lumos anchor verify` 全綠;`-k python_launcher_blocks_agree`、`-k t_drift_check_state_events_in_range` 全綠。

## 圖譜鏡頭逐條判定
- **Issues/code-loop守衛main-direct盲區(事故)**:不影響。code-loop check 的呼叫與範圍一行都沒動,drift 排在它後面,也只在它沒擋時才跑。main-direct 推送的遠端舊值在本機找得到,drift 從它算,正確。
- **Systems/存量漂移守衛(家)**:about_code 補了 pre-push 與 ci.yml,responsibility 也寫清楚只管「呼叫那一段」。RULE 的撤除條件是「預設改成 block 並接進掛鉤與 CI」,現在只接線、還沒改 block,保留是對的。但新 WHY「淺層 clone、上線點截斷都留在工具裡判」背後的起點判法有 F1、F2 兩個洞,該在這篇補上限制。
- **Systems/每支檔有家(家)**:沒有破壞。pre-push 與 ci.yml 多掛一個家,是寫回落點的變化,不改每支檔有家的判定。
- **Systems/筆記內容閘(家)**:note-shape 那步沒動。新步驟依賴它先做的 `git fetch` 與 `git branch --track main origin/main`,這是隱性的前後依賴,註解有寫。現在不會壞,但以後把 note-shape 那步改成條件執行時,drift 就沒有主線可用(會掉進 F2 的情況)。
- **Systems/測試假綠形態 ★INVARIANT★**:受影響,見 F3。新測試綁著「原樣交範圍」的 WHY,但沒有走到新分支那條路,把修法換回 `_range` 照樣綠。
- **Systems/anchor-integrity ★RISK★**:基準線同步更新了 test_lumos.py 與 pre-push 兩個指紋,clone 裡 anchor verify 全綠。不影響。
- **Systems/lumos-cli-lifecycle ★INVARIANT★(re-inject 只動 sentinel 之間)**:不影響。這次沒動 CLAUDE.md 注入,掛鉤是整支檔跟著 update 走。
- **Systems/lumos-cli-read ★INVARIANT★(search 排除 superseded)**:不影響。沒碰搜尋。
- **Systems/bound-tests-gate**:新 WHY 的順序描述(code-loop 之後、test-layers 與全套之前;CI 的全套在前)跟實作一致。「rc1 才讓 CI 紅」錯了,見 F4;「範圍刻意交原樣」的測試綁定證不出來,見 F3。
- **slim-get、slim-install、slim-uninstall、lumos-deinit**:掛鉤內嵌的 python-launcher 段沒動,`t_python_launcher_blocks_agree` 綠。消費專案 update 後多一次 drift 呼叫,舊版 lumos 不認得 drift 子命令時回 2,掛鉤放行。不影響。
- **canary-audit、design-loop、guard-kill、規格落成可驗收條件、雙向門放行、逃逸自動記、cochange-guard、節點範圍與索引守衛、check-r-guard**:這次沒改它們的呼叫點或判定。spec-gate、escape 的分支在 drift 之前,rc 處理沒變。不影響。

最高等級:major
