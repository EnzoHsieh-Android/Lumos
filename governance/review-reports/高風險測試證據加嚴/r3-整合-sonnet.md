severity: major

審查對象:`r3-snapshot.md`(與 repo 內計劃檔逐字相同)。先答上一輪(r2)的問題有沒有修好:帳與留痕不再參與判定、生效日改看 `created`、拆格與指紋、簽核欄位這幾組都已折進正文,沒有看到回頭。本輪的洞集中在兩處:補進來的基準重播,以及「跟著改的說法」清單和現況對不上。

我另外核對了兩個外部宣稱,都查得到:devops-cli issue 3124 確實是重播環境讓每支測試都紅、檢查形同虛設;PRProof 的 README 確實自承「錯的修補配錯的測試仍 PROVEN」。

1. 做法第 1 點的出口 `base_replay_skip` 用 `lumos set` 寫不進去。
引句:「理由去掉空白標點至少 10 個字,用 `lumos set` 寫」
severity: major
blocking: 是——環境跑不起來時唯一的出口,照規格做完是寫不進去的。
- **重現:**我在 repo 實跑 `python3.14 scripts/lumos set Projects/高風險測試證據加嚴_計劃 base_replay_skip "測試理由十個字以上才算數"`,結果擋下 rc2:「base_replay_skip 不能用 set 改,檔案沒動」。
- **原因:**`set` 只收 `SCALAR_KEYS` 那 11 個鍵,`base_replay_skip` 不在裡面。
- **清單沒列到:**做法第 8 點和第 9 點都沒把它列為要改的東西。要改的至少有:
  - `SCALAR_KEYS`
  - `_KNOWN_FRONTMATTER_KEYS`:不加的話 lint 會對每個用了這個欄位的計劃唸「沒見過的鍵」
  - `_set_keys_text` 說明
  - `remove` 的白名單
  - 專案鐵則 2「開頭欄位用指令改,別手改」
- **先例:**`plan_risk` 在 known keys 裡、卻不在 `SCALAR_KEYS`,所以一直靠手寫。照這個先例做,這份計劃就違反自己引的鐵則。
- file: `scripts/lumos:28705`、`scripts/lumos:29605`、`scripts/lumos:12273`、`scripts/lumos:12419`

2. 重播的分岔點取「推送範圍起點」,多次推送的分支會被誤擋。
引句:「起點取推送範圍的起點(`_range_base`,三點範圍取 merge-base)」
severity: major
blocking: 是——正常工作流程就會誤擋,出口只剩手寫跳過理由。
- **起點是什麼:**pre-push 對已存在的遠端分支給的範圍是 `遠端舊值..本地頂端`,所以 `_range_base` 回的是「上次推到哪」。新分支首推才改成跟主線的分岔點。
- **誤擋情境:**
  1. 第一次推送已經帶了實作和測試。
  2. 之後為了審查折入再推一次,範圍裡有計劃檔(改了審計紀錄或 status)加一支程式檔。
  3. 分岔點是上次推送的頂端,實作已經在裡面,新行為測試直接綠,判「在舊程式上就綠」而擋下。
  4. 推送前壓提交後 force push,舊遠端頂端同樣含實作。
- **同族閘怎麼處理:**test-guard 刻意改用「跟主線的分岔點」當起點,理由寫的就是「同一條分支先前推送已經處理過的候選」不重複擋。世界解 devops-cli 也是 `--base origin/main`。
- **後果:**這份計劃只對「第一次就把實作推上去」的分支正確,其他都靠 `base_replay_skip`,RETIRE-IF 第三條(跳過占一半以上)會被它自己觸發。
- file: `scripts/hooks/pre-push:41-46`、`docs/lumos-toolchain-knowledge/Projects/Android測試防竄改檢查_計劃.md:80`

3. 「遠端還沒有這條分支時 `_range_base` 回空」是錯的。
引句:「取不到起點(`_range_base` 回空,例如遠端還沒有這條分支時的首次推送)就判」
severity: minor
blocking: 否——最後還是擋下,只是原因和範圍不對,屬描述錯誤。
- **實際行為:**新分支首推時 `pp_block_range_for` 先問 push-range 取主線分岔點。失敗才退回 `空樹..頂端`。`_range_base` 對 `a..b` 一律回 `a`,所以回的是空樹雜湊,不是空。
- **後果:**
  - `git worktree add --detach <路徑> <空樹>` 會失敗,走的是「建樹失敗」那條,不是這裡寫的「取不到起點」。
  - 退回空樹時,`_spec_gate_touched_plans` 會把整個 repo 的計劃都當「範圍改到」。所有 created 不早於生效日的 doing 風險高計劃都進入重播和查表。
- file: `scripts/lumos:61298-61310`

4. 第 9 點說 `t_spec_gate_oneway_keeps_halfset` 不受影響,是錯的。
引句:「規格閘本身對風險高的行為沒變(仍只印不擋),`t_spec_gate_oneway_keeps_halfset` 不受影響」
severity: major
blocking: 是——判斷哪些既有測試會紅的前提是錯的,實作者會在大量測試紅燈上才發現。
- **重現:**該測試的計劃 fixture 由 `_sg_plan2` 產生,frontmatter 沒有 `created`,正文含「會動 pre-push hook」,所以判風險高。
- **為什麼會紅:**`created` 讀不懂,依 d6 與 `_nl_rule_lands_in` 的寫法被當成生效日之後(`not _note_date_ok("")`)。S16 就會因為沒有 `## 預期值表` 回 rc1。測試 ① 要求 `returncode == 0`,會紅。
- **範圍:**`_sg_plan` 和 `_sg_plan2` 產的風險高 fixture 全都沒有 `created`,波及的是整批 spec-gate 測試,不是一支。
- **還漏了一支:**`t_spec_gate_help_says_low_risk_blocks` 要求 help 與總表同時含「風險高只印不擋」。第 8 點要改這句,卻沒列這支測試。
- **消費專案:**手寫計劃沒有 `created` 的,升級後第一次推送也會被要求補表。
- file: `scripts/test_lumos.py:76630-76640`、`scripts/test_lumos.py:75801-75806`、`scripts/test_lumos.py:73804-73807`、`scripts/test_lumos.py:76786-76798`、`scripts/lumos:12813`

5. 重播樹的環境準備比最近的同類做法少了三件,第 3 點只寫了「平台設定用它自己的」。
引句:「分岔點那一棵其餘檔維持舊版,平台設定用它自己的」
severity: major
blocking: 是——Node 和 Python 這類消費專案兩棵樹都跑不起來,只能全部跳過。
- **同類做法:**修正關卡在隔離樹裡跑 `_spec_gate_judge_items`,多做了三件事。
  - `.lumos/config.json` 沒進版控就複製進樹。
  - 用 `_lint_link_deps` 連回 `node_modules`、`.venv`、`venv`。程式註解說不連的話 Node 的 `npx` 會在樹裡自己上網抓測試工具。
  - 平台根在樹外、沒進版控、是子模組或符號連結的,標「釘不住版本」。
- **計劃的借用清單:**第 96 行列的借用清單一件都沒有。
- **後果:**
  - 沒有 `node_modules` 的樹,兩棵都紅,判「推送版不綠」。
  - 平台 `root` 指到 repo 外的設定,兩次都在同一棵真實樹上跑。舊版「綠」,判成在舊程式上就綠而擋下。
  - 「誤擋一」「誤擋二」只講了資料檔和建置設定,沒講這幾類。
- file: `scripts/lumos:21936-22010`、`scripts/lumos:39181`、`scripts/lumos:21492`

6. 只有「推送範圍改到計劃檔」才會重播、查表、查簽,實作推送沒碰計劃檔就整道不觸發。這個缺口沒列進天花板。
引句:「只看推送範圍改到的計劃檔(`_spec_gate_touched_plans` 給的那份)」
severity: major
blocking: 是——設計審階段先推計劃、實作另外推的做法很常見,這時整道閘不啟動,而且 RETIRE-IF 會把它誤判成「沒在擋東西」。
- **情境:**計劃在設計審階段已經推上去。實作的推送只改程式和測試,沒有同時改計劃檔。
  - 計劃不在 touched 裡,S2 明文規定這種「連到同一節點被拉進來」的不重播。
  - 實作推送不重播、不查表、不查簽。
- **天花板清單:**一到五只列了 `--no-verify`、AI 簽、純人驗,沒有這一條。
- **RETIRE-IF:**生效 90 天內兩種擋下事件都是 0,結論是「沒在擋東西,改回只印」。零可能是閘根本沒觸發,不是沒東西可擋。
- file: `scripts/lumos:15534-15536`

7. 預期值表的簽核和重播讀的是工作目錄裡的計劃,不是被推送的提交,與「簽核綁內容」矛盾。
引句:「現在的表指紋要等於某一筆 `plan` 相同(NFC 後比)的事件的 `table_sha`」
severity: major
blocking: 是——並行會談共用工作目錄時,簽核可以對不上被推送的內容。
- **現況:**`_spec_gate_push_check` 的計劃文字來自 `env.notes`,也就是磁碟上的工作目錄版本。第 7 點寫的是「現在的表」,沒說從 `_lsha` 那一版讀。
- **情境:**
  - 同一工作目錄裡另一個會談改了計劃的表,還沒提交。
  - 這邊推送的提交裡,表是另一個內容。
  - 工作目錄那版剛好等於某次簽過的表,推送就過了,但被推送的表沒有人簽過。反過來,簽過的提交會被誤擋。
- **對照:**修正關卡明講「驗的是提交裡的版本,工作目錄沒提交的改動不算」,並用提交裡的設定。
- **同樣影響重播:**條款綁的測試名取自工作目錄計劃,測試檔取自推送版。
- file: `scripts/lumos:16330-16335`、`scripts/lumos:21925-21930`

8. 「跟著改的說法」清單還漏了這些仍寫著舊說法的地方。
引句:「使用者文件:`docs/指令參考.md` 與 `docs/command-reference.md` 講」
severity: minor
blocking: 否——文件過時,不會讓閘壞掉。
- `ARCHITECTURE.md:178`:流程圖「規格閘複驗 → 風險低計劃綁的條款測試沒全綠」。
- `docs/心智模型.md:188` 和 `docs/mental-model.md:190`:「推送前把風險重判一次、把測試全跑一次」只講風險低。
- `docs/methodology/圖譜即合約.md:162`:同樣的說法。
- `assets/spec-gate-zh.svg` 和 `assets/spec-gate-en.svg`:規格閘圖。
- `skills/lumos-project-notes/commands/INDEX.md:19`:「風險高→…紅綠只印」。這條列表有講 INDEX,但沒指到這一列。
- `skills/lumos-project-notes/SKILL.md:69` 和 `reference.md:687,973`:signoff 描述成「業務確認」,`--expected` 的語意不同,沒有區分。
- `scripts/lumos:16203` 的 `_auto_escape` 文案只講風險低,第 8 點只提了掛鉤那兩行。

9. 重播排在 pre-push 最前面、沒有結果快取。
引句:「每份要重播的計劃多開兩棵工作樹、各跑一次它綁的測試」
severity: minor
blocking: 否——只是慢,有出口(但出口只有 `base_replay_skip`)。
- **順序:**`spec-gate --push-check` 是第一道,在 0.6 秒的 `code-loop check` 之前。掛鉤註解的原則是「便宜的先跑」。
- **擋下後不停:**`sg_rc==1` 只記錄不 exit,後面各閘照跑。
- **重複跑測試:**一次被擋的推送,重播的測試會被 `bound-tests` 和全套測試再跑。
- **沒有快取:**因為其他閘(例如 lint-waive 要再提交)而重推時,每次重新建兩棵樹重跑,沒有以「分岔點、推送版、計劃指紋」為鍵的快取。Android 是每次多好幾分鐘。
- file: `scripts/hooks/pre-push:561-583`

10. Ctrl-C 時,序列跑法不會收掉測試子程序,卻會刪掉它正在跑的工作樹。
引句:「資源:兩棵工作樹在系統暫存資料夾,離開時收掉(`_isolated_worktree` 的收尾)」
severity: minor
blocking: 否——情境依賴 Ctrl-C 時機,孤兒程序最終會結束。⚠ 這條是讀碼推得,我沒有實跑。
- 沒開並行時走 `seen.update(_one(k) for k in jobs)`。`_kill_run` 用 `start_new_session=True` 開子程序,只接 `TimeoutExpired`,沒接 `KeyboardInterrupt`。
- 終端的 SIGINT 到不了新 session,Gradle 或測試程序繼續在剛被 `worktree remove --force` 和 `rmtree` 刪掉的目錄裡跑。
- 並行路徑有 `_BtProcs.reap`,序列路徑沒有。
- 計劃只寫「離開時收掉」。
- file: `scripts/lumos:26155-26178`、`scripts/lumos:69138`

11. 重命名測試檔時,舊檔留在分岔點樹,新舊兩份同名測試會讓判定變成弱證據。
引句:「推送範圍裡新增或改過、`_nodehome_is_test` 判成測試的檔,從推送版複製進分岔點那一棵(刪掉的不動)」
severity: minor
blocking: 否——少見情境,出口是 `base_replay_skip`。
- **情境:**把含新行為測試的檔案 `git mv a_test.py b_test.py` 再改。`git diff --name-only` 只印新路徑,複製的是 b。
- **後果:**a 留在分岔點樹裡,同名測試各一份。Python 的 `-k` 選到 2 支,declared 也是 2,判「篩選匹配到 2 支,測試名要唯一」,弱證據,擋下。
- **計劃沒說:**只寫了「刪掉的不動」,沒說改名的舊路徑怎麼處理。

12. 簽核提示用預設 30 秒逾時,人讀不完大表就會被記成 AI 簽。
引句:「逾時沿用 `LUMOS_TTY_TIMEOUT`;表大時人要先把環境變數調大」
severity: minor
blocking: 否——放行效果一樣,影響的是「人抽離多少由統計看」的統計準確度。
- 預設值 30 秒,讀不到回答就回 `None`,被判成 `"ai"`。
- 人坐在終端前、看表超過 30 秒沒答,會記成 AI 簽,並且 `gov --stats` 的「人簽 N 次」少算。
- 把環境變數調大寫進了說明,但預設行為會偏向 AI 簽,與 d3 的「預設就是人簽」不一致。
- file: `scripts/lumos:34220-34226`

13. 簽核事件寫在版控治理帳,但計劃沒說何時進哪個提交。
引句:「放在推送前、留痕之後也可以(治理帳是帳本)」
severity: minor
blocking: 否——本機推送會過,是遠端或別台機器看不到簽核的問題。
- 這句出自第 8 點,說明 code-loop 手冊要補的內容。
- `_gov_vc_gate_events` 讀的是工作目錄的帳檔,事件沒提交也讀得到。
- 但專案鐵則規定留痕通過後「只准再提交帳本,訊息固定 `chore(lumos): 記錄代碼審通過`」。簽核事件若在留痕之後寫,得多一個帳本提交,訊息該寫什麼沒有定義。
- 沒提交的話,別台機器或乾淨 clone 推同一個分支會被判未簽。
- file: `scripts/lumos:22229-22256`

14. 計劃正文有三處自己對不上。
引句:「先紅模式不加新指令、新帳欄只有留痕的 `red_first` 一個」
severity: minor
blocking: 否——只是文件內部矛盾。
- **第 244 行:**r1 時代的「最小解自問」還在,說新帳欄是 `red_first`。r2 已把留痕和 `red_first` 整個拿掉,三個月後的人會去找這個欄位。
- **S1 與做法第 1 點:**S1 寫「status 是 doing」,做法第 1 點寫「doing 或 done」。done 沒有任何條款或測試涵蓋。
- **第 221 行:**回退節說版號「跟著改回」。CHANGELOG 只記對外放出去的版本,`LUMOS_VERSION` 有守衛盯著。已升版的消費專案看到版本倒退,正確做法是再升一版,不是改回。

15. 第二批第 9 點引用的舊否決,出處和理由都對不上。
引句:「跟舊否決的關係:[[Systems/guard-kill]] 決定合約的殺傷力驗證」
severity: minor
blocking: 否——第二批另開計劃,現在還沒實作。
- 「不自動產生變異」的決定和「4–39%」誤報數字出在 `Projects/guard殺傷力驗證_計劃` 的 d1。`Systems/guard-kill` 沒有這個數字。
- d1 的理由是「等價變異不可判定、4–39% 誤報、零依賴」,沒有「會讓綁定測試被判失敗」這一條,那是計劃自己加的。
- 第二批要引入 PIT 或 Arcmutate 這類外部工具,d1 的「零依賴」理由沒有回應。
- 守衛閘門調研另記了「自動變異工具 2026-08-26 退場」,計劃也沒提。
- file: `docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:12-15`、`docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_守衛閘門_調研.md:278`

16. 全專案沒有開關,只有一個程式常數可以關。
引句:「基準重播與預期值表、簽核共用一個生效常數 `_HIGH_RED_SINCE`;設成遠未來,推送前不再重播、不再查表與簽」
severity: minor
blocking: 否——現在只在本 repo 生效,消費專案要等升級後才會碰到。
- **其他會擋的閘:**都有 `.lumos/config.json` 的 `gate` 開關(warn 或 off)和 `LUMOS_SKIP_*` 單次略過。
- **這兩道:**只有改程式常數。查表這道連每份計劃的出口都沒有,表格解析誤擋時只能改表。
- **消費專案:**生效日之後建立、升級前還在 doing 的風險高計劃,升級後第一次推送就被要求補表和簽。

## 各節結論
- 名詞、問題與最小解、調研結論:已讀。除上面引到的之外無 finding,兩個外部引用已查證。
- 做法第 2、4、5、6 點:已讀,無 finding。檢查順序、判定四種擋下、表格範圍與拆格、指紋與簽核欄位都和程式現況對得上。例外是 f3 提到的起點描述,以及 f12 提到的簽核提示逾時。
- 不做、驗收條款:已讀。16 條條款各一支互異的測試,S1 與做法第 1 點有一處不一致(見 14)。
- 回退、實務隱患、審計修正紀錄:見 14、16。

## 圖譜鏡頭(固定席節點)
- `Systems/guard-kill` 兩條 INVARIANT(rc 優先序、`--json` 純度):不影響。重播只借 `_isolated_worktree`,用自己的前綴,沒有要改 guard kill 的路徑或輸出。實作若改動 `_isolated_worktree` 的參數,要連同這兩條綁定測試一起看。
- `Systems/lumos-cli-lifecycle` 的 re-inject INVARIANT:不影響。注入範本(`scripts/templates/graph-discipline.md`)只改 sentinel 之間的內容,sentinel 之外的內容仍原樣保留。
- `Systems/test-guard`、`test-quality-evidence`、`test-quality-cli`、`Verification/測試品質第四輪修補驗證`:不影響。第一批不碰 `scripts/test_quality.py`。第二批「只借不改」,而 `test_quality.py` 有部署指紋。

## 風險類逐類答
- **併發:**
  - 兩個推送各自的前綴相同、資料夾不同,殘骸只清超過一天的,沒有互清問題。
  - 治理帳追加沿用既有寫法,無新 finding。
  - 共用工作目錄時計劃文字不是從提交讀,見 7。
- **效能:**見 9。
- **資源:**見 10。殘骸最多留一天,Android 的兩棵樹可能是數 GB。
- **回滾:**見 14、16。事件留在帳上無害這點沒問題。
- **資安:**無。只讀本機 git、計劃和帳,寫本機治理帳。威脅模型是單人本機,不防代簽是明確裁定。
- **資料增長:**無。每次被擋追加幾行,帳已是 21MB、12 萬行,讀取實測 0.16 秒,與計劃寫的 0.2 秒相符。

最嚴重 severity: major,共 16 條 finding;blocking 條數 6(f1、f2、f4、f5、f6、f7)。
