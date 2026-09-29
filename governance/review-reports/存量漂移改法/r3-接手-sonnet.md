severity: major

# 存量漂移改法 第 3 版 —— 整合與知識同步鏡頭(接手-sonnet)

範圍:把 spec 對 `guard settle` / `drift ack` / `drift scan` / `drift check` / `lumos set` / doctor E5 / 簿記名單 / 治理閘名 / skills 指令表 / lands_in 的每個假設,對 clone-ns 裡的 scripts/lumos 與 docs 逐項查過。CL = /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns

## F1 fix 寫進筆記的新句子會過推送前的筆記內容審,spec 完全沒交代這條接縫
severity: major
blocking: 是 — 不改,實作者做出的指令會產生「工具寫的句子被同一套工具的推送閘擋下」的死結,rtb 24 筆照做會卡在推送。
引句:「status 用 `edit_fm_scalar` + `edit_fm_sync_status_tag` 改;正文最後加一行」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:25363`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:25176`
1. `_note_audit_items` 把「推送範圍裡新寫、終點還在」的每一個非空行(region 不是 other 的)都列成待審行,`_note_audit_config` 沒寫設定時預設 block。fix 新寫的行全在這個範圍裡:c2 的「YYYY-MM-DD 結案(存量漂移 c2):<why>」(why 是人給的自由文字)、c3 的「狀態改為 pass(存量漂移 c3),由 [[X]] 解決」(狀態本來就在開頭欄位,判定者可能判成「推得出」)、c4 的 `--new` 與範本句「提交 <sha>;代碼審見 <卷證>」(含提交編號,典型的程式碼/git 答得出的事)、c1 改寫的四種句子。
2. 存量漂移防線 c1 的當初設計特地把 TEST 句寫成不含測試名,理由就是「筆記內容審會判成推得出」([[Projects/存量漂移防線_計劃]] 第 67 行)。這份 spec 的 c2、c3、c4 新句子沒有做同樣的分析,全文 grep 不到「筆記內容審」「note-audit」。
3. 後果二選一,spec 都沒選:(a) 要求判定者逐行判 fix 寫的句子(每次 fix 後推送前多一輪判定者工作,rtb 24 筆就是 24 批);(b) 這些行被判成推得出,推送被擋,人得回頭刪掉工具剛寫的行,而修復帳(記了「改了哪幾行」)與治理事件已經寫完,兩邊對不上。⚠ 判定者實際會把 c3 那句判成哪一類,我沒有實測,但「spec 沒寫、S1–S12 沒有任何一條釘住」這件事是確定的。
4. 同一個接縫的另一半:提交前的筆記形狀擋(見 [[Systems/筆記內容閘]])擋「新寫的程式行號引用、沒帶來源的 FACT/FLOW/DEP」。`--why`、`--reason`、`--new` 是自由文字,fix 不先套同一支形狀判定就寫入;人寫進 `path:12` 這類引用時,fix 回 0、寫了帳、留下一份 pre-commit 一定擋的髒筆記。
5. 要補:在做法裡寫明(a) fix 新寫的句子是否排除出待審行(要排除得在 `_note_audit_items` 認得特定句型,並列進 lands_in 的筆記內容審/筆記內容閘);或 (b) 寫入前對自由文字跑一次形狀判定、句式改成判定者一定判「脈絡」的說法;(c) 條款要有一條釘住「fix 寫完的筆記通得過 note-shape 與 note-audit check」。

## F2 「乾淨才准改、git 一定退得回去」的判準沒定義,對未追蹤筆記不成立,也跟 [S5] 的逐項修互相矛盾
severity: major
blocking: 是 — 不改,實作者可能用 `git diff --quiet` 實作,對新筆記直接放行卻沒有退路;或照字面擋掉同篇的第二筆修復,與 [S5] 的測試打架。
引句:「先確認那一篇在 git 裡沒有未提交的改動(工作目錄與暫存區都乾淨;有就回 2」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:14644`
1. 重現(臨時 repo):新檔 new.md 從沒提交過,`git diff --quiet -- new.md` 回 0、`git diff --cached --quiet -- new.md` 回 0,`git checkout -- new.md` 報 pathspec did not match。也就是「工作目錄與暫存區都乾淨」若用 diff 類指令判,未追蹤(也含被 .gitignore 的)筆記會通過,而 spec 第 87 行與隱患段的「git 一定退得回去」對它是假的:還原失敗、指紋不同時的最後退路(第 44 步「用 git checkout 那一篇還原」)也會失敗。spec 沒說要用 `git status --porcelain -- <路徑>` 還是 diff,`??` 算不算髒。
2. 對刻意還沒提交的新筆記(未提交的 Verification/Issue 正是 c4「前提寫未提交」的常見主角)照字面該擋,但擋下的訊息「先提交或還原」叫人先提交,提交會走 pre-commit 與 note-shape,又是 F1 的接縫。
3. 同一篇有兩件事要修(c3 加 c4 同在一篇驗證紀錄、c4 一欄兩項、c1 之後再 c4)時,第一筆修完那篇就是「有未提交的改動」,第二筆一律被擋。[S5] 寫「同一欄兩項都含時可以一項一項修」,做法第 5 節寫「一次修一項」,都沒提要在中間提交;而 [S1] 明列「那一篇在 git 裡有未提交的改動」要回 2。照字面,S5 那條測試在單一 git 狀態下不可能綠。
4. 要補:定義乾淨(含未追蹤要擋並講原因)、在 c4 與同篇多發現的說明裡寫「每修一筆要先提交那一篇」、把 [S5] 測試寫成「修一項、提交、再修下一項」。

## F3 修復帳與表態檔的符號連結檢查沒說放在哪一支、缺 repo 根參數,放進共用的 `_jsonl_append_verified` 會誤擋別的帳
severity: major
blocking: 是 — 不改,實作者最自然的放法(第 88 行同一段講的就是這支共用函式)會讓審查帳與逃逸帳在非典型佈局下整批寫不進去。
引句:「寫之前檢查帳檔、以及它解析後的真實路徑要在 repo 根底下、本身與上層目錄都不是符號連結(是就回 2)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:8511`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:5929`
1. `_jsonl_append_verified(path, rec, key_field, key_value)` 只收路徑,沒有 repo 根,無法判「要在 repo 根底下」;第 88 行前半句在改這支(追加前補換行),後半句「寫之前檢查…」緊接著沒指主詞。若放在這支裡,所有呼叫端一起受影響:審查帳 `env.vault.parent / ".canary-log.jsonl"`(scripts/lumos:5929、8482、8589、9881、9952、10124)、逃逸帳、CI 帳(29940)。
2. 這些路徑在獨立筆記庫(find_vault 支援 standalone vault)或圖譜資料夾本身是符號連結的 monorepo 佈局下,不在「repo 根底下」或上層有連結,整批記帳回 2。macOS 的臨時目錄 /var 本身是連結到 /private/var 的,若「上層目錄」一路查到檔案系統根,測試用的臨時 repo 全部踩到。spec 沒寫「查到 repo 根為止、不含 repo 根本身」。
3. 現行表態檔的讀取端(`_drift_load_acks`)只擋帳檔自己是連結,行為與新寫入端不一致,spec 沒說讀取端跟不跟。
4. ⚠ 我判斷實作者有兩種合理放法(共用函式內、或 fix/ack 各自的包裝),spec 不選,S9 只釘「帳檔是符號連結時擋下」,兩種放法都過測試,但後果差很多。要補:寫明包裝在 fix/ack 自己的寫帳函式、根由 `_vault_repo_root` 給、檢查只到 repo 根,並加一條「共用函式的其他呼叫端行為不變」的測試。

## F4 lands_in 與同步清單漏了被改動的共用函式的家
severity: minor
blocking: 否 — 不改,下一個 AI 讀到的那篇筆記仍寫舊行為,但不會做出壞系統。
引句:「同步改的筆記與文件:Systems/存量漂移守衛(drift fix 五種、修復帳、表態綁 related;responsibility 補 fix)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:32`
1. 第 88 行明說共用的 `_jsonl_append_verified` 改成「追加前先補換行」,「表態檔、治理帳等共用這支的一起受益」。這支的家是 Systems/loop-convergence-recording(第 32、34 行講它是逃逸帳與審查帳共用的寫完讀回自驗),另有 Systems/規格閘第 30 行也引它。lands_in 與第 9 節同步清單都沒列這兩篇。
2. 第 9 節的清單只有五篇;E5 標記放 lumos-cli-read,但那篇 grep 不到 E5(E5 只在存量漂移守衛、筆記內容閘出現),lands_in 是否指對家沒有查證。⚠ 我判不準 lumos-cli-read 是不是 doctor E5 的家,但可確定它現在沒有 E5 的敘述,實作者要新寫一段。
3. 第 57 行(存量漂移守衛)寫「這行是不是 REVISIT 全庫只有一支判定,三處餵的是同一版文字」,本計劃另外抽出 `_revisit_lines` 並明說其他逐行迴圈不動,同步清單沒提要改這句。

## F5 提示文字要改的地方,第 9 節與 [S10] 對不上,也漏了幾處
severity: minor
blocking: 否 — 不改,S10 的測試寫出來會抓不到全部路徑,但行為不會壞。
引句:「`lumos set` 計劃收尾的連帶待辦(c3 那一項指到 fix)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:26149`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:26145`
1. [S10] 寫「計劃收尾列出 c1–c5」都要指到 fix,第 9 節只寫 c3 那一項。`_drift_plan_followups` 出的項目是「Issue(c2)」「驗證紀錄(c3)」「回頭條件」「猜不準」四類,c2 那類與猜不準那類 spec 沒說指哪個指令。
2. c5 發現物自己的 why 字串(`_drift_guard_findings`,scripts/lumos:26145)寫死「重跑 lumos guard settle 補完」,scan、check、doctor 都印它;第 9 節沒列這個字串。改了會動到 t_drift_state_consistency_checks 一帶的斷言(我沒有逐支核對哪幾支)。
3. HELP_WHEN 的 `drift ack` 說明「那一行一改表態就失效」(scripts/lumos:35690)在 c2、c3 綁清單之後不精確(不是行改了失效,是計劃清單多了才失效),第 9 節只說「HELP_WHEN 與 argparse 的 help 一起補」沒提要改這句。

## F6 `guard settle` 對 pass 節點補改句,沒說套用 fix 的哪幾道安全步驟
severity: major
blocking: 是 — 不改,兩個入口對同一篇筆記的安全保證不一致,修復帳的欄位在 settle 路徑上是空話。
引句:「還有預告句就走第 2 節同一支(前提、日期、不疊、修復帳 `via: guard settle`)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:12195`
1. 括號列了四件事:前提、日期、不疊、修復帳。fix 的第 1 節另外有:那篇在 git 沒有未提交改動、BOM/CRLF 在鎖外就擋、寫完重讀重判、指紋相同才還原、`LUMOS_DRIFT_FIX_FAULT` 接縫、`after_sha256`。settle 路徑用不用?沒寫。
2. 若 settle 路徑跳過「乾淨才准改」,則第 87 行「筆記在版控裡、第 1 步確認過改之前沒有未提交的改動,所以一定退得回去」對 `via: guard settle` 的帳行是假話;若不做「寫完重讀確認並還原」,settle 路徑寫壞的筆記沒人發現(現行 `_guard_settle_record` 的失敗只擋寫入、不驗寫完的結果)。
3. [S3] 的測試名只釘「不需要 --test、接受 --date、沒預告句回 0」,兩種實作都過。
4. 要補:寫成「pass 補改句直接呼叫 fix 的同一支寫入流程(第 1 節第 3–6 步),只有參數解析不同」,並在 S3 加一條「pass 補改句寫入失敗時磁碟還原、帳不寫」。

## F7 c4 `--new` 沒有 YAML 值的逸出規則,驗證又只看那三個詞
severity: minor
blocking: 否 — 不改,壞掉的是別的工具(Obsidian 等)讀的前提欄,tool 自己的解析與驗證都過。
引句:「`--new` 不得含換行、不得含那三個詞(會立刻再被列出,回 2,提示改用 drift ack)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:14695`
1. 重現:用 `m.parse_frontmatter` 讀 `valid_under: "改成 \" 引號 x"`、`valid_under: 改成 a: b 這樣`、`valid_under: 改成 # 註解`,三種都 lint 空、值原樣回來。也就是 `--old/--new` 直接換原始文字時,`--new` 含 `"`、`: `、` #` 會破壞外層是雙引號或純量的欄位,`atomic_write_verify` 的「無新 lint 指紋」擋不住(自寫解析器不報)。
2. spec 說「欄位的寫法…一字不動」,但沒規定 `--new` 在雙引號欄位裡要擋 `"` 與反斜線、在純量裡要擋 `: `、` #`。範本句「提交 <sha>;代碼審見 <卷證>」目前沒有這些字元,問題只在人自己給 `--new`。

## F8 誠實界線的多處自承缺口沒有回頭條件(鐵則 4)
severity: minor
blocking: 否 — 不改,只是文件規範沒守;缺口本身有寫。
引句:「E5 只標已結案的 Issue:已結案計劃留著的過時回頭條件照樣唸、沒有標記,靠計劃收尾時的連帶待辦處理。」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/CLAUDE.md:1`
1. CLAUDE.md 鐵則 4:寫「沒機械守衛 / 只提醒不擋 / 單次量測」旁邊必須有 REVISIT 或事件入口。這份的自承有:E5 只標 Issue(沒有標記、靠連帶待辦)、set 結案「只印、不擋、不改」(第 82 行)、行程被殺「帳少一筆」、c1 日期「可能比實際轉正早一兩天」、c4 卷證「用名字猜」。只有 c2 related 那一條有 REVISIT:2026-11-28。
2. 其中 E5 那條最該加:連帶待辦只在計劃 `lumos set` 收尾當下印一次,之後沒有東西再提醒(E5 在到期日才唸,而那正是要標記的情況)。

## F9 指令文件同步的一句話與實際檔案內容對不上
severity: minor
blocking: 否 — 不改,實作者會多花一步查,不會做錯。
引句:「`commands/06` 的 guard settle 那列拿掉」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/skills/lumos-project-notes/commands/06-代碼審與推送.md:19`
1. 那一列(第 19 行)寫的是 `lumos guard settle <守衛節點> --test <測試方法名>`,全檔沒有「必填」兩個字;要改的是把它變成 `[--test <測試方法名>] [--date YYYY-MM-DD]` 並補「pass 節點會補改預告句」,而不是「拿掉必填」。
2. 「commands/04 補 drift check/scan/ack/fix 各一列」:04 現在完全沒有 drift 家族(只有 drift-history),是新增四列而非補列;reference.md 第 117 行的子命令全覽已經寫「`drift` check·scan·ack·exam」,補 fix 是對的。commands/INDEX.md 現在也沒有 drift 這一列,「INDEX 補一行」要指明放在哪個情境分類。
3. slim/skills/lumos-project-notes 只有 SKILL.md 與 reference.md、沒有 commands,內容也沒有 drift 家族的說明,不需要同步(已核對,列出來是避免接手的人再去查一次)。

## F10 c4 證據查詢重用的 `_plan_first_commit` 沒有逾時,跟第 1 節「git 查詢逾時回 2」對不上
severity: minor
blocking: 否 — 不改,只是逾時保證對 c4 證據路徑不成立,而且是在鎖外,不會拖死寫入鎖。
引句:「git 查詢逾時、不在 git repo 都回 2」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:5843`
1. `_plan_first_commit` 用 `subprocess.run` 沒有 timeout,而且「進不了歷史」與「git 失敗」都回 None;`_nodehome_git`(`_lens_git`,20 秒逾時)才有逾時。第 1 節說 c4 查證據的 git 逾時要回 2,第 5 節又說查不到寫「查不到」,重用 `_plan_first_commit` 兩者分不開。
2. 修法:c4 證據路徑先過 `_git_is_shallow`,再自己包一層帶逾時的呼叫,或改用 `_nodehome_git` 跑同一條 `log --diff-filter=A`;spec 目前只在 PRIOR-ART 寫「不另寫一支」。

## 各節檢查紀錄

- 範圍:已讀,無 finding。
  引句:「①`lumos drift fix <節點> <行號> --kind <種類>`:五種發現都有工具路」
- 做法 第 1 節:見 F2、F3、F10。
- 做法 第 2 節(c1):已讀,無 finding。git 指令 `git log --reverse --format=%H%x09%as -G "^status: pass"` 我在臨時 repo 實跑,pending 改 pass 那筆被找到、之後的無關修改不會重複列。
  引句:「settle 是原地換行,合約文字出現次數不變,`-S` 找不到轉正那次」
- 做法 第 3 節:見 F6。
- 做法 第 4 節(c2、c5):已讀,無 finding。Issue 結案狀態 done/resolved/wontfix 對得上 `_lint_collect` 裡 issue 的值域;c5 的偵測條件與 `_drift_guard_findings` 一致。
  引句:「那支現在自己寫檔、自己印訊息,不能直接叫;拆出」
- 做法 第 5 節(c3、c4):見 F7;`_STATUS_ENUM` 的位置與 verification 值域與 spec 相符。
- 做法 第 6 節:已讀,無 finding。E5 的到期迴圈與 `_revisit_split` 的輸入確實跟 spec 描述一致;E5 現在把 tuple 拆成四欄,加第五欄的標記要連 `_lines5` 一起改(實作細節)。
  引句:「抽出一支共用函式 `_revisit_lines(text)`:用 `_search_visible_lines` 剝程式碼區」
- 做法 第 7 節:見 F3、F4。`_BOOKKEEPING_FILES` 的另兩個消費者(留痕後只准提交簿記檔的提示、`_pull_source_or_abort` 的聯集合併)都會吃進新帳檔,兩者行為無害,已核對;`_KNOWN_GATES` 登記與 `_gate_event_or_warn` 的名單檢查對得上。
- 做法 第 8 節:已讀,無 finding。工具鏈 drift-acks.jsonl 實際是 17 筆 c2(2026-09-29)加 2 筆 c4,與 spec「17 筆」相符;scan.json 有 18 筆 c2 發現(1 筆已結案),補表態時以路徑加原文配對即可。
  引句:「上線時:工具鏈 2026-09-29 那 17 筆 c2 表態會因為沒記清單而重新列出。」
- 做法 第 9 節:見 F4、F5、F9。既有測試需要跟著改的兩支(t_guard_settle_rewrites_planned_prose、t_guard_settle_recovers_half_done)存在,其餘三處跑 guard settle 的測試(scripts/test_lumos.py 第 51177、51284、51388 行)只看 pending 轉正,不受 pass 新行為影響;沒有測試釘住「手改成歷史說法」的提示字串。
- 條款 [S1]–[S12]:已讀,見 F2(S5 與 S1)、F3(S9)、F5(S10)、F6(S3)。
  引句:「[S9] 所有 fix 寫入應在筆記庫寫入鎖內、重新載入後重判、原子寫入」
- 回退:已讀,無 finding。
  引句:「★同時把第 9 節改過的提示改回原本的說法★(不然閘與 scan 會指向不存在的指令)」
- 實務隱患(守衛面誤擋漏擋、不可逆、併發、效能、向後相容逐類):
  - 守衛面:見 F1(工具寫的句子被別的閘擋)、F3(共用帳誤擋)。
  - 不可逆:見 F2(未追蹤筆記沒有 git 退路)。
  - 併發:無新 finding。鎖內重建 `Env`、指紋比對還原、git 放鎖外的安排與現有 `_vault_write_lock` 可重入、30 秒接手的行為相容。
  - 效能:無 finding。我在 clone 上實測 `Env(vault)` 586 篇 0.15 秒、`_drift_state_findings` 全庫 0.009 秒、加 only 0.004 秒,鎖內兩次重建遠低於 30 秒接手門檻。
  - 向後相容:無新 finding。舊版讀表態檔會把新欄位原樣忽略(`_drift_load_acks` 只驗 path 與 kind),spec 的說法屬實。
  引句:「不拿鎖的寫入者(`decision-add`、`guard bind`、`new` 等直接寫檔的指令)仍可能在我們寫與驗之間改檔」
- 誠實界線:見 F8。
- 合約候選、審計修正紀錄:已讀,無 finding。
  引句:「(設計審過閘後填。)」

最嚴重等級:重大;blocking 共 4 條。
