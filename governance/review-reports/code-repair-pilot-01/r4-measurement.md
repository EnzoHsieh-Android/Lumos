severity: major

R4-M1 — unknown 在低有效率批次仍污染計分與歷史分母

severity: major  
blocking: true  
引句:「n = total if inconclusive else len(valid)」  
file: `scripts/scenario_probe.py:800`

現象：單一 unknown 結果同時出現在 `excluded`，卻仍產生 `scored=1`、總結 `0/1`，且 `history_record.total=1`。歷史資料又沒有保存 `inconclusive`，後續只讀 passed/total 的消費者會把儀器例外算成模型失敗。`scripts/test_lumos.py:37003` 只斷言 `excluded`、`failed` 與混合批次分母，沒有驗單一 unknown 的 `scored/history total` 必須為零。

重現：

```text
summarize_results([unknown])
→ passed=0
→ scored=1
→ excluded=["v04"]
→ failed=[]
→ inconclusive=true
→ history_record.total=1
```

本席以 `python3 -B` 純記憶體重現；unknown 加一個有效成功時則為正確的 `1/1`。

判準：對外成績、JSON 與歷史的分母只能是有效場次。零有效場應保存 `0/0 + inconclusive=true`；自主迴圈應直接依 `inconclusive` 告警，而不是藉由把排除樣本塞回分母製造 `p != n`。歷史紀錄也必須保存 inconclusive，避免之後被算成 0% 通過率。

歸因：舊漏報；分母退回整批早於 r4，本輪把更多畸形事件改成 unknown，卻沒有補齊其對外分母與歷史語意。不是本輪新回歸，但 r4 的「unknown 排除」修復仍不完整。

R4-M2 — Git local include 未納入隔離測試，remote／hook 安全結論尚不能成立

severity: major  
blocking: true  
引句:「subprocess.run(["git", "remote", "remove", name], cwd=str(work), env=genv)」  
file: `scripts/scenario_probe.py:544`

現象：r4 測試涵蓋 command/global/system 的 `GIT_CONFIG_*` 注入，但來源 `.git/config` 會被原樣複製；其中的 `[include] path=/副本外/injected.config` 沒有被停用或檢查來源。若 include 提供 remote 或較晚生效的 `core.hooksPath`：

- `git remote remove` 的退出碼未檢查；
- 清理後沒有重驗 remote 必須為空；
- 設定 hook 後沒有重驗有效值必須等於副本專用 hooks；
- 現有 `t_probe_repair4_git_config` 因此無法證明此輸入安全。

父代理 filesystem 重現：

1. 建立臨時來源 repo 與本機 bare repo。
2. 來源 local config 先設定一個 `core.hooksPath`，再於檔尾加入外部 `include.path`。
3. 外部設定檔宣告 `remote.escape.url=<bare>` 與空 hooks 目錄。
4. 呼叫 `make_sandbox(src)`。
5. 在副本檢查 `git remote`、`git config --get core.hooksPath`，再執行只對本機 bare 的 `git push --dry-run escape …`。
6. 同時比對來源與外部設定逐位元不變。

判準：建立副本完成後，有效 remote 必須為空、有效 hooksPath 必須恰為 `work.parent/hooks`；任何副本外的 config origin 應拒絕或被可靠隔離。上述 dry-run 必須被防推 hook 擋下，拒絕路徑必須清除副本且來源 byte-equal。

歸因：測試漏口確定；實際 dry-run 結果因本席禁止建立 filesystem fixture 而未判定。若父代理重現可推，屬既有隔離漏報而非 r4 新回歸，並應升級為 blocker。

覆蓋核對：

- 已知三組修補具有同例紅綠：舊版 28 過／17 失敗，現碼 50 過／0 失敗。
- unknown 的正證據優先、完整未讀仍算有效失敗已有測試。
- plain clone、相對 gitfile 正常路徑有涵蓋。
- absolute gitfile、core.worktree、external commondir、refs symlink 的拒絕、來源不變及拒絕後清理有涵蓋。
- 專用 source sandbox 的成功清理、runner 失敗清理、清理失敗 fatal 停批已有涵蓋。
- 本輪回歸：未確認。
- 未判定：M2 的臨時 repo 重現、真模型串流與部署週抽。
- `/tmp/r4-test-layers.txt` 與 repo 內同名鏡頭均為空檔。
- 完整讀過 `r4-code.patch`、`r4-context.patch`、`r4-delta.patch`；`r4-archive-measurement.patch` 僅作歷史量測證據。完整 snapshot SHA256 已核對為 `2e8dae39bcabc1d4793e43e096995d79e84bbcf4edb9c83dea009bdfeb0c2734`。
- 未讀其他 r4 席報告，未修改任何檔案，未執行網路、真 push 或 filesystem 測試。