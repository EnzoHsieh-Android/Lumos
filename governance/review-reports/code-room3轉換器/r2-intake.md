# code-room3轉換器 r2 收貨

席報告:r2-正確性-sonnet.md(severity minor,2 條)、r2-架構對齊-sonnet.md(severity minor,1 條)。兩席初交各有一處嚴重度寫法機器轉不了(正確性席一行「嚴重度:…」散文、架構對齊席 severity 寫在編號列表項裡並多一行空引句),退回該席自己重交,內容沒改;卷證存重交版,從子代理逐字稿取。
收貨四道:兩份 quote-check 全錨定、refcheck 全對得上、report-normalize 已正規化;seat-check 兩席都只標 unreported r2-snapshot.patch(只觀測;兩席實際引句都從它錨定)。repo 收貨時 `git status` 只有工具自動寫的治理帳、殺傷力帳與本輪卷證,程式沒被動過;正確性席的暫存 `/tmp/lumos-seat-work/code-room3轉換器/正確性-sonnet/` 收齊後已刪。

## 重現表

| id | 席 | 嚴重度 | 重現 | 結果 | 歸因 | 去向 |
|---|---|---|---|---|---|---|
| C1 | 正確性-sonnet #1 | minor | 修前 c95300ff、修後 70bddde4 各載入 scripts/lumos 呼叫 `_rg_spans`:Java `@ColumnTypeConverter` 下一行 `public static @Nullable Long f(@Nullable Date d) {`;另以同形 DAO 方法 `public @Nullable Integer f();` 對照 | HIT:修前 `[('f', 1, 2)]`、修後 `[]`;DAO 方法修前修後都 `[]` | 有證據的修復回歸(r1 改用 DAO 的取名規則,規則不收 `@`) | 折:轉換函式直接呼叫 `_rg_methods`(加 kinds 參數,傳 `_RG_CONVERTER_ANNS`),取名規則放行修飾字之間不帶括號的註記;DAO 方法同一寫法一起補上 |
| C2 | 正確性-sonnet #2 | minor | 修前修後各跑 `@ColumnTypeConverter\nfun toX(v: Long?): Instant? = v?.let {\n    Instant.ofEpochMilli(it)\n}` | HIT:修前修後都 `[('toX', 1, 2)]` | 有證據的原有漏查(`_rg_method_end` 遇 `=` 回該行,DAO 方法同樣) | 折:計劃〈誠實界線〉改寫成涵蓋 `= v?.let {`、`= when (x) {` 區塊,程式不改 |
| A1 | 架構對齊-sonnet #1 | minor | 修後 `_rg_spans` 起行取 `m.start()`(轉換註記那行),`_rg_methods` 取整串註記第一行;以 `@Deprecated` 疊在 `@ColumnTypeConverter` 上、只改 `@Deprecated` 那行驗 | HIT:修後不點名(新測試 t_room_java_typeuse_and_annotation_run 的「只改上面那個註記」修前紅) | 有證據的原有漏查(修前也取 `m.start()`);r1 宣稱「沿用 DAO 切法」不實 | 折:同 C1,改成同一支函式後起點一致 |

## 出處清單(修前列)

- 取宣告名的比對:scripts/lumos 只剩 `_rg_methods` 一處(`_rg_spans` 改成呼叫它);`_rg_declares` 是按名字找宣告、不取名,不受影響。
- 同一說法:計劃 [S43] 條款、〈誠實界線〉切法那一行、〈實作偏離紀錄〉Room 3 那一行;`_rg_methods` docstring。
- 反向案例:類別上的 `@ColumnTypeConverters(…)`、夾帶括號註記 `@SuppressWarnings("x")` 不當成函式名(既有斷言);沒改到的鄰居不點名(兩支測試各一)。

## 修補驗證

- 新測試 t_room_java_typeuse_and_annotation_run 修前紅 3 條(DAO 型別註記、轉換函式型別註記、只改上方註記),修後綠;`-k t_room_` 148 支全綠。
- 改壞:取名規則拿掉放行註記那段 → 新測試 2 條紅;轉換函式改用 DAO 註記種類 → 三支相關測試共 10 條紅;轉換註記只認舊名 → 9 條紅;還原後全綠。
- 抽查 Kotlin:短名、擴充函式、泛型、同行疊註記、帶參數完整名、類別註記,名稱與範圍都對。
