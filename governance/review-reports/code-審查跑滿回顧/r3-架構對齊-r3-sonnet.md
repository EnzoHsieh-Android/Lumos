severity: major

# 架構對齊-r3-sonnet(第 3 輪,鏡頭:架構對齊)

審的是 37f2379f..HEAD 的差異(/tmp/code-capretro-r3.patch)。第二輪收回了三處第二種做法(補換行、讀回顧檔、終端跳脫),對照結果:`_ledger_tail_needs_newline`、`_regular_own_fd`、`_esc_clean` 的既有呼叫者沒被改壞(`_local_ledger_append` 仍要求擁有者、`_drift_ledger_append` 的路徑已先擋捷徑)。但同一輪又各引入一套新的第二種做法,下面兩條是 major。

### F1 `--template --write` 的落點檢查另寫一套,與共用的 `_repo_path_unsafe` 並存(修補引起)
severity: major
blocking: 是 — 專案已有「逐層擋符號連結+解析後要在 repo 內」的唯一實作,這裡自己再寫一份,而且判準更弱,正是該函式註解點名要避免的分岔
- 輸入:`governance/review-reports` 這一層是符號連結、指到 repo 內別的資料夾(例如 `elsewhere/`),對該編號跑 `lumos loop retro <編號> --template --write`。
- 走到哪:`cmd_loop_retro` 的 write 分支自己算 `inside = not os.path.islink(d) and realpath(d).startswith(realpath(root)+sep)`,只看卷證資料夾本身是不是捷徑,上層不看。
- 壞在哪:既有共用函式 `_repo_path_unsafe` 逐層看,會回 `("symlink", governance/review-reports)` 拒絕;這裡的自寫版回「在 repo 內」放行,回顧檔建到 `elsewhere/<編號>/cap-retro.json`,而處置閘、`--check` 讀的是 `governance/review-reports/<編號>/`(讀端 `_regular_own_fd` 不跟隨最後一段、但中間層會跟隨),兩邊對「落點安不安全」的答案不同。字串 `startswith` 比對也與共用版的 `is_relative_to` 不同寫法。
- 既有做法對照:`scripts/lumos:31918` `_repo_path_unsafe`(註解寫明「★逐層擋符號連結+解析後要在 repo 內只有這一份★」),兩個既有呼叫者 `scripts/lumos:31957`(`_note_audit_safe_dir`)與 `scripts/lumos:35336`(`_drift_ledger_path_err`,同樣是「寫帳檔前」的檢查)。
引句:「os.path.realpath(d).startswith(os.path.realpath(str(root)).rstrip(os.sep) + os.sep))」
- 佐證行:file: `scripts/lumos:31918`、file: `scripts/lumos:35336`、file: `scripts/lumos:13645`
- 重現(臨時目錄,未動 repo):
  ```
  root/governance/review-reports -> root/elsewhere   (符號連結,指 repo 內)
  d = _retro_dir(root,"x")
  自寫判準 inside = True
  _repo_path_unsafe(root, "governance/review-reports/x") = ("symlink", root/governance/review-reports)
  ```
  修法方向:改呼叫 `_repo_path_unsafe(root, rel)`(`rel` 用 `governance/review-reports/<編號>`),不再自算。

### F2 審查帳切行「唯一規則」`_ledger_lines` 只接了三處,同一本審查帳還有五處 `splitlines()`,同一列在不同讀者眼中行數不同(修補引起)
severity: major
blocking: 是 — 同一件事(切審查帳)現在有兩套實作,且新函式的註解宣稱自己是唯一規則
- 輸入:審查帳一列的 `auditor` 含 U+2028(寫入端 `json.dumps(ensure_ascii=False)` 不跳脫,第一輪已確認是真實寫法)。
- 走到哪:`_canary_ledger_scan`、`cmd_loop_status`、`cmd_severity_check` 用 `_ledger_lines`(只認 `\r\n`、`\n`、`\r`);`_loop_first_ts_key`(`scripts/lumos:7227`)、逃逸帳去重掃描(`scripts/lumos:11024`、`:11256`、`:11360`)、`scripts/lumos:1021` 的 `_load_rows`,以及治理帳的 `_escape_released_loops`(`scripts/lumos:11377`)仍用 `str.splitlines()`,會在 U+2028/U+2029/U+0085 把那一列劈成兩半、整列當壞行丟掉。
- 壞在哪:同一本帳、同一列,`_canary_ledger_scan` 算出 1 列,`_loop_first_ts_key` 回 None(視為沒有這條迴圈的帳)。第二輪把 `_ledger_lines` 的 docstring 寫成「帳檔切行的唯一規則」,實際是引入第二種做法並只替換一半的呼叫者;原本全檔都是 `splitlines()` 一種做法。
- 既有做法對照:`scripts/lumos:7227`(`_loop_first_ts_key`)、`scripts/lumos:11360`(`_escape_review_rows_by_loop`,與 `_canary_ledger_scan` 讀同一本 `.canary-log.jsonl`、且審查帳列的 `kind` 判斷相同)。
引句:「帳檔切行的唯一規則:只認 \\r\\n、\\n、\\r。不用 splitlines(它還認 U+2028/U+2029/U+0085,寫入端」
- 佐證行:file: `scripts/lumos:7227`、file: `scripts/lumos:11360`、file: `scripts/lumos:11882`
- 重現(臨時目錄造 `.canary-log.jsonl`,一列 `{"loop":"L1","round":"r1","auditor":"a b","ts":"2026-10-01T00:00:00"}`):
  ```
  len(_canary_ledger_scan(env)[0]["L1"]) = 1
  _loop_first_ts_key(env, "L1")           = None
  ```
  修法方向:要嘛把其餘讀審查帳的呼叫者都換成 `_ledger_lines`(同一支再加讀治理帳的 `_escape_released_loops`),要嘛把 docstring 的「唯一」拿掉並在〈誠實界線〉列出還沒接的呼叫者與回頭條件。

### F3 規格〈誠實界線〉的既有缺口清單跟程式對不上(修補引起)
severity: minor
blocking: 否 — 只是筆記與程式不一致,不影響執行
- 輸入:讀規格 `審查跑滿回顧_計劃.md` 〈誠實界線〉第 188 行。
- 壞在哪:該行說「處置閘自己的讀帳迴圈、doctor S12、`_loop_close_stamps` 仍用 splitlines」,但本輪程式已把處置閘讀帳迴圈(`cmd_loop_status`)與 `cmd_severity_check` 換成 `_ledger_lines`;本輪另外沒列、實際仍是 `splitlines` 的清單見 F2。清單既過期又不全,下游照它判斷「還剩哪幾處沒接」會判錯。
引句:「處置閘自己的讀帳迴圈、doctor S12、`_loop_close_stamps` 仍用 `splitlines` 切行」
- 佐證行:file: `scripts/lumos:11564`、file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:188`

### F4 「不能編碼成 UTF-8」另寫一支 `_retro_utf8_bad`,與既有 `_fix_bad_strings` 並存(修補引起)
severity: minor
blocking: 否 — 兩者目前判準在孤立代理字元上一致(實測 `["\ud800"]` 兩邊都判壞;深巢狀 900/990/1500 層兩邊都判沒問題),具體分岔場景拿不出來
- 既有做法:`_fix_bad_strings`(`scripts/lumos:12472`)已經用迭代走訪每個字串(鍵也看)逐一 `.encode("utf-8")` 判孤立代理字元,註解明講「迭代不遞迴,深巢狀不爆」,修正紀錄一族用它。新函式改用 `json.dumps(...).encode(...)` 整份序列化再編碼,並把 `RecursionError`/`TypeError` 也當成「不能編碼」回 True,錯誤原因會被標成「孤立代理字元」。這是同一種檢查的第二套寫法,新增的部分沒有說明為什麼不共用。
引句:「_j.dumps(v, ensure_ascii=False).encode("utf-8")」
- 佐證行:file: `scripts/lumos:12472`、file: `scripts/lumos:13156`

### F5 `_esc_clean` 把「要特殊處理的 Unicode 字元」用寫死範圍再列一組,與以類別為準的 `_PATH_SPECIAL_CATS` 並存(修補引起)
severity: minor
blocking: 否 — 兩者用途不同(顯示消毒要保留 ZWJ,路徑拒收不能),目前沒有具體漏掉的字元造成錯誤輸出
- 既有做法:`scripts/lumos:32284` 的註解寫明「★路徑/名稱裡要當特殊字元處理的 Unicode 類別只有這一份★」(Cc、Cf、Zl、Zp、Cs)。`_esc_clean` 第二輪改成手列 U+202A–U+202E、U+2066–U+2069、U+D800–U+DFFF 與 C0/C1 範圍,新增的雙向控制字元清單是第二份,日後 Unicode 補類別要改兩處;`_esc_clean` 刻意不清 U+2028/U+2029(Zl/Zp),與共用組在這兩類上的判斷也不同,註解沒提這個差異的理由。
引句:「or "\ud800" <= ch <= "\udfff") else ch for ch in str(v))」
- 佐證行:file: `scripts/lumos:32284`、file: `scripts/lumos:10934`

總結:最嚴重 major,blocking 2 條
