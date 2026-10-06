severity: major

(spec 實為 /tmp/首推-r1.md;計劃節點路徑在 lumos-toolchain 不存在,改讀該檔。對照程式 /Users/enzo/harness/lumos-firstpush。實驗全在 mktemp 目錄。)

## F1 git 查詢失敗與「全部已在遠端」不分,會擋的閘從擋變放行
severity: major
blocking: 是——放寬了會擋的閘,且失敗時靜默放行,不是只放寬誤擋。
spec 段:做法 1、範圍第二條「它輸出空字串(這次沒有新提交)時,這幾道用「頂端..頂端」的空範圍跑」。
引句:「沒有新提交輸出空字串」
問題:file: `scripts/hooks/pre-push:337` 的 `git rev-list ... --not --remotes 2>/dev/null | head -1` 失敗(頂端物件缺、某個遠端追蹤 ref 損壞、被砍)時 `_hold` 也是空字串,跟「真的全部已在遠端」輸出一樣。舊 `_hrange` 只給每支檔有家、筆記形狀擋用,空了就跳過;這是一般檢查的 fail-open 取捨。本案把同一個空字串接到風險分級、code-loop check、雙向門放行、波及計算,於是 rev-list 一失敗,這些閘全跑空範圍:風險分級判 docs,全套測試也被跳過(我實跑 `pitfalls --diff X..X` 得 suite=docs、tier=light;code-loop check 空範圍 rc=0 OK)。舊行為(空樹兜底)是 fail-closed,spec 的守衛面只寫「放寬的部分正是誤擋」,沒承認這條。
具體例:push 的頂端 sha 在本機取不到(`git rev-list deadbeef --not --remotes` 實測 fatal、輸出空)→ `_brange` 空 → `$_lsha..$_lsha` → 全閘放行,不是擋。
修向:函式要分「查詢失敗」(退回空樹,維持舊的保守)與「查了沒有」(空字串)兩種輸出,並寫進 S3 旁的測試。

## F2 頂端含合併提交時,真起點把已在主線的改動算進範圍,S1 的保證只涵蓋「一個乾淨提交」
severity: major
blocking: 是——這是本案要修的誤擋在常見流程(新分支先 merge main 再首推)上沒修掉,spec 卻把它宣稱為「這次真正的新提交」。
spec 段:守衛面「看的範圍變小(從整個 repo 變成這次真正的新提交)」;驗收 S1 只測「只比主線多一個乾淨提交」。
引句:「從整個 repo 變成這次真正的新提交」
問題:起點取「最早新提交的 `^`」,範圍是兩點樹差。分支從 P 分出、之後 main 前進(M1、M2 已在 origin/main),分支內 `git merge main` 後首推:我實跑最早新提交=F1,範圍 `P..tip` 的檔案清單是 f、m1、m2——m1、m2 是別人早已在主線的改動。若 main 的那些提交帶「新增告警」,仍然誤擋;風險分級也被 main 的程式檔拉高。這正是 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 描述的洞,spec 把它列為「天花板 1」只談基在別人分支上,沒談合併頂端。另外多個互不相連的新根(平行分支合併)時 `head -1` 取哪個取決於拓撲排序,起點隨機,範圍可大可小。
具體例:feat 先 merge main 再 push -u → 預期只算 F1;實際含 m1、m2。
修向:S 條款補合併頂端案例;或起點改取 merge-base 與最早新提交上一個的較新者(lumos `_push_range_start` 已有類似),並明講取捨。

## F3 「別人推上遠端的提交本機不再查」的理由前提不成立
severity: major
blocking: 是——放寬的依據寫成事實,但有至少三條路讓遠端提交沒經過任何推送前掛鉤。
spec 段:實務隱患第二點。
引句:「它們被推上遠端那次已經過那個人的推送前掛鉤」
問題:`--no-verify`(本專案掛鉤自己教人用)、網頁介面直接改檔、沒裝掛鉤的機器、fork 貢獻者的分支,都會讓提交在遠端卻沒過掛鉤。舊算法首推時整段重掃,是這些提交唯一的本機補查;本案之後,先 `--no-verify` 推一個壞提交到分支 A,再從 A 長出新分支 B 首推:B 只算 B 的新提交,壞提交永遠不在任何本機閘的範圍。CI 後盾有效但 spec 沒把「--no-verify 一次後污染可傳遞」列為接受的風險,而且 code-loop 留痕是「綁版本」的,跳過帳不會跟著搬。另 `--remotes` 是所有遠端的聯集,不分推送目標:`git remote add backup` 後第一次 `git push backup main`,所有提交都已在 origin/* 上 → 空範圍 → 全閘放行,而目標遠端的 CI 可能完全不同。
修向:把這兩條寫進實務隱患並附回頭條件,或至少限定只看被推送遠端(`refs/remotes/$_PP_REMOTE/*`);直接推網址時 `$_PP_REMOTE` 是網址,要退回舊算法。

## F4 「遠端追蹤分支沒更新」只講了會多擋,漏了反方向(追蹤 ref 比遠端新)
severity: minor
blocking: 否——放行方向的偏差,CI 兜底,且需要特定前提。
spec 段:實務隱患第一點。
引句:「很久沒 fetch 時,遠端其實已有的提交會被當成新的——範圍變大(多擋),不是變小。」
問題:反方向也存在:遠端分支被伺服器端刪除或強制重設(合併後自動刪分支、為移除壞提交 force reset)而本機沒 `fetch --prune`,本機 `origin/X` 仍含那些已不存在的提交。把它們推到新名字時被當成「已在遠端」→ 空範圍 → 跳過全套測試與全部會擋的閘。spec 的結論「不是變小」不正確。
修向:改寫該句為雙向;或對「全部已在遠端」的情形(S3)要求追蹤 ref 在最近一次 fetch 之後仍有效,例如空範圍時只放行風險分級,不放行雙向門與測試跳過。

## F5 空範圍時跳過全套測試,與「放寬只放寬誤擋」的說法不一致
severity: minor
blocking: 否——spec 已寫明「照常放行」並說明理由,只是理由同 F3、F4 有洞。
spec 段:實務隱患第三點。
引句:「空範圍的風險分級判成只動文件,所以推送前也不跑全套測試」
問題:實測 `pitfalls --diff tip..tip` 確實判 suite=docs。把「已合進主線的分支推新名字」與 F1(查詢失敗)、F4(追蹤 ref 過期)共用同一個出口,後兩者不是「當初已跑過」。這是 F1、F4 的後果,不單獨成案;列出是為了修 F1 時一併分流。

## F6 推刪除 ref 與迴圈位置沒寫明
severity: minor
blocking: 否——現有迴圈已在更前面 `continue`,照現況放法不會壞;只有照 spec 字面「迴圈裡算一次」放到 `continue` 之前才壞。
spec 段:做法 2。
引句:「迴圈裡算一次 `_brange=」
問題:刪除 ref 時 `_lsha` 全零。若函式呼叫放在 file: `scripts/hooks/pre-push:319` 附近那行 `[[ "$_lsha" == "$_ZERO" ]] && continue` 之前,rev-list 失敗得空字串,再被設成 `0000..0000..0000..0000` 這種無效範圍。spec 沒寫明放在 `continue` 與 `[[ -z "$_EMPTY_TREE" ]] && continue` 之後。建議條文補一句位置。

## 逐節與極端情境對照
- frontmatter、白話、依據、PRIOR-ART、RETIRE-IF:已讀,無 finding(RETIRE-IF 指向的 `_push_range_start` 在 file: `scripts/lumos:41864` 存在)。
- 範圍:已讀;「不做」清單與做法第 3 點的呼叫點一致。唯一缺口見 F6。
- 做法 1「逐字同一套」:根提交(無上一個)走空樹——已讀,無 finding(行為同現況)。全新 repo 首推 main、沒有任何遠端追蹤 ref:最早新提交=根提交 → 空樹..頂端 = 整個 repo,跟舊行為一樣;本案不改善也不惡化,但 spec 沒寫這個案例,S 條款也沒覆蓋,已讀,無 finding。
- 遠端名不叫 origin:`--remotes` 不依賴名字,已讀,無 finding(取捨見 F3 的目標遠端問題)。
- shallow clone:舊值物件缺時走 rev-list 分支;邊界提交若在某遠端追蹤 ref 上則正確;若不在(CI 式只抓一個 ref 的淺層 checkout)邊界被當根,範圍=整個樹,等於舊的整 repo 誤擋。spec 沒提淺層,而同檔漂移檢查註解明講淺層 clone 跳過。⚠ 我未能在本機重現(實驗的 clone 因缺 git 身分沒走到),不列為 finding。
- SHA-256 repo:`_ZERO` 是 40 個零,64 個零的舊值會落到 `cat-file -e` 失敗分支,結果仍走 rev-list,正確,無 finding。
- 同一次推多個分支:每個 ref 各算各的,後者包含前者的新提交,只是重複檢查,無 finding。
- 推送前 fetch 過期:見 F4。
- 空範圍餵各消費者:實跑 pitfalls、code-loop check、impact 皆正常(rc=0、files 空);`spec-gate --push-check` 空範圍無輸出,放行;已讀,無 finding。
- 實務隱患四類排除(金流、對外送出、不可逆):已讀,無 finding。
- 驗收條款:S1 到 S4 缺合併頂端、查詢失敗、多遠端三種案例(F1、F2、F3)。
- 回退、天花板:已讀,無 finding(天花板 2 與 F4 要一併改寫)。

severity 最高 major;blocking 條數 3(F1、F2、F3)。
