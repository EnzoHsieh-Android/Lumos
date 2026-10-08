severity: major

固定席說明:`Systems/棧別提問表態閘.md` 和 `Systems/pitfalls-code-loop.md` 兩篇我用 grep 查過,沒有 INVARIANT、IRREVERSIBLE、CHECKPOINT 或 RULE 行,也就沒有合約能被破壞。兩篇的 KEY 敘述我沒逐條讀。這份 spec 對「棧別提問表態閘」的影響是新增八題,並新增一個旗標讓這題不參與行數門檻和舊語意整組清單。下面第 4 條說的是這個旗標漏掉一個讀取點。

1. 「不寫快取」加上 `_lens_wait_or_warm`,同一範圍會連續回超時,最久持續 900 秒
severity: major
blocking: 是(掛鉤路徑上,這個功能在受影響的範圍內等於整段失效)
- 輸入:diff 模式,改動命中形狀,補選時剩餘秒數不足 1 秒而中止。Hook 帶 deadline 進來,所以走 `_lens_wait_or_warm`。
- 走到哪一段:
  1. 第一次呼叫搶到 `.warming` 鎖,派出背景行程。
  2. 背景行程算完但不寫快取。快取寫入和「只刪自己那把鎖」的清理都在同一個 `if not no_cache` 區塊裡,不寫就連鎖也不會刪。
  3. 前景輪詢一直等不到快取,最後回 `timed_out`,rc=5。
  4. 之後同一範圍的每次呼叫都因為鎖還在(`_LENS_LOCK_STALE_SEC=900`)而判定「已有人在算」,不重派,又空等到 deadline 才回超時。
  5. 背景行程已經結束,沒有人會再補算。
- 壞在哪:使用者看到「背景在算、再敲一次」,實際上最久 15 分鐘內都拿不到鏡頭文字。截斷若是慢磁碟或 impact 太慢造成的,重算也一樣會截斷。
- spec 只說「不寫快取」,沒有處理鎖和等待端。
- 引句:「因時間停止時印一行「外部碼表補選因時間上限中止」,而且這次結果不寫進快取。」
- file: `scripts/lumos:40091`(`_lens_wait_or_warm`)、`scripts/lumos:40049`(`_LENS_LOCK_STALE_SEC`)、`scripts/lumos:40380`(寫快取與清鎖區塊)
- 修法方向:截斷時背景行程也要刪鎖。或者寫一份帶「已截斷」標記的快取,讓等待端取得文字。

2. A 組的「名稱片段」防線形同虛設,spec 自己的不命中例子換個寫法就會命中
severity: major
blocking: 否(S6 會抓到,但規則本身要先收窄)
- spec 說名稱片段 code、status、result、resp、ret、err「可以是識別字的一部分」,而且比對不分大小寫。
- 誤傷輸入:
  - `if (zipCode != "10001")`:`zipCode` 含 code,命中。
  - `countryCode == "886"`、`currencyCode == "840"`:命中。
  - `return pin == "1234"`:`return` 含 `ret`,命中。
  - `if (error ...)`、`promoCode.equals("2024")`:命中。
- 另一種誤傷:A 組是用「只剝註解、保留字串」的版本比對。`log("status == \"0000\"")` 這種 log 字串會命中。spec 只排除註解和測試檔。
- 引句:「同一行出現名稱片段 code、status、result、resp、ret、err 之一(不分大小寫,可以是識別字的一部分,例如 `respCode`、`pnqrStatus`)。」
- file: `scripts/lumos:23552`(`_STACK_TRIGGERS` 一律 `re.I` 編譯)、`scripts/lumos:23871`(`_stack_norm_line(keep_strings=True)`)
- 建議:名稱片段改成要求識別字邊界或詞尾(例如 `[a-z]Code\b`),把 `ret` 拿掉或改成 `\bret[A-Z_]`。

3. D 組和 B 組漏掉常見寫法
severity: minor
blocking: 否
- 逐例走一遍:
  - D 組要求「3 到 6 位整數」,`resultCode == 0` 和 `ret != 0` 漏掉。「0 代表成功」正是最常見的碼約定,`respCode == "00"` 之類兩位字串碼也漏。
  - `res.code === 2000`、`resp.code == 2000`、`result.code == 2000`:D 組要求識別字本身以 resp/result/ret/err 開頭再接 code,中間有點號的屬性存取比不到。`res` 也不在前綴清單裡。
  - `status == 2000`、`response.code == 2000`:D 組刻意排除,所以也漏。
  - Kotlin 單行 `when (c) { "2000" -> ... }`:B 組只認行首的 `"2000" ->`,不命中。
- 會命中的例子:`if (code.equals("2000"))`(A,有 code)、Swift `case "2000":`(B)、`in ("0000","2000")`(C)、`errCode != 404`(D)。其中 `errCode != 404` 是公開周知的 HTTP 狀態碼,D 組的 HTTP 排除只擋 status 和 response 開頭,擋不到它。
- 引句:「D 整數:名稱以 code 結尾、前面帶 resp、result、ret、err 之一的識別字(例:`resultCode`、`resp_code`、`errCode`),跟沒有引號的 3 到 6 位整數比較。」
- 這是召回率問題,不會造成錯誤輸出。用的是整數碼的專案,第三項作者端那題會常常不亮。

4. 新題掛在「效能檢核」名下,而 spec 的同步點沒列 hook 和 pre-push 的文案
severity: minor
blocking: 否
- 走到哪一段:`scripts/hooks/claude/impact-hook.py` 在編輯時呼叫 `_stack_applicability({_sk: delta_text})`,用 `stack_questions_applicable` 渲染,標題固定寫「[X 效能檢核——這次改動觸發了這幾題…]」。`scripts/hooks/pre-push` 的 tag 提示也寫「效能檢核被觸發」。
- 壞在哪:`extcode` 命中時會用「效能檢核」的標題把一題非效能題印給作者。
- spec 的同步點列了圖譜、手冊和測試,沒有這兩支 hook。
- 引句:「`Systems/效能檢核目錄`(各棧題數那串數字;extcode 不是效能題,在目錄裡註明它住在題目表但不屬效能檢核)」
- file: `scripts/hooks/claude/impact-hook.py:676`、`scripts/hooks/pre-push:454`
- 另一處小的:`_dispositions_template` 的 auto-na 理由只印 `s["when"]`(`scripts/lumos:42015`),`extcode` 的 A、B、C 組在 `when_raw`,理由會只剩 D 組,內容不完整。
- 旗標的讀取點我逐一查過:`scripts/lumos:35945`、`38679`、`36068` 都由 `_STACK_PERF_QUESTIONS` 派生,在派生處過濾就能一次擋住。`_stack_key_for_file`(23628)只用 key 做成員判斷,不受影響。`over` 分支在 `_stack_applicability`(23898 附近)必須逐題判斷旗標,spec 有寫。

5. 「外部事實行都只從 base 版讀」的註解改寫在設計審模式下是錯的
severity: minor
blocking: 否
- 設計審模式走 `cmd_dispatch_lens_spec` 並傳入 `_read_wt`,也就是從工作樹讀節點全文。
- 第一項要求共用渲染函式「diff 與設計審兩種鏡頭都印」,所以設計審會從工作樹印出投稿者可寫的 `[來源:外部]` 行,每篇最多 10 行、每行 300 字。
- 現有合約行在設計審本來就是這樣讀,框也套得上,所以注入面不是新增。錯的是 spec 要改寫的消毒註解。
- 引句:「鏡頭程式碼開頭那段「自由文字零輸出」的消毒原則註解改寫成:合約行與帶外部來源標記的事實行兩種例外,都只從 base 版讀、都在注入框內。」
- file: `scripts/lumos:40564`(`_lens_render_listed(lines, listed, _read_wt, ...)`)
- 這一條會把後人帶歪,屬於文件正確性。

6. 「含改動裡數字碼的行排前面」沒定義數字碼怎麼取
severity: minor
blocking: 否 ⚠(實作細節空白,spec 沒給判準)
- 沒有答案的問題:
  - 數字碼從改動行的哪裡取?全行所有 3 到 6 位數字,還是只取命中形狀的那一個?
  - 命中形狀的行常同時有別的數字,例如 `if (code == "2000") timeout = 30000`。
  - 以子字串比對,`200` 會誤中事實行裡的 `2000`。
  - D 組的整數碼和 A、B、C 組的字串碼是否算同一個碼?
- 另一處:補選段接在 `_lens_render_listed` 之後,spec 沒說受不受 `max_lines=400` 約束。主段若已因超過 400 行而中止,補選段仍會附加,輸出超出上限。
- 引句:「diff 模式且改動行命中形狀時,先印含有這次改動行裡出現的那些數字碼的行,其餘照檔案順序補滿」
- 設計審模式沒有 diff,自然退回檔案順序,這部分沒問題。

總結:最嚴重的是第 1 條(不寫快取加上鎖不放,hook 路徑最久 15 分鐘連續超時);其次是第 2 條,A 組的名稱片段太寬,`zipCode`、`return` 都會誤觸發。其餘四條是召回漏洞、hook 文案、註解事實錯誤、排序規則沒定義。