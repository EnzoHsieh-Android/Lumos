severity: minor

## F1 設定讀不懂的警告字面跟同批鄰居不一致
severity: minor
blocking: 否
引句:「cfg["warnings"].append(f"{p} 讀不懂({type(e).__name__}),fix_check 照預設")」
佐證行(鄰居寫法):file: `scripts/lumos:24214`(_lint_new_config:`.lumos/config.json 讀不了(類名),新增告警閘用預設值`)、file: `scripts/lumos:23258`(stack_questions)、file: `scripts/lumos:5791`、file: `scripts/lumos:25318`、file: `scripts/lumos:27270`、file: `scripts/lumos:27330`
1. 專案裡讀 `.lumos/config.json` 失敗的警告共 8 處以上,全是「`.lumos/config.json 讀不了(<例外類名>),<功能名> 用預設…`」:動詞「讀不了」、路徑寫固定相對字面。本 patch 改成「讀不懂」加 `{p}`(絕對路徑,依呼叫端可能含使用者家目錄),動詞與路徑寫法兩處都跟鄰居不同。結構(單欄位壞用預設並警告、回 warnings 清單)與 `_lint_new_config` 一致,所以只是字面不齊,不是第二種做法。
2. 附帶:`_fix_check_config` 例外集合是 (OSError, ValueError, RecursionError),鄰居是 `except Exception`。本專案 `RecursionError` 的專門處理另有大量先例(file: `scripts/lumos:22995`、file: `scripts/lumos:38158`),收窄不算錯,不另列。

## 三問
1. 分層與依賴方向:`_fix_load_record` 的逐字串檢查留在同一函式、只用標準庫,沒有往上呼叫別層。對得上。佐證:file: `scripts/lumos:11690`(原函式同一個 except 層)。
2. 命名與錯誤處理:孤立代理字元用 `x.encode("utf-8")` 捕 `UnicodeEncodeError`,跟 file: `scripts/lumos:25683`(`p.encode("utf-8")` 加 `except UnicodeEncodeError`)同一寫法;回 (None, 錯誤字串) 跟同函式其他回傳一致。唯一差異是 F1。
3. 第二種做法:專案沒有既有的「遞迴走訪 JSON 逐字串」函式(grep `stack.pop` / `_walk` 只有無關的路徑與縮排處理),所以明確的 stack 走訪是第一種做法,不算第二種。共用謂詞 file: `scripts/lumos:29130`(`_path_special_chars`)涵蓋 Cs,但同時涵蓋 Cc(換行、tab),拿來擋修正紀錄的 note 會誤擋合法多行文字,語意不同,不應強沿用;NUL 單獨判跟 `_FIX_ID_BAD_RE`(file: `scripts/lumos:11589`)的範圍相容。判「沒有第二種做法」。
4. 另外 `linked` 改用 `.is_symlink()` 看樹裡實際連結:跟 `_lint_link_deps` 的建連結行為對得上,屬於同函式內修正,不涉及架構。

不對齊共 1 條,其中 major 0 條。
最高等級:minor,blocking 共 0 條
