severity: major

審查範圍:我讀了 r2-delta.patch 和 r2-snapshot.md 全文,也核對了 `scripts/lumos` 與 `scripts/templates/android-e2e-run.sh`。spec 引用的 `_door_keyword_hits`、`E2E_PATH_LIST_MAX`、`_e2e_norm`、`_out_clean`、`_e2e_record_err`、`_e2e_load_json`、`PITFALL_CLASSES` 都存在。
決策 d1(不溯及既往)與 d2(單向門要人點頭)我沒有要求砍掉任何一條;下面各條拿掉後,這兩條仍然成立。

1. 建議拿掉「label 前綴指到新情境卻沒有這個 id,或指到不存在的情境就擋」這一條,連同 S7 的後半。
   拿掉不會壞的理由有兩個。
   - 這條的存在理由是「打錯字會讓句子看似有人管」,這個推論不成立。label 打錯,正確的 label 就不在 `checks.labels` 聯集裡。那一句會被另一條「A<n> 沒有檢查對到」擋下,不需要這條。
   - 打錯成另一個已存在的 id 時,這條也擋不到,因為那個 id 存在。
   這條會多擋的只有無害情形,例如共用流程裡殘留已改名或已刪情境的 label,或多寫了一個沒用的 label。「指到不存在的情境」的 label 會把新情境的推送擋死,而那個 label 對新情境的覆蓋毫無影響。這是明顯的誤擋,所以 major。
   引句:「label 的前綴指到一個新情境、但那個情境沒有這個 id,或指到根本不存在的情境 →列出那個 label(打錯字會讓句子看似有人管)。前綴指到舊情境的 label 不管(共用流程裡別的情境的 label 不算多餘)。」
severity: major
   blocking: 是(多餘的機制會造成明顯誤擋)

2. 建議拿掉新欄位 `evidence.debug` 和範本腳本多寫的那一行,judge 直接用既有的 `evidence.dir` 加上固定字串 `debug`。
   spec 的理由是「不加的話 judge 要從 flow 的 YAML 猜 `name:`」,這個前提已經被它自己的新設計推翻。
   - 新設計只讀 debug 目錄底下唯一的子目錄,不讀 YAML,也不猜 `name:`。
   - 路徑本身已能推出來:範本腳本的 `ev` 就是 `evidence.dir`,debug 目錄固定是 `os.path.join(ev, "debug")`。
   - `EVIDENCE` 為假時,`evidence.dir` 是 None,judge 本來就會記 `checks: null`。
   所以這個欄位只是複製一份可推得出的值,還多一個需要 `_e2e_record_err` 驗型別、並寫進回退清單的點。
   file: `scripts/templates/android-e2e-run.sh:493-501`,`ev` 是這次嘗試的目錄,debug 目錄是 `os.path.join(ev, "debug")`,`evidence` 已寫入 `dir`。
   引句:「範本腳本每次嘗試已經有獨立的 debug 目錄(`<run>/ui/<名>.try<N>/debug`),改成把這個路徑寫進 steps.json 那次嘗試的 `evidence.debug`」
severity: minor
   blocking: 否(只是多花工)

3. 建議把 7 個「各自一個擋下代碼」併成 3 個:無檢查、驗收句覆蓋、單向門。
   - 無檢查:count 為 0、`checks` 為 null、紀錄沒有 `checks` 欄。
   - 驗收句覆蓋:缺 `accept`、缺某一句的檢查。
   - 單向門:缺 `one_way`、`accept_review.by` 不是 human。
   併掉的理由是 spec 自己只用 `gate_code` 來數 RETIRE-IF,而 RETIRE-IF 只關心「驗收句沒對到」這一類。同一類內的細分原因已經印在訊息文字裡,不需要再各佔一個代碼。同類代碼還要各配 S12 的下一步處理,會讓 `gate_code` 與 S5、S6、S7 的測試成倍增加。
   引句:「這幾條各自一個擋下代碼,寫進治理帳的 `gate_code`(撤除條件要數);下一步印「改設定或流程再跑整套」」
severity: minor
   blocking: 否(多花工,不會誤擋)

4. 建議拿掉 `accept_review.at`(日期)的格式驗證與必填。
   - gate 只讀 `by` 是否以 `human:` 開頭,沒有任何一條規則讀 `at`。
   - 日期有 git 提交時間可查,簽名內容的新舊由指紋保證:e2e 段一改,舊紀錄就失效。
   留著 `at` 的唯一後果是 S13 多一種格式錯誤要擋,作者多一個會寫錯而被擋的欄位。同理 `state` 欄位判定不讀,只供代理對照,維持選填即可,不要再為它寫格式規則。
   引句:「`accept_review`:`{"by": "agent:<模型>" 或 "human:<名字>", "at": "YYYY-MM-DD"}`。跟放行紀錄的 `by` 只記 human/ai 不同:這裡要記「誰」」
severity: minor
   blocking: 否(只是多花工)

5. ⚠ 建議 `one_way` 不要「新情境必填」,改回選填;缺欄位就只靠機械地板和代理審。
   - 必填的 `[]` 擋不到任何事。spec 自己承認作者寫 `[]` 又避開表上的字,機械上擋不到。
   - 它讓「只列截圖、效能或記憶體、沒有 flows」的新情境也要被迫宣告,多出一個純形式的擋下條件。
   - 地板加選填的 `one_way`,功能已經等同 d2 原決策:「作者可加 one_way 往嚴標、不能往鬆標」。
   我標 ⚠ 的原因:spec 的理由是強制作者與審驗收句的代理看一眼。這個效果我沒辦法用現有證據證明有或沒有,只能指出它的機械擋力為零。
   引句:「新情境沒寫 `one_way` →「新情境要宣告碰哪幾類單向門(一類都不碰寫 [])」。」
severity: minor
   blocking: 否(多花工)

6. 建議在第 7 條「檢查數變少只提醒」裡,拿掉重新算指紋再去被推送提交的樹找分岔點紀錄的整段機制,改成「不實作,等有證據再加」。
   - spec 自己寫明這行「會常出現」,因為分岔點那一版的紀錄常常沒進這棵樹,所以多數時候只印「沒有可比的紀錄」。
   - 就算比得到,`count` 是執行次數,repeat 次數改了數字就變,提醒本身不可信。
   - 拿掉後,要記的只剩 `labels` 和「是不是零」,`count` 這個欄位也可以降成 `has_check` 布林,jsonschema 和 `_e2e_record_err` 的驗證跟著簡化,不用再為 repeat 計算寫「巢狀走完」的語意。
   反方向:Q5 的來源是 Enzo 對「少了要點名先只提醒」說「可以」。所以這條有人授權,砍它要先問 Enzo。我標 ⚠,不直接判定要砍,但建議向他報告「這條在實作上會常常只印一行無用文字」。
   引句:「分岔點那一版的紀錄常常沒進這棵樹,這行會常出現,只是提醒。」
severity: minor
   blocking: 否(只是多花工)

最嚴重 severity: major,blocking 共 1 條。
