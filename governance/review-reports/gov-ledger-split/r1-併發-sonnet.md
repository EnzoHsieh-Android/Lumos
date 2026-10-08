severity: major

# r1 併發席(sonnet)審查報告:治理帳例行紀錄分流_計劃

立場:時序一律往最壞排(多工作階段同時寫、多 worktree、批次寫到一半被切斷、本機帳目錄不存在)。r1-intake 已修的 7 條與存在類修正不重報。

## Findings

1. 本機帳的目錄與寫法沒定義,第一次寫就失敗,例行紀錄整批靜默丟光
severity: major
blocking: 是——在乾淨 clone 上例行紀錄全丟、`_gate_event` 那路每次噴 telemetry-write-failed,[S1] 的「出現在本機帳」做不到,屬 major。
spec 段落:〈做法〉3(本機帳的位置)、〈做法〉5(寫不進去)。
引句:「`<git 共用資料夾>/lumos/governance-local.jsonl`,共用資料夾用 `git rev-parse --git-common-dir` 取」
問題:spec 只給路徑,沒說 `.git/lumos/` 誰建、檔誰建、用哪種開檔方式。`.git/lumos/` 預設不存在。時序:新 clone 或新容器第一次提交 → pre-commit 的 `_gate_event`(nodehome-check)要寫本機帳 → 目錄不存在 → OSError → 回 False → 呼叫端印 telemetry-write-failed;`_append_governance_log` 同情況被 `except OSError: pass` 吞掉,什麼都不留。因為「取得到 common-dir」所以不會觸發〈做法〉6 的退回版控帳,這條失敗路徑沒有任何補救,而且每次都重現。若實作者為了解這個而借 `_ledger_append`(正是被提示要注意的原子追加寫法),那支用 `os.open(WRONLY|O_APPEND|O_NOFOLLOW)`、沒有 O_CREAT,檔不存在也會失敗,還有 4KB 單筆上限會讓大事件(drift-check 的 rows)被拒。spec 沒有在三種寫法(沿用現有 text-mode 追加 / `_ledger_append` / 新寫)之間選一個。[S4] 只測「寫不進去」的報錯,沒有測「第一次寫要能建出來」。
佐證:file: `scripts/lumos:1358`(`_gate_event` 直接 `open(...,"a")`,無 mkdir)、file: `scripts/lumos:1427`(`_append_governance_log` 同,`except OSError: pass`)、file: `scripts/lumos:18507`(`_ledger_append` 無 O_CREAT、4KB 上限)。`git rev-parse --git-common-dir` 回傳的 `.git` 底下沒有 `lumos/`(實測)。

2. 本機帳改成所有 worktree 共用一個檔,而批次寫入不是原子的:兩個 worktree 同時跑 doctor --ci 會把彼此的行切斷
severity: major
blocking: 是——併發寫入造成多筆紀錄同時作廢且讀者不報錯;這是新引入的共享寫入面,不是既有行為,屬 major。
spec 段落:〈做法〉3、〈做法〉2(分流發生在「逐筆寫的迴圈裡」)、[S5]。
引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
問題:現況版控帳是每個 worktree 各一個工作樹檔,兩個 worktree 從不寫同一個檔;只有同一 worktree 內的多工作階段才會撞。分流後所有 worktree 共寫 `.git/lumos/governance-local.jsonl`。`_append_governance_log` 在 `with open(...,"a")` 裡逐筆 `f.write`,文字模式緩衝 8192 位元組,批次一超過就會在行的中間切成多次 write()。實測 200 筆 ~130 位元組的行,實際 write 長度是 [8255, 8279, 8322, 4234],不是整行倍數。時序:worktree A 與 B 同時跑 `doctor --ci`(每次全名單重喊 check-s warned,批次輕易超過 8KB)→ A 先寫出 8255 位元組(結尾停在某行中間)→ B 的 8255 位元組插進來 → A 的剩餘部分接在 B 之後。結果出現「A 半行+B 整行」黏成一行的壞 JSON,`_drift_jsonl_parse` 遇到只會略過,A 與 B 各自至少一筆同時消失,沒有任何錯誤輸出。單行 `_gate_event` 是一次 write,不受影響;受影響的是 `_append_governance_log` 這條(doctor --ci、spec-gate-run、escape-auto-failed、bound-tests 全走它)。spec 在盤點裡有說 `_append_governance_log` 一批可能混兩種,卻沒處理這批寫入到了本機帳之後的原子性,也沒要求「單次 os.write 整批/逐行」。
佐證:file: `scripts/lumos:1427`(逐筆 f.write 在同一個 with 裡)、file: `scripts/lumos:3488`(doctor --ci 把 gov_events 整批丟給 `_append_governance_log`)、file: `scripts/lumos:18507`(專案自己已有的單次 O_APPEND 整行寫法,spec 沒指定採用)。

3. 「工作目錄永遠乾淨」的主目標被另一本版控帳破壞:唯讀的 `lumos context` / `lumos show` 每次都 append 版控的 `docs/.usage-log.jsonl`
severity: major
blocking: 是——spec 的 WHY、REVISIT 的成功度量(雲端工作階段不再被「有沒提交的改動」打斷)靠這個前提,實測前提不成立;屬遺漏平行路徑,major。
spec 段落:開頭 WHY 與白話段;〈盤點〉(只盤治理帳)。
引句:「兩者分開後平常提交推送完工作目錄就是乾淨的」
問題:時序:雲端工作階段 → 提交推送(分流後治理帳不動)→ AI 依 CLAUDE.md 的指示跑 `lumos context <節點>` 或 `lumos impact` 查筆記 → `_usage_log` 往進版控的 `docs/.usage-log.jsonl` 追加一行 → `git status` 再度有未提交改動 → 平台提醒照樣打斷。pre-commit/pre-push 提示每次都會推相關筆記到眼前,這條路徑比治理帳寫入更頻繁。〈盤點〉只數治理帳「寫帳約 17 處」,沒有盤同樣被 `_BOOKKEEPING_FILES` 列為簿記的其他進版控帳。[S1] 只驗治理帳位元組不變,不會發現這個缺口;REVISIT:2026-12-01 的度量會把「沒改善」誤歸因成分流規則不夠。
佐證:file: `scripts/lumos:16181`(`_usage_log` 寫 `docs/.usage-log.jsonl`)、file: `scripts/lumos:16197` 與 `scripts/lumos:16256`(show、context 都呼叫)、`git ls-files docs/.usage-log.jsonl` 回傳該檔在版控內(1038 行)、file: `scripts/lumos:24193`(`_BOOKKEEPING_FILES` 列出同族多本)。

4. 繞過閘的痕跡(skipped-env、skipped)被分到只存在單機的本機帳,與 spec 自己對 code-loop skipped-env 的理由互相矛盾;雲端容器丟掉後這些繞過紀錄就消失
severity: major
blocking: 是——spec 為 code-loop 訂的原則是「繞過痕跡必須留在治理帳上」,同一原則套到 drift-check、note-shape、note-audit、note-reread、nodehome-check 的略過事件卻被反向處理,且本案的動機環境(雲端工作階段)的 `.git` 隨容器丟棄;屬守衛面缺口,major。
spec 段落:〈做法〉2 分流表。
引句:「繞過代碼審的痕跡,工具承諾「留在治理帳上」」
問題:右欄收了 drift-check:skipped-env / skipped、note-shape(全部,含 skipped-env、skipped)、note-audit:skipped-env / skipped、note-reread:skipped-env / skipped、nodehome-check:skipped。這些全是「有人用 LUMOS_SKIP_* 繞過閘」的事件;pre-push 的錯誤訊息對使用者說「LUMOS_SKIP_DRIFT_CHECK=1 單次略過……會留帳」「都由 lumos 記帳」,CLAUDE.md 對 LUMOS_SKIP_NOTE_SHAPE 也說「會留帳」。時序:雲端工作階段中使用者設 `LUMOS_SKIP_DRIFT_CHECK=1 git push` → 事件寫進該容器的 `.git/lumos/`(不進提交、不被推送)→ 工作階段結束容器回收 → 繞過紀錄消失,事後 CI 與別台機器無從審計。左欄原則「拿不準的留在版控帳」沒有套到這些。spec 的〈實務隱患〉只論證「判定不讀本機帳」,沒回答「繞過可審計」這個承諾。
佐證:file: `scripts/hooks/pre-push:472`(drift 略過「都由 lumos 記帳」)、file: `scripts/hooks/pre-push:483`(逃生訊息「會留帳」)、file: `scripts/lumos:34702`(drift-check skipped-env 經 `_gate_event_or_warn`)。

5. `git rev-parse --git-common-dir` 回相對路徑,spec 沒寫解析基準
severity: minor
blocking: 否——只影響例行紀錄落點,不影響任何判定;實作時依 repo_root 解析即可避開,屬可執行性缺口。
spec 段落:〈做法〉3、[S5]。
引句:「共用資料夾用 `git rev-parse --git-common-dir` 取(worktree 共用同一份)」
問題:實測主 worktree 頂層回 `.git`、子目錄回 `../.git`、另一個 worktree 內回絕對路徑 `/tmp/gt/.git`。`_gate_event(repo_root, …)` 的 repo_root 與行程 cwd 不必相同(`_sp_run_text` 不帶 cwd、也有人用 `git -C`)。若實作用 `git -C root rev-parse --git-common-dir` 再拿結果跟行程 cwd 接起來,在 cwd≠repo_root 時落到錯的資料夾(有 mkdir parents 時還會在別處建出假的 `.git/lumos/`),而且「取得到」所以不走退回版控帳。spec 沒要求 `--path-format=absolute` 或「以 repo_root 為基準解析相對值」,[S5] 只測 worktree 與取不到,沒測相對路徑。
佐證:實測(git 2.43:`git rev-parse --git-common-dir` 在頂層 `.git`、`sub/` 內 `../.git`、worktree 內絕對路徑);file: `scripts/lumos:1405`(`_sp_run_text` 不帶 cwd);`_append_governance_log` 用 `cwd=str(vault)` 跑 git(file: `scripts/lumos:1417`)。

6. 分流表自己的規則有互相衝突處:`check-*` 被說成「全是提醒」但 check-r 會寫 hard blocked;「bound-tests 全部/nodehome-check 全部」與「各閘 fail-open 留左欄」沒有優先序
severity: minor
blocking: 否——只影響 `lumos gov` 統計的歸屬,判定不讀這些;但表若直接當常數實作,兩處結果不確定,是 spec 精確度缺口。
spec 段落:〈做法〉2 分流表第一列與左欄最後一列、備註括號。
引句:「doctor 各段 check-*(只由 doctor --ci 寫,全是提醒觀察)」
問題:`check-r` 在 IRREVERSIBLE 標錯位置或沒回退綁定時寫 `kind=blocked, hard=True`,是「doctor 會失敗」的紀錄,不是提醒。另外 `_gate_failopen(repo_root, gate, why)` 可對任何 gate 寫 `kind=fail-open`;右欄寫「bound-tests 全部」「nodehome-check、note-shape、delguard 全部」,左欄寫「各閘的 fail-open」,同一筆 (bound-tests, fail-open) 兩邊都命中,spec 沒說誰優先。實作者隨便選一邊,另一邊的測試([S1]/[S2])對不上。
佐證:file: `scripts/lumos:1908`(check-r blocked hard:True)、file: `scripts/lumos:43083`(`_gate_failopen` 對任意 gate 寫 fail-open)、file: `scripts/lumos:42447`(`_bound_tests_log` 的 kind 是自由參數)。

7. 兩本合併讀的排序與去重不等於「分流前後總數相同」
severity: minor
blocking: 否——只影響 `lumos gov` 統計與 doctor spec-gate 比例段的顯示,判定類不讀;但 [S3] 的斷言會在這幾種情形失真。
spec 段落:〈做法〉4、[S3]。
引句:「同一組事件分流前後總數相同」
問題:(a) `cmd_gov` 以 `sorted(rows, key=ts 字串)` 排序、鍵是 (commit,nodes,gate,kind,token,check),不含 ts。本機帳是共用的,兩個 worktree 在同一個 HEAD 各跑一次 doctor-run / nodehome-check,原本各自的版控檔分開算,合併後同鍵被折成一筆,總數變少。 (b) ts 是帶時區位移的字串;版控帳含別台機器(別的時區)寫入的行,字串排序跟時間順序不一致,doctor 的「最近一次規格閘」讀法是「同節點後者覆蓋前者」,舊的版控 spec-gate-run 與新的本機 spec-gate-run 同一秒或時區不同時,誰是最後一筆取決於排序方式,spec 只寫「依時間合併」沒定義排序鍵與同秒時的順序。(c) 統計讀者之前只看自己 worktree 的帳,合併後會包含其他 worktree(其他分支)的例行事件。
佐證:file: `scripts/lumos:8240`(`sorted(rows, key=lambda r: r["ts"])` 與去重鍵 k)、file: `scripts/lumos:2866`-`scripts/lumos:2876`(`_latest[節點]=note` 後者覆蓋前者)。

## 逐節

- 檔頭/WHY/白話段:finding 3。
- 盤點:finding 3(盤點範圍只含治理帳)。其餘已讀,無新 finding。
- 範圍:已讀,無 finding。
- 做法 1:已讀,無 finding。
- 做法 2(分流表):finding 4、6。
- 做法 3:finding 1、2、5。
- 做法 4:finding 7。判定類讀者只讀版控帳的清單我逐一對過(`_codeloop_read_from_ledger` 只認 passed/skipped、`_fix_check_events`、`_loop_close_stamps`、`_escape_released_loops` 讀的種類都在左欄),無遺漏。
- 做法 5:finding 1(S4 不涵蓋首次建檔)。
- 做法 6:已讀,無 finding(退回條件本身成立,問題在 finding 1、5 的「取得到卻寫不進」)。
- 實務隱患、驗收條款、回退、天花板:S1 受 finding 3 影響;S3 受 finding 7 影響;其餘已讀,無 finding。

## 實務隱患逐類(併發席視角)

- 併發/競態:finding 2。
- 中途失敗/斷電半行:本機帳沿用現有 text-mode 追加,半行與下一筆黏成壞行的風險與版控帳現況同等,不是新增;但納入 finding 2 的修法(單次 write 整行)即一併收斂。
- 稽核/繞過可追:finding 4。
- 部署/回滾:本機帳不影響判定,回滾成立,無 finding。
- 資安:本機帳在 `.git/` 內,不暴露;無 finding。
- 金流/對外送出:無——只寫本機檔,不呼叫網路。

最嚴重 severity 為 major,blocking 共 4 條(finding 1、2、3、4)。
