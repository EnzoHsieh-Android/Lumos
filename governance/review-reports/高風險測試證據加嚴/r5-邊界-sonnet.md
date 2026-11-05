severity: blocker

# r5 邊界席審查(邊界-sonnet)

重現用的小程式都放在 `/tmp/lumos-seat-work/高風險測試證據加嚴/邊界-sonnet/`,已刪。重現方式寫在各條裡。

## r4 邊界發現的修補狀況

- b1(工具壞了變擋推送):已修。整支包例外、`pr-evidence-skipped`、rc0,S4 有條款。
- b2(總預算):已移除。環境變數壞值改走預設,`float('nan')`、`inf`、`1e308` 實測不會讓 `_kill_run` 丟例外。
- b4(生效日):部分修。當天用「不早於」,淺複製只看 created。但「第一次進 git 歷史」這個來源還有洞,見第 2 條。
- b9(全標 keeps 死鎖):已修。
- b10(外側空格):已修。
- b11(上限):已加 2000 字與 500 列,但邊界定義與簽核提示的新問題見第 7 條。
- b12(帳壞行):只寫了「壞行跳過」,型別錯誤的行沒定義,見第 11 條。

## 發現

1. 引句:「定義在這次改檔清單裡的測試檔的那幾支」
severity: blocker
   blocking: 是。粒度是「檔」不是「測試」,在單一大測試檔的 repo 會對前一批早已合併的測試硬擋下(`base-replay-failed`,rc1),唯一出口是 `base_replay_skip`。
   - 重現:本 repo 的測試全在 `scripts/test_lumos.py`(3177 個 `def t_`)。
     - 風險高計劃 P 的第一個 PR 合併後,P 的新行為測試 T1..Tn 都在 `scripts/test_lumos.py`,在分岔點本來就綠。
     - 第二個 PR 只要 (a) 順手改了 P 的筆記(`lumos set status`、補審計紀錄,鐵則 1 本來就要求改 code 時寫回圖譜),又 (b) 動了 `scripts/test_lumos.py` 的任何一行。
     - 這時 P 在改檔清單裡,而 T1..Tn「定義在改檔清單的測試檔」,全部被重播。
     - 它們在分岔點是綠,於是被當成新行為測試、在舊程式上就綠,第 5 點判擋下。
   - 放大:一個掃過上百篇計劃的 PR(批次改連結)加一次測試檔改動,就是上百篇 × 每篇數支 × 2 棵樹的重播,同時全部誤擋。
   - S3 的字面(「不在這次改檔清單的測試檔裡」)與第 3 點「前一批已經合進主線、這次沒改到的測試不重播」只在不同檔時成立。
   - 缺的判準:這支測試在分岔點的樹裡是否已存在,或它的定義是否落在 diff 的 hunk 裡。
   - file: `scripts/lumos:23525`(`_platform_test_index` 只有方法名集合,沒有檔案資訊,拿不到 hunk)。
   - 沒有任何條款或測試名守這個場景:S3 的綁定測試 `t_pr_evidence_only_changed_tests` 只守「不同檔」。

2. 引句:「計劃的日期取開頭欄位 `created` 與計劃第一次進 git 歷史的日期兩者較晚的」
severity: major
   blocking: 是。計劃被搬路徑或改名,就會從生效日之前變成生效日之後,隨即被硬擋(要求預期值表與簽核),`base_replay_skip` 還免不掉表與簽。
   - 重現:`git mv a/p_計劃.md b/p_計劃.md` 後,執行 `git log --diff-filter=A --format='%H %cs' -- b/p_計劃.md`。
     - 只回改名提交(2026-11-04),不是原始建立提交(2026-01-01)。
     - 實測的就是 `_plan_first_commit` 用的那條命令,pathspec 限住後 git 看不到來源路徑。
   - 後果:created 很早的舊計劃被改名或搬目錄(PR 改名計劃、目錄整理、vault 改名)後,「較晚者」變成改名提交,落在生效日之後。
     - 風險高的舊計劃(審查帳 77% 是風險高)只要出現在改檔清單,就要預期值表與簽核,否則 `expected-unsigned`(hard,rc1)。
     - 第 2 點明寫「預期值表與簽核照查」,`base_replay_skip` 只免重播。
   - 天花板七只提到壓提交與 rebase,沒提改名;S12 的字面正好把這種情形判成生效。
   - file: `scripts/lumos:14194`(`_plan_first_commit` 沒用 `--follow`、`-M`,也沒辦法用)。

3. 引句:「不寄信不推播,只讀本機 git、計劃與帳、寫本機治理帳」
severity: major
   blocking: 是。`pr-evidence` 只在 CI 跑,事件寫進 runner 本機的 `docs/.governance-log.jsonl`,沒有任何步驟把它帶回版控,所以規格自己的撤除條件與回頭條件讀不到資料。
   - RETIRE-IF 靠「治理帳的 `base-replay-failed`、`expected-unsigned`、`pr-evidence-skipped`、`base-replay-proven` 連續 90 天的計數」。
   - REVISIT 2027-02-04 也是看「`pr-evidence-skipped` 佔全部重播結果的比例」。
   - 這幾種事件全都是 CI 指令寫的。
   - file: `.github/workflows/ci.yml:177`(gates 工作);全檔 grep `governance|upload-artifact|\.jsonl` 只命中第 302 行(anchor 基準檢查),沒有提交或上傳治理帳的步驟。
   - 缺口:CI 事件怎麼進治理帳沒有寫(例如 `lumos ci-status` 回抓、artifact、回寫提交)。鐵則 4 要求回頭條件可機械量,現在量不到。

4. 引句:「不另設總預算——整體上限交給 CI 工作的 timeout-minutes」
severity: major
   blocking: 否。逾時走的是封閉方向(CI 紅),與 S4「工具壞了不擋所有人」相反。有出口(`pr_evidence.gate: off`、`base_replay_skip`),但要先紅一次才用得上。
   - 規格沒寫新步驟放進哪個工作。`ci.yml` 現有 `timeout-minutes` 是 10、15、30、20(第 28、49、120、180 行),全套已逼近上限(檔頭寫 32–38.5 分、45 分上限)。
   - 算式:上百支新行為測試 × 2 棵樹 × 本 repo 實測每支每棵約 2.7 秒,約 9 分鐘;Android 冷樹單支可達 900 秒。
   - 工作整個被殺時,同工作的其他閘也跟著不報。
   - 與第 1 條疊加(幾百支重播)必踩。
   - 單支逾時只對單支生效,整批上限沒有。

5. 引句:「head 的表指紋不在 head 版本治理帳裡任何一筆同計劃的 expected-signed 事件裡」
severity: minor
   blocking: 否。比對鍵 `plan` 的寫法沒定義,兩端拼法不一致時變成永遠「未簽」,但重簽可解。
   - 寫的一端 `lumos signoff <計劃>` 走 `env.find(node)`,接受節點名、stem、路徑、帶不帶 `.md`;`cmd_signoff` 記的是 vault 相對的 `rel`(`scripts/lumos:16541`)。
   - 讀的一端的計劃來自 `git diff` 的 repo 相對路徑(如 `docs/…-knowledge/Projects/X_計劃.md`)。
   - 規格只寫「NFC 後比」,沒寫正規化成哪一種拼法。
   - 簽完後 PR 內把計劃改名,表指紋不變但 `plan` 變了,也會被當成未簽。

6. 引句:「資料列至少一列、每列剛好四格、四格都不能是空的」
severity: minor
   blocking: 否。只有「來源」欄有實字數門檻,「輸入」「預期」欄一個標點或看不見的字就算有內容。
   - `| S1 | . | . | 需求文件第二點 |` 或兩格都是 `U+200B`(零寬空格)的列可以過。
   - 實測 `'\u200b'.strip()` 仍是 `'\u200b'`、`'\u200b'.isspace()` 為 False,所以不會被去空白判空。
   - 預期值表「逐列寫輸入與預期」是整個機制要證明的東西。

7. 引句:「每格最多 2000 字、表最多 500 列(超過算格式錯,簽核時印得完)」
severity: minor
   blocking: 否。界線定義有歧義,「簽核時印得完」在大提示下不成立。
   - 「500 列」沒說含不含表頭與分隔列(資料列 500 與表格列 502 是兩種答案);「2000 字」沒說是 NFC 前或後的碼位數。
     - `t_expected_table_check`(S14)無法釘死這個界線。
   - 上限組合是 500 × 4 × 2000 = 4,000,000 字,全部進同一個提示字串。
   - `_confirm_tty_dev` 先 `os.write(fd, prompt.encode(...))` 才 `select`(`scripts/lumos:34251`),逾時(300 秒或 `LUMOS_TTY_TIMEOUT`)只管 `select` 的等待。
   - 實測:開一個 pty、不讀 master 端,寫入 100,000 位元組在 3 秒後仍阻塞(1,000 位元組就能正常寫完)。
   - 後果:終端不排空(斷線、流量控制、無人讀的 pty)時,大表簽核卡在寫入,不會進「逾時記 AI 簽」,無人看顧流程失去預設出口。

8. 引句:「欄位不是字串(例如寫成清單)當成沒寫、印一句」
severity: minor
   blocking: 否。「是不是字串」與「實字數」在實際解析器上兩頭都漏。
   - 實測 `_note_from_text` 解析:
     - `base_replay_skip: [a, b]` 得到字串 `'[a, b]'`,不是清單,所以「寫成清單」的例子在行內寫法下會被當字串處理。
     - `base_replay_skip: 1234567890123` 是字串、`_real_chars`=13,純數字就算理由。
     - `base_replay_skip:`(空值)得到 `[]`,正確地走「不是字串」。
     - 重複鍵取最後一個。
   - 同一個 PR 內作者可自己寫入,理由內容不查(本來就是自我認證,見名詞「已排除」行的同類設計),但數字與行內清單這兩個形狀沒測試守。

9. 引句:「用既有的 `_nodehome_name_status` 解析,路徑含 tab 或換行也切得對」
severity: minor
   blocking: 否。沒指定 `norm=False`,NFD 儲存的路徑查不到,計劃或測試檔被靜默略過(封閉方向外的放行)。
   - 重現:`core.precomposeunicode=false` 下提交 NFD 檔名 `café_計劃.md`(其中 `é` 為 e + 組合重音)。
     - `_nodehome_name_status(raw)`(預設 `norm=True`)回 NFC 路徑,`_note_text_at_rev(".", "HEAD", 該路徑)` 回 None。
     - `norm=False` 才讀得到。
   - 函式 docstring 明寫「要拿去 git 查的呼叫端用 norm=False」(`scripts/lumos:44527`)。
   - 規格要拿這些路徑去 `git show <head>:路徑` 和複製測試檔,沒寫要 `norm=False`。

10. 引句:「head 把它放寬(block 改 warn 或 off、warn 改 off)時改照分岔點那一版判」
severity: minor
    blocking: 否。比的是分岔點而不是目標分支現況,以及「分岔點版設定讀不到」沒定義方向。
    - 舊分支遇到目標分支後來把 `pr_evidence.gate` 從 off 改成 block:PR 沒碰這個設定,head 與分岔點都是 off,「PR 自己放寬」沒觸發,這次 PR 檢查整道不跑,儘管合併後的主線是 block。
    - 新增告警閘的先例比的是推送起點(`_lint_new_relax`,`scripts/lumos:39570`),這裡的分岔點是更舊的版本。
    - `_lumos_config_at_ref` 有 `missing`、`unreadable`、`git-failed` 三種狀態(`scripts/lumos:60011`),規格只說壞「值」當 block,分岔點整檔讀不到時 head=off 要照什麼判沒寫。
    - 壞值部分實測符合先例:`OFF`、`None`、`['off']`、`''`、`' off'`、`True`、非物件都回 block 加警告。

11. 引句:「兩版治理帳的讀法只留這一份;壞行跳過,整檔讀不到回 unreadable」
severity: minor
    blocking: 否。型別壞的簽核行會讓例外往上丟,被外層包成 `pr-evidence-skipped`+rc0,帳是追加的所以永久生效,整道檢查靜默關閉。
    - `_gov_rows_at` 把讀出的任意 JSON 值餵給 `keep`(`scripts/lumos:61061`):可能是字串、清單,或 `plan` 為整數。
    - 規格只定義「壞行(讀不出)跳過」,沒定義非物件行或型別錯欄位的 `keep`。
    - `_GOV_FIELD_TYPES` 只被要求新增 `origin`(`scripts/lumos:16917`),`plan`、`table_sha`、`row_count` 沒有型別檢查。
    - 只要版控帳裡有一行含 `expected-signed` 字樣的非物件行(手改、合併衝突誤解),每個 PR 的比對都例外。

12. 引句:「兩端都由呼叫者明確給;指令內部先算 `git merge-base <base> <head>` 當分岔點」
severity: minor
    blocking: 否。極端引數沒定義,以及 `--head` 若是分支名,在長時間重播中會看到不同提交。
    - `ci.yml` 的 `on:` 同時有 `push`(main 與標籤)和 `pull_request`(`.github/workflows/ci.yml:4`)。S22 只要求「有一步以 PR 的 base 與 head 呼叫」,沒要求 `if: github.event_name == 'pull_request'`。
    - 沒加 `if` 時,push 與標籤事件的 `${{ github.event.pull_request.base.sha }}` 是空字串,指令變成 `--base  --head `,argparse 回 rc2,不是「放行」(S4 只涵蓋 merge-base 算不出與例外)。
    - `--base`/`--head` 以 `-` 開頭、空字串、同一提交、互不相干歷史:除「相同」「互不相干」(merge-base 回 1,S4 已涵蓋)外,其餘沒寫是 rc2 還是放行。
    - 規格沒寫先把兩端解成完整 SHA 一次。後面讀計劃、讀設定、讀帳、`worktree add` 都用原字串;手動跑 `--head origin/feature` 時,背景自動 fetch 讓該 ref 在數分鐘重播中前進,各步驟看到不同提交。

13. 引句:「用 head 那棵樹的 `_platform_test_index` 找每支測試在哪個檔」
severity: minor
    blocking: 否。借用的函式回傳沒有「測試在哪個檔」。
    - `_platform_test_index` 回的是 `methods_for(plat)`(`discover_test_methods` 的名稱集合,`scripts/lumos:6908`)與 `hay_for`(字串),沒有檔案對應。
    - 現成可借的是 `_walk_test_files(..., with_path=True)`(`scripts/lumos:6735`、`6762`)。
    - 同名測試出現在多個檔時,「定義在改檔清單的測試檔」的判定也沒寫(任一個算,還是全部都要算)。

14. 引句:「任一支要重播的新行為測試在分岔點是綠」
severity: minor
    blocking: 否。這是唯一的硬擋,單次執行定生死,沒有重跑。
    - 針對競態或不穩定行為的回歸測試,在舊程式上有機率綠,也被硬擋。
    - 出口是 `base_replay_skip`。PRProof 對「跑不可靠」回 ERROR(規格自己的 PRIOR-ART 提到),這裡的硬擋沒有對應的重跑或不可靠判定。

## 各節逐項

- 名詞:已讀,無 finding(生效日的來源問題併在第 2 條)。
- 問題與最小解、調研結論、不做:已讀,無 finding。
- 做法第 1 點(指令與回傳碼):見第 12 條。
- 做法第 2 點(哪些計劃要查):見第 8、9 條。
- 做法第 3 點(要重播哪些測試):見第 1、13 條。
- 做法第 4 點(兩棵樹與環境變數):`LUMOS_REPLAY_TEST_TIMEOUT` 實測 `1e10`、`1e300`、`1.7e308` 都不丟例外。
  - 極小正值(`1e-9`、`0.0001`)會讓每支逾時,全部變弱證據、走 `pr-evidence-skipped`,記得到但等於關掉重播。
  - 要重播零支時印一句、不重播,正確。
  - TMPDIR 指到的目錄何時建立沒寫:不存在時 Python 的 `tempfile` 會退回系統 `/tmp`,現場就留在樹外。
- 做法第 5 點(判定):見第 4、14 條。
- 做法第 6 點(生效日與開關):見第 2、10 條;`created` 當天與格式不合的值走既有先例,沒有新問題。
- 做法第 7 點(預期值表):見第 6、7 條;其餘拆格規則的實際構造(外側空格、行尾空白、逃脫)我逐例推演,沒找到會被繞過或誤判的構造。
  - 表格列表頭後面的列若不以 `|` 開頭,會被當成表已結束而不納入指紋,但簽核提示印的是解析後的表,看不到的行也不會被簽,風險很低,不列。
  - 來源格內含 `[S1]` 寫法:實測 `clause_bindings` 不會把它當成第二次定義(條款解析只認行首)。
- 做法第 8 點(指紋與簽核):見第 5、7 條;`json.dumps(ensure_ascii=False)` 對 U+2028 等不會撞,沒有新問題。
- 做法第 9 點(PR 檢查查表與簽):見第 3、5、11 條。
- 第二批:已讀,無 finding(本批不實作)。
- 驗收條款:S1 到 S22 的邊界缺口已併入上面各條,另外 S3、S12 的字面直接對應第 1、2 條。
- 回退:已讀,無 finding。
- 實務隱患:效能、併發、資源、回滾逐類答。
  - 效能:`_plan_first_commit` 每份計劃一次全歷史 `git log`,本 repo 實測約 0.12 秒(332 篇計劃,約 40 秒);沒有逾時,大型 repo 每份數秒。
    - `_gov_rows_at` 每份計劃讀一次全檔,本 repo 治理帳 21,492,711 位元組、124,233 行,規格沒寫讀一次共用。
    - 兩者是效能隱患,在大 PR 與大帳下才顯著,不列為 finding。
  - 併發:同 PR 連推由既有 concurrency 取消舊的,規格已寫。兩個 `git worktree add` 同時對同一 repo 開同名 `wt`,git 自己加序號,我找不到會互相覆蓋的路徑,無 finding。
  - 資源:殘骸清理只掃超過一天的同前綴目錄,無新問題。`_isolated_worktree` 在 `KeyboardInterrupt` 會走 finally 清理。
  - 回滾:三層關法與事件追加的說明,無 finding。
- 審計修正紀錄:已讀,無 finding。

## 總結

最嚴重為 blocker,共 1 條(第 1 條),另有 major 3 條(第 2、3、4 條),其中 blocking 為「是」的共 3 條(第 1、2、3 條);其餘 10 條為 minor、blocking 為否。
