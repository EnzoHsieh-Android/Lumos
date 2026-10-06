severity: major

# 第 2 版 正確性/邏輯審查(sonnet)

實測方式:在 mktemp 風格臨時 repo(scratchpad/exp/w,主線 2 個提交、feat 分支 3 個提交、註記標籤)直接載入 `scripts/lumos` 呼叫 `_push_range_start`,並讀 `scripts/hooks/pre-push`。

## F1 遠端舊值本機找不到又找不到主線時,會擋的閘只掃最後一個提交,比今天鬆
severity: major
blocking: 是——會擋的閘少掃、該擋的放行,違反 spec 自己宣稱的「失敗一律退回空樹、不會更鬆」。
位置:「做法」第 1 點、「範圍」的 `pp_block_range_for`、「實務隱患」的舊版 lumos 與「遠端名是網址或空的」兩條、守衛面、[S7]。
引句:「找不到主線時全零起點回空樹(同今天)」
引句:「失敗一律退回空樹(多擋)」
問題:`_push_range_start` 在「舊值找不到(非全零)」且找不到主線(或跟主線無共同祖先)時走 `_push_no_mainline`,退到頂端的第一個父提交,只查最後一個提交,不是空樹。spec 的隱患段只講了「全零→空樹」這半邊,舊值找不到的那半邊沒講,而 `pp_block_range_for` 恰好把「舊值本機找不到」也導到這支函式,所以今天走空樹(多掃)的情形,改後變成只掃一個提交(少掃)。
具體例(已實跑):feat 上 3 個提交 fa/fb/fc,遠端是 `up`,沒有 main/master 可當主線,遠端舊值 `1111…`(別人 force-push 過、本機沒 fetch)。`_push_range_start(root, 1111…, tip, 'up', 'refs/heads/feat')` 回 `058d5174…`(tip 的父提交)與說明「從頂端的第一個父提交 058d5174ce59 算,只查最後一個提交」。預期(依 spec 與今天):空樹..頂端;實際:父提交..頂端,fa、fb 兩個提交裡的新告警、合約測試牽連、`--touched-from` 檔案全部不進波及與風險分級。
更實際的觸發:(a) 預設分支不叫 main/master(develop、trunk)又沒有遠端 HEAD 符號參照,而且 force-push 蓋掉本機沒有的舊值;(b) force-push 主線本身:`_push_mainlines` 會跳過「就是這次被推的那條」,main 的候選全被跳過,沒有其他主線 → 同一條路;(c) shallow clone 舊值缺物件、merge-base 找不到共同祖先。這些都是 [S7] 要處理的情境,[S6] 的三種情形(頂端在主線、找得到分岔點、git 失敗)沒有涵蓋這一格,所以測試也不會紅。
修法方向(不寫「建議」,指出矛盾點):`push-range` 指令端或 `pp_block_range_for` 端必須對「舊值不是全零、本機找不到、而且回的說明含『只查最後一個提交』/起點是父提交」這一格改回空樹,或 spec 明確改寫成接受這個放寬並進天花板、補一條 [S] 條款與測試;現在兩邊都沒有。

## F2 預設分支不叫 main/master 時,新分支首推仍整個 repo 當新改動,[S1] 在那種 repo 不成立
severity: minor
blocking: 否——退回空樹等於今天的行為,是修不到,不是更鬆;但 spec 沒把這個界線寫進天花板。
位置:「實務隱患」遠端名網址或空的那條、「天花板」。
引句:「找不到主線的方式跟存量漂移檢查同一套;找不到主線時全零起點回空樹(同今天)」
問題:`_push_mainlines` 只認 `refs/remotes/<遠端>/HEAD`、`main@{upstream}`、`master@{upstream}`、`<遠端>/main`、`<遠端>/master`。主線叫 develop/trunk 又沒設遠端 HEAD 時,新分支首推回空樹(已實跑:遠端名給網址或空字串,rc 都是空樹 `4b825dc6…`),誤擋照舊。rtb 這類消費專案若主線非 main/master,本案修不到。
具體例:遠端只有 `origin/trunk`,新分支多 1 個提交首推 → `_push_range_start` 回空樹 → 715 條舊告警照擋。
天花板第 1 條沒列這一格。

## 其他情境逐一查過,已讀,無 finding
- 新分支合過主線再首推([S3]):`merge-base --all` 取到分支實際合進的那個主線提交,範圍只含分支自己的提交與合併提交,實測正確。
- 標籤推送:註記標籤的本地 sha 是標籤物件,`merge-base`/`rev-parse ^{commit}` 都會剝殼,實測結果同分支;頂端在主線時回 None → `頂端..頂端`,pitfalls 判 docs、code-loop check 回 OK、`git diff X..X` rc0 空輸出(已實跑),不會崩;「範圍是空」天花板第 3 條已記。
- 空範圍餵 doctor:`pp_touched_file` 算出空檔時回空字串、`_DOCTOR_ARGS` 不帶 `--touched-from`,等同今天(今天空樹也是全 repo),不是新誤擋。
- 一次推多 ref:每個 ref 獨立算 `_brange`,`_push_mainlines` 的「跳過被推那條」逐 ref 比遠端與分支;刪除 ref 在迴圈與 `pp_touched_file` 都先跳過。無互相污染。
- 遠端名是網址或空:帶遠端的候選自動略過,只剩 `main@{upstream}`/`master@{upstream}`;找不到走全零→空樹,同今天(非全零的那格見 F1)。
- SHA-256 repo:掛鉤 `_ZERO` 是 40 個 0,64 個 0 的舊值 `git cat-file -e` 失敗而走 `push-range`,lumos 端 `_ZERO_SHA_RE` 認 64 位全零,輸出正規式 `{40,64}` 吻合,無問題。
- 一般增量推送([S4]):舊值找得到走 `舊值..頂端`,不呼叫 push-range,同今天。
- 舊版 lumos 無此指令:argparse 錯誤 rc2、印出不合形狀 → 退回空樹,成立(僅限這條,不含 F1)。

## 圖譜鏡頭
派工附的合約/事故節點:任務單只說 hook 會附,本份稿檔內沒有實際附上節點清單,無可逐條判的節點(固定席條目不適用,已讀,無 finding)。

severity 最高 major;blocking 共 1 條(F1)。
