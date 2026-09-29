severity: major

## F1 沒設 upstream 的專案,新分支首推會被主線上「別人已推過」的舊帳誤擋(掛鉤註解說會避開,實際沒避開)
severity: major
blocking: 是
引句:「lumos 用共用的推送起點判法(跟主線的分岔點;頂端已在主線就不查)」
佐證行:file: `scripts/lumos:33039`(_lens_push_base:起點是全 0 時只認 main@{upstream}/master@{upstream},找不到主線就回空樹)
佐證行:file: `scripts/lumos:24138`(_nodehome_clamp_base:空樹起點被截到上線點,整段上線後的歷史都算「這次推送帶進來的」)
1. 掛鉤刻意把 `$_rsha..$_lsha` 原樣(新分支時是 000..sha)交給 lumos,理由是「lumos 會從跟主線的分岔點算」。這句只在本地 main 設了 upstream 時成立。`git init` 後 `git push origin main`(沒加 -u)、或主線叫 develop/trunk 的消費專案,`_mainline_ref(remote_only=True)` 回 None,工具退到「空樹,截到上線點」。
2. 同一個掛鉤裡另一道閘早就有更準的算法(`git rev-list --topo-order --reverse "$_lsha" --not --remotes` 找最早一個不在任何遠端的提交)——這道沒用。
3. 重現(臨時 clone --shared 目錄,腳本 `scratchpad/conc-repro1.py`,用測試檔的 `_dr_repo` 造 block 模式專案):main 上有一筆舊版轉正留著預告句的守衛紀錄(已 push 到遠端 origin/main,main 沒設 upstream),再開一個只改 README 的 feat 分支,呼叫 `drift check --diff 0000000000000000000000000000000000000000..<feat 頂端>`:
   - 沒 upstream:`存量漂移檢查:新分支首推:找不到主線,從空樹算(截到上線點)` → `擋下:這次推送有 4 處要處理` → rc=1(全是 Verification/G.md 的 c1,與這次推送無關)
   - 只加一行 `git branch --set-upstream-to=origin/main main` 後同一範圍:`從跟主線(main@{upstream})的分岔點算` → rc=0
4. 影響:專案把 drift_check.gate 設成 block 之後,這類專案每個新分支的第一次推送都會被別人的舊帳擋(得 ack、fix 別人的筆記或 LUMOS_SKIP_DRIFT_CHECK)。預設 warn 只印不擋,所以只在切 block 時才咬人。CI 那步同一個原因(before=全 0)在沒有 main upstream 的 checkout 也一樣,雖然 note-shape 那步前面有 `git branch --track main origin/main` 墊著。

## F2 掛鉤註解說「最壞 60 秒」,預算只罩得住判定本體;前置的 git 呼叫不在預算內,還會因逾時走「放行」
severity: minor
blocking: 否
引句:「這道最壞 60 秒、全套 8 分鐘,便宜的先跑」
佐證行:file: `scripts/lumos:28250`(cmd_drift_check:deadline 是在 _note_audit_resolve、_nodehome_list 之後才起算)
佐證行:file: `scripts/lumos:33068`(_lens_git 單次逾時 20 秒,逾時回 None)
1. 重現:在 PATH 前面放一支 git 包裝腳本,每次呼叫先 sleep 6 秒再轉給真 git(一次正常執行實測共 18 次 git 呼叫),gate=block,`drift check --diff 618ee85f..HEAD`:總共 1 分 49 秒才回,rc=0、沒有任何輸出——前置約 10 次呼叫在預算外,預算只罩後段。單 ref 上限實際是「前置最多約 10×20 秒」+60+20。
2. 同一支包裝腳本改成每次 sleep 21 秒(超過 20 秒逾時):40 秒後印出 `擋下:範圍 618ee85f..HEAD 的終點在本機找不到——範圍寫錯了?`、rc=2。掛鉤把 rc 2 當放行,所以 git 慢(負載高、網路家目錄)時 block 模式靜靜放過,訊息還講成範圍寫錯;跟 `_drift_check_core` 文件寫的「判不了算要處理——放行等於一條繞過的路」相反。CI 後盾會補,但本機使用者看到的是一句誤導的「擋下」然後推送照走。
3. 多 ref 一次推(`git push --all`、多個 tag)每個 ref 各跑一次,上限線性相加;註解只講單次。

## F3 新掛鉤配舊工具、新 CI 步驟配舊工具的行為
severity: minor
blocking: 否
引句:「"$PY" "$GRAPHCTL" drift check --diff "$_rsha..$_lsha" --repo "$REPO_ROOT" || dr_rc=$?」
引句:「python scripts/lumos drift check --diff "$BEFORE..$SHA" --repo . || {」
佐證行:file: `scripts/lumos:37571`(drift 子命令登記在 07e5bc96 之後才有)
1. 舊工具(取 07e5bc96^ 的 scripts/lumos)跑 `drift check --diff HEAD~1..HEAD --repo .`:印 `擋下:沒有「drift」這個指令。` + `lumos --help` 提示,rc=2。掛鉤 rc≠1 放行,所以「消費專案裝了新掛鉤、工具是舊版」不會擋推送(正確);代價是每個 ref 一次「擋下:…」字樣卻照樣推出去,容易被當成真擋。
2. CI 那步 rc≠1 一律 `exit "$rc"`:工具比 ci.yml 舊(回滾工具但留 CI 步驟、或消費專案照 doctor 貼了步驟又降版)時,rc=2 讓 CI 每次推送都紅。加了又拿掉 CI 步驟沒有殘留狀態(步驟不寫檔);只拿掉掛鉤區塊、留 CI 步驟,上線點由 `git log -S"drift check"` 在歷史裡找,不受影響。
3. 反向(舊掛鉤配新工具):掛鉤不叫 drift check,工具的 doctor 只多唸「專案 CI 沒呼叫」之類提醒,不擋。

## F4 使用者中斷(Ctrl-C/TERM)時,rc 130/143 被當放行,掛鉤 trap 不退出、會往下接著跑全套
severity: minor
blocking: 否
引句:「rc 不是 0 也不是 1(參數錯)→ 放行,跟上面每支檔有家、筆記形狀擋同一種處理。」
佐證行:file: `scripts/hooks/pre-push:193`(trap 'impact_done; rm -rf "$_PP_TMP"' EXIT INT TERM,不含 exit)
1. drift check 自己不建暫存檔(drift 區段沒有 tempfile/mkdtemp),治理帳只在結尾用單次 append 寫一行,中斷不會留半個檔或半筆帳。這部分乾淨。
2. 但 python 被 SIGINT 殺掉回 130,`|| dr_rc=$?` 之後 130≠1 → 放行。用同樣 trap 結構的最小腳本(`scratchpad/conc-trap.sh`)重現:子行程自殺 SIGINT 後輸出 `TRAP`、`dr_rc=130`、`CONTINUES to full tests`,trap 清掉暫存目錄後腳本仍往下跑。trap 是舊有的,但這條新路徑多了一個把 130 當「放行」的明文規定;需要 rc≥128 也 `exit` 才對。

## 併發(兩個推送同時跑)
- 沒有共用暫存檔:掛鉤自己的暫存目錄是 `mktemp -d` 各用各的;drift check 讀的是頂端提交的 git 物件(`_drift_tree_env(root, tip, …)`),不讀工作目錄,同時改檔或同時推不互相影響。
- 唯一共用的是 docs/.governance-log.jsonl 單行 append,一行一次 write,兩個推送同寫時最多交錯行序、不會撕裂。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區:不影響。這次新增的呼叫在 code-loop check 之後、不動它的 tier/分支判定與留痕;drift 那步不看分支名(分支與 tag 都查),不會把 main-direct 盲區重開。
- Systems/存量漂移守衛:符合其「推送前+CI 雙層」;F1 是其起點判法在沒有 upstream 時對新分支的缺口。
- Systems/每支檔有家、筆記內容閘:不影響。掛鉤裡兩者的 rc 處理照舊,新步驟只是排在後面。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要有前置斷言證明現場成立):本審材只審掛鉤與 CI 行為,未逐條核對新測試 t_prepush_and_ci_wire_drift_check 的前置斷言,不下判。
- Systems/anchor-integrity ★RISK★:掛鉤改了、anchor-baseline.json 同一批已重簽,對得上。回滾提醒:只手刪掛鉤區塊而沒同時還原 baseline,會被 anchor verify 擋(「負責把關的檔案跟登記過的版本不一樣」);整個 revert 提交則 baseline 一起回。
- Systems/lumos-cli-lifecycle(re-inject 保留 sentinel 之外):不影響,沒動 CLAUDE.md 注入。
- Systems/lumos-cli-read(search 預設排除 superseded):不影響。
- 其餘「超出上限,只列名」的節點:未逐篇讀,不下判。

最高等級:major
