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
related:
  - "[[Projects/審查跑滿回顧_計劃]]"
decisions:
  - content: 查世界方向分兩層觸發:同一類 major 連兩輪、準備換形狀時先查(主,手冊規定);跑滿三輪要加開時回顧必填 world_check(保底,工具擋)
    id: d1
    context: 高風險測試證據加嚴的設計審 r1、r2 同類接縫問題連兩輪,r2 結束查世界解才換到基準重播站穩;只等跑滿要到 r3 結束才查,多燒一輪
    why_chosen: Enzo 問「是跑滿後查方向，還是連兩輪同樣問題重複改錯的時候就去查？」,評估後回「好」;主觸發時機對但要人判同類,保底機械但太晚,兩層互補;查一次幾分鐘,多一輪設計審約百萬 token
    decided: 2026-11-04
    valid: true
---
# 跑滿後查世界方向_計劃

> 白話:審查迴圈裡「這條路世界上有沒有人走過、走通了沒、有沒有更好的形狀」的查證,分兩層觸發:同一類 major 連兩輪、準備換形狀時先查(主,手冊規定);跑滿三輪要加開時,結論與來源要寫進跑滿回顧,沒寫回顧檢查不過(保底,工具機械擋)。查的是方向,不是怎麼修(怎麼修是每輪修補前那道)。

## 名詞

- 跑滿:設計審或代碼審的輪數到了分級上限(standard 與 high 是 3 輪),帳上狀態變成 cap-reached。
- 人裁:跑滿後使用者決定怎麼走,用 `lumos loop cap-decision <編號> --decision extra-round|accept-risk` 記下;extra-round 是加開一輪,accept-risk 是接受現況收尾。
- 跑滿回顧:人裁之後、繼續之前要寫的回顧檔 `governance/review-reports/<編號>/cap-retro.json`,由沒參與迴圈的代理起草、編排者補完,`lumos loop retro --check` 過了才 `--record`;沒記回顧,`canary record` 與處置閘都會擋(單源 [[Projects/審查跑滿回顧_計劃]])。
- 世界查證:回顧檔新增的一欄,記這次查了什麼、看了哪些來源、結論是方向對、要換方向,還是判不準。

## 問題與最小解

立案(2026-11-04,Enzo 原話):「我希望日後review在超過3輪之後，可以加上一道web搜尋方向對不對的程序」;接著問「是跑滿後查方向，還是連兩輪同樣問題重複改錯的時候就去查？」,評估後回「好」,採兩層觸發(d1)。

起因:風險高測試證據加嚴那份計劃的設計審,第一、二輪各自在紙上換了一次機制形狀,都卡在帳與留痕的接縫上;第二輪後使用者要求「搜世界解」,才查到 fail-to-pass 基準重播,主幹站穩。那個迴圈的跑滿回顧也把原因歸成「每輪換形狀,新接縫要到下一輪才被讀到」。如果跑滿時有一道固定的「方向對不對」查證,換形狀可以早一輪、而且有外部依據。

現有規矩只有「每輪修補前先查怎麼修」(收貨紀錄〈先查世界〉),查的是局部修法;沒有一道在「要不要繼續砸輪數」的決定點,回頭看整條路對不對。

最小解:主觸發只改手冊(同類判斷要靠編排者分組,設計審沒有機械訊號);保底不加新指令,在跑滿回顧檔加一欄必填的世界查證,`--check` 驗格式,只在人裁加開時必填。

PRIOR-ART:Stage-Gate(Cooper)在每個關卡做 go/kill/hold/recycle 決定,加碼投入前要重看外部證據與替代方案,而不是只看自己做了什麼——跑滿上限就是這裡的關卡;本 repo 既有的〈先查世界〉是每輪修補層級的同一個想法。借用:跑滿回顧的骨架、`--check` 的逐欄驗法與 `bad()` 列錯方式、`version` 欄;自建:世界查證欄與它的驗法。
RETIRE-IF:生效後半年內,人裁加開的迴圈裡世界查證結論是「要換方向」或「判不準」的次數為 0,而且加開後的那一輪平均折入數沒有比沒做查證之前少——代表這道只是多寫一欄、沒有改變任何決定,改回只提醒。

## 做法

0. **主觸發(手冊)**:lumos-design-loop SKILL.md 第 6 步〈折入〉與 lumos-code-loop SKILL.md 第 5 步〈修與釘〉各加一句:收貨分組時,有一組根因跟上一輪同類、而且這一輪仍有 major,決定新形狀之前先上網查方向(同樣的問題世界上用什麼形狀解、有沒有實證說走不通、有沒有更簡單的既有做法;至少兩個來源),結論與來源寫進 rN-intake.md 的〈世界查證〉,攤給人裁時一起給。只限 major。代碼審的修正紀錄已有「這類上一輪出現過」的 prior 欄,之後可以拿它當機械提醒,這份計劃不做(見回頭條件)。
1. **骨架**:`lumos loop retro --template --write` 產的骨架 `version` 改成 2,多一欄 `world_check`:`{"queries": [""], "sources": [{"url": "", "point": ""}], "verdict": "", "note": ""}`。
2. **檢查**(`_cap_retro_check`):
   - `version` 收 1 或 2;其他值照舊擋。
   - 最新一筆人裁是 extra-round 時:
     - `version` 要是 2;是 1 而且那筆人裁的時間(事件的 `ts`,用 `_loop_ts_key` 解)不早於生效日(程式常數 `_CAP_WORLD_CHECK_SINCE`,帶時區的完整時間戳,寫法同 `_SPEC_GATE_SINCE`,值取合併日的隔天零點)就擋,講「改用新骨架或把 version 改 2 並補 world_check」;早於生效日的照舊過(不追溯);`ts` 解不開當成生效日之後。沒有人裁紀錄(`decision` 是空的,既有測試這樣呼叫)不要求 world_check、不崩。
     - 先驗型別再數字數(`_real_chars` 遇到非字串會丟例外):`world_check` 要是物件、`queries` 要是字串清單、`sources` 要是物件清單而且每項的 `url` 與 `point` 是字串、`verdict` 與 `note` 是字串;型別不對逐欄列出,不丟堆疊。
     - `world_check` 要是物件;`queries` 至少一條、每條去掉空白標點後至少 4 個字(`_real_chars`);`sources` 至少兩項,每項 `url` 以 `http://` 或 `https://` 開頭、`point`(這個來源說了什麼)用 `_real_chars` 數至少 10 個字,兩項的 `url` 不能相同;`verdict` 只收 `direction-ok`、`change-direction`、`undetermined`;`note` 用 `_real_chars` 數至少 20 個字。不合的逐欄列出,跟既有欄位同一種列法。
   - 最新一筆人裁是 accept-risk 時:`world_check` 可以是空骨架或省略;有填就照上面驗(填一半算錯)。空骨架指 queries 每條、每個 source 的 url 與 point、verdict、note 去掉空白後全是空字串;只要有一格不是空的就算「有填」。
   - 字數口徑:`_real_chars` 數的是去掉空白標點後的字元,中文一字算一、英文一個字母算一(`a b c d` 也算 4);跟既有 `why_cap`、`avoid` 用的 `_retro_text_ok`(去頭尾空白後的長度)不同,新欄位刻意用 `_real_chars` 擋全標點的湊字。
3. **記帳時提醒**:`--record` 成功、`verdict` 是 `change-direction` 時多印一行「世界查證認為要換方向:加開前先跟人確認新方向,別照原方向直接派下一輪」;是 `undetermined` 時印「世界查證判不準方向,加開時把這點跟人講清楚」。只印不擋。
4. **手冊**:lumos-design-loop 與 lumos-code-loop 的 SKILL.md〈停手與護欄〉跑滿那一條,在「到頂沒過 → 停,攤給人裁」之前插一步:先上網查方向(查什麼同第 0 點;至少兩個來源),結論附在攤給人裁的訊息裡;人裁加開後,把同一份結論寫進回顧的 `world_check`。順序是查 → 攤人裁 → 記 cap-decision → 寫回顧,讓結論影響得到「要不要加開」。同一句「到頂沒過」還在 lumos-design-loop 的 reference.md 兩處與 lumos-code-loop 的 reference.md 一處([[Projects/審查跑滿回顧_計劃]]〈五〉列的同步點),一起改。templates.md §9 的編排者須知補一句:`world_check` 由編排者填(或另派查證代理),不交給起草回顧的代理(它只讀卷證)。
5. **寫回**:`Systems/loop-retro` 補一行 WHY(世界查證欄、只在加開時必填、版本 2)。
6. **既有測試**:測試的回顧產生器 `_cr_retro_doc` 寫死 `version: 1`、`_cr_decide` 預設 extra-round 而且時間用現在,生效後幾乎所有跑滿回顧測試都會被新規則擋;產生器改成預設 version 2 並帶一份合格的 world_check,另寫一支舊格式的測試釘「生效日前的 version 1 照舊過」;釘 `version == 1` 的那支骨架測試改成 2。

## 不做

- 不驗「真的有上網查」:工具只驗格式,AI 可以編網址;這跟本工具鏈的信任原則一致(單人、AI 依序操作,不防刻意偽造),天花板照實寫。
- 不在 accept-risk 時強制:那是收尾、不再砸輪數,查方向的價值在「要不要繼續」。
- 不改 `canary record` 的擋法:它本來就要求合格的回顧(或跳過紀錄),回顧不合格自然擋;處置閘的凍結判定與 code-loop pass 那條路本來就不驗回顧(既有天花板,[[Systems/loop-retro]] 已記)。
- 不拿掉 `--skip`:人裁後選擇不寫回顧是既有的出口(使用者核准過),走這條路就不驗世界查證;照實列為天花板,跳過次數 gov 統計本來就數。

## 驗收條款

- [S1] 當執行 lumos loop retro <編號> --template --write 時,骨架的 version 應是 2,並帶 world_check 的空殼(queries、sources、verdict、note) [test:t_retro_template_world_check]
- [S2] 當最新一筆人裁是 extra-round、回顧 version 是 2,而 world_check 缺少、queries 沒有一條夠 4 個字、sources 少於兩項或網址不是 http 開頭或兩項網址相同或 point 不到 10 個字、verdict 不在三個值裡、或 note 不到 20 個字時,loop retro --check 應判不過並逐欄列出 [test:t_retro_check_world_check]
- [S3] 當最新一筆人裁是 accept-risk 時,world_check 省略或是空骨架應照樣過;填了一半應判不過 [test:t_retro_check_world_check_accept_risk]
- [S4] 當最新一筆人裁是 extra-round、時間不早於生效日,而回顧 version 是 1 時,loop retro --check 應判不過並講要改用新骨架;人裁時間早於生效日的 version 1 回顧應照舊過 [test:t_retro_check_world_check_legacy]
- [S5] 當 loop retro --record 成功而 world_check 的 verdict 是 change-direction 或 undetermined 時,應各印一行對應的提醒而且不擋 [test:t_retro_record_world_verdict]

## 回退

拿掉 `world_check` 的驗法與記帳提醒,骨架改回 version 1;已寫成 version 2 的回顧檔讓檢查照收(version 收 1 或 2 那段留著),多出的欄位無害。手冊那一步刪掉,`Systems/loop-retro` 的 WHY 標作廢。

## 實務隱患
- 已排除:金流:只改審查迴圈的回顧檢查,不碰收費或扣款流程
- 已排除:對外送出:工具本身不上網;上網查是編排者在對話裡做,結果寫進本機檔
- 已排除:不可逆:只多驗一欄,回顧檔是本機檔、帳是追加的;生效日讓既有迴圈不受影響,改壞了回退就回來
- 守衛面:跑滿回顧是加開輪之前的關卡,改的是它的放行條件,走設計審與代碼審
- 相容:舊的 version 1 回顧(生效日前人裁的)照舊過;生效日後人裁加開還拿舊骨架的,擋下訊息要講怎麼補
- 天花板一:格式對不等於真的查過、查得對;結論是人裁時的參考,不是工具判定
- 天花板二:跑滿後用 `--skip` 不寫回顧,世界查證跟著不驗
- 天花板三:主觸發(同類 major 連兩輪)只有手冊規定,判不判「同類」靠編排者分組
REVISIT:2027-02-04 看這段期間跑滿加開的迴圈:用 `--skip` 跳過回顧的佔幾成、主觸發有沒有在 intake 留下〈世界查證〉;跳過超過三成就把「加開時不准 --skip」提出來給人裁,主觸發幾乎沒留紀錄就拿代碼審修正紀錄的 prior 欄做機械提醒
