severity: minor

## F1 _kill_show 自抄一組「要跳脫的 Unicode 類別」,專案已有唯一一份共用的
severity: minor
blocking: 否
引句:「    return "".join(c if unicodedata.category(c) not in ("Cc", "Cf", "Zl", "Zp") else f"\\u{ord(c):04x}"」
file: `scripts/lumos:27516`(`_PATH_SPECIAL_CATS = frozenset(("Cc", "Cf", "Zl", "Zp", "Cs"))`,上方註解明寫「★路徑/名稱裡要當特殊字元處理的 Unicode 類別只有這一份★」「不另抄一組」)
file: `scripts/lumos:27519`(`_path_special_chars`)、`scripts/lumos:30065`(`_drift_c4_show_name` 同樣是「跳脫 Cf 成 \uXXXX」的印法,但至少是在共用類別之外的單點特例並註明)

1. 專案裡已有共用類別集合 `_PATH_SPECIAL_CATS` 與謂詞 `_path_special_chars`(回頭重讀代碼審 r3 架構對齊席 F1 才剛把兩處各寫一組收成一份)。`_kill_show` 又手寫 `("Cc","Cf","Zl","Zp")`,是第二份;日後共用集合補類別,這裡不會跟著動。屬「引入第二種做法」。
2. 兩份已出現實際分歧:共用集合含 Cs(無損解碼的替身字元),`_kill_show` 不含。重現:`m._kill_show("a\udcffb")` 回 `'"a\udcffb"'`,`print` 它拋 `UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff'`,而 `m._path_special_chars("\udcff")` 為 True。配方欄位若經設定檔路徑或非 UTF-8 檔名帶入替身字元,提醒行會在 kill-add / doctor P2 印出時當掉(doctor 外層有兜底,kill-add 的 `_kill_add_warn` 有 `except Exception` 也接住,所以後果是提醒被吞,不是崩潰;能否真從配方欄位進來我未能重現,故不升 blocker)。
3. 建議:類別判斷改走 `_path_special_chars(c, surrogate=…)` 或直接以 `_PATH_SPECIAL_CATS` 取代手寫 tuple;替身字元沿用 `_nodehome_show` 先換成替代字元(專案印路徑的既有做法)。
4. 次要(不獨立列等級):函式內 `import unicodedata`、`unicodedata.normalize("NFC", …)` 共 5 處(`_kill_alias`、`_kill_pathspec`),專案已有模組層 `import unicodedata`(`scripts/lumos:62`)與 `nfc()`(`scripts/lumos:387`);`_kill_alias` 還有 `casefold` 比對,跟 `_nfc_child`(`scripts/lumos:391`,同樣「磁碟 NFD / git NFC 對名」問題)是兩套寫法,但後者不處理大小寫,語意不同,不算第二種做法。

## 已核對、與專案一致(不列 finding)
- git 子程序加 `timeout=`:專案同樣用「模組常數 + `capture_output/text/errors`」(`scripts/lumos:300`、`4951` `_git_is_shallow(timeout=…)`、`38857` `_disp_git_timeout`),`_KILL_GIT_TIMEOUT` 寫法一致;捕捉 `(OSError, subprocess.SubprocessError)` 涵蓋 TimeoutExpired,沒有跨層直呼。
- doctor Check T 包 `try/except Exception as _te`:與其他段的「體檢某段壞了不讓整支中斷」寫法一致(`scripts/lumos:1308`、`2322`、`2635`);P2 兜底改 `warn_soft([], …)` 與 `scripts/lumos:2635` 註解「標題寫不擋就只准 warn_soft」同方向。
- `_kill_pathspec` 的 NFC 只在 darwin 套用,有註明依據(git 的 precomposeunicode),不是重複造輪子。

最高等級:minor
