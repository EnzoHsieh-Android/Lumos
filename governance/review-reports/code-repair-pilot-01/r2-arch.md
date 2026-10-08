severity: clean
審材: `governance/review-reports/code-repair-pilot-01/r2-snapshot.patch`；輔助: `governance/review-reports/code-repair-pilot-01/r1-postfold.patch`

severity: clean

R2A1 分層與依賴方向  
severity: clean  
blocking: 否  
引句:「儀器層的覆寫(用量上限/截斷/退出碼)由呼叫端在這之後做。」  
file: `scripts/scenario_probe.py:93`  
對齊。共用 `grade` 維持判分層，Claude runner 在既有執行器邊界處理退出碼，沒有跨層直呼。

R2A2 命名與錯誤處理  
severity: clean  
blocking: 否  
引句:「儀器例外: claude -p 退出碼 {returncode}(這場不算分)」  
file: `scripts/scenario_probe.py:561`  
對齊。沿用既有「儀器例外」前綴作為摘要排除契約，且保持用量上限、截斷優先分類。

R2A3 第二種做法  
severity: clean  
blocking: 否  
引句:「本次保留既有 regex 題庫與 runner 分層，只要求這道常數題指向目標程式檔，不增加 shell 解析器」  
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:83`  
對齊。修復延用題庫 regex、共用 grader 與既有 runner，沒有新增解析器、結果格式或第二套錯誤分類機制。

Python 慣例：已讀，無 finding。

R2G1 `Systems/codex-harness`：已讀，無 finding。  
R2G2 `Systems/測試假綠形態`：已讀；既知待折項不重複，本席無新增 finding。  
R2G3 `Systems/bound-tests-gate`：已讀，無 finding。  
R2G4 `Systems/canary-audit`：已讀，無 finding。  
R2G5 `Systems/design-loop`：已讀，無 finding。  
R2G6 `Systems/guard-kill`：已讀，無 finding。  
R2G7 `Systems/lumos-cli-lifecycle`：已讀，無 finding。  
R2G8 `Systems/slim-get-一行安裝`：已讀，無 finding。

總結：最嚴重 severity clean；blocking 0 條。
