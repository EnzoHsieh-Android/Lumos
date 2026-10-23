severity: minor

整體判斷:結構跟鄰居一致。新範本放進既有的範本目錄,走既有的複製清單、有 SPDX 檔頭,測試的讀檔方式和鄰居一樣。重跑腳本的編碼指定和鄰居不同,只算命名/錯誤處理層級。佔位字的寫法也不同。我沒有發現跨層直呼,也沒有沒寫明用法的第二種做法。

**1. 分層與依賴方向:對齊**
- 新範本 `scripts/templates/android-ui-attribution.sql` 放在 `scripts/templates/`,和 `android-receipt-rerun.sh`、`note-audit-*.md` 同層。
- 它登記在 `_VENDORED_TREE_FILES`(`scripts/lumos:31929`),寫法和相鄰那行 `android-receipt-rerun.sh` 的登記一致。登記後 `t_vendored_file_list_matches_what_install_ships`(`scripts/test_lumos.py:15300`)才會綠。
- 相依方向:SKILL.md 指到範本,範本由人貼進收據的 `queries.sql`,再由 `rerun.sh` 讀。
- 測試用 `Path(GRAPHCTL).resolve().parent / "templates" / …` 讀範本(`scripts/test_lumos.py:17797`、`:17972`)。這跟改寫前 `t_android_evidence_rerun_refuses_empty` 的寫法一樣(`scripts/test_lumos.py:17759`)。
- `t_android_ui_attribution_vendored` 沒有直接呼叫 lumos 內部函式,是用既有的 `_load_lumos_inproc()` 載入(`scripts/test_lumos.py:17972` 起)。
- `t_android_ui_attribution_vendored` 讀 skills 的部分用 `raise _SrcOnly` 守住,和 `t_vendored_file_list_matches_what_install_ships` 用 `_need_src` 的做法同類。

**2. 命名與錯誤處理:大致對齊,有一條不對齊**
- 檔頭一致:SQL 範本用 `-- SPDX-FileCopyrightText` 和 `-- SPDX-License-Identifier: MIT`,對應 `.sh` 的 `#` 版本。
- `t_license_headers_travel_with_vendored_files`(`scripts/test_lumos.py:53856`)原本只認 `#`,現在依副檔名認 `--`。這是必要的擴充,並且有前置斷言(假檔名驗證)。
- 編碼指定的對照:
  - `scripts/lumos` 一律在每個呼叫上寫 `encoding="utf-8"` 或 `errors="replace"`,0 處用 `reconfigure`。
  - `scripts/test_lumos.py:22` 有 `sys.stdout.reconfigure(encoding="utf-8")` 的先例。
  - `scripts/templates/android-receipt-rerun.sh:12-13` 新增的 `reconfigure(..., errors='replace')` 加上逐呼叫的 `encoding='utf-8'`,和前述兩處都不衝突。
  - 該腳本是消費專案端的獨立 heredoc,單引號沿用原檔 `open(f'{here}/queries.sql', encoding='utf-8')` 的風格。
  - 所以編碼這項我判對齊,不列為 finding。
- 錯誤回報:`擋下:` 開頭、印到 stderr、回 2,沿用原檔做法,沒有新增形狀。
- 不對齊的一條是佔位字寫法,見 finding 1。

**3. 第二種做法:對齊,說明足夠**
- 新增的「固定查詢放工具鏈範本、整份貼進收據」,和原本「一次性查詢手寫在 `queries.sql`」是兩種來源。`skills/lumos-android-evidence/reference.md` 新增的「查詢有兩種來源」那條已寫明各自的情況:
  - 固定的分析查詢(每次都一樣、只換參數)放範本。
  - 一次性、照這次症狀寫的查詢手寫。
  - 範本的佔位字貼進來時就換掉,不留在收據裡。
- SKILL.md 的 L1 段落有逐步操作(換 `__PROCESS__`、套件名字元限制、expect 的第一欄寫法)。
- 接手的人不必猜,所以不列 major。
- 範本檔頭另寫了「註解不以分號結尾」。這條在 reference.md 的 SQL 本體規則也有,兩處一致。
- 測試用 Python 內建 sqlite3 在記憶體裡建四張表來跑範本(`scripts/test_lumos.py:17794`),和既有 `rerun_refuses_empty` 用假分析工具的做法不同。但被測物不同:前者驗查詢語意,後者驗腳本流程。專案裡沒有可共用的既有同功能做法,我判不列。

**Finding**

1. 佔位字寫法與既有範本不同(`__PROCESS__` 對 `{{NAME}}`)
severity: minor
   blocking: 否
   引句:「用法:把 __PROCESS__ 換成 App 的行程名(套件名),交給 trace_processor 跑」
   file: `scripts/templates/android-ui-attribution.sql:10`
   - 對照:`scripts/templates/note-audit-reread.md:9` 與 `note-audit-judge.md:6` 用 `{{DIFF}}`、`{{REPO_PATH}}`,`scripts/lumos:23125` 也是 `text.replace("{{" + k + "}}", v)`。
   - 差別:鄰居的佔位字由 lumos 程式替換,這份是 AI 照 SKILL.md 手動替換,而且 SQL 裡 `'__PROCESS__'` 要放在字串引號內。不能直接判成錯,但這是第二種佔位字約定。
   - 建議:要嘛改成 `{{PROCESS}}`,要嘛在 reference.md 或範本檔頭一句話說明「手動替換的範本用 `__X__`」。⚠ 這條判不準是不是該升為 finding,交編排者。

不對齊共 1 條,其中 major 0 條
