severity: major

條款逐項結論：

- S11：已讀，未發現成功外觀候選抵缺場的路徑。
- S12：已讀，場數、題號、組別、精確選題與相對輸出路徑符合條款。
- S13：已讀，正式結果的失效顯示與拒收符合條款。
- S14：已讀，純合併保留來源 meta，缺值標未知，未查當前 CLI。
- S15：有 finding；候選檔的 `calls` 列內容未完整驗型。
- S16：有 finding；錯型計分資料仍可進入 M2/M3。
- S17：有 minor finding；無關 JSON 的測試範圍窄於條款。
- S18：有 finding；失敗批次已消耗的模型嘗試未留在窗口帳。

Finding 1

severity: major  
blocking: 是  
引句:「or (calls is not None and not isinstance(calls, list))」  
file: `governance/eval/ablation_lumos_first.py:138`

S15/S16 要求每列型別與錯型計分欄位整檔拒收，但這裡只驗 `calls` 外層是 list，沒有驗每個元素必須是兩個字串。`calls: [42]`、`calls: [["Bash"]]` 或混入物件都會通過整批驗證；`backfill_limit` 隨後把它們當成「沒有敲 lumos」，安靜灌低 M2/M3。現有反例只測 `n_calls`、`answer_content_ok`、`limit_hit`，沒有碰 `calls` 內容形狀。

具體輸入：正式檔 `with-q-bad.json`，逐場列為 `{"id":"a","passed":true,"n_calls":1,"calls":[42]}`。

最小重現：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util
from pathlib import Path
p = Path("governance/eval/ablation_lumos_first.py").resolve()
s = importlib.util.spec_from_file_location("a", p)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
d = {
  "arm": "with", "fatal": False, "inconclusive": False,
  "skills_health_bad": [],
  "results": [{"id": "a", "passed": True, "n_calls": 1, "calls": [42]}],
}
print(m.invalid_batch_evidence(d, "with"))
print(m.backfill_limit(d["results"][0].copy())["ever_lumos"])
PY
```

實際輸出為 `[]` 與 `False`；預期第一行非空並整檔拒收。

Finding 2

severity: major  
blocking: 是  
引句:「n += sum(1 + len(r.get("retry_attempts", [])) for r in rows if isinstance(r, dict))」  
file: `governance/eval/ablation_lumos_first.py:223`

S18 的批內上限有效，但跨批窗口帳會漏掉 fatal 批次的所有實際模型呼叫。子程序達限後把實際結果與重試留在 `.candidate`，父程序因 rc=3 另寫一個 `results: []` 的正式 fatal JSON；`runs_in_window` 只掃正式 JSON。人工照 `retry_policy` 歸檔 fatal、pending、candidate 後，同一五小時窗口會重新得到完整額度，能再次啟動模型，違反 `--max-per-window`「含撞上限」的承諾。

具體路徑：第一場撞限、第二場成功，共兩次模型呼叫；第二個 requested run 在 `--max-attempts=2` 前被擋。候選檔保留兩次呼叫，正式 JSON 在 `governance/eval/ablation_lumos_first.py:306` 寫成空列 tombstone，下一批窗口計數為 0。

最小重現核心：

```python
# 模擬 run_job 的 rc=3 落地形狀
final_json = {
    "arm": "with", "results": [], "fatal": True, "inconclusive": True
}
candidate = {
    "arm": "with",
    "results": [{
        "id": "a", "passed": True,
        "retry_attempts": [{"reason": "limit"}]
    }],
    "fatal": True,
}
# runs_in_window 只收到 final_json，回 0；candidate 中兩次實際呼叫完全未入帳。
```

應新增父層反例：同一輸出目錄先產生上述 rc=3 批次，依標記指示歸檔後立即再跑，斷言第二批不會再取得兩次額度。現有 `t_probe_boundary_formal_retry_budget` 只驗子程序不啟動第三次，未驗下一批窗口。

Finding 3

severity: minor  
blocking: 否  
引句:「if p.name.startswith(("with-", "without-")))」  
file: `governance/eval/ablation_lumos_first.py:158`

S17 寫的是「輸出目錄內無關 JSON 不當探針事故」，實作卻把所有 `with-*`／`without-*` JSON 視為探針結果。無關的 `with-notes.json` 會被判為缺少逐場資料，整批 rc3。測試只放 `notes.json` 與 `with.json`，恰好避開這個寬泛前綴，因此是假綠邊界。

具體輸入：輸出目錄加入 `with-notes.json`，內容 `{"memo":"operator note"}`；`collect_skills_health` 會回報「結果檔缺少逐場資料」。

建議把正式檔名限定為既有的 `with-q-*`／`without-q-*` 與明確列出的 legacy shard 格式，並將反例改成 `with-notes.json`。

已讀其餘路徑，無 finding。

總結：最嚴重 severity major；blocking 2 條。
