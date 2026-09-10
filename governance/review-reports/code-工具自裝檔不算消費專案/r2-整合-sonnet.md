severity: minor

### F13 about_code 的 remove 沒有比照 append 正規化路徑,同一個值 append 完自己 remove 不掉
severity: minor
blocking: 否 — 不損毀資料、rc2 訊息本身就把目前存的值列出來,使用者能自行改正,不會擋 push
引句:「存成正規化的樣子,排序加分用的鍵才對得上(src/../src/a.py 跟 src/a.py 要是同一個)」
1. `cmd_append` 在寫入前呼叫 `_about_code_path` 把值正規化(`src/../src/c.ts` 存成 `src/c.ts`),但 `cmd_remove` 對 `about_code` 沒有等價呼叫,直接用使用者輸入的原始字串算 `tgt = link_target(value)` 去比對。
2. 實測重現(/tmp 隔離環境,非本 repo):append about_code `src/../src/c.ts` → 檔案存成 `about_code:\n  - src/c.ts`;接著 remove about_code `src/../src/c.ts`(同一個字串)→ rc2「Systems/TestNode.md 的 about_code 裡沒有 src/../src/c.ts(比對用的目標是 src/../src/c.ts)…目前有 1 項:['src/c.ts']」,必須換成正規化後的 `src/c.ts` 才能刪掉。
3. 佐證行:file: `scripts/lumos:10948` (`cmd_remove` 用未正規化的 `value` 算 `tgt`,沒有走 `_about_code_path`);file: `scripts/lumos:196` (`link_target` 只拆 `[[ ]]`/引號/`#`,不做路徑正規化,所以 `src/../src/c.ts` 跟 `src/c.ts` 對它是兩個不同字串)。

### F14 「安裝/移除的目錄改成同一個常數,不再各記一份」只涵蓋兩處,授權標頭測試仍是第三份硬寫清單
severity: minor
blocking: 否 — 目前三處字面值一致、不影響現有行為,只是未來新增 vendored 目錄時的漂移風險,不影響這批要推的功能
引句:「安裝時整個目錄照來源複製過去的那兩個」
1. 這輪把 `_vendor_toolchain`(安裝)與 `_deinit_remove_vendored`(移除)原本各自硬寫的 `("scripts/hooks", "scripts/templates")` 統一成 `_VENDORED_TREE_DIRS` 常數(`scripts/lumos:13152`),對應到事故筆記「安裝與拆除用的目錄也改成同一個常數,不再各記一份」。
2. 但既有的授權檔頭測試 `t_license_headers_travel_with_vendored_files` 仍自己硬寫同一組目錄字面值來算「會被複製出去的檔案集合」,沒有改用新常數。
3. 佐證行:file: `scripts/test_lumos.py:30371` (`for d in ("scripts/hooks", "scripts/templates"):`,獨立於 `_VENDORED_TREE_DIRS`/`_VENDORED_TREE_FILES` 之外的第三份硬寫清單)。

## 第一輪修法驗收
F1:修到 — 判別從目錄前綴改成 `_VENDORED_ALL` 精確檔名 frozenset(`scripts/lumos:13169`),/tmp 實測 `scripts/hooks/my_own_thing.py` 照樣命中、`scripts/lumos`/`scripts/hooks/claude/impact-hook.py` 才被排除,且 `t_vendored_file_list_matches_what_install_ships` 用 `git ls-files scripts/hooks scripts/templates` 逐檔比對(我自己重跑該指令,結果與 `_VENDORED_TREE_FILES` 十筆完全一致)。
F2:修到 — lint 層在「對齊」判斷之前先用 `_is_vendored_path` 濾過(`scripts/lumos:17744`),對齊/未對齊兩條路都會濾到,讀碼確認無遺漏。
F3:修到 — 全檔只剩 3 個 `_stack_changed_ok(` 呼叫點(刪除行、新增行、claims 掃描),三處都傳了 `_skip_vendored`,無第四處遺漏。
F4:修到 — 實測 append 兩次多筆清單(`src/d.ts`、`src/e.ts`)兩筆都在;`set about_code` 現在直接 rc2「不能用 set 改」,不會壓成一筆。
F5:修到 — 實測絕對路徑 `/etc/hosts`、`../` 跳出 repo、不存在的路徑、目錄(`src`)四種都 rc2 且檔案不動。
F6:修到 — `_set_about_code` 整支函式已移除,`about_code` 不在 `SCALAR_KEYS`,`set` 的擋下訊息也不再列 about_code,只剩 append/remove 一套規則。
F7:修到 — 舊的 `_set_about_code` 直接字串拼接已隨函式整個拿掉;新路徑走 `fmt_list_item`,實測 `src/a: b.ts` 正確存成帶引號的 `"src/a: b.ts"`。
F8:修到 — 事故筆記現在明寫「★它不建立波及連結★——波及計算看的是正文裡用反引號寫出的路徑」與「(波及計算本身不受影響)」。
F9:修到(範圍侷限,見 F14)— `_is_vendored_path` 文檔已拿掉「不另記一份」的失真宣稱,安裝/移除兩處的目錄字面值統一成 `_VENDORED_TREE_DIRS`;但授權測試那第三份硬寫清單沒被這輪動到。
F10:修到 — `_set_about_code` 整支被刪,命名/訊息順序不一致的問題隨函式消失。
F11:修到 — `_stack_ext_counts` 的 `os.path.relpath(dirpath, base)` 現在移到 filenames 迴圈外、每個目錄只算一次(`scripts/lumos` 對應段落),不再逐檔重算。
F12:修到 — `_is_toolchain_repo` 判別鍵沿用既有慣例且方向仍是 fail-closed(判別鍵檔存在才不跳過),既有測試 ④ 與新測試都繼續釘住「工具鏈本體不得被跳過」。

風險掃描清單:誤報 — `scripts/lumos:17603` 命中的是 `_stack_changed_ok` 中文 docstring 裡「『命中 open(...)』」這段描述文字,不是真的呼叫 `open()`,沒有 file handle 資源風險。

總結:最高 severity minor,blocking 共 0 條
