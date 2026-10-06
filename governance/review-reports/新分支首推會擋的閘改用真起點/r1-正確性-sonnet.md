severity: major

(正確性/邏輯鏡頭。spec 實際位置 /tmp/首推-r1.md;程式對照 /Users/enzo/harness/lumos-firstpush/scripts/hooks/pre-push。git 行為已在 mktemp 臨時 repo 實測。)

## F1 合過主線的新分支,起點仍把主線的改動算成這次新改動(多擋)
severity: major
blocking: 是 (起點推導會讓誤擋在最常見的流程裡復發,與 spec 目標相反)
spec 段落:做法 1、驗收 S1、PRIOR-ART、範圍「只算那一個提交」。
引句:「找出這次要推的提交裡「還不在任何遠端分支上」的最早那一個,從它的上一個提交算起。」
問題:起點是「最早新提交的第一個父提交」,範圍是兩點 tree diff。分支從主線 M0 切出,主線之後前進到 M1 並已在 origin/main;使用者 `git merge origin/main` 再加提交 c2。最早的新提交是 c1,其 `^` 是 M0,`M0..頂端` 的 diff 含主線 M0→M1 的全部檔案。
實測(臨時 repo):main 有 big 檔(已在 origin/main),feat 有 c1、merge、c2;`git diff --name-only <c1>^..<頂端>` 輸出 big、f、g。big 不是這次的新改動。
具體例:主線那段含舊寫法或高風險寫法時,新增告警閘與風險分級照樣把它算成新的,誤擋復發。這就是 spec 自己 related 列的 [[Issues/推送前其他閘的範圍在合過主線時會多算]],spec 把它丟給 RETIRE-IF,卻在 S1 宣稱「風險分級只算那一個提交」。S1 只測「比主線多一個乾淨提交」,沒覆蓋合過主線這個最常見情境。
合併提交當最早新提交時也一樣:本機把 origin/a 合進 origin/b 後推新分支,`_hold^` 只取第一父,另一邊的整段都算進來。
出路方向:起點改取 `git merge-base <頂端> <遠端追蹤分支們>`(或對每個 --remotes 分支取 merge-base 後挑最新),不用「最早新提交的 ^」。S1 加一條「分支合過主線」的案例。

## F2 全部已在遠端就整段放行,讓「換個新名字再推」成為穩定繞法(放行該擋的)
severity: major
blocking: 是
spec 段落:實務隱患「全部已在遠端」、範圍第 2 點(空範圍照常走完)。
引句:「會擋的那幾步跑空範圍、照常放行;空範圍的風險分級判成只動文件,所以推送前也不跑全套測試」
問題:掛鉤原註解(pre-push 約 :306-:312)明說「無基準倒向保守掃,非 fail-open,否則守衛升格成穩定繞法」。本案把這個性質拿掉。實測:feat 先推到 wip(例如 `--no-verify`,spec 自己的出路),再 `git push origin feat:feat2`,`git rev-list feat --not --remotes` 輸出 0 筆,範圍為空。
具體例:tier=high 的提交以 `--no-verify` 推到 A 分支(CI 當後盾,會標紅),再推成 PR 用的 B 名字:code-loop check 看空 diff 判成低風險,「留痕綁 remote_ref 目的地」的審查留痕要求落空,全套測試也被跳過。實際行為:放行。預期:B 仍需要 high 的留痕或至少不跳全套。
spec 的理由「當初推上遠端那次已過掛鉤」對 `--no-verify`、掛鉤未安裝、別人的機器、CI 紅了的分支都不成立。

## F3 「追蹤分支沒更新只會多擋、不會變小」不成立
severity: minor
blocking: 否 (需要殘留追蹤分支才發生,條件窄)
spec 段落:實務隱患第一條。
引句:「很久沒 fetch 時,遠端其實已有的提交會被當成新的——範圍變大(多擋),不是變小。」
問題:反向也會發生。伺服器端已刪除或 force-push 掉的分支,本機沒 `fetch --prune`,`refs/remotes/origin/<舊分支>` 仍指向那些提交,`--not --remotes` 把它們當「已在遠端」。具體例:PR 被關、分支被刪(伺服器那邊的提交其實已不存在),本機把那段提交推到新名字,範圍變小甚至為空,放行。另外 `--remotes` 含所有遠端:往 fork 推新分支時,只存在於 origin 的提交也算「已在遠端」。spec 的天花板只寫了多擋方向。

## F4 空範圍同時作用於標籤推送與全套測試分層,spec 的「標籤路徑照舊」與程式結構不符
severity: minor
blocking: 否
spec 段落:做法 3、範圍「不做」第一條。
問題:pre-push 約 :371-:372 的 `pitfalls --diff ... --json` 在分支與標籤共用一次呼叫,結果同時餵 `_tier_high`、`_suite_this`、`light_ok`。spec 說「分支路徑的兩處」改 `_brange`、標籤路徑照舊,但 JSON 那次不分路徑。照 spec 改,標籤推送(例如在已推上遠端的提交上打 release 標籤)的 `_suite_this` 與 tier 也由空範圍算出,判成 docs,跳過全套;而標籤路徑下方高風險提醒仍印 `_range` 的命中列表,同一次推送的 tier 與列表依據不同範圍,互相矛盾。spec 要嘛明寫「標籤也吃 `_brange`」,要嘛把 JSON 那次拆成兩次。

## 逐節
- 白話與依據:已讀,無 finding。
- PRIOR-ART/RETIRE-IF:見 F1(`_hrange` 的算法對「合過主線」本來就是有洞的,被當成現成輪子搬用)。
- 範圍:F4。
- 做法:F1、F4。步驟 2「空字串時設成 `頂端..頂端`」本身一致,後果見 F2。
- 實務隱患:F2、F3。多 ref 同推(B 基於同次推的 A)實測不受影響,因為 A 的提交此時還不在遠端追蹤分支上,B 會把 A 的提交也算進範圍;已讀,無 finding。
- 驗收條款:S1 缺「合過主線」(F1)、S3 把 F2 的行為當成預期;S2、S4 已讀,無 finding。
- 回退/天花板:天花板 1 只講「基在別人未合併分支上」,沒講「合過主線」(F1)。
- 本機 fetch 狀態、標籤、多 ref 已逐一檢查:除 F3、F4 外無其他 finding。已存在的遠端分支(增量推送)與缺物件的情況,`pp_block_range_for` 與現行 `_hrange` 逐字等價,無 finding。

最嚴重 severity: major;blocking 2 條(F1、F2)。
