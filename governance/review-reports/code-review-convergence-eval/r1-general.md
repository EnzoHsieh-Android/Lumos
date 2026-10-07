severity: major

F1 缺一側試行時仍輸出成本均值，會製造虛假的便宜訊號  
severity: major  
blocking:是  
逐字引句:「sum(xs) / len(xs) if xs and len(xs) == len(ds) else None」  
file: `governance/eval/review_convergence.py:347`  
file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:30`

`summarize()` 只要求目前有效的 `ds` 都有成本，沒有要求該 arm 的預排 slot 齊全。若昂貴的 candidate 試行缺場，剩餘樣本仍會得到較低均值，違反「成本有完整資料才給均值」及 S4 不報虛假改善。

最小翻紅實驗：1 case、2 repeats；baseline 成本為 1、100，candidate 只有 repeat 1、成本 1。

實際輸出：

```text
expected_trials=4
valid_trials=3
paired_trials=1
baseline.tokens_mean=50.5
candidate.tokens_mean=1.0
```

candidate 缺一場卻仍顯示 `1.0`，兩側分母不同。應在預排 slot 不完整時將 arm 均值設為未知，或只計算成對有效 slot 的成本。

F2 token 衝突只在同一 loop 內檢查，跨 loop 的同 token 會被重複計入  
severity: major  
blocking:是  
逐字引句:「for loop, source in sorted(groups.items()):」  
file: `governance/eval/review_convergence.py:107`  
file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26`

程式先按 loop 分組，之後才建立各組自己的 `tokens` 字典。因此同一治理 token 若被分到兩個 loop，兩筆永遠不會相遇，既不標衝突，也各自計入成本；這直接違反「重複 token 只計一次，有衝突則未知」。

最小翻紅實驗：

```python
ev.build_cohort([
    {"loop": "code-a", "round": "r1", "token": "SAME", "tokens": 5},
    {"loop": "code-b", "round": "r1", "token": "SAME", "tokens": 7},
])
```

實際輸出：

```json
{
  "observed_code_loops": 2,
  "loops": [
    {"loop": "code-a", "conflicting_tokens": false, "total": 5},
    {"loop": "code-b", "conflicting_tokens": false, "total": 7}
  ]
}
```

token 身分應先在全帳本層核對，再進行 loop 分組；否則 cohort 數量與成本都可能被重複或錯誤歸屬。

F3 讀檔入口在原生 Windows 會於任何輸入上直接拋出 AttributeError  
severity: major  
blocking:是  
逐字引句:「fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」  
file: `governance/eval/review_convergence.py:24`  
file: `docs/lumos-toolchain-knowledge/Systems/native-windows-support.md:46`

專案明訂原生 Windows 支援，但 `O_NONBLOCK` 是未做能力偵測的 Unix 旗標；同一行的 `O_NOFOLLOW` 已使用 `getattr`，`O_NONBLOCK` 卻沒有。`except OSError` 也接不到屬性不存在的 `AttributeError`。

最小實驗是在目前程序移除該平台不存在的屬性後呼叫 `read_bytes()`；未使用 Windows 真機，但精確重現缺少該常數的執行條件。

實際輸出：

```text
AttributeError: module 'os' has no attribute 'O_NONBLOCK'
```

應比照 `O_NOFOLLOW` 使用 `getattr(os, "O_NONBLOCK", 0)`，並補 Windows 路徑測試。

F4 PITFALL 的測試證據被塞進出處欄，圖譜不會辨識為防回歸連結  
severity: minor  
blocking:否  
逐字引句:「PITFALL:[根因:把較少輪誤當品質改善]較少輪但破壞既有行為不能算改善 [出處:Verification/2026-10-07_審查回顧eval補強;test:t_review_eval_comparison]」  
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:19`

`[test:t_review_eval_comparison]` 位於 `[出處:…]` 的值內，不是獨立欄位。

實際輸出：

```text
⚠ 筆記格子『PITFALL:』缺 test、repro、防回歸 三選一
0 error / 1 warning
```

應拆成獨立的 `[出處:…] [test:t_review_eval_comparison]`。

pitfalls／表態核對：

- `open()` 資源 claim 是誤報：fd 立即交給 `os.fdopen()`，並由 `with` 在一般及例外路徑關閉。
- `py-eventloop`、`py-parallel`、`py-external` 與 `py-extcode` 的 `na` 判定成立。
- 檔案大小有 16 MiB／256 KiB 上限，`py-memory` 的記憶體界線成立；但不影響 F1、F2 的統計錯判。
- 尚無模型實輪成效；本報告未把合成試行當成成效證據。
- 沙盒禁止建立指定 `/tmp` 目錄，因此原測試僅有 5 個不需暫存檔的案例實際通過，另外 7 個因沒有可寫暫存目錄而未執行；上列重大 finding 均以純記憶體反例取得實際輸出。

圖譜硬合約：`/tmp/review-eval-graph-lens.txt` 只有受影響節點排序與 `★INVARIANT★` 類別標記，沒有自動附上任何硬合約原文、綁定狀態或固定席合約內容；因此本席沒有可逐條作答的自動附加硬合約。

最高等級: major / 阻擋條數: 3