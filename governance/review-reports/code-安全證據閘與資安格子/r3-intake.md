# code-安全證據閘與資安格子 r3 收貨紀錄

preflight-4: ran

## 席位與報告
八席全收齊後一次從逐字稿存檔:正確性、資源、邊界、架構對齊(四席都讀 r3-repair-lumos.patch 全份)、整合(r3-repair-docs.patch)、通才(r3-repair-tests.patch)、資安(涵蓋 r3-snapshot.patch 全量與 r3-repair-lumos.patch)、規格對照(opus,r3-repair-tests.patch 與兩份計劃)。外家未派(預設不派)。
- 架構對齊席初交第一條標 severity: major 卻寫 blocking: 否,兩欄矛盾;退回該席自己重判,該席改判 minor(理由:底層檢查走共用 `_repo_path_unsafe`,只是外層包裝重複,不算第二種做法),存檔的是重判後全文。另用 report-normalize --write 把末行「severity: minor(blocking 條數:0)」拆成兩行,純格式搬移。
- 整合席與規格對照席初交的引句沒用「」包住,quote-check 抽不到;退回兩席自己補格式,內容與等級不變。規格對照席第 3 條改引 r3-repair-tests.patch 裡測試 docstring 的原文。
- quote-check:八份對各席自己的材料全數錨定(資安席對 r3-snapshot.patch)。
- seat-check 八份都回「派工單沒列任何要查的材料」(vacuous 豁免),等於材料涵蓋這項沒有機械驗到;各席報告內都寫明讀過的材料。

## 編號
- 正確性:C1(護欄層加證據層同時擋時,擋下訊息仍建議簽例外) C2(收據 cwd 不是 repo 根時路徑換算錯,誤判過期與無關)
- 資源:R1(收據快照路徑的批次讀取沒吃整道讀取總額度)
- 邊界:B1(review 觀察時間 9999-12-31 加 90 天溢位,整道出錯) B2(_SecevDataError 沒有任何丟出點) B3(同 C2:子目錄收證必誤擋)
- 整合:I1(Verification 與程式註解的 2000 筆驗章耗時兩個數字)
- 通才:G1(符號連結拒寫測試沒蓋 docs/ 這層) G2(S13 測試預期值照抄實作篩選式) G3(符號連結預算測試上限 60 秒太鬆) G4(主線設定讀不到只測兩條分支,讀內容失敗等三條沒測) G5(golden 重產測試在淺 clone 靜默略過) G6(新測試偏慢、重複建 repo) G7(擋下訊息跳脫測試只注入換行與 ESC)
- 資安:X1(security list --questions 題句原樣帶入筆記描述,沒框成資料) X2(payload 印給人看時雙向覆寫與行段分隔字元不跳脫)
- 規格對照:P1(major,_secev_judge_tq 內層寬 except 仍把判定碼內部錯誤收成單項 report_malformed) P2(S64「檔不在樹上」那半沒測試) P3(S65 前提「有 behavior 證據時」沒測試) P4(d19 limitations 新句沒測試守,退回舊句照綠)
- 架構對齊:A1(寫入前擋符號連結的包裝與 _note_audit_safe_dir 同形重複) A2(資安族輸出出口新舊寫法混用) A3(符號連結擋下訊息三份文字) A4(截止時間檢查第三份、剩餘預算四行樣式複製多處)

## 編排者機械重現與核對(被審版本 47434676)
| id | 命令要點 | 結果 |
|---|---|---|
| P1 | 編排者自己重跑席位腳本:`python3.14 -I probe/p1.py <security-gate 工作樹>`(把 `_secev_tq().fault_check` 換成丟 KeyError) | HIT(輸出 `fault_check KeyError -> None ['invalid:report_malformed'] blocked True`;`git show 47434676:scripts/lumos` 的 `_secev_judge_tq` 在 fault_check 外仍有 except (KeyError, TypeError, AttributeError, ValueError, IndexError)) |
| B2 | `git show 47434676:scripts/lumos \| grep -n _SecevDataError` | HIT(只有第 8506 行定義與第 10290 行 except,沒有 raise) |
| C2 / B3 | 邊界席直接呼叫 `_secev_tq_rel`,cwd `/r/backend`、路徑 `/r/backend/src/a.py` 得 `src/a.py` | 採信(席位附四組輸入輸出;讀碼確認 `pre = cwd.rstrip("/") + "/"`) |
| B1 | 邊界席以 observed_at=9999-12-31T23:59:59Z 呼叫 `_secev_judge_review`,兩版皆 OverflowError | 採信(席位附兩版輸出) |
| R1 | 資源席 40 個 15MB 檔直接呼叫 `_SecevTree.read_many` | 採信(席位附 600MB、0.66 秒、無擋下) |
| P2 / P3 | 規格對照席改壞第 8918 行、第 8943 行後 -k t_secev_r2_fault 照綠 | 採信(席位附變異與結果) |

## 修補因果(regression-set)
有證據屬上一輪修補造成:C1(新寫的擋下訊息邏輯)、C2(新加的收據路徑換算)、B2(新加的例外類別沒接上丟出點)、I1(新段落沒同步舊段)、A1–A4(新加的包裝與出口)。
有證據屬原有漏查:P1(修前 7655a12d 同結果;與 r2 Y2 同族,內層沒一起掃)、B1(兩版同為 OverflowError)、X1、X2。
未判定(本輪新加的測試或規則,無修前版可比):R1、B3(與 C2 同一處,計入 C2)、G1–G7、P2–P4。

## 判讀
- 本輪有 major(P1),依處置閘規則 accepted 必空,所有發現折入;refuted 無。
- P1 與上一輪 Y2 同類第二次出現:修法改整類形狀——判定層一律不兜外來例外,只留讀進來那一層丟 _SecevDataError,並用一條測試掃全部判定函式,不再逐點補。
- 本輪是上限第 3 輪;依使用者裁定「折完就合併」,折入後記 cap-decision 與跑滿回顧,不再派第 4 輪。
