---
type: project
status: doing
created: 2026-08-22
updated: 2026-08-22
tags:
  - type/project
  - status/doing
---
# 受波及合約測試真跑閘_計劃

> 白話:改到相依功能時,工具現在只會「點名」那些功能綁的測試,跑不跑靠編排者自律。Enzo 2026-08-22 裁:被點名的要當場跑完才能往下——把它做成閘:`lumos code-loop pass` 留痕前,先把波及節點上綁的合約測試真跑一遍,一條紅就拒絕留痕(pre-push 與 CI 認留痕,所以等於推不上去)。

## 需求
1. `lumos code-loop pass` 留痕前:算 `impact --diff <merge-base..HEAD>` 的固定席,收集這些節點 ★INVARIANT★ 行上的 `[test:…]` 方法名(含平台前綴),用 `.lumos/config.json` 的 `run_cmd`(多平台 `platforms.X.run_cmd` / 單平台 `test.run_cmd`)逐條真跑。
2. 任一條紅或超時 → 不寫留痕、rc1,訊息列「哪篇合約、哪支測試、尾段輸出」。全綠 → 留痕 note 自動附「受波及合約測試 N 條綠」。
3. 沒 run_cmd / 沒固定席 / 固定席沒綁測試 → 不擋,印一行提醒(第一天就擋死全天下專案是反效果)。
4. `--skip-bound-tests` 逃生門:跳過真跑但 note 強制附理由,並進治理帳 kind=bound-tests-skipped(被統計,同 skip 哲學)。
5. `code-loop skip` 不跑(本來就是刻意不審)。

## 設計
- 重用:`_kill_run(cmd, cwd, timeout)`(rc/tail/elapsed/timed_out)、`load_platforms`(run_cmd、root、method_regex)、`strip_test_refs` 同家族的 `[test:]` 解析、`cmd_impact_diff(..., as_json)` 的 results 取 `contract` 非空的 pinned 節點。
- 新函式 `_bound_tests_for_diff(repo_root, diff_range) -> [(node, method, platform)]` 與 `_run_bound_tests(repo_root, items) -> [(node, method, rc, tail, secs)]`;`cmd_code_loop` pass 分支接上。
- 超時:每支 max(60s, 5×baseline?) —— 沒 baseline,固定 300s,`LUMOS_BOUND_TEST_TIMEOUT` 可調;超時算紅(沒跑完=沒驗)。
- 方法名重驗 IDENT_RE / Kotlin 反引號白名單 + shlex.quote(同 kill,`[test:]` 可被手改不可信)。
- 去重:同方法名只跑一次;whole-suite run_cmd(無 {method})只跑一次並 note 標 whole-suite。
- 帳:治理帳 gate=code-loop kind=bound-tests-red / bound-tests-green(節點=被擋的合約),gov --stats 可見。

## 非目標
- 不跑相依功能的「整套」測試,只跑合約綁定的;綁得少守得少(doctor 裸合約提醒負責逼綁)。
- 不接 testmap affected(檔案級,對單檔大 repo 無意義;見 8/19 調研)。
- 不動 pre-push 本身(它認留痕即可)。

PRIOR-ART: 既有 kill 的 run_cmd 執行面 + impact 固定席 + code-loop 留痕三個機制接線,零新依賴;業界對應=「affected tests」(Bazel/Nx 的 affected 圖),但那是檔案級依賴圖,我們用的是圖譜合約級,借概念不借實作。

## 風險
- run_cmd 有副作用的測試(真 DB)會在 pass 時被跑——與 kill 同樣的 hermetic 警語,寫進 commands/06。
- 固定席對單體大檔(scripts/lumos)一次 30+ 節點、綁定測試可能數十支 → pass 變慢;用去重與超時兜,並印總耗時。回頭看條件:三次 pass 超過 5 分鐘就要加「只跑直接相依(direct)」的縮圈選項。
