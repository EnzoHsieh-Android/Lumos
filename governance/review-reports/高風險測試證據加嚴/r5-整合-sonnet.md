severity: blocker

# r5 外部審稿:高風險測試證據加嚴(基準重播改到 CI 的 PR 檢查)

**前提與限制。**
- 我以三個月後接手的人的姿態,對照 `/Users/enzo/harness/lumos-highrisk-evidence` 讀完 r5-snapshot.md 全文與 r4-intake.md。
- 這個席的 Bash 不能呼叫 `gh`,所以主線有沒有設分支保護、有沒有設必要檢查,我查不到(見第 7 條)。
- 我跑過一次 `lumos spec-gate … --no-run`,它寫的是被 git 忽略的本機帳,沒有改到任何版控檔。

**r4 的問題有沒有修好。**
- r4 的 G1 是「放在推送前帶來的接縫」(掛鉤與版本錯開、增量或累計範圍、直推主線、標籤、冷樹)。改成獨立指令加 CI 的 `pull_request` 事件後,這一類接縫確實拿掉了,包括版本錯開和直推主線的算不出分岔點。
- 但換位置帶出另一批新問題,下面是第 1 到 9 條。
- 推送前的舊說法沒清乾淨,在 d3、d4、白話、名詞四處(第 8 條)。

1. 以測試檔為單位選要重播的測試,會讓已經合進主線的風險高計劃被擋(誤擋)。
引句:「定義在這次改檔清單裡的測試檔的那幾支」
severity: blocker
blocking: 是,正常的 PR 會被 `base-replay-failed`(hard)擋成 rc1,等於讓閘不能用。
- 第 3 點挑的是「綁的測試定義在這次改到的測試檔裡」,粒度是整個檔,不是這次新增或改過的那幾支測試。
- 第 2 點選計劃只看「`_計劃.md` 在改檔清單裡」。S17 還特別說 status 是 done 也算,選計劃沒有 status 條件。
- 本 repo 的測試全在單一檔 `scripts/test_lumos.py`:`.lumos/config.json` 的 `run_cmd` 是 `scripts/test_lumos.py -k {method}`,3177 支 `t_` 函式。
- 重現:有一份風險高計劃 P,它的測試上一個 PR 已合進主線。下一個 PR 只改 P 的 status、補 REVISIT 或 `lumos set`,同時給別的功能在 `test_lumos.py` 加測試。
  - P 在改檔清單裡,P 的新行為測試所在的檔也在改檔清單裡。
  - 這些測試在分岔點(配上 head 的測試檔)本來就綠,於是被判「新行為測試在舊程式上就綠」,擋下。
- 實測頻率:`git log Lumos/main --first-parent --since=2026-10-20` 的 48 個合併裡,有 33 個動到 `_計劃.md`,29 個同時動到 `test_lumos.py`。
- S3 的措辭「不在這次改檔清單的測試檔裡」寫的也是檔級,所以綁定測試也會鎖死這個行為。
- 唯一出口是每個 PR 都替 P 手寫 `base_replay_skip`。
- file: `.lumos/config.json:5`
- file: `scripts/lumos:25982`(找 `_platform_test_index` 的呼叫端確認粒度是檔)⚠ 後半是推論,`_platform_test_index` 我沒逐行讀。

2. 驗收條款 S12、S16 文法不合,規格閘對這份計劃回 rc1,這兩條沒有被當成條款。
引句:「當計劃的 created 早於生效日、但第一次進 git 歷史的日期在生效日之後時應當成生效日之後;淺複製時應只看 created」
severity: blocker
blocking: 是,設計閘過不了,`[test:t_high_risk_evidence_since]` 與 `[test:t_expected_table_fingerprint]` 兩個綁定沒有生效。
- 重現:`python3.14 scripts/lumos spec-gate Projects/高風險測試證據加嚴_計劃 --no-run`,rc=1。
- 輸出:「條款綁定: ✗ — 2 條格式看不懂(不算條款):S12(第 232 行…觸發子句缺逗號)、S16(第 236 行…)」。
- 原因:S12 與 S16 的「當…時」後面沒有逗號(「時應當成」「時表指紋應改變」)。
- 該計劃檔與 r5-snapshot.md 逐行相同(diff 為空),所以不是快照落後。
- 同一份計劃的 `lumos lint` 是 0 問題,說明 lint 抓不到句式問題,只有 spec-gate 抓得到。
- 這是唯一讓這份計劃「現在就過不了自己的設計閘」的缺陷。
- file: `docs/lumos-toolchain-knowledge/Projects/高風險測試證據加嚴_計劃.md:232`、`:236`

3. 在 CI 裡寫的治理帳事件不會留下,RETIRE-IF、REVISIT 和天花板六量的是一個永遠看不到資料的東西。
引句:「兩種擋下事件都是 0,而且同期逃逸帳裡沒有一筆描述是」
severity: major
blocking: 是,撤除條件一定先觸發,判斷依據失真。
- 這個 repo 的 `pull_request` 工作只有 `permissions: contents: read`,而且沒有 commit、upload-artifact 步驟。
- 所以 `lumos pr-evidence` 在 runner 上寫的 `base-replay-failed`、`base-replay-proven`、`pr-evidence-skipped`、`expected-unsigned`,隨 runner 一起丟掉。
- 版控的 `docs/.governance-log.jsonl`(21 MB)只會收到簽核那一筆 `expected-signed`,那是人本機簽、跟功能一起提交的。
- 後果有三個:
  - RETIRE-IF 第一條「兩種擋下事件 90 天都是 0」在 CI 擋了多少人的情況下都會成立。
  - 第三條「skipped 佔比過半」的分母永遠是 0。
  - 天花板六說「只有 `pr-evidence-skipped` 的統計看得到」,實際也看不到。REVISIT 2027-02-04 同理。
- 圖譜已經有同族事故:`Systems/reversibility-governance-ledger` 的 PITFALL「度量式撤除條件在本機帳不在(新 clone、CI、被刪)時…誤報該撤」。
- `ci-wait` 的 `_ci_record` 只記 run 的結論和失敗步驟名,記不到 `skipped` 這類 rc0。
- file: `.github/workflows/ci.yml:14`
- file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:27`

4. 新事件寫在哪個閘名底下沒有定義,也沒說要登記到 `_KNOWN_GATES`;沒登記就靜默不寫。
引句:「寫一筆 `base-replay-proven` 事件(帶計劃與支數,回頭條件數得到分母)」
severity: major
blocking: 是,不補這條,事件寫不進去,同時 `t_gov_stats_gate_drift` 會紅。
- 只有 `expected-signed` 指定了閘名 `signoff`(第 8 點)。
- `base-replay-proven`、`base-replay-failed`、`pr-evidence-skipped`、`expected-unsigned` 的 `gate` 欄位完全沒有定義。
- `_gate_event` 對不在 `_KNOWN_GATES` 的閘名只印警告就不寫,不丟例外(`scripts/lumos:1840`)。
- `_KNOWN_GATES` 與 `gov --stats` 的漂移守衛都要求同步更新(`scripts/lumos:16574`,`t_gov_stats_gate_drift`)。
- `_GOV_LOCAL_PAIRS` 是白名單,沒列的組合進版控帳,所以 `hard:false` 的 proven/skipped 該不該分流到本機帳也沒說。
- 第 10 點和第 11 點都沒有提到這一步。
- file: `scripts/lumos:1840`
- file: `scripts/lumos:16574`
- file: `scripts/lumos:1638`

5. 「工具壞了不擋所有人」與「整體上限交給 CI 工作的 timeout-minutes」互相矛盾,而且沒指定加在哪個工作。
引句:「不另設總預算——整體上限交給 CI 工作的 timeout-minutes」
severity: major
blocking: 是,一支卡住的測試會讓不相關的後盾一起失效。
- 第 1 點說任何例外都要 rc0 放行,但逾時被 Actions 砍掉的結果不是 rc0。
- ci.yml 的 `gates` 工作 `timeout-minutes: 20`,裡面還有自主迴圈測試、doctor、code-loop、drift check、Anchor verify。
- 單支預設逾時 900 秒(15 分鐘),兩棵樹、多支串行。兩支卡住就超過 20 分鐘,工作被砍,後面的 Anchor verify 等步驟全部沒跑。
- 結論是紅或「未定」(`ci-wait` 把 cancelled 當 rc0 不判綠,`_CI_RED` 含 `timed_out`)。這和第 1 點的 fail-open 約定相反。
- 第 1 點只寫「CI 加一步」,沒有指定放在 `prep`、`shards`、`gates` 哪個工作。
- 放 `gates` 就和上面的步驟共用 20 分鐘;新開工作就要同時處理 `needs`、`fetch-depth`、`PR 事件補上本機 main` 三段重複樣板。
- file: `.github/workflows/ci.yml:179`
- file: `scripts/lumos:62543`

6. 消費專案的 CI 沒有任何機械守衛,淺層 checkout 會讓指令永遠靜默略過。
引句:「消費專案的 CI 範例寫進 lumos-project-notes 的說明」
severity: major
blocking: 是,消費專案的閘沒有任何訊號,沒接線也沒人知道。
- 第 1 點:算不出 merge-base 時印一句、寫 skipped、rc0。消費專案常見的預設 checkout 是淺層(`fetch-depth: 1`),`git merge-base` 一定算不出來,這道閘每次都「成功」略過。
- 現有的先例是 `_ci_jobs_calling_without_full_history` 加 doctor 的「專案 CI 沒呼叫 X」與「那個工作沒抓完整歷史」提醒,note-shape、note-audit 都有(`scripts/lumos:47579`、`:59285`)。這份計劃沒有為 `pr-evidence` 新增對應的 doctor 行。
- `lumos update` 不會動各專案的 CI 設定(note-shape 的 doctor 訊息自己這樣寫),所以版號升了 CHANGELOG 也寫了,消費專案還是不會有這一步。
- 第 3 條講的帳丟失讓「統計看得到跳過」這條補救也不成立。
- 第 10 點的 CHANGELOG 說明沒提醒消費專案要自己貼 CI 步驟。
- file: `scripts/lumos:47579`
- file: `scripts/lumos:59215`

7. 「本 repo 主線都走 PR」沒有出處,PR 檢查紅了擋不擋得住合併完全取決於一個沒查的設定。
引句:「lumos repo 自己的主線改動都走 PR」
severity: major
blocking: 是,「CI 才是最終依據」這個轉向的前提沒有證據,而且 `pull_request` 工作是這個 repo 目前唯一擋合併前的位置。⚠ 分支保護或必要檢查的現況我查不到。
- 能查到的只有歷史:`git log Lumos/main --first-parent` 在 2026-10-07 之前有 2186 個直推提交。2026-10-08 起 105 個第一親代提交裡 103 個是 `Merge pull request`。
- 另外兩個也是多親代的合併提交,其中一個帶 `[skip ci]`。GitHub 會因此略過整個 CI,包含這一步。
- `CLAUDE.md` 沒有「只走 PR」的規矩。
- 圖譜 `Projects/enforcement可觀測性_計劃` 在 2026-09-08 記「主線沒有分支保護(回 404)」,該句在那份計劃自己的 REVISIT 之下。現在是否已設必要檢查沒有 FACT 行。
- 現有的後盾幾乎都掛 `if: github.event_name == 'push'`,是主線合併之後才跑。這個 `pull_request` 工作是第一個在合併前擋的新閘。
- 紅了而人按了合併,什麼也不會發生,也不會在 push 事件重跑。
- 第 7 條的前提要補 `[來源:部署]` 的事實行和 `[confirmed:]` 日期,否則這是沒查的前提。
- file: `.github/workflows/ci.yml:4`
- file: `docs/lumos-toolchain-knowledge/Projects/enforcement可觀測性_計劃.md:153`

8. d1 到 d7 與正文不一致,d3、d4 還停在「推送前」。
引句:「第一批是推送前基準重播、預期值表與整表簽核」
severity: major
blocking: 是,決策紀錄是有結構的出處,寫錯的 d4 會讓照做的人把第一批做成推送前版本。
- d4(第 40 行)寫「第一批是推送前基準重播」。
- d3(第 34 行)寫「先紅模式的風險高計劃…才推得上去」。「先紅模式」在 r2 就整個拿掉了,而且簽核改成 PR 檢查才查。
- 白話(第 74 行)寫「推送前整張表要有人簽」,也寫「放到推送版上跑」。
- 名詞(第 82 行)用「推送版」指 head,第 80 行已經定義 head 為 PR 頂端提交,同一份文件兩個詞。
- 第 10 點「`templates.md` 講推送前行為那幾句」:這些句子(如第 71 行「推送前要這份計劃迴圈編號的一筆輕量審通過」)講的是風險低的推送前輕量審。那一路沒改,字面上看會被誤改。
- 這幾處如果照字面實作,第一批會被做成掛鉤。
- file: `skills/lumos-design-loop/templates.md:71`

9. 第 10 點和第 11 點有漏項,新增頂層命令會讓既有測試變紅。
引句:「產生器統一補一個早於生效日的 `created`,沒有產生器、直接寫檔的那批逐支補」
severity: major
blocking: 是,照清單做完,CI 還是紅。
- 新增頂層命令 `pr-evidence` 後 `t_docs_command_count` 一定紅。ARCHITECTURE.md 第 108、112、142 行與 `skills/lumos-project-notes/reference.md:118` 寫死「98 個頂層命令」,真值取自 argparse 的 `--help`。第 10 點的 ARCHITECTURE.md 只寫了「規格閘流程」。第 11 點沒提這個測試。
- 第 11 點漏的測試守衛:`t_gov_stats_gate_drift`(第 4 條)。`HELP_WHEN` 的漂移守衛要確認有沒有被涵蓋。
- `scripts/test_lumos.py` 與 `scripts/hooks/pre-push` 在 `governance/anchor-baseline.json` 的 anchors 裡。改測試檔照 Anchor verify 一定要先 `anchor approve`,計劃沒有一個字提到。
- 第 10 點圖譜清單沒列 `Systems/bound-tests-gate`。它是 `.github/workflows/ci.yml` 的家(`about_code` 列了),而且 WHY 行有「CI 拆工作」和「pull_request 補本機 main」兩條,這次加步驟會讓那兩條過時。frontmatter 的 `lands_in` 有它,第 10 點沒有,兩處對不上。
- 第 10 點也沒列 `skills/lumos-project-notes/commands/06-代碼審與推送.md`(這個檔寫了推送閘與 CI 後盾清單)。
- `lands_in` 還沒包含要新開的 pr-evidence 家,只是第 10 點說「lands_in 補上」。
- file: `scripts/test_lumos.py:39978`
- file: `ARCHITECTURE.md:108`
- file: `governance/anchor-baseline.json`

10. S22 的測試只要字串存在就會過,管不到接線位置。
引句:「當 CI 的 pull_request 工作流程跑時,應有一步以 PR 的 base 與 head 提交呼叫 lumos pr-evidence」
severity: minor
blocking: 否,不影響功能正確,但綁定偏弱。
- 現有 `t_ci_yml_matrix_and_gates_shape` 用指紋釘後盾步驟的內容和順序,守得更細。
- S22 若只比對「`ci.yml` 含 `pr-evidence`」,把步驟放到 `if: github.event_name == 'push'` 底下、或放進沒有 `fetch-depth: 0` 的工作、或用 `github.sha` 取代 `base.sha`,測試都還是綠。
- 這一條該同時要求:步驟的 `if` 含 `pull_request`、所在工作 `_ci_jobs_calling_without_full_history(…, "pr-evidence")` 為空、參數用 `pull_request.base.sha` 與 `head.sha`。
- file: `scripts/test_lumos.py:86909`

11. 沒有 CI 的專案手動指令的預設值在本 repo 就不成立。
引句:「沒有 CI 的專案在開 PR 前手動跑 `lumos pr-evidence --base origin/main --head HEAD`」
severity: minor
blocking: 否
- 本 repo 的遠端叫 `Lumos`,沒有 `origin`(`git remote -v`);預設分支也可能不叫 main。
- `origin/main` 沒先 fetch 就是舊的。
- 手動跑會把事件寫進版控帳,人要記得一起提交。
- file: `/Users/enzo/harness/lumos-highrisk-evidence/.git/config`

12. 「建樹前清同前綴的殘骸」與危險區段一天時限的寫法不一致。
引句:「建樹前清同前綴的殘骸」
severity: minor
blocking: 否
- 第 4 點寫的是無條件清同前綴。
- 實際的 `_isolated_worktree_sweep` 只清超過 `_ISOLATED_WT_STALE_SEC`(86400 秒)的。
- 危險區段(資源隱患)那行寫「超過一天」,兩處對不上。
- 字面照做會刪掉本機另一個會談正在跑的重播樹。
- file: `scripts/lumos:26117`

13. `ci-wait` 對這一步的認法沒寫:rc0 的跳過在它眼裡是綠,而且沒開 PR 就沒有這個 run。
引句:「任何沒預期的例外都印原因、寫 `pr-evidence-skipped`、rc0」
severity: minor
blocking: 否
- `ci-wait` 只看 run 的結論,失敗步驟名只在紅時取,所以略過會被報成綠。
- 這個 workflow 沒有 feature 分支的 `push` 觸發,只有 main 和 `pull_request`。推分支後馬上 `ci-wait` 會得到 no-run。
- file: `scripts/lumos:62672`
- file: `.github/workflows/ci.yml:4`

14. 簽核簽的是工作目錄那份文字,和 PR 檢查比的 head 提交不保證一致。
引句:「計劃文字只讀一次(工作目錄那份,簽的人看的就是它)」
severity: minor
blocking: 否
- 工作目錄有未提交的表格修改時,簽出來的指紋提交後就對不上 head,PR 檢查擋下 `expected-unsigned`。
- 沒有「工作目錄那份與 HEAD 相同才准簽」的檢查。

15. 開關放寬沒有 doctor 提醒,也沒登記進度量的 off 清單。
引句:「warn 只印不擋、off 整道不跑(含第 7 點規格閘的表格檢查),兩者都寫一筆事件」
severity: minor
blocking: 否
- note-shape、note-audit 等閘在 `gate` 不是 block 時 doctor 都會唸,`_metric_gate_off` 也有對應分支。
- `pr_evidence` 兩樣都沒寫。off 的期間事件數會被當成「沒擋任何東西」算進 RETIRE-IF。
- file: `scripts/lumos:4676`

## 實務隱患逐類

- **併發:**
  - 同一個 PR 連推,既有的 `concurrency` 取消舊的,屬實。runner 暫時,被砍的樹一起消失。
  - 本機手動跑時看第 12 條。
  - 兩個 PR 同時跑各用各的 runner,無共用路徑。
- **效能:**
  - 每支每棵約 2.7 秒(本 repo 實測)。重播串行加在 `gates` 的關鍵路徑上,延長每個 PR 的 CI 時間,看第 5 條。
  - 讀 21 MB 治理帳取簽核,一次 `git show` 加逐行比對,無影響。
- **資源:**
  - 暫存在 runner 上,離開即棄,無。本機手動跑才有殘骸問題(第 12 條)。
- **回滾:**
  - 順序要先拿掉 CI 步驟再拿掉指令,計劃寫的順序正確。
  - `base_replay_skip` 留著只會讓 lint 對未知鍵發軟警告(`scripts/lumos:12425`),計劃說「無害」大致成立。
  - 版號「已升不倒退」成立。
- **PR 來自 fork 的權限:**
  - 無。`GITHUB_TOKEN` 唯讀,這一步不需要任何 secret,不寫任何遠端。
  - 風險在於 fork 的測試碼在 runner 上執行,這和現有 `shards` 同級。
  - fork PR 可以自帶 `base_replay_skip` 與自己的帳列,屬於威脅模型單人自用,放行。

總結:最嚴重為 blocker,blocking 共 9 條(blocker 2 條:第 1、2 條;major 且 blocking 7 條:第 3 到 9 條),其餘 6 條 minor(第 10 到 15 條)不 blocking。
