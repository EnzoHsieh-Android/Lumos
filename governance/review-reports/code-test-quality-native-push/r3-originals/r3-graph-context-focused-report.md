severity: minor

審查狀態：範圍受限。本輪工具輸出閱讀至少 1,856 行，已超過 1,800 行上限；以下是已完成部分的有效結果，但不能冒稱完整席審或整體無回歸。後續需拆席續審。

## Finding 1

severity: minor  
blocking: 否

新增的圖譜前綴行沒有符合本輪 AGENTS 規定的必要欄位：9 條新增 `PITFALL:` 全部缺 `[根因:]`；2 條新增 `WHY:` 中有 1 條缺 `[出處:]`、`[因:]`。目前 `lumos lint` 全綠，表示現行檢查沒有攔住這個新格式要求。

引句：「PITFALL: 檔案都存在仍可能新舊混裝，同時間戳同大小的 bytecode 也曾讓新來源執行舊判讀」

佐證 file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:142`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md:98`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md:100`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:117`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:119`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:50`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:52`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:54`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:56`  
佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-multilang.md:48`

- input：598e41b…→03a46da… 的六份 focused 圖譜文件。
- expected：依 AGENTS 必要欄位表，`PITFALL:` 需有 `[出處:]`、`[根因:]` 及防回歸欄；`WHY:` 需有 `[出處:]`、`[因:]`。
- before：這些新增行不存在。
- after：`added_pitfall=9 with_root_field=0 added_why=2 with_source_and_reason_fields=1`。
- 判準命令：在 `/tmp/lumos-readme-oct-audit` 執行指定兩版本的 `git -C … diff --unified=0 … | awk …`，rc 0。
- 產品核對：HEAD 為 03a46da6…，before/after tree 分別為 `db550fcc…`、`8aeb81d6…`，與 binding 一致。
- comparison/attribution：這是修後新增圖譜文字的形狀問題，不代表相應產品修復失效，也不是既有歷史內容的回歸。
- case_source：`graph-context-focused-repair.patch` SHA-256 `4f37919989b9fe29eb1f6fcf9784c0a9a74e678423270e74d46ce29323016ebd`。

## Finding 2

severity: minor  
blocking: 否

新部署計劃的 S1–S3 雖標成可人工驗收，但第二輪驗證紀錄沒有透過 `plan_refs` 指回這份計劃；`lumos spec-trace` 因而顯示三條舊制回指皆未認領。這不推翻既有測試結果，但讓「哪份驗證驗了這三條」無法從計劃追溯。

引句：「當 test-quality 配套缺檔、混裝或來源不可讀時，CLI 應在執行收證命令前回退出2」

佐證 file: `docs/lumos-toolchain-knowledge/Projects/測試品質部署配套校驗_計劃.md:28`  
佐證 file: `docs/lumos-toolchain-knowledge/Projects/測試品質部署配套校驗_計劃.md:29`  
佐證 file: `docs/lumos-toolchain-knowledge/Projects/測試品質部署配套校驗_計劃.md:30`  
佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:11`  
佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:18`

- input：新計劃及第二輪驗證紀錄。
- expected：驗證紀錄以 `plan_refs` 指回它實際驗收的計劃。
- before：計劃不存在；搜尋 rc 1。
- after：計劃存在且被父計劃、系統節點引用；搜尋 rc 0，但驗證紀錄的 `plan_refs` 仍只列原工具接線計劃。
- 實跑：`python3 scripts/lumos spec-trace 'Projects/測試品質部署配套校驗_計劃'`，rc 0；結果為「3 條款／靠人 3／舊制回指未認領 3」。
- comparison/attribution：屬新增計劃的追溯缺口，不表示 S1–S3 未曾執行，也不把缺回指當產品紅燈。
- case_source：after tree `8aeb81d62fb6069bef85a39cd1d12b8777425600`。

## 修訂三問

1. 原問題修復效果：圖譜已補入混裝、舊 bytecode、UTF-16 DTD、孤立 suite failure、全域 `--vault`、副檔名分類與快取外逃等決策背景，且部署計劃明確限制「只證配套一致，不證業務答案或報告真實性」。修復方向成立，但有上述欄位形狀及計劃回指缺口。

2. 正常／錯誤／相鄰路徑：S1 對缺檔與混裝，S2 對正常配套與 stale bytecode，S3 對全域 `--vault`、`--help`、`--version`。固定版本靜態核對顯示 `scripts/lumos` 先驗證 bytes、再從同批 bytes `compile`，錯誤時註冊佔位入口；本席未實跑產品案例，因此只判定文件與接線存在，不判定執行行為通過。

3. 新發現同案例前後：修前沒有這批圖譜行；修後新增 9 條 `PITFALL:`，但 9 條皆漏必要 `[根因:]`。新計劃修前不存在，修後 S1–S3 存在，但三條驗證回指仍未認領。

## 正向修復與保留主張

- 原生資格邊界保留：驗證只認定 macOS CPython、針對性控制及既有五棧卷證重播；明載未重跑 Android/iOS，Windows 接入需另驗。佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:5`、`:20`、`:28`。

- 沒有改寫歷史結論：六份 focused 修訂共新增 80 行、刪除 0 行；既有 deinit Windows EOFError 歷史資格仍保留，新快取控制另行限定 POSIX、沒有 Windows 原生資格。佐證 file: `docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md:98`、`:100`。

- 治理流程沒有被冒稱全驗：第二輪驗證對 graph-sync 等節點明載只核對共用副檔名清單一致性。佐證 file: `docs/lumos-toolchain-knowledge/Verification/測試品質分支第二輪修復驗證.md:26`。

- 固定版本接線靜態成立：配套 digest、受限讀取、同 bytes 編譯、失敗回復 `sys.modules`、結構化 rc 2 路徑均存在。佐證 file: `scripts/lumos:49227`、`scripts/lumos:49242`、`scripts/lumos:49265`、`scripts/lumos:50290`。未執行，不升格為行為通過。

## 固定圖譜鏡頭逐項

| 節點 | 本輪判定 |
|---|---|
| Issues/vendored測試套件在消費端假紅 | focused delta 未涵蓋；沿原席資格，不重審 |
| Systems/lumos-cli-lifecycle | 本輪有其他席分擔的變更；未重審 |
| Systems/lumos-deinit | 已審；新增快取邊界，明確排除 Windows 原生資格 |
| Systems/lumos-cli-read | focused delta 未涵蓋；合約未重新驗證 |
| Systems/bound-tests-gate | focused delta 未涵蓋；合約未重新驗證 |
| Systems/guard-kill | focused delta 未涵蓋；合約未重新驗證 |
| Systems/授權與歸屬 | focused delta 未涵蓋；合約未重新驗證 |
| Systems/測試假綠形態 | 未改；本輪沒有重跑其破壞測試 |
| Systems/pitfalls-code-loop | 未列入 focused 範圍 |
| Systems/design-loop | 未列入 focused 範圍 |
| Systems/reversibility-governance-ledger | 有變更但由其他席分擔 |
| Systems/loop-convergence-recording | 未列入 focused 範圍 |
| Systems/doctor-irreversible-hint | 未列入 focused 範圍 |
| Systems/lumos-refcheck | 未列入 focused 範圍 |
| Systems/check-t-sentinel | 未列入 focused 範圍 |
| Systems/check-r-guard | 未列入 focused 範圍 |
| Systems/節點範圍與索引守衛 | 未列入 focused 範圍 |
| Systems/cochange-guard | 有變更但由其他席分擔 |
| Systems/canary-audit | 未列入 focused 範圍 |
| Systems/slim-get-一行安裝 | 未列入 focused 範圍 |
| Systems/slim-install-安裝器 | 未列入 focused 範圍 |
| Systems/slim-uninstall-一行卸載 | 未列入 focused 範圍 |
| Projects/規格落成可驗收條件_計劃 | 未列入 focused 範圍 |
| Projects/雙向門放行_計劃 | 未列入 focused 範圍 |
| Projects/引用座標依實際換行_計劃 | 未列入 focused 範圍 |
| Projects/逃逸自動記_計劃 | 未列入 focused 範圍 |
| Projects/異常派工單回報輸入錯誤_計劃 | 未列入 focused 範圍 |
| Systems/judge-severity-gate | 未列入 focused 範圍 |
| Systems/core-invariant-baseline | 未列入 focused 範圍 |

額外 focused 節點：`retrieval-ranking`、`test-quality-cli`、`test-quality-multilang` 及新部署計劃均已審；新增驗證連結沒有擴張原生資格，但存在 Finding 1、2。

## 來源與範圍

binding 必要欄原樣：

```json
"before_provenance": "R2 base_commit 598e and corrected original 5d8..598e repair regenerated byte-equal; preserve original material limitations."
```

```json
"Includes product repairs, moved tests, mechanical classifiers, graph decision context and historical report archival; ancestor alone does not establish causality."
```

指紋：

- `binding-source.json`: `52c39bf8612d87bdfb2d383e28d55842a0e9586275e6487e9de4bcd43e227ddc`
- `r3-repair.patch`: `f1060f6bb27ea33a312fedd768d0e26ba1f9117521a87dfa5c8422d2dc34a2e3`，與 binding 相符
- `graph-context-focused-full.patch`: `70f7ea14e1590b18d7e5e2a3103d4c685fae1464b69faf9306a3f4ed6f6309cd`
- `graph-context-focused-repair.patch`: `4f37919989b9fe29eb1f6fcf9784c0a9a74e678423270e74d46ce29323016ebd`
- 固定鏡頭：`54e26b2dd342fafe742b47a5fcf12487e030f1be2de1ee9bad77ed6ea474b93e`

實際覆蓋：六份 focused 圖譜文件、第二輪驗證紀錄作必要上下文、`scripts/lumos` 的配套載入與 deinit 快取完整 helper／必要呼叫點、CLAUDE 規則、skill 與固定鏡頭。

未驗：Windows 原生、任何產品行為測試、完整 74 檔重審、r1/r2 席報告及 intake、其他席負責文件、百萬行完整 snapshot 內容。`r2-behavior-cases.json` 未讀、未當結論；沒有把收集失敗當產品紅，也不保證整體無回歸。

因閱讀總量已超限，若要形成可供 push 使用的完整席結論，需把後續拆成「固定鏡頭未變節點」或「入口／manifest 核對」其中一個獨立範圍。