severity: major

這是第 2 輪設計審的「整合與知識同步」席報告,審的是凍結審材 `r2-snapshot.md`。除註明外,引用的程式與筆記都是 `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate` 工作樹內的唯讀查證,沒有改任何檔,也沒建臨時目錄,不需清理。

一句話結論:這份設計有 6 處照字面做會撞牆或做出壞行為,另有 7 處精度問題。最要緊的是 `question_refs` 引用了一個解析不了它的函式,以及 `security list` 的「唯讀、無程序執行」合約跟新做法互撞。

## Findings

### 1. `question_refs` 的解析函式不能解析 `#Qn`(〈二〉證據種類之後的 question_refs 段)

severity: major
blocking: 是
判準:照字面實作,所有帶 `question_refs` 的護欄都會永遠 `question_open`,或實作者被迫另寫一套解析,違背該段「不另寫」。

引句:「解析走既有 `_pq_decision_target`、`_pq_decision_state` 那一組 `_pq_*` 函式」
引句:「寫成 `<節點>#Qn`（指消費專案計劃開頭欄位的 `pending_questions`）。」

- 問題:這兩支函式解析的是決策連結 `<節點>#dN`,不是待決問題 `<節點>#Qn`,也不看問題的狀態。
- 具體例:`question_refs: ["Projects/X_計劃#Q3"]` 傳進 `_pq_decision_target`,會被判 `"bad"`。
  - 因為 `_dref_parse` 的正則只收 `(.+?)#(d\d+)`。
  - 照 S15,「找不到」判 unsound,所以這條護欄永遠擋。
- 佐證:
  - ``file: `scripts/lumos:24720` `` 是 `_dref_parse` 的正則。
  - ``file: `scripts/lumos:8762` `` 是 `_pq_decision_target`,只認 `#dN`。
  - 真正能判「這題結了沒」的是 ``file: `scripts/lumos:8697` `` 的 `pq_parse` 加 ``file: `scripts/lumos:8825` `` 的 `_pq_settled`。
- `_pq_settled` 比 S15 寫的「已決或已驗」更嚴:它還要決策連結存在且沒作廢。條款要在這兩者之間裁一個。

### 2. `security list --commit` 與簽章驗證撞上盤點合約 S7「無程序執行」(〈一〉schema v2 段、〈四〉內容簽章、〈五〉S4)

severity: major
blocking: 是
判準:實作者要嘛讓綁定測試 `t_seclist_s07_read_only_no_exec` 變紅,要嘛讓 `security list` 與閘門對「格子是 open 還是 not_applicable」得到不同答案。

引句:「的既有輸出欄位與 S1–S13 語意不變，只多認 v2 的新欄位與新輸出區。」
引句:「暫時檔放系統暫存目錄、判完就刪。」

- 問題 a:`security list --commit` 要跑 git 子程序。
  - 盤點計劃 S7 明文是「唯讀、無網路及無程序執行」。
  - 該測試把 `subprocess.Popen` 換成會丟例外的假貨去跑 `security list`。
  - 本篇一面說 S1–S13 語意不變,一面讓 `list` 跑 `git ls-tree` 和 `cat-file`。
- 問題 b:姊妹計劃規定 considerations 沒簽或驗不過,「格子是 open」。
  - 所以 `security list` 本身就要驗章,也就是跑 `ssh-keygen` 加寫暫存檔。
  - 本篇只定義了閘門用 merge-base 版 `.lumos/security-approvers` 驗章。
  - 不帶 `--commit` 的 `security list` 沒有 merge-base,該用哪份金鑰清單,全篇沒寫。
- 具體例:同一份 considerations 簽章,在 `security list` 顯示 not_applicable,在閘門卻因 merge-base 版清單不認這把金鑰而判 open。
- 佐證:
  - ``file: `scripts/test_lumos.py:99985` `` 是 S7 測試。
  - ``file: `docs/lumos-toolchain-knowledge/Projects/資安護欄唯讀盤點_計劃.md:144` `` 是 S7 條款。
  - ``file: `scripts/lumos:58890` `` 是 parser 的描述,寫著「不執行測試、不寫檔、不連網」。
  - ``file: `docs/lumos-toolchain-knowledge/Projects/資安風險提問分階段_計劃.md:212` `` 是姊妹計劃的簽章規定。
- 需要裁的:S7 要不要改成「不帶 `--commit`、不驗章才無程序」,以及 `list` 驗章用哪份金鑰。

### 3. 閘門的「最低種類」資料來源還不存在,對未知類別 id 與表改版沒有定義,跟姊妹計劃不一致(〈二〉最低種類怎麼算、〈四〉)

severity: major
blocking: 是
判準:照字面實作,作者寫一個亂編的類別 id 就拿到零最低種類;或威脅類別表一升版,已登記護欄在 `lumos update` 後被擋,而且例外蓋不掉。

引句:「護欄層有問題就是 unsound，例外蓋不掉」
引句:「最低種類算不出來不當成零」

- 問題 a(未知 id):閘門只定義了 `threat_categories` 缺、空的情況。
  - 姊妹計劃把「引用表裡沒有的類別 id」列為不擋推送的 `cell_errors`。
  - 本篇沒說這種 id 在算最低種類的聯集時算什麼。
  - 具體例:`threat_categories: ["typo"]`、`required_evidence: [behavior]`。
    - 若 id 查不到就當零,聯集為空,`insufficient_required_evidence` 不成立,這條護欄可能 sound。
    - 若實作成 KeyError,整道變 `evaluation_error`,所有推送被擋。
- 問題 b(表改版):姊妹計劃規定表改版後「舊版號的資料列照舊算數」。
  - 本篇 §一 的表把 `threat_table_version` 的使用者只列姊妹計劃,沒說最低種類用哪一版。
  - 若用當前鏡像常數,表一升版(最低種類變嚴),所有已登記護欄就會 `insufficient_required_evidence`。
  - 這是護欄層,例外蓋不掉,唯一出路是簽 `gate: warn`。
- 問題 c(資料不存在):表目前只是「設計提案」,尚未取得使用者核可。
  - `Systems/資安威脅類別表` 是 planned 狀態,`about_code` 為空。
  - `scripts/lumos` 裡沒有任何威脅類別鏡像常數,我 grep 過。
  - 本篇的〈四〉「要跟著改的地方」沒把鏡像常數列為本篇或姊妹計劃誰的實作。
  - 兩篇的實作先後沒寫,閘門的 `insufficient_required_evidence` 寫不出來。
- 佐證:
  - ``file: `docs/lumos-toolchain-knowledge/Projects/資安風險提問分階段_計劃.md:147` `` 到 148 行是版號規則與 `unknown_category`。
  - ``file: `docs/lumos-toolchain-knowledge/Systems/資安威脅類別表.md:1` `` 起是該節點的現況。

### 4. 凍結起點自造 `origin/<預設分支>`,沒用既有的主線起點函式,失敗時會悄悄變成空樹(〈四〉起點一律是 merge-base)

severity: major
blocking: 是
判準:remote 不叫 origin、沒有 remote、或 CI 沒有 origin/HEAD 時,「凍結比對」不報錯地整個失效,而且這是往放寬的方向失效。

引句:「pre-push 用遠端追蹤的 `origin/<預設分支>`；CI 的 push 事件用 `before`」
引句:「預設分支還不存在（新 repo 的第一次推送，根提交就帶登記）：起點＝空樹，所有護欄當成新增照判。」

- 問題:專案已有一組起點函式,且內有「remote 未必叫 origin」「CI 的 checkout 不建 origin/HEAD」這類踩過的坑。本篇另訂了第 4 套規則,沒說「預設分支」怎麼認。
- 具體例:
  - 試行專案 order-demo 目前 `git remote -v` 是空的。「origin/main 不存在」在規則上等於「新 repo 首推」,起點被當成空樹。
  - 空樹起點下,被刪除、被降級的條目都「不是 merge-base 版有的」,必驗集合凍結(G1)靜默失效。
  - 同樣的事會發生在 remote 取名為 upstream 的 fork 上。
- 佐證:
  - ``file: `scripts/lumos:52527` `` 的 `_mainline_ref`,註解寫「remote 未必叫 origin」。
  - ``file: `scripts/lumos:52080` `` 的 `_push_mainlines`,把遠端 HEAD、main、master 全當候選。
  - ``file: `scripts/lumos:52110` `` 的 `_push_range_start`,以及 ``file: `scripts/lumos:52001` `` 的 `_lens_push_base`。
- 需要:說明為何不用這幾支,或明寫「預設分支」的認定規則與「認不出來」時的行為(應擋,不應空樹)。

### 5. 消費專案端沒有任何「推送後 CI」的交付路徑,試行專案現況既無遠端也無 CI(〈四〉要跟著改的地方、〈六〉上線順序、S28、S32)

severity: major
blocking: 是
判準:本篇和 d9 反覆當成後盾的「本機與 CI 判定相同」「tag 推送 CI 也判」,在唯一的試行消費專案上沒有任何東西能兌現,第 4 步的「真推送」也沒有可推的遠端。

引句:「加 tag 觸發與只跑安全判定的一步。」
引句:「維持本機 pre-push 閘加推送後 CI」

- 問題 a:本篇只改工具鏈自己的 `.github/workflows/ci.yml`。消費專案的 CI 是各自的檔案。
  - 既有慣例是 `doctor` 在消費專案 CI 缺步驟時印出可貼的步驟範本,對象是 note-shape、drift check、note-audit。
  - 本篇沒有 doctor 提醒,也沒有 `--security-only` 與 tag 觸發的範本。
- 問題 b:order-demo 現況是 `git remote -v` 空、沒有 `.github`。
  - S18、S19 的「真實版」和 S28、S32 的 CI 半邊,在它身上沒法做。
  - 〈六〉第 4 步寫「用真推送驗擋下與放行各一次」,前提是先建一個遠端。
- 問題 c:第 5 步說「前面幾步都過、使用者確認後才隨 `lumos update` 發出」,但沒寫分批機制。
  - `lumos update` 是從工具鏈來源 repo 拉最新。第 4 步要讓 order-demo 先拿到實作 ②,同時其他專案不拿,靠什麼?
  - `cmd_update` 支援 `--source`,但本篇沒用。
- 佐證:
  - ``file: `scripts/lumos:46359` `` 和 ``file: `scripts/lumos:37471` `` 是 doctor 貼 CI 步驟的先例。
  - ``file: `scripts/lumos:26976` `` 是 `cmd_update(source=…)`。
  - `/Users/enzo/orca/workspaces/order-demo` 沒有 `.github` 目錄,git 沒有 remote。

### 6. `gate: warn` 的簽章內容沒綁專案也沒到期,能被複製到別的專案,也永不自動恢復擋(〈四〉擋或只提醒的設定)

severity: major
blocking: 是
判準:使用者為某個專案簽過一次降級,AI 可以把同一段簽好的設定原樣貼進同一把金鑰釘住的其他專案,而且那份降級永遠有效。

引句:「但這份設定要有 d7 的內容簽章」
引句:「簽章放在同一個鍵下的 `signature`」

- 問題:簽的內容是 `{"type":"gate_setting","value":"warn","approved_on":…}`。
  - 其中沒有專案或 repo 識別,沒有 `expires_on`。
  - 例外有 30 天上限,gate 降級沒有上限。
  - `approved_on` 也沒寫在 config 的哪個鍵。簽章驗證要重建同一份規範化 JSON,卻沒說日期存在哪裡。
- 具體例:使用者為 order-demo 的過渡期簽了 warn(Q4)。
  - 若第二個專案也釘了同一把使用者金鑰(§四「建議至少釘兩把」,多專案共用個人金鑰是常態),AI 把該 `security_evidence` 物件整段貼過去。
  - 簽章驗得過,那個專案的閘門就被降成只提醒。
  - 降級不會到期,所以「過渡期」永遠不會結束。
- 補充:`ssh-keygen -Y verify … -I <簽章人>` 需要簽章人,但核可物件的欄位表裡沒有 signer 欄,實作者只能逐一嘗試清單裡每一列。
- 需要:簽章內容加入專案識別(例如 repo 根提交的 sha)、`expires_on` 與 signer,並把 `approved_on` 在 config 裡的位置定下來。

### 7. 破壞測試背書「沿用」的函式不能這樣用(〈二〉fault_sensitivity ①)

severity: minor
blocking: 否
判準:不改,實作者會發現沿用不了,多繞一圈。

引句:「同一配方組至少一筆非弱的 killed、沒有 survived」
引句:「不沿用 `covers`，也不從配方內容猜。」

- 問題:同一段先說沿用 `_backing_judge_groups`,又說不沿用 `covers`。
  - 該函式靠 `qid in groups[rid][-1]["covers"]` 選配方組,且回傳只有 strong 或 none 加一句理由。
  - 原因代碼表要的 `kill_unattributed`、`kill_timed_out_weak`、`kill_drifted`、`kill_abort`、`kill_error`、`kill_weak_only`、`survived` 是細緻的。
  - 這個函式會把這些全壓成 none,而且依 `covers` 運作。
- 具體例:一條配方只有 `killed_unattributed`,函式回 none 加「沒有強證據」,拿不到 `kill_unattributed` 這個碼。
- 佐證:``file: `scripts/lumos:57596` `` 的 `_backing_judge_groups`,以及 ``file: `scripts/lumos:57572` `` 的 `_backing_valid_rows`。
- 順帶:guard-kill 的合約「survived→rc1、drifted/abort/error→rc2、弱證據不放行」與本篇的 failed/invalid 分法方向一致,不衝突。

### 8. git 批次讀取沒用既有的有上限讀取器,另外治理帳讀取沒有上限(〈四〉要跟著改的地方、〈二〉讀不可信資料的上限)

severity: minor
blocking: 否
判準:字面實作的「一次 cat-file --batch 取全部」會把超限檔先整個讀進記憶體才比大小,失去 16 MiB 單檔上限的意義。

引句:「git 呼叫一律走既有包裝（`_lens_git`、`_nodehome_git`）」
引句:「冪等鍵是（護欄、種類、head_sha）：同鍵已有一筆就不再寫」

- 問題 a:`_lens_git` 沒有 stdin 參數,餵不了 `cat-file --batch`。
  - 專案已有 ``file: `scripts/lumos:34614` `` 的 `_nodehome_cat_blobs_capped`:先 `--batch-check` 問大小,超過上限的不讀進記憶體,還有總量上限。
  - 還有 ``file: `scripts/lumos:34183` `` 的 `_nodehome_list`:`ls-tree -z` 加模式過濾,連結檔與子模組不算一般檔。
  - 本篇沒提到這幾支,會是第三份批次讀取。
  - 這類自寫一套的做法在前幾輪審查被點過。
- 問題 b:冪等鍵檢查要讀整本治理帳,但上限只涵蓋證據檔。本 repo 的 `docs/.governance-log.jsonl` 現在就有 20,480,865 位元組(122,814 行),超過 16 MiB。
- 另需說明:路徑含換行時 `_nodehome_cat_blobs` 會整批判不了,這在本篇對應哪個原因代碼。

### 9. `test_quality.py` 的改動範圍低估,「原因代碼」也缺解析失敗的碼(〈二〉fault_sensitivity ②、JUnit 格式、〈原因代碼〉)

severity: minor
blocking: 否
判準:只抽 `check()` 並不夠,實作者要自己決定多改哪些,而且可能走到該節點已否決的字串比對。

引句:「把核對本體抽成只吃資料的純函式，放在 `scripts/test_quality.py` 自己裡面」
引句:「JUnit XML 在解析時數元素深度，超過 64 層判 invalid。」
引句:「實作時這張表放進程式當單一來源，測試逐一對照。」

- 問題 a:`load_receipt(folder)` 才是讀檔的一層(經 `read(folder/'receipt.json')`),不是 `check()`。
  - 從提交讀位元組餵進去,要連 `load_receipt` 一起抽。
  - 三份 capture 在目錄裡的子目錄名(baseline/fault/restored/refactor)本篇沒定。
- 問題 b:`junit()` 對所有拒收都只丟無型別的 `ValueError`,訊息是英文字串。
  - `zero_cases`、`suite_error`、`count_mismatch` 等代碼要從這些訊息分流。
  - test-quality-cli 的 WHY 明文否決「各呼叫端比對例外訊息字串」,要改成型別。這也是對 `test_quality.py` 的改動。
  - 64 層深度上限同樣需要改動 `junit()` 的建構器。
- 問題 c:代碼表缺「證據檔本身讀不出來」的碼。
  - 例:壞 JSON 的 SARIF、k6 摘要、被截斷的 XML、含 DTD 的 JUnit、重複測試身份、`outcome outside testcase`、`testcase missing name`。
  - 這些在表裡沒有對應代碼。
- Verification 節點牽動:`Verification/測試品質第四輪修補驗證` 的 `revalidate_when` 寫「改動…test-quality 拒收原因、bundle digest」。本篇改 `test_quality.py` 與更新 `_TEST_QUALITY_BUNDLE_DIGESTS` 就命中。計劃沒列要重驗該節點,也沒列固定 corpus。
- 佐證:
  - ``file: `scripts/test_quality.py:282` `` 的 `load_receipt`,以及 ``file: `scripts/test_quality.py:151` `` 的 `junit`。
  - ``file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:60` `` 的 WHY。
  - ``file: `docs/lumos-toolchain-knowledge/Verification/測試品質第四輪修補驗證.md:6` `` 的 `revalidate_when`。

### 10. 要跟著改的清單漏了幾項必經步驟(〈四〉要跟著改的地方)

severity: minor
blocking: 否
判準:實作者會在推送前被擋才發現,屬於流程漏項,不改規格也補得上。

引句:「擋下原因對照表 `pp_cl_reason`（有測試雙向比對）」

- `scripts/hooks/pre-push` 和 `scripts/test_lumos.py` 都在 `ANCHOR_FILES`,改了必須先簽名(anchor approve)。本篇完全沒提。
  - ``file: `scripts/lumos:28479` `` 是 `ANCHOR_FILES` 清單。
- pre-push 擋下後印的「逃生路依上面 check 講的原因走…」整句,不含資安這一道。
  - ``file: `scripts/hooks/pre-push:599` ``。
- CI 的紅燈訊息「合約測試紅 / 效能檢核題沒表態 / 高風險代碼無審查留痕」同樣沒資安。
  - ``file: `.github/workflows/ci.yml:198` ``。
- `skills/lumos-project-notes/commands/08-自動跑的.md` 的 pre-push 和 CI 兩列把 `code-loop check` 寫成「三個判定各自擋」(連 `lint_new` 都沒計入),新增第四道要同步。
  - ``file: `skills/lumos-project-notes/commands/08-自動跑的.md:7` ``。
- 加 `push: tags` 到 ci.yml 的 `on:` 會讓整個 workflow(含全套測試切片與現有 code-loop gate 步驟)在 tag 推送時全跑。現有步驟的 `BEFORE` 在新 tag 是全零,語意沒驗過。
  - 本篇的 pull_request 起點規則沒有對應步驟,現有 code-loop gate 步驟 `if: github.event_name == 'push'`。
- `security` 的 parser help 寫「資安護欄唯讀盤點」,新增會寫治理帳的 `security backing` 後,help 和 `_SECINV_NOTICE` 的說法要改。
  - ``file: `scripts/lumos:58886` ``。

### 11. 三條 REVISIT 的事件條件在本 repo 永遠不會觸發(〈二〉、〈四〉)

severity: minor
blocking: 否
判準:實際只有 `by` 日期會起作用,與「事件發生那次推送被點名」的用意不符,但不會做出壞系統。

引句:「REVISIT:[when-file:.lumos/security-tools.json][by:2027-01-31]」

- 問題:`.lumos/security-tools.json` 與 `.lumos/security-approvers` 是消費專案的檔,本 repo 不會有。
- 後果:這幾條 `when-file` 只剩 `by` 日期那一半有效,到期日一到可能預設擋下無關的推送。
- 需要:改用 `by` 日期本身,或寫成「消費專案出現該檔時由使用者通知」並移出機器式回頭條件。

### 12. 「唯一完整清單」漏了證據種類值域的擴充(〈一〉schema v2 新欄位表、〈二〉)

severity: minor
blocking: 否
判準:契約變更的清單不全,審過後同步回盤點計劃時會漏一項契約。

引句:「下表是本篇與姊妹計劃所有 v2 新欄位的唯一清單」
引句:「新增種類照盤點規矩升 schema_version，不用未知字串冒充。」

- 問題:`required_evidence` 與 `evidence_refs[].kind` 的值域,從 v1 的 5 種擴成 11 種,是一項 schema 契約變更。
  - 姊妹計劃第 107 行也寫了這件事。
  - 本篇唯一清單的表裡沒有對應列。
- 佐證:``file: `scripts/lumos:6391` `` 的 `_SECINV_KINDS` 現在只有 5 個值。

### 13. 提交樹快照路徑缺少同族問題的條款(〈四〉從提交樹產快照、〈五〉S4)

severity: minor
blocking: 否
判準:新入口缺少對應測試,日後出同族問題時沒有守衛會紅。

引句:「即使工作目錄停在別的提交」

- 問題:`lumos-cli-read` 的 PITFALL 明列「同族:提交樹、考試樹等其他 Env.from_texts 入口」,指 Unicode 等價路徑碰撞會讓兩篇變一篇。
  - `_secinv_snapshot_tree` 的快照走同一支 `_secinv_env`(已含分組,見 ``file: `scripts/lumos:6966` ``),結構上多半已涵蓋。
  - 但 S1 到 S47 沒有任何條款釘住提交樹路徑的 NFC 碰撞、符號連結拒收、容量常數。S4 只比兩邊相等,是 happy path。
- 佐證:``file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:19` ``。

---

## 逐條判附加節點「是否破壞宣稱的行為或合約」

- `Systems/資安威脅類別表`、`Systems/安全證據閘`:兩篇都是 planned、`about_code: []`、尚無實作,所以沒有可破壞的既有行為。但前者的表尚未核可、也無鏡像常數,是 finding 3 的來源。
- `Systems/test-quality-cli`:會牽動,見 finding 9。
- `Systems/lumos-cli-read` 的 ★INVARIANT★(search 預設排除 superseded、不排除 stale):不影響。本篇不碰 search 的濾網與排序。同節點的 PITFALL 與 WHY 見 finding 13 與 finding 2。
- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間):不影響。本篇不動 CLAUDE.md 的紀律區塊或 reinject。`lumos update` 只多一段版本變更說明。`test_quality.py` 只是它的牽連檔,不是 re-inject 的路徑。
- `Verification/測試品質第四輪修補驗證`:`revalidate_when` 命中(改 bundle digest),見 finding 9。
- 落點現況列的另外幾篇:
  - `Systems/bound-tests-gate` 的 ★INVARIANT★ 不影響。安全判定排在合約測試之前,擋下時不會讓合約測試的「紅或證不出跑過就擋」判準變弱,只是少跑一次。
  - `Systems/guard-kill` 的 rc 優先序合約不影響,與本篇的 failed/invalid 分法一致,見 finding 7。
  - `Systems/pitfalls-code-loop`、`Systems/棧別提問表態閘`:`_PPC_KIND_SENTENCES` 由四句變五句是真的,我核對過計劃那一行(`推送前一次列出全部擋下原因_計劃.md` 第 68 行)與測試。落點與 pre-push、ci.yml 的擁有者沒有衝突。

最嚴重 severity:major。blocking 共 6 條(finding 1 到 6),minor 共 7 條不阻擋。
