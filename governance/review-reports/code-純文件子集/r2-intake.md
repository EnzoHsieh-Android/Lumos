# r2 收貨(2026-09-18;四個全新席看第一輪折法;外家仍缺席:Codex 額度用盡至 2026-09-19 21:45)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| C1 | 正確性-r2-sonnet | blocker | HIT:`--suite keys --keys _range_base --shard 3/4` rc1「一支測試都沒分到」 | 折:執行器帶 --suite 時空片回 0 並說「沒分到(別片有跑)」;沒帶 --suite 的空片照舊擋;斷言兩邊 |
| B1 | 邊界與輸入-r2-sonnet | blocker | HIT:LUMOS_TEST_SHARDS=abc → seq 零次、零測試回綠 | 折:片數不是正整數就串行;掛鉤真跑斷言只叫一次執行器 |
| B2 | 邊界與輸入-r2-sonnet | major | HIT:TMPDIR 不可寫 → _PP_TMP 空、路徑變根目錄 | 折:mktemp 失敗就擋並講明;掛鉤真跑斷言 rc1 |
| B3 | 邊界與輸入-r2-sonnet | major | HIT:-x.py → --keys -x 被 argparse 吃掉 rc2 | 折:同 S1 |
| A1 | 架構對齊-r2-sonnet | major | HIT(引句在 patch 外、機械重現:scripts/lumos 5716/5776 仍是 split("..")[0]) | 折:_sc_churn/_small_change_check 改 _range_base;結構釘 ⑤d |
| A2 | 架構對齊-r2-sonnet | minor | HIT:_run_group 是同檔唯一底線前綴函式 | 折:改名 run_group |
| S1 | 資安-r2-sonnet | major | HIT:-xx.py 的關鍵字整串以 - 開頭進 argparse → rc2 → 掛鉤當紅誤擋 | 折:_KEY_OK_RE 不准 - 開頭;案例⑤c |
