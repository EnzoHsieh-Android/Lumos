## 設計（v4）

### f1 — blocker

spec 段落：設計 §4「處置」

引句:「修 agent 在 `git worktree`(從 HEAD 建)內修該篇」

問題：審計沙盒會複製主工作樹，包含未提交內容；修復 worktree 卻從 `HEAD` 建。若候選筆記在主樹已有未提交修改，審計員看的是新版，修復員改的是舊版，最後 `copy 回主樹` 會直接覆蓋使用者修改。即使候選本身乾淨，spec 也沒規定 copy 前確認主樹該檔仍等於派工時版本，15 分鐘內的並行修改同樣會被覆蓋。現場 `git status` 已證明主樹允許 dirty，不能假設排程執行時乾淨。必須保存候選內容雜湊並在收貨時 CAS 比對，或要求候選路徑乾淨且 copy 前重驗；不相等應放棄收貨，不能覆寫。

查證：`scripts/scenario_probe.py:94-109`（沙盒 rsync 後把未提交內容一併 commit）；`governance/autonomous-loop.sh:377-380`（既有寫入流程沒有全樹 clean 前置條件，只 add 指定檔）；本次 `git status --short` 顯示工作樹已有 modified/untracked 檔。

### f2 — major

spec 段落：設計 §2、§4

引句:「`governance/review-reports/self-audit/<日期>-<stem>.md`;逾時/is_error=無檔=FAIL」

問題：初審與複審同一天、同一 stem，卻只定義一個 `<日期>-<stem>.md` 報告地址。複審若也按本節的落盤規則執行，就會覆寫初審 FAIL；若複審不落這裡，則「真相源＝報告檔」沒有複審證據。這會抹掉為何啟動自動修復的原始證據，也無法誠實驗證 trailer 中 audited/reverified 兩席各自的判定。檔名至少需要 phase/run-id（例如 `-audit`、`-reverify`），並用排他建立避免同日重跑覆寫。

查證：`governance/review-reports/self-audit/2026-08-24-lumos-cli-read.md:1-5`、`governance/review-reports/self-audit/2026-08-24-lumos-cli-write.md:1-5`（現行手動報告只靠日期與 stem 識別，沒有階段欄位）。

### f3 — major

spec 段落：設計 §2「探針式沙盒」

引句:「照 `scenario_probe.make_sandbox` 三層隔離先例建沙盒副本」

問題：被借用的先例沒有可正常執行的清理契約。`make_sandbox()` 只回傳 `<tmp>/repo`，不回傳外層 tmp；現行 caller 的 `finally` 卻執行 `shutil.rmtree(tmp, ...)`，其中 `tmp` 在 `main()` 未定義，會在結束時拋 `NameError` 且留下整份 repo 副本。spec 又沒有另訂 sandbox/worktree 的 `try/finally`、worktree remove/prune、異常/timeout 清理及殘留回收。每日進場下，這是確定性的磁碟洩漏，不只是成本未量化。

查證：`scripts/scenario_probe.py:91-110`（建立 tmp 但只回 work）；`scripts/scenario_probe.py:210`（caller 只收到 work）；`scripts/scenario_probe.py:230-240`（finally 使用該 scope 不存在的 `tmp`）；spec 未列任何 `git worktree remove`／`prune` 清理步驟。

### f4 — major

spec 段落：設計 §4「週帳」

引句:「配額=`N - 本週行數`(N=2 寫死)——每日進場只補殘額」

問題：同一 JSONL 同時寫審計結果列與 `nagged:true` 列，但配額直接減「本週行數」。只要本週喊過一個 pending，nag 列就會吃掉一個審計名額；兩個 pending 被喊後，本週候選配額直接歸零。更多 nag 還會令配額為負。應只計具備 `verdict` 的完成列，且明確 clamp 至零；測試也必須覆蓋 nag 與 quota 混存，而非分開測。

查證：`governance/autonomous-loop.sh:117-131`（既有 `run_nags` 的週排程與工作配額分離，通知不會消耗工作額度）；spec 測試 §⑨只寫「中斷後補殘、喊人每檔每週一次」，未測 nag 行不影響配額。

### f5 — major

spec 段落：設計 §4、§6

引句:「複審 PASS=檔案 copy 回主樹+蓋章+commit」

問題：這個多步寫入不是交易式流程，也沒有失敗恢復狀態。copy 成功後，蓋章、lint 或 commit 任一步失敗，主樹已被修改，但週帳可能沒有完成列、pending 也不存在；隔天會重新派同篇，或把半完成修改當新輸入。反向地，若先記週帳再 commit，commit 失敗會永久吃掉配額。spec 的「中斷後補殘」只針對週帳配額，沒有定義各步 checkpoint、原子順序及 rollback。應在 worktree 完成修正、戳記、lint 與 commit，主樹收貨則用可驗證的 commit/cherry-pick 或 CAS；任何失敗不得留下未記錄的主樹修改。

查證：`scripts/lumos:7578-7593`（蓋章本身是另一個會寫檔且可能 rc2 的操作）；`governance/autonomous-loop.sh:377-381`（既有 commit 流程各步由 `set -e` 控制，但沒有本案所需的跨日恢復帳）；`scripts/lumos:7550-7574`（`cmd_set` 有自身驗證，不等於 copy＋stamp＋commit 整鏈原子）。

## 不做什麼（邊界）

已讀，無 finding。

## 連動

### f6 — major

spec 段落：設計「架構」、連動、測試 §⑧

引句:「autonomous-loop.sh 每日進場呼叫 3 行(配額按週,見 §4)」

問題：沒有指定三行插在現行控制流的哪個位置。腳本在今日報告不存在時可於第 25/26 行退出，也會在 gap 無候選時於第 164 行退出；若 self-audit 接在 gap loop 附近或之後，「每日進場」根本不保證執行。另 `gap_select.pending_exists()` 現在只看 `pending/*.md` 的非遞迴 glob，所以子目錄不連坐雖成立，但 self-audit 的每日 nag 也不能依賴現行第 148-164 行區塊，因為該區塊只在 `GAP_JSON` 為空時執行。spec 必須指定 self-audit 在報告檢查與所有早退之前或之後的確切位置及 fail-open/exit 行為，並測 shell 接線。

查證：`governance/autonomous-loop.sh:22-27`（日報缺失早退）；`governance/autonomous-loop.sh:139-165`（gap 選擇及另一早退）；`governance/autonomous_loop/gap_select.py:16-18`（既有 pending 非遞迴）；`scripts/test_lumos.py`（沒有 autonomous-loop.sh 接線測試）。

## PRIOR-ART

已讀，無 finding。

## 測試（草）

### f7 — major

spec 段落：測試

引句:「⑥FAIL 鏈:worktree 修→複審 PASS→copy+戳+commit」

問題：十一條測試沒有覆蓋 f1/f2/f3/f5 的關鍵失敗面：主樹候選 dirty、派工後同檔被修改、初審與複審報告地址碰撞、sandbox/worktree 在正常/timeout/例外後確實移除、以及 copy 後 stamp/commit 失敗的恢復。現有正向鏈測試即使全綠，仍可在真實 dirty repo 覆寫使用者內容並累積臨時副本。

查證：`scripts/scenario_probe.py:80-110,210,230-240`（先例的清理缺陷）；`governance/autonomous-loop.sh:1-20`（排程在共享 repo 建立 scratch，現行以 shell exit 管生命週期）；spec 測試 §①–⑪未列上述案例。

## 實務隱患

### f8 — major

spec 段落：實務隱患「併發」

引句:「併發:週戳+循序派工,無共享寫。」

問題：宣稱不實。週帳、主樹候選檔、報告路徑與 pending 路徑全是共享寫；「單一程序內循序」不排除 cron 重疊、人工同時執行、前一日 900 秒×多 agent 尚未結束，或另一工作階段修改同篇。週帳 append 也沒有鎖或原子 reservation，兩個 runner 可同時讀到相同殘額、選同一候選並超額派工。需用 repo 級鎖或原子 claim，不能靠週帳與循序敘述宣稱無併發。

查證：`governance/autonomous-loop.sh:15-20`（固定日期共享輸出與 mktemp 僅保護 scratch，沒有全流程鎖）；`governance/autonomous-loop.sh:117-121`（既有週戳也是無鎖的 check-then-write）；`governance/autonomous_loop/gap_select.py:59-70`（選擇流程為讀後再 pop，非跨程序鎖定）。

## 審計修正紀錄

已讀，無 finding。

最嚴重 severity：blocker
