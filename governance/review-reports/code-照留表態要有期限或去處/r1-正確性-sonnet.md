severity: major

## F1 scan 與 doctor 判「綁去處的照留還開著」那段完全沒有測試守住
severity: major
blocking: 是 判準:驗收條款 S4、S8 宣稱的「綁去處」分支,把 `_drift_note_state` 弄壞測試全綠,附能當場重現的變異。

file: `scripts/lumos` 的 `_drift_note_state`(diff 內新增,`cmd_drift_scan` 與 `_drift_dead_ack_rows` 都靠它)。

具體失敗場景:`_drift_note_state` 的內層 `_state` 改成永遠回 None(或前綴比對寫錯、type 與 status 對調),則 scan 與 doctor 把每一筆綁了去處的照留都判成「綁的 X 不在了或讀不出」而重列;已綁開著 Issue 的照留會天天被當失效。

引句:
引句:「        return _drift_str(n, "type"), _drift_str(n, "status")」

重現(在臨時目錄複製 scripts,只改那一行為 `return None`,清 __pycache__ 後跑):
- `python3.14 scripts/test_lumos.py -k drift_ack_routed` → 19 passed, 0 failed
- `-k drift_doctor_dead` → 2 passed, 0 failed
- `-k drift_check_born` → 4 passed, 0 failed
全綠。

原因:`t_drift_ack_routed_expiry` 的三種混雜裡,綁去處的那筆是 `tracked_in=…/Issues/不存在.md`(本來就該失效),活著的是 `until=future` 與舊表態;沒有任何一個測試讓 scan 或 doctor 看到「綁的 Issue 開著、因此已表態」,也沒有「綁的 Issue 收尾、因此重列」。`t_drift_ack_live_rules` 只測純函式,自己傳 `note_state`,測不到 `_drift_note_state` 的接線。S4 條文寫「一筆舊表態、一筆有期限、一筆綁去處的三種混雜」也因此沒被驗到。

引句:
引句:「tracked_dead = dict(rows[-1], until=None, tracked_in="docs/kg-knowledge/Issues/不存在.md")」

建議補:scan 一支綁開著 Issue 的照留 → acked;同一支把 Issue 改成 resolved 再 scan → 回要處理並印「已收尾」。

## F2 doctor 對多行的 RULE 撤除條件照留永遠不報失效
severity: minor
blocking: 否 判準:只影響 doctor 的提醒一行,drift scan 與推送路徑不受影響。

file: `scripts/lumos` 的 `_drift_dead_ack_rows`(diff 內新增)與 `_drift_ack_text`(`scripts/lumos:34628`)。

具體失敗場景:retire 的表態記的是「摘要條目接回續行的整條」(`_drift_ack_text` 對 retire 回 `_ns_summary_logical(text)[line]`)。RULE 的 `[retire:when-file:…]` 寫在續行時,記下的原文是接成一行的字串;`_drift_dead_ack_rows` 用 `text not in {ln.strip() for ln in 筆記按實體行切}` 判「那一行還在」,接起來的整條不等於任何一個實體行,於是被 `continue` 略過。已過期的 retire 照留在 doctor 永遠不出現,而計劃〈做法〉8 與 S8 都寫 probe/retire。

重現(唯讀,行程內載入 scripts/lumos):摘要 `  RULE:要人簽 [依據:人] [since:2026-09-01]` 加續行 `    [retire:when-file:src/new.py]`,`_drift_ack_text(txt, lines, 4, "retire") in {l.strip() for l in lines}` 回 False(logical 為 `RULE:要人簽 [依據:人] [since:2026-09-01] [retire:when-file:src/new.py]`)。單行寫完的 RULE 才會對上。

引句:
引句:「        if text not in {ln.strip() for ln in (env_text(env, rel) or "").split("\n")}:」

`t_drift_doctor_dead_acks` 只造 probe,所以沒抓到。修法:retire 改用 `_ns_summary_logical` 的值集合比對。

## F3 S7 的翻紅釘宣稱「old is None 也標 born_now → ③紅」,實際不紅
severity: minor
blocking: 否 判準:born_now 的標法只剩 `old is False` 這個寫法沒有測試釘住「沒有起點不標」,屬測試力度不足,不是現行行為錯。

file: `scripts/test_lumos.py` 的 `t_drift_check_routed_no_date`(diff 內新增)。

具體失敗場景:把 `"born_now": old is False,` 改成 `"born_now": old is not True,`(沒有起點的推送也被當新寫就已成立、裸照留被擋),跑
- `-k drift_check_routed_no_date` → 3 passed
- `-k drift_check_born` → 4 passed
都綠。③是手造 `{"born_now": False}` 的發現丟給 `_drift_split_acked`,根本沒走 `_drift_probe_check` 的標記;②走的是截到上線點(old 為 False),也不會踩到 None。計劃 S7 與測試 docstring 都說這個變異會紅,是假的。

引句:
引句:「翻紅釘:推送路徑套用期限 → ①紅;old is None 也標 born_now → ③紅。」

建議補一題:`_drift_probe_check(root, None, tip, …)`(沒有起點)新寫就成立的行,配裸照留,必須放行。

## 其餘走過、沒找到問題的路徑(不是 finding)
- `_drift_ack_live`:until 為 None、數字、全形數字(`２０２６-１０-１０`)、20261105、空字串都回失效原因不丟例外;期限當天有效(實跑確認)。
- `_drift_expiring_acked` / `_drift_bound_latest`:seq 為字串或缺值時 `_drift_ack_seq` 回 0,不丟例外;`_drift_retire_guarded` 的 try 因此不會因壞表態靜默放行。
- 推送路徑 `as_of=None` 不碰日期,與計劃宣稱一致;born_now 用 `old is False`,與 `_drift_probe_judge` 的「新寫(或改了條件)」分支同一來源(`_drift_probe_old` 回 True/False/None)。新筆記在起點沒有同名檔時 `old` 為 False,會收緊,合理。
- 新舊互讀:舊版忽略 until/tracked_in(放寬,計劃已寫);新版讀舊表態在推送時不是 born_now 就算已表態。
- `drift fix --keep`(kind c2)走 `_drift_ack_route` 時直接回空尾巴,行為不變。
- 已知上限(計劃天花板 4):新寫行的條件標記與同一篇起點已有的另一行相同時 `old` 為 True,不收緊,計劃已承認。
- 圖譜鏡頭:派工詞說這次沒有固定席節點(鏡頭計算超時),未逐條答。diff 內有改動 `Systems/存量漂移守衛` 加一條 WHY 與 `Projects/存量漂移防線_計劃` 的 [S3] 合約候選行補充,內容與程式實作一致,看不出破壞該節點既有合約。
- 角色卡:未附,略過。

總結:max severity major,blocking 1 條(F1);minor 2 條(F2、F3)。
