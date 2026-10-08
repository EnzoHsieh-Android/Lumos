severity: major  
blocking: 是  
引句:「lines += ["", f"不一致題 with: {', '.join(a['inconsistent_questions']) or '—'};without: {', '.join(b['inconsistent_questions']) or '—'}"]」  
file: `governance/eval/ablation_lumos_first.py:410`  
具體輸入與路徑：qid `<img src=x onerror=alert(1)>` 可通過 `load_ids`；同題一過一敗後進入 `inconsistent_questions`，表格雖有轉義，頁尾卻重新使用原始 qid，輸出的 Markdown 含可執行原始 HTML，違反計劃中「轉義 HTML 尖括號」的約束。  
最小重現：
```sh
python3 - <<'PY'
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location("a",Path("governance/eval/ablation_lumos_first.py"))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
q="<img src=x onerror=alert(1)>"
a=m._arm_stats([{"id":q,"passed":True},{"id":q,"passed":False}],[q],2)
b=m._arm_stats([], [q], 2)
x={"arms":{"with":a,"without":b},"expected_ids":[q],"runs":2,"m1_delta_pp":None,
   "per_question":{q:{"with":[1,2],"without":[0,0]}},"question_class":{q:"缺資料"},
   "class_counts":{"缺資料":1}}
print(m.render_md(x,{"date":"d","claude_version":"v"}).splitlines()[-1])
PY
```
觀測：`不一致題 with: <img src=x onerror=alert(1)>;without: —`。

severity: major  
blocking: 是  
引句:「lines[2:2] = [f"**整批不可採信：探針失效；請先處置 {bad}。**", ""]」  
file: `governance/eval/ablation_lumos_first.py:405`  
具體輸入與路徑：輸出目錄放入 `with-<img src=x onerror=alert(1)>.json`，結果掃描把它列為失效檔，`render_md` 將檔名原樣插入 Markdown；CommonMark 會把其中的原始 HTML 留給渲染器。  
最小重現：
```sh
python3 - <<'PY'
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location("a",Path("governance/eval/ablation_lumos_first.py"))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
b={"n":0,"m1_passed":0,"m1_rate":None,"m2_ever":0,"m2_n":0,"m2_rate":None,
   "m3_first_idx_median":None,"m3_n":0,"m4_gated_passed":0,"m4_gated_n":0,
   "m4_content_passed":0,"m4_content_n":0,"inconsistent_questions":[],
   "missing":1,"limit_hits":0,"instrument_errors":0}
x={"arms":{"with":b,"without":dict(b)},"expected_ids":["a"],"runs":1,"m1_delta_pp":None,
   "per_question":{},"question_class":{},"class_counts":{},
   "skills_health_poisoned":[("with-<img src=x onerror=alert(1)>.json",["bad"])]}
print(m.render_md(x,{"date":"d","claude_version":"v"}).splitlines()[2])
PY
```
觀測：`**整批不可採信：探針失效；請先處置 with-<img src=x onerror=alert(1)>.json。**`。

severity: major  
blocking: 是  
引句:「lines = [f"# 修法 A ablation 對照(記錄日期 {meta.get('date')};當次 Claude CLI {meta.get('claude_version', '?')})", ""」  
file: `governance/eval/ablation_lumos_first.py:388`  
具體輸入與路徑：純合併會接受歷史 `meta.json` 內任何非空字串；`date` 或 `claude_version` 含換行與 HTML 時會突破標題並注入原始 Markdown/HTML。  
最小重現：
```sh
python3 - <<'PY'
import importlib.util
from pathlib import Path
s=importlib.util.spec_from_file_location("a",Path("governance/eval/ablation_lumos_first.py"))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
b={"n":0,"m1_passed":0,"m1_rate":None,"m2_ever":0,"m2_n":0,"m2_rate":None,
   "m3_first_idx_median":None,"m3_n":0,"m4_gated_passed":0,"m4_gated_n":0,
   "m4_content_passed":0,"m4_content_n":0,"inconsistent_questions":[],
   "missing":0,"limit_hits":0,"instrument_errors":0}
x={"arms":{"with":b,"without":dict(b)},"expected_ids":[],"runs":1,"m1_delta_pp":None,
   "per_question":{},"question_class":{},"class_counts":{}}
print(m.render_md(x,{"date":"d\n<img src=x onerror=alert(1)>","claude_version":"v"}).splitlines()[:2])
PY
```
觀測：第二行為裸 `<img src=x onerror=alert(1)>;當次 Claude CLI v)`。

severity: minor  
blocking: 否  
引句:「if p.name.startswith(("with-", "without-")))」  
file: `governance/eval/ablation_lumos_first.py:158`  
具體輸入與路徑：掃描條件比實際格式 `with-q-*`／`without-q-*` 及合法舊 `with-shard*`／`without-shard*` 更寬；旁邊的 `with-notes.json` 仍會被當成正式結果並讓整批 rc3，與「無關 JSON 不當探針事故」的目標不符。  
最小重現：
```sh
python3 - <<'PY'
import importlib.util,json,tempfile
from pathlib import Path
s=importlib.util.spec_from_file_location("a",Path("governance/eval/ablation_lumos_first.py"))
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
    (Path(d)/"with-notes.json").write_text(json.dumps({"memo":"operator note"}))
    print(m.collect_skills_health(d))
PY
```
觀測：`with-notes.json` 被報為「結果檔缺少逐場資料」，後續整批不可採信。

argparse 精確選題、短線起頭 qid、arm 驗證、非物件列整檔拒收、合法舊 shard：已讀，無其他 finding。

總結：最高 severity major；blocking 3 條。
