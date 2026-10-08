severity: minor

**Q1 分層與依賴方向:對齊。**
- 新碼放在 `scripts/lumos` 裡 `_ns_tag_hints_*` 與「筆記格子的擋」之間(diff 約 31281 起),跟前綴提醒、否定現況句提醒在同一區。
- 呼叫鏈和鄰居一樣:`cmd_note_shape` 呼叫 `_ns_wording_prepare` 取得容器,`_note_shape_eval` 逐篇呼叫 `_ns_wording_collect`,結尾由 `_ns_wording_emit` 印出並記帳。對照 `_ns_tag_hints_prepare`、`_ns_tag_hints_collect` 在 `scripts/lumos:31203`、`scripts/lumos:31212`,以及 `cmd_note_shape` 現有的 `tags` 傳法。
- 開關解析共用 `_note_shape_mode_parse`(`scripts/lumos:31179`),doctor 那行 `_ns_wording_doctor_lines` 接在 `_note_shape_doctor_lines` 裡,位置和 `_ns_tag_hints_doctor_lines` 同層。
- 沒有跨層直呼。引號、行內遮罩、片段、數法都呼叫既有函式:`_ns_neg_quote_spans`(`scripts/lumos:30975`)、`_inline_blank`(`scripts/lumos:389`)、`_inline_hidden`、`_inline_visible_mask`、`_ns_negation_snippet`(`scripts/lumos:31052`)、`_NotelinesPairs`、`_drift_probe_is_py`(`scripts/lumos:35719`)、`_count_members`、`_count_enum`。
- 句尾補括號的「只看補上的那段」沿用 `_ns_negation_hints`(`scripts/lumos:31061`)的做法,配對表也是有命中才查。

**Q2 命名與錯誤處理:大致對齊,有一處結構差異。**
- 前綴 `_ns_wording_*`、常數 `_NS_WD_*`、容器 `{"items","error","seen"}` 加幾個額外鍵,都照鄰居。
- 錯誤處理一致:collect 丟例外就清空 items、記類別名、這次不再算(對照 `scripts/lumos:31212`);emit 整段包 try、只印一句、不改回傳碼;記帳用 `_gate_event_or_warn(... "hinted" ...)` 帶 `check`、`rules`、`lines`、`notes`,和 tag_hints 同形狀。
- 差異見 F1:鄰居是 collect、collected、emit 三步,wording 少了 `collected` 那一步。

**Q3 第二種做法:沒有 major。兩個被點名的地方分別判定如下。**
- **「只解析定義那一段」不算第二種做法。** 真正數成員的地方仍是 `_count_members` 與 `_count_enum`,沒有另寫一套數成員。縮小解析範圍的理由寫在 `_ns_wd_def_count` 的說明裡(整支 3 MB 約 1.8 秒、350 MB),而 `_count_eval` 的整支解析是 drift scan 的路徑,兩者用途不同。唯一重複的是「在語法樹裡挑出指派或類別」那三行,見 F2。
- **`_ns_wd_paren_groups` 查不到可對照的既有做法,標 ⚠ 交編排者。** `_ns_paren_groups_only`(`scripts/lumos:30493`)回傳的是「整串是不是只由括號群組成」的布林值,不吐位置區間,功能不同,不能直接換。但專案裡本來就有好幾份各自為政的括號掃描:`_drift_mask_settled`(`scripts/lumos:34985`)、`_DriftM1Clauses`、`_drift_m1_paren_span`(`scripts/lumos:38711`)。鄰居自己沒有統一的括號群函式,所以無從判它是不是第二種做法。

### F1 wording 沒有 `_collected` 這一步,提醒的設定警告改在 emit 裡印
severity: minor
blocking: 否 — 結構上仍是「eval 之後才印、不改判定」,只是步驟切法跟鄰居不同
引句:「def _ns_wording_emit(root, box, warns, fail):」
對照的佐證行 file: `scripts/lumos:31238`(`_ns_tag_hints_collected`)、`scripts/lumos:32910`(`_ns_negation_collected`)
- 兩個鄰居都先用 `*_collected(容器, warns, fail)` 回傳 `(items, fail)`,再交給 emit。設定警告在 collected 印、items 先排序。
- wording 把這些全塞進 emit:`box.get("seen")` 時印 warns,也在 emit 裡排序。
- 結果是 `cmd_note_shape` 的收尾對 wording 只有一行呼叫,和另外兩組提醒的兩行寫法不一樣。

### F2 在語法樹裡挑指派或類別的比對,是 `_count_eval` 迴圈的複本,而且認的形狀略有差異
severity: minor
blocking: 否 — 數成員仍共用 `_count_members` 與 `_count_enum`,只是「挑哪個語句」的判定另寫了一份
引句:「if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) and st.targets[0].id == name:」
對照的佐證行 file: `scripts/lumos:36658`(`_count_eval` 的 hits 迴圈)
- `_count_eval` 用 `any(isinstance(t, ast.Name) and t.id == name for t in st.targets)`,所以 `A = B = (...)` 會被數到。`_ns_wd_def_count` 要求恰好一個 target,同樣的句子它回 None。
- 同一個名稱,提醒不印、掛了標記後 drift scan 卻能數,兩邊會不一致。
- 可行的收斂:`_ns_wd_def_count` 已經把定義那一段切好,直接對那一段呼叫 `_count_eval(段落, name)` 就能保留效能理由,又不複製判定。
- 這段原本就只有單一語句,`_count_changed` 在這裡不會誤擋。

### F3 「獨立的數字」判定另寫了一套邊界規則
severity: minor
blocking: 否 — 只影響提醒的誤報與漏報
引句:「if raw.rstrip().endswith("第") or (m.group(1).isdigit() and prev.isascii() and (prev.isalnum() or prev in "_."))」
對照的佐證行 file: `scripts/lumos:36680`(`_count_rewrite`,正規式 `(?<![0-9A-Za-z_./:\-]){old}(?![0-9A-Za-z_./:\-])`)
- `_count_rewrite` 判定句子裡的數字不能緊貼英數字、底線、`.`、`/`、`:`、`-`,前後兩邊都看。
- `_ns_wd_numbers` 只看前一個字元,而且只擋英數字、`_`、`.`,少了 `/`、`:`、`-`。所以 `r1-3 種` 這類寫法,提醒會判成數量,掛標記時 `drift fix`(`_count_rewrite`)卻會判成不是獨立數字。
- 這兩處本來就要判同一件事:「這個數字是不是句子裡那個被 `[count:]` 管的數量」。可抽成共用的判定函式。
- 該規則帶著量詞單位,所以不能整段原樣複用 `_count_rewrite`。這條只標記出兩處判定不一致,不是要求合併。

總結:不對齊共 3 條,其中 major 0 條
