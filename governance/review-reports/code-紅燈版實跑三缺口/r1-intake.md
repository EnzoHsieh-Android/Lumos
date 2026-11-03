# r1 收貨紀錄(code-紅燈版實跑三缺口)

## 收貨

- 兩席(單reviewer-sonnet、架構對齊-sonnet)都審 r1-code.patch(程式、測試、筆記那一包,1406 行;完整差異 r1-snapshot.patch 2383 行,多出的是設計審卷證與帳本,屬簿記)。報告從各席逐字稿原樣存檔。
- 單審席首交時第 3 行與小結寫了「沒有 blocker 或 major」,被格式檢查判成總結句藏更高等級,退回該席只改那兩處後重交、重存;重交版小結那行行內等級用 `report-normalize --write` 純格式搬成獨立一行(不改等級)。
- 引句:兩席全數錨定。refcheck 全對得上。
- 兩席交回期間 repo 沒被席位改動:`git status` 只有新報告與我自己跑工具寫的帳;`git reflog` 頂端是編排者自己的提交。單審席的暫存目錄(/tmp/lumos-seat-work/code-紅燈版實跑三缺口/單reviewer-sonnet)收齊後已刪。

編號:單審席 F1–F4 記 R1–R4;架構對齊席依報告出現順序 A1–A6(A1 doctor 跨層叫比對工具內部、A2 doctor 新段只接窄例外、A3 平台例外接寬的 ValueError 再猜 prefix、A4 規格閘那行帶 ⚠ 走標準輸出、A5 環境樣式放進 TEST_PROFILES、A6 切參數兩套切法且 angle 被靜默忽略)。共 10 條;major 2 條(A1、A5),其餘 minor。全數折入,沒有放行,沒有重現不到的。

## 編排者重現

| id | 案例 | 結果 | HIT/MISS |
|---|---|---|---|
| R1 | 測試搬進 inner class、本體有多行三引號字串 | 補進 t_tq_guard_string_comma_args 的斷言,修前(簽名只用保留字串那份)列 tq/test-removed | HIT |
| R2 | 多平台寫的 jvm:fee_jvm,設定改回單平台後推送 | 補進 t_spec_gate_record_keeps_platform 的情境,修前 rc1、逃逸帳多一筆 | HIT |
| R3 | 只有還沒提交那條時看不到孤兒那條的改法 | 讀碼成立;補斷言「自帶 check-ignore -q、不提孤兒那條」 | HIT |
| R4 | `"${a}, ${f("x")}"` 只改預期值 | 席位用真函式實跑回 False;修補前就漏、退回現況照樣漏 | HIT(文件) |
| A1/A5 | 讀碼:doctor 叫 `_tg_ledger_ignored`;`env_missing_re` 在 TEST_PROFILES | 成立 | HIT |

## 歸因(照 §3.1)

第一輪,沒有上一輪修補,不填 regression_set。R1、R2 是這批改動自己引入的(簽名改法、留痕新格式),在同一批內修。

## 根因分組與處置

| 組 | 根因 | id | 處置 | 先紅的測試 |
|---|---|---|---|---|
| 1 | 共用判法掛在比對工具那區 | A1 | 改名 `_gov_ledger_ignored`、搬到帳檔區(跟 `_local_ledger_doctor_msgs` 同區),三處呼叫 | 改名;既有 S7–S10 照綠 |
| 2 | 照輸出判狀態的樣式放錯表 | A5 | 移到 `_RAN_EVIDENCE` 旁的 `_ENV_MISSING_EVIDENCE`(同樣以測試格式為鍵) | t_spec_gate_device_missing_not_red(改壞 N6 翻紅) |
| 3 | 新段的錯誤處理與輸出跟鄰居不一致 | A2、A3、A4 | doctor 接 Exception 照 fail-open;接專屬 `_TestRefPrefixError` 用 `e.prefix`;規格閘那行拿掉 ⚠、走錯誤輸出 | S9 改看錯誤輸出(改壞 N7 翻紅) |
| 4 | 兩套切法沒綁在一起、angle 被靜默忽略 | A6 | 只有 angle=False 才走剝過文字那條;補 300 段隨機文字等價比對與 angle=True 不走新路的斷言 | t_tq_guard_string_split_fallback(改壞 N4、N5 翻紅) |
| 5 | 一份簽名同時給「找搬家」與「判本體變了」 | R1 | 拆兩份:sig(拿掉全部空白)找搬家、isig(_tg_ident)判變了 | t_tq_guard_string_comma_args 搬家那案(改壞 N1 翻紅) |
| 6 | 新格式留痕沒考慮設定改回單平台 | R2 | 單平台時整串找不到、去掉前綴找得到才用去掉前綴的名字 | t_spec_gate_record_keeps_platform 單平台那案(改壞 N2 翻紅) |
| 7 | 提醒引用了可能不在的另一條 | R3 | 還沒提交那句自帶改法與自查指令 | t_tq_guard_redbase_ledger_ignored(改壞 N3 翻紅) |
| 8 | 計劃宣稱失實 | R4 | 做法 1 照實寫「退回的兩種寫法跟現況相同,現況本來漏的照樣漏」並舉例 | 無(文件) |

## 先查世界(r1 修補前,2026-11-03)

- 組 5:clone 偵測的通例把「只差空白、版面、註解」(Type-1)跟內容改動分開判(Roy、Cordy、Koschke 的分類;Schwarz 等 ICSE 2012 以「只差空白」定義 Type-1,https://www.inf.unibz.it/~rrobbes/p/ICSE2012-clones.pdf),本案照這個分法拆兩份簽名。
- 其餘組都是本專案內部的模組位置、錯誤處理慣例、相容與文件,沒有外部做法要比。

## 改壞驗證

見同目錄 r1-fix-mutation.md(修補後把上一輪 20 點與這輪 7 點逐一改壞)。
