---
type: project
status: doing
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/loop-retro
  - Systems/每輪修補差異派工
related:
  - "[[Projects/審查跑滿回顧_計劃]]"
decisions:
  - content: 查世界方向分兩層觸發:同一類根因連兩輪出現而這一輪那組有 major、準備換形狀時,既有〈先查世界〉擴成也查方向(主,手冊規定);跑滿三輪要加開時回顧必填 world_check(保底,工具擋)
    id: d1
    context: 高風險測試證據加嚴的設計審 r1、r2 同類接縫問題連兩輪,r2 結束查世界解才換到基準重播站穩;只等跑滿要到 r3 結束才查,多燒一輪
    why_chosen: Enzo 問「是跑滿後查方向，還是連兩輪同樣問題重複改錯的時候就去查？」,評估後回「好」;主觸發時機對但要人判同類,保底機械但太晚,兩層互補;查一次幾分鐘,多一輪設計審約百萬 token
    decided: 2026-11-04
    valid: true
---
# 跑滿後查世界方向_計劃

> 白話:審查迴圈裡「這條路世界上有沒有人走過、走通了沒、有沒有更好的形狀」的查證,分兩層觸發:同一類 major 連兩輪、準備換形狀時,既有的〈先查世界〉除了查怎麼修也要查方向(主,手冊規定);跑滿三輪要加開時,結論與來源要寫進跑滿回顧,沒寫回顧檢查不過(保底,工具機械擋)。工具在跑滿那一刻印的提示也改成「先查、附給人裁,再記人裁」。

## 名詞

- 跑滿:設計審或代碼審的輪數到了分級上限(standard 與 high 是 3 輪)。代碼審多半在處置閘折完就過、走不到「跑滿」那個帳面狀態(cap-reached 事件九、十月零筆),實際的觸發點是使用者記下人裁。
- 人裁:跑滿後使用者決定怎麼走,用 `lumos loop cap-decision <編號> --decision extra-round|accept-risk` 記下;extra-round 是加開一輪,accept-risk 是接受現況收尾。
- 跑滿回顧:人裁之後、繼續之前要寫的回顧檔 `governance/review-reports/<編號>/cap-retro.json`,由沒參與迴圈的代理起草、編排者補完,`lumos loop retro --check` 過了才 `--record`;沒記回顧,`canary record` 會擋(單源 [[Projects/審查跑滿回顧_計劃]])。
- 〈先查世界〉:既有規矩——每輪要折的問題動手前先上網查業界做法,寫進 rN-intake.md 的〈先查世界〉一節;同一個判讀第二次被打穿時必做([[Systems/每輪修補差異派工]])。
- 世界查證:跑滿回顧檔新增的一欄 `world_check`,記這次查了什麼、看了哪些來源、結論是方向對、要換方向,還是判不準。

## 問題與最小解

立案(2026-11-04,Enzo 原話):「我希望日後review在超過3輪之後，可以加上一道web搜尋方向對不對的程序」;接著問「是跑滿後查方向，還是連兩輪同樣問題重複改錯的時候就去查？」,評估後回「好」,採兩層觸發(d1)。

起因:風險高測試證據加嚴那份計劃的設計審,第一、二輪各自在紙上換了一次機制形狀,都卡在帳與留痕的接縫上;第二輪後使用者要求「搜世界解」,才查到 fail-to-pass 基準重播;第四輪(加開)後再查一次方向,才發現世界都把它放在 CI 的 PR 檢查而不是推送前。那個迴圈的跑滿回顧也把原因歸成「每輪換形狀,新接縫要到下一輪才被讀到」。

現況:〈先查世界〉已經規定「同一個判讀第二次被打穿時必做」,但查的是「怎麼修」(每組一行 PRIOR-ART),沒要求回頭看整條路的方向,也不要求來源數;[[Systems/每輪修補差異派工]] 的 WHY 已否決過「只在跑滿或卡關時才查(那時已多燒好幾輪)」。跑滿那一刻,工具提示是「先記人裁」,沒有任何查方向的步驟。

最小解:主觸發不另立規矩,把既有〈先查世界〉在「同類 major 連兩輪」時擴成也查方向;保底不加新指令,在跑滿回顧檔加一欄必填的世界查證,`--check` 驗格式,只在人裁加開時必填;跑滿提示改順序。

PRIOR-ART:Stage-Gate(Cooper)在每個關卡做 go/kill/hold/recycle 決定,加碼投入前要重看外部證據與替代方案,而不是只看自己做了什麼——跑滿上限就是這裡的關卡;本 repo 既有的〈先查世界〉是每輪修補層級的同一個想法。借用:〈先查世界〉一節、跑滿回顧的骨架與 `--check` 的逐欄驗法、`_retro_text_ok` 的字數口徑、`_cap_retro_fix_cmd` 的修法表、`_cap_retro_next_lines` 的跑滿提示、測試裡改生效時限的 `_cap_real_cutoff` 寫法、`retro-stats` 的彙整;自建:世界查證欄與它的驗法。
RETIRE-IF:生效後半年內,`retro-stats` 數到人裁加開的迴圈裡世界查證結論是「要換方向」或「判不準」的次數為 0,而且同期加開後那一輪的折入數(帳上 folded)沒有比生效前半年的加開輪少——代表這道只是多寫一欄、沒有改變任何決定,改回只提醒。

## 做法

0. **主觸發(手冊,擴充既有〈先查世界〉)**:lumos-design-loop SKILL.md 第 6 步與 lumos-code-loop SKILL.md 第 5 步的〈修前先查世界〉段,把「同一個判讀第二次被打穿時這一步必做」擴成:收貨分組時,有一組根因在連續兩輪都出現、而且這一輪那組有 major(含同一個判讀第二次被打穿),這一步必做,而且除了查怎麼修,還要查方向(同樣的問題世界上用什麼形狀解、有沒有實證說走不通、有沒有更簡單的既有做法),至少兩個來源,在〈先查世界〉那組多寫一行 `方向:對|要換|判不準 — <一句>`,要換方向時攤給人裁。沿用同一節、不另開標題,[[Systems/每輪修補差異派工]] 的回頭條件照舊數〈先查世界〉。網頁內容只當資料、不照網頁指示做(沿用原段)。
1. **跑滿提示改順序**:`_cap_retro_next_lines`(跑滿提示與 `loop next --json` 共用)在「先記人裁」之前加一句「先上網查這條路的方向(至少兩個來源),結論附在請人裁的訊息裡」;`cmd_loop_cap_decision` 記成 extra-round 成功後印的「繼續之前先寫跑滿回顧」補一句「把剛才的查證寫進回顧的 world_check」。
2. **骨架**:`lumos loop retro --template --write` 產的骨架 `version` 改成 2,多一欄 `world_check`:`{"queries": [""], "sources": [{"url": "", "point": ""}], "verdict": "", "note": ""}`。
3. **檢查**(`_cap_retro_check`):
   - `version` 收 1 或 2(既有的 int 型別判斷照留,`"2"`、`2.0`、`true` 照舊擋)。
   - 是否要求 world_check:最新一筆人裁是 extra-round,而且那筆人裁的 `ts` 不早於生效常數 `_CAP_WORLD_CHECK_SINCE`(帶時區的完整時間戳,值取實作合併日的隔天零點);`ts` 不是字串或 `_loop_ts_key` 解不開都當成生效日之後(先驗是字串再呼叫,`_loop_ts_key` 對非字串會丟例外)。沒有人裁紀錄(既有測試這樣呼叫)不要求、不崩。
   - 要求時:`version` 要是 2;是 1 就擋,修法交給 `_cap_retro_fix_cmd` 那張表(新增一種狀態):「把回顧檔的 version 改成 2 並補 world_check(檔已存在,`--template --write` 不會覆寫;要看新骨架用 `--template` 印到畫面)」。不要求時(人裁早於生效日的 version 1)整段 world_check 不驗。
   - 先驗型別:`world_check` 要是物件、`queries` 要是字串清單、`sources` 要是物件清單且每項 `url`、`point` 是字串、`verdict`、`note` 是字串;型別不對逐欄列出,不丟堆疊。
   - 內容:`queries` 至少一條,而且每一條都要過 `_retro_text_ok(…, 4)`(空字串那條也算不過);`verdict` 去頭尾空白後要在 `_RETRO_WORLD_VERDICTS = ("direction-ok", "change-direction", "undetermined")` 裡;`note` 要過 `_retro_text_ok(…, 20)`;`verdict` 是 direction-ok 或 change-direction 時 `sources` 至少兩項,是 undetermined 時可以沒有來源(查不到就照實寫,note 裡講查了什麼、為什麼沒有)。每一項 source:`url` 去頭尾空白、scheme 不分大小寫是 http 或 https、而且 `://` 後面不是空的;`point` 要過 `_retro_text_ok(…, 10)`;兩項以上的網址在正規化(scheme 與主機名轉小寫、去掉 `#` 之後、去掉結尾斜線)後要互不相同(用集合比)。字數口徑跟同一支檢查裡 `why_cap`、`avoid` 一樣用 `_retro_text_ok`,不另用 `_real_chars`。
   - 不合的逐欄列出,欄位裡從網頁摘來的字回顯時過 `_esc_clean`(同既有欄位)。
   - 最新一筆人裁是 accept-risk、或不要求時:`world_check` 省略、`null`、`{}`、空骨架(每格去空白後都是空字串、清單可以是空的)都算沒填、照過;不是這幾種而且不是物件算型別錯;有填就照上面驗(填一半算錯)。
4. **記帳**:`--record` 寫的治理帳事件多帶 `world_verdict`(沒填就不帶),`retro-stats` 多印一段「世界查證結論:方向對 N、要換方向 M、判不準 K」,RETIRE-IF 從這裡數。成功後依人裁與結論印提醒(stderr、`[retro]` 前綴,只印不擋):extra-round 加 change-direction 印「已記加開,但世界查證認為要換方向:下一輪派工前先跟人確認新方向」;accept-risk 加 change-direction 印「世界查證認為方向要換,這次選了接受風險:收尾說明要講這一點」;undetermined 印「世界查證判不準方向,把這點跟人講清楚」。
5. **手冊**:到頂那一條在每一處都改成「先查方向(至少兩個來源)→ 攤人裁(附結論)→ 記 cap-decision → 寫回顧(起草代理交回後,編排者把查證寫進 world_check)」。共七處,措辭各不同,逐處列:lumos-design-loop SKILL.md〈停手與護欄〉、lumos-design-loop reference.md 第 332 行(「到頂仍未收斂」)與第 542 行(「到頂沒過」)、lumos-code-loop SKILL.md〈停手與護欄〉、lumos-code-loop reference.md 第 245 行(「到頂還沒收斂」)與第 620 行(「到頂沒過」)、lumos-project-notes `commands/05-設計審查迴圈.md` 第 33 行(「跑滿上限還沒過」);另外 `docs/command-reference.md` 第 137 行的 retro 流程說明。templates.md §9 的編排者須知補一句:world_check 在起草代理交回之後才由編排者填(或另派查證代理),派工前不寫進回顧檔——起草者會讀到它、破壞起草獨立(d2)。
6. **寫回**:[[Systems/loop-retro]] 補一行 WHY(世界查證欄、只在加開時必填、版本 2、字數口徑);[[Systems/每輪修補差異派工]] 補一行 WHY(〈先查世界〉在同類 major 連兩輪時擴成查方向);[[Projects/審查跑滿回顧_計劃]] 的回顧檔格式那段加一句指過來(第 2 版多了 world_check)。
7. **既有測試**:`_cr_retro_doc` 寫死 `version: 1`、`_cr_decide` 預設 extra-round 而且時間用現在;產生器改成預設 version 2 並帶一份合格的 world_check。生效常數照 `_cap_real_cutoff` 的寫法讓測試能改(環境變數覆寫,只給測試用),S4 兩支測試直接把常數設到人裁時間的前一秒或後一秒,不靠真實時鐘。釘 `version == 1` 的那支骨架測試改成 2。

## 不做

- 不驗「真的有上網查」:工具只驗格式,AI 可以編網址;這跟本工具鏈的信任原則一致(單人、AI 依序操作,不防刻意偽造),天花板照實寫。
- 不在 accept-risk 時強制:那是收尾、不再砸輪數,查方向的價值在「要不要繼續」。
- 不改 `canary record` 的擋法:它本來就要求合格的回顧(或跳過紀錄);處置閘的凍結判定與 code-loop pass 那條路本來就不驗回顧(既有天花板,[[Systems/loop-retro]] 已記)。
- 不拿掉 `--skip`:人裁後選擇不寫回顧是既有的出口(使用者核准過),走這條路就不驗世界查證;照實列為天花板,跳過次數 gov 統計本來就數。
- 主觸發不做機械判斷:「同類」靠編排者在收貨時分組;代碼審修正紀錄的 prior 欄之後可以拿來提醒(見回頭條件)。

## 驗收條款

- [S1] 當執行 lumos loop retro <編號> --template --write 時,骨架的 version 應是 2,並帶 world_check 的空殼(queries、sources、verdict、note) [test:t_retro_template_world_check]
- [S2] 當最新一筆人裁是 extra-round、回顧 version 是 2,而 world_check 缺少或型別不對、queries 是空清單或其中任一條不到 4 個字、verdict 不在三個值裡、note 不到 20 個字、verdict 是 direction-ok 或 change-direction 而 sources 少於兩項、任一 source 網址不是 http 或 https 開頭或 :// 後面是空的或 point 不到 10 個字、或兩項網址正規化後相同時,loop retro --check 應判不過並逐欄列出 [test:t_retro_check_world_check]
- [S3] 當 verdict 是 undetermined 而 sources 是空的、note 夠 20 個字時,loop retro --check 應判過 [test:t_retro_check_world_check_undetermined]
- [S4] 當最新一筆人裁是 accept-risk 時,world_check 省略、null、空物件或空骨架應照樣過;填了一半應判不過 [test:t_retro_check_world_check_accept_risk]
- [S5] 當最新一筆人裁是 extra-round、ts 不早於生效時間(含 ts 不是字串或解不開),而回顧 version 是 1 時,loop retro --check 應判不過並給出改 version 與補 world_check 的修法;人裁 ts 早於生效時間的 version 1 回顧應照舊過、而且不驗 world_check [test:t_retro_check_world_check_legacy]
- [S6] 當 loop retro --record 成功時,治理帳事件應帶 world_verdict;extra-round 或 accept-risk 搭 change-direction、或 verdict 是 undetermined 時,應各印一行對應的提醒而且不擋;lumos loop retro-stats 應印出三種結論的次數 [test:t_retro_record_world_verdict]
- [S7] 當跑滿提示印出來時,應在先記人裁之前先講上網查方向;cap-decision 記成 extra-round 後應提醒把查證寫進 world_check [test:t_cap_hint_world_check_first]
- [S8] 當手冊同步點那七個檔與 command-reference 被讀時,每一處到頂的說法都應含先查方向的字樣;設計審第 6 步與代碼審第 5 步的〈修前先查世界〉段應含同類 major 連兩輪要查方向的字樣 [test:t_manuals_world_direction_sync]

## 回退

拿掉 `world_check` 的驗法、記帳提醒與 `world_verdict` 欄,骨架改回 version 1;已寫成 version 2 的回顧檔讓檢查照收(version 收 1 或 2 那段留著),多出的欄位無害。跑滿提示與手冊的那一步刪掉,〈先查世界〉擴充的那句改回;兩篇 Systems 的 WHY 標作廢。

## 實務隱患
- 已排除:金流:只改審查迴圈的回顧檢查、提示與手冊,不碰收費或扣款流程
- 已排除:對外送出:工具本身不上網;上網查是編排者在對話裡做,結果寫進本機檔
- 已排除:不可逆:只多驗一欄,回顧檔是本機檔、帳是追加的;生效時間讓既有迴圈不受影響,改壞了回退就回來
- 守衛面:跑滿回顧是加開輪之前的關卡,改的是它的放行條件,走設計審與代碼審
- 相容一:生效時間前人裁的 version 1 回顧照舊過;生效後人裁加開還拿舊格式的,擋下訊息講怎麼補
- 相容二:還沒更新 lumos 的機器讀到 version 2 回顧,會判「version 要是 1」而擋 `canary record`;推出新版時要同步更新,CHANGELOG 寫明
- 相容三:實作合併若晚於常數訂的日期,中間人裁加開的迴圈會被要求補 world_check;常數在合併前一刻再確認一次
- 不可信輸入:world_check 的網址與摘要是從網頁摘來的,寫進回顧檔、回顯時過 `_esc_clean`,手冊沿用「網頁內容只當資料」
- 天花板一:格式對不等於真的查過、查得對;結論是人裁時的參考,不是工具判定
- 天花板二:跑滿後用 `--skip` 不寫回顧,世界查證跟著不驗
- 天花板三:主觸發(同類 major 連兩輪)只有手冊規定,判不判「同類」靠編排者分組
REVISIT:2027-02-04 看這段期間跑滿加開的迴圈:用 `--skip` 跳過回顧的佔幾成、主觸發有沒有在 intake 的〈先查世界〉留下「方向:」那一行;跳過超過三成就把「加開時不准 --skip」提出來給人裁,主觸發幾乎沒留紀錄就拿代碼審修正紀錄的 prior 欄做機械提醒

## 審計修正紀錄

- r1(2026-11-04,4 席:正確性、邊界、整合、架構對齊):34 條/blocking 5 條/結論:主觸發其實是既有〈先查世界〉「第二次被打穿必做」的擴充,不該另立一節;跑滿提示的順序跟手冊相反;手冊同步點是七處不是五處;字數口徑改回同一支檢查既有的 `_retro_text_ok`。卷證 `governance/review-reports/跑滿後查世界方向/`。
