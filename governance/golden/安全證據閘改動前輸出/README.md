# 安全證據閘改動前輸出(golden)

`golden.json` 是安全證據閘上線之前的主線版(提交 `d42840cf643eb5c027e7eeb86660a2fdc2396966`)對固定輸入產出的輸出,給三支「跟改動前逐字相同」的測試比:

- `t_secev_s01_no_registration_unchanged`:沒有資安登記的合成 repo 跑 `code-loop check`(文字、`--json`、治理帳多寫幾行)。
- `t_secq_s08_s11_existing_unchanged`:固定一份計劃全文(`s8.plan_text`,取自那一版的 `Projects/消費專案產品安全Brief與證據驗收_計劃`)跑 `pitfalls` 與四個階段的 `--stage --json`。
- `t_secev_s59_junit_rejections_unchanged`:`test_quality.junit()` 對五份壞 JUnit 的拒收訊息,與一份合格輸入的案例清單。

為什麼存成檔:原本跟「本機 `Lumos/main` 的分岔點」比,CI 沒有這個遠端名時退成 `HEAD~1`(新碼跟自己比),合併進主線後也變成跟自己比,三支守衛都會空轉(代碼審通才席)。

重產:把那一版的 `scripts/lumos`、`scripts/test_quality*.py` 抄到一個暫存目錄,在 `scripts/test_lumos.py` 裡對它呼叫 `_sg_golden_capture(<那份 lumos>)`(得到頂層的 `s1`、`s59`、`s59_ok`),再把 `_sg_golden_capture_s8(<那份 lumos>, <那一版的計劃全文>)` 的結果存成頂層 `s8`,並在 `s8` 底下另加 `plan_text`(那份計劃全文);頂層另加 `source_commit`(那一版的提交編號)。照 `json.dumps(..., ensure_ascii=False, indent=1, sort_keys=True)` 寫回。只有刻意改了這三種既有輸出時才重產,並在提交說明講為什麼。`t_secev_r2_golden_capture_reproduces` 對那一版跑這兩支、比對存好的 golden,擷取程式壞了或 golden 被手改都會紅(這份 clone 沒有那一版時略過)。

撤除條件(RETIRE-IF):三支測試改成直接斷言行為、不再比整段逐字輸出,或這三種輸出已被刻意改過而重產兩次以上——到時刪掉這個目錄與 `_sg_golden_capture*`。回頭條件記在 [[Systems/安全證據閘]] 的 REVISIT(2027-04-30)。
