severity: major

## S 條款逐條判定

- S1 — 已實作：保留所有帳上 `code-` 樣本；缺輪次、成本或 token 衝突時輸出未知；未讓 context 推算收斂。
- S2 — 已實作：案例、分組、起點、指紋及兩組模型條件缺漏或矛盾時拒收；template 不補造未知值。
- S3 — 縮水：來源、雜湊、狀態及品質欄位有驗證，但非法成本欄位仍被當成有效試行。
- S4 — 縮水：品質與輪數採成對計算，但缺少排定 slot 時仍可能輸出不完整樣本的成本均值。
- 多做 — 未見超出條款而改動產品審查閘或執行外部命令的行為。

ID: S3-F1  
severity: major  
blocking: 是  
逐字引句:「xs = [d[field] for d in ds if number(d.get(field))]」  
file: `governance/eval/review_convergence.py:313`  
file: `governance/eval/review_convergence.py:343`

`validate_outcome` 沒驗證 `tokens` 與 `wall_seconds` 是否為 `null` 或非負有限數字；後續只把非法值從成本統計濾掉，整筆 receipt 仍列為有效且可進入成對品質差。這違反 S3「結果資料不符時，試行應列未判定並保留原因」。

最小翻紅實驗：

```sh
PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'from governance.eval import review_convergence as e; d={"status":"completed","repair":True,"preserve":True,"new_defects":0,"rounds":1,"tokens":-7,"wall_seconds":"bad"};
try: e.validate_outcome(d)
except e.DataError: pass
else: raise AssertionError("malformed cost accepted as valid")'
```

實際輸出：

```text
AssertionError: malformed cost accepted as valid
exit_code=1
```

完整比較路徑另實測得到：

```text
valid_trials=2
paired_trials=1
invalid_records=[]
quality_delta=0.0
candidate.tokens_known=0
candidate.wall_seconds_known=0
```

也就是非法 receipt 沒留下未判定原因，反而以品質通過參與比較。

ID: S4-F1  
severity: major  
blocking: 是  
逐字引句:「sum(xs) / len(xs) if xs and len(xs) == len(ds) else None」  
file: `governance/eval/review_convergence.py:337`  
file: `governance/eval/review_convergence.py:346`

成本完整性只與 `ds`——已判有效且實際存在的子集——相比，沒有與 manifest 排定的 case/repeat 分母相比。候選缺一個 slot 時，剩下的一筆仍會產生成本均值，造成兩組覆蓋率不同卻出現可直接比較的 `100.0` 與 `1.0`，違反 S4「缺一側仍保留分母、成本完整才給均值且不報虛假改善」。

最小翻紅實驗以兩個 repeat、候選缺 repeat 2 驗證：

```text
{'expected_trials': 4,
 'paired_trials': 1,
 'baseline_mean': 100.0,
 'candidate_valid': 1,
 'candidate_mean': 1.0}
AssertionError: incomplete candidate arm still reports a cost mean
exit_code=1
```

## 圖譜硬合約材料邊界

`/tmp/review-eval-graph-lens.txt` 只附節點名稱與 `★INVARIANT★` 標記，沒有自動附上任何硬合約正文或綁定測試狀態。因此下列各項均只能判為「材料未附，無法逐條核對」，不能由節點名稱反推合約：

- `Systems/測試假綠形態.md`：未附正文，未判定。
- `Systems/bound-tests-gate.md`：未附正文，未判定。
- `Systems/canary-audit.md`：未附正文，未判定。
- `Systems/guard-kill.md`：未附正文，未判定。
- `Systems/slim-get-一行安裝.md`：未附正文，未判定。
- `Systems/slim-install-安裝器.md`：未附正文，未判定。
- `Systems/slim-uninstall-一行卸載.md`：未附正文，未判定。
- `Systems/lumos-cli-read.md`：未附正文，未判定。
- `Systems/lumos-cli-lifecycle.md`：未附正文，未判定。
- `Systems/design-loop.md`：未附正文，未判定。
- `Systems/節點範圍與索引守衛.md`：未附正文，未判定。

凍結的 `after.log` 宣告既有四個入口為 4 passed / 0 failed；目前唯讀沙箱拒絕建立指定實驗目錄，因此沒有改用 repo 或其他目錄重跑會落暫存檔的正式 runner。上述兩個失敗均以不落檔的現行函式路徑重現。

最高等級: major  
阻擋條數: 2