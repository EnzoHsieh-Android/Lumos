severity: major

F1 Unicode 正規化碰撞會讓其中一篇 Systems 筆記靜默消失  
severity: major  
blocking: 是  
引句:「以選定vault與推得的repo為界，列舉所有Markdown，包含作廢筆記」  
file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:81`  
file: `scripts/lumos:716`  
輸入→錯誤：在可同時容納 NFC/NFD 檔名的檔案系統建立 `Systems/é.md` 與 `Systems/é.md`，各登記一項護欄；規格指定重用 `Env.from_texts`，但它先把路徑 NFC 化再建 dict，兩鍵碰撞後只剩一篇，可能仍以完整讀取、rc0 輸出，破壞 d6/G7 的全量盤點。  
最小重現：
```python
import runpy
Env = runpy.run_path("scripts/lumos", run_name="probe")["Env"]
texts = {
    "Systems/e\u0301.md": "---\ntype: system\n---\nA",
    "Systems/\u00e9.md": "---\ntype: system\n---\nB",
}
assert len(Env.from_texts("/tmp/vault", texts).notes) == 2
```
現碼得到 `1`，斷言翻紅。  
最小修正：進 `Env.from_texts` 前以原始相對路徑分組檢查 NFC 後碰撞；碰撞須列明 `normalized_path_collision`、退出 2，禁止任選一篇覆寫。補一個兩篇各含正常護欄的案例，驗證不會靜默少列。

已讀，無 finding：

- 守衛誤讀：`purpose=inventory`、`security_verdict=not_assessed`、宣告狀態與機械核對分離，未把 rc0 當安全通過。
- 輸入安全其餘面：嚴格 JSON、重複鍵／NaN／未知欄位拒絕、路徑跳脫與符號連結拒絕、控制字元輸出消毒已有明確條款。
- 資源：單檔、總量與檔案數均有上限，超限退出 2。
- 併發：檔案清單或內容變動列不完整，不宣稱跨檔原子快照。
- 回退：只撤命令與專用解析，不改既有 contracts/query/enforcement。
- d5、d6／Q3、Q4：通用 Invariant 與安全關注面仍分離；唯讀盤點未越權執行故障、接 CI/push 或自動核可。
- `refcheck --json`：0 claims、0 missing、0 out-of-range；`prose-lint`：0 命中。

總結：最嚴重 severity: major；blocking: 1
