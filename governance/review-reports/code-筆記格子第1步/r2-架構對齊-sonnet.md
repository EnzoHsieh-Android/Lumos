severity: minor

R1 的 4 條(A1 到 A4)在這批修正裡都已對齊,沒有新長出第二套做法。我讀了 diff 和 `rw` 裡的程式碼,沒有跑測試。

## R1 四條驗證

- **A1 圖譜選擇,已對齊。** `_ns_vault_rel`(`scripts/lumos:26788`)同時給 `cmd_note_shape`(`:27322`)和 `_ns_skip_slot_extra`(`:26839`)用,優先序是「工作目錄所在圖譜 > 第一個」。單次跳過路徑的 MERGE_HEAD 判斷是照鄰居逐處內聯寫的(`:25752`、`:27285`),跟既有做法一樣。跳過路徑自己再讀設定、再跑 eval,是它不經 `cmd_note_shape` 的必然結果,不算第二套。
- **A2 缺漏統計,已對齊。** `_ns_slot_extra`(`:27070`)改讀 `slot_check_keyed` 帶的格,不再用 regex 反推字樣。測試 `t_slots_ledger_fields` 釘了三選一(`test/repro/防回歸`)也會算進去。
- **A3 擋下尾句,已對齊。** `_note_shape_report`(`:27411` 附近)的收尾句現在只在 `mode == "block" and (viol or errs)` 時印。
- **A4 `check` 鍵,大致對齊。** 格子帳補了 `"check": "slots"`,跟 `:27389` 的 `negation`、`:26717` 的 `tag-hints` 同形。仍有一個小問題,見 R2A3。

## 三問

**① 分層與依賴方向:對齊。**
- `_ns_vault_rel` 抽成共用,是把兩處重複收成一處,方向正確。
- `pre2` 掛在 `_notelines_range_added`(`:26018` 起)同一趟逐提交抽取上,用 `mark2` 當開關,跟 `by_path2` 同層同形。`_carry` 兩者一併處理。
- 批次讀起點版本走既有的 `_nodehome_cat_blobs`(`:25189`),不另起 `git show`。失敗回 None 再 fail-open,跟 `:25142` 的呼叫端一樣。
- 治理帳仍走 `_gate_event_or_warn`,沒有跨層直呼。

**② 命名與錯誤處理:大致對齊,有 4 條小出入,都不是結構問題。**
- 提醒字樣沿用「提醒:…這次沒跑(…),不影響其他檢查」。
- 例外包裝沿用 `_ns_skip_slot_extra` 一貫的「任何一步失敗回 None」。

**③ 第二種做法:沒有 major。**
- **`slot_check` 與 `slot_check_keyed`:** 這是一支薄委派(`scripts/lumos:3595` 只做 `[msg for _keys, msg in slot_check_keyed(...)]`),判斷邏輯只有一份。`:3684`(lint)與 `:26687`(RULE 提醒)仍呼叫 `slot_check`,正好是只要字樣的呼叫端。這不是第二套,不列。
- **舊行比對:** 只放連結的行另開一條路,但仍在 `_ns_slot_key`/`_ns_old_keys`/`_ns_is_old` 這一組裡,沒有另寫一套比對。
- **兩道擋同一件事:** `_ns_slot_line_problems` 的「整行或第一個實體行對上都算舊行」是同一道判斷的兩個入口,不是兩道保護。

## 不對齊條目

**R2A1 路徑清控制字元,只做了格子這半邊,同函式的舊違規輸出沒清**
引句:「        out.append(f"  {_esc_clean(p, 200)}:{n}  {'; '.join(_esc_clean(m, 200) for _k, m in probs)}")」
- 對照:同一個 `_note_shape_report` 印舊違規的那行是 `print(f"  {p}:{n}  {rule} {frag}:{fix}")`(約 `:27404`),沒清。
- doctor 事後掃描也是一邊清、一邊不清:新的 `sv` 那行清了(`:27248`),下面 `shown = "; ".join(f"{p}:{n} {rule} {frag}" ...)` 沒清。
- 做法本身沒錯(`_esc_clean` 在 `:2300` 等處是慣例),但同一個輸出裡現在有兩種路徑寫法。
severity: minor
blocking: 否 — 只是輸出一致性,放行判定不受影響。

**R2A2 比對鍵靠元組長度分兩種形狀,字典裡又塞一個 `None` 鍵放另一類資料**
引句:「        out[k] = out.get(k, False) or _ns_superseded(ln)」
- 對照:`_ns_slot_key` 回 2 元組或 3 元組,`_ns_old_keys` 與 `_ns_is_old` 用 `len(k) == 3` 分流;`out[None] = ptr` 把連結集合塞進同一個字典。
- 既有的 `*_parse` 一族回的是固定欄位的 dict(`{mode, warns, bad_value}`)。這裡是同一個容器、同一個鍵空間裝兩種型別的資料。
- 結構上仍在一組函式內,沒擴散到別處,所以只列 minor。
severity: minor
blocking: 否 — 現有測試 ④ 釘住行為,沒有具體失敗場景。

**R2A3 擋下事件同時有舊規則違規與格子違規時,整筆帳被標成 `check: slots`** ⚠
引句:「    return {"check": "slots", "slots_lines": len(sviol), "slots_missing": miss}」
- 對照:`negation`(`:27389`)與 `tag-hints`(`:26717`)的 `check` 都只標在自己專屬的 `hinted` 事件上。
- 格子是跟 `blocked`/`warned` 共用同一筆帳,`kw` 只要 `sviol` 非空就帶 `check: slots`(`_note_shape_report` 約 `:27411`)。
- 因此一筆同時有形狀違規與格子缺漏的 `blocked`,會被標成 `slots`。`:7709` 的去重鍵含 `check`,這筆會跟只有形狀違規的 `blocked` 分開算。
- 我沒造出實際讀帳會算錯的場景,所以標 ⚠。
severity: minor
blocking: 否 — 只影響讀帳時怎麼分類,放行與擋下判定不變。

**R2A4 doctor 的 `--slots` 掛鉤提醒依 `ci` 分兩種做法,跟鄰居「每次都唸」不同**
引句:「        elif not ci and gate_mode != "off" and _NOTE_SHAPE_GOLIVE_MARK in txt and _SLOTS_GOLIVE_MARK not in txt:」
- 對照:`_note_shape_doctor_lines` 約 `:27170` 的註解寫「放在 ci 返回之前,推送前與 CI 路徑每次都唸」,`_ns_negation_doctor_lines` 與 `_ns_tag_hints_doctor_lines` 都不看 `ci`。
- 這次只有格子這行靠 `ci` 抑制,理由(開擋前每個專案都是這個狀態,每次唸是噪音)寫在註解裡,合理。但它是第一個做這種分流的子開關提醒。
- 同一個函式裡另有一處用寫死的字面 `"--slots" in txt`,而不是 `_SLOTS_GOLIVE_MARK`。這是刻意的:要找的是「帶了 `--slots` 但位置不對」,記號常數會匹配不到。這點沒問題。
severity: minor
blocking: 否 — 屬提醒字樣的分流方式,不影響放行。

不對齊共 4 條,其中 major 0 條

最高嚴重度 minor,blocking 0 條
