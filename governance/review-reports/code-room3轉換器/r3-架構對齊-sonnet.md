severity: clean

這份 diff 在三問上都跟既有做法一致。我只判一致與否,沒有判到行為對錯的項目。

**1. 分層與依賴方向:對齊**

新碼全放在 `scripts/lumos` 的 Room 守衛段,都是 `_rg_` 函式和 `_RG_` 常數。沒有跨層直呼,也沒有新增層。

- 型別轉換函式原本由 `_rg_spans` 自己用兩條 regex 抓。現在改成呼叫 `_rg_methods(t, java, _RG_CONVERTER_ANNS)`,跟 DAO 方法走同一個下層函式。`_rg_spans` 的回傳形狀沒變,仍是 `(dao, ms, cs)`,下游不用動。
- 呼叫關係跟鄰居相同:`_rg_spans` 呼叫 `_rg_methods`,`_rg_methods` 呼叫 `_rg_annotations` 與 `_rg_balanced`。
- `_rg_methods` 用「參數帶預設常數」切換種類,專案裡早有這種寫法。對照:`def _secinv_blocks(rel, text, mark=_SECINV_MARK)`,見 `scripts/lumos:7187`。同類的還有 `scripts/lumos:4386` 的 `_gov_tail_bytes` 和 `scripts/lumos:43624` 的 `_nodehome_golive`。
- 觸發用的 `_RG_TRIGGER_RE` 加了 `(?:Column)?TypeConverter`。它本來就跟 `_RG_METHOD_ANNS` 各自列一份註記名,這次延續同一做法。

引句:「+    型別轉換函式傳 _RG_CONVERTER_ANNS,同一套切法,代碼審 code-room3轉換器 r2)。宣告名前面的修飾字之間可夾不帶括號的註記」

file: `scripts/lumos:47365-47366`(`ms` 與 `cs` 現在都經 `_rg_methods`)

**2. 命名與錯誤處理:對齊**

- 新常數 `_RG_CONVERTER_ANNS` 對照既有 `_RG_METHOD_ANNS`(`scripts/lumos:46906`),命名、frozenset 型別、行尾註解風格都一致。
- 新測試 `t_room_column_typeconverter_warns`、`t_room_java_typeuse_and_annotation_run`、`t_room_mig_never_exported_hint_room3` 都用 `t_room_` 前綴,docstring 開頭帶 `[S43]` 或 `[S44]` 條款標記,跟 `t_room_typeconverter_warns` 的 `[S29]` 一樣。
- 測試用既有的 `_rg_repo`、`_rg`、`_nh_file`、`_nh_commit`、`_nh_git`,以及 `check(...)`。`_rg` 的 `rng=` 參數本來就有,見 `scripts/test_lumos.py:116600`。開分支 `_nh_git(root, "checkout", "-q", "-b", ...)` 也是既有寫法。
- 這次沒有新增例外處理或日誌。`_rg_methods` 對不符的宣告仍用 `continue` 略過,跟原來一樣。
- 提示文字走 `out["warns"].append(...)`,跟同函式其他警告相同。

引句:「+_RG_CONVERTER_ANNS = frozenset(("TypeConverter", "ColumnTypeConverter"))     # Room 3 改名成 ColumnTypeConverter」

**3. 第二種做法:對齊**

沒有引入第二種做法,反而把原有的兩套收成一套。

- 修前,DAO 方法用 `_rg_methods`,型別轉換函式另用一組自成一套的 regex(Kotlin 找 `fun`,Java 找括號前的名字)。這份 diff 把後者刪掉,全部走 `_rg_methods`。
- 宣告名 regex 改成 `(?:[^(@{};]|@[\w.]+(?=\s))*?`。這是改同一條 regex,沒有另寫一個函式。DAO 方法和轉換函式一起受益。
- 沒有自創工具函式。Room 2 的 `@TypeConverter` 仍走同一條路徑,由 `_RG_CONVERTER_ANNS` 涵蓋。
- `_rg_methods` 回傳的第四欄「是交易方法」,轉換函式呼叫端用 `_tx` 丟棄。這是 Python 慣例寫法,沒有另開分支。
- 我另外查了 `scripts/lumos`,Room 守衛段裡沒有第二處寫死 `TypeConverter` 的 regex 漏改。

引句:「+    cs = [(n, a, b) for n, a, b, _tx in _rg_methods(t, java, _RG_CONVERTER_ANNS)]」

**修補鏡頭三項(只就一不一致回答)**

- ①修復效果的行為證據:案例檔列的證據是 `t_room_java_typeuse_and_annotation_run` 修前紅、修後綠。我沒有實跑,行為面未判定。
- ②正常路徑與相鄰呼叫路徑:結構上,`_rg_spans` 的回傳形狀沒變,DAO 與 `@TypeConverter` 的呼叫點都沒動。實際行為未判定。
- ③同一案例修前修後的結果:未判定。案例檔另列了兩個已知未涵蓋的限制(Kotlin `=` 單一運算式本體,以及修飾字之間夾帶括號註記),這兩條跟一不一致無關。

不對齊共 0 條,其中 major 0 條
