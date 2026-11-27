severity: major

## B1 survived 且守的測試沒變的行不會用新順序,〈白話〉〈實務隱患〉的宣稱與程式不符
severity: major
blocking: 是(宣稱的上線行為與程式現況不符,S7 的量法也會跟著錯)
引句:「所以上線後舊行停在舊挑法挑到的那個壞法;新行與存活、跑不出結果要重跑的行才用新順序」
1. 輸入:帳上最新一筆是 survived(舊順序挑到運算子壞法)、守的測試雜湊(tests_sha)沒變。
2. 走到:`_choice_kill_pick` 對這種行判 `carried`,不重跑,見 `scripts/lumos:80075`。
3. 壞在:spec 把「存活」整類寫成會用新順序,實際只有守的測試變了才重跑。
4. 依覆蓋判的存活(`via cov`)是另一條路,見 `scripts/lumos:80069`。cov_sha 含 new_sha,新挑法換壞法後 cov_sha 對不上,所以會重跑。
5. 同一類的兩種存活走兩條路,spec 沒分。
6. 後果:這行帳上存的是舊運算子壞法的存活,推送閘現在算出的挑法卻是兄弟寫法。`_choice_ledger_status` 印「存活」時沒有任何東西核對存活的是哪個壞法。
7. 使用者要處置的存活,對的是已不是現行挑法的壞法,而且這種行不會被新順序修正,直到測試動到為止。
8. spec 要補:
   - survived(非 cov)在 tests_sha 不變時 carried,算進〈不做〉的舊行範圍;
   - 或明定 carried 前要核對帳上壞法的 new_sha 是否等於現行挑法;
   - 兩種存活的處理要分開講。
9. S7「改挑行的殺/存活數」在空帳本上量,量不到這個 carried 的量。

## B2 S6 的測試不會對症狀翻紅,是空殼
severity: major
blocking: 是(違反專案〈實作測試品質〉,綠燈不代表守住了)
引句:「已殺掉或已放行的行 應 在挑法改了之後照舊算有效處置、不重跑」
1. `_choice_disposition(evs, waived, bound)`(`scripts/lumos:79774`)只吃帳、放行檔、bound,完全不吃挑法或 tiers。
2. `_choice_kill_pick` 也是先用 `(檔, fp)` 查帳,才看 `x["status"]` 與挑到什麼。
3. 預期值表 S6 寫「不管新順序挑到哪個」。所以把 `_choice_pick_iter` 改成新順序、舊順序、或亂挑,這個測試都綠,翻不紅。
4. 要有殺傷力,S6 該餵一份帳(killed 且 killing_test 仍被綁)加新挑到不同壞法的行,走 `_choice_kill_pick` 全路徑,斷言該行進 `done`、不進 `first` 或 `again`。
5. 同理要補斷言:
   - killed 但 killing_test 已不在 bound(stale)會重跑,而且用新挑法;
   - waived 照舊;
   - survived 的 carried 見 B1。
6. 現在 spec 只有「killed、仍被綁」一種狀態有案例,stale、waived、survived、no_result 都沒有。

## B3 tiers 的值沒有驗證,自檢只核對鍵集合
severity: major
blocking: 是(自檢是唯一擋線,而值壞了會靜默讓整個類別消失)
引句:「`CHOICE_CATEGORIES` 裡有類別不在 `CHOICE_TIERS`、或 `CHOICE_TIERS` 有 `CHOICE_CATEGORIES` 沒有的類別,都回報問題」
1. 輸入:`tiers = {"API": 0, "NUL": 4, "SBR": "2", ...}`(值是 0、4、字串、None、bool、3.5)。
2. spec 規則是「由第 1 級往第 3 級串接」,也就是只迭代 1、2、3。
3. 值是 0、4、字串、None 的類別,鍵齊全、自檢過,但串接時不落在任何一級。
4. 那個類別的選擇點在 `_choice_pick_iter` 不被交出,整行回 None,status 變 `none`,而且不報任何問題。
5. 值是 `True` 時 `True == 1` 成立,會被誤當第 1 級。
6. 做法段另說「表裡查不到的類別當第 3 級」,這是第二種規則。
7. 值不合法時走「當第 3 級」還是「整張表判壞」,spec 沒寫。
8. 要補:自檢加「值必須是 int 且在 {1,2,3}」,值不合法也整張表判壞。
9. 要補的測試:S3 現只有「少一個鍵、多一個鍵」兩案,要再加值壞案。

## B4 tiers 傳入的各種極端形狀,spec 沒定義預設
severity: major
blocking: 是(`tiers=None` 與「查不到」兩個預設互相打架,實作者各取一邊就分歧)
引句:「`tiers` 是 None 時整個當一級(就是改之前的挑法),表裡查不到的類別當第 3 級」
1. 輸入:`tiers={}` 空字典。
   - 若用 `is None` 判,`{}` 不是 None,所有類別都「查不到」,全當第 3 級。結果碰巧等於舊挑法,但走的是另一條路徑。
   - 若用 `not tiers` 判,結果相同,但兩種寫法是兩個實作。
   - spec 沒說 `{}` 屬哪一邊,S5 只測「沒傳」。
2. 輸入:tiers 只含部分類別(例 `{"API": 1}`)。
   - 另一邊(ROR 等)全落第 3 級,看似合理。
   - 但 `{"AOR": 1}` 會讓 AOR 與 API 同屬第 1 級而不是第 3 級,「兩個都有」的行打亂的是並級後的清單。
   - 防呆路徑沒有測試,而「正式路徑自檢已擋」又取決於 B3 的值驗證。
3. 輸入:`CHOICE_TIERS` 與 `CHOICE_CATEGORIES` 順序不同。
   - 現行 `categories` 的順序是 `("AOR","LCR","ROR","UOI","SBR","API","NUL")`,見 `configs/ast-grep/kotlin-android/check.py:1393`。
   - 那一行註解還寫了「順序也是洗牌前的基準順序」。
   - spec 的 `CHOICE_TIERS` 字典順序是 `API, NUL, SBR, AOR, ...`,跟它不同。
   - 做法段寫「照 `categories` 原本的順序」取出各級的類別,所以順序來源要是 `categories`,不能是 tiers 的字典順序。
   - 但 S2、S5 的期望值「跟改之前寫死的期望值同一個」只在順序來源是 `categories` 時成立。
   - 沒有測試守這一點:實作者若遍歷 tiers 字典,S2 與 S5 的單級案例仍可能因同級內順序不同而紅,但多級混合案例不會被發現。
4. 輸入:一行同時有三級(API、NUL、AOR)。
   - 預期值表只有 API+ROR(S1)、NUL+AOR(S4)、AOR+ROR(S2) 三個兩級以內的案例,沒有三級齊全的案例,也沒有「第 2 級內 NUL、SBR 同級」的案例。
   - 第 1、2、3 級串接的順序只靠 S1 與 S4 兩兩間接證明,沒有直接斷言。

## B5 全部候選被排除或在跳過集合時,「先挑第 1 級」會把行判成 none 或 exhausted,而不是退到下一級
severity: major
blocking: 是(spec 只說「類別順序」,沒說用盡後是否往下級走,行為由實作順手決定)
引句:「不改節點與候選的挑法,只改類別順序。」
1. 輸入:一行有 API(第 1 級)與 ROR(第 3 級)的節點,API 節點全被 `_choice_excluded`(型別前提排除)或 `_choice_edits` 產不出。
2. 現行迭代器(`scripts/lumos:79358`)是 `for cat in cats` 一路往下取,上一類沒產出就換下一類。
3. 新順序把串接的清單當成同一條,應該也會退到下一級。這是對的,但 spec 沒寫,且所有案例(S1~S5)都是第 1 級有可用壞法,沒有案例測「第 1 級全空退下級」。
4. 輸入:第 1 級候選全在跳過集合(合批編譯確認編不過)。
   - `_choice_line_pick`(`scripts/lumos:79431`)取第一個不在 skip 的候選,會退到第 3 級的運算子壞法。
   - 這代表「兄弟寫法全編不過」時,這行被運算子壞法取代。與使用者「易混淆寫法更重要」的裁示一致,但〈實務隱患〉沒提這條退路。
   - 要測的是退下級而不是 exhausted。
5. 反向案例:全部級的候選都在 skip 裡,才是 `exhausted`。spec 沒有案例。
6. 〈做法〉末段有「跳過集合以 new_sha 比對,換順序不會誤跳或漏跳」。這句是宣稱,沒有測試綁:S1~S7 都沒給 skip。
7. 要補:
   - 一個「第 1 級全被排除、退到第 3 級」案例;
   - 一個「跳過第 1 級唯一候選後換到第 3 級,且 new_sha 比對跟順序無關」案例。

## B6 S7 的「空帳本複本」、「新舊挑法各算一次」沒有可執行做法
severity: major
blocking: 是(驗收條款依賴的量測沒有定義做法,而且 spec 說 4 席審過卻沒補這一步)
引句:「在一份空帳本的複本上各用新舊挑法算一次」
1. 帳本由 `_gov_vc_gate_events(repo_root, _CHOICE_KILL_GATE)` 從版控治理帳讀,見 `scripts/lumos:79549`;放行檔另由 `_lint_waivers_load` 讀。
2. 「空帳本」要同時處理兩處:治理帳(git 版控)與放行檔。spec 只提「帳本」。
3. 複本怎麼做:是複製整個實驗專案 repo 再清帳,還是傳參數覆寫路徑?現行 `choice-points` 與 `choice-kill` 沒有帳路徑參數,`_choice_ledger_status` 的「讀工作目錄的版控治理帳」是寫死的。
4. 「各用新舊挑法算一次」也沒說:舊挑法怎麼取得(checkout 改動前的 scripts/lumos 另跑?),實驗專案批 4a 範圍 `4f170b2..ff9c96a` 在本機能不能 checkout、是否為 spec 要求的唯一來源,spec 沒說。
5. spec 的 S7 預期值欄寫「驗證紀錄列出改挑行數、三組分列、…」,也就是只列要印什麼,沒列怎麼產。
6. S7 又是 `[manual:]` 條款,沒有任何機械檢查「三組分列」是否真有數字。
7. 另外,S7 的「改挑行的殺/存活數、多花秒數」要實際跑 choice-kill,需要實驗專案的測試環境。spec 沒寫前置(ast-grep、模擬器或 Gradle)。
8. 工作目錄髒(實驗專案跑殺傷力要求乾淨,見 `scripts/lumos` 的 `_choice_kill_base`)也沒提。
9. 〈白話〉引用 `[[Systems/規格閘]]` 說只列「行指紋」那條,但這是量測前置依賴,不是驗收做法。

## B7 一行同時有「身分 None」候選時,新舊挑法挑到的壞法 status 會翻,已有帳的 not_unique 行無處置
severity: minor
blocking: 否(現行機制已有 not_unique 一路,只是新挑法讓分布改變;沒有新破口,但 S7 未量)
引句:「`tiers` 是 None 時整個當一級(就是改之前的挑法)」
1. 輸入:同一行有 API(第 1 級)與 ROR(第 3 級)。舊挑法抽到 ROR,身分唯一(status `mutant`);新挑法抽到 API,但 API 壞法的 `identity` 是 None(`_choice_identity` 判不唯一)。
2. 該行 status 由 `mutant` 變 `not_unique`。`_choice_kill_pick` 把它放進 `nu`(不唯一沒放行的行),上線後這行從「可處置的壞法」變成「要擋推送、要人放行」(見 `scripts/lumos:80071`)。
3. 反過來也可能由 not_unique 變 mutant。
4. spec 說 S7 量改挑行數與殺/存活,沒量「改挑後變 not_unique」的行數。
5. 這不是新破口(not_unique 機制已存在),但上線會造成突增的人工放行量。S7 要加一欄「改挑後變 not_unique 的行數」。

## B8 〈落點〉與 `lands_in` 與節點宣稱的行為
severity: minor
blocking: 否(落點只是寫回位置,不影響行為)
引句:「改寫行指紋那條 WHY 的「挑壞法的種子也用它;論文整次呼叫洗一次類別」,補「各級各自洗、依級串接」。」
1. 規格閘節點 `docs/lumos-toolchain-knowledge/Systems/規格閘.md:68` 該句實際原文是「挑壞法的種子也用它;論文整次呼叫洗一次類別、沒規定種子,這裡每行各用自己的種子」,spec 引的是片段,位置對得上。
2. 同節點第 72 行有效處置 WHY 宣稱:「survived 在守的測試雜湊變了才重跑」。這條跟 B1 直接相關:spec〈白話〉說「存活要重跑的行才用新順序」,與該 WHY 的「survived 測試沒變不重跑」一致,但 spec 沒引這句,而是只提 `no_result` 與存活,造成讀者以為存活一律重跑。
3. 同節點第 116 行說「`_choice_pick` 改成 `_choice_pick_iter` 依序交出候選」、「不帶 skip 時挑到的跟原本相同」:新排序不影響這條,因為第一個交出的依舊是 `_choice_pick` 不帶 skip 的結果,不破壞該宣稱。
4. 規格閘節點「行指紋挑法穩定」的測試是 `t_choice_points_stable`:同一行重跑挑同一個壞法。新挑法仍以行指紋為種子,每一級各自洗都是決定性的,不破壞該宣稱。
5. 判不影響的理由:行指紋、有效處置鍵 `(檔, 行指紋)`、skip 集合 `new_sha` 都不依賴類別順序,所以節點宣稱的穩定性與合約不被破壞。

## B9 RET 補登等級靠「自檢會擋住漏補」,但那是在第四批計劃還沒做時才成立的假設
severity: minor
blocking: 否(對現行 55 列無影響,只是前向依賴)
引句:「歸第 2 級是 AI 自定(2026-11-28:回傳值換成預設值性質接近刪掉陳述,不是兄弟寫法也不是運算子)。自檢會擋住漏補。」
1. 〈做法〉說在第四批計劃補 `"RET": 2`,漏補由自檢擋。但 `CHOICE_CATEGORIES` 目前只有 7 個類別,沒有 RET。
2. 第四批新增 RET 時兩份常數都要動:`CHOICE_CATEGORIES` 加 RET、`CHOICE_TIERS` 加 RET。自檢擋的是「只加一邊」,是對的。
3. 但如果第四批先落地、本計劃後落地,RET 會在 `CHOICE_CATEGORIES` 裡而本計劃的字典沒有它,自檢會擋下並整張表判壞,推送閘全停。spec 沒寫兩份計劃落地順序,也沒寫本計劃 `CHOICE_TIERS` 要不要先預填 RET。
4. 要補:落地順序,或本計劃的字典現在就預填但自檢不認多的鍵(與〈做法〉第 49 行「有 CHOICE_CATEGORIES 沒有的類別,都回報問題」衝突)。

## 已讀無 finding 的節
- 〈白話〉類別表:型錄列數 API 35、NUL 2、SBR 1、AOR 5、ROR 8、LCR 2、UOI 2,合計 55,與 `skills/kotlin-idioms/checks-catalog.md` 〈選擇點表〉實際計數一致。
- 〈回退〉:有效處置鍵不帶壞法的宣稱與 `_choice_disposition` 現行行為一致。回退只涉及 `_choice_pick_iter`、check.py 常數與自檢,不影響帳,已讀,無 finding。
- 〈不做〉、〈依據來源〉、PRIOR-ART:未見新增的未查證數字(論文兩個數字 r1 已核對)。
- 身分為 None 的情形:`_choice_identity` 回 None 是既有分支,新舊挑法都處理,見 B7 的上線量影響,其餘已讀。

總結:最嚴重 severity 為 major,blocking 共 6 條(B1 到 B6),minor 非 blocking 3 條(B7、B8、B9)。
