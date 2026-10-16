severity: major

C1 — preflight 可放行洩題且不完整的 manifest  
severity: major  
blocking: true  
file: `governance/eval/unfamiliar_stack_brief.py:77`  
引句:「if any("answer-key" in item.lower() or "answer_key" in item.lower() for item in materials):」  
`preflight_run` 只用檔名片段擋 answer key；不驗材料存在、是否屬凍結檔，也不保證 control 無 Brief、fixed 不外洩。`verify_manifest` 亦不要求 S1 的主缺陷、正常反例、oracle。以五案十臂的有效 fixture，刪掉 U1 三欄並令 control materials 為不存在的 `fixed.cs`、`brief.json`，結果仍為：
```text
PASSED ['cases/U1/fixed.cs', 'cases/U1/brief.json']
missing ['normal_counterexample', 'oracle', 'primary_defect']
```
重現：以 `test_unfamiliar_stack_brief.py` 的 `valid_manifest(root)` 建 fixture，套用上述欄位刪除與 materials 後執行 `MODULE.preflight_run(path, root/'new-output')`。現行三支測試仍全綠。

C2 — 字串 `"false"` 會被算成確認命中並放行擴大  
severity: major  
blocking: true  
file: `governance/eval/unfamiliar_stack_brief.py:153`  
引句:「任一場無效、不是陌生棧、缺臂或重複臂，結果只能是 incomplete。」  
`valid`、`primary_hit`、`evidence_grounded`、`normal_counterexample_harmed`、時間與 token 都未做型別／範圍驗證；Python 將非空 `"false"` 視為真。十筆 receipt 全填 `valid="false"`，Brief 的 hit/evidence 填 `"false"`，時間填 `"bad"`、tokens 填 `-100`，實得：
```text
proceed-to-historical 5 []
```
重現核心：
```python
rows = receipts()
for row in rows:
    row.update(
        valid="false",
        primary_hit=("false" if row["arm"] == "brief" else ""),
        evidence_grounded=("false" if row["arm"] == "brief" else ""),
        elapsed_seconds="bad",
        tokens=-100,
    )
print(MODULE.summarize_receipts(rows)["decision"])
```

C3 — U4 fixed 版遺失 worker 結果，但 oracle 假綠  
severity: major  
blocking: true  
file: `governance/eval/unfamiliar-stack-brief/cases/U4/fixed.js:11`  
引句:「It must process caller-supplied finite collections, return worker results, and keep simultaneous worker executions at or below 3.」  
fixed 的 `processAll` 只 `await Promise.all(...)`，沒有回傳結果；輸入 `[1,2]`、worker 回傳兩倍值，實際得到 `undefined`。現有 oracle 只量峰值，因此 fixed target、normal 仍皆 rc0，違反「保持相鄰好行為」與測試假綠合約。
```text
undefined
fixed_target_rc=0
fixed_normal_rc=0
```
重現：
```sh
node --input-type=module - <<'JS'
import fs from 'node:fs';
const s = fs.readFileSync('governance/eval/unfamiliar-stack-brief/cases/U4/fixed.js','utf8');
const p = s.split('async function run')[0];
await import(`data:text/javascript,${encodeURIComponent(
  `${p}\nconsole.log(JSON.stringify(await processAll([1,2], async x => x * 2)));`
)}`);
JS
```

C4 — U2 兩支 Dart 程式沒有圖譜家  
severity: major  
blocking: true  
file: `governance/eval/unfamiliar-stack-brief/cases/U2/buggy.dart:6`  
引句:「StreamSubscription<int>? subscription;」  
分支新增 U2 的 buggy/fixed，但沒有 `Systems/陌生棧案例U2_Dart.md`；計劃 `lands_in` 與資格驗證 `system_refs` 也都從 U1 跳到 U3。人工依 AGENTS「每支程式檔有家」判定違規；兩檔 impact 均無任何家：
```text
{"file":".../U2/buggy.dart","direct":[],"indirect":[],"incidents":[]}
{"file":".../U2/fixed.dart","direct":[],"indirect":[],"incidents":[]}
```
重現：
```sh
python3 scripts/lumos impact --file governance/eval/unfamiliar-stack-brief/cases/U2/buggy.dart --json
python3 scripts/lumos impact --file governance/eval/unfamiliar-stack-brief/cases/U2/fixed.dart --json
```
`home check` 的既有 profile 未涵蓋 Dart，故 rc0 不能推翻人工合約判定。

r1-snapshot.patch、r1-manifest.json／r1-dispositions.json：已讀；無額外 finding；刻意 buggy fixtures 未當作 production defect。候選 v2 的 C#／Dart／Swift／Node／Java source ID 均與 idiom 原文相符。

新增殘留：governance/residual-index.json 無差異，治理帳新增行也沒有 `residual-ask`；因此沒有殘留問答可核對改號、改字重問或第二代理身分。

總結：最高 severity major；blocking 4 條。
