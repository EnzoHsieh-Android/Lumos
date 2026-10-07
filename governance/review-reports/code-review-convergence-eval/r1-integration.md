severity: major

ID: F1
severity: major
blocking: 是
逐字引句:「真實帳本唯讀試行：來源SHA為4581f2f4c44f5cddc96368f409e7197911768811059889d44aa2c62357c88feb，225個code編號；11個分輪未知、152個成本總量未知。」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-07_審查回顧eval補強.md:26`

同一來源 SHA 依文件命令重跑，實際是 224／10／151；`cohort-smoke.json` 與 status=pass 的 Verification 均不可重現。

最小翻紅：

```sh
python3 governance/eval/review_convergence.py cohort docs/.canary-log.jsonl |
python3 -c 'import json,sys; d=json.load(sys.stdin); got=(d["observed_code_loops"],sum(x["round_count"] is None for x in d["loops"]),sum(x["tokens"]["total"] is None for x in d["loops"]),d["source_sha256"]); print(got); assert got[:3] == (225,11,152), f"smoke mismatch: {got[:3]} != {(225,11,152)}"'
```

實際輸出：

```text
(224, 10, 151, '4581f2f4c44f5cddc96368f409e7197911768811059889d44aa2c62357c88feb')
AssertionError: smoke mismatch: (224, 10, 151) != (225, 11, 152)
```

需重產 smoke、修正 Verification，並建議把工具版本或工具檔 SHA 一併釘入，避免來源帳相同但彙整邏輯已變時仍看似可重現。

ID: F2
severity: major
blocking: 是
逐字引句:「rounds：正整數；tokens/wall_seconds：非負有限值，缺資料填 null。」
file: `governance/eval/review_convergence.py:313`

`validate_outcome()` 完全沒驗 `tokens` 與 `wall_seconds`。負數或字串成本會被接受成有效 trial，甚至計入 `quality_pass`；之後只被 `summarize()` 靜默當作成本未知，沒有進 `invalid_records`，違反 S3 的結果資料不符須保留原因。

最小翻紅：

```sh
python3.14 -c 'import sys; sys.path.insert(0,"governance/eval"); import review_convergence as e; d={"status":"completed","repair":True,"preserve":True,"new_defects":0,"rounds":1,"tokens":-1,"wall_seconds":"bad"};
try: e.validate_outcome(d)
except e.DataError: pass
else: raise AssertionError(f"invalid cost accepted as valid: {d}")'
```

實際輸出：

```text
AssertionError: invalid cost accepted as valid: {'status': 'completed', 'repair': True, 'preserve': True, 'new_defects': 0, 'rounds': 1, 'tokens': -1, 'wall_seconds': 'bad', 'quality_pass': True}
```

ID: F3
severity: minor
blocking: 否
逐字引句:「repair、preserve、新缺陷分開；已執行而失敗的產品驗收仍進分母」
file: `governance/eval/review_convergence.py:339`

比較輸出只保留 `quality_passes`，沒有各自輸出 repair、preserve 或 new-defects 的統計。修復失敗、保留失敗與新增一個／大量缺陷都被壓成同一個布林值，無法兌現計畫所說的分開比較。

ID: F4
severity: minor
blocking: 否
逐字引句:「PITFALL:[根因:把較少輪誤當品質改善]較少輪但破壞既有行為不能算改善 [出處:Verification/2026-10-07_審查回顧eval補強;test:t_review_eval_comparison]」
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:19`

`test:` 被塞進 `[出處:...]`，不是獨立 `[test:...]`。實跑 `lumos lint Systems/review-convergence-eval` 得到「PITFALL 缺 test、repro、防回歸三選一」，所以這條防回歸連結目前不可被機器辨識。

ID: F5
severity: minor
blocking: 否
逐字引句:「return parse(decode(read_bytes(path, 256 * 1024)))」
file: `/tmp/review-eval-disp.json:23`

`py-memory` 的 hint 已明示新 `read_json` 與三支對照檔形成候選張力、應填 `tension`，表態卻填 `satisfied`。新做法本身合理，但應記成 `tension/chosen=suggested`，留下既有寫法、隱患與採用證據。

圖譜鏡頭逐條答覆：

- 自動鏡頭未附任何硬合約原文、`[test:]` 綁定狀態或外部事實行；只有節點名。因此沒有可按原文逐句核對的自動附加合約，這點依派工要求明說。
- 手動查詢後，測試假綠形態、bound-tests-gate、canary-audit、guard-kill、三個 slim 節點、lumos-cli-read、lumos-cli-lifecycle、design-loop、節點範圍與索引守衛：本 patch 未改其既有實作或綁定測試；受波及合約測試實跑為 56 綠。
- lumos-deinit、逃逸自動記、引用座標、規格落成、異常派工單、check-r-guard：未登記硬合約。
- cochange-guard：只有 DEBT，無硬合約。
- 新計畫 S1 被 F1 的不可重現證據打破；S2 的 `CaseTests` 3 案實跑通過；S3 被 F2 打破；S4 的防虛假改善主路徑存在，但缺 F3 的分項輸出。

驗證限制：

- `template` 命令可執行；`cohort` 可執行但產出與凍結證據不符。
- 直接 `CaseTests`：3 tests，OK。
- Ruff：All checks passed。
- 正式 runner 與需 receipt 臨時檔的測試無法在本席重跑：指定實驗目錄不存在，唯讀沙盒拒絕建立，runner 回 `No usable temporary directory found`。因此未把凍結的 after.log 冒充本席實跑。
- 尚無模型 baseline/candidate 實輪；本報告未把合成 trial 當模型成效。

工作樹副作用：`lumos doctor --verbose` 意外在 `docs/.governance-log.jsonl` 尾端追加 10:11:19 bound-tests 與 10:11:22 code-loop blocked 兩筆；唯讀沙盒拒絕撤回。這兩筆由本席觸發，不屬作者改動，折修前應移除。

最高等級: major  
阻擋條數: 2