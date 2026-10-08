severity: clean

未發現新增 finding；修訂 spec 自身沒有矛盾，四組問題均已實質折入，原報告等級沒有被降級。

觀察與判準：

- 五席共同指出的中間提交缺口，已改為逐 group、按提交及父版建立 `route_tests`；S13 才使用它，原 `reqN/reqB`、`g_code` 啟動、安家與 S13b 維持不變。符合「只補合法分類、不重建全圖、不跨提交借證據」的界線。佐證：`governance/review-reports/test-home-writeback/r1-folded-snapshot.md:29`、`:31`；現碼入口 `scripts/lumos:26852`、`:27105`、`:27444`、`:27506`、`:27611`。
- `pure-test-other-home` 能殺掉錯把測試放進啟動集合的實作；它只改測試、寫 Production 正文，正確舊行為應維持 rc0。佐證：`scripts/test_lumos.py:47853`、`:47859`。
- shebang 正反控制確實製造索引／工作樹相反狀態：positive 是索引有 `#!`、工作樹沒有；negative 反之。兩方向及 `-O` 都會跑。佐證：`scripts/test_lumos.py:47849`、`:47875`、`:47893`。
- 中間刪除、一次改名、二次改名三案都建立真正的中間路徑，且不會靠整段端點取得該路徑。佐證：`scripts/test_lumos.py:47861`、`:47880`。
- 程序成本措辭已修正：不再宣稱沒有新程序，明列可能增加 `git show`／`git ls-tree`，並要求一／十提交收據。佐證：`governance/review-reports/test-home-writeback/r1-folded-snapshot.md:56`。
- 讀取失敗維持空 `route_tests` 並沿原拒收，沒有用未讀資料放行。佐證：`governance/review-reports/test-home-writeback/r1-folded-snapshot.md:31`。
- Windows 與全圖清帳仍明確排除。佐證：`governance/review-reports/test-home-writeback/r1-folded-snapshot.md:57`。

收據：

- 我未自行重跑測試：唯讀席無可寫暫存區。
- 父席新出現的綁源收據顯示正式 CLI SHA-256 仍為 `52c9…0276`，36 控制對舊碼為 `20 passed / 16 failed`、rc1；這是預期紅燈，不是實作已綠。佐證：`governance/review-reports/test-home-writeback/r1-fold-red-source-bind.json:2`、`:5`、`governance/review-reports/test-home-writeback/r1-fold-red.json:1`。
- 原24控制的 `16通過/8失敗` 敘述仍保留於修訂 spec，沒有被新收據覆寫。佐證：`governance/review-reports/test-home-writeback/r1-folded-snapshot.md:43`、`:71`。
- fold-check rc1 仍有提醒，不能稱作無提醒：具體是正文的「`--name-status給實際改動類型`」未出現在 summary。這篇 Project 本來沒有 summary 欄，因此視為 advisory，不要求手改 header。佐證：`governance/review-reports/test-home-writeback/r1-fold-checks.json:23`、`:28`、`:29`。

鏡像：已跟上。`r1-folded-snapshot.md` 與正式計劃逐位元一致，SHA-256 同為 `3f7052…dd16`；`scripts/lumos` 未改，只有計劃與候選測試有 diff。

完整已讀：

- `CLAUDE.md`
- `docs/lumos-toolchain-knowledge/MOC/index.md`
- `governance/review-reports/test-home-writeback/r1-fold-diff.patch`
- `governance/review-reports/test-home-writeback/r1-folded-snapshot.md`
- `governance/review-reports/test-home-writeback/r1-snapshot.md`
- `governance/review-reports/test-home-writeback/r1-logic.md`
- `governance/review-reports/test-home-writeback/r1-boundary.md`
- `governance/review-reports/test-home-writeback/r1-integration.md`
- `governance/review-reports/test-home-writeback/r1-resources.md`
- `governance/review-reports/test-home-writeback/r1-rollback.md`
- `governance/review-reports/test-home-writeback/r1-architecture.md`
- `governance/review-reports/test-home-writeback/r1-receiving.json`
- `governance/review-reports/test-home-writeback/r1-format-resubmission.json`
- `governance/review-reports/test-home-writeback/r1-fold-checks.json`
- `governance/review-reports/test-home-writeback/r1-intermediate-baseline-counter.json`
- `governance/review-reports/test-home-writeback/r1-preparation.json`
- `governance/review-reports/test-home-writeback/r1-fold-red.json`
- `governance/review-reports/test-home-writeback/r1-fold-red-source-bind.json`
- `governance/review-reports/test-home-writeback/r1-fold-red.log`
- 定點已讀 `scripts/lumos` 的 `_NodehomeSide`、`_nodehome_required`、`_nodehome_mark_note_content`、`_nodehome_evaluate` 及相鄰快照／reader 邏輯
- 定點已讀 `scripts/test_lumos.py` 的 fixture helpers 與 `t_nodehome_optional_test_home_writeback` 全方法