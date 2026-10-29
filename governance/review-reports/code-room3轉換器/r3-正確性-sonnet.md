severity: minor

整體判斷:未發現 blocker 或 major。有一條原有行為的回歸(轉換函式與其他程式碼寫在同一行時認不出),僅影響只提醒、不擋推送的那半,所以是 minor。

**finding 1:轉換註記不在行首的轉換函式不再被點名**
severity: minor
blocking: 否

- 引句:「cs = [(n, a, b) for n, a, b, _tx in _rg_methods(t, java, _RG_CONVERTER_ANNS)]」
- 失敗場景:輸入 `class Conv { @TypeConverter fun a(d: Long): Date = Date(d) }`,或 `companion object { @JvmStatic @ColumnTypeConverter fun a(...) = ... }`,或 Java 的 `public class C { @TypeConverter public static Long f(Date d) { ... } }`。
- 走到哪一行:`_rg_methods` 迴圈第一句 `if not lines[i].lstrip().startswith("@"): i += 1; continue`。這一行以 `class`、`companion object` 開頭,不是 `@`,整行被跳過,轉換函式沒被認出。
- 修前的 `finditer` 是整份文字掃描,不看行首,認得出。這是切法換掉後多出的限制。
- 結果:只改這種寫法的轉換器檔時,`_rg_spans` 回的轉換函式清單是空的,「型別轉換 a 沒有測試提到它」的提醒不會出現。觸發判斷 `_RG_TRIGGER_RE` 仍然會中,所以整道會跑,但不點名。
- 計劃〈誠實界線〉和 [S43] 都沒寫這條限制。
- 影響範圍:DAO 方法本來就用這個行首規則,所以這是新增的限制,只落在轉換函式上,而轉換函式只提醒、不擋。
- 最小重現:用下面「兩版查證命令」那段腳本,以 `_rg_strip(src)` 對兩版各呼叫一次 `_rg_spans`。
- 歸因:有證據的修復回歸。基線 74204dc 的轉換器搜尋用 `finditer`(`scripts/lumos` 約 47364 行),修前 70bddde4 也是 `finditer`;只有修後 3ae01c0c 的 `_rg_methods` 要求行首是 `@`。
- 兩版查證命令與結果:
  - 命令:用 `importlib.machinery.SourceFileLoader` 載入 `/tmp/lumos-seat-work/code-room3轉換器/正確性-sonnet/lumos_before.py` 與 `lumos_after.py`,對同一份輸入呼叫 `_rg_spans(_rg_strip(src), java)`,取第三個元素。
  - 修前:`kt_oneline_class` 得 `[('a',1,1)]`,`kt_oneline_companion` 得 `[('a',2,2)]`,`java_conv_inline` 得 `[('f',1,1)]`。
  - 修後:三者都是 `[]`。
- 測試缺口:`t_room_column_typeconverter_warns` 與 `t_room_java_typeuse_and_annotation_run` 的轉換註記都獨佔一行,抓不到這個。
- file: `scripts/lumos:47323`(`_rg_methods` 的行首判斷)

**已驗的正向主張(同一案例,修前 vs 修後)**

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| 修復:Java `@Nullable` 在修飾字之後,DAO 方法認得宣告名 | `@Query("a")\n public @Nullable Integer p();` | spans 含 `p` | G1 repair [S43] | `_rg_spans` 的 DAO 方法清單 `[]`(漏認) | `[('p',3,4)]` | 有證據的修復效果 |
| 修復:同一行寫多個註記 `@Query("a") @SuppressWarnings("x") public @Nullable Integer q();` | 同上 | 認得 `q` | G1 repair | 沒認出 | `('q',5,5)` | 有證據的修復效果 |
| 修復:`@Deprecated` 疊在 `@ColumnTypeConverter` 上,範圍從整串註記第一行起算 | 疊兩層註記的 Java 轉換函式 | 只改上面註記也點名 `unbox`,不點名 `box` | G1 repair | 未跑修前版的整合測試,未判定 | `t_room_java_typeuse_and_annotation_run` 4 項檢查全綠 | 修後行為成立;修前紅未獨立驗 |
| 保留:Kotlin `@Throws(...)` 接 `suspend fun`、`@JvmSuppressWildcards`、`@field:` 目標、`@Query` 字串含 `@` | 見腳本 `kt_throws`、`kt_fieldtarget` | 方法清單修前修後相同 | G1 preserve | `f(3,4)`、`g(5,5)`、`g(3,4)` | 相同 | 無回歸 |
| 保留:Java 夾帶括號註記的轉換函式 | `@ColumnTypeConverter\n @Nullable\n public static Long f(@Nullable Date d) {…}` | `f` 範圍 2~6 | G1 preserve | `('f',2,6)` | `('f',2,6)` | 無回歸 |
| 保留:Kotlin 屬性接在轉換註記後 | `@TypeConverter\n val x: Int = foo(1)` | 不該把 `foo` 當函式 | 補充案例 | 誤認 `foo` | 不再誤認 | 附帶改善 |
| 轉換器提醒、Room 3 匯出提示、轉換函式測試 | `-k` 三個測試名 | 全綠 | 測試 | — | 4、9、4 項通過,0 失敗 | 修後成立;修前紅未判定 |

我把 `-k t_room_` 這組 148 支的修後全綠當作作者證據,沒有自己重跑。

**三問**
1. 原問題(Java `@Nullable` 漏認、起點不一致)的修復效果:有上表的修前修後行為證據。
2. 修補處的正常、錯誤與相鄰路徑是否成立:DAO 的 Kotlin 與 Java 形態、轉換函式的多註記疊放都成立。唯一例外是 finding 1 的行首限制。
3. 新發現的同一案例修前修後:修前認得、修後認不出(finding 1,歸為修復回歸)。

**其他鏡頭**
- `_RG_TRIGGER_RE` 與 `kinds` 預設值:兩個呼叫端(DAO 傳預設、轉換函式傳 `_RG_CONVERTER_ANNS`)都對得上。類別上的 `@ColumnTypeConverters` 因為註記短名是精確比對,不會被當成轉換函式。
- 新取名規則 `(?:[^(@{};]|@[\w.]+(?=\s))*?`:兩個分支不重疊,沒有災難性回溯。`@field:Foo` 因為後面不是空白而不匹配,行為與修前相同(認不出)。
- 圖譜:已讀計劃條款 [S43][S44][S45] 與〈誠實界線〉。程式、測試與條款文字一致,唯一缺的是 finding 1 那條限制。`Systems/room-guard.md` 我沒有逐段比對。其餘 36 篇固定席筆記只因為 `scripts/lumos`、`scripts/test_lumos.py` 是全庫共用大檔而連上,與這份 diff 無關。
- 未驗範圍:沒有在真實專案上跑過;沒有獨立重跑修前版的三個新測試,無法確認它們修前會紅;資源、時間、冪等這幾類題目不適用,這份 diff 是純文字切割。

臨時檔 `/tmp/lumos-seat-work/code-room3轉換器/正確性-sonnet/` 留作證據,未清理。
