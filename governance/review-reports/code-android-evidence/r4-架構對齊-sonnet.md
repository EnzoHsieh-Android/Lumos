severity: minor

## 1 重跑腳本的直譯器與檔頭跟 scripts/ 既有 .sh 不一樣
severity: minor
blocking: 否
引句:「# lumos-android-evidence 收據的重跑腳本:照 queries.sql 標頭重跑每條查詢並比對 expect。」

新檔 `scripts/templates/android-receipt-rerun.sh` 的 shebang 是 `#!/bin/sh`,安全設定是 `set -eu`。專案所有既有 .sh 都是 `#!/usr/bin/env bash` 加 `set -euo pipefail`:
- `scripts/external-seat.sh:1` 和 `:8`
- `scripts/fetch-notesmd.sh:1`
- `scripts/graph-rename.sh:1`

檔頭也有兩處不同:
- `fetch-notesmd.sh:4-5` 和 `graph-rename.sh:4-5` 在 SPDX 後面有兩行「MIT licensed. Full text…」。新檔沒有。
- 鄰居第一行說明寫成「檔名 — 一句描述」(`fetch-notesmd.sh:6`、`graph-rename.sh:6`、`external-seat.sh:2`)。新檔寫成「名稱 收據的…:…」。

這只是寫法不一致,結構是對的。`sh` 在沒裝 bash 的機器上更能跑,而收據本來就要在沒裝 Lumos 的機器上重跑。這一點我判不準是刻意還是疏忽,所以不升級成 major。

## 三問

**1. 分層與依賴方向:對齊,沒有跨層直呼。**
- 重跑腳本放在 `scripts/templates/`,並登記在 `_VENDORED_TREE_FILES`(`scripts/lumos:31913` 附近)。登記位置和寫法都照 `note-audit-reread.md` 那一行的先例,行尾附註解。
- 複製清單由 `_vendored_pending`(`scripts/lumos:32202`)統一處理,新檔不需要另外接線。
- 檔案權限 755 和 `scripts/*.sh` 一致(`git ls-files -s` 對過)。
- 腳本自己不呼叫 `scripts/lumos`,所以沒有跨層。這符合已人裁的「不做 lumos 子指令」。
- `lumos macrobench` 這邊的新碼都落在 macrobench 那一組函式裡,依賴方向和鄰居相同:
  - `_macrobench_thresholds` 是 `(值, err)` 的回傳形狀,和 `_macrobench_config`(`scripts/lumos:39394-39406`)一致。
  - `_macrobench_mode` 呼叫它,再交給 `_macrobench_check_thresholds` 和 `_macrobench_print_thresholds`。這個拆法和既有的 `_macrobench_compare` / `_macrobench_print` 一致。

**2. 命名與錯誤處理:對齊,只有發現 1 那一項。**
- 錯誤處理:
  - 門檻檔或設定檔壞了,印 stderr「擋下:…」並回 2,走的是 `_macrobench_mode` 原本的路徑。
  - `rerun.sh` 的「擋下:收據本身寫錯——…」回 2,也符合 lumos 慣例。測試用 `said.startswith("擋下:")` 驗過。
- 命名與匯入:
  - 命名用 `_macrobench_*` 前綴和 `MACROBENCH_*` 常數,和 `MACROBENCH_DEFAULTS` 等同族。
  - 函式內才 `import math` / `import hashlib` / `import datetime`,這是檔內的慣例,`_macrobench_read_one` 就是 `import json` 放函式內。
- `_macrobench_num` 包住 `_secev_num`(`scripts/lumos:8554`),再加 `math.isfinite`。檔內其他地方也是就地用 `isfinite`(`scripts/lumos:52195`、`:58321`),所以沒有出現新的有限數判法。
- 測試用 `_mb_run` 以 `sys.executable GRAPHCTL …` 跑 subprocess(`scripts/test_lumos.py:17552`)。新測試沿用同一個函式,`rerun.sh` 那支另用 `sp.run(["sh", …])`,寫法一致。

**3. 第二種做法:沒有。**
- 把 Python 用 heredoc 嵌在 shell 裡,已有先例:`scripts/external-seat.sh:16` 的 `python3 - … <<'PY'`。
- 「收據目錄複製範本」這個做法,是已人裁的項目,不重開。
- 新 skill 目錄 `skills/lumos-android-evidence/` 是 SKILL.md 加 reference.md,和 `lumos-code-loop` 同形。我 grep 了安裝清單,既有 skill 沒有登記處,所以新 skill 不需要補登記。
- 基準新增的 `source.sha256` 是另一個欄位,沒有取代 `_vendored_digest`。兩者目的不同:前者對原始 bytes 雜湊,後者會把換行統一成 LF,不構成第二種做法。
- `.lumos/config.json` 的 `node_home.ignore` 用來排除收據目錄,是既有設定(`scripts/lumos:3425`、`:39835`),沒有新機制。

不對齊共 1 條,其中 major 0 條
