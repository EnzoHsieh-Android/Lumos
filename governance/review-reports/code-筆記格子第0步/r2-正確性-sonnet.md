severity: minor

我逐 hunk 讀了這份 diff,並跑了 `-k slots`(48 過)、`-k tags_hints`(9 過)、`-k rule_lifecycle`(15 過)。我另外用 python3.14 直接呼叫 `context_marker_warnings`、`slot_check` 走了幾個輸入。沒有 blocker 或 major,下面有 3 條 minor。

**R2C1 SEE 的兩道判斷不一致:提交時的違規清單比 lint 鬆**
- 引句:「if m and m.group(1) == "SEE" and body and not _NS_POINTER_ONLY_RE.match(body):」
- 輸入:`SEE:見`,或 `SEE:、`(只有分隔字、沒有 `[[`)。
- `_NS_POINTER_ONLY_RE` 允許整串只有「見、→、、」這類分隔字,所以 note-shape 的 SEE 分支不產生違規,提交放行。
- `slot_check("SEE", …)` 另外要求 `"[[" in body`,同一行在 lint 會唸「SEE 只放 [[連結]]」。我實跑確認 `slot_check("SEE","見")` 回傳錯誤。
- 影響很小:沒有連結的 SEE 也帶不進現況句,繞不過來源檢查。但同一條 SEE 規則在 lint 與提交時判法不同,「只放連結」的單一判準沒有守住。
- 佐證:`scripts/lumos:3580`(`slot_check` 的 SEE 分支)、`scripts/lumos:26185`(`_NS_POINTER_ONLY_RE`)。
severity: minor
- blocking: 否 — 只多放過沒有連結的 SEE,放過的內容不含現況句。

**R2C2 `_ns_tag_hints_collected` 改變了「提醒沒跑完」時的輸出**
- 引句:「    if tags.get("seen"):\n        for w in warns:\n            print(f"提醒:{w}", file=sys.stderr)」
- 修前條件是 `if not fail and tags.get("seen")`:失敗時不印設定提醒。
- 修後 `fail = fail or tags.get("error")` 先算,但印設定提醒只看 `seen`,不看 `fail`。
- 輸入:`tags["error"]` 已被 `_ns_tag_hints_collect` 的 except 設成例外類別名,且 `seen>0`,設定提醒 `warns` 非空(例如 tag_hints 設成壞值)。
- 結果:修前只印「沒跑完」一句;修後先印設定提醒,再印「沒跑完」。
- 影響只是 stderr 多幾行。diff 沒有宣告這個行為變更,現有測試也沒有咬住這條。
- 佐證:`scripts/lumos:26583`。
severity: minor
- blocking: 否 — 只影響 stderr 文字,不影響判定與回傳碼。

**R2C3 S16 新增的 `check-s16` 治理帳沒有任何測試,而且每條過期 RULE 都記一筆**
- 引句:「gov_events.append({"gate": "check-s16", "kind": "warned", "hard": False, "nodes": [n.stem]})」
- 在 `scripts/test_lumos.py` 搜 `check-s16` 與 doctor S16 段都沒有命中。這輪改過的 `_rule_stale_keys` 在 doctor 的路徑、事件有沒有寫、`_KNOWN_GATES` 有沒有登記,都沒有測試釘住。
- 變異想一遍:把 `scripts/lumos:2528` 的 append 刪掉,或把 `_rule_stale_keys` 在 S16 裡的 `"until" in _sk` 判斷改反,沒有任何測試會紅。
- 同一節點若有多條過期 RULE,每次 `doctor --ci` 會記多筆同節點事件,而不是每節點一筆。
- 以目前這個 vault 估算,RULE 行只有 18 條(其中 6 條沒寫 confirmed),帳不會暴增。
- 這個事件會進「同一道閘對同一篇連續喊」的空轉清單,這點應是有意的。
- 佐證:`scripts/lumos:2528`、`scripts/lumos:7249`(已登記 `_KNOWN_GATES`)。
severity: minor
- blocking: 否 — 登記本身是對的,缺的是測試。

**其他鏡頭逐項判定:沒找到會出錯的輸入**
- **空骨架行不唸:** 我實跑 `RULE:`、`RULE:  ` 都不唸。`RULE:。` 與 `RULE: [since:2026-01-01]` 仍照舊唸缺鍵,所以只有純空白被跳過,標點與只有欄位的行不受影響。
- **新舊互讀:** 舊寫法的行仍走舊判準。`rule_lifecycle_warnings` 對 superseded 與非 active 的行,跟修前一致:`stale = … if st == "active" else []` 等價於原本兩處 `and st == "active"`。S16 本來就先濾掉 superseded,再由 `_rule_stale_keys` 判斷,語意相同。
- **日期:** `DATE_RE.match` 加 `_rule_date` 與舊的 `_slot_date` 在實務上等價。`DATE_RE` 的 `$` 理論上放過結尾換行,但摘要是逐行切的,值裡不會有換行。我實跑 `20261001` 仍被擋。
- **時間:** `commit_time=True` 用本機日期,容許 +1 天。台北凌晨 1 點寫當天日期,本機日期就是台北當天,不會被唸。寫 UTC 的前一天只是更早,不唸。寫後天(+2)才唸「晚於今天」,我實跑確認。
- **SEE 進違規清單:**
  - 它走既有的 gate 設定:off 不 eval,warn 只記 warned,單次跳過同其他規則。
  - 「新程式檔喚醒」那段對它不會誤觸發:片段不以 `` `路徑: `` 開頭,會被 `continue` 掉。
  - 現有測試把 `SEE:[[甲]]、[[乙|別名]]` 當成 `_plan_system_links` 的正向輸入,但那裡測的是連結解析器,不是 SEE 合法性,不衝突。
- **新補測試有沒有咬住:**
  - `t_rule_lifecycle_warns_at_commit` 的 ③ 會咬住 `_ns_rule_hints` 不走 `slot_check`,因為它斷言輸出裡有 `[since:]` 與 `[被取代:`。
  - `t_slots_see_prefix_and_links` 會咬住 SEE 分支。
  - `t_slots_field_parser` 新增的逐項值判斷,各自對應一個判斷:條件式、列舉、散文撤除、三選一、recheck、作廢、度量閘。
  - 範本鍵白名單那條因為先減 `被取代` 再加回,等於沒減;不影響正確性,只是多餘的運算。

**固定席(圖譜)**
- 這份 diff 動到的是 `Systems/筆記內容閘` 的 tag_hints 描述。新描述(舊寫法走生命週期檢查、新寫法走筆記格子,都只提醒;SEE 夾句子進違規清單擋)跟程式一致。
- tag_hints 的合約沒有被破壞:仍是自己的開關、容器、例外隔離與 hinted 帳,不改變 note-shape 判定,`t_note_tags_hints_isolated` 照綠。
- SEE 進違規清單是新增的擋點,頁面已寫進去。除了 R2C1 說的邊界,沒有看到它跟其他節點的宣稱衝突。

最高嚴重度 minor,blocking 0 條
