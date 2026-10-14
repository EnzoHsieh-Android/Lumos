---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/guards-gates
  - risk/守衛面
lands_in:
  - Systems/筆記內容審
---
# 回頭重讀指紋不因主線前進失效_計劃

> 白話:推送前的「回頭重讀」會記住「這篇筆記對照過這一版程式」。現在它認的是程式檔在分支頂端的整份內容,所以只要主線有人改了同一支檔、你 rebase 上去,你自己的改動一個字沒變,所有對照過的筆記也全部要重讀一遍。改成認「你這條分支對那支檔做的改動本身」:主線前進、rebase 之後,只要你的改動沒變,對照紀錄照樣算數。

## 緣起

- 2026-10-13 一條分支因主線連續前進兩次而 rebase 兩次,回頭重讀也跟著重派兩次;自己的改動沒變,判定者讀的是同一段改動。`scripts/lumos` 被大約 49 篇筆記的 about_code 管著,主線上任何人改到它,所有管它的筆記在每條進行中的分支上都會失效。出處:使用者 2026-10-14 問「這次示範有什麼 lumos 可以改進」時列的第 3 條。
- 詞彙:**候選**=這次推送要對照的家筆記(改到的檔的家 ∩ 這次被改過的筆記);**主線候選**=算分岔點用的主線分支(遠端 HEAD、main/master 的上游等);**頂端**=被推送(或被 prepare)的那個提交;**對照紀錄**=`governance/reread-verdicts/` 裡以對照指紋開頭的判定紀錄。
- 原設計 [[Projects/守檔筆記對照改動_計劃]] 的對照指紋是雜湊(筆記路徑、那篇頂端 about_code 每支檔的頂端 blob、範本版本),刻意不含範圍與 diff。理由寫在它的〈做法〉第 1、2 節:「手動 prepare 與推送前 check 的起點算法可能不同,含 diff 的指紋對不上、提醒永遠消不掉」(設計審 r1 四席)。本計劃要推翻「不含 diff」這一半,所以必須正面回應那條理由(見〈做法〉2)。

PRIOR-ART: git 自己的 `git patch-id --stable` 就是為了「rebase 之後認出同一個改動」而設計(`git cherry`、`git rebase` 判斷哪些提交已經在上游都靠它):把 diff 去掉行號後雜湊。借它「去掉行號、`index` 行」的想法,但不借它「忽略所有空白」那一半——本 repo 以 Python 為主,縮排就是語意,忽略空白會把縮排不同的改動當成同一個(前掃實測:把 `return y` 搬進迴圈與只縮成兩格,patch-id 相同);正規化在 Python 裡做,不另跑 `git patch-id`。主線分岔點借本 repo 既有的手動代碼審預設起點算法(主線候選與推送閘共用),不另寫一份。
RETIRE-IF: 上線 8 週內,「主線前進後同一篇筆記被要求重讀、而作者那支檔的改動前後相同」的次數仍大於 0(代表新指紋沒解決問題),或新指紋造成至少一次「該重讀卻被當成已對照」——撤回成頂端 blob 指紋。
REVISIT:2026-12-15 照 RETIRE-IF 數一次:治理帳 `note-reread` 事件裡同一篇筆記、同一個分支被重列的次數,以及有沒有回報漏判。

## 做法

1. **對照指紋改用「這條分支對每支檔的改動」**:雜湊(筆記路徑、範本版本、指紋算法版本 `v2`、那篇 about_code 每一項配上「它在分岔點..頂端的改動指紋」)。
   - 每支檔的改動指紋:跑一次 `git diff <分岔點> <頂端> -- <那幾支檔>`,選項沿用現有給判定者組 diff 的那組(`_NOTE_REREAD_DIFF_ARGS`,已釘 `--src-prefix=a/ --dst-prefix=b/` 等),再加 `--literal-pathspecs --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3`——前掃實測 `diff.noprefix`、`diff.interHunkContext` 兩個本機設定在沒釘前綴、沒釘區塊合併時會改變結果,`--literal-pathspecs` 防檔名含 `[`、`*` 時把別支檔混進來。切成逐檔,每檔去掉 `index` 行、把 `@@ -a,b +c,d @@` 的數字換成固定字樣,其餘每一行(含空白、含上下文行、含檔頭的路徑)原樣雜湊。
   - 這條分支沒改那支檔:記成「未改」——主線怎麼改它都不影響指紋。理由:回頭重讀問的是「你的改動有沒有讓這篇筆記的舊句過期」,主線的改動由合進主線那次推送自己的回頭重讀負責。
   - 一批算完:同一次 check 或 prepare 裡,所有候選的 about_code 聯集只跑一次 `git diff`,逐檔結果快取起來給每篇用。
2. **分岔點只有一種算法,跟推送參數無關**(回應舊否決理由):把手動代碼審的預設起點那支函式 `_codeloop_default_base`(主線候選照推送閘的 `_push_mainlines`,外加本機 main/master,遠端取這條分支登記的上游、沒有用 origin、再沒有而只有一個遠端用它;多個共同祖先取歷史最長的)改成吃頂端:簽名 `(repo_root, tip)`;「這條分支」改成「指向頂端的本機分支」(`git for-each-ref --points-at <頂端> refs/heads`,恰好一條就用它的上游遠端,零條或多條退回目前簽出的分支),`merge-base --all` 也改對頂端算。現有唯一的呼叫點(代碼審判定在沒給範圍時)傳 HEAD,行為不變;引用它的測試一起檢查。
   - 它只看本機 refs 與頂端,不吃 `--diff`、`--push-remote`、`--pushed-ref`,所以手動 prepare 與推送前 check 在同一份 refs 狀態、同一個頂端下算出的分岔點必然相同。舊理由說的「起點算法可能不同」是指範圍起點:兩個子指令都經 `_note_audit_start` 取起點,不帶推送參數走 `_lens_push_base`(給定的起點在本機找得到就原樣用),帶推送參數走 `_push_range_start`;那個起點照舊只決定「誰是候選」,不進指紋。
   - CI:CI 的 reread-check 不擋、只印(見 [[Systems/筆記內容審]] 的 WHY 行)。CI 沒有本機 main/master、也可能是淺層 clone,算出的分岔點可能不同或算不出而退回 `v1`;結果只會多列、不會漏判,不另處理。
   - 主線前進、rebase 之後頂端變了,分岔點也跟著變成新的主線位置;作者的改動沒變,逐檔改動指紋就相同。rebase 時解衝突改到了作者那段,或主線改動落在作者那段的前後三行內(上下文變了),指紋會變——這兩種本來就該重讀。
3. **算不出就退回舊指紋**:分岔點算不出(沒有主線候選、沒有共同祖先、git 失敗)、組 diff 那次 git 逾時(`_lens_git` 預設 20 秒)、或分岔點就是頂端本身(推的是主線、或頂端已在主線上),整篇改用現在的頂端 blob 指紋——雜湊輸入一字不改、不加版本字樣(稱為 `v1`),所以退回時升級前記的紀錄照舊算數。退回只會讓已對照的被多列,不會漏判。推主線時本來就沒有「分支自己的改動」可比,維持現行行為。
4. **新舊紀錄不混**:新指紋的雜湊輸入多一行 `指紋算法 v2`,跟 `v1` 不會撞。升級之後,進行中的分支上已經用舊指紋記的對照紀錄不再算數,要重新 prepare 一次;新紀錄點出的規則類條目要重新表態(第二層的表態以判定紀錄的指紋為鍵;第二層本身按筆記路徑讀紀錄、不看對照指紋,不受影響)。一次性成本,只影響還沒推的分支。紀錄檔格式、檔名正規式(只要求 16 個十六進位字)、材料指紋的算法都不變;`reread-record` 不重算對照指紋,來源核對不受影響。
5. **呼叫點**:`_note_reread_fps` 與 prepare 單篇那個呼叫都改走新函式;兩邊共用同一份逐檔快取。`_note_reread_scan` 多帶一個分岔點欄位。

## 驗收條款

- [S1] 當分支改了 `a.py`、對照紀錄已記,接著主線也改了 `a.py`(不在作者改動的前後三行內)、作者 rebase 到新主線時,reread-check 應認得那篇已對照、不再列出。[test: t_reread_fp_survives_mainline_advance]
- [S2] 當 rebase 時解衝突改到了作者對 `a.py` 的那一段時,reread-check 應重新列出那篇。[test: t_reread_fp_changes_with_own_patch]
- [S3] 同一個 repo、同一個頂端,手動 `reread-prepare --diff <任一起點>..<頂端>` 與推送前 `reread-check --push-remote … --pushed-ref …` 算出的對照指紋應相同(起點不同也一樣)。[test: t_reread_fp_same_for_prepare_and_check]
- [S4] 推主線(頂端在主線上)或算不出分岔點時,指紋應等於現行的頂端 blob 指紋算法(版本 `v1`)。[test: t_reread_fp_falls_back_to_blob]
- [S5] 作者本機設了 `diff.algorithm=patience`、`diff.noprefix=true`、`diff.interHunkContext=10`、`diff.mnemonicPrefix=true`、外部 diff 工具時,指紋應與沒設時相同。[test: t_reread_fp_ignores_local_diff_config]
- [S6] 分支沒改、但主線改了某篇的第二支 about_code 檔時,那篇的指紋不應改變。[test: t_reread_fp_survives_mainline_advance]
- [S7] 兩條分支對同一支 Python 檔的改動只差縮排(例:一條把 `return y` 搬進迴圈、一條只把它縮成兩格)時,兩者的指紋應不同。[test: t_reread_fp_keeps_whitespace]

## 實務隱患

- 守衛面:這是推送前會擋的閘(`note_reread.gate` 是 block 時)。風險是「該重讀的被當成已對照」:新指紋只在作者改動逐字相同(只去掉行號與 `index` 行,空白照算)時才相同,上下文三行變了也會變,比 blob 指紋寬的只有「主線改了作者沒碰的地方」這一種——那一種由主線那次推送的回頭重讀負責。S2、S4、S7 守住其他邊。
- 已排除:金流:不碰。
- 已排除:對外送出:只跑本機 git。
- 已排除:不可逆:紀錄檔格式不變;回退只要還原提交,舊指紋的紀錄照舊可用(升級後記的 `v2` 紀錄在回退後不再算數,要重 prepare 一次)。
- 時間:多一次 `git diff`(候選 about_code 聯集一次),跟 prepare 本來就組的 diff 同量級;check 原本只跑 `--name-status`,現在多這一次。耗時沒量過,實作時在本 repo(`scripts/lumos` 約五萬行)量一次寫進實作紀錄;逾時照第 3 點退回 `v1`。

## 回退

- 還原提交即回到頂端 blob 指紋;升級期間記的 `v2` 紀錄不再算數,進行中的分支重 prepare 一次。消費專案跑 `lumos update` 取回舊版。
