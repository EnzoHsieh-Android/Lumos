# 代碼審第 1 輪收貨紀錄:殺傷力驗證編譯快取誤判(high)

8 席(正確性、資安 opus;併發、邊界、合約圖譜、通才、spec-conformance、架構對齊 sonnet)全收齊後才動程式。四道機械檢查:8 份正規化;quote-check:6 份全錨,通才席 4 句有 1 句、邊界席(clean)2 句有 1 句錨不到——通才席那條的發現由編排者機械重現(見下 t1),邊界席 clean、該句不支撐任何 finding;refcheck 全數對得上;兩欄一致;repo 根 reflog 無異動。外家 finder/否決照 2026-09-30 使用者裁定預設不派。

本輪有 major(通才 F1)→ 全折。

finding 編號:c=正確性-opus、k=併發-sonnet、g=合約圖譜-sonnet、t=通才-sonnet;資安、邊界、spec-conformance、架構對齊 0 條。

| 編號 | 席 F | 等級 | 重現 | 處置 |
|---|---|---|---|---|
| t1 | 通才 F1 | major | HIT(引句錨不到,編排者機械重現:補 sleep(1.1) 後,突變「壞法跑完不記結束秒」讓 ③ 翻紅;補之前同一突變照綠) | 折:S2 測試腳本加 time.sleep(1.1) |
| t2 | 通才 F2 | minor | HIT(突變:重試時設未來時間 → 新測試翻紅) | 折:新增 t_kill_after_write_retry_no_future 驗重試分支不設未來時間;3 秒上限只在時鐘往回撥有差,記在計劃 |
| t3 | 通才 F3 | minor | HIT(席位推測 CI 若設 PYTHONPYCACHEPREFIX 會恆綠,未實測) | 折:計劃實務隱患已寫明靠時序的那幾格,② ③ 是穩定守衛;記錄這個推測 |
| c1 | 正確性 F1 | minor | HIT(席位用替身重現;突變「還原沒錯開不帶到下一條」→ 新格 ④ 翻紅) | 折:mstate["carry"],還原沒錯開時下一條也記弱證據;S4 測試補 ④ |
| g1 | 合約圖譜 F1 | minor | HIT | 折:Systems/guard-kill 開頭 weak 定義補第四項、rc 那條註明 weak 欄不影響 rc |
| k1 | 併發 F1 | minor | HIT | 折:計劃實務隱患寫明不設開關的取捨與 REVISIT 2026-10-15 |

重現不到而沒折的:無(refuted-set none)。放行的:無。
