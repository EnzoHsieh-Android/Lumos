# code-過期鎖安全接手 r3 收貨與未結處置

兩個全新唯讀 `codex exec` 進程各自讀同一份 1,207 行累積快照 `r3-snapshot.patch`，SHA-256 `8a208ee6944eca15b1352a542a2aad6e36a520d9c70a264b6b54291d49c3a0c8`。收齊兩席前未改被審程式。兩份原報告已原樣保存，`report-normalize`、`quote-check`、`refcheck` 全過。此為第三輪上限，不把未修重大缺陷記成 accepted 或 folded。

| id | 重現 | 處置 |
|---|---|---|
| F1 | HIT：背景程序以 `LUMOS_LENS_WARMING=1` 與正確啟動者身份進場，快取早期命中回 rc 0，原 `.warming` 鎖仍存在；編排者在隔離暫存目錄再現 `owned_lock_left=True`。 | unresolved-major；獨立 Issue `Issues/背景快取命中留下暖機鎖`，本迴圈不放行 |
| F2 | HIT：`Popen` 注入 `OSError` 且無快取或替代持有者，回 rc 5／`lock_uncertain=true`，鎖已不存在；編排者獨立重現。 | unresolved-major；獨立 Issue `Issues/背景啟動失敗誤報逾時`，本迴圈不放行 |
| F3 | HIT：`fstat` 在獨佔建檔成功後失敗時，identity 尚無值，清理不刪空鎖；席位已在控制流重現，編排者確認對應路徑。 | unresolved-minor；後續須驗 S3 邊界與人工復原說明 |
| A1 | HIT：計劃 S4/S5 與測試 docstring／斷言 S3/S4 不一致，報告引句在快照中核實。 | unresolved-minor；後續修正測試說明 |

既有子集與上一版 `code-loop check` 全綠只覆蓋已寫出的案例，不覆蓋 F1/F2 的出口。第三輪處置閘須呈未通過；此分支不執行 `code-loop pass`、不推送。下一次修復以兩條 Issue 分開寫會翻紅的回歸測試，再由人裁新的審查範圍。
