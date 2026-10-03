severity: major

U1、U2 為 major 且 blocking(皆有翻紅重現),U3 為 minor。

**U1 「SEE 只放連結」一樣是整行規則,舊 SEE 句尾補括號仍把新寫的沒來源現況句放過去**
severity: major
blocking: 是 — 跟 r1 修掉的「現況描述沒寫來源」同一種偷渡,同族只修了一條;可翻紅
引句:「if k == ("現況描述沒寫來源",):」
- 輸入:起點版本有一行舊的違規 SEE 句,例如 `SEE: 付款走舊閘道的說明 [[Systems/Pay]]`。這次只在句尾補 `(實際上生產環境用 Redis 做快取三台機器)`,括號裡沒有來源。
- 路徑:`_ns_check_line` 在 `m.group(1) == "SEE"` 且有句子時,只報 `SEE 只放連結`,走不到 `現況描述沒寫來源` 那條。`_ns_viol_key` 對 SEE 回傳 `("SEE 只放連結",)`。舊行本來就有這個違規,所以 `_ns_append_subtract` 在 `scripts/lumos:27692` 之後的計數扣減把它扣掉,整行放行。
- 預期:跟「新寫一行同樣內容」一樣被擋。實際:rc 0。
- 重現:在 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/tmp.V84m0el5Rr` 的複本跑 `python3.14 scripts/test_lumos.py -k probe_see`。同一句當新行加進去是 `SEE baseline-new rc 1`,補在舊 SEE 句尾是 `SEE rc 0`。
- 其他整行規則沒有這個洞:`程式行號引用` 和 `釘版本不合法` 用片段當鍵;回頭條件三條用改法當鍵。同族裡只有 SEE 留下。
- 修法二選一:`_ns_append_subtract` 對 `SEE 只放連結` 也不扣;或把「整行層級、括號新增內容會變」的規則名收成一個常數(例如 `_NS_NEVER_CUT_RULES`),不要再用單點的 `== (...)` 比對。
- 補充:舊句已帶 `[來源:部署]` 時,括號裡的新現況句不用自帶來源(`sourced rc 0`),因為這條是整行判的。這跟使用者裁定的「沒來源的舊句,括號要自己帶來源」不衝突,只是不對稱,第二層仍會判尾巴,所以不另列。

**U2 候選篇數或對數超過上限時完全靜默,擋下訊息的提示對清舊筆記的人做不到**
severity: major
blocking: 是 — 清一批舊筆記的人照提示做仍被擋,而且看不出原因;可翻紅
引句:「# 沒有候選,或總量超過上限(偏嚴,不算失敗)」
- 輸入:一次推送範圍內有超過 `_NS_APPEND_MAX_FILES`(200)篇筆記,每篇都只在舊句尾補合格括號。注意範圍是整次推送的 `base..tip`,所以拆成多個提交沒用。
- 路徑:`_notelines_append_pairs` 在 `len(cands) > _NS_APPEND_MAX_FILES` 或總對數超過 20000 時 `return {}, None`。`error=None`,所以:
  - 沒有「配對這次沒跑成」提示(`_note_audit_mark_appended` 只在 `pairs.failed` 時印);
  - 放寬帳沒有 `git-failed` 或 `error` 紀錄;
  - 擋下訊息仍只說「舊句一個字不動、只在句尾補括號就只查補上的那段」。
- 預期:使用者知道是批量上限,或至少帳上有紀錄。實際:每篇照做都被整行擋,舊行的違規全部浮出來,無從得知原因。
- 重現:複本裡把 `_NS_APPEND_MAX_FILES` 改成 1,`-k probe_cap` 兩篇各補合格括號 → rc 1,輸出沒有任何上限說明。comment 說「偏嚴」是對的,但這是唯一一條沒有訊息的偏嚴路徑。
- 規模:計劃自己寫過消費專案實測 193 處補括號,離 200 很近。
- 修法:超限時回傳 `error="cap"`,讓「配對沒跑成」提醒、放寬帳 `state:error` 和擋下訊息的提示都帶出「這次範圍候選篇數超過 N,請分批推送」。

**U3 同一次推送去重只擋完全相同的 (起點, 終點, 配對),重疊的分支範圍仍重記**
severity: minor
blocking: 否 — 只多一筆放寬帳,不影響判定
引句:「key = hashlib.sha256(f"{att}\0{base_where}\0{tip_where}\0{sorted(map(tuple, pairs))}".encode()).hexdigest()[:16]」
- 輸入:一次推兩條分支,頂端不同但共用提交,掛鉤逐分支呼叫。
- 路徑:`base_where` 或 `tip_where` 不同,所以 key 不同,兩筆都記,`pairs` 重疊的部分被重複計入。
- 預期:`_ns_relaxed_seen` docstring 寫「範圍重疊會重記」是 r1 要修的問題。實際:只修到「同一個範圍被呼叫兩次」。這項我沒有實機重現,是讀程式推出的。
- 若放寬帳要當計數用,key 要改成以 (路徑, 行號, 舊行雜湊) 的集合去重,不看範圍端點。

**檢查過、未發現問題的部分**
- **使用者裁定「括號要自帶來源」**:清舊筆記那邊,舊句沒來源、括號帶 `[來源:…]`,整行不再違規,rc 0。括號沒帶來源則被擋,訊息裡有提示,提示照做得到。偷渡那邊,括號帶假來源和沒來源兩種,都跟新寫一行的行為一致。範本、訊息、doctor 的措辭沒有誤導的地方。
- **`_gate_event_fit`**:二分法與舊的逐筆丟行為一致,`_drift_m1_fit` 的 `nodes_cap=20` 也等價。
- **`_ns_deleted_summary_lines`**:改走共用的區塊讀法後,被刪檔、含 `-- x` 內容的被刪行都能正確讀到。
- **範本**:`scripts/templates/note-audit-judge.md` 新段的 CODE 定義與前面一致,規則 6 對整筆項目仍有效;`t_note_audit_judge_template_pinned` 在 repo 內通過。
- **`_note_audit_dispute_map` 不分範圍**:內容編號含 路徑、區域、標題、整行文字,同一篇裡要同編號同時有整行與尾巴兩種項目才會互相影響,幾乎做不出來,不列。

**固定席節點**:這份 diff 只動 `scripts/lumos`、`scripts/templates/note-audit-judge.md` 和一份說明文件。
- `lumos-cli-read` 的 search 排除 superseded 合約、`guard-kill` 的兩條 rc 與 JSON 合約:程式路徑沒碰,不影響。
- `bound-tests-gate`:沒動 code-loop check 路徑,不影響。
- `授權與歸屬`:`scripts/lumos` 檔頭與範本的 SPDX 行沒動,不影響。
- `測試假綠形態`、`design-loop`:diff 沒含它們管的測試或處置閘,不影響。我沒看到本輪測試檔改動,所以還原翻紅釘合不合格無法判斷。
- `reversibility-governance-ledger`、`pitfalls-code-loop`:只列名沒有內容,不答。

最高嚴重度 major,blocking 2 條
