severity: major

固定席筆記:派工詞尾端沒有附固定席筆記,沒有逐條判。

查證範圍:我讀了程式碼,沒有跑 git 實驗。路徑都在 rw 副本裡(`scripts/lumos` 等)。已核對上一輪回滾席(r1-回滾)的 K1 到 K9。上線點、旗標的組合語意、`{retire}` 截斷、工具樣板豁免這幾條在 r2 已補上。K2 在 r2 只補了一半,見 R2K1。

**R2K1**
severity: major
blocking: 是 — 照 spec 實作,「記號不寫進 pre-commit 就不查」會變成相反的行為,14 天等待期反而是全面開查。
- 輸入:第 1 步程式已上主線,但格子記號還沒寫進 `scripts/hooks/pre-commit`(〈相容〉描述的 14 天等待期)。消費專案走一次推送,或 CI 跑一次 `note-shape --diff`。
- 走到〈相容〉那段,以及〈擋〉的「自己的上線點」。spec 假設沒有記號就等於還沒上線。
- 實際情況相反:`_nodehome_golive` 找不到記號時回 None。`scripts/lumos:25674` 於是把 `live_mark` 設成 None,`scripts/lumos:25590` 起的 `live = None`,`scripts/lumos:25616` 的 `dest = by_path if (live is None or sha in live)` 就把範圍內每個提交都當成已上線來查。`_nodehome_clamp_base` 在上線點為 None 時也原樣回傳 base,不截斷。
- 結果是 spec 的文字和既有機制相反:「沒有記號=整段歷史都套格子規則,包含上線前寫的舊行」。實作者若照既有機制直接複用,就會在 14 天等待期內全面擋人。
- S7 的測試只寫「提交發生在上線點之前」,沒涵蓋「歷史裡根本沒有記號」。
- 回退面:要「停格子」除了 `slots: off`,還得確保歷史裡留得住記號。
- 引句:「在那之前格子上線點記號不寫進 pre-commit,格子檢查不跑」
- 佐證:`scripts/lumos:25590`、`scripts/lumos:25616`、`scripts/lumos:25674`、`scripts/lumos:24933`

**R2K2**
severity: major
blocking: 是 — 第 2 步是推送時的硬擋,卻沒有獨立的細分開關。回退段和〈不可逆〉都假設有,實作者會照這個假設少做一個開關。
- 輸入:第 2 步上線後,`[retire:when-*]` 的抽取或轉變判定誤報,卡住推送。
- 走到〈回退〉的「第 2 步上線期間可用 `drift_check.gate` 或單次跳過先停」,以及〈實務隱患〉最後的「擋都能用子開關降級」。
- `drift_check.gate=off` 會連 c1 到 c5 與既有的回頭條件探針一起關掉(`scripts/lumos:30405` 的訊息寫明「c1–c5 與回頭條件關掉了」)。這是用已運作數月的護欄去換新功能的誤報。
- 單次跳過 `LUMOS_SKIP_DRIFT_CHECK=1` 只管這一次推送,CI 照查(`scripts/lumos:30379`)。
- 第 1 步有 `note_shape.slots`,既有的舊句檢查也有專屬子開關 `drift_check.old_sentence`(`scripts/lumos:30317`)。第 2 步沒有對應的子開關。
- 唯一的細分手段是逐條 `drift ack`,誤報成批時救不了。
- 引句:「第 2 步上線期間可用 `drift_check.gate` 或單次跳過先停。」
- 佐證:`scripts/lumos:30405`、`scripts/lumos:30379`、`scripts/lumos:30317`、`scripts/lumos:28146`

**R2K3**
severity: major
blocking: 是 — 撤掉 SEE 的回退步驟沒有清單工具,對消費專案的筆記也動不到。照做會留下一批被漏算的計劃連結,風險分級會默默變低。
- 輸入:SEE 上線後,多個消費專案的筆記已寫了 `SEE:` 行,之後決定回退第 0 步。
- 走到〈回退〉第 0 步。回退段只說「要撤 SEE 前先把 SEE 行改回 DEP」。
- 落地三個缺口:
  - 沒有指令能列出所有 SEE 行。
  - SEE 行在別的專案的筆記庫裡,toolchain 的還原提交碰不到。
  - 程式是 symlink 立即全域生效,每個專案的改回動作卻要各自的人去做。
- 時間差內,現行 `_plan_system_links` 只認 `DEP:`(`scripts/lumos:6217`),SEE 連結默默消失。相依回歸、門判定訊號 2、推送前「落點被碰到」三處都走這支函式。
- 同時 `SYMBOL_NAMES` 少了 SEE,lint 把這些行唸成非標準符號(`scripts/lumos:3261`、`scripts/lumos:4932`)。
- spec 的〈回退〉承認了這件事,但沒有給可執行的步驟。更便宜的退法 spec 沒提:撤第 0 步時,只撤範本和骨架提示,SEE 留在 `SYMBOL_NAMES` 與 `_plan_system_links`,當一個惰性前綴。
- 引句:「SEE 前綴撤掉後,已寫的 SEE 行會被 lint 唸成非標準符號(承認),算計劃連結的程式回到只讀 DEP」
- 佐證:`scripts/lumos:6206`、`scripts/lumos:3261`、`scripts/lumos:4932`

**R2K4**
severity: major
blocking: 是 — 決定「要不要退場」的兩個數字,現有治理帳算不出來,RETIRE-IF 和 REVISIT 會憑感覺判。
- 輸入:上線 8 週後,依 RETIRE-IF 第二條統計「擋下事件之後,同一提交用單次跳過推上去的比例」。
- 走到 RETIRE-IF 與〈擋〉的治理帳條。
- spec 只在擋下事件的說明欄補了「格子違規條數與各鍵缺漏次數」。
- 跳過那一筆在 `scripts/lumos:26370` 到 `26371` 寫帳,發生在評估之前,內容只有 `LUMOS_SKIP_NOTE_SHAPE`。它不知道這次提交有沒有格子違規,所以分子沒有格子資訊。
- 擋下事件的 `_note_shape_report` 寫帳(`scripts/lumos:26493`)沒有提交編號。提交前模式記的是 HEAD,也就是上一個提交,所以「同一提交」要靠上一個提交編號與時間去猜。
- 第一條「抽查 20 筆被擋下又補好的行」,帳裡沒有行文字,只能重建 git 歷史。這點 spec 可接受,但沒寫。
- 引句:「或治理帳裡帶格子違規的擋下事件,之後同一提交用單次跳過推上去的超過三成」
- 佐證:`scripts/lumos:26370`、`scripts/lumos:26493`、`scripts/lumos:1234`

**R2K5**
severity: major
blocking: 是 — 這個度量的文法沒有指明數哪一道閘或哪一種事件,實作者只能自己猜,S13 的測試也沒有基準。
- 輸入:RULE 寫 `[retire:度量 觸發次數 > 3 近4週]`。
- 走到〈格子規格〉的度量條,以及〈格子欄位的過期檢查〉表的 doctor 度量列。
- 度量文法只有「觸發次數|跳過次數」兩個詞和比較、數字、週數,沒有指明閘名(note-shape、drift-check、bound-tests 等)和事件種類(blocked、warned、skipped-env)。
- 程式碼裡找不到「觸發次數」「跳過次數」這兩個詞(`scripts/lumos` 搜不到),治理帳也沒有按規則種類分的指標。
- RETIRE-IF 兩個條件用的也是這個詞。
- 引句:「度量:`[retire:度量 觸發次數|跳過次數 <比較> <數字> 近<N>週]`,指標只收這兩個(白名單,其他指標算寫錯)。」
- 佐證:`scripts/lumos:1234`、`scripts/lumos:26493`

**各節已讀**
- 〈格子規格〉:R2K5。
- 〈擋〉:R2K1、R2K4。
- 〈lint 與擋同一張表〉:已讀,無 finding。屬回滾面的部分,即停用第 1 步後 lint 回到舊判準,與〈回退〉一致,`[防回歸:無 理由]` 被舊 lint 唸缺防回歸只會多一條警告。
- 〈格子欄位的過期檢查〉:R2K2、R2K5。取代鏈指到被刪節點的情況已排除。回退第 3 步只是還原提交,doctor 的提醒沒有持久狀態。
- 〈分期〉:已讀,無 finding。
- 〈天花板〉〈不做〉〈合約候選〉:已讀,無 finding。
- 〈實務隱患〉:R2K1(相容)、R2K2(自我治理)。
- 〈驗收條款〉:S7 的測試條件漏了「歷史裡沒有記號」這種情況(R2K1)。
- 〈回退〉:R2K2、R2K3。

**回滾視角補充(已核對、無 finding)**
- 回退第 2 步後,新種類的 `drift ack` 紀錄:載入時被 `scripts/lumos:29343` 的 `d.get("kind") in _DRIFT_KINDS` 靜默濾掉,留在檔裡無害,重新上線時又會生效。
- 第 1 步還原後,歷史裡的新文法 `[取代:[[節點]]]` 之類的行:舊的欄位解析只對 RULE 行生效,其他前綴不認它,只是文字。
- 範本還原後,消費專案的 CLAUDE.md 區塊與範本不一致,doctor 提醒到 `lumos update` 為止,這是既有行為,spec 已寫。

最高嚴重度:major,blocking 5 條
