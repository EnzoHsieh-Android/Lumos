severity: major

審查範圍:〈資料怎麼流〉第 4、5 步、〈查證紀錄〉、〈推送前怎麼按功能判〉、S8–S14、S17、S29–S33、〈實務隱患〉、〈回退〉。已實作的部分只當背景對照,不另開 finding。所有 file 佐證都是我實際開檔或 grep 看到的。

## Findings

**1. 兩端「e2e 段」雜湊相同、指紋卻不同時,按功能判定的「要驗的情境」是空集合,字面實作會空放行**
severity: major
blocking: 是。實作者照字面寫,會讓「改弱記憶體驗收」的推送零重驗就過,而這正是 d1 要擋的洞。
引句:「兩端的 `e2e` 段不一樣(正規化雜湊不同)→要整套。」
引句:「只取 `e2e` 段不取整個 `macrobench.json`:改效能基準或 `results_dirs` 不用重跑 E2E。」
- 段落:決定 d1、S2、〈查證紀錄〉`fingerprint` 條、〈推送前怎麼按功能判〉判定順序第 3 點。
- 問題:d1 與 S2 把 `macrobench.json` 最外層的 `stability`、`stability_scenarios` 算進指紋(`e2e` 段開了記憶體時)。第 3 點判「要整套」的條件只有兩個:兩端 `e2e` 段正規化雜湊不同,或改到的檔落在 `shared_paths` 或對不到功能。
  - 「改到的檔」只留指紋範圍內的檔(`app_dirs` 加驗收素材)。`.lumos/macrobench.json` 本身不在這個範圍,第 62 行的驗收素材清單只寫「這一段設定本身」。
  - 所以只動 `stability_scenarios` 時,指紋不同,但 `e2e` 雜湊相同、範圍內也沒有改到的檔。
  - 第 3 點最後一條「全部符合→過」對空集合成立,還會印「按功能放行:驗了 」(後面是空的)。
- 失敗例:分支只把 `stability_scenarios.player_cycle.cycles` 從 10 改成 1。
  - S8:指紋不同,所以要求紀錄。開發者跑 `--case list.scroll`,寫出新指紋的紀錄(只有 `feature_runs`)並提交。
  - 預期:記憶體標準被改弱,要重驗 player 的記憶體情境(或整套)。
  - 照字面:紀錄讀得懂、`runs` 為 null、改到的檔為空、要驗的情境為空,放行。
- 同源不一致:〈查證紀錄〉`fingerprint` 條寫「只取 `e2e` 段不取整個 `macrobench.json`」,沒提 d1 的例外,與 S2 內部矛盾。
- 佐證:file: `scripts/lumos:40586-40589`。`_e2e_fingerprint` 把 `stability` 與 `stability_scenarios` 另外雜湊接進去,`e2e` 段的雜湊裡沒有。
- 修法方向:spec 要寫明「要驗的情境為空時要整套」,或把「記憶體設定雜湊」納入第 3 點兩端比較。

**2. 分岔點端用被推送提交的 `app_dirs` 算指紋,遇到分岔點樹裡沒有的項目會報錯,S9 的「改 app_dirs 並跑過驗收要認得紀錄」做不到**
severity: major
blocking: 是。新增模組或新增 `app_dirs` 項目的分支,即使紀錄完全合格也會被擋,訊息還指錯方向。
引句:「用同一份設定算分岔點與被推送提交兩端的指紋,不同才要求」
- 段落:第 4 步「何時要求」(「用同一份設定算分岔點與被推送提交兩端的指紋」)、S9、S17。
- 問題:S17 只規定「被推送提交的 `app_dirs` 有一項不存在」要擋。分岔點那一端沒有任何規定。
- 失敗例:分支新增 `app_dirs` 項目 `feature-x/`(新模組),分岔點的樹沒有這個目錄,分支已跑過整套驗收且紀錄已提交。
  - 預期(S9):認得紀錄,放行。
  - 照字面:算分岔點指紋時 `_e2e_fingerprint` 回「app_dirs 的 feature-x 在分岔點的檔案樹裡不存在」。
  - 這落在「其他內部錯誤→擋」,不是「要求紀錄」。放行路徑永遠走不到,而且擋下原因會被誤讀成工具錯誤。
- 佐證:file: `scripts/lumos:40570-40572`。`gone` 非空就回 `(None, 錯誤)`,沒有區分「這端的樹本來就可以沒有」。
- 修法方向:spec 要寫明分岔點端缺項目時的語意。例如「該項目視為空集合,指紋照算」,與被推送提交端分開處理。

**3. 被推送提交沒有 `e2e` 段(舊分支、或刻意刪掉),又改了 App 程式時,擋下訊息叫人跑的指令都跑不通**
severity: major
blocking: 是。開發者會被擋在一條沒有出口的路上,只剩環境變數。
引句:「選檔設定用被推送提交的 `e2e` 段(被推送提交刪掉了這一段,改用主線版的)」
- 段落:第 4 步「何時要求」(被推送提交刪掉這一段改用主線版)、第 4 步「怎麼判」(印要跑的指令)、第 5 步 `waive` 預設放行「HEAD 提交的指紋」、〈回退〉。
- 問題:這個情況下指紋是「主線版 `e2e` 段套在被推送提交的樹上」算出來的。能產生這份紀錄的工具都用 HEAD 的 `e2e` 段:
  - `judge` 與範本腳本讀 HEAD 的段;不在 HEAD 就回「工作目錄的 macrobench.json 沒有 e2e 段」。
  - `waive` 預設指紋是 HEAD 的指紋,HEAD 沒有 `e2e` 段就算不出來。
- 失敗例:分支在 E2E 上線前切出,只改 `app/` 程式、沒 merge 主線,推送。
  - 主線版有 `e2e` 段,指紋兩端不同,找不到紀錄,擋下,印「重跑驗收,或放行」。
  - 照做:`android-e2e-run.sh` 的前置檢查失敗;`waive` 算不出指紋。
  - 真正的出口是 merge 或 rebase 主線,spec 沒有印這一句。
- 附帶不一致:〈回退〉寫「刪段的那次推送本身用環境變數關」。但只改文件、同時刪掉 `e2e` 段的推送,兩端指紋相同,第 4 步字面規則是「不要求」。這與 〈回退〉的說法、也與 WHY 44「被推送的提交不能自己把驗收改弱」都不一致。實作者無法判斷刪段到底算不算被擋。
- 佐證:file: `scripts/lumos:40963-40970`。`_e2e_worktree_e2e` 讀工作目錄的段,沒有就回錯誤。

**4. 要驗的情境裡只要有「只列效能」的情境,按功能放行永遠過不了,擋下訊息叫人跑的 `--case` 也修不好**
severity: major
blocking: 是。S31 的放行條件對這種情境不可滿足,擋下訊息會讓人和 AI 一直重跑。
引句:「每個要驗的情境,`feature_runs` 裡都要有一筆 result 是 pass、complete 是 true」
- 段落:判定順序第 3 點「每個要驗的情境…complete 是 true」、S31、S27、判定順序第 2 點。
- 問題:設定檢查允許一個情境只列 `macrobench`(`_e2e_case_err` 只要求四種清單至少有一種非空)。這種情境按功能跑時沒有會判的項目:`result` 是 `unjudged`、`complete` 是 `false`。
- 失敗例 A:功能 `perf` 底下有情境 `bench`,只列 `macrobench: ["ScrollBenchmark#scrollList"]`。改了 `perf` 的 `paths` 底下的檔,開發者跑 `--case perf.bench`。
  - 紀錄寫入 `unjudged`、`complete:false`。
  - 推送檢查:`result` 不是 pass 且 `complete` 不是 true,擋下,印 `--case perf.bench`。再跑結果相同,無限循環。
- 失敗例 B(第 2 點):先整套跑過 pass,之後跑 `--case perf.bench`。
  - 這筆 `feature_runs` 的 `ended` 比 `runs` 晚,且不是 pass,第 2 點擋下,但 `_e2e_keep_old` 在沒有舊紀錄時不會保護它。
  - 一次本來就不可能判定的情境,把一份完整通過的整套紀錄推翻。
- 佐證:file: `scripts/lumos:41041-41048`。`complete` 為 `not skipped and bool(rs)`,`rs` 為空時固定 `False`,並註記「推送前檢查要不要認由下一批定」。這就是本稿該補的地方,spec 沒補。
- 修法方向:spec 要規定「沒有會判項目的情境」在推送檢查怎麼算。例如視為不需要驗,或設定檢查直接拒收只列效能的情境。

**5. `ended` 缺欄或格式不對時,字面規則會讓失敗的按功能紀錄被當成「比較舊」而放行**
severity: major
blocking: 是。第 2 點是整個「最新結果算數」機制的核心,壞資料時偏向放行,與 S17「判不清就擋」相反。
引句:「再看 `feature_runs` 裡有沒有哪個情境結束得比 `runs` 晚而且不是 pass」
- 段落:〈查證紀錄〉`feature_runs`(`ended`)、判定順序第 2 點與第 3 點最後一條(「結束得比…晚」)、S10、S30。
- 問題:S10 與第 4 步「判不清就擋」的列舉只有 JSON 壞、schema、`result` 值、指紋欄位。沒有 `ended`、時間格式、時區、`runs` 缺 `ended` 等。實作者用既有 `_gov_ts` 比較,壞值回 `None`,「晚於」判成 false,等於「沒有更晚」。
- 失敗例:兩台機器各寫了同一份紀錄,git 合併衝突後手動解,`feature_runs["list.scroll"]` 留下 `{"result":"fail","ended":""}`(或欄位消失),`runs` 是 pass。
  - 第 2 點:該情境的 `ended` 不比 `runs` 晚,不擋,放行。
  - 預期:紀錄讀不懂,擋。
- 佐證:file: `scripts/lumos:1713-1725`。`_gov_ts` 對非字串、非 ISO 回 `None`。file: `scripts/lumos:40589-40606`。`_e2e_record_err` 只驗 `feature_runs` 每筆的 `result`,不驗 `ended`。

**6. `waive <指紋>` 沒有指紋格式規定,工具自己印的是 12 字縮寫,貼回去會建出永遠對不上的假紀錄**
severity: minor
blocking: 否。不會做出壞系統,但會讓人白放行一次。
引句:「人用 `lumos android-e2e waive --ack <指紋>` 標成看過」
- 段落:第 5 步 `waive [<指紋>]`、`--ack <指紋>`、`--list`。
- 失敗例:judge 與按功能跑的終端輸出都印「指紋 `{fp[:12]}`」。使用者把這 12 字貼進 `waive abc123def456 --note "…"`。
  - 預期:放行當前版本。
  - 照字面:`_e2e_record_update` 在 `.lumos/e2e-records/abc123def456.json` 新建「只有放行」的紀錄。其內 `fingerprint` 欄位也是 12 字。
  - 推送檢查讀 64 字指紋對應的檔,找不到,照擋。治理帳卻已記一筆 `waived`,污染 RETIRE-IF 的放行計數。
- 佐證:file: `scripts/lumos:41105`、`scripts/lumos:41314` 都印 `fp[:12]`。

**7. `waive` 預設指紋是 HEAD 的,但推送檢查看的是被推送的那個提交;推非 HEAD 的 ref 時,預設放行放錯對象**
severity: minor
blocking: 否。擋下訊息可印出明確指紋來避免,所以屬於須補一句的事。
引句:「預設放行 HEAD 提交的指紋」
- 段落:第 5 步「預設放行 HEAD 提交的指紋」、第 4 步「何時要求」、「一次推多個 ref」。
- 失敗例:人在 `feature-a` 上執行 `git push origin feature-b`。
  - pre-push 以 `--at-sha $_lsha`(feature-b 的頂端)呼叫檢查,擋下,訊息建議 `waive --note`。
  - 預設放行 HEAD(feature-a)的指紋,feature-b 的指紋沒被放行,重推仍被擋。AI 放行此時會連記一筆錯的 AI 放行。
- 佐證:file: `scripts/hooks/pre-push:577`。傳 `--at-sha "$_lsha"` 而不是 HEAD。
- 修法方向:spec 要規定擋下訊息裡的 `waive` 與重跑指令帶明確指紋與提交。

**8. 「主線找不到→擋」沒有「這個專案根本沒用 E2E」的前置判斷,會擋掉不相干的專案**
severity: major
blocking: 是。這道閘接進所有消費專案共用的 `code-loop check`,不能只對有設 `e2e` 段的專案生效。
引句:「主線找不到、主線版的 `e2e` 段本身不合格、被推送提交的 `app_dirs` 有一項不存在」
- 段落:第 4 步「位置與接線」(排在所有放行早退之前)、「判不清就擋」(主線找不到)、S17。
- 問題:安全證據閘先用 git grep 預檢「有沒有登記痕跡」,沒痕跡就走 `no_registration`,不會被 `mainline_unknown` 擋。本稿只說「照安全證據閘那套挑主線」,沒說借預檢。
- 失敗例:純後端專案(沒有 `macrobench.json`)clone 後有 remote、但沒有任何追蹤 ref(未 fetch)。
  - 預期:這個專案跟 E2E 無關,不跑。
  - 照字面:先挑主線,`_secev_mainline` 回 `mainline_unknown`,擋下,訊息寫 Android E2E。
- 佐證:file: `scripts/lumos:10029-10050`。找不到時回 `mainline_unknown`。file: `scripts/lumos:11014-11036`。`_secev_stage_head` 的預檢在 `mainline_unknown` 之前。
- 相關未定義:新 repo 首推 main 時 `_secev_mainline` 回 `(None, 說明, None)`,代碼為 `None` 表示「新 repo,空樹起點」。本稿的「主線找不到→擋」與「主線版沒有 e2e→不跑」都沒說這種 `None` 算哪一邊。

**9. 分岔點算不出來(無共同祖先、淺層 clone)時沒有規定**
severity: minor
blocking: 否。「判不清就擋」大致可涵蓋,但「何時要求」的敘述讓實作者以為一定有分岔點。
引句:「分岔點 = 被推送提交跟主線的 `git merge-base`」
- 段落:第 4 步「何時要求」、S17 列舉。
- 失敗例:`git checkout --orphan` 建出的分支,或淺層 clone 的歷史被截斷。
  - `git merge-base` 無輸出(rc 1)。S17 的列舉(主線找不到、主線版 `e2e` 段不合格、`app_dirs` 不存在、內部錯誤)沒有這個情況。
  - 實作者可以選「當作沒有基準→要求」「略過」或「擋」,三種結果不同。
- 佐證:file: `scripts/lumos:10002-10015`。`_secev_mainline_pick` 對「跟每個候選都沒有共同祖先」是「取第一個,之後照 freeze_base_unavailable 判」,spec 沒有等價的敘述。

**10. 在 CI 環境變數有設時整道不跑,不留治理帳,是一條沒記帳的繞過路**
severity: minor
blocking: 否。符合「不防刻意偽造」的威脅模型,但違反本稿自己的對帳假設。
引句:「在 CI 裡(`_in_ci`)不跑這道,印一句」
- 段落:第 4 步第一個項目、WHY 41(出口有留帳)、REVISIT 2026-12-31(數 `skipped`)。
- 失敗例:使用者或 AI 的外殼環境有 `CI=1`(某些工具鏈會設)。
  - `git push` 時 `_in_ci()` 為真,印一句「第一版只在本機推送時判」就略過。
  - 治理帳沒有 `skipped` 紀錄,REVISIT 的「skipped 多過擋下次數的一成」永遠少算,而且 `CI=false` 也算「有設」。
- 佐證:file: `scripts/lumos:225-228`。`_in_ci` 是 `bool(os.environ.get("CI") or ...)`。

## 逐節結論
- 第 4 步:findings 1、2、3、8、9、10。其餘邊界(推主線本身、分岔點等於被推送提交、tag 推送、刪除 ref、新分支首推、一次多個 ref)已讀。
  - 推主線:pre-push 把舊位置當 `range_start`,字面可實作。
  - 分岔點等於被推送提交:兩端指紋必相同,不要求。
  - tag 推送:`pre-push` 只走 `--security-only`,與本稿「這道不跑」一致。
  - 刪除 ref:pre-push 第 467 行已 `continue`。
  - 新分支首推(非 main):走 `_secev_mainline_cands`,字面可實作,無 finding。
  - 多個 ref:逐 ref 獨立判,無 finding。
- 第 5 步:findings 6、7。
- 〈查證紀錄〉:finding 1(與 d1 不一致)、finding 5(`ended`)。「寫一半被殺的暫存檔」「同指紋重跑覆蓋」已讀,無 finding。
- 〈推送前怎麼按功能判〉:findings 1、4、5。
  - 一支檔同屬兩個功能:取聯集,合理,無 finding。
  - `shared_paths` 與 `paths` 重疊:`shared_paths` 優先,合理,無 finding。
  - `shared_paths` 為空清單:S29 沒禁止,語意是無共用路徑,無 finding。
  - 改名(新舊路徑一內一外):`--no-renames` 取聯集,再各自過濾範圍,字面可實作,無 finding。
  - 只刪檔:名單照列,字面可實作,無 finding。
  - 主線無 `features` 而分支加了、分支刪掉 `features`:`e2e` 雜湊不同,要整套,無 finding。
  - 與「兩端 e2e 段不同→整套」合起來看,「涵蓋主線版同名情境」那條在 `features` 欄位上等於死碼:兩端 `e2e` 雜湊相同,所以兩版的 `features` 必同。這不會造成錯誤,留下是冗餘。
  - `feature_runs` 有對照表沒有的情境:同指紋下 `e2e` 段必相同,正常產生不出來;只有手動合併才會發生。
  - `feature_runs` 為空物件:不放行,要求的情境全部缺,擋下,正確。
  - 功能底下零個情境:設定檢查擋(`cases` 要非空物件),被推送提交那端的設定沒被推送檢查驗,但配上「e2e 段不同→整套」仍安全。
- S8–S14、S17、S29–S33:已讀。S10「只有放行、`runs` 是 null 的紀錄應放行」措辭,可能讓實作者把「只有 `feature_runs`、`runs` 為 null」的紀錄也當放行。既有 `_e2e_record_err` 的註解已警告這點,但 S10 沒同步,屬措辭,不另開 finding。
- 〈實務隱患〉:逐類答如下。
  - 金流、對外送出、不可逆:各段已排除,理由成立。
  - 守衛面、略過檢查:已寫。
  - 時序:本稿比對「結束時間」,finding 5。
  - 路徑與識別:`waive` 的指紋參數,finding 6、7。
  - 資料增長:`history`、`waivers` 只增不刪,紀錄檔沒有上限。安全證據閘有單檔上限,本閘沒規定,但沒有具體失敗場景,不開 finding。
  - 並行:judge 與 waive 的讀改寫鎖已規定。
- 〈回退〉:與第 4 步「刪掉 e2e 段」不一致,見 finding 3。

## 固定席逐條判
- `Systems/bound-tests-gate` 的 ★INVARIANT★(code-loop check 對固定席上合約綁的測試逐支真跑,任一紅、懸空、偽證據、證不出跑過→`blocked=True` rc1;沒綁、算不出→不擋但寫帳):不影響。新增的 `android_e2e` 是獨立的擋下種類,走既有的 `--keep-going` 多行機讀(`LUMOS-BLOCKS:`)與 `pp_cl_reason` 對照,沒有改 bound-tests 的判定、也沒有碰它的帳。條件是實作時 `android_e2e` 不得早退而跳過 bound-tests 的跑與記帳。
- `Systems/pitfalls-code-loop`:不影響。spec 只加一行連結與簿記目錄,不改它宣稱的行為。
- `Systems/macrobenchmark-adapter`、`Systems/android-stability-collector`、`Systems/安全證據閘`:會談目錄沒有這幾篇,我只能對照 spec 自述的引用。借用「判不清就擋」與「設定只讀主線版」,沒有看到違反。

最嚴重 severity 是 major,blocking 共 6 條(findings 1、2、3、4、5、8)。
