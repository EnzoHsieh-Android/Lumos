# 正式 r1 收貨與重現表

審材：`r1-formal-snapshot.patch`，SHA-256 `02c08f6f714de48446e232a8da34169ce096c71ddef3901dbe28914ad6cf4563`。以下 ID 只在各席內計數；「HIT」表示舊凍結版可重現且已折進 S11–S13，「MISS」表示未能重現為本輪差異內的缺陷或超出已明示邊界。原報告一律保留，不改席的文字。`r1-formal-*` 採用版均經 report-normalize、quote-check、refcheck、seat-check rc0，後者只出部分席未明講審材的觀測提醒，無越界引句。

| 席／報告 ID | 重現 | 處置與證據 |
|---|---|---|
| 正確性 F1 | HIT | 非零／缺檔事故跨執行洗白；`t_probe_boundary_formal_dispatch_fail_closed` 先紅後綠，折 S11。 |
| 正確性 F2 | HIT | 1000 runs 突破 50 場窗口；同測試先紅後綠，折 S12。 |
| 正確性 F3 | HIT | 真進程父程序被殺而子程序仍落檔；`t_probe_boundary_formal_parent_killed_child_continues`，折 S11。 |
| 正確性 F4 | HIT | 歸檔中斷注入未確實發生；`t_probe_boundary_postreview_archive_interrupt` 加注入斷言，折 S13。 |
| 併發 F1 | HIT | 與正確性 F3 同因，真進程反例折 S11。 |
| 併發 F2 | MISS | 目錄被對手改名時 inode 鎖仍鎖舊目錄，反例本身成立；原驗證 `valid_under` 逐字排除「被對手任意改名的輸出目錄」，故不是本輪合作進程範圍內的回歸。若部署到共用目錄須重驗，入口在 Systems/ablation-lumos-first 與計劃回退節。 |
| 併發 F3 | HIT | 與正確性 F2 同因，折 S12。 |
| 邊界 finding 1 | HIT | 與正確性 F1 同因，折 S11。 |
| 邊界 finding 2 | HIT | `passed` 字串及計分欄位錯型，可誤算或崩潰；定向錯型反例折 S13，歷史非 dict 雜項仍逐列跳過。 |
| 邊界 finding 3 | HIT | 非法／重複 arms 會重派或導出 log；入口拒絕測試折 S12。 |
| 邊界 finding 4 | HIT | 與正確性 F3 同因，折 S11。 |
| 邊界 finding 5 | HIT | 與正確性 F4 同因，折 S13。 |
| 邊界 finding 6 | HIT | tombstone 再次落檔失敗會留下成功外觀檔；前置未完成標記持續阻止合併，折 S11；仍需故障注入到此精確點。 |
| 資料 D1 | HIT | 與正確性 F1 同因，折 S11。 |
| 資料 D2 | HIT | Markdown 沒失效告示；定向反例折 S13。 |
| 資料 D3 | MISS | 三檔不同代可重現，但 `git show 5ed04382:governance/eval/ablation_lumos_first.py` 已有三次分開寫檔（原版 322、361、363），本輪只改單檔原子替換；沒有跨檔交易合約或自動消費端。Python `os.replace` 官方僅保證一次成功替換的原子性。列為既存限制，計劃已寫新增跨檔消費端前的處置入口與 2026-11-04 回看，不把它假報成已修。 |
| 資料 D4 | HIT | 與邊界 finding 3 同因，折 S12。 |
| 資料 D5 | HIT | 頂層／逐列 arm 不一致會歸錯實驗臂；定向反例折 S13。 |
| 資料 D6 | HIT | 純合併覆寫舊 provenance；`t_probe_boundary_formal_input_validation` 折 S14，舊版已錯覆的逐場版本無法反推。 |
| 資安 F1 | HIT | 相對 out-dir 鎖與落檔位置分離；定向反例折 S12。 |
| 資安 F2 | HIT | 空題號／逗號／前綴擴題；精確選題 dry-list 反例折 S12。 |
| 資安 F3 | HIT | arms 可導出 log；與邊界 finding 3 同因，折 S12。 |
| 資安 F4 | HIT | 題號可注入控制字元與 Markdown；入口拒控制字元、呈現時轉義，折 S12–S13。 |
| 外家 finder F1 | HIT | 父死子活；真進程反例折 S11。 |
| 外家否決 F1 | HIT | 父死子活；真進程反例折 S11。 |
| 外家否決 F2 | HIT | Markdown 未標不可採信；定向反例折 S13。 |
| 架構／規格符合 | clean | 原席 v2 文字與凍結快照逐字引句已核對。 |

辯方獨立核對 D3、併發 F2、D6：前兩項對「本輪新增 blocking」為 MISS；D6 雖早已存在，對資料語意是真缺陷，本輪已修。資料版位只有單檔原子替換，不推論跨檔同代或斷電安全。正式 canary 處置記帳、最終版新席與回放仍未完成，本 intake 不能代替 PASS。

更正記帳時，一輪只留一筆彙總 carrier；`../probe-postreview-dispatch-rebook/r1-aggregate.md` 將重複原席項收成下列七個處置 ID。原本 `code-probe-postreview-dispatch` 同輪九席各帶處置清單，被 `loop status --disposal` 明確拒絕；不可撤的原帳留作程序事故，新的 `code-probe-postreview-dispatch-rebook` 沿用同一凍結快照與原席報告，但只由彙總 carrier 帶處置清單。

第二本 `code-probe-postreview-dispatch-rebook` 雖改成單 carrier，記帳時 `--spec` 指到活計劃而不是凍結 patch，問閘以 G3 hash 拒絕。第三本 `code-probe-postreview-dispatch-ledger` 保留相同審查報告與本彙總，但 `--spec` 與 `--snapshot` 都指到原凍結 patch；派工快照依工具的目錄慣例放在 `governance/review-reports/code-probe-postreview-dispatch-ledger/r1-dispatch.json`。前兩本僅供追溯，不作 PASS 依據。

| 彙總 ID | 重現 | 對應處置 |
|---|---|---|
| G1 | HIT | 事故持久性與父死子活，折 S11。 |
| G2 | HIT | 窗口剩餘額度，折 S12。 |
| G3 | HIT | 精確單題選取，折 S12。 |
| G4 | HIT | 組別白名單、相對輸出路徑與呈現，折 S12。 |
| G5 | HIT | 結果欄位與跨組校驗，折 S13。 |
| G6 | HIT | Markdown 失效告示與純合併來源，折 S13–S14。 |
| G7 | HIT | 故障注入現場成立，折 S13。 |
| CONC-F2 | MISS | 任意改名輸出目錄超出原本合作進程邊界；重啟入口已記。 |
| DATA-D3 | MISS | 三檔不同代為基線既有，沒有跨檔消費合約；重啟入口與日期已記。 |
