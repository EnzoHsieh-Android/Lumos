# 第3輪父代理重現方法與證據界線

被審程式固定4a60b231，對照1c91755a。程式以git show載入獨立ModuleType，不checkout共享工作目錄；所有Git可寫操作只在TemporaryDirectory自建fixture，沒有真模型、網路或真push。以下都是本機實驗，不能推為部署狀態。

## 缺ID

對兩版各自v04情境，mock subprocess.run回傳exit0與下列相同JSONL，呼叫run_one_codex再summarize_results。新版另給當場source_token；舊版沒有此參數。把item.started改成item.updated再跑一次。

```json
{"type":"item.started","item":{"type":"command_execution","command":"cat scripts/lumos"}}
{"type":"item.completed","item":{"type":"agent_message","text":"這是帳本檔案白名單"}}
{"type":"turn.completed"}
```

預期判準：不完整支援工具紀錄不得進有效分母。實際兩版均scored1、inconclusive false；新版source_evidence absent。控制組在第一事件加id=x而仍缺完成事件，新版unknown。輸出r3-missing-id-before-after.json及r3-missing-id-repro.json。

## Git設定注入

各版建立獨立temp普通repo、一筆fixture commit、本機空bare repo與空hooks目錄。普通repo配置pre-push exit1。控制組以清洗後环境執行 `git -C <temp> push --dry-run <local-bare> HEAD:refs/heads/probe`，rc1。然後環境加下列五個鍵，經該版_git_env，再跑同dry-run及以r3escape為目標的dry-run，兩者rc0。

```text
GIT_CONFIG_COUNT=2
GIT_CONFIG_KEY_0=remote.r3escape.url
GIT_CONFIG_VALUE_0=<local-bare>
GIT_CONFIG_KEY_1=core.hooksPath
GIT_CONFIG_VALUE_1=<empty-hooks>
```

驗bare仍空、沒有refs；未做非dry-run push。git remote -v可見注入remote，但git remote get-url返回2，不能以後者否定實際push解析。輸出r3-git-config-repro.json。

## Git來源內絕對路徑

各版獨立temp/src，關閉全域/system設定以排除使用者設定影響。`git -C <src> init --separate-git-dir <src>/.hidden-git .`，寫x、提交base、設hooksPath=/dev/null、加入本機sentinel remote。記錄remote/hooksPath/HEAD，再呼叫該版make_sandbox(src)。

來源gitdir原本位於來源內；複製後用git rev-parse --absolute-git-dir查副本與來源相同。再讀來源remote/hooksPath/HEAD，兩版皆remote清空、hooks變成副本臨時hooks、HEAD改變。刪除副本與temp來源。完整數值r3-separate-gitdir-repro.json；不觸及真專案。

## 完整批次入口

用真make_sandbox、真source注入、真Git與清理，替換外部CLI為回傳合法JSONL的fixture。兩家各main跑v04兩次：2/2，副本2個、乾淨開始、全部移除、來源不變、結果不留標記。輸出r3-entry-verification.json。這驗主流程接線，未驗真CLI輸出/模型行為或部署。

## 已有自動測試

`python3.14 scripts/test_lumos.py -k probe_`：157 passed/0 failed（r3-regression.txt）；原第二輪審查席獨立 `-k source_probe`：59 passed/0 failed（r3-original-acceptance.md）。新發現不在這些測試覆盖內，綠燈不代表三個反例已修。被審程式於收齊後未改，未重跑無新變動的全套。
