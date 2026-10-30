severity: minor

## 發現

### Y1
severity: minor
blocking: no
`scripts/test_lumos.py` 的 `t_prepush_next_step_is_the_call_the_gate_ran`(③ 項)和 `scripts/hooks/pre-push:117` 的 `pp_q`。

測試只用 `;`、`'`、中文、`&`、`?`、`:` 這幾種字元,沒有 `$`、反引號、`(`、`)`、`|`、`<`、`>`、`!`、`#`。把 `pp_q` 的判斷從白名單改成黑名單,測試仍然全綠,但 `feat$(id)` 會原樣印出來。使用者把整行貼進 shell,`$(id)` 就會被執行。

引句:「+    case "$1" in
+    "" | *[!A-Za-z0-9_./:@%+=,-]*)」

我拿暫存 clone 把 `pp_q` 的樣式改成 `"" | *[\;\&\ \']*)`。
- 兩版對照:
  - 6365cb906(修後)正式版:`pp_q 'feat$(id)'` 輸出 `'feat$(id)'`,有被包起來。
  - 改成黑名單後:同一個輸入輸出 `feat$(id)`,沒有引號。
- `python3.14 scripts/test_lumos.py -k t_prepush_next_step_is_the_call_the_gate_ran` 結果是 `44 passed, 0 failed`,沒有任何斷言變紅。
- 修前版 e4190cab7 我沒另外跑。修前用的是 `printf '%q'`,對 `$` 本來就會跳脫。

歸因:未判定。這是測試不夠完整,不是掛鉤現在的行為有錯。修補新增的 ③ 項本來要保護的就是引號,只是少了 shell 元字元那一半。掛鉤目前的白名單對 `$`、反引號是正確的。

### Y2
severity: minor
blocking: no
`scripts/hooks/pre-push:117` 的 `pp_q` 白名單包含 `=`。`=` 放在字首時(分支名或遠端名以 `=` 開頭),`pp_q` 不會加引號。使用者的互動 shell 是 zsh,貼上後 `=ls` 會被展開成 `/bin/ls`。

引句:「+    "" | *[!A-Za-z0-9_./:@%+=,-]*)」

驗證:`zsh -c 'echo =ls'` 輸出 `/bin/ls`。修前的 `printf '%q' =ls` 在 bash 3.2 輸出 `=ls`,同樣沒加引號。
- 歸因:有證據的原有漏查,不是修復回歸。
- 這個場景需要以 `=` 開頭的分支名,很冷門,所以只標 minor。

## 已驗主張(命令與結果)

**① 原問題的修復效果**
- 中文在 bash 3.2 下照原樣輸出。
  - `/bin/bash -c 'printf "%q\n" 中文'` 輸出 `$'�\255�\226\207'`(舊寫法會損壞中文)。
  - 同一支 bash 3.2.57 跑 `pp_q "中文"` 輸出 `'中文'`。
  - `LC_ALL=C` 下結果相同。
- 15 個輸入全部通過「用 eval 還原後等於原值」的檢查,在 bash 3.2.57 加 `set -u` 下跑:空字串、`abc`、`a'b`、`a\b`、含換行、`a*b`、`中文`、`feat;'中x`、含空白、`~x`、`#x`、`a=b`、`-x`、`!x`、`a$b`、反引號。
- 純文件推送的自主迴圈重跑指令會帶上實際跑的 `-k`,直譯器路徑有空白時也不會斷。
  - `python3.14 scripts/test_lumos.py -k t_prepush_blocked_last_line_is_next_step` 結果 `5 passed, 0 failed`。
  - 變異 M5(`$(pp_q "$PY")` 改回 `$PY`):③ 自主迴圈那支轉紅。
  - 變異 M6(拿掉 `${_AUTOLOOP_ARGS+…}`):② 轉紅。M6 等於修前的寫法,所以修前這條也是紅的。
- 遠端名和 ref 名都有被測試保護。變異 M4(`--push-remote` 不加 `pp_q`):③ 遠端名轉紅,`43 passed, 1 failed`。
- `python3.14 scripts/test_lumos.py -k t_superseded_contract_not_sent` 結果 `11 passed, 0 failed`,新增的 ④ 兩條都過。
- `_impact_contract` 改用 `line.partition(":")[2]` 後,四種輸入的判定與修前一致:`KEY:★IRREVERSIBLE★ x [status:superseded]`、`KEY:(2026-01-01)★IRREVERSIBLE★ …`、`說明:foo` 都判為作廢(True)。「`line` 一定以 `KEY:` 開頭」這點由 `IRREVERSIBLE_RE.match(line.strip())` 保證。
- 未驗:`_door_linked_signals` 只透過 `_contract_key_matches` 走作廢過濾,我沒另外對它造變異。

**② 修補處的正常、錯誤與相鄰路徑**
- `pp_q` 定義在 117 行,使用處最早在 593、698、838、984 行,函式都已定義,沒有順序問題。
- 這支掛鉤沒有 `set -e`。`grep -n "set -e\|errexit\|pipefail"` 只在註解的 788 行有出現,所以新增的 `$(…)` 不會讓掛鉤提前結束。`set -u` 下 `pp_q` 的 `$1` 一定有傳。
- 展開 `${_AUTOLOOP_ARGS+ ${_AUTOLOOP_ARGS[*]}}`:
  - 空陣列時,bash 3.2.57 輸出 `xy`(空)。
  - 非空時輸出 `x -k realy`。
  - `IFS` 在這段是預設值,沒有被改動。
- `local _s=${1//\'/\'\\\'\'}` 寫在 `case` 分支裡,bash 3.2 正常。賦值右邊沒加引號,但賦值不會斷詞,輸出已驗證正確。
- 相鄰路徑:
  - `python3.14 scripts/test_lumos.py -k t_prepush_next_step_is_the_call_the_gate_ran` 結果 `44 passed, 0 failed`,包含 ① 各閘、兩個 ref、⑥ 簡版彙總、⑦ 真 lumos 解析。這支耗時 96.7s,餘裕只有 2 倍。我是和另一個測試同時跑的,沒在無負載下重測,所以這個數字未判定。
  - `FAKE_PY_PATH` 和 `FAKE_PITFALLS_JSON` 只有在環境變數有設時才生效,其他測試沒設就維持原行為。`hook_argv=()` 的預設值也不會改變原行為。
  - 變異 M1(黑名單版 `pp_q`)讓測試照綠,見 Y1。

**③ 新發現在修前、修後各是什麼結果**
- Y1:未判定,見上。
- Y2:修前 `printf '%q'` 在 bash 3.2 輸出 `=ls`(無引號),修後 `pp_q` 輸出 `=ls`(無引號),兩版相同。

## 鏡頭
- **正確性**:上面已逐項走過。
- **pitfalls manifest**:0 條,沒有題目。
- **圖譜鏡頭**:
  - 這次沒附固定席筆記(鏡頭計算超時)。
  - 讀了 `Systems/bound-tests-gate.md`:新增了 PITFALL 行,`[出處:]`、`[根因:]`、`[防回歸:]` 都有寫。
  - 讀了 `Systems/派工鏡頭.md:19`:作廢過濾的 WHY 行已存在,而且 `_impact_contract` 單獨過濾這點已有寫。
  - 兩處筆記跟程式行為一致。
  - 研究報告的「Sonnet 席是 5.5」措辭修正只改了筆記,不影響程式。
- **消費專案、bash 3.2 與特殊路徑**:
  - `pp_q` 只用 bash 3.2 就有的語法:`case` 樣式、`${var//pat/rep}`、`local`。沒用 `printf %q`、關聯陣列或 `${var@Q}`。
  - 特殊字元(單引號、反斜線、換行、`*`、中文)都已在 bash 3.2 下驗證。
  - 路徑含空白的情況由 ③ 測試覆蓋,變異 M5 能把它翻紅。
- **角色卡**:沒附,略過。

## 未驗範圍
- 沒有在 Linux、GNU bash 4/5 或其他語系(例如 Big5)下實跑。只驗了 macOS 的 `/bin/bash` 3.2.57,以及預設語系和 `LC_ALL=C`。
- 沒跑全套測試,也沒跑 `-k prepush` 整批,只跑了點名的三支測試。
- 不寫整體無回歸保證。

暫存 clone 和腳本已用字面絕對路徑刪除;repo 未被我改動。

本報告最高等級:minor
