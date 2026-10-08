severity: minor

# 第 3 輪 正確性鏡頭報告(sonnet)

範圍:/tmp/code-revB-r3.patch(第 2 輪修正)。我在 rw clone 裡載入 scripts/lumos 實跑,並跑了 `python3.14 scripts/test_lumos.py -k when_gone`(45 passed, 0 failed)。blocking 級的重點(方括號擋法、反引號檢查、讀不出與超過上限分開講、_drift_specs)都逐項構造輸入走過,沒找到 blocker 或 major;只找到一條 minor。

**C1 反引號檢查用「前面反引號個數的奇偶」判斷是不是行內程式碼,雙反引號包起來的範例會被誤擋**
severity: minor
blocking: 否 — 只會誤擋一種寫法、改寫就能過,不會讓壞條件過關
引句:「if end >= 0 and s.count("`", 0, m.start()) % 2 == 0 and "`" in s[m.end():end]:」

1. 輸入:一行回頭條件,後面的說明文字用雙反引號包住一段含反引號的範例,例如 ``REVISIT:[when-file:a.py][by:2099-01-01] 教 ``[when-gone:a::`b`]`` 寫法``(這正是要寫「字串不能含反引號」這條限制的說明時,最自然的雙反引號寫法)。
2. 路徑:`_ns_revisit_cond_viol` 呼叫 `_probe_gone_backtick_err(ln)` 看原文。標記前面有兩個反引號(雙反引號的開頭),個數是偶數,被當成「不在行內程式碼裡」;標記內有反引號,於是回報。
3. 對照:同一行經 `_strip_inline_markup` 已正確把 ``...`` 整段剝掉(輸出是「教  寫法」),共用解析器根本沒看到這個標記。奇偶判斷跟剝除器的配對規則不一致。
4. 實測(rw clone,python3.14 載入 scripts/lumos):`_probe_gone_backtick_err(該行)` 回「when-gone 的字串不能含反引號…」,`_ns_revisit_violations(該行,"body",True)` 回 `['條件寫錯']`,提交時會擋下一行手冊上合法的寫法。這跟第 2 輪要修的「說明文字裡提到寫法被誤擋」是同一類,只修了單反引號那一形狀。
5. 影響面窄(要同時有真條件、雙反引號範例、範例內含反引號),改成讓檢查跟 `_strip_inline_markup` 用同一套配對(例如對剝除後的結果比對,或只在標記位於行首條件區時才檢查)即可。

## 沒問題的項目

- 方括號擋法:`_probe_check_value` 對 file、symbol、test、gone 四種鍵的 `app/[id`、以及 `_slot_retire_err("when-gone:app/[id")`、`when-file:app/[id`、`when-file:x]` 都實測回「不能含方括號」。`_probe_bad_path` 只有這幾處呼叫(`_probe_value_err` 的 file、`_probe_gone_err`、`_probe_named_err`),repo 內現有筆記與程式碼用 grep 找不到帶方括號路徑的條件,新規則不會讓既有筆記突然變紅。測試 ① 把 `_probe_bad_path` 的方括號判斷拿掉會紅,有咬到。
- 撤除條件的反引號:`_slot_retire_err("when-gone:a.py::`t`")` 回同一句訊息,`when-gone:a.py::x` 回 None;原先 `_probe_gone_backtick_err` 對「when-gone:」開頭值的分支已移除,全 repo 只剩 `_ns_revisit_cond_viol` 一個呼叫端、傳的是原文,沒有人再傳裸值進去而悄悄放行。
- 單反引號的行內程式碼裡提到 `[when-gone:` 不再誤擋(實測 `... 寫 `[when-gone:a::`b`]`` 回 None);多個行內程式碼各提一次(`[when-gone:a.py]` 與 `[retire:when-gone:b.py::x]`)也回 None;真標記(行首、前有 `- ` 或 `KEY: ``a`` `)照擋。
- 讀不出與超過上限分開講:`_read_raw` 只對 capped 回 None 的那幾支再問一次大小;`_nodehome_cat_sizes` 回同順序、失敗回 None,`sizes or [None]*len(miss)` 處理了失敗;非 blob(子模組)問不到大小仍記 None;條件路徑不可能含換行(`_PROBE_TOKEN_RE` 排除 `\n`),不會讓 `_nodehome_cat_sizes` 的逐行對位錯位。測試 ④ 把修法改回去:大檔那條 `gone_why` 會變成「讀不出或超過…」,同時含「讀不出」而紅;`tr2` 那條也會因文字不等於「讀不出」而紅,前置斷言(`tr.one` 真的讀到大檔)成立。
- `_drift_specs` 抽出:`_drift_cat` 與 `_read_raw` 取得的規格與原寫法逐字相同(`oids.get(p) or f"{where}:{p}"`),純搬移。
- 工作目錄模式預算用完:測試 ③ 的 `_over` 序列(False, False, True)實際走到第二支檔前停下,`src/b.py` 不進 `_raw`。
- 新舊互讀:舊版工具讀到帶 `when-gone` 的新筆記會視為不認得的鍵(既有行為),本 diff 沒改這一點;本 diff 沒碰 `when-gone` 的存檔格式。
- 計劃宣稱對照:〈驗收條款〉S1 到 S5 本 diff 沒動,對應測試(t_drift_when_gone_evaluates、_push、_grammar、_retire)仍綠。S3 的列舉沒提方括號、新測試 `t_drift_when_gone_review_r2` 也沒掛在條款上,但〈天花板〉第 4 點已寫明方括號限制,條款沒有說錯的地方。

## 固定席節點

- Systems/bound-tests-gate.md、guard-kill.md、授權與歸屬.md、測試假綠形態.md、lumos-cli-read.md、lumos-cli-lifecycle.md、design-loop.md:本 diff 只動 `_probe_*`/`_drift_*`/`_slot_retire_err` 與對應測試,不碰它們綁的函式(測試綁定閘、guard kill 的 rc 優先序與 JSON、授權白名單、re-inject sentinel、search 的 superseded 濾網、處置閘第五步);新測試的前置斷言做法符合「測試假綠形態」那條合約(測試 ② 有「前提:真標記照擋」,④ 有 `tr.one` 先走到大檔路徑),判不影響。
- Systems/pitfalls-code-loop.md(★RISK★)與其餘只列名的節點:沒有可讀的內容宣稱,本 diff 沒有牽涉到它們管的路徑,判不影響。

最高 severity:minor
