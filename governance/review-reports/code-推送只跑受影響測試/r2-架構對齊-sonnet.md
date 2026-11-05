severity: minor

**1. 分層與依賴方向:對齊。**
- 掛鉤的新碼是把「先算降級原因、再共用一段」放在同一個 `for _ppl` 迴圈內。它延續同檔既有的做法,先算 `_suite_this`,再用 `case "$_suite_this"` 設 `_SUITE_*` 旗標(`scripts/hooks/pre-push:552-553`、`:596`)。
- 這一輪把兩份複製的取關鍵字段落(`affected_keys`、`autoloop_full`)合成一份。這是往既有做法靠攏,沒有新增層。
- `scripts/lumos` 沒有新增函式或跨層呼叫。`_pitfall_diff_collect` 兩處(`scripts/lumos:62272`、`:62339`)從 `_sr.get("computed", True)` 改成 `_sr["computed"]`,和同一行的 `_sr["light_ok"]`、`_sr["graph"]` 直接索引一致。
- `_test_suite_for_range` 的所有回傳路徑都帶 `computed`,逐條看過:`:62073`、`:62075`、`:62079` 用 `dict(full, …)`;`:62086`、`:62089` 明寫 `"computed": True`。
- 新測試用 `m._test_suite_for_range = lambda …`,配 try/finally 還原。這和同檔的猴子補丁寫法一樣(`scripts/test_lumos.py:2114` 的 `_orig_append`、`:14970`)。

**2. 命名與錯誤處理:大致對齊,有一處命名不一致。**
- 失敗方向對齊。漏帶 `computed` 會丟 `KeyError`,pitfalls 就不輸出 JSON,掛鉤拿不到 JSON 就照全套,也就是往多跑的方向退。這和同檔 fail-safe 的註解一致(`scripts/lumos:62060`)。
- 測試名 `t_prepush_feature_branch_already_light` 接在 `t_prepush_feature_branch_*` 系列後面,沒問題。
- 命名有一條 finding(下面 finding 2)。

**3. 第二種做法:有一處。**
- 新測試 `t_prepush_feature_branch_already_light` 用 `next(d.rglob("Systems/Home.md"))` 找筆記。
- 鄰居測試直接用 `_sc_setup` 回傳的 `kg`,寫成 `kg / "Systems" / "Home.md"`(`scripts/test_lumos.py:76653`、`:76659`、`:77419`、`:77445`、`:77566`)。
- `_ppfb_harness` 呼叫 `_sc_setup` 時把 `kg` 丟掉了(`d, _kg, _p = _sc_setup(name)`),所以新測試才得靠搜尋。
- 整個測試檔裡沒有第二處用 `rglob` 找筆記(`rglob` 用到的地方都是別的用途),所以這是新做法。

---

severity: minor
blocking: 否
Finding 1:測試用 `rglob` 找筆記,鄰居直接用 fixture 回傳的路徑
引句:「hm = next(d.rglob("Systems/Home.md"))   # _sc_setup 建的那篇(管 tests/test_x.py);harness 不回圖譜根,照路徑找」
- 對照:`scripts/test_lumos.py:76653` 等處直接用 `kg / "Systems" / "Home.md"`。
- 差異:`_ppfb_harness` 不回傳 `kg`,新測試改用搜尋。
- 這確實是「同一件事的第二種做法」。我把它降到 minor,因為 fixture 目錄裡只有一篇 `Home.md`,搜尋結果是確定的,拿錯檔的具體失敗場景我講不出來。
- ⚠ 交編排者:如果依錨判「引入第二種做法即 major」,這條可升。
- 歸因:修補新增,是有證據的修復回歸。這個測試是本輪新增的,修前不存在。

severity: minor
blocking: 否
Finding 2:`_down` 的值混了兩條軸
引句:「      _down="light"」
- 同一個變數,`"light"` 描述的是「走 push-check 判 light 的路徑」,`"branch"` 描述的是「走功能分支的路徑」。
- 對照:緊鄰的 `_suite_this` 值是 full/light/docs,表示結果;`_SUITE_BRANCH_DOWN` 是 `_SUITE_*` 結果旗標家族。
- 差異:`_down="light"` 讀起來像「降成 light」,和同段註解「原本就判 light 的不算降級」互相矛盾,而且和 `_suite_this="light"` 字面撞名。
- 具體場景:下一個讀的人會把 `_down="light"` 當成印降級那行的條件,但實際只有 `"branch"` 那條會設 `_SUITE_BRANCH_DOWN`。
- 歸因:修補新增。修前是兩個 `if` 各自直接設 `_suite_this`,沒有 `_down`。

---

不對齊共 2 條,其中會擋的 0 條。
