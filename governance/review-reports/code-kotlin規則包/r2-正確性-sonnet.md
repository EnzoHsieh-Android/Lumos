severity: major

正確性席(sonnet)第 2 輪:程式本身沒找到會做出錯行為的洞,但新加的檢查有三道改壞了測試照綠。
- 基線:`check.py --sg` 回「規則 207 條,問題 0 個」,`-k kotlin` 92 題全過。
- 方法:在工作樹逐一改壞 `check.py`,各跑一次 `-k kotlin`,跑完用 `cp` 還原備份,`git status` 乾淨。
- 暫存目錄 `/tmp/lumos-seat-work/code-kotlin規則包/正確性-sonnet` 已刪。

### F1 「info 只准放 rules-review/」的限制,測試抓不到
severity: major
blocking: 是
來源:修補引入
引句:「if r["severity"] not in _DIR_SEVERITY.get(r["dir"], ()):」
- 改壞一(最小重現):把 `_DIR_SEVERITY` 的 `"rules"` 改成 `("error", "warning", "info")`,`-k kotlin` 結果是 92 passed / 0 failed。
- 改壞二:把 `"rules-hints"` 改成 `("hint", "info")`,同樣 92 passed。
- 原因:舊測試 `t_kotlin_rulepack_messages_cite_catalog` 的 `kt-e`(info 放在 `rules/`)正是這道限制的唯一覆蓋,這輪被改成 `severity: "critical"`。現在 `kt-f` 只驗 hint 放錯目錄,沒有任何一筆驗「info 放在 rules/ 或 rules-hints/」。
- 後果:`rules/` 是會擋的那一級,info 規則混進去不會被抓到。
- 建議補兩筆:`{"severity": "info", "dir": "rules"}` 和 `{"severity": "info", "dir": "rules-hints"}`,都要報「只收」。

### F2 review-fp- 好例放行的範圍條件,測試抓不到
severity: major
blocking: 是
來源:修補引入
引句:「if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and review_ids and rule_id in review_ids:」
- 改壞一(最小重現):拿掉 `and review_ids and rule_id in review_ids`,讓任何規則命中 `review-fp-*` 檔都被放行,`-k kotlin` 是 92 passed。
- 改壞二:拿掉 `kind == "good"`,壞例目錄裡叫 `review-fp-*` 的檔命中也被吞掉,同樣 92 passed。
- 原因:測試只有「整段放行拿掉會紅」(改壞 A 紅了),沒有「放行只限語意覆核級規則、只限好例」的對照。
- 後果:`rules/` 的正式規則若在名叫 `review-fp-*` 的好例檔誤報,自我檢查不會報。
- 建議補兩筆:複本裡放一個 `review-fp-x.kt`,內容是 `rules/` 某規則的壞寫法,要報「好例誤報」。再放一個 `bad/<id>/review-fp-*.kt`,要算進壞例命中數。

### F3 「(無)」觸發字分支與掃描逾時是沒人驗的死程式
severity: minor
blocking: 否
來源:修補引入
引句:「if c[4].strip() in ("(無)", "(無)"):」
- 把這個分支改成 `if False:`,`-k kotlin` 92 passed,因為真型錄沒有任何 D 列用「(無)」。這道新規則沒有「改壞就紅」的驗證,也沒有真實用例。
- 全形與半形各一個的預期寫法,需要確認是不是各寫了一個。我用十六進位看過,原始碼裡兩個都是全形 U+7121,所以半形「(無)」其實進不來,與意圖不符。
- 同類:把 `scan` 和 `loaded_count` 的 `timeout=SCAN_TIMEOUT` 拿掉,同樣 92 passed。逾時變成回 None 的路徑沒有任何測試走過。
- 建議在 `t_kotlin_catalog_rows_wired` 的複本加一列 D,觸發字寫「(無)」,要不報錯。並用會睡過逾時的假 `sg` 驗 `scan` 回 None、`check` 報「跑不起來」。

### F4 好例路徑算錯目錄(測試腳手架小瑕疵)
severity: minor
blocking: 否
來源:修補引入
引句:「(bad_src.parent.parent.parent.parent.parent / "good" / fp_rid / "src" / "main" / "kotlin").mkdir(parents=True, exist_ok=True)」
- `bad_src` 往上五層是 `samples/bad`,接上 `/ "good"` 得到 `samples/bad/good/<id>/…`,不是 `samples/good/…`。
- 目前測試會過,是因為 `samples/good/<fp_rid>/src/main/kotlin` 本來就存在。
- 後果:複本裡多出一個空的 `samples/bad/good/…`。日後若該規則的好例目錄結構不同,寫檔那行會因目錄不存在而崩。
- 建議改成直接 `mkdir` 寫入那一行的 `parent`。

總結:這輪修補本身在邏輯上站得住,但新加的語意覆核級檢查(F1、F2)有三處改壞照綠,其中 F1 是修補時把原本唯一的覆蓋換掉造成的。
