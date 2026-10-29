severity: minor

我逐 hunk 讀完 diff,並把修前(c95300ff)與修後(70bddde4)兩版的 `_rg_spans` 載入,用 28 個輸入各走一遍。只找到兩條 minor。
- 原問題「Java 夾註記時點成註記名、範圍太短」確實修好。
- Room 2 的 `@TypeConverter` 判斷沒有回歸。
- 三個相關測試修後全綠(`t_room_column_typeconverter_warns`、`t_room_typeconverter_warns`、`t_room_mig_never_exported_hint_room3` 所在的 `never_exported_hint` 組)。

1. 修補引入的回歸:Java 把型別註記寫在修飾字之後(`public static @Nullable Long f(...)`),轉換函式整支不點名。

severity: minor
blocking: 否

引句:「dm = re.match(r"[^(@{};]*?\b(\w+)\s*(?:<[^>]*>)?\s*\(", t[k:], re.S)」

- 輸入:`@ColumnTypeConverter\npublic static @Nullable Long f(@Nullable Date d) {\n  return null;\n}\n`,`java=True`。
- 路徑:`_rg_annotations` 吃掉 `@ColumnTypeConverter` 後,從 `public static @Nullable ...` 開始比對。字元類 `[^(@{};]` 不收 `@`,在 `@Nullable` 卡住,`dm` 為 None,這支不進 `cs`。
- 修前:第二個分支 `[^;{]*?\b(\w+)\s*\(` 允許 `@`,點名 f。
- 結果:觸發條件仍成立(檔案有改、`_RG_TRIGGER_RE` 命中),但不產生「型別轉換 f 沒有測試提到它」的提醒,整支靜默漏掉。`public @Nullable static Long f` 同樣漏。`@Nullable` 放在修飾字之前的寫法不受影響。
- 判準對照:`_rg_methods` 也有這個限制,所以這是照 DAO 切法搬過來的副作用。但對轉換函式來說,這是修前能認、修後不能認。
- 兩版查證命令:`python3.14 /tmp/lumos-seat-work/code-room3轉換器/正確性-sonnet/run2.py`。
  - 修前:`java_typeuse_nullable` 得 `[('f', 1, 2)]`。
  - 修後:`java_typeuse_nullable` 得 `[]`;`java_final_nullable_mid` 同樣是修前 `[('f',1,2)]`、修後 `[]`。
- 歸因:有證據的修復回歸。
- 標 minor 的理由:類型註記寫在修飾字之後在 Android 不常見,而且轉換器提醒只是 warn。

2. 文件誠實界線描述不足:Kotlin `= v?.let {` 與 `= when (...) {` 多行本體只算到 `=` 那一行。

severity: minor
blocking: 否

引句:「Kotlin 用 `=` 寫、換行接續的單一運算式本體,範圍只算到 `=` 那一行,只改接續那一行時不算改到」

- 輸入:
  ```
  @ColumnTypeConverter
  fun toX(v: Long?): Instant? = v?.let {
      Instant.ofEpochMilli(it)
  }
  ```
- 路徑:`_rg_method_end` 遇到 `=` 就回該行行尾。`_rg_spans` 回 `('toX', 1, 2)`,範圍沒涵蓋第 3、4 行。只改第 3 行時不點名。
- 修前修後結果相同,是原有行為,所以歸因是「有證據的原有漏查」。
- 問題在文字:[S43] 寫「只改多行本體裡的一行也算改到」,並沒有排除 Kotlin。誠實界線只說「換行接續」。但寫成 `= ... {` 同一行開頭的 lambda 或 when 區塊,第二行起也是漏的,而這在 Kotlin 轉換器很常見。這個寫法的測試只有 Java,沒有 Kotlin。
- 兩版查證:`run2.py` 的 `kt_let_block`、`kt_when`,修前修後都是 `[('toX', 1, 2)]`。

已驗主張(同一案例前後對照,`case_source` 為我自己補的案例,不是作者案例):

| claim | input | expected | before | after | 結論 |
|---|---|---|---|---|---|
| Java 夾註記取對名 | `java_annparam`(`@ColumnTypeConverter @SuppressWarnings("unused") public static Date toDate(...) {…}`) | 名為 toDate | `[('SuppressWarnings',1,2)]` | `[('toDate',1,6)]` | 已修復(F1) |
| Room 2 同樣修好 | `java_old_TC`(`@TypeConverter` 加 SuppressWarnings) | toDate | SuppressWarnings | `[('toDate',1,5)]` | 已修復 |
| 多行本體範圍 | `kt_basic`(g 有 5 行本體) | g 範圍到本體結束 | `('g',4,5)` | `('g',4,8)` | 已修復 |
| 帶參數註記 | `kt_args`(`@ColumnTypeConverter(x = 1)`) | 取 f | `('f',1,2)` | `('f',1,4)` | 正常路徑仍成立 |
| 泛型函式 | `kt_generic_fun`、`java_generic`、`java_generic2` | 取 f | f | f | 仍成立 |
| 擴充函式 | `kt_ext_fun` | 取 toLong | 修前誤取 `Instant` | `toLong` | 改善 |
| 檔尾孤註記 | `kt_eof` | 空 | `[]` | `[]` | 仍成立 |
| 註記在類別上 | `kt_class` | 不點名 | 誤取 `bar` | `[]` | 改善 |
| DAO 與轉換器混在一檔 | `kt_mixed_dao` | 取 c | `('c',7,8)` | `('c',7,8)` | 仍成立 |
| `_rg_methods` 沒改 | `-k t_room_`(作者自報 144 支綠) | — | — | 我只跑了 3 個相關子集,皆綠 | 未判定全套 |

未驗範圍:
- 註記在屬性上(`@ColumnTypeConverter val x = 3` 後接 `fun other(...)`)會把鄰居 `other` 當成轉換函式。修前修後行為相同,而且 Room 不允許這種寫法,所以不報。
- 括號不平衡時 `_rg_balanced` 回 `len(s)`,範圍一路算到檔尾。修前沒有這種行為,但剝掉字串與註解後不平衡的輸入罕見,我沒給出具體失敗輸入,所以不報。
- 註記前還有別的註記時,起行取 `@ColumnTypeConverter` 那行,不取最上面那條。只改前一個註記行時不算改到,修前修後相同。
- 全套 `t_room_` 沒有自己跑,也沒有端到端推送。

三問回答:
1. 原問題修復效果:Java 夾 `@SuppressWarnings` 取對函式名、範圍涵蓋多行本體,兩項都有前後案例證據。修前取到註記名、範圍只到函式名那一行。
2. 修補處的正常、錯誤與相鄰路徑:Kotlin 短名、泛型、擴充、帶參數註記、混合 DAO 檔、檔尾,以及 DAO 方法,正常路徑仍成立。例外是第 1 條,Java 型別註記在修飾字之後的寫法修前能認、修後不能認。
3. 新發現同一案例的前後結果:見第 1 條(修前點名 f、修後空)與第 2 條(修前修後皆只到 `=` 那行)。

圖譜鏡頭:
- `room-guard.md` 與 `Room資料庫測試守衛_計劃.md`:[S43][S44][S45] 的文字與程式、測試行為一致,唯一出入是第 2 條的文件精度。
- [S45] 改寫後與驗收筆記互相一致:轉換器情境用修正前的守衛推送、另用修正後的版本手動跑,驗收筆記也寫了「clone 裡那次用的是 r1 之前版本」。
- 其餘固定席(`scripts/lumos`、`scripts/test_lumos.py` 的共用大檔所連的 36 篇):不影響,因為只動 `_rg_spans` 與測試,沒碰這些節點的合約行。

暫存:`/tmp/lumos-seat-work/code-room3轉換器/正確性-sonnet/`(含 `run.py`、`run2.py`、`before_lumos.py`、`after_lumos.py`)留給編排者收貨後刪除。
