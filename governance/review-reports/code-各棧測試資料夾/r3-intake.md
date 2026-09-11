# code-各棧測試資料夾 r3 收貨紀錄(編排者)

## 收貨

- 六席 Claude 從輸出紀錄抽最終回覆,原樣存檔(跑的期間存在 repo 外,六席都交完才搬進來)。
- 外家 finder(Codex)本輪缺席:排在設計審第三輪那席之後跑,開跑三秒就被擋——Codex 帳號用量用完,要到 2026-09-16 16:27 才恢復(原樣存 r3-外家codex-額度用完.txt)。三輪都沒有外家席,收斂結論只能講「單家族(Claude)視角下未發現」。
- report-normalize 六份都已正規化;quote-check 六份全數錨定;refcheck 六份都對得上。
- 席報告合計:正確性 1 條(blocking 1)、邊界 2(1)、接手的人 1(1)、牽連 1(1)、架構對齊 0(判 clean,確認第二輪兩條收斂)、資安 2(0),共 7 條、blocking 4。

## 機械重現

| 發現 | 重現做法 | 結果 |
|---|---|---|
| E1 Gradle 那條沒限定那一棧的副檔名(正確性 F1、邊界 F1、接手的人 F1、資安 F2) | in-process:`app/src/main/scripts/gen.py`+`app/src/androidTest/scripts/evil.py` 回 True;`mod/src/main/build.sh`+`mod/src/androidTest/setup.sh` 回 True。接手的人舉的 `backend/src/test/handler.go` 那例改動前就回 True(資料夾名 test 走既有測試地圖規則),那一半不是這次引入的 | HIT(test 那半 MISS) |
| E2 Xcode 測試資料夾裡的 .h 仍被擋、計劃「輔助檔一起算」說過頭(牽連 F1) | `PosTerminalTests/BridgingHeader.h` 在 home check 仍列沒家;計劃名詞段那句無條件 | HIT |
| E3 同名資料夾的同種檔證據不限深度,刻意放一支就能免家(資安 F1) | `tools/anywhere/deep/util.cs`+`toolsTests/x.cs` 回 True | HIT |
| E4 漂移守衛重算資料夾名沒濾空字串(邊界 F2) | 程式那一支有 `if d`,測試那一支沒有 | HIT |

## 去重分組與處置(本輪有 major:accepted 必須為空)

| 組 | 等級 | 怎麼處置 |
|---|---|---|
| E1 | major | 折:Gradle 那條也連同那一棧的副檔名推(同頂層那條),只認 Kotlin;反例寫進測試先看它翻紅;另補「src/main 只有資源、沒有 Kotlin」的反例殺掉原本存活的突變 |
| E2 | major | 折(觀察成立、判準不採):放寬成「資料夾裡什麼檔都算」會重開 E1 那個洞(四席要收緊、一席要放寬,不能兩全),照事故筆記「寧可過嚴」取收緊——.h 與 Java 的 androidTest 輔助檔寫進「沒涵蓋」、逃生口 node_home.ignore、事件入口是健檢 S8;用一條測試釘住這個取捨;計劃名詞段改成「同一棧副檔名的輔助檔一起算」 |
| E3 | minor | 折(寫明天花板):事故筆記「沒涵蓋」過鬆那一面補「刻意放一支同副檔名的檔就能免家,跟改 node_home.ignore 同級但不顯眼;這道錨防命名意外、不防刻意」,沿用同段的 REVISIT:2026-10-12 |
| E4 | minor | 折:漂移守衛補 `if d` |

- 突變檢查十一種殺十種;活下來的一種是等價突變(「緊接在 src 下一層」被 src/main 的路徑前綴順帶保證:不緊鄰時前綴不以 src 結尾,永遠對不上)。
- ★這是高風險分級的最後一輪,這一輪的修正沒有下一輪獨立審查;機械兜底只有測試先行、突變檢查、平板 POS 實跑。★
