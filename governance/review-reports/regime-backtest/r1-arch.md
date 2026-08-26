# 審查報告:改制回測_計劃 r1-snapshot(架構對齊席)

驗證:行號已確認。

### arch-f1
**severity: major(第二種做法)**

引句:「判定重算★不寫任何帳★(唯讀)」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:29`

說明:`loop replay` 重算的是同一套 `--disposal` 四合取判定,但既有 `cmd_loop_status`/`cmd_loop_next` 家族裡,「算出 PASS」跟「寫 `_loop_gov_mark`」從未分離過——`scripts/lumos:4808`(`--disposal` 前身的 gate 分支)、`scripts/lumos:5350`(`loop next`「唯讀指針,不 spawn agent」也在收斂時落帳)、`scripts/lumos:10325`(`disposal gate PASS` 落帳)全部在判定為真的當下無條件寫帳,11 個 `_loop_gov_mark` 呼叫點沒有一個是「只算不寫」的先例。spec 沒說 replay 到底是重用 `cmd_loop_status`(需要一個從沒出現過的 no-mark 參數)還是另外重寫一份判定算式(等於自己再刻一份可能跟正式邏輯漂移的算術,正好違背 replay 想證明的「判定邏輯沒被改壞」)。兩條路都是對既有「算=寫」耦合的新分支,任一條都該在 spec 裡挑明,不能隱在一句「唯讀」帶過。

### arch-f2
**severity: major(第二種做法)**

引句:「為 08-25 後全部 d5 迴圈(含本日十餘個)凍結首批」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:30`

說明:`governance/golden/` 現有 30 包,`find governance/golden -maxdepth 2 -type f` 顯示每一包內容 100% 是 `spec.md`/`spec-ref.txt` + `findings.md` 的散文對——沒有一個 JSON。`verdict.json` 是這個目錄第一個機器格式檔,而且服務的是完全不同的機制:`scripts/test_lumos.py:16965` 明文定義「golden/ 是凍結語料(過去 loop 的 spec 快照,replay 校準用)」,其中「replay 校準」指的是 `docs/lumos-toolchain-knowledge/Verification/2026-07-16_replay校準baseline_v0.md` 那種——拿凍結前的 spec v1、釘 worktree、真的派 LLM 審計員重審,測模型抓不抓得到已知 finding 的**校準實驗**;跟 S1/S2 提的「讀凍結帳算術重算 PASS/FAIL」是兩件事(一個測 LLM 判斷力、一個測程式碼決定論)。把「gate 逐輪四合取結果」這種機械回歸驗證的產物,套進一個定義上是「LLM 校準用散文快照」的目錄,是幫既有目錄加了第二種、語意不相容的用途,而不是延伸既有格式。

### arch-f3
**severity: major(第二種做法)**

引句:「新舊制同料對照(一次性分析,產物入 golden/)」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:31`

說明:兩層問題。結構上,`find governance/golden -mindepth 1 -maxdepth 1 -type f` 回傳 0——30 個項目全部是「以 loop id 命名的資料夾」,golden/ 根目錄從沒有裸檔;S3 卻要直接寫一個裸檔 `governance/golden/regime-comparison-2026-08.md`,不落在任何 id 資料夾底下。語意上,`scripts/test_lumos.py:16965` 把 golden/ 定義成「過去 loop 的 spec 快照」,是特定 loop 收斂時的凍結產物(design-loop FLOW 本身寫「收斂+天花板提醒+golden凍結」),不是泛用分析報告倉庫。而「拿兩套機制對同一批歷史料重算、產對照表、結論折回 Systems 節點」這件事,本專案已經有現成、正在用的容器——`docs/lumos-toolchain-knowledge/Verification/2026-07-16_replay校準baseline_v0.md` 就是同一種形狀(比較表+結論折回 `[[Projects/loop數據收集_計劃]]`),而且走圖譜規範(`valid_under`/`revalidate_when` frontmatter)。S3 自己都寫「結論寫回 `[[Systems/design-loop]]`」用的是圖譜語法,產出本體卻要放圖譜外的裸檔——這是替「一次性對照分析該放哪」立了第二套規則,跟 CLAUDE.md 開頭「圖譜是唯一來源」的鐵則也對不上。

### arch-f4
**severity: minor(出入)**

引句:「已有 30 包快照素材與單次重放先例」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:19`

說明:PRIOR-ART 把 07-16 那次重放先例講成「缺的只是 runner 與排程」,暗示現在只是把既有機制自動化。但 07-16 的「重放」是釘 git worktree、真的跑 LLM 審計員去測模型能不能重新挖到已知 finding(重放對象=LLM 判斷),跟 S1 提的「唯讀重算帳本裡的四合取算術」(重放對象=確定性算式)不是同一件事,也不是「加個 runner 就補齊」的關係——後者要建的其實是這個 repo 目前完全沒有的東西:一個真正的 CLI/gate 輸出 golden 比對基礎設施(`t_gov_stats_rc` 那條測試本身就寫過「本 repo 無 CLI golden/snapshot 基礎設施」,`scripts/test_lumos.py:4226-4234` 目前唯一的變通做法是同一測試內兩次即時執行結果互比,連存檔比對都沒做過)。PRIOR-ART 的「借用既有做法」框架因此把新機制的新穎度講小了,值得補一句講清楚 07-16 precedent 跟本案 replay 語意不同、不是同一機制的延伸。

### arch-f5
**severity: minor(出入)**

引句:「復用既有 line_notify.send 素警示通道(build_alert,不套模板)」

佐證:file: `governance/review-reports/regime-backtest/r1-snapshot.md:41`

說明:S4 明講「比照考卷 run_exam 形狀」,但 `governance/autonomous-loop.sh` 裡實際的 `run_exam`/`run_probe`/`run_nags` 三支週期任務——即 S4 聲稱要模仿的那個家族——喊人時全部用 `line_notify.build_message('labeling-refresh'/'scenario-probe'/'gov-nags', MSG, None)`(`autonomous-loop.sh:173,214,232`),沒有一支用 `build_alert`。`build_alert` 在這支腳本裡只出現兩處(`autonomous-loop.sh:74,103`),而且 `line_notify.py:8-10` 的 docstring 明講它是留給「連兩天管線死」這種結構性故障用的素警示,理由是套上 `build_message` 的「好消息標頭」反而會被當正常通知忽略。loop 判定漂移是否真的跟「管線死」同一嚴重度,見仁見智,但 spec 一邊宣稱「照抄 run_exam 形狀」一邊在通知模板這個具體細節上選了 run_exam 家族從不用的那支函式,這個自我宣稱的對齊沒有站穩,該在 spec 裡講清楚是刻意升級警示等級、還是筆誤。

## 對齊良好的面

- **`loop replay` 掛進 `loop` 子命令家族是對的位置**:既有 `loop` 家族(`status`/`compress`/`verify-progress`/`rewrite`/`next`/`canary-stats`/`capture-counts`,`scripts/lumos:15505-15556`)裡本來就混著唯讀/advisory 成員(`verify-progress`「獨立進度驗證器:直讀帳只吃結構欄位」、`next`「唯讀指針,不 spawn agent」)跟會落帳的成員,`replay` 加進同一個 subparsers 底下沒有另立新的頂層命令,是延伸既有分類、不是自建平行體系。
- **`PRIOR-ART:` 這一行本身就是照規矩來的**:CLAUDE.md 要求「設計動筆前先問世界...一行 `PRIOR-ART:` 記進計劃筆記」,r1-snapshot.md 第 19 行確實這麼做了,且借用「golden master testing」「event sourcing replay」這兩個外部教科書概念是正當、常見的自建理由(即便對本案既有先例的引用有 f4 那個出入)。
- **「帳不可撤」邊界守得住**:第 33 行「golden 檔=判定快照非帳(帳不可撤原則不變)」跟 `scripts/test_lumos.py:16965-16969` 把 `golden/`、`external-reviews/`、`l4-audit/`、`review-reports/`、`audits/` 全部歸為「同性質:歷史不得回改」的既有規則一致,S1~S4 沒有任何一條打算回改既有帳列或報告檔。
- **rc 語意跟既有 `--disposal` 分支一致**:`cmd_loop_status` 的 `--disposal` 路徑本來就用 rc2 標結構性/用法錯誤(如缺 `--spec`)、rc0 標 PASS;S1「異=rc1 白話列差異」把「有差異但非用法錯誤」放在 rc1,跟既有「rc0 過/rc1 判定不過/rc2 用法或結構錯」三層語意對得上,沒有另立一套 exit code 慣例。
