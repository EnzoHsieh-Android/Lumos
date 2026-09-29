severity: major

## F1 四支入口腳本各抄一份「印略過原因」,放在受守衛段之外,沒有任何機械守一致
severity: major
blocking: 是 — 同一件事在四個檔各寫一份而沒有機械守一致(第二種做法)
引句:「+# LUMOS_PYTHON 設了卻被略過、改用別支時現在就講:之後掛鉤問 lumos 會因同一個值擋下(代碼審 r3)」
1. 這一行加四行(get.sh、install.sh、scripts/install-hooks.sh、scripts/install-graph-toolchain.sh 各一份,get.sh 縮排還不同)的 `if [ -n "$_LUMOS_ANY_NOTE" ]; then printf ...` 貼在 `# ── python-launcher end ──` 標記之後。專案對「找任何 python」段的既有做法是逐字內嵌加測試守一致。
2. 對照:t_python_launcher_blocks_agree 只比 begin/end 之間的段落,標記之外的這一行不在守衛範圍。
3. 重現:在臨時複製的 repo 把四支腳本的這一行全刪,跑 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k python`,輸出「118 passed, 0 failed」,全綠。刪掉、改字、只留一支都不會紅。
4. 這一行是規格第 2 點「LUMOS_PYTHON 被略過要當場印原因」的唯一實作,未來改 `_LUMOS_ANY_NOTE` 語意時每個接手的人要自己記得改四處。
file: `scripts/test_lumos.py:51425`
file: `get.sh:94`
file: `scripts/install-hooks.sh:54`

## 已看,無 finding
- 問 1(分層):`_py_which`、`_py_uv_find`、`_hook_python_problems` 都留在 scripts/lumos 既有的 `_py_*` 那一組,呼叫方向與 r3 前一致,無跨層直呼。
- 問 2(命名與錯誤處理):`_py_uv_find` 回 `(路徑或 None, 說明)` 與同組 `_py_probe`、`_py_which` 一致;`hook_dir`、`dirs[fam]` 沿用同函式內既有的 `fam` 迴圈。已看,無 finding。⚠ `_py_uv_find` 用 uv 英文訊息 `No interpreter found` 判斷,專案裡沒有既有的對照做法可比,不列。
- 問 3(第二種做法):pre-commit 與 pre-push 新增的「絕對路徑且真為 3.14」驗證位在 `# ── python-314 begin/end ──` 段內,t_python_launcher_blocks_agree 會比兩份逐字一致,已有機械守。doctor 的兩家目錄集合(`dirs`)是照 merge-claude-settings.py 的 `_hook_cmd` 手抄的形狀,但測試 ⑩ 拿合併程式真寫出的設定餵,安裝端改形狀會紅,已有守衛。
- 棧別檢核 py-external(tension):existing 指的 scripts/slim-scan.py 的寫法、hazard、suggestion 與 chosen 這輪 diff 沒有動到相關處,查不到為假,不報。

不對齊共 1 條,其中 major 1 條;blocking 共 1 條。
