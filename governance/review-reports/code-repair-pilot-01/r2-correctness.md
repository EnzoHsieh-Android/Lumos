severity: major

R2C1 Bash 判準只看命令中出現 `scripts/lumos`，把「在 README 搜尋這段路徑文字」誤認為讀過程式碼，原 C1 假綠仍未折掉。  
severity: major  
blocking: 是  
引句:「修復試行 C1: 只列檔或讀文件不能冒充讀碼;保護原生工具與 shell 的正常讀碼。」  
file: `governance/scenarios/paraphrase.jsonl:4`  
file: `scripts/test_lumos.py:36744`  
最小翻紅重現：載入 `scripts/scenario_probe.py` 與 v04 題目，執行 `grade(v04, [("Bash", "grep 'scripts/lumos' README.md")], "這是帳本檔案白名單")`；預期 `False`，實際 `(True, 'ok', True)`。`find . -type f | grep scripts/lumos` 也實際得到 `True`，只列檔名即可過關。  
來源分類：原有漏看／原 C1 修復未完成；舊判準與修後判準對第一個案例都回 `True`。  
最小修法建議：先把上述兩例加入壞例。不要再疊 shell 字串排除規則；原始 stream 已有以 `tool_use_id` 關聯的 `tool_result` 結構，可考慮用原生 Read/Grep 的結構化路徑，並讓歷史 Bash grep/sed 以其成功結果中的目標程式證據判定。若本輪不擴充結果資料，應把歧義場次列為不算分。

R2C2 修後判準要求命令逐字帶 `scripts/lumos`，在 `scripts` 目錄用相對路徑讀同一支程式會被誤判未讀碼。  
severity: major  
blocking: 是  
引句:「修復試行 C1: 只列檔或讀文件不能冒充讀碼;保護原生工具與 shell 的正常讀碼。」  
file: `governance/scenarios/paraphrase.jsonl:4`  
file: `scripts/test_lumos.py:36749`  
最小翻紅重現：執行 `grade(v04, [("Bash", "cd scripts && cat lumos")], "這是帳本檔案白名單")`；預期 `True`，實際 `(False, "沒敲到期望指令: […]", True)`。同一輸入套舊判準實際為 `True`。  
來源分類：修復引入；合法讀碼由修前綠變成修後紅。  
最小修法建議：與 R2C1 同根因處理；不要為 `cd`、管線及各種 shell 寫法逐層補 parser。以結構化工具路徑和已關聯的工具結果建立證據；方案細節未定。

已讀範圍：正式審材 `governance/review-reports/code-repair-pilot-01/r2-snapshot.patch` 中 production、測試、題庫及相關圖譜，輔助修復差異 `r1-postfold.patch`，並查讀 `scripts/scenario_probe.py` 呼叫與衍生輸出路徑。`python3.14 scripts/test_lumos.py -k probe_` 實跑 110 passed、0 failed；上述兩條反例均另行本機重現，未呼叫外部模型、未改檔。

資料五問：新舊互讀命中 R2C2；新判準版本有分版，但合法舊輸入被新判準拒絕。寫一半路徑已讀，無 finding。衍生資料命中 R2C1、R2C2；誤判會流入總結、逐題統計、輸出 JSON 與 history。時間口徑已讀，無 finding。不可逆與外部副作用已讀，無 finding。

圖譜固定席逐條回覆：

- `Systems/codex-harness`：R2C1、R2C2。
- `Systems/測試假綠形態`：R2C1；新增壞例未覆蓋「搜尋字串恰為目標路徑」及只列檔名的現場。
- `Systems/bound-tests-gate`：已讀，無 finding。
- `Systems/canary-audit`：已讀，無 finding。
- `Systems/design-loop`：已讀，無 finding。
- `Systems/guard-kill`：已讀，無 finding。
- `Systems/lumos-cli-lifecycle`：已讀，無 finding。
- `Systems/slim-get-一行安裝`：已讀，無 finding。
- `Systems/slim-install-安裝器`：已讀，無 finding。
- `Systems/slim-uninstall-一行卸載`：已讀，無 finding。
- `Systems/lumos-cli-read`：已讀，無 finding。
- `Projects/規格落成可驗收條件_計劃`：已讀，無 finding。
- `Projects/逃逸自動記_計劃`：已讀，無 finding。
- `Systems/lumos-deinit`：已讀，無 finding。
- `Systems/check-r-guard`：已讀，無 finding。
- `Systems/節點範圍與索引守衛`：已讀，無 finding。
- `Systems/cochange-guard`：已讀，無 finding。

總結：最嚴重 severity major；blocking 2 條。
