# r2 凍結差異收貨與重現

審材 `r2-snapshot.patch` SHA-256 `741847879e42e51e80e26944d244d1123681d1d7b0a179353af09424f798ee21`，658 行。原報告 9 席，架構席 clean；修正版只調格式或引句，原稿保留。`report-normalize`、`quote-check`、`refcheck`、`seat-check` 均已逐席執行；架構席 quote-check 採原席重發的 `r2-architecture-v2.md`。`seat-check` 的 unreported 是唯讀範圍觀測，out_of_scope 均為零。

| 原 finding | 觀察重現 | 處置組 | 證據與判準 |
|---|---|---|---|
| E1 | HIT | G1 | rc2 子程序先寫成功外觀 JSON；只歸檔 pending 後 `needed` 由 1 變 0。候選檔先寫、驗證後才原子升正式 JSON。 |
| K1、規格席第1條 | HIT | G2 | 要求 2 列只回 1 列，舊碼移除 pending、`needed=1`；改成列數須精確相等。 |
| K2 | HIT | G3 | 1 列含 2 筆 retry，舊窗口計 1 而非 3；實際探針重試達額度後零新增模型呼叫。 |
| C1、C2、D1、資安席第1條、規格席第2條、邊界席第1條 | HIT | G4 | 錯型 reason／健康欄／fatal、非物件列均可讓同檔成功列抵缺場；以精確型別及整檔拒收修正。邊界席的「半寫 JSON 可過」影響描述過強；外家辯方 `r2-boundary-defender.txt` 確認 S13 違規，但部分寫入的非法 JSON 會被既有掃描擋住。 |
| C3、E2、V1、V2、資安席第2條 | HIT | G5 | 空白、C1／Unicode 控制字元與重複題號原可入派工；短線題號以分離選項給 argparse 會報錯。入口拒絕不可列印／重複題號，合法短線題號改用 `--exact-id=<值>`。 |
| E4 | HIT | G6 | 舊歸檔中斷測試只檢 pending，拿掉 fatal tombstone 仍可能綠；新斷言直接驗正式 JSON 已是 fatal。 |
| V3 | HIT | G7 | A 題多 2 列可遮住 B 題缺 1 列；改逐題加總缺場。這是凍結差異前已有的錯誤，一併折入。 |
| 規格席第3條 | HIT | G8 | `{}` meta 會印 `None`／`?`，沒有標未知；只補缺欄、不改完整歷史來源。 |
| E3 | HIT | G9 | `notes.json`、`with.json` 無 arm 會把整個目錄判壞；只掃本工具的 `with-`／`without-` 正式結果檔，舊 shard 檔仍涵蓋。 |

G1–G9 均已用定向反例折入程式或測試，無接受風險、無 MISS。`t_probe_boundary_formal_second_round_regressions` 在修前 14 條紅燈；`test_load_results_skips_bad_json` 修前紅；修後定向、探針額度與舊測試詳見圖譜 Verification。原報告對同一缺陷的不同鏡頭不另灌不同缺陷數。
