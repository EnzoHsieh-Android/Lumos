# r2 收貨紀錄(code-紅燈版實跑三缺口)

## 收貨

- 兩席全新(單reviewer-sonnet、架構對齊-sonnet)審 r2-repair-review.patch(修前 bcd9a1703 → 修後 06e101684 的修補差異,程式、測試、筆記那一包,723 行;來源 r2-repair-binding.json;待驗案例 r2-behavior-cases.md)。報告從逐字稿原樣存檔,兩份都已是正規化格式。
- 引句:架構對齊席全數錨定(當載體);單審席 5 句有 1 句錨不到——它自己註明那句是計劃回退節原文、不在修補差異裡,依規不採信,改由編排者讀碼撈回(見下表 C4)。
- 兩席交回期間 repo 沒被席位改動:`git status` 只有兩份新報告;`git reflog` 頂端是編排者自己的提交 201f4b0b3。單審席自己刪了暫存目錄;它提到系統暫存目錄有 605 個 gctl-* 測試暫存分不出是誰的、沒動,本輪也不動(只刪自己建的)。

編號:單審席 F1–F3 記 C1–C3,報告末「筆記不一致」那段(沒有獨立 severity 行)記 C4;架構對齊席第 1–3 條記 A1–A3。共 7 條;major 2 條(C1、A1),其餘 minor。全數折入,沒有放行,沒有重現不到的。

## 編排者重現

| id | 案例 | 結果 | HIT/MISS |
|---|---|---|---|
| C1 | 把 `_ENV_MISSING_EVIDENCE` 的 java-junit 那一項拿掉,跑 -k t_spec_gate_device_missing | 補 Java 專案的行為案例前 6 passed(席位實跑);補了之後改壞 P1 翻紅(r2-fix-mutation.md) | HIT |
| C2 | 沒斷言、有多行字串的測試,整檔重新縮排 | 補進 t_tq_guard_string_comma_args 的斷言,修前列 tq/no-assertion | HIT |
| C3 | 單平台,條款綁本身含冒號的 `gone:fee_jvm`,那支測試刪掉,另有 fee_jvm 綠 | 補進 t_spec_gate_record_keeps_platform,修前 rc0、跑了 fee_jvm(被頂替) | HIT |
| C4 | 計劃回退節寫「拿掉兩個測試格式的 env_missing_re」 | grep 計劃第 95 行成立,欄位已改名 | HIT(讀碼撈回錨不到的引句) |
| A1–A3 | 讀碼:`t.split(":", 1)[1]` 自切冒號;`.get("isig", …)` 回退;`_ENV_MISSING_EVIDENCE` 值是光字串、行內 re.search | 成立 | HIT |

## 歸因(照 §3.1 第 6 步;修前 bcd9a1703、修後 06e101684)

| id | 歸因 | 依據 |
|---|---|---|
| C1 | 有證據的原有漏查 | 修前版拿掉 java 欄位同樣 6 passed(席位兩版實跑) |
| C2 | 有證據的原有漏查(這條分支 r1 之前的提交引入) | 修前修後同為 tq/no-assertion,主線版回空(席位兩版實跑) |
| C3 | 有證據的修復回歸 | 修前紅並記逃逸、修後綠放行(席位兩版實跑) |
| C4 | 有證據的修復回歸(文件) | r1 修補改了做法節的欄位名、沒同步回退節 |
| A1 | 有證據的修復回歸 | 自切冒號是 r1 修補(R2)新寫的 |
| A2 | 有證據的修復回歸 | `.get("isig", …)` 是 r1 修補(R1)新寫的 |
| A3 | 有證據的修復回歸 | `_ENV_MISSING_EVIDENCE` 是 r1 修補(A5)新寫的 |

regression_set:C3、C4、A1、A2、A3。

## 根因分組與處置

| 組 | 根因 | id | 處置 | 先紅的測試 |
|---|---|---|---|---|
| 1 | 改回單平台時另起一套切冒號,還拿所有測試名比對 | A1、C3 | 拿掉自切冒號;改成只拿現在條款的名字比(整串先比,單平台再找恰好一個條款名字接在冒號後面),跟補舊留痕平台共用同一張條款名字表(`_spec_gate_push_match`、`_spec_gate_push_fill` 單平台也建) | t_spec_gate_record_keeps_platform 的 C3 案(修前紅);改壞 N2、P3 翻紅 |
| 2 | 新守衛只用一種格式驗 | C1 | 補 java-junit 專案的行為案例 | 改壞 P1 翻紅(修前在只有 Kotlin 案例時照綠) |
| 3 | 「只差空白版面」也被當成本體改了、所有規則重判 | C2、A2 | sig 相同、isig 不同時只比預期值(抽出 `_tg_expected_cands`),其他規則照沒改;兩份簽名直接取值、不回退 | t_tq_guard_string_comma_args 重新縮排案(修前紅);改壞 M3、P2 翻紅 |
| 4 | 同類表的值形狀與讀法跟鄰居不同 | A3 | `_ENV_MISSING_EVIDENCE` 的值改成具名欄位字典(re、why、measured),加存取函式 `_env_missing_why`(去色碼後比,同 `_ran_evidence_check`) | 改壞 N6 翻紅 |
| 5 | 改了做法節沒同步回退節 | C4 | 回退節改成拿掉 `_ENV_MISSING_EVIDENCE` | 無(文件);出處清單:grep 計劃與四篇筆記的 env_missing_re、_tg_ledger_ignored、TEST_PROFILES 的說法,只剩卷證裡的歷史 patch |

## 先查世界(r2 修補前,2026-11-03)

- 五組都是本專案內部的切法單一來源、測試覆蓋、比對範圍、設定表慣例與文件同步,沒有外部做法要比;組 3 沿用 r1 已查的 clone 偵測分法(只差空白版面算同一支)。

## 改壞驗證

見 r2-fix-mutation.md。
