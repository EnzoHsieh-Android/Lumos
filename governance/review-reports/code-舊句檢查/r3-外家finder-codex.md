severity: minor

## F1 新建私有目錄固定走 Unix 權限 API，原生 Windows 無法建立快取層

severity: minor
blocking: 否
引句:「return _chmod_no_follow(cur, 0o700)」
file: `scripts/lumos:34925`, `scripts/lumos:34984`, `scripts/test_lumos.py:57366`, `docs/lumos-toolchain-knowledge/Systems/native-windows-support.md:52`

1. 在原生 Windows 的新家目錄呼叫 `_mkdir_trusted_under_home(".cache", "lumos", "drift-m1")`。
2. `_mkdir_private_layer` 建好第一層後，無條件呼叫 `_chmod_no_follow`；後者以目錄 fd 配合 `os.fchmod`，兩者都是 Unix 路徑，且 `AttributeError` 不在 `except OSError` 內。
3. 若 Windows 拒絕以 `os.open` 開目錄，函式在已建立目錄後回傳 `False`；若開啟成功但沒有 `os.fchmod`，則例外直接逸出。m1、bound-filter、dispatch-lens、vault-lock 共用的新目錄路徑都受影響。
4. 新測試使用 `os.umask`、`os.mkfifo`、`SIGALRM`，只覆蓋 POSIX 分支，沒有測到專案宣稱支援的原生 Windows。
5. 未能重現：唯讀環境沒有 Windows 真機；以移除 `fchmod` 的替身執行 `_chmod_no_follow` 可得到 `AttributeError`。依規則下修一級。

## F2 路徑安全判斷漏掉換行與終端控制字元，仍會印出指向別處的照貼指令

severity: minor
blocking: 否
引句:「if kind == "m1" and _drift_c4_show_name(path) != path:」
file: `scripts/lumos:27809`, `scripts/lumos:27855`, `scripts/lumos:28185`, `scripts/test_lumos.py:57260`

1. 呼叫 `_drift_fix_hint("m1", "Systems/a\nb.md", 7, ["gone"])`；也可將換行換成 ESC。
2. `_drift_c4_show_name` 只轉換 Unicode `Cf`，換行與 ESC 屬於 `Cc`，所以新增的拒絕分支不會觸發。
3. `_drift_fix_hint` 先產生含原始控制字元的命令，之後 `_drift_print_hints` 經 `_esc_clean` 將控制字元改成空格。
4. 最終顯示成 `lumos drift ack 'Systems/a b' 7 --kind m1 ...`，它指向另一個節點，卻仍被呈現為可照貼指令。
5. 新測試只涵蓋 RLO 與零寬字元，沒有覆蓋同一條輸出鏈上的 `Cc` 路徑。

## F3 doctor 拆分兩個開關後，父層設定型別錯誤時漏報舊句檢查狀態

severity: minor
blocking: 否
引句:「out += _drift_old_sentence_doctor_lines(parts)」
file: `scripts/lumos:28481`, `scripts/lumos:29628`, `scripts/lumos:29638`, `scripts/test_lumos.py:57336`

1. 將設定寫成 `{"drift_check": "off"}`，再交給 `_drift_config_parts`。
2. gate 解析器正確產生「drift_check 不是物件」警告；舊句解析器因父層不是字典而把值當成未設定，回傳預設 `warn` 與空警告。
3. 新增的 `_drift_old_sentence_doctor_lines` 對預設 `warn` 回傳空清單，因此 doctor 只說 gate 設定壞了，不再交代舊句檢查仍是 `warn`。
4. 修正前，同一個 gate 警告會附帶 `舊句檢查(drift_check.old_sentence)是 warn`；這次拆線造成資訊遺失。
5. 新測試覆蓋的是父層為物件、內層值寫成 `"Block"`，沒有測到 `drift_check` 本身為字串或 `null` 的分支。

## 圖譜鏡頭判定

- `Systems/lumos-cli-read`：不影響；搜尋結果排除 superseded 的過濾流程沒有改動。
- `Systems/bound-tests-gate`：合約判定流程沒有改動；F1 會讓原生 Windows 的 bound-filter 快取目錄建立失敗，但未見跳過綁定測試或改變阻擋回傳碼。
- `Systems/guard-kill`：不影響；回傳碼優先序與 JSON 輸出路徑均未變。
- `Systems/授權與歸屬`：不影響；vendored 白名單、移除流程及 `scripts/lumos` 授權檔頭均未變。
- `Systems/測試假綠形態`：新增測試對其宣告的 POSIX、`Cf`、內層錯值場景有前置斷言；但 F1 至 F3 分別暴露未覆蓋的平台、字元類別與 malformed 父層分支。
- `Systems/lumos-cli-lifecycle`：不影響；CLAUDE.md sentinel 外內容的 reinject 流程未變。
- `Systems/design-loop`：不影響；設計審材型別與條款綁定判定沒有改動。
- `Systems/pitfalls-code-loop`：未見對風險分級或 code-loop 判定流程的改動；本次問題限於共用目錄、m1 提示及 doctor 接線。

最高等級:minor