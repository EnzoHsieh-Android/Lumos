severity: major

(圖譜鏡頭:派工訊息沒有附上牽連的合約/事故節點,固定席無從逐條判;已讀 LUMOS-SPEC 指向的計劃檔即本 spec。)

## F1 條件 3 用預設改名偵測的 `git diff --name-only`,合併時刪掉的程式檔可被藏起來
severity: major
blocking: 是 — 條件 3 是整個放行的安全論證,字面照做會放行含手改(刪檔)的合併,與「合併時沒手改」的宣稱相反
引句:「`git diff --name-only 第二個母 目標` 與 `git diff --name-only 第一個母 目標` 的交集裡沒有非簿記檔」
具體例(已在 mktemp 臨時 repo 實跑):P1 有 A.py;P2 有 A.py(改過一行)與 B.py(內容等於 P1 的 A.py);合併提交 M 手動刪掉 A.py、保留 B.py。`git diff --name-only P2 M` 得 `A.py`;`git diff --name-only P1 M`(預設偵測改名,A.py→B.py 配成一對)只列新路徑 `B.py`(與另一個空檔)。交集為空 → 照 spec 條件 3 成立。但 A.py 在 M 裡與兩個母都不一樣(被刪),正是 spec 要擋的手改。應該:兩個 diff 都加 `--no-renames`(`_codeloop_record_valid_ex` 已因同一原因用 `--no-renames`,見 file: `scripts/lumos:46562`),或改用 `git diff --raw --no-renames -z` 逐檔比物件與模式,不用 `--name-only` 的文字交集。同族:spec 的「刪檔、改名」反例就在此;檔案模式(`--name-only` 會列出只改模式的檔)與子模組(gitlink 也列)實測行為正常,不構成洞。

## F2 條件 3 的「簿記」判定在交集裡沒講怎麼套「簿記資料夾裡的程式檔算程式」
severity: minor
blocking: 否 — 只會因實作者用前綴判法而多放簿記資料夾裡的程式檔,範圍窄,可用一句話補上
引句:「判法沿用 `_codeloop_record_valid_ex` 那套」
具體例:合併提交在 `governance/replay/x.py`(可執行或程式副檔名)上兩邊都不一樣。名詞段說判法沿用 `_codeloop_record_valid_ex`,但那支判的是(舊 sha,新 sha)一對的差異與 `_codeloop_bookkeeping_code(rec_sha, marker_sha, files, ...)`(file: `scripts/lumos:46614`),交集裡是「兩邊都不同」的檔,沒有一對 sha 可餵。實作者最自然的寫法是 `f.startswith(_BOOKKEEPING_DIRS)` 前綴判法,於是這個手改程式檔被當簿記放行。應該:spec 明寫交集內的簿記檔也要對「合併結果對兩個母」各驗一次是否為程式(內容/模式),或乾脆規定簿記資料夾內出現在交集的檔一律不認。

## F3 「推送範圍起點」取自替換前還是替換後的範圍沒講清,另缺「範圍終點必須等於目標」
severity: minor
blocking: 否 — 兩種讀法都只導致多擋,唯獨終點不一致一項可能多放,但需手動傳 `--diff` 與 `--at-sha` 不同值
引句:「推送範圍起點由呼叫端傳進判定函式(CI 與推送前掛鉤都已經傳範圍 `起點..目標`,從範圍取起點)」
具體例:(a)`_codeloop_guard_verdict` 在 `diff_range` 起點為全零或本機找不到時,先換成 `_lens_push_base` 算的起點(file: `scripts/lumos:46968`,`scripts/lumos:43616`);新分支首推時該起點是「跟主線的分岔點」,合併提交的第一個母絕不等於它(合併後分岔點=主線頂端=第二個母),所以條件 2 一律不成立。這是安全方向,但 spec 沒寫「用替換後的」,實作若取原始範圍起點,全零會被「空樹、全零不認」擋、與實際行為不同,測試也會歧異。(b)本機 `lumos code-loop check --diff A..B --at-sha C` 可讓終點 B 與目標 C 不同:tier 與適用題算 A..B,合併判定卻看 C 的母。應該:規定「範圍終點解出的提交必須等於目標,否則不認」,並寫明起點用替換後的值。另外 `--diff` 起點若是 `origin/main` 這種 ref 名,條件 2 要先 `rev-parse` 成完整 sha 再比(spec 只說「等於」)。

## F4 往回走第一母鏈 20 個:pass 在鏈上,但合進來那側在 pass 之後又合過主線時整筆失效,spec 的天花板沒列
severity: minor
blocking: 否 — 只會多擋,但常見流程(PR 分支審完後再按「更新分支」合主線)會讓這個修法在實際上常常不起作用
引句:「以第二個母往回走第一母鏈最多 20 個提交當索引(一次 `git rev-list --first-parent -n 20`)」
具體例:#28 能過是因為 pass 記在 afb7115c——那本身就是「合入主線的合併」(實測 `git rev-list --first-parent 5dbb85e0` 中 afb7115c 在第 2 位,`git diff --name-only 5dbb85e0 b0b48b7b` 為空,#28 代進三條件:兩個母 d0b24391/5dbb85e0、起點 d0b24391、交集空、afb7115c 有效 → 放行,且前三次合併 d0b24391、b4637da0、c150ac43 的交集實測為 0 筆)。若 P2 頂端是 pass 之後才合主線的合併提交 W(pass 在 W 的第一母鏈上第 2~3 位),索引會找到 pass,但 `_codeloop_record_valid_ex(pass, P2)` 的 `git diff pass P2` 包含主線帶進來的程式 → 判「之後動了代碼」→ 不認,照舊擋。這不是安全洞;spec 的「天花板」沒寫這個限制,會讓人以為「合進來那側審過就行」。應該:天花板補一條「合進來那側在 pass 之後又合過主線(帶進程式)要在分支上重記 pass 才認」。另「舊紀錄誤認」一節的測試要涵蓋此例以免被誤改成放寬。第 21 位以後的 pass(中間全是簿記提交)索引不到,也應寫進天花板。

## F5 表態那關的接點只寫「同一條規則」,既有程式有三個早退點,最常見的「主線上有舊表態紀錄」那個走不到新路
severity: major
blocking: 是 — 字面照做 S2 會在 #28 同型情境(主線已有一筆舊表態)仍紅,驗收條款 S2 無法成立
引句:「表態那關同一條規則,但讀的是 kind=dispositions 的紀錄(同一支讀帳函式帶 kind 參數),有效性對第二個母驗」
具體例:`_dispositions_verdict`(file: `scripts/lumos:46756`)有:(1) `rec is None` 早退擋;(2) `_codeloop_record_valid` 不通過就回「表態記錄過期」並 `blocked=True` 早退(file: `scripts/lumos:46779` 附近);(3) 之後逐題核對。spec 審查留痕那關寫「目標分支找不到有效紀錄」才呼叫合併側,表態卻只說「同一條規則」。主線(branch=main)通常有舊表態紀錄(正是 #28 的 pass 那邊 eeaa6162 的處境):走 (2) 而不是 (1)。若實作者只在 (1) 接合併側,過期紀錄情境照擋。另外 (3) 的逐題核對讀的是 `rec["dispositions"]`,換成合進來那側的紀錄後,錨點驗證用的 `marker_sha`(M)與紀錄 head_sha 的對應也要改驗 P2,spec 只說「有效性」。應該:明寫「rec 為空、或對目標驗無效兩種情況都先試合併側;試到有效就用那筆紀錄走 (3)」。適用題:非主線分支用 merge-base(主線,at_sha)..at_sha 另算(file: `scripts/lumos:47032` 附近),主線分支用推送範圍;spec 只講了後者,「推到功能分支且目標是合併」時的適用題口徑要補一句。主線那側 P1..M 的樹差異等於 PR 自己的改動,與 PR 分支上答題時的 merge-base..tip 一致,#28 型沒有口徑落差(已推演,非 finding)。

## F6 時間預算「整段用 _DISP_BUDGET」在程式裡是每個閘各建一個 deadline
severity: minor
blocking: 否 — 只影響最壞耗時(至多約兩倍),不影響判定對錯
引句:「整段用表態閘既有的總預算 `_DISP_BUDGET`,每次 git 用剩餘時間當上限」
具體例:`deadline` 只在表態呼叫處現場建立(file: `scripts/lumos:47055`,`_time.monotonic() + _DISP_BUDGET`),不是整個 verdict 共用。留痕關與表態關各自算一次合併側 ≈ 最多 2×20 秒,加每筆有效性判斷各自逾時。另外既有行為是表態超預算且尚未查出問題就 fail-open 放行(file: `scripts/lumos:47058`),spec 說新路徑逾時「照舊擋」,要明寫新路徑的逾時不得套 fail-open。應該:建一個共用 deadline 傳進合併側函式,並寫「逾時=不認(blocked),不得走 fail-open」。

## 其餘節:已讀,無 finding
- 範圍/「不做」:已讀,無 finding。引句:「不做:章魚合併(三個以上的母)、squash 合併(主線上是一般提交,照舊)、合併提交本身有手改的(照舊要在主線補審)。」(章魚=三母,條件 1 擋;squash 不是合併提交)
- 推送前掛鉤與 CI 範圍起點實際值(重點 5,已核實):CI 傳 `"$BEFORE..$SHA"`,新分支 before 全零、force-push 後 before 本機可能找不到,兩者都在 `_codeloop_guard_verdict` 內被 `_lens_push_base` 換成分岔點或回「沒有新東西」(file: `.github/workflows/ci.yml:186`,`scripts/lumos:46968`);推送前掛鉤增量推送傳 `遠端舊值..本機`,新 ref 或本機沒有舊物件傳空樹(file: `scripts/hooks/pre-push:40`),新分支首推再換成 `push-range` 的起點(file: `scripts/hooks/pre-push:53`)。因此:CI 推 main 的合併提交(before=舊主線頂端=第一個母)與推送前直接推主線(舊值=第一個母)才會成立條件 2,其餘形狀(新分支、force-push、空樹)一律不認,與 spec 敘述相符。引句:「CI 三處 checkout 都是完整歷史;淺 clone 時明講判不了。」(`ci.yml` 實有三處 `fetch-depth: 0`)
- 實務隱患/回退/天花板/審計修正紀錄:已讀,無 finding。引句:「帳本是沒簽章的純文字,手寫一筆就能偽造——這在現行規則下寫成 branch=main 也成立,不是新洞」

重點走查結論:(1) #28 代進三條件放行(實測母數、起點、交集空、afb7115c 在第一母鏈第 2 位且對 5dbb85e0 有效);(2) 反例 = 改名偵測藏刪檔(F1,已實跑);(3) 合進來那側 pass 後又合主線:索引找得到但有效性判無效,多擋不多放(F4);(4) 表態接點缺(F5);(5) 範圍起點實際值見上。

總結:最嚴重 major,blocking 共 2 條(F1、F5)。
