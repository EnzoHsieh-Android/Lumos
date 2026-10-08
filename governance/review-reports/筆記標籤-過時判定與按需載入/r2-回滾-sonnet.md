severity: major

審查範圍:/tmp/tags/r2.md 全文,鏡頭是回滾。hook 沒有附固定席筆記,所以「逐條判不影響」那項沒有對象可判。

上一輪回滾席(r1-回滾-sonnet.md)的 K1(取代鏈欄位)、K2(單一 gate 開關)、K4(init 寫入)、K9(決策取代鏈並行)已因設計改寫而消失:不再有 `superseded-by`,有獨立子開關,也不改 `lumos init`。K7(第 0 步 W4 沒有開關)這一版仍然存在,見 R2K5。

**R2K1 既有專案舊筆記裡的 HTML 數量標記,會在欄位判定上線後自動變成擋推送,只能每個專案各自改設定退**
severity: major
blocking: 是——照字面實作,S1 與「不溯及既往」的承諾對舊標記不成立,實作者會做出自動擋住舊專案的行為。
1. 輸入:消費專案的舊筆記裡已有 `<!--lumos:count=N re=… in=…-->`。例如 Check N 自家說明引用的 LandmarkMember 事件,和這個 repo 的 `docs/lumos-toolchain-knowledge/Systems/check-n-recomputable.md`。這些標記現在只由 doctor N 重算,而且只是提醒、不擋(`scripts/lumos:3010`)。
2. 走到〈欄位 v1〉的「正規式數量」:存量漂移檢查改成在「這次推送改到符合 `in=` 的檔」時重算,從吻合變不吻合就擋。
3. 這道擋掛在 `drift_check.fields`,預設 block,而且〈不溯及既往怎麼做〉與 S1 只說「沒寫依賴欄位的筆記完全不受影響」。舊標記不是「欄位」,卻照樣進入判定。
4. 回滾上,每個有舊標記的消費專案第一次推送改到 `in=` 範圍的程式,就被新增的擋卡住。沒有任何不改設定的收回方式。
5. 要退只能各專案各自提交 `drift_check.fields: off`。這又要靠設定檔,而 `lumos init` 不寫預設值。
6. 修法方向是 ⚠ 交編排者:要不要讓舊標記預設只提醒,或把標記納入判定改成需要明確 opt-in。
引句:「這次推送改到符合 `in=` 的檔,才重算那個標記」
佐證:`scripts/lumos:3010-3017`、`scripts/lumos:2933`

**R2K2 `drift_check.fields` 與既有 `gate` 的關係沒定,壞值方向還與它自稱「照先例」的先例相反**
severity: major
blocking: 是——不同實作者會做出相反的行為:把 `gate=warn/off` 的專案升成擋,或在壞設定下的行為與先例不符。
1. 輸入:已經自己寫了 `drift_check.gate=warn`(分階段上線)或 `off` 的消費專案。
2. 現有程式把兩個開關各管各的:`cmd_drift_check` 把 `gate` 傳給 c1 到 c5 與 probe,把 `old_sentence` 傳給 m1(`scripts/lumos:29778-29803`)。`gate=off` 時 `_drift_check_c` 直接回 0(`scripts/lumos:29806-29813`)。
3. spec 加了第三個獨立開關 `fields`,預設 block。`gate=warn` 的專案因此被新檢查擋,而它刻意選了不擋。`gate=off` 的專案要不要跳過欄位判定,spec 沒定。
4. 壞值方向:spec 寫「壞值照 block」並稱「照 `drift_check.old_sentence` 的先例」。但 `_drift_old_sentence_config` 的先例是壞值與設定檔壞掉一律 warn,預設也是 warn(`scripts/lumos:29724-29738`)。只有 `gate` 的預設是 block。
5. 兩個先例方向不同,spec 引的名字與寫的行為不一致,實作者無從判斷該照哪個。
6. 這直接決定「關開關退不退得乾淨」:設定檔被寫壞的專案想關掉 `fields`,卻因壞值照 block 而關不掉。
引句:「加子開關 `drift_check.fields`(block 預設,壞值照 block 並講一句,照 `drift_check.old_sentence` 的先例)」
佐證:`scripts/lumos:29724-29738`、`scripts/lumos:29741-29756`、`scripts/lumos:29778-29803`

**R2K3 欄位擋下指向的 `drift ack` 只收既有七種 kind,spec 沒定新發現的 kind,印出與表態兩條路都會壞**
severity: major
blocking: 是——照字面實作,擋下訊息教人貼的 ack 指令會被拒,或在印發現時直接例外。
1. 輸入:一筆欄位判定的發現(count、value、lives 或標記)。
2. 擋下訊息要附 `drift ack`。但 `_DRIFT_KINDS = ("probe","c1","c2","c3","c4","c5","m1")`(`scripts/lumos:27554`)。
3. `drift ack --kind` 的 argparse 選項是 `choices=_DRIFT_KINDS`(`scripts/lumos:40602`),`_drift_ack_args_err` 對不在內的 kind 回錯(`scripts/lumos:28861`)。
4. `_drift_print_findings` 用 `_DRIFT_KIND_NAMES[f['kind']]` 直接取值(`scripts/lumos:29729` 附近的印出段),新 kind 沒有中文名就是 KeyError。
5. `_drift_load_acks` 還會過濾掉 kind 不在 `_DRIFT_KINDS` 的 ack 列(`scripts/lumos:28751`)。
6. 回滾上:新 kind 一旦加進表,消費專案留下的 ack 帳列在還原提交後會被這個過濾靜默丟掉。這不致命,但 spec 的〈回退〉沒提。
7. spec 全文沒出現新增 kind、`_DRIFT_KIND_NAMES`、`_drift_fix_hint` 的條目。〈分期〉第 1 步只寫「發現種類記進治理帳既有的 `drift-check` 閘」。
引句:「加上單次跳過(`LUMOS_SKIP_DRIFT_CHECK=1`,既有)與 `drift ack`(既有)的指令」
佐證:`scripts/lumos:27554-27559`、`scripts/lumos:28751`、`scripts/lumos:28861`、`scripts/lumos:40602`

**R2K4 「舊帳由 doctor 列出」沒有任何分期項與條款承接,關掉再打開欄位判定之間的漂移會永久看不見**
severity: major
blocking: 是——合約候選 S3 與原則 3 依賴 doctor 兜底,但字面實作不含這一半,「不擋」變成「永遠沒人看」。
1. 輸入:`drift_check.fields` 先 off(或還原提交)一段時間,期間程式改了、欄位數字沒跟上;之後重新開啟。
2. 欄位起點(推送前版本)與終點都不吻合,依 S3 一律不擋。
3. 原則 3 與 S3 都說「舊帳由 doctor 列出」。但〈分期〉第 0 到 4 步沒有任何一步是 doctor 列出陳舊欄位,驗收條款也沒有對應的 `[test:]`。
4. 〈回退〉還說「欄位留著無害」,把「關掉再開」當安全操作,實際上這段期間漂移的欄位會變成永久失效的假守衛。
5. 沒有 doctor 那一半,S3 的「舊帳不擋」就沒有對應的出口。
引句:「起點就已經對不上的舊帳不擋(doctor 列出)」

**R2K5 W4 在第 0 步先出貨,而管它的開關 `note_shape.tag_hints` 要到第 2 步才有**
severity: minor
blocking: 否——只是多印提醒、不擋推送,但回滾口徑與〈相容〉的說法不符。
1. 輸入:W4(新寫 RULE 行缺 since、retire、until 過期)。
2. 〈分期〉第 0 步出貨 W4,第 2 步才出 `note_shape.tag_hints`。〈實務隱患〉的相容那條卻說 W4 在所有專案出現,「要關就 `note_shape.tag_hints: off`」。
3. 第 0 步到第 2 步之間沒有開關。若第 2 步被還原而第 0 步留著,W4 也沒有開關,S14 把 W4 列為被 `tag_hints: off` 關掉,與這個狀態不符。
4. 這是 r1 回滾席 K7 的殘留,這一版只把 W4 放進第 0 步,沒補開關。
引句:「要關就 `note_shape.tag_hints: off`」
佐證:`scripts/lumos:3268`(RULE 效力判定註解所在位置,W4 的提醒邏輯也在這一帶)

**R2K6 回退第 3 步說「撤掉後只剩 RULE 行有意義」,但既有 lint 對 RULE 的 superseded 行叫人刪掉,與新設計的「留著、隱藏」相反**
severity: minor
blocking: 否——只影響提醒措辭與還原後的閱讀,不會做出壞的擋行為。
1. 既有的 RULE lint 對 `[status:superseded]` 的說法是「確定撤掉就把整行刪掉,別留著讓人誤讀」(`scripts/lumos:3336-3338`)。
2. 新設計要求這種行留著並附連結,搜尋預設隱藏。W4 又是對新 RULE 行印 lint 警告,同一行會同時被叫「刪掉」。spec 沒處理這個措辭衝突。
3. 回滾上,第 3 步還原後,新寫在 WHY、PITFALL 上的 `[status:superseded]` 行不再被任何搜尋隱藏。舊的被取代決定重新像現行決定一樣出現。這與〈回退〉的「無害」不符。
引句:「`[status:superseded]` 是既有欄位,擴大適用撤掉後只剩 RULE 行有意義」
佐證:`scripts/lumos:3334-3339`

各節已讀,無其他 finding:
- 〈現況〉、〈設計原則〉、〈前綴表〉:已讀,無 finding。
- 〈寫法提醒〉:除 R2K5 外無 finding。W1 到 W6 只在上線點之後新增的行出現,關掉或還原都不留帳。
- 〈按需載入〉:唯讀,還原提交即可;stderr 印隱藏行數已補上 r1 K3。無 finding。
- 〈不溯及既往怎麼做〉、〈分期〉:除 R2K1、R2K4 外無 finding。
- 〈實務隱患〉逐類:
  - 併發:無,只沿用既有寫帳點。
  - 效能:無,數量重算受 `_DRIFT_BUDGET_SEC=60` 管(`scripts/lumos:27572`)。
  - 資源:無,不開長駐程序。
  - 回滾:有,見 R2K1、R2K2、R2K4、R2K6。
  - 相容:有,見 R2K5。
  - 注入:無,輸出是唯讀片段。
  - 自我治理:`LUMOS_SKIP_DRIFT_CHECK` 與 `drift ack` 是既有,新 kind 問題見 R2K3。
  - 金流、對外送出、不可逆:無,同 spec 的已排除說明。
- 〈回退〉:第 1 步「關開關」的前提見 R2K1 與 R2K2。其餘各步已讀。
- 〈驗收條款〉、〈合約候選〉:S1 與 R2K1 衝突,S3 缺承接見 R2K4。其餘已讀,無 finding。

最高嚴重度:major,blocking 4 條
