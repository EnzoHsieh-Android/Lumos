# r3 收貨與去向(2026-10-26)

範圍:只審推送前檢查與放行(〈資料怎麼流〉第 4、5 步、〈查證紀錄長怎樣〉、〈推送前怎麼按功能判〉、S8–S14、S17、S29–S33、〈實務隱患〉、〈回退〉);已上線的按功能跑當背景。6 席:正確性(C)、邊界(B)、整合(I)、資源併發(P)、回滾(K)、架構對齊(A)。四席(C、B、I、P)初交沒有逐字引句,退回只補引句、內容不變,補完全數錨定。

編號照各席報告裡帶 severity 的發現順序;架構對齊席兩個標 ⚠、沒有 severity 的觀察(環境變數判法、CI 與接線矛盾)不編號,照樣折入(見最後)。

## 編排者重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| I1 | `sed -n 615,622p scripts/hooks/pre-push`:rc=0 時只 grep `提醒|受波及合約測試|表態閘|安全證據` | HIT |
| I4 | `grep -n "\[a-z_\]+" scripts/test_lumos.py`:79956、79983 兩處樣式不收數字,79984 寫死 `len(got) == 5` | HIT |
| P3、I13 | `_confirm_tty` 內 `if sys.stdin.isatty(): return _norm(input(prompt))`,逾時只在 /dev/tty 那條路的 select | HIT |
| P2 | `_vault_write_lock` docstring「過期也不自動接手」、等 60 秒丟 WriteBlocked | HIT |
| P1 | `_lumos_config_at_ref`:`cat-file -e` 回傳碼非 0 判 missing,物件缺時也走這條 | HIT |
| C4、B4、I2 | `_e2e_case_results`:`complete = not skipped and bool(rs)`,`rs` 為空時 result unjudged | HIT |
| C2、B1、I3 | `_e2e_fingerprint` 的 memory-config 那行只在 e2e 段開了記憶體時接進去,`.lumos/macrobench.json` 不在檔案清單 | HIT(讀碼) |

## 去向

根因分組(修法用一條規則補整組,不逐點補):

1. 判定順序與 S8、S10、第 4 步說法打架、`runs` 是 null 的語意:C1、K4、I9 → 折。第 4 步「怎麼判」改成照〈推送前怎麼按功能判〉;S8、S10 改寫;`waivers` 定欄位與「算數的放行」。
2. 指紋變了、範圍內改到的檔卻是空集合:C2、B1、I3 → 折。`memory-config` 那行不同→要整套;範圍內沒有改到的檔→要整套;〈查證紀錄〉的指紋那句補 d1 例外。
3. 只列效能、略過效能、較新的沒判完紀錄:C3、C4、B4、I2 → 折。只列效能的情境不用驗;`skipped` 只看 `stability`;第 2 步只看 fail。
4. 讀不懂時偏放行(時間欄、同一秒、路徑跳脫):C5、C7、B5 → 折。`ended` 讀不懂→擋;同一秒算較新;`git diff` 帶 `-z`。
5. 兩端不對稱與前置判斷:B2、K6(分岔點端缺 app_dirs 項目)、B3(被推送提交沒有 e2e 段)、B8(沒用 E2E 的專案)、B9(算不出分岔點)、P1(在樹裡卻讀不出)→ 折。
6. 放行與鎖:P2、P3、I13、B6、B7 → 折。確認在鎖外、標準輸入終端也逾時、Ctrl-C 回 1 不寫帳、鎖可接手、指紋只收 64 碼、擋下訊息帶完整指紋與 `--commit`。
7. 通知:I1、I6、A6、P5、K7 → 折。提醒行以「提醒」開頭、接 `_cl_say_ok_extras`;不進 enforcement、開場另印一行;掃描範圍定為全部紀錄、補 `--ack --all`。
8. 治理帳與撤除條件:C8、K2、I5、K1、K3、A1、I8、K8 → 折。事件名 `skipped-env`、擋下記 `blocked`;`passed-by-feature` 附指紋、按指紋去重;按功能的 RETIRE-IF 改成數逃逸帳;刪掉「整套是推上主線前最後一次全面驗」;〈回退〉補降回只提醒、撤掉按功能、程式回退順序。
9. 共用、接線與文件:A2(共用函式)、I4(守衛測試樣式)、P4、A5(時間預算與 pathspec)、I7(ci.yml 白改、CI 印行順序)、I10、A4(shared_paths 存在檢查與文件)、I11(欄位名)、I12(HELP_WHEN)、C6(死分支拿掉)→ 折。

放行(minor,附理由):
- B10、P6:`CI` 設成任何非空值都算在 CI 裡。這是 `_in_ci` 這支各閘共用的判法,安全證據閘等其他閘一樣;本機設了 `CI` 是使用者自己的環境,照單人威脅模型不另防,也不在這一道另寫一套判法。
- P7:寫一半被殺留下的暫存檔走 `_write_bytes_atomic` 共用寫法、判定只讀正式檔;不同機器的時鐘差幾分鐘照單人威脅模型不防。同一秒的部分已折(算較新)。
- K5:指紋算法沒有版本欄,lumos 升降版後一律找不到紀錄、要重跑一次;方向是擋(不會錯放),代價是多跑一次,不另做版本欄。
- A3:waive 的形狀跟 lint-waive 有四處不同(終端確認分人與 AI、誰的取法、同指紋可多筆、一個指紋一個紀錄檔),都是 r1 後 Enzo 裁定、計劃有理由;鎖與寫入照沿用。

架構對齊席 ⚠ 兩條(沒有 severity、不編號):環境變數判法鄰居不一致 → 折,選只認 `1`(同 `LUMOS_SKIP_BOUND_TESTS`,也對上〈回退〉的寫法);CI 不跑卻要接 ci.yml 說明 → 折,ci.yml 不改。

refuted:none(每條都重現或讀碼對上)。
