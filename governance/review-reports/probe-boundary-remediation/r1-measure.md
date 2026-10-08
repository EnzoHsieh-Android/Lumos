severity: major

審材：`r1-snapshot.patch`。

F1
severity: major
blocking: 是
引句:「final_attempt = sc_idx == len(scs) - 1 and k == a.runs」
file: `scripts/scenario_probe.py:1043`
具體輸入→路徑→錯誤：`--keep` 跑「普通題→讀碼題」；普通題先被清除，最後讀碼題因有 token 也不保留，違反 S4「保留最後一個普通題副本」。
最小重現：臨時 Git repo，兩題 runner 均成功，第二題帶 `source_probe`。輸出：`rc=0`；`exists_after=[('ordinary', False), ('source', False)]`；`retained_notice=[]`。

F2
severity: major
blocking: 是
引句:「if res.get("limit_hit") and waited < a.wait_on_limit:」
file: `scripts/scenario_probe.py:1075`
具體輸入→路徑→錯誤：同一題第一次 `limit_hit`、第二次成功；第一次的逐場時間在 `continue` 前未保存，只有批次總數包含它，違反 S7 的每次／批次時間紀錄。
最小重現：runner 每次耗時約 0.06 秒，依序回傳用量上限與成功，使用 `--wait-on-limit 300`。輸出：`runner_calls=2 result_rows=1`；`batch_model_secs=0.134 saved_result_model_secs=[0.065]`；`excluded=[] valid_total=1`。

F3
severity: minor
blocking: 否
引句:「raise mod.SourceProbeCleanupError("forced cleanup failure")」
file: `scripts/test_lumos.py:37280`
具體輸入→路徑→錯誤：測試讓首次 `_remove_source_sandbox` 在真正刪除前拋錯，之後未補測試清理；每次執行都可能殘留一份 `lumos-probe-*` 暫存副本。`t_probe_source_probe_main` 的 fatal 分支也有同形狀。

審過範圍：逐 hunk 讀完指定 SHA-256 的 1307 行 snapshot，共九個檔案；對照 S4–S7。原案四輪 FAIL 在試行計劃與驗證紀錄中均明確保留，未冒稱收斂，無 finding。

驗證：`probe_boundary` 29 項、`probe_source_probe_main` 10 項、`probe_repair_per_question_cli` 6 項均通過；`py_compile` 通過。現有綠測試沒有覆蓋上述混合題序與重試時間歸屬。

固定席：`Systems/codex-harness`：F1、F2。`Systems/測試假綠形態`：F1、F2 的測試場景缺口及 F3。`Systems/lumos-cli-read`、`Systems/bound-tests-gate`、`Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`、`Systems/lumos-cli-lifecycle`：已讀,無 finding。

總結：最嚴重 severity: major；blocking: 2 條。
