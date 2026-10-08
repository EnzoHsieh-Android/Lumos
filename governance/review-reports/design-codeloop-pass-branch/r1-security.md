severity: major

## F1 — 治理帳失敗後，半筆 marker 仍會放行推送

severity: major  
blocking: 是

引句:「既有 `pass` 在沒有 `docs/` 或治理帳寫入失敗時仍可能只寫 marker，本案的 S1 驗收限可寫治理帳的 repo，不把這個既有缺口冒充已修。」

設計照字面實作後，`pass --branch main` 會先產生可供推送閘使用的 `main` marker；治理帳追加若因權限、磁碟滿或短寫失敗，現行函式會吞掉 `OSError`，命令仍印成功並回 rc0。之後本機 pre-push 優先讀 marker，會把這筆不完整寫入視為有效；乾淨 CI checkout 沒有 marker，卻找不到相同治理證據。這使同一次 `pass` 在兩個守衛面產生相反真相，也直接違反 S1 所稱 marker 與治理帳均寫入。

file: `scripts/lumos:36036` — `pass` 先 `_codeloop_write`，再寫治理帳，最後無條件回 0。  
file: `scripts/lumos:34484` — marker 是獨立直接寫入，沒有與治理帳形成共同成功條件。  
file: `scripts/lumos:34495` — `_codeloop_gov_log` 在 `OSError` 時直接吞掉失敗。  
file: `scripts/lumos:35833` — 判定側只要 marker 的 SHA、狀態吻合便放行。  
file: `scripts/hooks/pre-push:397` — pre-push 以遠端目的分支查這份 marker。

必須把治理帳成功變成 `pass` 的前置成功條件，例如沿用 dispositions 的「治理帳先寫、失敗回 rc2，再寫本機 marker」順序；並加入治理帳不可寫、追加失敗及 marker 寫到一半的失敗注入測試。單純把 S1 限縮到正常可寫環境，沒有關掉這條守衛旁路。

## F2 — 舊 marker 的碰撞判斷漏掉大小寫檔名別名

severity: major  
blocking: 是

引句:「舊 marker 沒有分支欄且請求名含 `/` 或 `__` 時也退讀治理帳，不能把檔名當身分。」

設計只在舊 marker 的請求名含 `/` 或 `__` 時拒絕把檔名當身分，但檔案系統本身還會製造別名。本工作樹 `core.ignorecase=true`，`scripts/LUMOS` 與 `scripts/lumos` 解析為同一檔案；同時 Git 的 `check-ref-format --branch` 對 `Main`、`main` 都回成功。

具體錯放路徑：

1. 升級前在 `Main` 對提交 X 留下不含 `branch` 欄位的 `Main.json`。
2. 升級後將同一提交 X 推向遠端 `main`；相對 `main` 的實際 diff 可以與原審查範圍不同。
3. pre-push 以目的分支 `main` 查留痕。
4. 大小寫不敏感檔案系統把 `main.json` 導向 `Main.json`；請求名不含 `/` 或 `__`，設計允許直接信任舊 marker。
5. SHA X 相同，守衛因此把另一分支的舊 pass 借給 `main`，放行未按 `main` 範圍審過的差異。

file: `scripts/lumos:34378` — 分支檔名只替換 `/`，沒有可驗證的唯一身分。  
file: `scripts/lumos:34383` — marker 存在時直接解析使用，不依治理帳的完整分支名核對。  
file: `scripts/lumos:34484` — 現有舊 marker 不保存原始分支名。  
file: `scripts/lumos:35833` — SHA 與狀態吻合即接受 marker。  
file: `scripts/hooks/pre-push:397` — 查詢名稱來自遠端目的分支，會以 `main` 查詢。

所有缺少 `branch` 欄位的 legacy marker 都不能證明其完整分支身分；應一律退讀治理帳或保守拒絕，而非只檢查 `/`、`__`。回歸案例至少應包括 `a/b`／`a__b`、`Main`／`main`，並在大小寫不敏感檔案系統執行。

其餘核對：S2 的空白、全名、`@{-N}` 與非法名稱拒絕策略可行；完整 HEAD SHA 仍由推送端 `--at-sha` 再核對。`skip` 的明示旁路及回退段未發現另一條獨立錯放路徑。

## 審材與風險類

- 凍結審材：`governance/review-reports/design-codeloop-pass-branch/r1-snapshot.md`
- SHA-256：`41c3f660ea703b68cca60f1ab3511189aad55252210aa5f8929caa13b246f8d2`
- 對照：`docs/lumos-toolchain-knowledge/Issues/code-loop-pass不能指定分支.md`
- 對照：`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- 對照：`scripts/lumos`
- 對照：`scripts/hooks/pre-push`
- 生效條件：修復穩定性試行計劃及 2026-10-04 改道生效驗證
- 風險類：守衛面、部分寫入、治理帳耐久性、版本綁定、分支身分碰撞、旁路、回退相容性
- 其他席報告：未讀
- 本席：唯讀，未寫檔或還原變更