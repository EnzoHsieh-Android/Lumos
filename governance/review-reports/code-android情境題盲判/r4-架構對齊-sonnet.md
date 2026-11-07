severity: minor

**① 模組邊界**

結構對。三處改動都留在 `scripts/lumos` 原有的治理帳寫入層,沒有跨層直呼,也沒有新檔或新模組。補帳尾直接呼叫既有的帳尾判斷函式,不重寫判斷。

引句:「if _ledger_tail_needs_newline(path):」

對照 `scripts/lumos:1850`(`_gate_event`)和 `scripts/lumos:1982`(`_append_governance_log`),呼叫位置和用法都一致。

`_ledger_tail_needs_newline` 的 docstring 在 `scripts/lumos:1864` 也同步更新,列出新增的呼叫者。這是既有的漂移守衛做法,沒問題。

**② 命名與錯誤處理**

兩支寫入器接例外的寫法,大方向跟 `_gate_event` 一致,只有一處小偏差。`_codeloop_gov_log` 的 `except (OSError, UnicodeEncodeError)` 和 `scripts/lumos:1858` 同形。`_codeloop_gov_append` 也同形,但回傳值有偏差,記為 F1。

F1:`_codeloop_gov_append` 的回傳文字被改了。
severity: minor
blocking: 否
引句:「return False, f"治理帳寫不進去({e.__class__.__name__})"」
- 原本的 `return False, f"治理帳寫不進去({e})"` 會帶出 OSError 的 errno 和路徑。改後只剩例外類別名,「權限不足」「磁碟滿」這類細節不見了。
- 註解寫「同 _gate_event」,但 `_gate_event` 只回 bool(`scripts/lumos:1858-1859`),沒有可比的文字格式。
- 結構沒問題,只是對呼叫端的訊息資訊量變少。這個回傳文字有沒有外部契約,我判不準,建議編排者確認。

⚠ 另一處觀察不列為不對齊。`_codeloop_gov_log` 把補帳尾放在 `try` 裡面,`_gate_event` 放在 `try` 外面(`scripts/lumos:1849-1855`)。帳尾判斷函式自己吞 OSError,所以行為沒有差別。

手冊新條目的格式跟相鄰條目一致:

引句:「**換真相來源先盤點讀寫者**:修補要換掉某份資料的真相來源」

- 位置對照 `skills/lumos-code-loop/SKILL.md` 第 5 步內的兩條:前面的「修前先查世界」和後面的「補防護工具先找既有」。
- 格式也一樣:同樣縮排 3 格、粗體標題加全形冒號、句末括號附卷證路徑與來由。
- 插在同一步的粗體條目群裡,位置合理。

測試名稱 `t_codeloop_writers_add_missing_tail_newline` 沿用 `t_` 前綴,用 `check()` 和 `_load_lumos_inproc`。兩者在 `scripts/test_lumos.py:170` 和 `:239` 都存在。

**③ 第二種做法**

帳尾補換行沒有另寫一套判斷。

引句:「if _ledger_tail_needs_newline(path):   # 同 _codeloop_gov_append:帳尾沒換行先補」

- 兩支新接的寫入器都呼叫同一個既有函式,補法也跟 `_gate_event` 一樣:先組好 `line`,需要時前面加 `"\n"`,再一次寫出。這就是 `scripts/lumos:1849-1851` 的做法。
- 沒有發現新增的內嵌 `read_bytes[-1]` 之類的帳尾判斷。
- 純重複:`_codeloop_gov_log` 和 `_codeloop_gov_append` 兩支在同一帳上各自組行加補尾,原本就並存,這次是平行補齊。因為判斷都走共用函式,不算第二種做法。

筆記裡的 REVISIT 行把 pass/skip 退帳和表態的真相來源並存,記成日期綁定的回頭條件(2026-11-21),寫法合規。

不對齊共 1 條,其中會擋的 0 條
