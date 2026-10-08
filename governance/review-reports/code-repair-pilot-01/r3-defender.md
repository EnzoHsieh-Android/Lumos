## F1 — 缺少事件 ID 被誤判成確定未讀

refute-verdict: agree

severity: major

blocking: 是

引句:「已發出支援呼叫卻缺結果、格式無法識別或未準備標記時應記儀器例外、不進有效分母」

file: `docs/lumos-toolchain-knowledge/Projects/探針讀碼結果證據_計劃.md:33`

file: `scripts/scenario_probe.py:115`

file: `scripts/scenario_probe.py:178`

evidence: `item.started` 或 `item.updated` 的 `command_execution` 缺字串 ID 時，115–118 行未設 `unknown`；遇到 `turn.completed` 後，178 行回傳 `absent`。唯讀函式重現兩者皆為 `no-id=absent`，相同事件加入 ID 則為 `unknown`。

最小重現:

```json
{"type":"item.started","item":{"type":"command_execution","command":"cat scripts/lumos"}}
{"type":"turn.completed"}
```

結果：`source_evidence=absent`，進入有效分母並記失敗；違反 S3，major 判準沒有過度擴張，不能降級。

concern: finding 若把缺口分類為「本次修復引入」便過度擴張。`/tmp/r3-missing-id-before-after.json` 顯示相同缺 ID 串流在 `1c91755a` 與 `4a60b231` 均為 `passed=false、scored=1、inconclusive=false`；舊版沒有 `source_evidence` API，沒有修前正常、修後失敗的證據。來源應分類為「原有漏看／新 S3 修補不完整」，不是 repair-introduced regression。

## R3-B1 — Git command-scope config 可繞過副本隔離

refute-verdict: agree

severity: major

blocking: 是

引句:「當呼叫端環境含Git定位變數時，兩runner與所有副本Git操作應使用既有_git_env清洗，外部暫存repo的設定與檔案應不變。」

file: `docs/lumos-toolchain-knowledge/Projects/探針讀碼結果證據_計劃.md:35`

file: `scripts/scenario_probe.py:385`

file: `scripts/scenario_probe.py:617`

file: `scripts/scenario_probe.py:692`

evidence: `_git_env()` 僅移除六個 Git 路徑變數，保留 `GIT_CONFIG_COUNT/KEY/VALUE`；兩個 runner 又把該環境交給模型程序。唯讀解析確認注入後 `git remote -v` 出現額外 remote，`git config --get core.hooksPath` 回傳攻擊者路徑。

最小重現:

```sh
GIT_CONFIG_COUNT=2
GIT_CONFIG_KEY_0=remote.r3escape.url
GIT_CONFIG_VALUE_0=<本機 bare repo>
GIT_CONFIG_KEY_1=core.hooksPath
GIT_CONFIG_VALUE_1=/tmp/r3-no-hooks
```

`/tmp/r3-git-config-repro.json` 在 `1c91755a`、`4a60b231` 均顯示：控制組 `push --dry-run` rc=1，注入組及具名 remote rc=0，且持久設定仍無 remote。這證明 command-scope config 同時補回 remote 並跳過硬擋 hook，major 不能降級。

concern: 重現刻意未執行真 push 或網路，bare repo 仍空，因此證據不足以升為 blocker；維持 major 恰當。

總結最嚴重 severity: major；blocking: 2 條。
