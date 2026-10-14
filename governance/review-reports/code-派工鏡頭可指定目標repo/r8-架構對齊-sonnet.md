severity: major

**範圍說明**:讀了修補差異全文,也對照了程式檔裡的 `slot_parse`、`parse_rule_fields`、`_pq_bad_char`、`_pq_blank`、`_esc_clean`、`_residual_claim_fp`、`_lens_spec_cap_lines`、`_lens_spec_code_cands`,以及 spec-gate-nondo 分支的 `_is_invisible`。

**finding 1**
severity: major
blocking: 是 — 專案已有切 `[鍵:值]` 欄位的共用讀法,`_arch_target_rule_show` 另手寫一套,等於引入第二種做法。
引句:「先從尾端剝掉 [鍵:值] 欄位(從後往前逐個比,不用帶 $ 的正規式,長字串不回溯)」
對照:`scripts/lumos:4500` 的 `slot_parse(rest)["core"]` 就是「去掉所有欄位後剩下的一句」,`scripts/lumos:34556` 與 `34699` 已拿它取核心句。`scripts/lumos:3942` 的 `parse_rule_fields` 註解寫明「不留第二套切欄位的規則」。同檔 `_arch_target_note_rules`(`scripts/lumos:45189`)已用 `parse_rule_fields` 讀同一批 RULE 行。
判定理由:同一條 RULE 行,同一支函式鏈的前半段走 `parse_rule_fields`,後半段(`_arch_target_rule_show` 加新增的 `_ARCH_TARGET_RULE_FIELD_RE`)自己用「結尾是 `]` 就往前找 `[`」的規則剝欄位。兩套的判準不同:
- `slot_parse` 只認白名單鍵,值內方括號成對才算,行內程式碼裡的方括號不算欄位。
- 新寫的那套認任何 `[x:y]` 形狀,只剝尾端。
- 結果是 `[[節點]]` 連結、行內程式碼、欄位後面還有字的 RULE,兩邊切法會分歧。
- 這是上一輪資安席講的那種「讀取用另一套規則」。
- 建議改用 `slot_parse(rest)["core"]`:`_arch_target_note_rules` 回傳前就在已有的 `rest` 上算好核心句,或在這裡用 `entry.partition(":")` 後再 `slot_parse`。長字串的效能由 `_slot_scan` 負責,用測試補一個大輸入的檢查。

**finding 2**
severity: minor
blocking: 否 — 在這條分支上只有一份判定,是合併後才會變兩份,而且註解已宣稱唯一;屬收斂時機問題。
引句:「名字出口、_lens_visible、名字是不是空的都用這支;掛鉤是獨立腳本,照同一份全表抄(全碼位比對測試盯著)。」
對照:spec-gate-nondo 分支 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:5042` 的 `_is_invisible`:
- 類別表 `_INVISIBLE_CATS` 是 Cc、Cf、Cn、Co、Cs、Mn、Me、Zl、Zp,再加 `_pq_is_default_ignorable` 與 `_PQ_BLANK_LOOKALIKES`。
- 它排除 tab、換行(`\t\n\r`)。
- 它的「分工」註解(約 5035 行)點名了 `_pq_bad_char`、`_pq_blank`、`_PATH_SPECIAL_CATS`、`_esc_clean`、`_residual_claim_fp`,但沒提 `_lens_hidden_char`,因為這條分支還沒合。

判定理由:
1. 本分支內分工清楚。
   - `_esc_clean`(有損換空格、故意不清零寬連字)、`_residual_claim_fp`(只剝 Cf/Cc,動了指紋全變)和 `_pq_blank`(判有沒有可見基底)是不同用途,沒被這支吃掉。
   - `_pq_bad_char` 與 `_lens_hidden_char` 的類別判斷是同一段:`cat in _PATH_SPECIAL_CATS or cat in ("Co","Cn")`(`scripts/lumos:7165` 附近與 `17272`)。這是同一個判斷寫了兩遍,但 `_pq_bad_char` 另有 DICP 位置規則,不必併。
2. 合併後會是三份「看不見」。
   - `_is_invisible`(比對時拿掉)和 `_lens_hidden_char`(輸出時跳脫)用的類別集合不同:前者多 Mn、Me,後者含全部 Cc(tab 也跳脫)。
   - 兩者共用的只有 DICP 全表與 `_PQ_BLANK_LOOKALIKES` 這兩個資料表,類別清單各抄一份。
   - 本分支改的 `_PQ_BLANK_LOOKALIKES` 註解寫「★「看不見」全 repo 只有這份清單加 DICP 表★」,合併後就不成立。
3. 建議分工:
   - 抽一支共用底層,例如 `_hidden_base(c)`,內容是 Cc、Cf、Cn、Co、Cs、Zl、Zp 加 DICP 加 blank lookalikes。
   - `_lens_hidden_char` 直接等於 `_hidden_base`(輸出跳脫要全部跳)。
   - `_is_invisible` 等於「`_hidden_base` 但放過 `\t\n\r`,再加 Mn、Me」(比對要拿掉組合記號)。
   - 兩邊的差異各只剩一行,在註解寫明。
   - 後合併的那條分支負責收斂,並把 `_lens_hidden_char` 補進 `_is_invisible` 的分工註解。
   - 否則先合併的分支現在就把「唯一」兩個字改掉。

**finding 3**
severity: minor
blocking: 否 — 只是留下沒人用的參數,不是第二套做法。
引句:「    cats = _PATH_SPECIAL_CATS | frozenset(extra_cats)」
對照:`scripts/lumos:17275` 的 `_kill_esc`。
判定理由:這輪把名字出口的類別擴充改走 `hidden=True`,全檔搜尋已找不到任何呼叫端傳 `extra_cats`,但參數和說明段落還留著。`_kill_esc` 現在有 `extra_cats`、`extra_chars`、`wide`、`hidden` 四個旋鈕,而 `hidden` 已涵蓋 `extra_cats` 原本負責的 Co 與 Cn。建議移除 `extra_cats`,或在說明裡標明留存理由。

**finding 4**
severity: minor
blocking: 否 — 兩者層級不同(行清單對整段文字、有無注入框),同樣的「在行界截斷並補一句」邏輯寫了兩遍,但沒造成行為分歧。
引句:「def _lens_text_cap(text, cap=None):」
對照:`_lens_spec_cap_lines` 在 `scripts/lumos:52101`(依行截斷、最後補一句);同函式 `_dispatch_lens_graph` 內另有 400 行上限(`scripts/lumos:51100`)。
判定理由:代碼審路徑現在有「400 行」和「120000 字」兩道截斷,設計審路徑有「12000 字」那道。`_lens_text_cap` 的新增處只有補框尾這一點,其餘是行界截斷。可以讓它先 `split("\n")` 呼叫 `_lens_spec_cap_lines`,再補框尾,note 文字改成參數。不改也不會出錯,只是日後調整截斷邏輯要改兩處。另外設計審路徑(`_dispatch_lens_spec_with_arch`)的輸出沒有經過 `_lens_text_cap`,這是兩路不一致,但因為它有自己的 12000 字上限,不列 finding。

**finding 5**
severity: minor
blocking: 否 — 這是上一輪留下的兩套抽取,這輪只是把其中一套改寫成函式,沒新增第三套。
引句:「found = list(_LENS_SPEC_CODE_RE.findall(scan)) + _arch_target_spec_bt_paths(scan)」
對照:`_lens_spec_code_cands`(`scripts/lumos:52080`)用 `_LENS_SPEC_CODE_RE` 加 `_LENS_SPEC_CODE_BT_RE`,並過濾 `.md` 與 NUL。
判定理由:
1. 差異是刻意的。
   - 設計審找「固定席節點」只認 `_LENS_SPEC_CODE_DIRS` 底下的路徑。
   - 目標架構宣告可以指任何目錄,所以反引號候選不限前綴(舊寫法的 `re.findall(r"`([^`\s]+/[^`\s]+\.[A-Za-z0-9]+)`")` 就已經是這樣)。
2. 兩條路各有自己的 NFC 分組:`_lens_spec_nfc_groups` 兩邊都叫了,沒有重複寫。
3. 但 `_arch_target_spec_bt_paths` 的 `"\0"` 過濾這條路沒做(`_lens_spec_code_cands` 有)。下游 `_arch_target_split` 與 `_lens_git` 對含 NUL 字串的行為沒驗證。最後輸出走名字出口會跳脫,安全面不構成問題。
4. 建議在 `_arch_target_spec_bt_paths` 的註解裡寫明「與 `_LENS_SPEC_CODE_BT_RE` 的差別:不限目錄前綴」,避免下一輪又被問。

**⑤ `_PQ_BLANK_LOOKALIKES` 加字**:已讀,無 finding。
- 新增 U+303F、U+16FE4、U+13441、U+13442 都是「不是 DICP、畫面像空白」的字,跟它原本的用途(註解:Braille 空白、物件替代字元、音樂空符頭)一致。
- 擴充同時讓 `_pq_bad_char`、`_pq_blank` 和 `_pq_leading_problem` 對待辦問題欄位也多擋這四個字。這是同一份定義的自然結果,方向一致,不是副作用。
- 掛鉤抄本 `SPEC_NAME_BLANK_LOOKALIKES` 內容跟 lumos 這份逐字相同。

**其他已讀,無 finding**:
- 掛鉤 `_spec_hidden` 照抄全表,有全碼位比對測試 `t_dispatch_lens_hidden_chars_every_codepoint` 盯著,屬獨立腳本的既有慣例。
- `_clean_field` 的呼叫端改走 `_spec_name_show` 與 lumos 一致。
- `_lens_author_name_show` 加 `code_ok` 旗標沿用「同一出口加參數」的既有形狀,規則原文走名字出口沒有另開出口。
- `_LENS_RESIDUAL_REFS_MAX` 與 `_LENS_RESIDUAL_ASKS_MAX` 同形。

最高等級 major,blocking 1 條。
