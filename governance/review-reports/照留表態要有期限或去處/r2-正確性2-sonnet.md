severity: major

審查鏡頭:正確性/邏輯(r2 修訂稿)。對照碼:`/Users/enzo/harness/lumos-b1/scripts/lumos`。圖譜節點:派工時沒有附上合約/事故節點,無可逐條判的固定席。

## F1 舊表態寬限日用設計日算,沒照 Enzo 裁的「上線日起算」
severity: major
blocking: 是——規格自己引的裁定與做法互相矛盾,上線晚一天寬限就少一天,屬可確定的判錯。
段落:依據段、範圍第 2 條、做法第 1 條、S5、實務隱患「舊表態一起到期」。
引句:「依據:Enzo 2026-10-06 裁定兩題(做法:兩種都給、至少選一;舊表態:從上線日起算 30 天)。」
引句:「在 2026-11-05(本案設計日 2026-10-06 + 30 天)當天以前照舊有效,之後失效。」
問題:`_DRIFT_ACK_LEGACY_UNTIL = "2026-11-05"` 是寫死的絕對日期,起算點是設計日,不是上線日。例:10-20 才上線,舊表態寬限只剩 16 天;若上線拖到 11-05 之後,所有舊表態在第一次 drift scan 就失效、寬限為 0。裁定的語意是「上線日 + 30」。
具體例:輸入=2026-10-20 上線的工具、rtb 的 11 筆無欄位 probe 照留;預期=寬限到 2026-11-19;實際=2026-11-06 起全部重列。
r1 的處置(卷證 r1-intake)只改了日期算法,沒回頭對裁定原文;修訂稿補進來的「本案設計日 + 30 天」就是這個新不一致。要嘛把常數改成「上線時寫進去的日期」(上線日 + 30),要嘛由 Enzo 明確改裁並刪掉依據段那句。

## F2 沒有起點的推送:天花板第 4 條對「今天的行為」的描述錯,已提交的裸照留會被整批擋掉
severity: major
blocking: 是——不該擋的被擋:早就提交進主線的照留,在起點是空樹的推送裡被當成新寫。
段落:天花板第 4 條、做法第 5、6 點、範圍第 3 條。
引句:「沒有起點的推送(全新 repo 的第一次推送)裡,所有已成立的條件都算新寫,照留都要綁去處」
問題:
1. 規格說這「跟今天全部都會被擋一致」。查碼不是:`_drift_check_c` 在 `_drift_split_acked` 把已表態的扣掉(`scripts/lumos:34372` 的 `keys` 分支與 `scripts/lumos:35741`),今天有照留的行在空樹起點照樣放行。所以改後是新增的收緊,不是「一致」。
2. 空樹起點很常見,不限全新 repo:`_push_no_mainline`(`scripts/lumos:41671` 起)在找不到主線且遠端舊值全 0 時回 `_EMPTY_TREE_SHA`,新分支首推走這條。`_drift_probe_prepare` 對這個起點(字串為真)建的是空的起點圖譜,`_drift_probe_old` 回 False(不是 None),所以每一行已成立的條件都是 `old` 不為真 → `born_now`。
具體例:消費專案(例如 rtb)沒有可辨識的主線、已有 11 筆提交進樹的裸 probe/retire 照留;新分支首推 → 起點空樹 → 11 行全標 `born_now` → 裸照留不認 → 整次推送被擋。預期=只擋這次新寫的;實際=擋掉歷史上已表態的行,唯一出口是逐筆補 `--tracked-in`,而 S7 還宣稱「只收緊新寫的」。
⚠ 「截到上線點」(`scripts/lumos:41671` 區塊的 docstring 與 `_DRIFT_GOLIVE_MARK`)會不會把空樹範圍的舊行裁掉,規格沒講、我沒實跑驗;若會裁掉,影響縮小,但規格要寫明並加測試。
處置方向:`born_now` 要在起點是空樹/無起點時不套(沿用今天的照留規則),或只在起點是真提交時套;天花板第 4 條改寫成實情並補 [S] 條款。

## F3 推送路徑沒復用 `_drift_ack_live` 的欄位驗證:壞掉的 `tracked_in` 在推送端沒有定義的行為
severity: minor
blocking: 否——要手改壞表態檔才觸發,但失敗方向是放行或崩潰,屬可補的空白。
段落:範圍第 4 條、做法第 3 點與第 5 點。
引句:「發現帶 `born_now` 時只認有 `tracked_in` 而且 `status_of` 判開著的照留」
引句:「綁驗證紀錄、Systems 節點、沒有狀態欄的筆記、或那一行所在的同一篇,表態時擋、判斷時當失效」
問題:
1. 「判斷時當失效」的「同一篇」規則,在做法第 3 點的 `_drift_ack_live` 條文裡沒有列(只列了字串、`..`、圖譜資料夾底下、`status_of` 結果),S3 也沒有測。
2. 第 5 點的推送路徑只說「有 `tracked_in` 且 `status_of` 判開著」,沒說先過第 3 點的型別驗證。表態檔是 jsonl、手改或合併會壞(碼裡已有同類防禦:`_drift_related_ok` 把壞 related 當沒涵蓋)。例:一筆 `{"kind":"retire","tracked_in":["x"], ...}` 進推送路徑 → 拿 list 去查路徑會丟例外;`_drift_retire_guarded` 的兜底把例外轉成「沒跑完,不擋」(`scripts/lumos:35653` 起)= 該擋的 `born_now` 撤除條件被放行。另一筆 `tracked_in` 等於自己那一行所在的檔、狀態是 doing → 推送路徑認作開著 → 放行,但表態時是被擋的。
3. `prev_ack={reason, dead}` 的 `dead` 原因文字只在 scan 路徑有來源(第 3 點的原因);推送路徑被擋時 `dead` 寫什麼規格沒給。另外 `_drift_prev_ack_line` 現在讀 `pa["related"]`(`scripts/lumos:34451`),新形狀沒有這個鍵,實作時 `dead` 分支必須排在前面,否則 KeyError。
處置方向:推送路徑與 scan 共用同一個欄位驗證函式(把「同一篇」也放進去),只是不比日期;補一條壞欄位進推送路徑的測試。

## F4 推送路徑補建圖譜物件的失敗與預算行為沒定義
severity: minor
blocking: 否——只影響邊角,但規格要寫死失敗方向。
段落:做法第 7 點。
引句:「要 `status_of` 時,retire 用手上的 tenv,核心路徑在」
問題:核心路徑的照留扣除發生在 `_drift_check_c`(`scripts/lumos:35741`),此時 `_drift_check_core` 內的 tenv 已出作用域,要再 `_drift_tree_env(root, tip, …)` 建一次;該函式 `deadline=None` 時預設等 60 秒(`scripts/lumos:32643`),而 `_drift_check_c` 外面沒有 try。建失敗回 None 時,規格第 5 點寫「`status_of` 沒傳就當沒有綁去處」,但沒說建失敗是同一種處理(擋)還是判不了。例:讀樹逾時 → 該擋成「綁去處不在」,訊息會誤導(其實是 git 讀不出)。
處置方向:寫明建失敗=判不了(算要處理,同既有核心路徑規矩)並給預算;或讓 `_drift_check_core` 把 tenv 一併回傳,免重建。

## F5 「born_now 與擋下條件完全一致」成立,但擋下條件本身有同形漏洞,規格沒承認
severity: minor
blocking: 否——是既有行為,不是本案新增,但本案宣稱「新寫就成立一律要綁去處」。
段落:做法第 6 點、天花板。
引句:「`_drift_probe_check` 的 must 裡 `old` 不為真(起點沒有同一條,或沒有起點)的發現加 `born_now: True`」
問題:`old` 是拿「條件標記元組」比對起點同一篇的集合(`_drift_probe_old`,`scripts/lumos:33780` 前後),不是比對行。新寫一行,條件元組跟同一篇起點已存在的另一行相同:`old` 為真;起點那條已成立就連發現都不列(`_drift_probe_judge` 的 `was` 為真回 "")。例:同一篇起點已有 `REVISIT:[when-file:src/a.py] 甲` 且 src/a.py 早已存在,這次新寫 `REVISIT:[when-file:src/a.py] 乙` → 不列、不擋,B2 要收的情況沒收到。r1 紀錄的例子(新寫 `[when-file:src/a.py]` 而檔已在)只在這一篇起點沒有同條件時才成立。
處置方向:天花板加一條,承認「跟起點同篇既有行同條件的新寫行不受 B2 管」。

## 逐節
- 前言(frontmatter、白話、依據、PRIOR-ART、RETIRE-IF):已讀;問題見 F1。其中 PRIOR-ART 對 `_drift_split_acked` 的 related/seq、REVISIT 的 `[by:]`、doctor 到期的描述與碼一致。
- 範圍:已讀;範圍第 2 條見 F1,第 3 條見 F2/F3,第 4 條 Issue/計劃的「開著」集合與碼對得上(`_DRIFT_OPEN_ISSUE=("open","doing")`、`_STATUS_ENUM["project"]={"todo","doing","done","superseded"}` 扣掉 `_DRIFT_CLOSED` 剩 todo、doing)。
- 做法 1 到 2:已讀,無 finding(`drift fix --keep` 呼叫 `cmd_drift_ack`:`scripts/lumos:35473` 確認存在、kind 固定 c2)。
- 做法 3 到 5:見 F3;日期比較(期限當天有效、`until` 不早於表態日、不晚於表態日 + 30)與 S3/S5 一致,表態紀錄確有 `date` 欄(`scripts/lumos:34531` 區塊的 `rec`)。
- 做法 6:見 F5;與 `_drift_probe_judge` 新寫分支一致(已核對)。
- 做法 7:見 F4;「考試與歷史重放不扣表態」不在我的鏡頭驗證,碼裡 `_drift_check_core` 的呼叫點只有 `_drift_check_c` 一處用到 split,與規格相符。
- 做法 8 到 9:已讀,無 finding。
- 實務隱患:已讀。日期取本機、舊表態一起到期(見 F1)、綁的節點改名、退回提交:四段與碼行為一致。
- 驗收條款:缺三個測試場景,見 F2(空樹起點)、F3(壞欄位進推送路徑、同一篇)。S6、S7 其餘已讀無 finding。
- 回退、天花板、REVISIT、審計修正紀錄:已讀;天花板第 4 條見 F2,其餘無 finding。

## 實務隱患類逐類
- 金流:無——只改筆記治理工具。
- 對外送出:無——不連網。
- 不可逆:無——表態檔只追加,失效只在判斷時算;但 F2 讓推送被擋後的唯一出口是逐筆補表態,屬流程成本。
- 並行/資源:F4(補建樹的逾時與失敗方向)。
- 守衛面(該擋放行/不該擋被擋):F2 不該擋的被擋;F3 的壞欄位走兜底會放行;F5 同形漏洞。
- 時間/日期:F1;本機日期只在 scan 用,已讀無其他 finding。

severity: major
blocking 2 條(F1、F2)。
