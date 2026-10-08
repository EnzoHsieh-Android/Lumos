severity: minor

F1
severity: minor
blocking: 否
引句:「+  - scripts/test_lumos.py」

新節點把共用測試 runner 登記成自己的 `about_code`，但它已有既定的 Systems 家。這造成所有權與 impact 路由不一致：實跑 `lumos impact --file scripts/test_lumos.py` 時，家仍是 `Systems/測試假綠形態`，`Systems/review-convergence-eval` 只經 MOC 成為 hop2；未來修改這四個 eval wrapper 時，不會直接帶出 eval 節點脈絡。

file: `CLAUDE.md:62`
file: `docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md:11`
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:64`
file: `governance/review-reports/code-review-convergence-eval/r2-graph-lens.txt:10`

建議只從新節點的 `about_code` 移除 `scripts/test_lumos.py`，正文改連到既有測試家；實作模組、專屬測試與說明文件仍留在新節點。

F1 端點證據：

- input：兩端 `Systems/review-convergence-eval.md` 第 7–13 行。
- expected／case_source：`CLAUDE.md:62` 的一檔一家規則，以及 graph lens 指定的既有家。
- before command：`git show 8950308b71969f95119c7b2780f7a9ef93f669ac:docs/lumos-toolchain-knowledge/Systems/review-convergence-eval.md | nl -ba | sed -n '7,13p'`
- after command：同命令改用 `c909bf980125dc90f1696372205e322e2ac877c7`。
- cwd：`/private/tmp/lumos-future-repair-regression-research`
- 實際載入：before 文件 SHA `bf08a6da…ba7`；after 文件 SHA `149089c6…43`。
- 前提：固定 base `ce4c30f9…75da` 不存在該新節點，`git cat-file -e` rc=128。
- before：executed=yes、rc=0，原始輸出第 11 行為 `- scripts/test_lumos.py`。
- after：executed=yes、rc=0，原始輸出相同。
- 可比性／歸因：兩端命令與欄位相同；因此它由整體投稿新增，但不是 `8950308b..c909bf98` 修補誘發。

修補三問：

1. 原問題有沒有修好：就固定的 20 個案例而言有。before 為 5 failures＋3 errors，after 為 20/20 OK。
2. 之前正常路徑是否仍成立：固定案例中 12 個原有保留候選在 after 仍通過；只證這 12 個案例。
3. 新增問題能否歸因修補：F1 兩端都存在，不能歸因於 r2 修補。本鏡頭未找到其他可重現的修補誘發缺陷。

共用成對案例證據：

- input：兩端固定產品樹中的 `review_convergence.py`。
- expected／case_source：同一份 after 測試來源 `governance/eval/test_review_convergence.py`，SHA `6af875e4…029b`。
- command：Python 3.14.6 執行 `r2-paired-cases.json` 內 SHA `b2b47cb5…a6e63` 的 importlib probe，依端點載入產品模組後跑同一 unittest module。
- before cwd：`…/review-eval-source-restore-d0_i6ykl/before`
- after cwd：`…/review-eval-source-restore-d0_i6ykl/after`
- before 實際模組 SHA：`6e7b04fc…2dc4`，executed=yes，rc=1。
- after 實際模組 SHA：`f1e5df1e…933c`，executed=yes，rc=0。
- before 原始輸出：`r2-paired-before.log`，SHA `6827d98a…8cb0`，`FAILED (failures=5, errors=3)`。
- after 原始輸出：`r2-paired-after.log`，SHA `61ea6056…2c83`，`Ran 20 tests`、`OK`。
- 我另以 `git show <commit>:<path> | shasum -a 256` 重算三個來源 SHA，均與紀錄相符。
- 可比性：相同 Python、平台、測試來源、無網路；只替換固定產品端點。
- 歸因界線：修補與 case 字典重構同提交，不能分離個別效果；不證 Windows、未來模型收斂或完整產品樹無回歸。
- 獨立重跑未執行：指定 `architecture-tmp` 在本席唯讀 sandbox 無法建立，`mkdir` 回 `Operation not permitted`；沒有改去其他目錄。

圖譜硬合約逐條回答：

1. 修 bug 翻紅釘須證明現場成立：固定 probe 明確列印實際模組與 case SHA；20 案例有 before-red/after-green。限於列出的案例。
2. bound-tests 必須真跑且可過濾：四個 wrapper 名稱可過濾、會呼叫子程序；after 的 bound-tests gate 本席未能重跑，保留未判定。
3. canary record/second 落盤可讀回：未改相關路徑，不作重新驗證主張。
4. second telemetry 不影響 gate：未改相關路徑。
5. guard-kill rc 優先序：未改相關路徑。
6. guard-kill JSON 純度：未改相關路徑。
7. `.ps1` ASCII-only、無 BOM：Windows 原生驗證依指示排除；檔案未改。
8. `.ps1` 不得使用 `$Args`：同上。
9. CLAUDE 注入原地保留外部內容：未改。
10. 注入冪等：未改。
11. 完整版區塊位元組備份：未改。
12. 安裝寫 manifest：未改。
13. 注入前目標守衛：未改。
14. `.cmd` 直譯器不得寫死：未改。
15. Windows `lumos`／`lumos.cmd` 雙碰撞偵測：未改；原生驗證排除。
16. 卸載 bin 前內容比對：未改。
17. 四項清理互不阻擋：未改。
18. skill 移除前備份：未改。
19. CLAUDE sentinel 精確還原：未改。
20. `.cmd` 與主 script 獨立移除：未改。
21. 卸載清 manifest：未改。
22. search 排除 superseded、不排 stale：未改。

py-memory 表態核對：`tension / chosen=suggested` 與 after 實作一致。ledger/trial 索引上限 16 MiB、manifest 1 MiB、receipt 256 KiB，receipt 解析後只投影比較欄位；鄰居的直接 `read_text` 是舊做法，未發現因此形成第二個產品行為入口，故不升 major。

實讀範圍：

- 完整：`CLAUDE.md`、`lumos-project-notes/SKILL.md`、`r2-snapshot.patch` 1–1235、`r2-graph-lens.txt` 1–69、`docs-repair.txt` 1–73、`r2-paired-cases.json`。
- 定向：r2 dispositions 的 py-memory、repair binding 欄位、paired logs 的案例結果行、repair patch 的檔案／hunk 索引、三支鄰居 eval 的讀檔段落、涉及 finding 的 Systems 行。
- 未讀：所有 r1 席報告與 intake、歷史報告正文、完整歷史測試 log；Windows 原生未驗。
- repo 未寫入。單一家族架構鏡頭不保證沒有其他回歸。

最高等級：minor
阻擋條數：0