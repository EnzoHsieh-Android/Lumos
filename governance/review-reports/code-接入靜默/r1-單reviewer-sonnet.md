severity: blocker

### f1 C#/Node-Jest 骨架 run_cmd 必被冒煙測試判不可信
severity: blocker
blocking: 是
file: `scripts/lumos:13296`
引句:「dotnet test --filter FullyQualifiedName~{method}」
實測 dotnet 9.0.117 對不存在的測試名跑 `dotnet test --filter FullyQualifiedName~<probe>` 仍回 rc=0(印「No test matches…」但仍 Passed!),jest 29 的 `-t <probe>` 同樣回 rc=0(「1 skipped」)——這兩支正是 `_STACK_GUESS`/`_SKELETON_RUN_CMD` 替 C# 與 TS/JS 專案(9 種副檔名裡的 4 種)產出的預設骨架。用 in-process 呼叫 `_bound_tests_filter_probe` 對這兩支真實指令跑,回傳皆為 `(False, …)`,代表 `lumos init` 剛猜出的骨架不改一字,合約測試閘就永遠卡在 unfilterable、拿不到真正的綠。

### f2 unfilterable 從沒有真的讓 pre-push 擋下來
severity: blocker
blocking: 是
file: `scripts/lumos:22033`
引句:「elif st == "unfilterable":」
全檔搜尋 `unfilterable` 只出現在產生它的 `_bound_tests_check` 與印訊息的 `cmd_bound_tests` 兩處;真正決定 pre-push blocked=True 的 `_codeloop_guard_verdict`(`scripts/lumos:22033`、`scripts/lumos:22064`)只認 `status == "red"`,從未檢查 unfilterable。xcodebuild「跑 0 支仍回 0」那種情況,現在只是把訊息從「4 支全綠」換成「提醒:沒跑」印到 stderr,push 照樣不擋——跟這批派工詞背景欄「★假綠改成擋★」的宣稱不符。

### f3 S3 對 symbol_profile 的警告整類被 out[:8] 吃掉
severity: major
blocking: 是
file: `scripts/lumos:13343`
引句:「return out[:8]」
用 9 種 `_STACK_GUESS` 副檔名各建 4 個檔實測,`_profile_stack_mismatch` 該回 8 條 test_profile 訊息加 6 條 symbol_profile 訊息共 14 條,實際回傳只有 8 條、且全部是 test_profile 那組,symbol_profile 的 6 條整類消失。`run_doctor` 用 `_soft_list(_mismatch, f"有 {len(_mismatch)} 項…")` 印,但 `_mismatch` 進來前已被裁到 8,`_soft_list` 自己「還有 N 篇」的截斷提示(同一支 doctor 裡 S1/S2 都有這個提示)永遠不會觸發,header 照樣印「有 8 項」,看不出還有 symbol_profile 的問題沒講。

### f4 _profile_stack_mismatch 與 _init_config_skeleton 的 skip 名單不同步
severity: major
blocking: 否
file: `scripts/lumos:13314`
引句:「"docs", "governance", "scripts"}」
`_profile_stack_mismatch`(13314 行)排除 `scripts`,`_init_config_skeleton`(13357 行)沒有排除——若一個 repo 的 `scripts/` 底下堆了另一種語言的較多檔案,init 猜骨架會被 `scripts/` 帶偏,doctor 驗證卻不算這些檔案,兩支函式對同一個專案可以吐出不同答案。這正好是這次要修的「猜錯沒人知道」的鏡像:骨架剛猜完,S3 立刻可能對不上或漏掉。

### f5 rglob 對 skip 名單完全沒有剪枝效果
severity: major
blocking: 否
file: `scripts/lumos:13315`
引句:「root.rglob("*")」
實測在只有 `node_modules/` 裝 2000 個檔的目錄跑 `Path(d).rglob("*")` 再用 skip 名單過濾,rglob 仍把 `node_modules` 底下全部 2000+1 個項目走過一次才被丟掉——skip 名單只是「事後丟棄」,對它想排除的正是最大的那幾個目錄(node_modules/Pods/DerivedData)完全沒省到掃描成本。`_profile_stack_mismatch` 掛在每次 `lumos doctor`(提醒用、常跑),大型專案這段會隨依賴目錄大小線性變慢卻查不出理由。

### f6 bound-filter 快取沒套用專案自己的私有目錄信任檢查
severity: major
blocking: 是
file: `scripts/lumos:21191`
引句:「".cache" / "lumos" / "bound-filter"」
同一個 `~/.cache/lumos/` 底下的鄰居 `dispatch-lens` 快取寫入前一定呼叫 `_trusted_private_dir`(`scripts/lumos:19940`),`_lens_cache_write` 的 docstring 寫明理由:「目錄若被換成指向別處的 symlink,就會把別人的目錄權限改掉……現在兩邊都走同一支」——這正是 2026-09-06 全 repo 審視 #6 修過的同一種漂移。新的 `_bound_tests_filter_probe`(21157 行起)只有 `mkdir` 加 `_write_lf`,沒呼叫 `_trusted_private_dir`,也沒查 uid/群組可寫性,是同一種漂移第三次發生。

### f7 冒煙測試只證明「認得出完全不存在」,證不了「精準只選中那一支」
severity: major
blocking: 否
file: `scripts/lumos:13297`
引句:「python3 -m pytest -k {method}」
實測 `pytest -k test_pay` 會用子字串比對選中並跑 `test_pay_extra_unrelated`(不是精準比對 `test_pay`),該測試若碰巧通過,閘照樣報綠,但真正該跑的 `test_pay` 從沒執行過。冒煙測試探針名是全域唯一亂碼(`lumosProbeNoSuchTest9f3c`),不會撞到任何子字串重疊,因此這條指令仍被判「可信」,擋不住「合約 `[test:]` 名字打錯字或跟別的測試同字首」這種假綠。

### f8 bound-filter 快取沒有 TTL、也沒有版本欄位
severity: major
blocking: 否
file: `scripts/lumos:21172`
引句:「realpath(str(root))}|{run_cmd}」
同檔案 `_lens_cache_path` 的 key 明寫「帶 schema 版本:v1.1 舊快取自然 miss」、讀取端 `_lens_cache_read` 也吃 `ttl_sec`,而 `_bound_tests_filter_probe` 的 key 只有 root 與 run_cmd 文字兩項、永久有效。專案之後在 jest.config.js 加 `passWithNoTests: true`,或升級 SDK 修掉「filter 沒對到也回 0」的行為,run_cmd 文字都不會變,快取永遠不重算——一次判定「可信」終身有效,即使背後行為已經反過來變得不可信也是。

### f9 猜不到的技術棧:骨架寫空字串,S3 也永遠抓不到
severity: major
blocking: 否
file: `scripts/lumos:13371`
引句:「"test_profile": "", "symbol_profile": "", "test": {"run_cmd": ""}}」
用 20 個 `.rs` 檔實測:`_init_config_skeleton` 產出空字串骨架後,`load_test_profile` 因 `cfg.get("test_profile") or "csharp-xunit"`(`scripts/lumos:3373`)靜默退回 csharp-xunit 預設,而 `_profile_stack_mismatch` 的計數只認 `_STACK_GUESS` 那 9 種副檔名,對 20 個 `.rs` 檔仍回空 list、不出聲。跟這批要修的「非 C# 專案第一天起兩個關鍵設定都錯而且沒有任何提示」是同一個症狀,只是換到清單外的任何語言就完全沒解掉。

---

**其餘鏡頭速記(非獨立 finding):**
- 鏡頭 6(零覆蓋訊息語意):`_bound_tests_for_diff` 把 `_vault_in` 檢查提前,vault 存在但 diff range 錯的路徑(exception 分支)未被改動,行為不變;唯一改變是「vault 不存在」時原本可能落到 diff-unavailable 或 no-pins 的情況統一變 no-vault,是設計意圖內的修正,判「不影響」。
- 鏡頭 8(pitfalls manifest):`r1-pitfalls.txt` 0 條 claim,略。
- 鏡頭 9(圖譜):`lumos impact --diff HEAD~1..HEAD` 命中 22 個固定席,直接相關且逐字核對過合約行的只有 `Systems/bound-tests-gate.md`(見 f2——那條 ★INVARIANT★ 只講「紅/懸空/fake/不合法→blocked=True」,完全沒提 unfilterable 這個新狀態,而它實際上落在「不擋」那側,與這批診斷背景欄的敘述有落差)。其餘固定席(canary-audit、guard-kill、slim-install/uninstall/一行安裝、授權與歸屬、測試假綠形態、lumos-cli-read/lifecycle、reversibility-governance-ledger、design-loop、pitfalls-code-loop、loop-convergence-recording、check-t-sentinel、core-invariant-baseline、doctor-irreversible-hint、lumos-deinit、check-r-guard、cochange-guard、lumos-refcheck、judge-severity-gate)只是因為同檔 `scripts/lumos` 的 hop1 關聯被排進來,這次 diff 沒有碰到它們各自的合約範圍,判「不影響」。

最嚴重 severity: blocker,blocking 條數 4
