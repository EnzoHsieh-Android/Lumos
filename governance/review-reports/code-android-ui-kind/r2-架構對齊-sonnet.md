severity: clean

**1. 分層與依賴方向:對齊**
- 新增的 `android-ui-attribution.sql` 放在 `scripts/templates/`,跟 `android-receipt-rerun.sh` 同一層。
- 登記方式一樣:`scripts/lumos` 的 `_VENDORED_TREE_FILES` 同一個表,緊接在 rerun.sh 那一行之後,都帶行尾註解(`scripts/lumos:31928`、`31929`)。
- 呼叫方向一樣:skill 只用 `scripts/templates/...` 這種專案相對路徑(SKILL.md:53,對照 SKILL.md:138),不依賴工具鏈的安裝位置。
- Lumos 本體沒有去跑 trace_processor。新範本由 skill 指示子代理在收據流程裡使用。
- 測試用 Python 內建的 sqlite3 在記憶體裡建四張表,跑同一份 SQL,沒有去呼叫第三方工具。
- 新測試找範本的寫法跟既有 `t_android_evidence_rerun_refuses_empty` 一樣:`Path(GRAPHCTL).resolve().parent / "templates" / …`,先做「前置:範本檔在」的檢查(`scripts/test_lumos.py:17761`,對照 17984)。
- `t_android_ui_attribution_vendored` 找不到 `skills/` 時拋 `_SrcOnly`,這是專案既有的來源專用跳過機制(`scripts/test_lumos.py:129`、`147`)。

**2. 命名與錯誤處理:對齊**
- 檔頭:rerun.sh 是第 2、3 行 `# SPDX…`,新 SQL 是第 1、2 行 `-- SPDX…`。只有註解符號不同,而 SQL 只能用 `--`。
- 授權測試改成 `.sql` 認 `--`、其他維持只認 `#`,不整體放寬。測試另外加了前置檢查,確認 `.sql` 這條路徑真的有走到(patch 中 `照類型認註解符號那條路徑真的有走到` 那行)。
- 檔名 `android-ui-attribution.sql` 的前綴跟 `android-receipt-rerun.sh` 一致。
- 測試名 `t_android_ui_attribution_*` 沿用 `t_android_evidence_*` 的前綴與 `check(…)` 寫法。
- 重跑腳本把「第一個以分號結尾的行」當查詢結尾,範本註解刻意不以分號結尾。我用 grep 驗過,整份只有最後一行 `ORDER BY f.ts;`。`t_android_ui_attribution_receipt_rerun` 用假分析工具實際跑一次,所以這個約束有測試守著。
- 這個測試的假分析工具和收據目錄組法,沿用 `t_android_evidence_rerun_refuses_empty` 的做法(`scripts/test_lumos.py:17770` 起)。
- 一個小差別:占位字 `__PROCESS__` 的套件名白名單檢查只寫在 SKILL.md:53 的文字裡,沒有機械擋。rerun.sh 的檢查則是機械式的。但這是新增的「代入參數」動作,鄰居沒有對應的東西,所以不算不一致,不列 finding。

**3. 第二種做法:有,但 skill 與 reference.md 已寫明何時用哪一種,足以讓接手的人不必猜**
- 收據裡的查詢出現兩種來源。一種是固定查詢,整份貼範本並換掉 `__PROCESS__`。另一種是一次性查詢,照症狀手寫。
- 這個分界寫在 `reference.md:77`:固定的分析查詢放工具鏈範本目錄、整份貼進來,其餘照舊手寫。SKILL.md:53 也寫了「整份範本連檔頭註解一起貼」。
- 範本的取用方式跟 rerun.sh 不同:rerun.sh 是 `cp` 不改(reference.md:81–84),新範本是貼上並代入參數。差異有理由(範本需要代入行程名),`reference.md:77` 也說明了「占位字貼進來時就換掉,不要留在收據裡」。
- L2 這邊,「Compose 分支」取代 CPU 取樣的條件寫明了:先分 XML / Compose,Compose 長最多才走這條,其他三類長最多就照原本的往下條件(SKILL.md:53 之後的第 2–4 點)。
- 測試用 sqlite3 模擬 Perfetto 的表,專案裡沒有先例。但它只是測試手段,沒有進入生產路徑。
- 表態記錄裡我看到的條目都是 `na` 或 `satisfied`,沒有 `tension`,所以沒有要查的四欄真假。

不對齊共 0 條,其中 major 0 條
