severity: minor

# 邊界-sonnet 席 第 2 輪報告

實驗環境:`git clone --shared` 臨時目錄,把 pp_mainline / pp_drift_range 原樣抽出來跑,並逐字跑 CI 那段 shell。

## F1 遠端宣告的預設分支排在本地過期的 main/master upstream 之後,舊 master 會劫持起點
severity: minor
blocking: 否
引句:「local _c _cands=("main@{upstream}" "master@{upstream}")」
佐證行:file: `scripts/hooks/pre-push:58`
敘述:
1. 輸入:主線其實叫 trunk(遠端 HEAD 已設成 trunk,`git remote set-head fork trunk`),但本地還留著一個舊 `master` 分支,upstream 指到過期的 `fork/master`(停在第一個提交)。新分支 feat2 從 trunk 頂端開出、加 1 個提交,`pp_drift_range 全0 <feat2>`。
2. 走到:pp_mainline 依序先試 main@{upstream}、master@{upstream},舊 master 先命中,`refs/remotes/fork/HEAD` 根本沒被問到。
3. 實測輸出:RANGE 起點是第一個提交,`git rev-list` 該範圍有 3 個提交,真正新的只有 1 個。多出來的 2 個是 trunk 上別人的提交,被當成這次新分支帶進來的。block 模式下就是註解自己說要避免的那種誤擋。
4. 這跟 lumos 自己的 _mainline_ref 只認 main/master 是同一種取捨,所以歸為 minor。修法方向:遠端宣告的預設分支優先,或取候選裡最新的一個。

## F2 CI 起點補法對「多提交的新分支首推」與「force push」只查頂端一個提交
severity: minor
blocking: 否
引句:「改用這次頂端的第一個父提交(至少查到這次推送的最後一個提交;頂端沒有父提交就從空樹比)」
佐證行:file: `.github/workflows/ci.yml:143`
敘述:
1. 輸入:before 是全 0(新分支首推)、空字串、或 force push 後本機找不到,而這次推了 N>1 個提交。
2. 走到:補法把起點設成 `$SHA^1`,範圍是 `父..頂端`,只含最後一個提交的差異。
3. 壞在哪:CI 是 `--no-verify` 的後盾。第 1 個提交造成的漂移(例如把計劃轉正而留著預告句),只要後面還有別的提交,CI 這步不會看到。實測:一個提交的 repo 三種 before(空/全 0/全 f)都補成空樹起點;多提交時起點固定是頂端的父提交。checkout 用 fetch-depth: 0,origin/* 都在,merge-base 取分岔點原本做得到,舊做法(交給 lumos 從主線分岔點算)反而涵蓋整段。作者已在註解承認「至少」,但沒附回頭重驗的條件。
4. 同一段字也被逐字放進 `_DRIFT_CI_STEP` 給所有消費專案,影響面是全部消費專案。

## 已驗證沒問題的極端輸入(不是 finding,供收貨端對照)
- 遠端名含 `'`、`;`、`@{`、空白,或遠端是 URL(`git@github.com:a/b.git`、含空白的路徑):變數都加引號,rev-parse 靜默失敗,落到「找不到主線」的提醒與原範圍交給 lumos,沒有崩潰也沒有誤擋。
- 分支名含斜線:掛鉤只用 sha,不碰 ref 名。
- 主線叫 trunk:遠端 HEAD 設了就找得到;沒設也沒 main/master upstream 就走提醒路徑。
- 孤兒分支(沒有共同祖先)、只有一個提交的 repo:merge-base 空,`_DR_NOTE` 有講,範圍交給 lumos;實跑 `drift check`,回傳碼 0。
- 帶註解的 tag、tag 指到已在主線的提交:merge-base 會剝殼,起點落在提交本身,範圍為空,不重查。tag 指到 blob:走「沒有共同祖先」提醒。
- CI before 為空、全 0、40 個 f、本機不存在:三者都補成頂端的父提交,單提交 repo 補成空樹。淺層 clone(depth 1)補成空樹後,lumos 回「淺層算不出範圍,這次不查」rc 0,不是錯誤。
- workflow_dispatch:該步 `if: github.event_name == 'push'`,不跑。
- `set -u` 下 `_cands` 陣列一定非空、`${1:-}` 有預設,bash 3.2 可用。管線 `merge-base | head -1` 沒有 pipefail 也沒有 set -e,不會提前退出。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區:這份 diff 沒動 code-loop 那段,也沒動它用的 _range,不影響。
- Systems/存量漂移守衛(家):掛鉤與 CI 行為與該節點描述相符,起點補法的說明寫進了家,不影響。
- Systems/每支檔有家、筆記內容閘:兩道閘的 _hrange / _range 沒改,不影響;新開的 Issue 承認它們有合過主線多算的問題並附 test 綁定,不影響。
- Systems/測試假綠形態 ★INVARIANT★:diff 沒有修 bug 用的還原翻紅釘被拿掉,不影響。
- Systems/anchor-integrity:anchor-baseline.json 有跟著更新,不影響。
- Systems/lumos-cli-lifecycle、lumos-cli-read ★INVARIANT★:re-inject 與 search 排除 superseded 都沒被碰,不影響。
- 其餘超出上限只列名的節點:沒讀全文,不下判定。

最高等級:minor
