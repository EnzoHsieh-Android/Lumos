severity: minor

回滾走得通。我在臨時 clone 裡實際走過〈回退〉的每一步,只有一個小缺口:「單一提交還原」的說法跟實際不符,而且整段還原會一併刪掉三行追加式帳目。

## Findings

1. 〈回退〉寫「單一提交還原即可」,但實際是 5 個提交,整段還原還會刪掉追加式帳目
severity: minor
blocking: 否
引句:「單一提交還原即可。只想關掉不還原程式時,把本 repo 設定的 `bound_tests.parallel` 拿掉或改成 1,行為就回到循序」
file: `docs/.governance-log.jsonl:最後 2 行`
file: `docs/.canary-log.jsonl:最後 1 行`
1. 在 3daa00a8 上,範圍是 `a701909c..HEAD`,共 5 個提交:c9bd21d2、5b05034f、d3ac862a、280192b7、3daa00a8。
2. 照字面只還原其中一個提交,會留下半套程式。我先試過只還原後 4 個、漏掉 c9bd21d2,結果程式不完整。
3. 我試過把 c9bd21d2 排在最前面一起還原,結果在 `scripts/lumos`、`scripts/test_lumos.py` 和 Systems/bound-tests-gate.md 三處衝突,要手動解。
4. 用 `git revert -n a701909c..HEAD`(新到舊)可以乾淨還原。
5. 但它同時刪掉:
   - canary-log 的 1 行 spec-gate 記帳(token SPEC-bf9681a6)。
   - governance-log 的 2 行 bound-tests green 記帳(commit a701909c)。
   - 這些是只增不減的帳。
6. 還原後 `lumos doctor` 仍是「0 issues」,也沒有殘留引用。計劃另寫的「還原後帳上 secs 會混著兩種值」,在整段還原時其實不成立,因為那兩行帶 `secs_kind` 的新帳已被刪。
7. 這不會擋住回退。要補的是回退步驟:寫清楚用 `git revert -n a701909c..HEAD`(新到舊),並說明帳行會被帶走。
歸因:未判定。這是工作流程的描述缺口,兩版之間沒有程式回歸。
- 查證命令:`git revert --no-edit -n a701909c..HEAD`,再看 `git diff --cached --stat`。
- 結果:10 個檔變動,含上述 3 行帳。

## 回滾逐步實測(在臨時 clone,3daa00a8 起)

| 步驟 | 實際發生什麼 |
|---|---|
| ① 設定改成 1 | `pitfalls --diff` 判 light。`-k parallel_repo_config` 2 passed。 |
| ① 設定整個拿掉 `bound_tests` | 判 light。`-k parallel_repo_config` 2 passed。 |
| ① 之後的閘行為 | 回到循序。記帳仍帶 `secs_kind: wall`,與計劃寫的一致。 |
| ② 整個還原(新到舊) | `pitfalls` 判 standard。`code-loop check` 顯示 OK,受波及合約測試 59 支全綠(179.9 秒,循序)。 |
| ② 還原後的殘留 | 全 repo 搜不到 `bound_tests.parallel`、`secs_kind` 或計劃檔名。`doctor` 通過。 |
| 全套相關測試 | 在 3daa00a8 上 `-k bound_tests` 142 passed、0 failed。 |

## 新舊版本混用
- 舊版程式(a701909c)配新設定與新帳,`gov --stats` 正常、無例外,新鍵與 `secs_kind` 被忽略。
- 消費專案用舊工具配新設定同樣被忽略。
- 閘自己壞掉時,逃生路是 `--skip-bound-tests --note` 與 `LUMOS_SKIP_BOUND_TESTS=1`。
- 這個跳過動作在讀取 parallel 設定之前就返回,所以不受新程式影響。
- 並行出錯時例外往外丟,和循序開不了程序時的行為一致。

## 已驗與未驗
- 已驗:
  - 設定改 1 與拿掉兩種停用法。
  - 整段還原。
  - 新舊混用。
  - 逃生路。
  - 中斷時留下孤兒子程序的行為:`_kill_run` 在循序時也沒有清理,計劃寫的「跟原本一樣」屬實。
- 未驗:
  - `t_bound_tests_parallel_config_values` 單支要 62.8 秒,離 180 秒上限只有 3 倍餘裕,測試工具印了警示。它靠睡眠計時,負載影響小,我給不出會失敗的具體場景,所以不列 finding。
  - 代碼審通過後的帳本提交與這 5 個提交的互動:本 clone 裡沒有卷證,未驗。

## 圖譜鏡頭(固定席逐條)
- **guard-kill、lumos-cli-read、lumos-cli-lifecycle:** 這份 diff 沒碰 guard kill 的 rc 優先序或 JSON 輸出,也沒碰 search 濾網與 re-inject sentinel。`_kill_run` 只被呼叫、沒被改。不破壞。
- **測試假綠形態:**
  - 新增的修補類測試都有前置斷言證明現場成立。
  - 例如 secs_monotonic 先斷言閘有跑到、wall_time 先斷言兩篇都綁到、wait_is_quiet 先斷言牆上時間約 4 秒。
  - repo_config_valid 本來就不是還原翻紅釘。
  - 不破壞。
- **bound-tests-gate:**
  - 紅、懸空、偽證據與證不出跑過仍然擋;沒設指令或沒綁定測試仍是不擋但寫帳。
  - `-k bound_tests` 142 項全綠。
  - 不破壞。
  - 唯一的變動是 secs 語意與 `secs_kind` 欄位,筆記已補。
- **loop-convergence-recording、pitfalls-code-loop、design-loop:** 不在這份 diff 的改動路徑上。
- **其餘只列名的節點:** 非逐條對照,本席不判。

總結:最高等級 minor
