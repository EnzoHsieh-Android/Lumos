severity: minor

# 規格符合審查 r2(只換測試綁定不算寫說明)

範圍:spec 現檔〈範圍〉做 4 條、不做 4 條,〈做法〉1–5,[S1]–[S6];對照 r2-snapshot.patch(scripts/lumos、scripts/test_lumos.py、兩篇 Systems 筆記)。唯讀,未跑測試。

## 一、已實作

### 範圍·做1(提交前與推送前都比 sig_t,只在 test_refs 與 note_shape 都是 block 時)
severity: clean
blocking: 否 + 對應實作齊全
- scripts/lumos @@ -4135 起:`_nodehome_tag_exempt` 讀 `_note_shape_config` 與 `_ns_test_refs_mode`,只有 block 才回真;`cmd_home_check` 的 hunk 把 `cfg["tag_exempt"]` 設好。提交前走 `_nodehome_evaluate` 的 sk,推送前走 `_nodehome_mark_note_content(..., tag_exempt=...)`。
引句:「sk = "sig_t" if cfg.get("tag_exempt") else "sig"」
spec:「★只在專案的「筆記測試綁定要存在」推送時會擋(note_shape 總開關與 test_refs 都是 block)時這樣比★」

### 範圍·做2(逐行、照 slot_parse 判法)
severity: clean
blocking: 否 + 鍵、收尾、行內程式碼、未收尾、別欄位內、圍欄行都有處理
- `_slot_scan` 保留反引號段、`_SLOT_KEY_RE` 加 `_SLOT_CANON`、`_slot_value_end`。`_slot_strip_keys` 對 `err is None` 才拿,未收尾的整段照留。別欄位值裡的標記整體是一個欄位,內層不被掃到。圍欄行由 `_visible_lines` 排除後原樣放回。
引句:「if kind == "field" and key in keys and err is None and not (keep and keep(val)):」
spec:「值沒收尾就那一段到行尾原樣照留」

### 範圍·做3(值像測試名)
severity: clean
blocking: 否 + 字元集、200 字、反引號包裹都對得上
- `_NODEHOME_TEST_TAG_VALUE_RE` 字元集含英數 _ . : / # @ , ( ) [ ] ' > 連字號與空白;`_nodehome_test_tag_value_ok` 判非空、至多 200、整段包一對反引號時套同一組字元。
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」

### 範圍·做4(只剩清單符號整行不算、空白壓平、空行收斂)
severity: clean
blocking: 否 + 用既有 `_NOTELINES_BARE_LIST_RE`
引句:「if k and (not line.strip() or _NOTELINES_BARE_LIST_RE.match(line)):」

### 範圍·不做 4 條
severity: clean
blocking: 否 + diff 無對應豁免
- 無更正括號、現況句、`[confirmed:]` 豁免;測試檔不當家;筆記形狀擋未動。

### 做法1(共用產生器 `_slot_scan`、`_slot_strip_keys(line, keys, keep)` 回兩個值、連前面空白一起拿)
severity: clean
blocking: 否 + 掃描只有一份
引句:「def _slot_strip_keys(line, keys, keep=None):」

### 做法2(值判準函式與 `_nodehome_strip_test_tags`)
severity: clean
blocking: 否 + 唯一差異見下方多做 ⚠
引句:「vis = {no for no, _ln in _visible_lines(lines)}」

### 做法3(sig 不動、另加 sig_t;讀被檢查版本設定;兩處改比 sig_t)
severity: clean
blocking: 否 + 決策欄未動,提交前與推送前都改
引句:「"sig_t": (_nodehome_strip_test_tags(summ).strip(), dec, _nodehome_strip_test_tags(body).strip()),」

### 做法4(寫回圖譜)
severity: clean
blocking: 否 + 兩行現況與兩篇 WHY 都有
- 每支檔有家:加 WHY;「內容(摘要、決策、正文)是在這個提交改的才算寫回」那行補「只換、加、刪測試綁定標記也不算」;「越界的唯一合法寫法」那行補「只換測試綁定標記不算寫說明、不算越界」。筆記內容閘加 WHY 記 `_slot_scan` 與 `_slot_strip_keys`。
引句:「只換測試綁定標記不算寫說明、不算越界——前提同上一條」

### 做法5(上線後告知 rtb)
severity: clean
blocking: 否 + 屬上線後動作,不在 diff 範圍
⚠ 無法由 diff 驗證,未判。

## 二、驗收條款逐格對照

| 條款 | 情境 | 對應測試格 |
|---|---|---|
| S1 回0 | 舊換新 | t_nodehome_test_tag_only_edit_is_not_write_back ① |
| S1 回0 | 多加、刪、鍵大寫、全形冒號、鍵旁空白 | 同上 ② |
| S1 回0 | test 改 test-gone | 同上 ③ |
| S1 回0 | 反引號包英文句子 | 同上 ④ |
| S1 回1 | 同時改散文字 | 同上 ⑤ |
| S1 回1 | 值是中文 | 同上 ⑥ |
| S1 回1 | 空的 `[test:]` | 同上 ⑦ |
| S1 回1 | 行內程式碼裡的舉例 | 同上「⑦b」(編號與空值格重複,內容有對應) |
| S1 回1 | 設定沒設、test_refs warn、gate warn | 同上 ⑪,三種設定迴圈 |
| S2 | 推送前換綁定 回0、改散文 回1 | t_nodehome_diff_test_tag_only_edit_is_not_write_back ①②(散文那格只改了散文,綁定同一版) |
| S3 | 沒家舊檔加只換綁定,只提醒 | t_nodehome_test_tag_only_edit_is_not_write_back ⑧ |
| S4 回1 | 跨三行假標記 | t_nodehome_test_tag_strip_edges ① |
| S4 回1 | 前行落單反引號、下一行行內程式碼被改 | 同上 ② |
| S4 回1 | 圍欄內被改 | 同上 ③ |
| S4 回1 | 別欄位值裡被改 | 同上 ④ |
| S4 回1 | 方括號沒收尾 | 同上 ⑩ |
| S4 回1 | 空白值 | 同上 ⑦ |
| S4 回1 | 超過 200 字 | 同上 ⑨ |
| S4 回1 | 反引號裡中文 | 同上 ⑧ |
| S4 回0 | 單獨成行加、刪 | 同上 ⑤ |
| S4 回0 | 夾在空行之間 | 同上 ⑪ |
| S4 回0 | 行首、全形空白 | 同上 ⑫ |
| S4 回0 | pytest 參數化換名 | 同上 ⑥ |
| S5 | 全 repo 逐行 slot_parse 一致、strip 全鍵等於核心一句 | t_slot_parse_unchanged_after_scan_refactor 兩格 |
| S6 | block 時 home check 回0 | t_nodehome_tag_exempt_hidden_sentence_caught_by_test_refs ① |
| S6 | 同段推送筆記形狀擋回1 並點名 | 同上 ② |
| S6 | 改 warn 後 home check 回1 | 同上 ③ |

每種情境都有對應格,無缺格。

## 三、縮水
無。

## 四、未實作
無。(做法5 為上線後動作,diff 不含,⚠ 不判。)

## 五、多做
### 圍欄內空行也被收斂 ⚠
severity: minor
blocking: 否 + 只影響圍欄內連續空行的比對,不會讓說明漏判成沒變
- `_nodehome_strip_test_tags` 的空行收斂在 `if no in vis` 區塊外,圍欄內的連續空行也會收成一行。
引句:「if not line.strip() and out and not out[-1].strip():」
spec:「圍欄內的行與圍欄標記行原樣放回」
- 判斷:〈範圍〉做4 寫「圍欄外每行空白壓成一格、連續空行收成一行」,並未明說圍欄內;與做法2 的「原樣放回」有輕微張力。圍欄內只差空行的改動,會被當成沒變。

### 其他
- 兩篇筆記的 TEST 支數與 updated 更新、WHY 行綁測試,屬寫回,不算行為多做。
- 無其他 spec 沒有對應的行為變更。

總結:縮水加未實作共 0 條
