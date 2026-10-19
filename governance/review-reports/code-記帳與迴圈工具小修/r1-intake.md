# code-記帳與迴圈工具小修 r1 收貨與修正

七席(正確性、邊界、資源、整合、通才、架構對齊、資安)報告全收,資安 clean。共 19 條:正1–2、邊1–4、資1、整1–4、通1–5、架1–3;major 2(通1、通2),其餘 minor。全部折入,無駁回。base_commit d2da0e8c。

每個程式根因先寫會紅的測試再修(A、C、D、E 的新斷言在修前實跑為紅);F 與 C 的跑滿回顧那條是測試缺口,用故障變體驗證(拿掉 suggested 的型別檢查 → t_dispositions_suggested_evidence_type_error 0/3;讓跑滿回顧對沒人裁的迴圈也擋 → t_cap_retro_only_blocks_decided_loops 2 條紅;還原後全綠)。

| 根因組 | 條目 | 修法 | 守它的測試 |
|---|---|---|---|
| A 結局帳讓迴圈卡死 | 通1 | 編排者裁定:結局帳結構上不能帶輪次,讀側判混用一律不算結局帳列(新增 `_review_rows`);寫側照舊放行結局帳。loop next、loop status(含 --panel)、處置閘(含回放直接呼叫)、跑滿上限提示的範圍都先濾結局帳。S14、S15 期望照這個語意改 | t_canary_record_outcome_exempt_round_format、t_canary_record_round_ignores_outcome_rows |
| B 共用判法只接一半 | 架1、通4 | `loop status --panel` 與處置閘自己數 `"round" in r` 的兩處改呼叫 `_loop_round_format`,loop next 的 n_round 收掉(panel_fmt 改看判法回 all);判法本身含結局帳排除 | t_canary_record_outcome_exempt_round_format、t_loop_panel_gate、t_disposal_gate_r3_panel_hardening |
| C 帳壞擋太廣、跑滿回顧守衛沒人守 | 通2、正2(另含邊界席「其他邊界」第 1 點) | 整本不是 UTF-8 照擋,訊息改「審查帳讀不懂……任何編號都先不記」;這個編號自己有壞列只擋它、訊息講「這個審查編號的帳有一列讀不懂(別的編號不受影響)」(讀側 `_canary_ledger_scan` 本來就分得出兩種,不用寫成已知限制;整本壞擋所有編號寫進計劃已知限制)。補一支測試守跑滿回顧只擋有人裁紀錄的迴圈(健康、無人裁的迴圈 B 照常寫帳、不落 cap-ledger-bad);t_cap_retro_bad_ledger_fail_closed 註解寫明哪部分是有意改變 | t_canary_record_round_check_bad_ledger_blocks、t_cap_retro_only_blocks_decided_loops、t_cap_retro_bad_ledger_fail_closed |
| D none 與 regression-set | 通3、邊1 | `--regression-set` 的空值判斷改用 `_ids` 切(全空白含 Tab、只有逗號都擋),none 判法改用跟折入放行同一支 `_set_or_none`(`none,` 也是空清單) | t_canary_record_regression_set_code_only、t_canary_regression_set |
| E 訊息與出口 | 正1、邊4、邊3、架2、通5、架3(另含邊界席 ESC/換行編號) | 既有全無輪次又沒定分級時第一筆規則講換新編號(不再叫人補上輪次);docstring 規則③對齊程式(只在零筆或都沒定錨時用這筆 --tier);`--round` 純空白當沒帶;existing 清單內 null 講型別;`_disp_value_type_err` 改收格式說明與 none_ok 參數,拿掉事後 .replace;`cb3 s3-f1` 註解歸回 record_cmd;範例指令裡的編號過 `_esc_clean` | t_canary_record_unanchored_tier_from_this_row、t_canary_record_first_row_needs_round、t_dispositions_existing_item_type_error、t_dispositions_evidence_type_error |
| F 測試缺口 | 邊2 | 補 tension chosen=suggested 的 evidence 型別測試(清單、物件、數字) | t_dispositions_suggested_evidence_type_error |
| G 每筆記帳讀三次帳 | 資1 | cmd_canary 開頭讀一次(`_canary_ledger_scan` 一次,再 `_loop_records_checked(scan=…)`),--orchestrator、--regression-set、輪次規則、載體最後記共用;帳壞時前兩處照舊走原本的讀法(保持既有行為) | t_canary_record_blocks_round_format_mix、t_canary_regression_set |
| H 文件 | 整1、整2、整3、整4 | 跑滿回顧計劃 S17 與第 208 行、loop-convergence-recording d7 WHY 標註已改並指過來;循序 tier 錨定計劃開頭加指標;design-loop 問閘雙軌 KEY 加指標;canary record --help 的 --folded-set/--accepted-set 補 none 規則、--regression-set 補只收 code-;計劃白話段條數改八 | t_canary_record_regression_set_code_only(help 文字沒有自動測試;以 `lumos canary record --help` 人工核對) |

## 機械重現

| 編號 | 指令 | 輸出 | HIT/MISS |
|---|---|---|---|
| 正2 引句(轉述版) | `grep -c 'print(f"擋下:這個審查編號的帳讀不懂({lerr}),沒辦法確認輪次格式", file=sys.stderr)' r1-snapshot.patch` | 0 | MISS(席位自承是轉述) |
| 正2 引句(原文版) | `grep -c '擋下:這個審查編號的帳讀不懂({lerr}),沒辦法確認輪次格式' r1-snapshot.patch` | 1 | HIT |
| 正2 觀察 | 帳尾加 `\xff\xfe junk` 後記一個全新編號(t_canary_record_round_check_bad_ledger_blocks 的整本壞那段) | 修前:rc2、訊息「這個審查編號的帳讀不懂(審查帳不是 UTF-8…)」;修後:rc2、訊息「審查帳讀不懂…任何編號都先不記」 | HIT(觀察成立,照協調裁定只改訊息與範圍) |
| 邊1 | `grep -n 'if not str(regression_set).strip(" ,"):' r1-snapshot.patch` | 第 594 行命中 | HIT |
| 通1 | t_canary_record_outcome_exempt_round_format 修前跑 | 4 條紅(loop next、處置閘、--panel 判混用,r2 被擋) | HIT |

## 駁回

無。
