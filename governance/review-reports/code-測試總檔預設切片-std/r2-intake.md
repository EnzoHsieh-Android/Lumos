# r2 收貨紀錄(code-測試總檔預設切片-std)

## 派工與收貨

- 2026-11-05 派兩席全新代理(正確性、架構對齊),材料:r2-repair-review.patch(修前 4efa74fb6 → 修後 c816c9f2a,排除卷證與帳本純追加;來源 r2-repair-binding.json),禁讀上輪席報告與 r1-intake。派工前修正關卡 `lumos loop fix-check code-測試總檔預設切片-std --round r1` 全部通過。
- 報告從子代理逐字稿取出;report-normalize 都已正規化;quote-check 對 r2-repair-review.patch 全數錨定。席位臨時目錄收齊後已刪。

## 重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| e1 | 正確性 #1 | 席位實測:拿掉子程序開頭還原遮罩那行,-k interrupt/signal_handling/spawn_error/green 全綠;小程式驗遮罩會跨 fork/exec 繼承 | HIT,折入:新測試 t_runner_fanout_spawn_mask 照 _fanout_spawn 給的參數真的開子程序印自己的遮罩;同一改壞(N16)翻紅 `[1, 2, 15]` |
| e2 | 正確性 #2 | 家筆記那行 WHY 綁 signal_handling,但前綴是紅燈測試驗的 | HIT,折入:拆成兩行 WHY,前綴那行綁 t_runner_default_fanout_red、遮罩那行綁 t_runner_fanout_spawn_mask |
| g1 | 架構對齊 #1 | 同檔通篇用 mock.patch.object,新測試直接改寫 globals() 再手動還原 | HIT,折入:兩支測試改用 mock.patch.object(含 subprocess.Popen 與環境變數 patch.dict);改寫後 N12、N13、N14 照樣翻紅 |

## 修補因果

- e1、e2、g1 的對象都是上一輪修補(c816c9f2a)新加的:修前 4efa74fb6 沒有遮罩、沒有那行 WHY、沒有 globals() 寫法(git show 4efa74fb6 查得到)。三條都記進 regression-set。

## 折入後驗證

- 背景環境 `env -u LUMOS_FANOUT_CHILD -u LUMOS_TEST_SHARDS bash -c '… --serial -k t_runner_ … & wait $!'` 204 過 0 紅,沒殘留 --shard 程序。
- 變異 N16(子程序不還原遮罩)、N12、N13、N14 都翻紅。
