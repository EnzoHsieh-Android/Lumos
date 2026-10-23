severity: minor

**1. 分層與依賴方向:對齊。**
- 新的歸因查詢放在 `scripts/templates/android-ui-attribution.sql`,與重跑腳本同層。它登記在 `_VENDORED_TREE_FILES`(`scripts/lumos` 表尾,緊接 `android-receipt-rerun.sh` 那一行)。
- 相依方向沒有反過來。測試經由 `Path(GRAPHCTL).resolve().parent / "templates"` 讀範本,和改動前的 `t_android_evidence_rerun_refuses_empty` 取範本的方式一樣(`scripts/test_lumos.py:17761`)。
- skill 只用路徑指向範本。重跑腳本沒有呼叫範本,範本也沒有呼叫 lumos,所以沒有跨層直呼。
- `skills/` 只在工具鏈 repo 才有,測試用 `_SrcOnly`(`scripts/test_lumos.py:129`)處理,是既有做法。

**2. 命名與錯誤處理:大致對齊,有兩處不一致。**
- 對齊的部分:
  - 檔頭帶 SPDX 兩行,SQL 用 `--` 註解,與 `.sh`、`.md` 範本的 `#` 標示對應。
  - 分析工具執行不了時,印 stderr「擋下:…」並回 2。這和改動前的重跑腳本、`reference.md` 的回傳碼約定一致。
  - 測試命名 `t_android_ui_attribution_*` 對齊 `t_android_evidence_*` 的系列。
- 不一致一(finding 1):編碼處理。
  - `PYTHONUTF8` 是本 repo 生產程式碼裡第一次出現。全 repo 用 grep 找,在 `scripts/hooks`、`scripts/templates`、`scripts/lumos`、`install.sh` 都沒有;只出現在測試的 `env=` 和筆記裡。
  - 鄰居的做法是逐處明寫 `encoding="utf-8"`、`utf-8-sig` 或 `errors="replace"`。例如 `scripts/lumos:632`、`scripts/lumos:838`、`scripts/hooks/claude/lumos-entry-hook.py:33`。
  - `android-receipt-rerun.sh` 這一支現在兩種並用:先開 `PYTHONUTF8=1`,又在 `open(...)` 與 `subprocess.run` 上保留 `encoding='utf-8-sig'` 和 `errors='replace'`。
- 不一致二(finding 2):`PYTHONUTF8` 的啟動方式與腳本對 Python 版本的要求。
  - 腳本是 `exec env PYTHONUTF8=1 python3`。`env` 是外部指令,並不保證存在。
  - 腳本直接找 `python3`,不走三支 git 掛鉤共用的 python-launcher 區塊(`scripts/hooks/pre-commit:50` 起)。這點在改動前就如此,不算本輪新增。
  - `reference.md` 現在寫「需要 python3.7 以上」。其他地方的下限是 3.14,所以這個數字是第二個版本基準。

**3. 第二種做法:有兩處,說明足夠程度不一。**
- 佔位字有兩種寫法。`__PROCESS__` 與既有的 `{{NAME}}` 並存(`scripts/templates/note-audit-reread.md:9`)。這裡有說明:`skills/lumos-android-evidence/reference.md` 新增的一行寫明 `{{NAME}}` 由 lumos 程式替換、`__NAME__` 由 AI 照 skill 手動替換。判準是「誰來替換」,接手的人不必猜,所以不報。
- 編碼的第二種做法(UTF-8 模式)就是 finding 1。
  - 為什麼不逐處加參數,有寫:`android-receipt-rerun.sh:9-10` 的註解,加上計劃筆記的 PITFALL(傳給分析工具的路徑在參數編碼那一步就失敗,逐處加管不到)。
  - 沒有寫的是「專案其他腳本(逐處明寫 encoding)什麼時候該用哪一種」。
  - 這個理由只在重跑腳本這一個地方成立。`reference.md` 只寫「腳本用 UTF-8 模式跑」,沒有劃清界線。
  - 我判為 minor 而不是 major,是因為理由已留在腳本註解和 PITFALL 裡,且目前只有這一支 sh 包 python 的範本,沒有另一支同功能的檔可以拿來對照。
- SPDX 檢查也分成兩種(finding 3)。
  - `spdx_for` 對 `.sql` 認 `--`、其餘認 `#`。理由寫在測試註解,另有前置斷言釘住行為。
  - 這是為了新檔案類型做的合理擴充,沒有引入第二個檢查機制,只是依副檔名分支。
  - 但 `.lumos` 其他地方(例如 `授權與歸屬.md` 的 KEY 行)只談 `#`,筆記是否同步我沒有逐行查。這是 minor。

**Finding 1:重跑腳本的編碼處理與專案慣例不同**
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 python3 - "$HERE" "$PROJECT_ROOT" "${TP:-trace_processor}" <<'PY'」
file: `scripts/templates/android-receipt-rerun.sh:11`

**Finding 2:`reference.md` 新寫的 python3.7 下限,與專案其他處的 python 版本基準不同**
severity: minor
blocking: 否
引句:「需要 python3.7 以上(標準庫;腳本用 UTF-8 模式跑,收據裡有中文也不受系統語系影響,檔頭帶 BOM 也讀得到)」
file: `skills/lumos-android-evidence/reference.md:90`

**Finding 3:SPDX 檢查依副檔名分兩套註解符號**
severity: minor
blocking: 否
引句:「_spdx_sql = _re.compile(r"^--\s*SPDX-License-Identifier:\s*MIT\s*$", _re.M)」
file: `scripts/test_lumos.py:53632`

不對齊共 3 條,其中 major 0 條

⚠ 兩處交編排者:
- 「UTF-8 模式」這個新做法,是否要另在 skill 或圖譜寫一句與逐處 `encoding=` 的分界,由編排者裁。我判 minor 的前提是只有這一支 sh 包 python 的範本,以後再有同類範本就得補。
- `reference.md:90` 的行號是我依 patch 的 hunk 位置估的(hunk 起於第 66 行),未開原檔逐行核對。
