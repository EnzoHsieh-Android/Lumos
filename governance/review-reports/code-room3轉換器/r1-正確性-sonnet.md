severity: major

最高嚴重度 major。兩條正規式沒有 Room 2 回歸,觸發條件的改動有測試守住。但 Java 夾註記的情形實際會點錯名字,而驗收條款 [S43] 把它寫成已涵蓋。

**(a) 回歸**
- `@TypeConverter` 與 `@androidx.room.TypeConverter` 的行為沒變。
- 新正規式是 `(?:Column)?TypeConverter\b`。類別上的 `@TypeConverters(...)` 與 `@ColumnTypeConverters(...)` 都因 `\b` 失敗而不誤配,我實跑確認過。
- 我把 `_RG_TRIGGER_RE` 改回舊式後跑 `t_room_column_typeconverter_warns`,5 條斷言全紅。觸發改動有測試守住。我已還原檔案並刪掉測試暫存。
- Java 完整套件名的第二個分支原本沒有 `androidx.room.` 前綴,現在補上,是淨改善。

**(b) 其他 Room 3 註記**
- `@ProvidedColumnTypeConverter` 和 `@DaoReturnTypeConverter` 在 `@` 後面接的不是 `(?:Column)?TypeConverter`,不會被誤認成轉換函式。
- `@DaoReturnTypeConverter` 的函式不被點名,是合理的缺漏。
- 這一點是依註記名稱判斷,我沒有連網查 Room 3 官方文件。

**(c) 提醒文字**
- 新寫的 `room3 { schemaDirectory(...) }` 與 `room.schemaLocation`,依據是驗收筆記宣稱的實驗專案實測(room3-compiler 3.0.3)。我沒有獨立重驗。

**Finding**

1. Java 轉換函式與註記之間夾別的帶括號註記時,會點到註記名而不是函式名。位置在 `scripts/lumos:47359`(`_rg_spans`)第二個分支 `[^;{]*?\b(\w+)\s*\(`,條款在計劃 [S43]。
   - 輸入:`class C {\n @ColumnTypeConverter\n @SuppressWarnings("x")\n public static Long fromDate(Date d){}\n}`。
   - 結果:`_rg_spans` 回傳的轉換函式名是 `['SuppressWarnings']`,不是 `fromDate`。提醒點錯名字。
   - 後果:比對範圍變成註記那幾行。只改函式本體時,改動行落在範圍外,該轉換器不會被點名。
   - 測試缺口:`t_room_column_typeconverter_warns` 的 Java 檔(`JConverters.java`)沒有夾註記。夾註記的 `@Suppress` 只放在 Kotlin 的 `fromUuid`,走的是第一個分支。
   - Room 2 的 `@TypeConverter` 也有同樣的毛病,不是這次新增的回歸。但這份 diff 把 Java 夾註記寫成已涵蓋,事實不符。
   - 最小重現:對 diff 第 267–268 行的正規式跑 `re.finditer`,輸出 `['SuppressWarnings']`。
   - 處置:補 Java 夾註記的測試並修分支,或把 [S43] 的 Java 夾註記宣稱收窄。

severity: major
blocking: 是
引句:「Kotlin 或 Java,註記與 `fun` 之間夾著別的帶括號註記也算」
file: `scripts/lumos:47359`

2. 驗收條款 [S45] 是 manual 條款,要求從實驗專案的 Room 3 分支實際 git push。驗收筆記卻在同一份 diff 裡承認,修正後的轉換器判斷沒有從實驗專案推過,只在另一份 clone 與工具鏈測試裡驗過。「另一份 clone」的證據無法從這份 diff 重驗。這是措辭與證據精度的落差,不會讓測試或推送被擋。

severity: minor
blocking: 否
引句:「修正後的轉換器判斷只在工具鏈測試與上面那份 clone 裡驗過」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-29_Room守衛Room3實跑.md`

**其他判定**
- manifest 是 0 條 claims,沒有項目需要判定。
- 圖譜固定席(bound-tests-gate、guard-kill、測試假綠形態等):本 diff 只動 `_RG_*` 與 `_rg_spans` 及新測試。
  - 沒有碰這些節點的合約函式,判不影響。
  - 新測試有還原翻紅的證據(上面的實測),並有前置斷言(`rc == 0` 且點名函式),符合「測試假綠形態」的要求。
- `room-guard.md` 與計劃〈做法〉、〈誠實界線〉:型別轉換仍只提醒,rc 沒變,未破壞。
