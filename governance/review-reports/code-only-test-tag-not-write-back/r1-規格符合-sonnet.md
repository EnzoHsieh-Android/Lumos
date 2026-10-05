severity: minor

# 規格符合對答案 r1(spec:只換測試綁定不算寫說明_計劃;diff:r1-snapshot.patch)
實測:`-k test_tag` 21 passed 0 failed;`-k scan_refactor` 1 passed。

## 已實作
- 範圍1(兩條路判內容有沒有變先拿掉綁定):`_nodehome_parse_note` 的 sig 摘要與正文都過 `_nodehome_strip_test_tags`,決策欄不動;提交前與推送前共讀同一 sig。
  引句:「"sig": ("\n".join(l.rstrip() for l in _nodehome_strip_test_tags(summ).splitlines()).strip(), dec,」
- 範圍2(逐行、走 slot_parse 判法):`_slot_scan` 保留反引號段(成對跳過、不成對 break 後剩餘當正文)、`_SLOT_KEY_RE`+`_SLOT_CANON`、`_slot_value_end`;未收尾欄位帶 err 被 `_slot_strip_keys` 照留;別欄位值內的 [test:] 因整個欄位不是 test 鍵而保留;圍欄行靠 `_visible_lines`(預設 keep_fenced=False,與 spec 一致)排除、原樣放回。
  引句:「if kind == "field" and key in keys and err is None and not (keep and keep(val)):」
- 範圍3(值判準):regex 字元集、空值、200 字上限、整段一對反引號內套同組字元,皆與 spec 逐項一致。
  引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
- 範圍4(拿完只剩空白/清單符號整行不算):有。
  引句:「if k and _NODEHOME_BARE_ITEM_RE.fullmatch(line):」
- 範圍「不做」四條:diff 無更正括號豁免、無測試檔當家、無 confirmed 日期豁免、未動筆記形狀擋。皆遵守。
- 做法1:`_slot_scan` 產生器 + `slot_parse` 與 `_slot_strip_keys` 共用;拿掉時連標記前空白一起拿(rstrip " \t"),其餘原樣;值沒收尾照留。
  引句:「def _slot_strip_keys(line, keys, keep=None):」
- 做法2:`_nodehome_test_tag_value_ok`、`_nodehome_strip_test_tags` 皆在,逐行呼叫 keep=lambda v: not value_ok,拿掉後裸清單行丟棄。
- 做法3:見範圍1。
- 做法4(寫回圖譜):每支檔有家加 WHY、兩行現況說明(「只換、加、刪測試綁定標記也不算」「只換測試綁定標記本來就不算寫說明、不算越界」)皆改;筆記內容閘加 WHY。
  引句:「WHY:[2026-10-05 [[Projects/只換測試綁定不算寫說明_計劃]]]行內標記的掃描規則抽成一支 `_slot_scan`」
- S1:test 有 ①換名 ②多加+刪+大寫鍵+全形冒號+鍵旁空白+`Cls::方法`+`名稱@提交` ③test-gone ④反引號英文句子 皆 rc0;⑤散文字 ⑥中文值 ⑦空 `[test:]` ⑦b 行內程式碼舉例 皆 rc1 並點名 B。「只有空白的值」那格在 S4 測試 ⑦ 而非 S1 測試(見 minor 備註),但有對應格。
  引句:「check("⑦空的綁定標記不算綁定 → rc1", rc == 1 and "Systems/B" in out, out[-800:])」
- S2:`t_nodehome_diff_test_tag_only_edit_is_not_write_back` ①rc0 ②改散文 rc1。
  引句:「check("①推送前:同一個提交改程式、B 只換綁定 → rc0", rc == 0, out[-800:])」
- S3:S1 測試 ⑧ 改沒家舊檔+B 只換綁定 → rc0 且輸出含 ui/old.py。
  引句:「check("⑧改到沒家舊檔+B 只換綁定 → rc0(只提醒)", rc == 0 and "ui/old.py" in out, out[-800:])」
- S4:跨三行假標記①、落單反引號+行內舉例②、圍欄③、別欄位值④、方括號沒收尾⑩、超 200 字⑨、反引號中文⑧ 皆 rc1;單獨成行綁定加刪⑤、pytest 參數化⑥ 皆 rc0。七種 rc1 情境與兩種 rc0 情境全有格。
  引句:「check("⑤單獨成行的綁定(清單符號加標記)刪一行、加兩行 → rc0", rc == 0, out[-600:])」
- S5:`t_slot_parse_unchanged_after_scan_refactor` 以保留的舊版實作逐行比全 repo 筆記並加刁鑽行。
  引句:「bad = [ln for ln in lines if m.slot_parse(ln) != _slot_parse_reference(ln, m)]」

## 縮水
無。

## 未實作
無(做法5「上線後告訴 rtb」屬事後人工動作,不在 diff 範圍,不判。)

## 多做
1. 清單符號判法比 spec 多收 `1)` 型。
   引句:「_NODEHOME_BARE_ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+[.)])?\s*")」
   spec:「整行不算(單獨成行的綁定加或刪不算內容有變)」且清單符號列「(`-`、`*`、`+`、`1.`)」
severity: minor
   blocking: 否 + 行為只放寬到 `1)` 這種同族清單符號,方向與 spec 意圖一致,不會讓說明漏過(行內仍只剩標記才丟)。
2. `_slot_strip_keys` 回傳 (行, 拿掉個數) 的 tuple,spec 寫「回拿掉指定鍵的欄位後的那一行」;另拿掉標記前空白含 tab。屬實作細節,供做法2「有拿掉東西」判斷之用,非行為變更。⚠ 純備註,不計入。
   引句:「return "".join(out), k」
severity: minor
   blocking: 否 + 純內部簽名差異,無外部行為。

備註(minor,非縮水):S1 條款把「只有空白的值」列在 S1 情境,實際由 S4 測試 ⑦ 驗(S1 測試 ⑦ 是空 `[test:]`);條款綁定的測試分檔略有不同,但情境均有格。

縮水+未實作共 0 條
