severity: minor

第 2 輪「測試是否真的守住修正」。做法:在 clone 對 scripts/lumos 做 30 個突變(每個突變前清 __pycache__),各跑 5 組相關測試(`-k guard_kill_add_warns_drifted`、`doctor_kill_recipe_drift`、`kill_recipe_check_matches`、`guard_kill_rm`、`multiplatform_doctor_check_t`)。30 個裡 17 個被翻紅;沒紅的 13 個中,真有分量的 4 條列在下面,其餘 9 個是等價突變或補充說明(見最後)。沒有發現「修法本身做錯」,全是測試沒釘住。

翻紅的(確認測試真的守住):`_kill_pathspec` 拿掉結尾 `.`/`..` 檢查、整個停用還原檢查、不做 NFC(只在 macOS 才紅);`_kill_alias` 只比大小寫、只比 Unicode、兩者都不比;`_kill_show` 不跳脫 Cc(含 C1)、整個不跳脫、不做 json 引號;malformed 不驗 new、不驗 test 名白名單;P2 設定檔讀不了時提早 break、設定壞時先回 cfg 再驗欄位格式;Check T 去掉例外保護、Check T 無條件吞掉;原文次數判成 `<1` 才算錯;CRLF 不正規化;相對連結目標當絕對;kill-add 兜底只接一種例外。

## F1 `_kill_pathspec` 的「`..` 退出 repo 頂就失敗」那條沒有測試釘住
severity: minor
blocking: 否
引句:「+            if not out:」
file: `scripts/lumos:13087`
1. 突變:`if not out: return None; out.pop()` 改成 `if out: out.pop()`(`..` 退過頭時照樣略過)。五組測試全綠(guard_kill_add_warns_drifted 27/0、doctor_kill_recipe_drift 27/0、kill_recipe_check_matches 63/0、guard_kill_rm 21/0、check_t 2/0)。
2. 為什麼現有格子抓不到:對照測試的「..爬出 repo 頂再經 wt 爬回來」(`../wt/prod.py`)在 repo 裡沒有 `wt/prod.py`,所以突變後算出的 `wt/prod.py` 本來就不在提交裡,恰好還是 unrestorable;別格(`../outside.py`、`../myrepo/prod.py`)在 `_kill_resolve` 就判 outside,到不了這裡。
3. 重現(當場翻出錯判):在突變版 clone 用 `_krc_cell(recipe_file="../wt/prod.py", files={"wt/prod.py": "LIMIT = 5\n"})`——repo 內多提交一支 `wt/prod.py`。突變版判斷函式回 `ok`,真跑 guard kill 回 error(「revert 失敗——後續同組配方作廢防污染」),`_krc_match` 回 `(False, 'error', ...)`;原版回 `unrestorable`、對得上。建議對照測試加一格這個。
4. 影響範圍窄(需要 repo 裡真的有叫 `wt` 的資料夾),所以只標 minor。

## F2 `_kill_show` 只有 Cc 被測試釘住,Cf(雙向覆寫)與 Zl/Zp 拿掉測試照綠
severity: minor
blocking: 否
引句:「+    return "".join(c if unicodedata.category(c) not in ("Cc", "Cf", "Zl", "Zp") else f"\\u{ord(c):04x}"」
file: `scripts/lumos:13050`(`_kill_show`;測試端見 `scripts/test_lumos.py` 的 t_doctor_kill_recipe_drift ⑫ 與 t_guard_kill_add_warns_drifted ⑦c)
1. 突變 A:元組拿掉 "Cf" → 五組全綠。突變 B:拿掉 "Zl" → 五組全綠。對照:拿掉 "Cc"(只留 Zl/Zp/Cf)→ doctor_kill_recipe_drift 紅;整個不跳脫 → 紅。
2. 也就是第 1 輪資安席 F1 的實質威脅「雙向覆寫字元(U+202E)蓋掉修法」「U+2028 行分隔」,修法的 Cf/Zl/Zp 三類沒有任何測試用到;測試只放了 `\x1b`、換行這類 Cc。有人把元組「簡化」成只剩 Cc,CI 不會紅。
3. 建議在 kill-add 測試 ⑦c 或 doctor ⑫ 的路徑再夾 `‮` 與 ` ` 各一個,斷言輸出不含原始字元。

## F3 git 子程序逾時、ls-tree 失敗也快取,兩條修法都沒有測試
severity: minor
blocking: 否
引句:「+            ctx["trees"][key] = (None, why)」
file: `scripts/lumos:13027`
1. 突變 A:`_kill_tree` 的 `subprocess.run(... timeout=_KILL_GIT_TIMEOUT)` 拿掉 timeout → 五組全綠。突變 B:`_KILL_GIT_TIMEOUT = None` / `100000` → 全綠。突變 C:失敗時不寫快取(`return (None, why)`)→ 全綠。
2. 測試檔裡根本沒有 `_KILL_GIT_TIMEOUT`、對 `_kill_tree` 注入 `TimeoutExpired`、或計算 ls-tree 被呼叫幾次的斷言(grep 結果只有別的功能的 TimeoutExpired)。第 1 輪併發席 k1/k2 兩條折入的修法,目前靠讀碼保證。
3. 建議:行程內把 `subprocess.run` 換成會丟 `TimeoutExpired` 的替身,斷言 (a) 判成 noroot、不是崩潰,(b) 同一個 repo 兩條配方只呼叫一次替身。i. 這兩條是 minor 風險(逾時只在鎖 30 秒被接手的極端情況才有後果)。

## F4 本機(macOS)抓不到「`_kill_alias` 先問檔案系統」這道保護;大小寫格只在大小寫敏感的檔案系統才有分辨力
severity: minor
blocking: 否
引句:「+    if not os.path.lexists(os.path.join(str(top), *pth[1:], name)):」
file: `scripts/lumos:13062`(測試端:t_kill_recipe_check_matches_guard_kill 的「大小寫跟提交裡不同」格,期望值寫成 `os.path.exists` 的 lambda)
1. 突變:把這個 `lexists` 守門整段拿掉 → 本機(APFS 不分大小寫)五組全綠。
2. 原因:期望值是「檔案系統開得到就 unrestorable、開不到就 missing」,macOS 上 `PROD.py` 一定開得到,「開不到 → missing」那一支永遠不會被走到。在 Linux CI 上這格會走 missing 那支,拿掉守門就會變成 unrestorable、紅;所以不是恆綠,只是本機看不出。
3. 結論:Linux CI 有守住,但作者在 macOS 改這段時本機測試不會警告;可以在測試裡直接造一個「名字不存在」的格(如 `NOPE.py`,提交裡沒有同名檔)讓兩種檔案系統都走到「回 None」那支。同理,`_kill_pathspec` 的 NFC 分支只在 darwin 才有測試分辨力(拿掉 NFC 後 kill_recipe_check_matches 在 macOS 紅 2 格;Linux 上那兩格走 missing,不會紅)。這兩處是平台特性造成的守衛不對稱,不是錯誤。

## 其餘存活突變(不當 finding,供收貨參考)
1. `_kill_bad_fields` 拿掉 "test" 的型別檢查:全綠。kill-add 一定帶 test,手寫缺 test 的筆記才會到;P2 的每條例外保護會接住。「缺 new」有格、「缺 test」沒格,補一格即可。
2. `_kill_judge_file` 把 `kind != "file"` 放寬成連結也過、`_kill_read_text` 拿掉 S_ISREG 判斷:全綠。前者結果仍由後續 `os.stat` 迴圈擋成 missing(等價);後者沒有具名管線的測試格。
3. 新測試有沒有依賴本機檔案系統特性而恆綠/恆紅:對照測試的 Unicode 與大小寫兩格已用 `os.path.exists` 算期望值,Linux 上不會恆紅;沒看到斷言恆真的(逐格 `got["status"] == want` 與「跟真跑 guard kill 對得上」兩個斷言都真的有被突變翻紅過)。

最高等級:minor
