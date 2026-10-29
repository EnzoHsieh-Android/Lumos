severity: minor

**第一問 分層與依賴方向:對齊,有一處結構重複(minor)**
- 新碼放在 `_rg_spans`,這是原本就負責回傳 DAO 方法範圍和轉換函式範圍的地方。依賴方向沒變:`_rg_dao_changes` 呼叫 `_rg_spans`,`_rg_spans` 呼叫 `_rg_annotations`、`_rg_balanced`、`_rg_method_end`。這些都是同一段 Room 守衛裡既有的底層函式,沒有跨層直呼,也沒有新增相依。
- 對照 `_rg_methods`:`scripts/lumos:47327` 先呼叫 `_rg_annotations`,`:47328` 取名,`:47333` 呼叫 `_rg_balanced`,`:47334` 呼叫 `_rg_method_end`。新碼是同一組呼叫,同一個順序。
- 這是同一套切法抄第二份,不是第二套做法,所以只列 minor。重複的部分是取名的 regex `[^(@{};]*?\b(\w+)\s*(?:<[^>]*>)?\s*\(`、`_rg_balanced(...)+1`,以及 `max(_rg_method_end(t, j), j - 1)`。這三個原本只在 `_rg_methods` 一處,現在 `_rg_spans` 又有一份,以後兩邊改動要同步。
- 第三問會把這一點算成一條 finding,這裡不重複計數。

引句:「dm = re.match(r"[^(@{};]*?\b(\w+)\s*(?:<[^>]*>)?\s*\(", t[k:], re.S)」

**第二問 命名與錯誤處理:對齊**
- 命名:`_anns` 前綴底線表示不用的回傳值,和 `_rg_spans` 同一函式已有的 `for n, a, b, _tx in _rg_methods(...)` 同款。變數 `dm`、`j`、`k`、`m` 與 `_rg_methods` 一致。
- 錯誤處理:鄰居沒有 try/except,也沒有日誌,對不上就用 `if dm:` 或 `continue` 略過。新碼用 `if dm:` 略過,同款。
- 註解:括號內標「代碼審 code-room3轉換器 r1」是鄰居的慣例,見 `scripts/lumos:47354` 一帶的「代碼審 r1、r2 正確性席」。
- 測試新增段落沿用既有的輔助函式,見 `scripts/test_lumos.py:116600` 的 `_rg(root, ..., rng=...)`,以及 `_nh_file`、`_nh_git`、`_nh_commit`、`check(...)`。`checkout -q -b` 這種開分支寫法在測試檔裡很普遍,例如 `scripts/test_lumos.py:26143`。

引句:「check("沒改到的 fromDate 不點名", "型別轉換 fromDate " not in out, out[-600:])」

**第三問 第二種做法:一處不一致(minor,不到 major)**

finding 1:轉換函式範圍的起點,和同一個函式裡 DAO 方法的起點算法不同。

severity: minor
blocking: 否

- DAO 方法的起點是這串註記第一行,見 `_rg_methods` 的 `out.append((dm.group(1), i + 1, last, ...))`(`scripts/lumos:47335`)。
- 轉換函式的起點是 `t.count("\n", 0, m.start()) + 1`,也就是 `@ColumnTypeConverter` 那一行。
- 同一個註記串裡,`@ColumnTypeConverter` 前面若還疊著別的註記,轉換函式的範圍就不含那幾行。DAO 方法的範圍含。
- 修補說明與 [S43] 條款都寫「沿用 DAO 方法的切法」,起點這一項沒沿用。
- 起點以 `m.start()` 算是修前就有的寫法:修前 `scripts/lumos:47364` 也是 `m.start()`。
- 這條只判「做法一不一致」。這個差異會不會讓只改上方註記行的情況漏報,我沒有跑,行為上未判定。
- 歸因:有證據的原有漏查。

引句:「cs.append((dm.group(1), t.count("\n", 0, m.start()) + 1, t.count("\n", 0, max(_rg_method_end(t, j), j - 1)) + 1))」

對修補三問的補充,只就一不一致回答:
- 原問題的修復效果:新測試 `t_room_column_typeconverter_warns` 加了夾 `@SuppressWarnings("unused")` 的 Java 轉換函式 `toDate`,以及只改多行本體一行的情境。我沒有執行,行為證據是未判定。
- 修補處的相鄰呼叫路徑:`_rg_dao_changes` 把 `ocs` 併入 `hit_old`,但 `gone` 只對 `oms` 計算,轉換函式被刪不會進 `gone`。這是修前就有的作法,修補沒動,與鄰居一致。
- 修前修後對照:同一份「夾註記的 Java 轉換函式」,修前會把註記名當函式名。這一點可由修前的 regex(`scripts/lumos:47364`,`[^;{]*?\b(\w+)\s*\(`)讀出來。修後取到函式名是從程式讀出來的,我沒有實跑。

不對齊共 1 條,其中 major 0 條
