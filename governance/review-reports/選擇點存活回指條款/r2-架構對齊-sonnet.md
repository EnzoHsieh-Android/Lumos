severity: major

**第 1 問 分層與依賴方向:不對齊(有跨層)**

既有做法:`cmd_choice_kill`(`scripts/lumos:79361` 起)不碰隔離工作樹,也不直接跑測試。它只組好壞法,再呼叫 `cmd_guard_kill`(`scripts/lumos:79306`)。`_isolated_worktree`(`scripts/lumos:28461`)、基準快取 `baselines = {}`(`scripts/lumos:28474`)、`_kill_run_dir`、`mstate`、撞名判定與逐支量基準(`scripts/lumos:28498-28502`)全在 `cmd_guard_kill` 裡。連合併快篩量單支基準也是在它裡面做(`_kill_merge_base` / `_kill_merge_singles`,`scripts/lumos:29100` 一帶)。選擇點的選用機制一向包成物件交進去:`_KillMerge`(`scripts/lumos:28975`)、`hk`(`_KillHooks`)。

新設計在 choice-kill 這一層自建 `lumos-kill-` 隔離樹,自己逐支量基準,再把結果塞回 `cmd_guard_kill`。這樣上層越過下層,另做一份「建樹加量基準」的迴圈。基準的第五格「不確定」取自 `mstate["unsure"]`(`scripts/lumos:28502`),那是 `cmd_guard_kill` 自己那棵樹的修改時間追蹤。設計沒說上層量的基準怎麼填這格。快取鍵是 `_run_cmd_expand` 展開後的指令字串。覆蓋基準指令多帶 `--init-script`,鍵跟 `cmd_guard_kill` 組出的 `cmd` 對不上的處理設計也沒寫。

severity: major
blocking: 是
引句:「這些基準交給 `cmd_guard_kill` 的新選用參數 `baselines`」

**第 2 問 命名與錯誤處理:大致對齊,有三處不一致**

對齊的部分:
- 新 kind 用連字號(`reach-run`),跟 `blind-judge` / `choice-kill` 一致(`scripts/lumos:21040-21054` 的白名單)。
- 事件欄位用蛇底線(`new_sha`、`run_id`),跟既有一致。
- `--no-cov` 對應 `--no-merge`(`scripts/lumos:82901`)。
- 參數衝突回 rc2,跟既有 `say(...)` 擋下一致(`scripts/lumos:79109`)。
- `choice-layer` 當頂層指令,跟 `choice-points` / `choice-kill` / `situation-rule` 同族。
- 治理帳 (gate, kind) 白名單與讀取欄位白名單的補法,跟 `scripts/lumos:18458`、`scripts/lumos:18560` 同一套。

不一致的三處:

severity: minor
blocking: 否
引句:「照舊數 `attempt == 1`;換候選的壞法事件帶 `candidate`」

現行 gov 讀法是 `attempt == 1` 而且 `via == "run"`(`scripts/lumos:17962`)。新設計的 `via: "cov"` 存活事件不會被數進去,「照舊」不成立。殺掉率分母會悄悄變動。設計要寫明 `via: "cov"` 怎麼算。

severity: minor
blocking: 否
引句:「平台設定多一個選填的 `coverage`(布林或物件,穿過 `load_platforms` 帶進平台資料」

既有設定鍵要嘛是平台層的標量(`run_cmd`,`scripts/lumos:6445`、`scripts/lumos:6469`),要嘛是 `note_lint.gate` 這類字串。「布林或物件」是新形狀。`load_platforms` 對壞值的處理是 `raise ValueError`(`scripts/lumos:6458-6461`)。設計沒寫 `coverage` 型別不對時走哪一種(raise、提醒後預設關、還是 doctor 提醒)。

severity: minor
blocking: 否
引句:「外加 lumos 產生的 Gradle init script(開 `enableUnitTestCoverage`」

既有 init script 的產法是:常數文字 `_CHOICE_MERGE_INIT` 寫進 `wt.scratch`,用 `_choice_merge_init_write`(`scripts/lumos:29068`)寫入,寫不進去就印一行並降級。`--init-script` 由 `_choice_merge_cmd`(`scripts/lumos:28818`)用 `_cmd_arg_quote` 插入。結果目錄有 `_choice_merge_results_dir` 的 realpath 圍欄(`scripts/lumos:28830`)。新設計要動態產生(逐模組算類別資料夾、逐一登記報告任務)。它沒說是否沿用 scratch、寫檔失敗降級、參數引號、覆蓋資料檔的路徑圍欄,也沒說跟事件 init script 同時存在時怎麼並用。

**第 3 問 第二種做法:有三處**

severity: major
blocking: 是
引句:「第一次呼叫(沒帶 `--part`)把整份清單寫成一個清單檔 `.lumos/choice-layer/<清單編號>.json`」

既有分份有兩種,都不是這種:
- `code-loop blind-judge` 每次呼叫從治理帳與範圍重算,`--part n` 只是切片(`_cmd_codeloop_bj_template`,`scripts/lumos:76803-76808`)。檔頭明寫「不寫也不讀本機標記檔」(`scripts/lumos:76331-76334`),原因是標記檔蓋過帳、a/b 與 a__b 撞檔。
- `reread-prepare` 的項目檔放在 `_note_audit_work_dir`(`scripts/lumos:56728`)。那個目錄有符號連結拒用、自動寫 `.gitignore`、14 天清檔。

新設計是第三種:在 `.lumos/`(放進版控的設定目錄)寫有狀態的清單檔。`.gitignore` 沒涵蓋(`.gitignore` 只列特定的 `.lumos/*` 檔),也沒有符號連結防護與清理。判讀材料與記錄本來就是 blind-judge 加 reread 的混合體,應沿用其中一個。

severity: major
blocking: 否
引句:「每項 `quote` 10–200 個實字(`_real_chars`,NFC、空白壓成一個、全形半形引號統一後比對)」

既有引句正規化已有 `_quote_norm`(`scripts/lumos:37439`,註明「嚴禁第二份實作」)與 `_kt_sit_quote_norm`(`scripts/lumos:75356`)。後者就是情境題 `spec`/`quote` 欄、同樣 10 實字門檻的先例。新設計的「全形半形引號統一」是第三套正規化,沒說明為什麼不能沿用既有那一支。

severity: minor
blocking: 否
引句:「JaCoCo 報告的外部 DOCTYPE 宣告先從字串裡拿掉再交給它」

⚠ 這條判不準是不是「第二套讀 XML」,標 minor 交編排者。設計重用 `NoDtdTreeBuilder`(`scripts/test_quality.py:160`),只拒收點這件事一致。差異有三:
- 既有讀法走串流的 `junit()`(`scripts/test_quality.py:250`),有 `JUNIT_MAX_DEPTH=64`,並由 `_secev_junit_facts` 回拒收代碼。新設計直接建樹,沒提深度上限與代碼。
- 大小上限的常數另開 32 MiB(`_CHOICE_COV_FILE_MAX`),既有合併是 8 MiB / 64 MiB(`scripts/lumos:28763-28764`)。
- 先用字串剝掉 DOCTYPE,等於在拒收點之外另做一道前處理。

**第 4 問 落點:合理,有一處要補**

severity: minor
blocking: 否
引句:「現況寫進 [[Systems/規格閘]](choice-kill 的家)的選擇點那段」

先例對得上:`Systems/規格閘` 已經收了 choice-kill 的 WHY(`規格閘.md` 第 70、71 行)與 `選擇點變異加速` 的現況,所以主體寫進它是一致的。兩個落點節點都只管 `scripts/lumos` 一支檔,新增獨立節點也沒有檔可管,不另開是對的。

要補的是:`規格閘.md` 第 6 行 `responsibility` 只寫到「改動選擇點的語法樹掃描與每行挑壞法(choice-points)」,沒有 choice-kill,更沒有判讀記錄(`choice-layer`)與覆蓋基準。新設計又加判讀契約與無效壞法記憶,責任文字應該在同一次一併更新。這篇現在 232 行、20 行 KEY,要預期它再變大。

`Systems/guard-kill` 只補一句 `baselines` 參數,量很小。該節點有兩條 ★INVARIANT★(rc 優先序、`--json` 純度),`baselines` 不碰這兩條,沒有衝突。

不對齊共 8 條,其中 major 3 條
