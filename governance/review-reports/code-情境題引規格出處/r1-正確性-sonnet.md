severity: major

## c1 人裁指令的壞法檢查,沒擋「--old 不含該列觸發字」,測試照綠
severity: major
blocking: 是
引句:「if not hit[0] or not hit[1] or hit[0] == hit[1]:」
file: `scripts/lumos:75300`(`_situation_rule_recipe_problem` 的最後一道,patch 內文在 r1-code.patch 約 1299–1303 行)
1. 輸入:`--seg <第一段> --row D-5 --old "class Vm(private val q: Flow<String>) {" --new "class Vm(private val q: Flow<String>) { val z = q.flatMapConcat { search(it) }"`。這個 `--old` 在檔內恰好一次、落在段內,但不含任何觸發字。
2. 原碼走到 `hit[0]` 為空集合,回拒絕,符合 S9 和預期值表的「新舊兩邊要是同一列不同的觸發字」。
3. 把 `not hit[0] or` 拿掉(變異):`hit[0]=∅ ≠ hit[1]`,這個輸入被放行,進到殺傷力驗證。「機器保證是在同一列的寫法之間換」這個保證就失效了。
4. 重現:在 clone 裡把 `if not hit[0] or not hit[1] or hit[0] == hit[1]:` 改成 `if not hit[1] or hit[0] == hit[1]:`,跑 `python3.14 scripts/test_lumos.py -k situation_rule_recipe_scope`,輸出 `5 passed, 0 failed`。
5. 原因:`t_situation_rule_recipe_scope` 的 5 個案例裡,沒有「--old 無觸發字、--new 有觸發字」這一種。案例③只測了 `--new` 無觸發字。

## c2 人裁指令只測了「落在段後面」,沒測「落在段前面」,拿掉 `a < start` 測試照綠
severity: major
blocking: 是
引句:「if a < sg["start"] or b > sg["end"]:」
file: `scripts/lumos:75293`(`_situation_rule_recipe_problem`)
1. 輸入:`--seg <第二段,起訖 22–26> --row D-5 --old "flatMapLatest { search(it) }"(第 4 行,屬第一段)--new "flatMapConcat { search(it) }"`。
2. 原碼走到 `a=4 < start=22`,拒絕:「不在這一段的起訖行裡」。
3. 把條件改成只剩 `b > sg["end"]`(變異):`b=4 ≤ 26`,放行。那就等於人裁可以拿第一段的壞法去替第二段背書,也就是 S9 預期值表第一列「同檔另一處不在這段起訖行」。
4. 重現:把該行改成 `if b > sg["end"]:`,跑 `-k situation_rule_recipe_scope`,輸出 `5 passed, 0 failed`。
5. 原因:案例①只用第一段(start=1)配上第二段的 `--old`,只走到 `b > end` 這一半。`a < start` 那一半沒有任何案例。

## c3 「讀不懂的 written_at 當新制」沒有測試守著
severity: minor
blocking: 否
引句:「日期讀不懂也當新制(寧可多要求出處,不無聲退回舊制)」
file: `scripts/lumos:73778`
1. 變異:把 `return not _DAY_RE.fullmatch(day) or day >= _kt_sit_spec_since()` 改成 `return bool(_DAY_RE.fullmatch(day)) and day >= _kt_sit_spec_since()`。壞掉的 `written_at`(例如 `"garbage"`)就會靜默退回舊制,出處擋整個失效。
2. 重現:改完跑 `-k kt_sit_spec_since`,輸出 `10 passed, 0 failed`。`t_kt_sit_spec_since` 的案例只有「缺」和「日期正常」,沒有「寫了但讀不懂」。
3. 這條是 fail-closed 路徑上的實作承諾,不在驗收條款裡,所以只算 minor。

## c4 有 `[S0]` 的計劃:清單會列出 S0,但 S0 不能被引
severity: minor
blocking: 否
引句:「if not left.startswith("Projects/") or len(left) <= len("Projects/") or not re.fullmatch(r"S[1-9][0-9]*", right):」
file: `scripts/lumos:73448`(`_kt_sit_spec_parse`)
1. 輸入:計劃〈驗收條款〉節有 `- [S0] 當甲,系統 應 乙 [test:t_a]`。
2. `_kt_sit_plan_clauses` 回 `{'S0': …}`(我實跑確認)。`_kt_sit_spec_listing` 和樣板的 `spec_plans` 都會印出 S0。
3. 作者照清單寫 `Projects/甲#S0`,`_kt_sit_spec_parse` 因 `[1-9]` 回 None,形狀檢查回「n 不帶前導 0」。清單教你可以引,收件卻不收。
4. 規格〈用詞〉只禁前導 0,S0 不是前導 0。解法是 parse 正則和清單用同一個規則:要嘛兩邊都收 S0,要嘛清單濾掉 S0。

## c5 答不適用的列填了出處,在整題沒有任何「適用」列時完全不核對
severity: minor
blocking: 否
引句:「答不適用的列一樣驗(填了照樣核對)。」
file: `scripts/lumos:74634`(`_kt_sit_verdict_one`)、`scripts/lumos:73915`(`_kt_sit_row_verdict`)
1. 輸入:兩列都答 `applies:false`,D-3 填 `spec:"Projects/結帳_計劃#S9"` 加合格形狀的 quote。
2. `_kt_sit_has_applies` 為 False,`specs` 維持 None。`_kt_sit_row_verdict` 的 `spx = … if (spec_rules and specs is not None) else None` 讓內容核對整個跳過。
3. 規格〈範圍〉1 的「填了照樣核對」只在至少有一列適用時成立。`t_kt_sit_spec_verify` ⑧用的就是有 D-1 適用的案例,測不到這個缺口。
4. 影響小,因為不適用的列本來就不需要出處。但不適用列的「填了照樣核對」沒有一致的行為。

## c6 治理帳的 recipe_id 跟殺傷力帳本的 recipe_id 對不上
severity: minor
blocking: 否
引句:「"consent": consent, "kill_verdict": r0["verdict"], "recipe_id": _kill_recipe_key(prel, cid, nfc(file), old)}」
file: `scripts/lumos:27945`(guard kill 蓋章用 `res.get("file")`)
1. 輸入:平台根是 repo 的子目錄(例如 `android/`),`--file android/app/src/Vm.kt`。
2. 殺傷力帳本的 recipe_id 是 `_kill_recipe_key(prel, cid0, "app/src/Vm.kt", old)`,檔路徑是相對平台根的 `kfile`。
3. 治理帳的是 `_kill_recipe_key(prel, cid, "android/app/src/Vm.kt", old)`,檔路徑是 repo 相對路徑,而且 `cid` 是鎖內重算的。兩邊雜湊不同,「配方身分」沒辦法拿來把人裁事件連到殺傷力證據。
4. 本案目標是 Android 專案,平台根常常是子目錄。沒有人讀這個欄位,所以影響小。

## c7 寫了計劃、帳還沒記就被中斷時,重跑會多寫一條重複條款
severity: minor
blocking: 否
引句:「計劃已寫入 {cid},治理帳沒記到——不要重跑(重跑會多寫一條重複條款)」
file: `scripts/lumos:75673`(`cmd_situation_rule`)
1. 這段只教了「`_gate_event` 回非 True」這一種失敗。`_situation_rule_write` 成功後、`_gate_event` 完成前如果按 Ctrl-C 或丟例外,不會進這段處理。
2. 結果是 traceback,沒有救法。計劃裡已經有 S(n),治理帳沒有。規格閘會把 S(n) 當新行為要求測試紅。
3. 再跑一次(同 clause、同 test),`_situation_rule_insert` 不檢查「已有同文同測試的條款」,會寫出 S(n+1)。
4. 這個窗口很小,但這正是「寫一半被中斷」要問的情形。最小防護:寫入前偵測同文同測試的既有條款,有就回報而不重插。

## c8 CRLF 計劃被靜默整份改成 LF,`nl` 判斷是死碼
severity: minor
blocking: 否
引句:「換行沿用原檔(有 \\r\\n 就用 \\r\\n)。」
file: `scripts/lumos:75377`(`cmd_situation_rule` 用 `ppath.read_text(encoding="utf-8")`)
1. `read_text` 預設做 universal newline,`\r\n` 在讀進來時就變成 `\n`,所以 `_situation_rule_insert` 裡的 `"\r\n" in text` 永遠是 False。
2. 我實跑:CRLF 的計劃經過 `_situation_rule_insert` 加 `_situation_rule_write` 之後,位元組裡 `\r\n` 從 9 個變 0 個,每一行都變了,diff 整份改寫。
3. 本 vault 慣例是 LF(`load_raw_for_edit` 對 CRLF 是「拒絕、不靜默正規化」)。這裡反而靜默正規化。要嘛用 `newline=""` 讀,要嘛跟 `load_raw_for_edit` 一樣拒絕。

## c9 〈用詞〉要求排除「重複定義」的條款,沒有任何測試
severity: minor
blocking: 否
引句:「if r.get("defined") and r.get("state") != "duplicate" and r["line"] in in_sec and 0 < r["line"] <= len(lines):」
file: `scripts/lumos:74013`(`_kt_sit_plan_clauses`)
1. 輸入:節內有兩行 `[S1]`。實跑 `clause_bindings` 把 S1 標成 `duplicate`,`_kt_sit_plan_clauses` 把 S1 整個排除(行為是對的)。
2. 整份測試 patch 裡只有一處提到 `duplicate`,在 S11 的新條款斷言,跟出處無關。把 `state != "duplicate"` 拿掉,出處測試照綠,重複編號的條款就可以被引。
3. 只算覆蓋缺口,所以 minor。

## 附:manifest 與圖譜鏡頭
manifest 的 2 條(`pitfalls-builtin`,「檔案 handle 有沒有 with/確定 close」),都判誤報。
- 第 75400 行:`_tty_reachable` 的 `os.open(...)`,下一行 `os.close(fd)`,沒有任何會跳過 close 的路徑。
- 第 75466 行:`_situation_rule_write` 的 `os.open(... O_EXCL)`,馬上交給 `with os.fdopen(fd,"wb")`。外層 `except BaseException` 會 unlink 暫存檔,fd 不會漏。

圖譜固定席:這次派工附的是「鏡頭計算超時」備援段,沒有固定席節點可逐條判。以下是我看到的、可能牽到合約的範圍:
- 規格閘(`_spec_gate_ruled_ids`、`_expected_requirement`):帳讀不到或沒事件時回空集合,只會更嚴,沒有放寬規格閘。
- 殺傷力 guard-kill(`recipes_override`、`source` 欄、`_kill_run` 的 Ctrl-C):不傳 override 的呼叫端行為不變。我跑過 `-k kt_sit_spec`,63 個通過。
- 治理帳閘名單(`_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、`_GOV_FIELD_TYPES`):新增的 `situation-rule` 三處都有登記。

我另外做了 9 組變異,對應的測試都紅,守得住的有:盲判捷徑只認第一盲判、捷徑忽略段放行、出處不同改成只比計劃、人裁編號只看節內最大號。`t_spec_gate_ruled_clause_as_keeps` 裡「雜湊對不上就照一般條款」我沒另外變異,只讀過測試內容。

清理:我在 `/tmp/lumos-seat-work/code-情境題引規格出處/正確性-sonnet/` 底下的 clone、變異副本和腳本已刪掉,留下的紅燈現場 `gctl-run-*` 4 個也已刪。其間複製 clone 曾把磁碟寫滿,現已騰出約 19GB。

最嚴重 severity 是 major,blocking 共 2 條(c1、c2)。
