severity: major

**1. 分層與依賴方向:對齊,但有一處不一致。**
- 新範本放在 `scripts/templates/`,登記在 `_VENDORED_TREE_FILES`,位置、登記方式、skill 用 `scripts/templates/…` 這種專案相對路徑引用,都跟 `android-receipt-rerun.sh` 一樣。對照:`scripts/lumos:31913`(patch 新增的那一行緊貼在 receipt-rerun 那行之後)、`skills/lumos-android-evidence/reference.md:80`、`SKILL.md:138`。
- Lumos 本體沒有去跑 trace_processor 或 sqlite。skill 叫人把 `__PROCESS__` 換掉、交給 trace_processor 跑,這個做法跟 rerun.sh 範本相同,沒有跨層直呼。
- 沒有跨層直呼,不判 major。
- 有一處不一致:查詢放在範本檔,而 skill 以往只靠 reference.md 的程式碼區塊規定查詢怎麼寫(見第 3 問)。

**2. 命名與錯誤處理:大致對齊,有一處檔頭不對齊。**
- 檔名 `android-ui-attribution.sql` 沿用 `android-<用途>` 的命名。
- 測試命名 `t_android_ui_attribution_*` 沿用 `t_android_evidence_*` 的前綴。
- 前置檢查沿用 `check("前置:範本檔在 scripts/templates/", …)`。
- 讀範本真檔的方式 `Path(GRAPHCTL).resolve().parent / "templates" / …` 跟 `scripts/test_lumos.py:17761` 一致。
- 範本不在時回 `None` 並提早 return,也跟既有測試一致。
- 不對齊:既有授權守衛 `t_license_*`(`scripts/test_lumos.py:53797-53824`)規定每支被複製的檔都要有以 `#` 開頭的 SPDX 行。新 .sql 用 `--` 寫 SPDX,所以那條檢查會判成缺標示。我用同一條 regex 對新檔跑過,結果是 False。這是用了不同的註解寫法,導致既有守衛判錯。

**3. 第二種做法:有,判 major。**
- 範本目錄原本只放 `.sh` 和 `.md`,放 `.sql` 是新類型。
- 更大的差別在查詢的位置。reference.md:62-76 是「查詢由審查者寫在 queries.sql 標頭 + SQL 本體」,SQL 是每份收據自己寫的內容。diff 把一條固定的 88 行查詢變成工具鏈的版控範本,再讓人把 `__PROCESS__` 取代後複製進 queries.sql。工具鏈裡沒有其他「SQL 範本 + 佔位字取代」的先例。
- 測試用 `sqlite3` 偽造 Perfetto 的四張表來跑 SQL,也是新做法(`scripts/test_lumos.py:17798`)。既有的 rerun 測試是用假的 trace_processor shell 腳本。專案裡的 `sqlite3` 只出現在 usage ledger 檔名,和一個列在禁用清單的字串。
- 這個 sqlite 測試用的是 SQLite 語法,而 skill 要在真的 trace_processor(Perfetto 方言)上跑。測試內容和實際執行環境不是同一個,兩邊也沒有互相對照的守衛。
- 專案裡沒有既有的 SQL 範本可以對照。我不確定這算「該改回 reference.md 程式碼區塊」還是「新增一類範本」,所以只列出事實,是否接受交給編排者決定。

**Finding**

1. 引入第二種做法:`.sql` 範本、`__PROCESS__` 佔位字取代、sqlite3 偽表測試
severity: major
blocking: 是
引句:「只用標準 SQLite 語法與 slice/thread_track/thread/process 四張表(測試用 Python 內建的 sqlite3 跑同一支檔)。」
file: `scripts/templates/android-ui-attribution.sql:20`

2. 範本檔頭的 SPDX 用 `--` 註解,既有授權守衛只認 `#` 開頭
severity: minor
blocking: 否
引句:「-- SPDX-License-Identifier: MIT」
file: `scripts/templates/android-ui-attribution.sql:2`

不對齊共 2 條,其中 major 1 條

⚠ 交編排者:第 1 條的 major 嚴重度成立的前提是「專案要有單一的做法」。專案目前沒有 SQL 範本的先例,所以也可能被視為合理的新增類型。
