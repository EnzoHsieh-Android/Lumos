severity: minor

### PF-1

severity: minor  
blocking: no

引句:「同repo既有_nodehome_required/side/route_groups是借用入口，不新建解析器。」

觀察：現碼沒有 `_route_groups` 或 `route_groups` 這個符號。實際入口是 `_nodehome_commit_groups` 產生逐提交群組、`_nodehome_mark_note_content` 補上 `content_notes`，再由 `_nodehome_evaluate(..., groups=...)` 消費。`side` 也實際對應 `_nodehome_side`。這不妨礙候選實作，但凍結計劃的既有機制指標不能直接定位。

判準：實作前計劃宣稱借用既有機制時，名稱應能對到真實符號或明確標成概念名，避免實作者另找或誤建第二套分組。

佐證 file: `scripts/lumos:27401`、`scripts/lumos:27444`、`scripts/lumos:27506`、`scripts/lumos:27971`

建議：把原句改成 `_nodehome_required/_nodehome_side/_nodehome_commit_groups + _nodehome_mark_note_content`；不需改方案。

### 四項前掃

1. 未定義詞：除 PF-1 外無阻擋項。`include_tests` 已明寫為本案新增、預設關閉的選項，不當成既有 API。
2. 壞引用：未發現。五條驗收引用的測試函式均存在；`Systems/每支檔有家` 與兩份相關計劃均存在。Git 官方文件也支持索引／提交端點、`--name-status` 和 `-z` 的描述。[Git diff 官方文件](https://git-scm.com/docs/git-diff)
3. 範圍自相矛盾：未發現。提案只擴大 S13 的可核對路由視圖；`reqN/reqB`、`code_touched/g_code` 啟動、S13b、安家要求與純測試豁免均明確保持。
4. 既有機制語意：已開碼核對。現碼確實先由 `_nodehome_required` 排除測試，再以 `reqN/reqB` 算 `code_touched` 與逐提交 `g_code`，最後 S13 只拿該集合和家的 `about_code` 相交，因此混合提交只看見 `src/a.py`。候選在此增加獨立路由視圖可直接處理症狀，且不必改正式安家集合。佐證 file: `scripts/lumos:27105`、`scripts/lumos:27511`、`scripts/lumos:27527`、`scripts/lumos:27605`、`scripts/lumos:27612`、`scripts/lumos:27638`

### 測試與證據

- 當前 `scripts/lumos` SHA-256 仍是卷證綁定的 `52c9…f376`；相對基準提交，正式 CLI 沒有變更，只有新測試加入。
- 現有紅燈卷證是合成 Git fixture：24 格中 16 pass、8 fail；失敗恰為 mixed、deleted-test、renamed-test、diff-mixed 的普通／`-O` 兩版。其餘負控制、純測試與免安家格維持預期。
- 兩份三案例 counter 都呈現：混合提交 rc1、未改測試仍 rc1、純測試 rc0；不能把 fixture 說成實際審查輪數下降。
- 本席嘗試重跑 `python3.14 scripts/test_lumos.py -k nodehome_optional_test_home_writeback`，但唯讀環境在測試啟動前即因沒有可寫暫存目錄而停止；沒有產生新的測試結果，這不是產品紅燈。
- `lumos contracts` 對本案計劃、落點 System 與舊測試綁定計劃均回報無正式合約。既有 d4 決策只約束「有寫回時，需要家的改動檔仍須有家」，本提案未破壞它。

已讀路徑：

- `/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`
- `CLAUDE.md`
- `docs/lumos-toolchain-knowledge/MOC/index.md`
- `scripts/lumos`（指定 node-home 定點）
- `scripts/test_lumos.py`（完整新測試及相鄰路由控制）
- `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`
- `docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md`
- `docs/lumos-toolchain-knowledge/Projects/已宣告測試家的同次寫回_計劃.md`
- `governance/review-reports/test-home-writeback/preflight-plan-snapshot.md`
- `governance/review-reports/test-home-writeback/red.json`
- `governance/review-reports/test-home-writeback/red.log`
- `governance/review-reports/test-home-writeback/red-source-bind.json`
- `governance/review-reports/test-home-writeback/baseline-counter.json`
- `governance/review-reports/test-home-writeback/integration-counter.json`
- `governance/review-reports/test-home-writeback/counter-function-source-bind.json`
- `governance/review-reports/test-home-writeback/existing-reader-prompt.txt`
- `governance/review-reports/test-home-writeback/existing-reader-raw.md`
- `governance/review-reports/test-home-writeback/preflight-four-checks.json`
- `governance/review-reports/test-home-writeback/preflight-prompt.txt`
- `https://git-scm.com/docs/git-diff`