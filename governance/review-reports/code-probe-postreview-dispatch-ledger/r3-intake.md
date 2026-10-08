# r3 收貨與重現紀錄（2026-10-04）

審材 `r3-snapshot.patch`，SHA-256 `2615b5fa90d2eec0e0f5742f72aed9efef844d7ecc5b88ed61f33085ed257c35`，1101 行。九個獨立席（正確性、併發、邊界、資料、外家 finder/veto、架構、資安、規格）已收齊。各席採用版 `report-normalize`、`quote-check`、`refcheck`、`seat-check` 均 rc0；`seat-check` 的未提及材料是觀測提醒，沒有引句越界。邊界、架構席首稿的第一條沒有另列 finding 級 severity，原稿保留，原席純格式重發 `-v2` 後才記帳。資安席原帳的席名 `資安3-codex` 不符合工具的「連字號分段須有完整 `資安`」規則；同一報告及快照以 `r3-資安-codex` 補記，沒有增加實派席。沒有在收齊九席前改程式。

以下只把可重現的行為列為 HIT；「更嚴重嗎」另按實際消費面判。重現都在暫存目錄或唯讀載入現碼，沒有啟動真模型。

| 組 | 原報告 | 重現與觀測 | 判讀 |
|---|---|---|---|
| G10 失敗嘗試額度消失 | 正確性、併發、資料、資安、架構、規格、外家 finder/veto | HIT：mock 子程序產生含兩次重試的 candidate 後以 rc2 退出，`run_job(...max_per_window=5)` 留 `.json/.candidate/.pending`，`runs_in_window(out)` 印 `0`；歸檔後重新取得完整額度。 | major，S18 未滿足；正式結果可否計分與實際用量不可共用唯一帳。 |
| G11 跨日期目錄清空窗口 | 併發、資料、外家 veto | HIT：前一日目錄 `with-q-old.json` 含一列與兩次重試，`runs_in_window(old)` 印 `3`，新日期目錄印 `0`。 | major；舊缺口，不謊稱 r3 才引入，但新 S18/CLI 五小時承諾仍未滿足。 |
| G12 超額列灌高 M1–M4 | 資安、資料 | HIT：兩題各預定一次，`a` 100 筆通過、`b` 一筆失敗，`_arm_stats` 印 `n=101, m1_passed=100, m1_rate=0.9901, missing=0`；按題應是 1/2。 | major，逐題 missing 修了遮缺場，但統計仍讓超額列加權。 |
| G13 錯型 `calls` 計分 | 規格 | HIT：`calls:[42]` 的整批證據 `invalid_batch_evidence` 印 `[]`，`backfill_limit` 把 M2 算成 `False`。 | major，S15/S16 的逐列型別驗證未完成。 |
| G14 `with-notes.json` 假事故 | 邊界、資料、規格 | HIT：暫存目錄僅有 `with-notes.json`，`collect_skills_health` 回「結果檔缺少逐場資料」，live/純合併停批。 | minor；S17 未滿足，但屬保守誤擋，沒有污染分數。 |
| G15 原始 HTML 進報表 | 邊界、資安、外家 finder | HIT：`render_md` 的不一致題列直接輸出 `<img src=x onerror=alert(1)>`；健康警示檔名與歷史 meta 同樣可產生原始 HTML。 | minor；違反計劃的轉義承諾。辯方查現有消費面只有本機檔與終端，沒有證明現行瀏覽器執行鏈；若新增原始 HTML 渲染器，重評嚴重度。 |
| G16 恢復指示漏 `.pending` | 併發 | HIT：照 `retry_policy=archive-fatal-and-candidate-then-rerun` 只歸檔兩檔後，殘留 `.pending` 仍令 `collect_skills_health` 回 fatal。 | major，照事故紀錄操作不能恢復；須明列三檔並測完整恢復。 |
| G17 壞 meta 在純合併被覆寫 | 外家 finder | HIT：暫存 `meta.json` 截斷後跑真 CLI `--merge-only`，rc0 且原 byte 被 `來源日期未知/來源版本未知` 取代。 | minor，S14 只要求報表標未知，沒有授權抹掉可供救援的原始檔。 |
| G18 額度到頂先等 300 秒 | 併發、外家 finder | HIT：程式路徑 `scenario_probe.py` 在判 `limit_hit` 後先 `time.sleep(300)`，下一圈才檢查 `max_attempts`；外家席用受控 mock 驗過。 | minor，造成無效等待和誤導診斷。 |
| G19 題目預驗失敗仍占用嘗試 | 正確性 | HIT：`attempts_started += 1` 在 `run_at` 外圍，而 `run_one` 仍可因缺 `expect` 在模型前返回；來源反例見正確性報告。 | minor，保守誤擋，與「實際模型呼叫」文案不一致。 |
| G20 候選獨立警示、剩餘額度、橫幅位置測試弱 | 外家 finder/veto | MISS：兩席指出測試斷言不足；其中 finder 用記憶體 mutant 驗剩餘額度與橫幅位置仍綠，候選獨立警示未做實際 mutant。這是測試增強線索，沒有另算一個已證的程式故障。 | minor 線索，不拿來代替 G10–G19 的真反例。 |

辯方 `r3-defender.md` 只挑低共識 major：G11 維持 major（雖既有，仍違反正常跨午夜的 S18）；G14 與 G15 降為 minor，因一個是保守停批、一個未找到既有外部渲染鏈。這是判準調整，不否認 HIT 觀測。G10 有多家、跨鏡頭同意且編排者實跑，不需以「資安席說了算」代替機械證據。

原第1案四輪 FAIL、先前儀器第三輪 FAIL／例外第四輪、五案真模型收斂率均不因這份 r3 改寫。r3 對新修補有未折 major，沒有宣稱處置集合已閉合。
