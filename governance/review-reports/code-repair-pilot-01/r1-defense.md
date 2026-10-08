Finding 1  
severity: major  
blocking: 是  
引句:「只 grep 圖譜資料夾、沒讀程式碼的要判不過。」file: `scripts/test_lumos.py:36727`  
agree: 是。現行 `v04-where-used` 的 `expect` 接受任何不含 `-knowledge` 的 `Read/Grep/Glob`；`answer_expect` 又只要求「帳／ledger／log」。  
evidence: `grade(v04, [("Read", "README.md")], "這是一本帳")` 實際回傳 `(True, "ok", True)`，完全沒有讀程式碼。  
範圍: 本提交引入。`618ee85f` 原本要求 `lumos ...`；`2db51cc4` 才改成這個廣泛的讀取正則，屬本提交核心判準調整的合理審查範圍。  
concern: 新判準聲稱驗證「已讀程式碼」，實際只能驗證讀過任意非圖譜檔，會把未建立程式碼證據的回答記成有效通過。  
最小重現: 載入 `scripts/scenario_probe.py`，以上述 `calls` 與答案呼叫 `grade`；預期 `passed=False`，實際 `passed=True`。

Finding 2  
severity: major  
blocking: 是  
引句:「一批結果 → 總結。分母只算有效場次(扣掉截斷、用量上限、其他儀器例外)。」file: `scripts/scenario_probe.py:570`  
agree: 是。Claude `run_one` 在 `subprocess.run` 後只取 `stdout/stderr`，未檢查 `r.returncode`；Codex 路徑則明確把非零退出設為儀器例外。file: `scripts/scenario_probe.py:524`、`scripts/scenario_probe.py:451`  
evidence: 本機 mock 回傳 `returncode=7`、`stderr="boom"`，事件流含期望的 `lumos search`；`run_one` 仍產生 `passed=True, reason="ok", truncated=False`，`summarize_results` 記為 `1/1`，`history_record` 的 `excluded=[]`。  
範圍: 原本已存在；本提交暴露。`git show 618ee85f:scripts/scenario_probe.py` 的 Claude 路徑已忽略 return code；本提交新增「有效樣本」摘要與歷史排除契約後，該缺口會直接污染新增輸出，因此仍屬合理修復範圍。  
concern: Claude CLI 異常退出可被記成有效成功；即使沒命中期望，也會被記成有效失敗，兩者都會扭曲摘要、歷史與後續趨勢判讀。  
最小重現: monkeypatch `scenario_probe.subprocess.run` 回傳帶上述事件流且 `returncode=7` 的物件，再呼叫 `run_one → summarize_results → history_record`；預期列入 `excluded`，實際列入有效分母並記成 `1/1`。

測試載入整理：已讀,無 finding。`t_scenario_probe_per_scenario_max_turns` 的 inline `SourceFileLoader` 與緊接著的 `_load_probe_module` 使用相同 path／spec／module／exec 流程。file: `scripts/test_lumos.py:36590`、`scripts/test_lumos.py:36601`。這只是 helper 抽取未順手套回前一支測試的整理建議，不影響行為或測試可信度。

總結: 最嚴重 severity=major；blocking=2
