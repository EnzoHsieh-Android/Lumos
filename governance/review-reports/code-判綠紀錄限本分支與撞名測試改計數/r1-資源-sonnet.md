severity: major

資源席審查報告:共 2 條 finding(1 條 major、1 條 minor),另附 3 條不評級的觀察。我把 `scripts/lumos` 當模組載入,在臨時 repo 實測,實驗目錄已用字面絕對路徑刪掉。

先講結論:新增的 `merge-base --is-ancestor` 與 `cat-file -e` 沒有防備「部分複製(partial clone)」。在部分複製裡,問一個本機不存在的 head_sha 會讓 git 去遠端抓物件,逾時之後抓取程序還會殘留。

1. 部分複製裡問本機沒有的 head_sha,git 會自動連遠端抓物件。10 秒預算被第一個 sha 吃光,逾時只殺到 git 本身,抓取程序成孤兒,過濾整批失效。
引句:「r = _lens_git_dl(rr, "merge-base", "--is-ancestor", sha, head, deadline=deadline)」
引句:「e = _lens_git_dl(rr, "cat-file", "-e", f"{sha}^{{commit}}", deadline=deadline)」
- 重現:
  - 準備:`git clone --filter=blob:none --no-local` 做出部分複製,在 `remote.origin.uploadpack` 指向一支 `sleep 40` 的腳本,模擬慢遠端。
  - 呼叫:`m._redbase_on_branch(rr, rows, head, br, time.monotonic()+10)`,rows 是 30 筆不同的不存在 sha。
  - 量到:耗時 10.01 秒,30 筆全部判不了、照舊留下,過濾等於沒做。逾時後 `ps` 看到 `git ... fetch origin --no-tags --filter=blob:none --stdin`(ppid 1)與那支腳本還活著。
  - 原因:`_lens_git` 的 `subprocess.run` 逾時只殺直接子程序,自動抓取的孫程序不會被收。
- 為什麼走得到:S6(提交不存在照存紅燈版)這條設計路徑就是問不存在的 sha。就算遠端很快,每個不存在的 sha 也會連遠端好幾次。我在本機 file 遠端實測,`merge-base` 與 `cat-file` 各印兩次 `not our ref`,代表各抓兩次。
- 前提:治理帳被忽略,加上部分複製,加上 sha 在本機已被清掉。我判 major 是因為「讓修補失效」加上殘留孤兒,但這個前提不算常見。判不準,請裁。
- 這個 repo 沒設 `GIT_NO_LAZY_FETCH`(`grep` 只找到幾處 `start_new_session`,與這段無關)。本機 Apple git 2.39 不支援該環境變數,所以不能靠它補,要改成收整個程序群組,或先偵測部分複製就不問。
severity: major
blocking: 是

2. 10 秒共用預算在大 repo 或慢 git 上很快耗盡,過濾被靜默跳過。時鐘又比受限的呼叫早開始。
引句:「dl = _t.monotonic() + _REDBASE_ANC_BUDGET_SEC」
- 時鐘起點在 `_redbase_attach`,這支只把截止時間傳給 `_gov_ledger_ignored` 與 `_redbase_branch_rows`。而 `_redbase_branch_rows` 前段的 `_lens_full_sha`、`_lens_fork_point`(約十幾次 git)、`_gov_rows_delta` 與 `_redbase_branch_name` 都沒收到 deadline。前段不受預算限制(一次最多 20 秒),卻吃掉預算。
  - 量到(PATH 放一支每次 git 先 sleep 0.7 秒的 shim,模擬慢 git):3 筆確定不是祖先的紀錄全被照留,`_redbase_branch_rows` 耗 9.92 秒。前段把 10 秒耗盡,祖先判定一次都沒問。
- 另一個量到的數字是 15 萬提交的 repo。每次祖先判定的耗時:

  | 條件 | 每次 | 200 個不同 head_sha 的結果 |
  |---|---|---|
  | 有 commit-graph | 約 0.05 秒 | 耗 10.01 秒,判出 190 個,10 筆照留 |
  | 無 commit-graph | 0.4–0.6 秒 | 只問得到約 22 個,178 筆照留 |

- 每次規格閘判紅都可能多等到 10 秒。上限與逾時都是 fail-open,而且會印一句說明,所以不會做出錯的結果。對應的失敗場景是舊的判綠紀錄在慢環境又被算進來,新分支存不到紅燈版,但是有訊息可看。這條不算擋人,判 minor。
severity: minor
blocking: 否

觀察,不評級:
- 三引號正規式 `_TG_CONST_PAT` 是佔有式,沒有回溯風險。我用 `fullmatch` 對 100 萬個 `"`、30 萬組 `a"b` 的未收尾三引號、5 萬組 `"""a"""` 等輸入量,最慢 0.007 秒。
- 讀帳與記憶體沒問題。真實的 21MB、12.4 萬行治理帳讀入加過濾 0.15 秒,行程尖峰約 115MB。同一個 head_sha 有很多筆時,`verdict` 有快取,是線性。200 個上限本身也不是二次方。
- 新測試:
  - `t_name_collision_scales`:1000 個名字走快取路徑只花 0.3 秒,改成 4000 個是 1.2 秒,線性,很穩。
  - `t_spec_gate_redbase_green_other_branch`:約 28 秒(含啟動共 33 秒),在 5 個臨時 repo 各跑規格閘,是這次新增最貴的測試。
  - 其餘新測試各 4 到 5 秒,淺複製測試也是。
  - 跑完我的 `TMPDIR` 內是 0 個殘留。

固定席筆記逐條判定:
- `Systems/lumos-cli-read.md`(search 預設排除 superseded 的 ★INVARIANT★):這份 diff 沒碰 search,不影響。
- `Systems/測試假綠形態.md`(還原翻紅釘要配前置斷言的 ★INVARIANT★):新測試在 S7、S8、S9 與撞名測試都有「★前置★」斷言,沒有違反。
- `Systems/design-loop.md`、`Systems/guard-kill.md`、`Systems/bound-tests-gate.md`:各自的合約(處置閘、guard kill rc 與 JSON、對合約綁定測試逐支真跑)都不在這份 diff 動到的函式裡,不影響。
- `Systems/loop-convergence-recording.md`、`Systems/pitfalls-code-loop.md`、`Systems/reversibility-governance-ledger.md`(★RISK★):只因 `scripts/lumos` 同檔而被點名,這份 diff 的行為沒有牽連,不影響。
- 超過上限只列名的節點:我沒有逐篇對照。

總結:max severity 為 major,blocking 1 條。

涉及檔案:
- `/Users/enzo/harness/lumos-green-scope/scripts/lumos`:`_redbase_on_branch`、`_redbase_attach`、`_redbase_branch_rows`
- `/Users/enzo/harness/lumos-green-scope/scripts/test_lumos.py`:新增的測試
