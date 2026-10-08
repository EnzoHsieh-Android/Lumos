severity: major

finding: 超額的同題結果仍會灌高整體通過率；修補只逐題算缺場，統計分子與分母仍吃進全部重複列。攻擊者或舊殘檔只要加入大量合法外觀的 A 題通過列，就能把預註冊為「每題 1 次」的 M1 從 50% 改成接近 100%。

severity: major

blocking: 是

引句:「"missing": sum(max(0, runs - per.get(q, [0, 0])[1]) for q in expected_ids),」

file: `governance/eval/ablation_lumos_first.py:345`

具體輸入與執行路徑：`load_results` 接受多個同題正式列後，`_arm_stats` 只用 `expected_ids` 篩題號，沒有把每題裁到 `runs` 筆；`valid`、`n`、`m1_passed` 因此全部被重複列加權。

最小重現：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("abl",p)
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
rows=[{"id":"a","passed":True}]*100+[{"id":"b","passed":False}]
st=m._arm_stats(rows,["a","b"],1)
print({k:st[k] for k in ("n","m1_passed","m1_rate","missing")})
PY
```

觀測：`{'n': 101, 'm1_passed': 100, 'm1_rate': 0.9901, 'missing': 0}`；每題一次的正確結果應是 1/2，而非 100/101。現有測試只斷言 `missing`，沒有驗證 M1 加權。

finding: fatal／健康事故已實際啟動的模型嘗試沒有寫進可核帳檔；依標記指示歸檔事故檔與候選檔後，五小時窗口會忘掉這批消耗，下一次可重新取得完整額度。

severity: major

blocking: 是

引句:「n += sum(1 + len(r.get("retry_attempts", [])) for r in rows if isinstance(r, dict))」

file: `governance/eval/ablation_lumos_first.py:218`

file: `governance/eval/ablation_lumos_first.py:306`

具體輸入與執行路徑：探針完成三次模型嘗試後以 rc=3 結束；候選檔保有重試列，但父程序另寫 `results: []` 的 fatal 正式檔。`runs_in_window` 只掃正式 JSON，因此計為 0；人工依 `archive-fatal-and-candidate-then-rerun` 處置後即可再次派滿窗口。

最小重現：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util,json,tempfile
from pathlib import Path
from unittest.mock import patch
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("abl",p)
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    out=Path(td)
    def fake(cmd,**kw):
        Path(cmd[cmd.index("--out")+1]).write_text(json.dumps({
          "arm":"with","results":[{"id":"a","passed":False,"limit_hit":True,
          "retry_attempts":[{"reason":"limit"},{"reason":"limit"}]}],
          "fatal":False,"inconclusive":False,"skills_health_bad":[]}))
        return type("R",(),{"returncode":3})()
    with patch.object(m.subprocess,"run",side_effect=fake):
        m.run_job("with","a",1,["dummy"],1,1,out,1,max_per_window=3)
    print(sorted(x.suffix for x in out.iterdir()))
    print(m.runs_in_window(out))
PY
```

觀測：產生 `.candidate/.json/.pending`，但 `runs_in_window` 回傳 `0`，實際已發生三次嘗試。額度需另有只增不減的嘗試帳，或 fatal 正式檔保存父程序可驗證的實際嘗試數；人工歸檔不能抹掉五小時帳。

finding: 報表仍可被歷史 meta 與題號注入 Markdown；字串只驗非空，題號也只處理管線與尖括號，沒有處理換行、圖片、連結及反斜線逃逸。

severity: minor

blocking: 否

引句:「lines = [f"# 修法 A ablation 對照(記錄日期 {meta.get('date')};當次 Claude CLI {meta.get('claude_version', '?')})", "",」

file: `governance/eval/ablation_lumos_first.py:388`

file: `governance/eval/ablation_lumos_first.py:407`

具體輸入與執行路徑：merge-only 的 `meta.json` 若含 `date: "x\n\n![track](https://example.invalid/pixel)"`，`render_md` 會產生主動圖片語法；題號 `![track](https://example.invalid/pixel)` 也會原樣進表格。帶反斜線的 `\|` 經目前替換後可形成偶數反斜線，再讓表格分隔符恢復作用。建議把所有外部字串經同一個 Markdown 純文字編碼器處理，並拒絕 meta 換行。

題號精確選取、候選檔升格、路徑雜湊、同目錄鎖與短線題號傳參：已讀,無 finding。

總結：最嚴重 severity major；blocking 2 條。
