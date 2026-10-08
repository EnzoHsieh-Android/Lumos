# 守檔筆記對照改動_計劃 r1 折入核對

現稿 = negguard/.../Projects/守檔筆記對照改動_計劃.md。行號指現稿行號。判定:已處理 / 部分 / 沒處理。

## 一、44 條 finding 對照

| 席 | F | 判定 | 現稿依據或缺口 |
|---|---|---|---|
| 正確性 | F1 列了的測試檔兩頭不收 | 已處理 | L50「★不經 `_nodehome_required` 過濾★:測試檔、about_code 明寫的任何檔都算」;L59 diff 放「about_code 列了…含測試檔、含刪掉的」;S1、S2 |
| 正確性 | F2 同一層目錄不等於 rtb 版面 | 已處理 | L60「或它在 `tests/<X>/…` 而那支檔在 `src/<專案>/<X>/…`」;S10 改用 reread-prepare 重跑(L117) |
| 正確性 | F3 刪檔、移出 about_code 不觸發 | 已處理 | L51「頂端…以及起點那邊列它的家(刪檔、從 about_code 移出時只剩起點那邊有)都算」;S1 |
| 正確性 | F4 指紋含範圍 diff | 已處理 | L57 指紋不含範圍;L49「兩邊起點可能不同,但項目指紋不含範圍」;L81 check 印原樣參數;S6 |
| 正確性 | F5 resolve 自己寫 skipped、記兩筆 | 部分 | L49 改傳自己的閘名 `note-reread`,不再污染 `note-audit`(S7 釘)。但 resolve 內部仍會在 `note-reread` 閘記 `skipped`/`skipped-env`,L83/L85 又記一筆 `skipped`,同一次跳過雙記,沒寫誰吞掉一筆 |
| 正確性 | F6 共用函式吞掉 strict 語意 | 已處理 | L52「只回路徑清單…git 失敗或逾時回 None,不做任何『頂端讀不到』的過濾」;S12 |
| 正確性 | F7 掛鉤回傳值不看 | 已處理 | L86「回傳碼交給 `pp_stop_if_signaled`…其他非零一律放行」;S9 |
| 正確性 | F8 NFD pathspec | 已處理 | L43「要拿去問 git 的路徑…一律用 git 原樣路徑(`norm=False`)」 |
| 正確性 | F9 record 取全文、bool、切行法 | 已處理 | L73 從項目檔頭 blob 讀;L71「布林不算、字串不算」;L44 `split("\n")`;S5 |
| 正確性 | F10 trunc、others 填入字串 | 已處理 | L62 逐項寫出 TRUNC、OTHERS、DIFF「(無)」等;S3 |
| 正確性 | F11 S6 漏推送參數只給一個 | 已處理 | L83 列「推送參數只給一個」與「任何沒預料到的例外」;S7 |
| 正確性 | F12 指紋受 diff 設定影響 | 已處理 | L57 指紋只用 ls-tree、「不受作者本機 diff 設定影響」;L58 diff 固定參數 |
| 邊界 | F1 刪檔家不成候選 | 已處理 | 同正確性 F3(L51、S1) |
| 邊界 | F2 起點不同指紋對不上 | 已處理 | 同正確性 F4 |
| 邊界 | F3 共用函式 strict 語意、路徑形狀 | 已處理 | L52(只回路徑、None 傳遞)、L42(補圖譜資料夾前綴、NFC)、S12 |
| 邊界 | F4 非 UTF-8 與未預期例外 | 已處理 | L44 `errors="replace"`;L83「任何沒預料到的例外(最外層接住)」;L72 報告非 UTF-8 rc2 |
| 邊界 | F5 行切法 | 已處理 | L44 切法、CRLF、檔尾空字串;L65 檔頭記筆記行數;L73 全文從 blob 讀 |
| 邊界 | F6 json 區塊抽法與逐項驗證 | 已處理 | L70「整行就是 ```json 的行」到「整行就是 ``` 的行」、頂層非清單拒收;L71 逐項規則、重複行留第一次;S5 |
| 邊界 | F7 多圖譜只看一個 | 已處理 | L45、L150 誠實界線 |
| 邊界 | F8 NFC pathspec | 已處理 | 同正確性 F8(L43) |
| 邊界 | F9 檔頭與本文分隔 | 已處理 | L65「用既有清單檔的 `\n---本文---\n` 切開,record 只讀檔頭」 |
| 邊界 | F10 提早結束情形分不出、原因、「擋下」措辭 | 部分 | L83 先自驗範圍格式與終點以避開「擋下」。缺:淺層 clone、沒有圖譜、刪除分支、清單讀失敗時 `_note_audit_resolve` 只回 `(None,0,None)`,沒寫怎麼拿到原因;resolve 內部 `skipped` 雙記同正確性 F5 |
| 邊界 | F11 diff 過大、git 失敗 | 已處理 | L61「組 diff 的 git 失敗或逾時:那一篇不產項目檔,印原因」;L82 整體 30 秒 |
| 架構 | F1 兩種起點判法 | 已處理 | 同正確性 F4(L49、L57、L81) |
| 架構 | F2 掛鉤吞 Ctrl-C、無標記行 | 已處理 | L86 標記註解行 `# lumos note-audit reread-check` 加 `pp_stop_if_signaled` |
| 架構 | F3 閘名沿用 note-audit | 已處理 | 閘名改 `note-reread`(L49、L76、L85),事件不加前綴;S7 釘不寫 `note-audit` |
| 架構 | F4 路徑形狀、前置 | 已處理 | L42、L51「前置照 `_nodehome_evaluate` 那一串」 |
| 架構 | F5 沒有 config 開關 | 已處理 | L84 `note_reread.mode` warn/off;L89;S13 |
| 架構 | F6 範本載入與模型另寫一套 | 已處理 | L63 抽共用、佔位字全大寫、版本整數;L64 `_note_audit_judge_model` 加參數;S3「筆記內容審派工詞逐字不變」 |
| 接手 | F1 skill 小節沒落點 | 已處理 | L101 寫明檔案與小節名與流程順序;L35;S14。(lands_in 沒跟上,見鏡像 2) |
| 接手 | F2 帳上事件缺欄位 | 已處理 | L76、L85 `reminded` 帶路徑與指紋、`none`、`covered`、`skipped`、來源;L96 用這些量 |
| 接手 | F3 S10 不自足 | 已處理 | S10 改用 reread-prepare、selection.json、rtb `git clone --shared`、12–13 行重跑取平均、花費記帳;L104 提交順序 |
| 接手 | F4 8 週 REVISIT、成本條件 | 已處理 | L31 新增 2026-12-02 REVISIT;L29 成本改用項目檔字元數代理。(代理值本身有鏡像 1 問題) |
| 接手 | F5 掛鉤吞 Ctrl-C | 已處理 | 同正確性 F7 |
| 接手 | F6 提醒後的出口 | 已處理 | L81 末句「這只是提醒、不擋,忽略照推也可以」;L77 |
| 接手 | F7 上線公告與模型別名 | 部分 | L103 CHANGELOG 加跨會談訊息請 rtb `lumos update`;L64 判定者 model 由報告寫入紀錄。缺:項目指紋與 S4 都不含判定者模型,「換模型要重跑」(L63)仍只是文字,沒有機械偵測 |
| 併發 | F1 check 沒時間預算 | 已處理 | L82 30 秒、每次 git 前看截止;L86 不組 diff;L132 逐 ref 各自 30 秒;S7 |
| 併發 | F2 掛鉤吞 Ctrl-C | 已處理 | 同正確性 F7;L87 CI 吞 OOM 標明刻意 |
| 併發 | F3 同指紋蓋檔頭 | 已處理 | L65 項目檔名帶編排者;L134 |
| 回滾 | F1 指紋含 diff | 已處理 | 同正確性 F4;L49 傳自己的上線點標記字串 |
| 回滾 | F2 共用函式 strict | 已處理 | 同正確性 F6;L52 保留走模組全域 `_ns_git`;S12 |
| 回滾 | F3 掛鉤慣例、版本偏斜、時間預算 | 已處理 | L86;L136 版本偏斜(stderr 丟掉、rc2 放行);L82 |
| 回滾 | F4 回退後紀錄檔與豁免 | 部分 | L126 改成同一個 revert 提交 `git rm -r governance/reread-verdicts`,並給 `code-loop pass --note` 重記。缺:沒 `lumos update` 的協作者(舊 lumos 沒這項豁免)在自己分支遇到紀錄檔提交會被擋,L136 版本偏斜只談掛鉤、沒談豁免;RETIRE-IF 的撤除(L29)也沒提刪紀錄資料夾 |
| 回滾 | F5 候選交集 NFC | 已處理 | L42、L52「reread 拿到清單後自己轉 NFC」;S1「NFD 路徑的筆記照樣認得」 |

統計:44 條裡 沒處理 0、部分 4(正確性 F5、邊界 F10、接手 F7、回滾 F4)、已處理 40。

## 二、鏡像不一致

1. **RETIRE-IF 的成本條件在截斷上限下永遠不會成立**
   - L29「項目檔字元數的中位數超過 40 萬字元(約 1 美元列價…)」
   - L61「上下文照 3 行、1 行、0 行依序試,哪一種不超過 10 萬字元就用哪一種;0 行仍超過…各檔 diff…分配剩下的字數」;L131「每篇約 4 萬 token、列價約 0.17 美元」
   - diff 上限 10 萬字元加一篇筆記全文,項目檔遠不到 40 萬;這條撤除條件是死條款。數字也跟 L131 的單價不成比例。
2. **lands_in 沒跟上〈做法〉6 要改的家**
   - L10-11 `lands_in: - Systems/筆記內容審`
   - L102「推送前掛鉤與 CI 設定檔的家([[Systems/存量漂移守衛]] 管著呼叫漂移檢查那一段)補一句…;程式的說明寫進 [[Systems/筆記內容審]]」
   - 鐵則 5 要求計劃寫 lands_in 落在哪幾篇;存量漂移守衛沒列。
3. **回 0 情況清單與訊息字串在三處不一致**
   - L83 清單含「沒有圖譜」;S7「範圍格式錯、終點找不到、推送參數只給一個、起點算不出、淺層 clone、git 失敗、超過 30 秒、丟出沒預料的例外」沒有「沒有圖譜」,測試不會釘到。
   - 訊息字串:L82「這次沒提醒完:逾時」、L83「這次沒提醒:<原因>」、S7「這次沒提醒」加原因,三種寫法。
4. **`none` 事件歸屬混淆**
   - L53(第 1 節,prepare 與 check 共用)「候選是空的:印『這次沒有要對照的家筆記』、rc0、不產生檔,記 `none` 事件」
   - L85「(閘 `note-reread`):…沒候選記 `none`」屬 reread-check;L96 拿 `none` 當「有候選的推送占比」分母;S1 只寫 prepare 印訊息 rc0、沒說記帳。
   - 若 prepare 也記 `none`,分母被手動 prepare 灌水;需擇一寫死。
5. **同一次跳過在 `note-reread` 閘內雙記**
   - L49「傳自己的閘名 `note-reread`」交給 `_note_audit_resolve`(它內部會記 `skipped`、`skipped-env`)
   - L83「一律印『這次沒提醒:<原因>』、記 `skipped`(帶原因)」;S7 只釘「不寫任何事件到閘 `note-audit`」
   - 起點算不出、淺層 clone 兩種會記兩筆同名 `skipped`,L96 的次數會偏高。
6. **RETIRE-IF 的撤除範圍與〈回退〉不同**
   - L29「就把三個 reread 子指令與推送前、CI 那兩處呼叫整個撤掉」
   - L125「三個子指令留著不影響別的閘」;L126「整案回退…★同一個 revert 提交裡 `git rm -r governance/reread-verdicts`★——不然豁免項撤掉之後…會讓高風險推送被擋」
   - 照 RETIRE-IF 撤(子指令與呼叫)卻沒提刪紀錄資料夾與簿記豁免、範本登記,可能踩 L126 講的那個坑。
7. **紀錄檔認法:check 沒套自己的檔名正規式**
   - L74「自己的檔名正規式(`_write_lf` 中斷留下的 `.tmp-wlf` 不合、不算)」
   - L81「看…`governance/reread-verdicts/` 有沒有檔名以這個指紋開頭的紀錄」
   - `.tmp-wlf` 殘檔也以指紋開頭,照 L81 字面會被當成已對照;S6 沒有這個案例。
8. **「不組 diff、只列目錄與 ls-tree」低估 check 的工作量**
   - L132「reread-check 不組 diff、只列目錄與 `ls-tree`,並有 30 秒上限」;L183「改後只 ls-tree」
   - L47-52 候選要算 `_nodehome_changes`(帶改名偵測)、兩邊 `_nodehome_homes`、`git log --name-only -M`;這才是 30 秒要罩的成本。
9. **指紋組成與 diff 內容範圍不對等**
   - L57 指紋只含「那篇 about_code 列的每支檔在頂端的路徑+blob 編號」
   - L59-60 diff 還含「起點那邊 about_code 列了」的檔(已從 about_code 移出)與補進來的測試檔
   - 補測試檔或被移出的檔內容變了,指紋不變,已對照的紀錄仍算數。可能是刻意,但現稿沒說。

殘留舊字眼掃描:`home-`(只剩實驗資料夾路徑 `governance/eval/home-check/`,是真路徑,非舊名)、`diff 全文雜湊`(無)、「縮成 0 行」與「回傳值不看」(只剩〈審計修正紀錄〉裡引原稿的歷史句)、`reread-reminded/skipped/recorded/reread-v1`(無)、「about_code 列了其中任一」(無)、`_lens_push_base`(L49 只當「不帶推送參數時」的後備,且明寫指紋不依賴範圍,不算唯一判法)。都沒有殘留。
閘名 `note-reread`、子指令三名、資料夾 `governance/reread-verdicts/`、佔位字六個、範本檔名、REVISIT 兩個日期(10-21 加 42 天=12-02,對得上兩週與八週)、五個簿記消費者、審計紀錄的 44/14 與「四席、五席」計數,彼此一致。
