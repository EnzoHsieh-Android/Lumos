severity: major

# r3 正確性-opus(舊句檢查_計劃,第 3 輪凍結版)

鏡頭:照凍結版字面實作,會不會做出錯的結果;重點驗 r2 折進來的規則。實驗在自己的 clone `osr3op`(`git clone --shared`)與暫存 `osr3op-exp/` 跑,直譯器 /opt/homebrew/bin/python3(3.14.6);沒改 repo 任何檔。

逐節結論:
- 〈依據〉、PRIOR-ART:已讀,無 finding(P4r3 的數字跟 `osfold/p4r3-results.json` 對得上:rtb 91 筆、要處理 20,工具鏈 1 筆只列出;兩組 parse_fail 都是 0)。
- RETIRE-IF / REVISIT:F2、F7。
- 〈範圍〉:F2(前置漏了 rtb)。
- 〈做法〉1:已讀,無 blocking。「粗候選先算」我逐步對過參考實作 `disappeared(repo)`:先扣同一支檔終點那版、再扣終點語料,跟參考實作一次算完是同一個集合,粗候選空的時候最終候選一定也空,結果不變。
- 〈做法〉2:F6(家)。撤除節、句內字眼(54 個逐字跟 `HIST_WORDS2` 相同、沒有重複)、整字、名稱先篩(我逐條驗過先篩是保守的:整字命中的地方,名稱每一段 ASCII 詞在全文切詞裡一定是完整的詞)都對得上參考實作。
- 〈做法〉3:F1、F3、F5。
- 〈做法〉4:F4、F8。
- 〈與參考實作的刻意差異〉:F6(漏列兩處,在驗收資料上影響 0 筆)。
- 〈條款〉:F3(S13 跟正文打架);S17 缺的那一句見 F1。
- 〈回退〉:已讀,無 finding。
- 〈實務隱患〉〈誠實界線〉:已讀,無 finding(下面實務隱患逐類答)。

## F1 done 而且只有只列出(要處理 0、只列出 >0)沒有結論行可印,「一定印一行結論」在最常見的情況破了
severity: major
blocking: 是
引句:「要處理有筆數、或判不了(timeout、git-failed、unreadable)」
file: `governance/review-reports/舊句檢查/r3-snapshot.md:111`
file: `governance/review-reports/舊句檢查/r3-snapshot.md:114`
1. 〈做法〉3 先把「有東西」定義死:要處理有筆數、或判不了三種之一。緊接著的結論句只有三條給 done 用:候選 0、「候選 N>0、兩層都 0」、「done、有東西」。
2. 輸入:done、候選 N>0、要處理 0、只列出 B>0。照這個定義它不算「有東西」,也不是「兩層都 0」,三條都套不上。照字面實作會落到沒有分支的地方:要嘛一句都不印(違反同一節「一定印一行結論」),要嘛實作者自己挑一句,而且開頭詞規則也沒講。
3. 這不是邊角情況。P4r3 在 rtb 有命中的 9 個提交裡,4 個(626cccb、b2b17ea、5efe4d2、b8c6ccc)就是要處理 0、只列出 1–2;工具鏈 300 個提交唯一的那一筆也是只列出。所以兩週帳裡最常見的「有發現」推送,正好沒有定義結論句。
4. S13 固定輸入是要處理 1、只列出 1,S17 只釘了六種(候選 0、兩層都 0、三種判不了、no-base),兩條條款都沒蓋到這個情況,測試也不會發現。這是 r2 鏡像核對 F17「有東西的開頭詞規則寫清楚、S17 釘六種結論行」折進來時留下的洞。
5. 折法:把第三條的標籤改成「done、兩層有任一筆」,開頭詞照舊只跟「要處理有筆數」走(只列出 → 沒有開頭詞、rc 0、kind passed);S17 補一例「要處理 0、只列出 2 → `舊句檢查:這次推送消失了 N 個名稱,筆記裡還在講的——要處理 0 筆、只列出 2 筆`,沒有開頭詞」。

## F2 兩週量準度的資料照計劃自己的數字湊不到 20 筆:工具鏈幾乎是 0,rtb 那份又沒列成前置
severity: major
blocking: 是
引句:「沒接上,工具鏈這邊兩週沒有帳,REVISIT 只剩 rtb 的數」
file: `scripts/lumos:17717`
file: `scripts/hooks/pre-push:1`
1. RETIRE-IF 要求去重後的要處理層至少 20 筆,不到就一律延長。計劃自己量的工具鏈基準是:300 個提交(09-12 到 09-30,18 天)**要處理 0 筆**。所以兩週的工具鏈帳在要處理層的期望值接近 0,20 筆幾乎全要靠 rtb。
2. rtb 要有帳,得先有兩件事:rtb 手上的 `scripts/lumos` 已經帶 `m1`,而且 rtb 的推送前掛鉤會呼叫 `drift check`。但工具鏈裝進消費專案的 `scripts/hooks` 是整個資料夾複製過去的(`_VENDORED_TREE_DIRS`),`scripts/lumos` 也是複製過去的(`_VENDORED_TOOLKIT`)。工具鏈自己的 `scripts/hooks/pre-push` 現在一個 drift 字樣都沒有(`grep -c drift` 是 0);實驗用的 rtb 複製(067f005)CI、`.lumos`、治理帳也都沒有 drift-check。所以 rtb 要等工具鏈接好線、`m1` 上線之後,自己再跑一次 lumos 更新並提交,才會開始記帳。
3. 〈範圍〉的前置只寫了工具鏈接線,還明講「沒接上就只剩 rtb 的數」,等於假設 rtb 一定有數。REVISIT 的日期順延也只綁工具鏈接上的那天。照字面走:10-14 → 樣本不足延到 10-28 → 11-11 → 攤給人裁。原因根本不在準度,而在 rtb 從頭到尾沒接上。
4. 就算 rtb 接上了,量得到的量也不多。rtb 09-21 到 09-28 一週 594 個提交(爆發期);P4r3 的 20 筆要處理裡有 16 筆來自 b2fc512 那一個提交,其他提交加起來一週只有 4 筆。沒有同樣規模的大改動,兩週大約 8 筆,還是不到 20。
5. r2 接手席點過「rtb 端可能還沒接上」,但折法只補了延長與出口,沒補前置。**折法**:前置加一條「rtb 更新到帶 `m1` 與掛鉤接線的版本並提交,REVISIT 從兩邊都接上那天起算」;依據段寫明兩邊預期的量(工具鏈約 0、rtb 非爆發期每週約 4 筆),讓人一開始就知道 20 筆門檻大概要幾週才到。或者把 20 筆改成跟這個量相符的數字,並寫明理由。

## F3 超過 20 筆那句,正文印的字樣提到 drift scan,S13 卻要求不提
severity: minor
blocking: 否
引句:「改完這些再推會再列(`drift scan` 不含舊句檢查)」
file: `governance/review-reports/舊句檢查/r3-snapshot.md:123`
file: `governance/review-reports/舊句檢查/r3-snapshot.md:180`
1. 〈做法〉3 把整句放在引號裡,括號也在引號內,所以印出來的字串帶 `drift scan`。S13 寫的是「那句寫『其餘 N 筆這裡沒印;改完這些再推會再列』、不提 `drift scan`」。
2. 照正文實作,S13 的「不提」斷言會翻紅;照 S13 實作,又不是正文那個字串。兩邊只能對一邊。折法:括號那段移到引號外面當說明,或讓 S13 跟正文同一個字串。

## F4 REVISIT 抽範圍的那行指令會把判不了的推送也帶進準度,跟「只有 done 進準度」打架
severity: minor
blocking: 否
引句:「state 是 `done` 的才進準度」
file: `governance/review-reports/舊句檢查/r3-snapshot.md:142`
file: `governance/review-reports/舊句檢查/r3-snapshot.md:148`
1. 〈做法〉4 抽 `--pairs` 的那行 python 只濾掉 `base_sha` 是空的(也就是 no-base)。timeout、git-failed、unreadable 的事件都有 `base_sha`,會照樣進 pairs。
2. 帳裡的 rows 最多只有 10+3 筆,所以準度的完整清單來自 revisit 重跑(〈做法〉3 最後那段就是這樣說的)。這樣一來,timeout 那次的範圍會在 revisit 裡被完整重算,P4r3 命中照樣進「要處理層去重後」的池子,跟「state 是 done 的才進準度」「timeout 那筆沒有 rows,不進準度」相反。
3. 通常是範圍大、最容易時間到的推送(上線點以來的首推)被多算進去。折法:那行加 `e.get('state')=='done'`,或者改寫成「判不了的範圍也進準度」,兩處擇一講清楚。

## F5 帳的一行壓在 4 KB 只靠丟 rows 做不到:nodes 最多 50 篇,加上 note/detail 重複,光這些就可能超過
severity: minor
blocking: 否
引句:「整行(json 編碼後的位元組)還超過 4 KB 就先從只列出、再從要處理尾端丟」
file: `scripts/lumos:1198`
file: `scripts/lumos:1202`
1. `_gate_event` 本來就會把 note 再寫一份到 `detail`,而 `m1` 的 nodes 最多 50 篇。我量了工具鏈現在 588 篇筆記的名稱:json 編碼後,中位長度 50 篇約 2.2 KB,最長 50 篇約 3.3 KB。再加上兩份結論句、`ts`、`head_sha`、`base_sha`、`attempt_id`、`ref`,還有最多 3 條可能很長的 `oversize_paths`,rows 全丟光之後仍然可能超過 4 KB。
2. 計劃沒寫「rows 丟光還超過」要怎麼辦,所以「一行 4 KB 內」這個承諾不成立。實際後果不大:`_gate_event` 是一般文字模式追加,8 KB 內還是一次寫出,不會交錯。折法:nodes 也照位元組截(或最多 20 篇),或者把保證改寫成「rows 丟光為止,不保證 4 KB」。

## F6 「家」有兩處跟 P4r3 不同,沒列進刻意差異(驗收資料上影響 0 筆)
severity: minor
blocking: 否
引句:「改名的新舊兩條路徑都算」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:613`
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:371`
file: `docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md:7`
1. 改名怎麼配對:參考實作的 `homes_any` 用 `code_changes(True)`,也就是 `-M` 認改名,整組改名只照**新路徑**判是不是程式檔。正式工具照〈做法〉1 的 `--no-renames`,拆成一刪一加,各自判。碰到一邊在排除清單內的改名(例:`tools/x.py` 搬到 `docs/`、或 `governance/` 搬出來),兩邊得到的「家」會不一樣。我實際量了(`osr3op-exp/homes.py`):工具鏈 300 個提交 0 次;rtb 有 1 次(8cdc94b8,`tools/make_agent_flow_gif.py`,家 `Systems/README流程動圖產生器.md` 在正式工具算家、P4r3 不算),命中差 0 筆。
2. about_code 怎麼讀:參考實作 `_about` 只認區塊清單 `- x`。工具鏈有 2 篇寫成單值 `about_code: scripts/lumos`(`Systems/節點範圍與索引守衛`、`Issues/健檢技術棧那段撞到多平台設定就整支中斷`)。正式工具如果用專案的開頭欄位解析,這兩篇會變成 `scripts/lumos` 的家,幾乎每次推送都改到這支檔。這兩篇在三組驗收資料裡都沒有命中,所以差 0 筆;但計劃沒指定用哪種讀法。
3. 驗收規則是「差的每一筆都要落在刻意差異裡」。這兩處現在碰巧 0 筆,但沒寫進清單,以後重跑一旦有差就找不到出處。折法:刻意差異加一條,或在〈做法〉2 寫明「家」照 `-M` 配對、about_code 只認區塊清單。

## F7 RETIRE-IF 的「壞訊號、留在提醒」這條路沒有下一個回頭點;「總共六週」的起算點也寫錯
severity: minor
blocking: 否
引句:「任一條成立就不把預設改成擋、留在提醒」
1. ①要處理層準度低於 60%、或②單次超過 30 筆成立時,計劃只說留在提醒。沒有下一個 REVISIT 日期,也沒有撤除條件(RETIRE-IF 只在轉擋之後兩個月才會撤)。12-14 那行說「沒轉擋就改成人裁定的日期」,但這條路上沒有人被要求裁定。結果是:準度低的 `m1` 會以提醒模式一直跑、一直記帳,沒有人回頭。這正是鐵則 4 說的「回頭條件沒接電」。折法:①②成立也走「攤給人裁」,或者給一行帶日期的 REVISIT。
2. 「連續延長兩次(從第一次 REVISIT 起總共六週)」:從第一次 REVISIT(10-14)延兩次到 11-11 是四週;六週要從 09-30 上線那天起算。REVISIT 那行的例子(10-28 → 11-11)是對的,只是括號裡的起算點寫錯。

## F8 revisit 用(筆記, 行)判「放過」,同一行只放過一部分名稱時算不到,④⑤會少算
severity: minor
blocking: 否
引句:「`clause_released` 與 `shape_released` 各自兩層合起來、照上面的鍵去重」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:1279`
1. `cmd_revisit` 判放過的寫法是 `k not in main_`,其中 k =(筆記, 行)。
2. 輸入:一行同時提到 A 和 B,A 所在那一小句有歷史字眼,B 沒有。P4r3 用 {B} 列出這一行,P4r3c 用 {A,B} 列出。因為這一行已經在 main_ 裡,它不算 clause_released,A 被字眼過濾放過這件事完全不會出現。
3. 〈做法〉4 的鍵含名稱集合,但 revisit 那邊是用行來判,口徑不一樣,④⑤的分子會偏低,結果偏向「可以轉擋」。一行多個名稱不常見,所以列 minor。折法:revisit 改成比對同一行的名稱集合差集(P4r3c 的名稱減 P4r3 的名稱,非空就算放過,只帶差出來的那些名稱)。

## 合約(★INVARIANT★)逐條判
- `Systems/guard-kill` 兩條(rc 優先序、`--json` 輸出只有一行):不影響。`m1` 不碰 `guard kill` 的程式與輸出。
- `Systems/lumos-cli-read`「search 預設排除 superseded」:不影響。`m1` 掃 superseded 筆記是 drift check 自己的判定,不經 `cmd_search`。
- `Systems/lumos-cli-write`、`Systems/存量漂移守衛`:沒有 ★INVARIANT★ 行。存量漂移守衛的「預設改 block 要三條全過」RULE,計劃已經說明為什麼不管 `m1`,我對過沒有矛盾。

## 實務隱患
- 不可逆:無。只讀程式與筆記、只印與記帳;快取刪掉就好。
- 金流、對外送出:無。本機命令列,不連外部服務。
- 守衛面:碰到。F1(結論句漏一種情況)、F7(提醒模式沒有回頭點)。
- 效能:碰到。粗候選先算我驗過不改結果。冷快取時批次讀會把整個語料的內容都讀進來(只是不剖),成本在 0.1 秒量級,可以接受。
- 記憶體:碰到。4 MB 上限擋的是剖檔;超過 4 MB 的 blob 內容還是會整支讀進批次讀的結果裡,11 MB 級的量無害。
- 併發:碰到。F5:帳一行可能超過 4 KB,但 8 KB 內仍然一次寫出。快取用唯一暫存名加原子替換,沒問題。
- 量準度:碰到。F2(資料量到不了門檻)、F4、F8(口徑)。
- 資安:無新增。`--name=` 等號寫法我實測過:3.14.6 的 argparse 把 `--name=--restore` 正確解析成 `['--restore']`。

最高等級:major;blocking 共 2 條
