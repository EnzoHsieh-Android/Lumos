severity: clean

# 規格符合審查 r3(只換測試綁定不算寫說明)

實跑(python3.14 scripts/test_lumos.py -k ...):test_tag_only_edit 15 過 0 敗(含 diff_test_tag_only 那支)、test_tag_strip_edges 15 過、new_names_must_be_real 5 過、diff_test_tag_only 2 過、slot_parse_unchanged 2 過,全綠。

## 已實作

### 〈範圍〉做 1(提交前與推送前兩路;新 test 要真測試、test-gone 要上一版綁過、拿掉不核對、自己核對)
hunk:scripts/lumos `_nodehome_tag_only_change`、`_nodehome_evaluate`、`_nodehome_mark_note_content`
引句:「for k, nm in sorted(n["tag_names"] - b["tag_names"]):」
引句:「if j is None or j(nm)[0] != "yes":」
裁定:已實作。拿掉的綁定不進核對(只迭代新增集合);judge 為 None 不豁免。

### 〈範圍〉做 2(逐行、共用 slot_parse 判法、行內程式碼/未收尾/別欄位值/圍欄)
hunk:`_slot_scan`、`_slot_strip_keys`、`_nodehome_strip_test_tags`
引句:「if kind == "field" and key in keys and err is None and not (keep and keep(val)):」
引句:「vis = {no for no, _ln in _visible_lines(lines)}」
裁定:已實作。別欄位值內的標記在 `_slot_value_end` 內被整段吞掉,不成為獨立欄位。

### 〈範圍〉做 3(值判準)
hunk:`_NODEHOME_TEST_TAG_VALUE_RE`、`_nodehome_test_tag_value_ok`
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
裁定:已實作(200 字、反引號包裹、空值皆對)。

### 〈範圍〉做 4(空白規則、清單符號整行、空行、尾端空白)
hunk:`_slot_strip_keys`(`_SLOT_STRIP_WS = " \t　"`)、`_nodehome_strip_test_tags`(`_NOTELINES_BARE_LIST_RE`、dropped 旗標)
引句:「if rm and (not line.strip() or _NOTELINES_BARE_LIST_RE.match(line)):」
裁定:已實作。

### 〈範圍〉不做 四條(更正括號、測試檔當家、confirmed、筆記形狀擋)
hunk:全 diff 無相關程式變更
引句:「"sig": ("\n".join(ln.rstrip() for ln in summ.splitlines()).strip(), dec,」
裁定:已實作(沒多做);原 sig 保留、決策欄不動。

### 〈做法〉1(`_slot_scan` + `_slot_strip_keys`,slot_parse 走共用產生器)
引句:「def _slot_scan(rest):」
裁定:已實作。

### 〈做法〉2(`_nodehome_test_tag_value_ok`、`_nodehome_strip_test_tags`,名稱照 `_test_names_of`)
引句:「names |= {(key, nm) for nm in _test_names_of({"fields": [(key, val, None)]}, key)[0]}」
裁定:已實作。

### 〈做法〉3(sig_t、tag_names、`_nodehome_tag_judge` 共用 `_NsTrJudge`、`_ns_tr_guard`、用到才建)
引句:「if tip and _ns_tr_guard(repo_root, tip, pidx[0]):」
引句:「"""測試名判定,第一次真的需要(某篇只差測試綁定)才建——建索引要掃測試檔。"""」
裁定:已實作。

### 〈做法〉4(寫回圖譜)
hunk:Systems/每支檔有家.md(WHY 一行、兩行現況說明改寫)、Systems/筆記內容閘.md(WHY)、Projects/每支檔有家_計劃.md(內容有變定義、[S12]、誤擋唯一解法那句)
引句:「(2026-10-05 補:只換測試綁定本來就不算寫說明,不經這條,見 [S12])」
裁定:已實作。

### 〈做法〉5(上線後告訴 rtb)
裁定:屬上線後人工動作,diff 不含;⚠ 不計入縮水(非程式規格)。

### 驗收條款對測試格
- S1:換名/新增/刪/test-gone ①②③⑨;rc1 各情境:散文⑥、英文句子/不存在名稱/反引號英文④、新寫 test-gone 非舊綁⑤、中文值⑦、空 `[test:]`⑧、行內程式碼舉例⑪。
引句:「check("②多加綁定(逗號清單、大寫鍵與全形冒號)、刪掉一個綁定 → rc0", rc == 0, out[-800:])」
- S2:t_nodehome_diff_test_tag_only_edit_is_not_write_back ①rc0、②rc1。
引句:「check("②推送前:同一個提交改程式、B 改散文 → rc1", rc == 1 and "Systems/B" in out, out[-800:])」
- S3:⑩。
引句:「check("⑩改到沒家舊檔+B 只換綁定 → rc0(只提醒)", rc == 0 and "ui/old.py" in out, out[-800:])」
- S4:rc1 的跨三行①、落單反引號②、圍欄③、別欄位④、沒收尾⑩、空白值⑦、200 字⑨、反引號中文⑧、pytest 參數化⑥、只改縮排⑬、圍欄少空行⑭;rc0 的單獨成行(含空行夾住)⑤⑪、行首/縮排/全形⑫、CRLF⑮。全部有格。
引句:「check("⑭圍欄裡少一個空行 → rc1(圍欄裡原樣)", rc == 1 and "Systems/B" in out, out[-600:])」
- S5:全 repo 逐行比對與 strip 全鍵等於 core。
引句:「check(f"全 repo 筆記 {len(lines)} 行的 slot_parse 輸出跟改之前一樣", not bad, repr(bad[:3]))」
- S6:合約行英文 test、test-gone 帶/不帶 @ ①②③;真測試 ④rc0;非簽出版本 ⑤rc1。
引句:「check("⑤推送的不是目前簽出的版本(測試索引對不上)→ 不豁免、rc1", rc == 1 and "Systems/B" in out, out[-600:])」
- 天花板 1–6:皆為已知限制說明,與實作一致(英文真測試名可過;中文/白名單外符號/參數化不拿;不是終點不豁免;test-gone 只認舊綁)。

## 縮水
無。

## 未實作
無。

## 多做
無(diff 中除規格列的行為外,只有 test 夾具、治理筆記的 TEST 支數機械數更新、純改名 `l`→`ln`)。

總結:縮水加未實作共 0 條
