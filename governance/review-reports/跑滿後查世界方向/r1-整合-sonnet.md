severity: major

# 外部審稿:跑滿後查世界方向(r1)

先講結論:這份 spec 最大的洞,是它宣稱「現有規矩只有每輪修補前查怎麼修」,但手冊裡早就有一條在「同一判讀第二次被打穿」時必查方向的規矩。主觸發因此是第三條重疊的規矩,沒有說明跟前兩條怎麼接。其次,手冊要改的地方數錯了,工具印給人的提示又跟新順序相反。

## 一、主觸發與既有規矩

1. 主觸發跟既有的〈先查世界〉與「同類第二次換形狀」重疊,spec 沒有說三者怎麼接,三個月後接手的人會做兩次或不知道誰優先。
引句:「決定新形狀之前先上網查方向(同樣的問題世界上用什麼形狀解、有沒有實證說走不通、有沒有更簡單的既有做法;至少兩個來源)」
- 設計審 SKILL.md 第 6 步與代碼審 SKILL.md 第 5 步已經規定:每組動手前上網查,寫進 rN-intake.md〈先查世界〉。
- 同一段還寫:「同一個判讀第二次被打穿時這一步必做,而且先找不靠字面判斷的現成做法」。這就是 spec 的主觸發條件。
- 代碼審 SKILL.md 第 4 步的守衛面條款(同類第二次被打穿就換形狀),又在更前面直接規定「整類拿掉或外面加看門」,沒要求先查。
- 新規矩要求另寫一節〈世界查證〉、至少兩個來源,放在同一份 rN-intake.md。spec 沒說它是取代〈先查世界〉、補在它後面,還是同一節改名。
- 結果:同一個觸發點要寫兩段查證,而且〈先查世界〉的「查不到就寫查了哪些詞」不要求兩個來源,跟新的「至少兩個來源」互相打架。
- spec〈問題與最小解〉第二段說「現有規矩只有每輪修補前先查怎麼修,查的是局部修法」,與手冊原文不符。
- 圖譜上已有相關裁定,spec 沒有引用:`Systems/每輪修補差異派工` 的 WHY 寫著 `[不選:只在跑滿回顧或卡關時才查(那時已多燒好幾輪)]`。同一篇的 REVISIT 2026-12-15 還在觀察〈先查世界〉有沒有被漏做。
- 既有規矩已經常被漏做,新主觸發又是同樣沒有機械訊號的散文,不會改變遵守率。
- spec 自己的 lands_in 與 related 都沒有連到 `Systems/每輪修補差異派工`。
- 該 REVISIT 只認〈先查世界〉標題,新標題〈世界查證〉會把量測拆成兩邊。
- file: `skills/lumos-design-loop/SKILL.md:41`
- file: `skills/lumos-code-loop/SKILL.md:45`
- file: `skills/lumos-code-loop/SKILL.md:50`
- file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:20`
severity: major
blocking: 是(照字面做會在同一個 intake 檔裡寫出兩段重疊又互相矛盾的查證要求)

2. 手冊的人裁順序「查 → 攤人裁 → 記 cap-decision」,跟工具現在印給人的「先記人裁」相反。「跑滿」的定義也用了實務上幾乎不發生的 cap-reached。
引句:「順序是查 → 攤人裁 → 記 cap-decision → 寫回顧」
- `_cap_retro_next_lines` 在 [cap-hint] 與處置閘輸出裡印「要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision …」。`cmd_loop_cap_decision` 成功後印「繼續之前先寫跑滿回顧」。
- 編排者在到頂那一刻看到的就是這兩句。照提示做,會先記人裁、後查世界,查證結論就影響不了「要不要加開」。這正是 spec 設計這個順序的目的。
- spec〈做法〉只列了 `_cap_retro_check` 與 `--record` 的提示,沒有列這些既有訊息要改。
- spec〈名詞〉把跑滿定義成「帳上狀態變成 cap-reached」。`Systems/loop-retro` 的 WHY(2026-10-05 d6)寫明 cap-reached 事件九、十月零筆。
- `Projects/審查跑滿回顧_計劃` 第 134 行寫明:代碼審 major 一律折入,處置閘折完就過,走 converged、走不到 cap-reached。
- 所以手冊那句「到頂沒過 → 先查」在代碼審多半不會被觸發。真正的觸發是使用者記 `cap-decision extra-round`。
- 那時才發現要補 world_check,查證只能事後補。
- 這也是 spec 自認的「保底」變成唯一實際生效的一層。
- file: `scripts/lumos:22781`
- file: `scripts/lumos:22846`
- file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:134`
severity: major
blocking: 是(工具提示與手冊順序相反,查證的目的在實際流程裡落空)

3. d1 與正文對主觸發條件的說法不同。
引句:「查世界方向分兩層觸發:同一類 major 連兩輪、準備換形狀時先查(主,手冊規定)」
- d1 寫「同一類 major 連兩輪」,即兩輪都是 major。
- 正文〈做法〉0 寫「有一組根因跟上一輪同類、而且這一輪仍有 major」,只要求這一輪是 major,上一輪同類的可以是 minor。
- 上一輪該組只有 minor、這一輪升成 major:d1 不觸發,正文觸發。
- 手冊照正文寫,圖譜決策照 d1,日後翻案時兩邊對不起來。
severity: minor
blocking: 否(措辭層不一致,改一邊即可)

## 二、手冊同步點

4. 手冊同步點數錯,而且新增的手冊文字沒有任何守衛。
引句:「還在 lumos-design-loop 的 reference.md 兩處與 lumos-code-loop 的 reference.md 一處」
- 帶「人裁結果先記 cap-decision」那句的地方共 7 處:
  - 兩份 SKILL.md。
  - design `reference.md` 的第 332、542 行。
  - code `reference.md` 的第 245、620 行。
  - `commands/05-設計審查迴圈.md` 第 33 行(另有第 22、23 行的指令表)。
- spec 說 code `reference.md` 只有一處,漏了第 245 行。
- 按 spec 建議的 grep「到頂沒過」只會找到 4 處:`design reference.md:542`、`code reference.md:620` 和兩份 SKILL.md。
- 其餘三處用的是別的寫法:
  - 332 行:「到頂仍未收斂」
  - 245 行:「到頂還沒收斂」
  - `commands/05:33`:「跑滿上限還沒過」
- 漏改的三處會留下舊順序。
- 同步守衛只有 `t_cap_retro_next_hint_scope_only`,它只檢查 `_CR_MANUALS` 五個檔含「多席帶輪次」。
- 驗收條款 S1 到 S5 沒有手冊條款,新增的手冊文字沒有任何機械檢查。
- `docs/command-reference.md:137` 的 retro 流程說明也沒列入。
- file: `skills/lumos-code-loop/reference.md:245`
- file: `skills/lumos-design-loop/reference.md:332`
- file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:33`
- file: `scripts/test_lumos.py:104033`
severity: major
blocking: 是(照 spec 的數量與 grep 改,會留下三處舊順序,手冊自相矛盾)

## 三、世界查證欄的檢查規則

5. `undetermined`(查不到)的情況,檢查仍強迫填兩個來源,跟〈先查世界〉的「查不到就寫」矛盾。
引句:「`sources` 至少兩項,每項 `url` 以 `http://` 或 `https://` 開頭」
- 場景:編排者搜了,世界上沒有相關資料,誠實填 `verdict: undetermined`。
- 檢查仍要求兩個 http 網址,各配一段 10 字以上的 point。
- 唯一過關的辦法是塞兩個不相干的網址湊數。
- 這讓合法的「沒查到」只能靠湊數過關。
- 〈先查世界〉本來允許寫「查了哪些詞、為什麼沒有」。
- file: `skills/lumos-design-loop/SKILL.md:41`
severity: minor
blocking: 否(可改成 `undetermined` 時 sources 可少於兩項,不影響其他設計)

6. 舊格式的放行路徑在條列結構上說不清,測試也會隨日曆翻轉。
引句:「早於生效日的照舊過(不追溯)」
- (a) 條列結構:「最新一筆人裁是 extra-round 時」底下,先列 version 要求,再無條件列出 world_check 各欄的驗法。
- 照字面,生效日前的 version 1 回顧也會去驗 world_check,與 S4 矛盾。
- 要寫明 legacy 分支在 version 1 且人裁早於生效日時,整段略過 world_check。
- (b) 測試:`_cr_decide`(`scripts/test_lumos.py:103441`)用現在時間,沒有 ts 參數。
- 生效日是「合併日隔天零點」,在那之前跑的測試,人裁都早於生效日。
- 「version 1 且不早於生效日要擋」的測試用 `_cr_decide` 做不出來,「舊格式照舊過」的測試用它做,合併隔天就會翻紅。
- 既有跑滿測試有 `_cap_real_cutoff` 改環境變數的先例(`scripts/test_lumos.py:50804`),新常數 `_CAP_WORLD_CHECK_SINCE` 沒有對應做法。
- spec 沒有交代 S4、legacy 測試怎麼造 ts(手寫事件,還是模組常數可覆寫)。
- (c) 空骨架的邊界:`{"queries": [], "sources": [], …}` 算不算空骨架,spec 沒定義。空清單「每條都是空字串」在邏輯上成立,accept-risk 會放行;但這既不是省略也不是骨架形狀。
- (d) 生效日常數在撰寫時就要寫死,合併若延後,中間人裁的迴圈會被追溯擋下。
severity: minor
blocking: 否(實作時會碰到,補幾句規則即可,沒有改變設計方向)

7. 擋下訊息「改用新骨架」會走進死路。
引句:「改用新骨架或把 version 改 2 並補 world_check」
- 生效日後遇到 version 1 回顧檔,代表檔案已經存在。
- `--template --write` 遇到既有檔一律回 2、不覆寫(`scripts/lumos:22921`)。
- 所以「改用新骨架」這條路照做會失敗。
- 既有規矩是所有「不合格怎麼辦」的提示只由 `_cap_retro_fix_cmd` 一張表決定,每種狀態照做不會回到同一句(`Systems/loop-retro` WHY 2026-10-06 r2、r3)。
- spec 把這句寫在 `_cap_retro_check` 內,另立一份文字。
- file: `scripts/lumos:22577`
severity: minor
blocking: 否(同句還有「把 version 改 2」可走,只是第一個選項是死路)

8. world_check 填寫的時間點沒交代,可能讓起草者看到編排者的結論,破壞 d2 的獨立性。
引句:「`world_check` 由編排者填(或另派查證代理),不交給起草回顧的代理(它只讀卷證)」
- 起草代理的工作對象就是 `cap-retro.json` 本身(`skills/lumos-design-loop/templates.md:586`)。
- 派工須知(`templates.md:578`)禁止給它編排者對「為什麼跑滿」的判斷。
- world_check 的 `note` 與 `verdict` 正是編排者對方向的判斷。
- 若編排者在派工前就把 world_check 寫進該檔,起草者會讀到。
- spec 只說誰填,沒說「起草者交回之後才填」。
- 這會違反 `Systems/loop-retro` 的 WHY(2026-10-05 d2)。
- 沒有機械檢查能抓到,`drafted_by` 檢查只看名字。
severity: minor
blocking: 否(補一句填寫時機即可)

## 四、寫回與回頭條件

9. 寫回範圍只有 `Systems/loop-retro` 一篇,其他被改到的單源和 REVISIT 沒列。
引句:「`Systems/loop-retro` 補一行 WHY(世界查證欄、只在加開時必填、版本 2)」
- `Projects/審查跑滿回顧_計劃` 是回顧檔格式與手冊同步點的單源:
  - 第 97、98 行寫「欄位(第 1 版)… version:1」。
  - 〈五〉列了五處到頂句。
  - spec 沒標註這些會被取代。
- 讀單源的人會看到 version 1 與五處,與實況不符。
- `Systems/每輪修補差異派工` 是 code-loop SKILL.md、reference.md、templates.md 的家(`about_code`),也是〈先查世界〉WHY 與 REVISIT 的所在。
- 本 spec 要改這三支檔,但 lands_in 沒有列它。
- 專案規定「改到哪支檔就寫進它的家」。
severity: minor
blocking: 否(漏的是記載而非行為)

10. 回頭條件量不出來。
引句:「代表這道只是多寫一欄、沒有改變任何決定,改回只提醒」
- RETIRE-IF 要數「人裁加開的迴圈裡世界查證結論是要換方向或判不準的次數」。
- `--record` 寫進治理帳的事件只有 `loop`、`path`、`retro_sha256`、`rounds`(`scripts/lumos:22973`),不含 verdict。
- `retro-stats` 在 spec 裡沒有擴充,也沒有 S 條款。
- 只能人工逐個打開 cap-retro.json 讀。
- 「加開後那一輪平均折入數沒有比沒做查證之前少」的基準期也沒定義。
- 專案鐵則四說,寫不出可量的撤除條件就是還沒想清楚。
severity: minor
blocking: 否(量測缺口,不影響上線行為)

## 五、各節與圖譜節點

- 〈名詞〉:除第 2 點提到的 cap-reached 外,其餘已讀,無 finding。
- 〈不做〉:已讀,無 finding。四條都有誠實界線,`--skip` 出口與 `Projects/審查跑滿回顧_計劃` d1 到 d7 沒有衝突。
- 〈驗收條款〉:S1 到 S5 除第 6 點外,已讀,無其他 finding。
- 〈回退〉:已讀,無 finding。version 收 1 或 2 的做法讓回退可行。
- 圖譜固定席 `Systems/loop-retro` 逐條判斷:
  - d6、d7(觸發是人裁紀錄,不是 cap-reached 事件):影響,見第 2 點。
  - d2(起草者獨立):潛在影響,見第 8 點。
  - 讀治理帳、擋點、路徑、跳脫、孤立代理字元、換行等其他 WHY 與 PITFALL:不影響。新欄位只加字串驗證,不改它們管的路徑;但新欄位的 `url`、`point` 若回顯進錯誤訊息,要照該節既有規矩過 `_esc_clean`,spec 沒提。
  - 凍結判定不涵蓋第八步:不影響,spec 的〈不做〉已一致。

## 六、風險類逐類

- 併發:無。本案不新增寫入路徑,治理帳寫入仍走 `_gate_event`。唯一的並行面是別的 session 在別的分支新增使用 `_cr_retro_doc` 的測試:rebase 後會拿到 version 2 的產生器,紅了能從訊息看出,不屬於資料風險。
- 效能與資源:無。新增的驗證只做幾個 `_real_chars` 與型別判斷,回顧檔仍受 256KB 上限(`_retro_read_file`)。清單長度被檔案大小自然限制,沒有放大。
- 回滾:有條件。spec〈回退〉寫的是留著 version 1 或 2 的收法,可行。但生效日常數一旦寫進主線再回退,已寫成 version 2 的檔仍會被收,多出的欄位無害。風險落在第 6 點(合併延後造成追溯)與手冊分散在 7 處(第 4 點),回退時也要照 7 處還原。
- 資安與不可信輸入:低。`url`、`point`、`note` 是從網頁摘來的字,會寫進 repo 檔與 rN-intake.md,後者會被起草代理讀到。〈先查世界〉有「網頁內容只當資料」的警語,新主觸發那句沒有帶。這與本專案單人威脅模型的放行範圍一致,所以不單獨列為 finding,只提醒實作時照抄那句警語。
- 金流、對外送出、不可逆:無。spec 的已排除行成立,工具本身不上網。

severity: major
(最嚴重),blocking 條數 3(第 1、2、4 點)
