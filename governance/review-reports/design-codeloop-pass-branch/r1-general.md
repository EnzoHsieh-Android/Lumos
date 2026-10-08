severity: major

severity: major
blocking: 是
引句:「工具應維持 `skip`、`dispositions`、`check` 的既有語意和守衛要求」
finding: 設計只替 `pass` 增加目的分支參數，卻保留 `skip` 只能寫 checkout 分支；兩者目前共用同一寫入路徑，而 pre-push 明示 `skip` 是缺留痕時的合法出口。因此在 feature checkout 推 `HEAD:main` 時，選擇刻意不審仍會把紀錄寫到 feature，main 的推送閘繼續判無留痕。file: `scripts/lumos:36036` file: `scripts/lumos:37630` file: `scripts/hooks/pre-push:425`
最小重現: 未能重現（唯讀席未建立臨時 repo）。按設計實作後，在 feature 分支執行 `lumos code-loop skip --note intentional`，再執行 `lumos code-loop check --diff main..HEAD --at-sha "$(git rev-parse HEAD)" --branch main --repo .`；預期仍回 rc1。應讓 `skip` 同樣接受並驗證 `--branch`，或明確改掉 pre-push 對此流程的可用出口承諾。

severity: major
blocking: 是
引句:「編排者應先加最小回歸測試並觀察 S1／S2 翻紅」
finding: 驗收只直接呼叫 `code-loop check --branch main --at-sha …`，沒有走實際故障入口 `git push HEAD:main`。現有 pre-push 測試把遠端分支設成目前 checkout 分支，因此即使掛鉤日後漏傳目的分支或錯取 checkout 分支，S1／S2 與原有子集仍可全綠，真實推送仍會被擋。file: `scripts/hooks/pre-push:397` file: `scripts/hooks/pre-push:405` file: `scripts/test_lumos.py:16704`
最小重現: 未能重現（唯讀席未建立臨時 remote）。在候選實作上把 pre-push 的 `--branch "$_rbranch"` 改成 checkout 分支；依目前設計所列直接 CLI 測試與既有 pre-push 同名分支案例仍會通過，但從 feature 執行 `git push origin HEAD:main` 會因查錯 marker 而翻紅。S4 應加入真 remote 的 `HEAD:main` 端到端回歸，先證明舊版被擋，再證明 `pass --branch main` 後放行。

分支名正規化與 marker 身分碰撞修法：已讀，無 finding。回退、完整提交綁定與試行隔離：已讀，無 finding。
