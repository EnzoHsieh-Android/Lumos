severity: major

# 架構對齊席(第 2 輪)報告:架構對齊-sonnet

審材是 r2-snapshot.md。對照的程式在 `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/lumos`。我沒有跑 git 實驗,所以沒建臨時目錄。

## 問 1:分層與依賴方向

整體對齊:
- 新判定掛在 `_codeloop_guard_verdict`,跟 `last_lint_new` 同形狀加 `last_security`。
- 收尾走 `_codeloop_kg_finish`。
- 訊息由 `_cl_say_block` 分派到新的 `_cl_say_sec_block`。
- pre-push 的 `pp_cl_reason` 加第五句,測試常數 `_PPC_KIND_SENTENCES` 同步。
- 這些都是沿用現有結構,沒有跨層直呼。
- `_secinv_build` 吃的是快照、不碰磁碟,所以 `_secinv_snapshot_tree` 產出同形狀快照是可行的接縫。

finding 1:快照樹讀取與批次讀 blob,計劃沒寫沿用既有函式,有重蹈第二套的風險。

引句:「git 讀取批次化:要推的提交與起點版各用一次」

file: `scripts/lumos:34647`

severity: major
blocking: 是

說明:
- 計劃新增 `_secinv_snapshot_tree`,只說「一次 `git ls-tree -r -z`、一次 `git cat-file --batch`」,並明說不用 `_drift_tree_env`。它沒提到專案裡已有的同功能函式。
- `_nodehome_list`(`scripts/lumos:34183` 附近)已經做「提交樹列檔加內容編號」。
- `_nodehome_cat_blobs`(`:34647`)已經做批次 `cat-file --batch`。
- `_nodehome_cat_blobs_capped`(`:34614`)已經做大小上限、總量上限與逾時,docstring 寫明是「上限放在批次讀取這一層,不另起查法」,出自先前審查席的要求。
- `scripts/lumos:26610` 的註解也記過:先前有一輪另寫 `cat-file --batch` 解析,被架構席點成第二套。
- 這次計劃要的 16 MiB、256 MiB 與一萬項上限,以及批次讀取,正是這幾支函式的職責。
- 若實作另寫一套,就是同一類問題再犯一次。
- 要求:計劃明寫 `_secinv_snapshot_tree` 建在 `_nodehome_list` 加 `_nodehome_cat_blobs_capped` 之上。若不能用,寫出為什麼。例如 `_nodehome_cat_blobs` 遇路徑含換行整批回 None,與 `symlink_rejected`、`file_too_large` 這類錯誤代碼不合,就要說明怎麼轉接。

finding 2:`security backing` 是寫入型命令,放在宣告為唯讀的 `security` 家族裡。

引句:「把結果連同護欄 id、revision、配方 id、配方改到的檔與 head_sha 寫進治理帳」

file: `scripts/lumos:58886`

severity: minor
blocking: 否

說明:
- `security` 子命令組的說明是「資安護欄唯讀盤點」。
- 家節點 `lumos-cli-read` 的 INVARIANT 與唯讀契約也以此為前提。
- 同樣會寫治理帳的表態背書放在 `code-loop dispositions`。
- 建議二選一:把 `backing` 放到 code-loop 那一族,或在計劃寫明 `security` 組分成唯讀與寫入兩類,並改 help 字樣與 `lumos-cli-read` 的唯讀表述。

## 問 2:命名與錯誤處理

對齊的部分:
- 擋下訊息是三段式,最後一行是獨立指令。
- 原因代碼統一成 `<判定>:<代碼>`,規則明確。

finding 3:判定函式出例外時改成擋下,但同族的閘(例如新增告警閘)走 fail-open 加記帳。

引句:「判定函式裡任何沒預期到的例外（型別錯、遞迴過深、記憶體錯誤）一律轉成擋下」

file: `scripts/lumos:56396`

severity: minor
blocking: 否

說明:
- `_gate_failopen` 全檔共 11 處用於同族閘,是刻意設計:不因缺環境讓推送整個卡死,放行但落一筆帳。
- 這份計劃的 fail-closed 符合 d9「判不清就擋」,但計劃沒說它是刻意偏離同族。
- 要求:寫明是刻意偏離,並寫明 `evaluation_error` 不走 `_gate_failopen`。否則實作者很可能照鄰居套用 fail-open。

finding 4:閘門開關的值域與壞值處理,跟它宣稱的同族不一致。

引句:「但這份設定要有 d7 的內容簽章」

file: `scripts/lumos:33940`

severity: minor
blocking: 否

說明:
- 計劃說 `security_evidence.gate` 取 `block` 或 `warn`,「跟 `node_home.gate`、`note_shape.gate` 同族」。
- `node_home` 與 `note_lint` 的值域是 `on|warn|off`(`:7919`、`:33940`)。
- `lint_new` 與 `note_shape` 是 `block|warn|off`(`:32690`)。
- 現有慣例是「看不懂的值照預設並講一句」(`:35463`)。計劃只寫了「沒簽或驗不過當 block」,沒寫值不合法時怎麼處理。
- 計劃也沒寫從提交快照讀設定,而 `_lint_new_config(..., from_snapshot=True)`(`:32851`)是現成先例。
- 要求:改正「同族」的說法,寫明值域、壞值處理、讀法沿用 `_lint_new_config` 那一型。

finding 5:同一個子系統裡出現兩套證據狀態詞彙,而且 `stale`、`missing` 兩個詞意義不同。

引句:「整體判定（sound／unsound／excepted，規則見下）」

file: `scripts/lumos:6400`

severity: minor
blocking: 否

說明:
- `security list` 沿用 `_SECINV_RANK` 的 `missing/stale/incomplete/declared_only`。
- `security evidence` 新增 `qualified/failed/invalid/stale/missing/uncalibrated`。
- 兩邊都有 `stale`、`missing` 兩個詞,語意卻不同。
- 另開子命令讓兩者不互相污染,這個取捨可接受,但使用者會對兩個指令看到同詞不同義。
- 要求:在計劃或 `安全證據閘` 節點補一張對照,或明寫兩邊詞義不通用。

## 問 3:第二種做法

- finding 1 是主要一條。
- SARIF 嚴格解析另寫、uri 正規化各寫,計劃有寫理由。查證後 `_lint_run_and_parse` 是檔內唯一的 SARIF 讀法,理由成立,不報。
- 其餘重用都有名指,不報:JUnit 重用 `test_quality.junit()`(`scripts/test_quality.py:151`)、決策解析走 `_pq_*` 與 `_secinv_decision_problem`、治理帳讀取走 `_ledger_lines`、圍欄走 `_fence_regions`。
- 新引進的 `ssh-keygen` 簽章,檔內原本沒有(grep 無結果)。它是使用者已裁的 d7,屬於決策範圍,我不要求翻案,只審落地。

finding 6:JSON 深度上限的描述,對不上現有函式的實際行為。

引句:「JUnit XML 在解析時數元素深度，超過 64 層判 invalid。」

file: `scripts/lumos:6688`

severity: minor
blocking: 否

說明:
- 計劃寫「JSON 一律用 `_secinv_json_loads`(拒重複鍵、NaN、巢狀太深)」,又寫「沿用…的深度上限」。
- `_secinv_json_loads` 本身沒有深度上限,只拒重複鍵和非標準常數。巢狀過深是靠呼叫端 `_secinv_parse_block`(`:6979`)接 `RecursionError` 轉成錯誤。
- 證據讀取是新的呼叫端,不會自動繼承。
- 要求:寫明證據讀取要自己接 `RecursionError`,或共用 `_secinv_parse_block` 那一型。S42 的 10 萬層 JSON 測試剛好可綁。

## 問 4:落點

finding 7:`lands_in` 與「說明寫在新節點」兩句互相矛盾,有幾個落點沒有對應的改動。

引句:「實作落地時說明寫在那篇，其他節點只放連結。」

file: `docs/lumos-toolchain-knowledge/Systems/安全證據閘.md`

severity: minor
blocking: 否

說明:
- `lands_in` 列了七篇:六篇既有加新開的 `安全證據閘`。
- 計劃內文對 `bound-tests-gate`、`guard-kill`、`棧別提問表態閘` 都沒有寫會改動它們。
- `.github/workflows/ci.yml` 的 tag 觸發與只跑安全判定的步驟,以及 `scripts/hooks/pre-push` 的改動,也沒指明各自寫進哪一篇家節點。
- 查證發現 `Systems/` 沒有「新增告警閘」專屬節點,同族的閘分散在各處。
- 要求:`lands_in` 只留真的會寫的幾篇,並為 ci.yml 與 pre-push 的改動各指一個家。
- 另外,`pitfalls-code-loop` 與 `lumos-cli-read` 的現況都是「沒寫負責範圍」,動它們之前先補範圍,不然新內容會往大節點堆。

## 給編排者的 ⚠(超出架構對齊範圍,轉別席核對)

- 工具清單 `.lumos/security-tools.json` 沒有簽章,「核可決策」只是 `decision_ref`。`_secinv_decision_problem` 只核決策存在且有效,AI 寫得出來。
- 同一份計劃裡,例外、修訂紀錄、gate 設定、人審紀錄都要 d7 內容簽章,只有工具清單與它登記的 `min_requests` 下限、覆蓋證明種類沒簽。
- 這等於核可方式有兩種:金鑰簽章與決策引用。若這是漏洞而不只是不一致,應由正確性或資安席定嚴重度。

引句:「核可決策（消費專案某篇筆記的 dN）」

file: `scripts/lumos:6898`

severity: minor
blocking: 否

說明:這條放在這裡只是標 ⚠ 轉交,我不判它是否必須擋。

不對齊共 7 條,其中 major 1 條。

涉及的主要檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/governance/review-reports/安全主張驗收閘/r2-snapshot.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/test_quality.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/scripts/hooks/pre-push`
