severity: major  
審材: governance/review-reports/code-repair-pilot-01/r1-snapshot.patch

C1 純程式碼題把任意非圖譜文件誤判成「已讀程式碼」  
severity: major  
blocking: 是  
引句:「"expect": ["^(?:Grep|Glob|Read):(?![\\s\\S]*-knowledge)」  
file: `governance/scenarios/paraphrase.jsonl:4`  
`Read:README.md` 或 `grep _BOOKKEEPING_FILES README.md` 都會命中；只要回答含「帳」便通過，未證明讀過任何程式碼。這使唯一的純程式碼反向題可假綠；現有測試只否決 `-knowledge` 路徑，沒否決其他非程式文件。  
file: `scripts/test_lumos.py:36736`  
最小重現：
```sh
python3 - <<'PY'
import importlib.util,json,pathlib
s=importlib.util.spec_from_file_location("sp","scripts/scenario_probe.py")
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
q=next(json.loads(x) for x in pathlib.Path("governance/scenarios/paraphrase.jsonl").read_text().splitlines() if '"v04-where-used"' in x)
print(m.grade(q,[("Read","README.md")],"這是一本帳"))
PY
```
結果：`(True, 'ok', True)`。應要求實際程式檔，並增加 README 等非程式文件的反例。

C2 Claude runner 非零退出仍被算成有效失敗，與 Codex runner 不一致  
severity: major  
blocking: 是  
引句:「分母只算有效場次(扣掉截斷、用量上限、其他儀器例外)」  
file: `scripts/scenario_probe.py:524`  
Claude 路徑取出 stdout/stderr 後未檢查 `r.returncode`；相鄰 Codex 路徑會把非零退出標成儀器例外。Claude CLI 的驗證、登入或程序錯誤因此會污染通過率與歷史失敗清單。  
file: `scripts/scenario_probe.py:451`  
最小重現：
```sh
python3 - <<'PY'
import importlib.util,pathlib
s=importlib.util.spec_from_file_location("sp","scripts/scenario_probe.py")
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class R: stdout=""; stderr="cli crashed"; returncode=7
real=m.subprocess.run; m.subprocess.run=lambda *a,**k:R()
q={"id":"x","prompt":"p","expect":["lumos search"],"forbid_before":[]}
try:
 print("claude",m.run_one(q,pathlib.Path("."),18,10,"")["reason"])
 print("codex",m.run_one_codex(q,pathlib.Path("."),10,"")["reason"])
finally: m.subprocess.run=real
PY
```
結果：
```text
claude 沒敲到期望指令: ['lumos search']
codex 儀器例外: codex exec 退出碼 7(這場不算分)
```
應在用量上限、回合上限判定優先序不變的前提下，把 Claude 非零退出同樣列為儀器例外。

C3 `--runs > 1` 的逐題通過次數仍把截斷放進分母  
severity: minor  
blocking: 否  
引句:「一批結果 → 總結。分母只算有效場次」  
file: `scripts/scenario_probe.py:735`  
總結與歷史已排除截斷，但「每題通過次數」仍直接遍歷全部 `results`。一場截斷、一場通過會同時輸出整體 `1/1` 與逐題 `1/2`，讓重跑分析得到互相矛盾的數字。  
最小重現結果：
```text
1/1 個情境 Claude 自己敲對了 lumos 指令;不算分:截斷 1
每題通過次數: q 1/2
```
逐題計數應只納入有效場次，或明列排除數。

治理帳、計劃、調研、驗證紀錄與 anchor baseline：已讀,無 finding。  
answers/commands 題庫及 paraphrase 其餘異動：已讀,無 finding。  
正常結束、回合上限、逾時、用量上限、低有效樣本回退與歷史版本欄位：已讀,無 finding。  
新增測試其餘斷言：已讀,無 finding。

圖譜鏡頭逐條回覆：

- `Systems/codex-harness`：C1–C3。
- `Systems/測試假綠形態`：C1；負例只覆蓋圖譜路徑，未證明一般非程式文件會翻紅。
- `Systems/bound-tests-gate`：已讀,無 finding。
- `Systems/canary-audit`：已讀,無 finding。
- `Systems/design-loop`：已讀,無 finding。
- `Systems/guard-kill`：已讀,無 finding。
- `Systems/lumos-cli-lifecycle`：已讀,無 finding。
- `Systems/slim-get-一行安裝`：已讀,無 finding。
- `Systems/slim-install-安裝器`：已讀,無 finding。
- `Systems/slim-uninstall-一行卸載`：已讀,無 finding。
- `Systems/lumos-cli-read`：已讀,無 finding。
- `Projects/規格落成可驗收條件_計劃`：已讀,無 finding。
- `Projects/逃逸自動記_計劃`：已讀,無 finding。
- `Systems/lumos-deinit`：已讀,無 finding。
- `Systems/check-r-guard`：已讀,無 finding。
- `Systems/節點範圍與索引守衛`：已讀,無 finding。
- `Systems/cochange-guard`：已讀,無 finding。

總結: 最嚴重 severity major；blocking 2 條。
