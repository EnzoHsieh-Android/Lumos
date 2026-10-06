severity: clean

# 規格符合審查(只換測試綁定不算寫說明,r3fix)

實跑結果(python3.14 scripts/test_lumos.py -k ...):test_tag_only_edit 22 過、test_tag_strip_edges 17 過、new_names_must_be_real 6 過、diff_test_tag_only 2 過、slot_parse_unchanged 2 過,全部 0 失敗。

## 縮水
無。

## 未實作
無。(〈做法〉5「上線後告訴 rtb」是上線後的人工動作,不在 diff 範圍,見下方 ⚠。)

## 多做
無。(無 spec 對應的行為變更;r3 實作紀錄內已載的「判定建立失敗印一句」「判定丟例外當不豁免」屬 spec 實作紀錄,不算多做。)

## 已實作(逐條)

### 〈範圍〉
1. 做:新名稱核對(單一識別字、指得到真測試、test-gone 要上一版綁過且去前綴、@ 後只認 7–40 碼十六進位、拿掉不核對、自己核對):已實作。位置 scripts/lumos `_nodehome_tag_only_change`、`_NODEHOME_TAG_NAME_RE`、`_NODEHOME_COMMIT_RE`、`_nodehome_test_tag_value_ok`。
引句:「if not _NODEHOME_TAG_NAME_RE.fullmatch(nm):」
引句:「return all(_NODEHOME_COMMIT_RE.fullmatch(x.split("@", 1)[1].strip()) for x in _NS_TR_SPLIT_RE.split(v) if "@" in x)」
   ⚠ 小註:@ 提交編號檢查在 value_ok 對 test 與 test-gone 兩種鍵都套(spec 只講 test-gone);但 test 名稱本來就過不了 NAME_RE 的 @,結果不變,不算多做。
2. 做:逐行、跟 slot_parse 同判法、行內程式碼/不成對反引號/沒收尾/別欄位值/圍欄:已實作。`_slot_scan` + `_slot_strip_keys`(err 不為 None 或 keep 為真原樣留)、`_visible_lines` 取圍欄外行。
引句:「if kind == "field" and key in keys and err is None and not (keep and keep(val)):」
3. 做:值判準(非空、至多 200、白名單字元、可整段反引號包):已實作。
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
4. 做:空白規則、只剩清單符號整行不算(沿用 `_NOTELINES_BARE_LIST_RE`、核取方塊不算)、多出空行不算、每行去尾端空白:已實作。
引句:「if rm and (not line.strip() or (_NOTELINES_BARE_LIST_RE.match(line) and "[" not in line)):」
5. 不做(更正括號、測試檔當家、confirmed 日期、筆記形狀放行):已遵守,diff 沒有碰這些,strip 的鍵只有 test、test-gone。
引句:「_slot_strip_keys(line, ("test", "test-gone"), keep=lambda v: not _nodehome_test_tag_value_ok(v))」

### 〈做法〉
1. `_slot_strip_keys(line, keys, keep)` + 抽共用產生器 `_slot_scan`、slot_parse 改走它:已實作。
引句:「掃描規則只有這一份,slot_parse 與 _slot_strip_keys 共用」
2. `_nodehome_test_tag_value_ok`、`_nodehome_strip_test_tags` 回 (文字, 名稱集合),圍欄內原樣、名稱照 `_test_names_of`:已實作。
引句:「names |= {(key, nm) for nm in _test_names_of({"fields": [(key, val, None)]}, key)[0]}」
3. sig 不動、加 sig_t(摘要與正文過 strip、決策不動)與 tag_names;`_nodehome_tag_only_change`;`_nodehome_tag_judge` 共用 `_NsTrJudge`、推送時 `_ns_tr_guard` 對不上回 None;判定用到才建、交給 `_nodehome_evaluate` 與 `_nodehome_mark_note_content`:已實作。
引句:「if tip and _ns_tr_guard(repo_root, tip, pidx[0]):」
引句:「if n is not None and any(o["sig"] == n["sig"] or _nodehome_tag_only_change(o, n, tag_judge) for o in olds):」
引句:「if ((b is None or b["sig"] != n["sig"]) and not _nodehome_tag_only_change(b, n, tag_judge)」
4. 寫回圖譜:Systems/每支檔有家 加 WHY 並改兩行現況(逐提交那行、唯一合法寫法那行);Systems/筆記內容閘 加 WHY;Projects/每支檔有家_計劃 的「內容有變」、[S12]、「唯一的解法」三處補例外:已實作。
引句:「只換、加、刪測試綁定、而且新出現的名稱指得到真測試也不算,見 [[Projects/只換測試綁定不算寫說明_計劃]]」
引句:「只換測試綁定本來就不算寫說明,不經這條,見 [S12]」
5. 上線後告訴 rtb:⚠ 不在 diff,屬人工動作,無法由 diff 判定;不計入縮水/未實作(計劃狀態仍是 doing)。

### 〈驗收條款〉(情境對測試格)
- [S1] test:t_nodehome_test_tag_only_edit_is_not_write_back
  - rc0:換舊為新=①;逗號清單、大寫鍵、全形冒號加綁定+刪綁定=②;test-gone 改標=③;帶平台前綴=⑤d;同提交測試改名=⑨。
  - rc1:改散文=⑥;新綁定指不到真測試(英文句子、不存在名稱、反引號英文句)=④;test-gone 非上一版綁過=⑤;非單一識別字(說明.真測試名、不存在類別.真測試名、::、#)=⑤b;test-gone 的 @ 後非提交編號=⑤c;值是中文=⑦;空 [test:]=⑧;行內程式碼舉例=⑪。全數有格。
  引句:「check("⑤d test-gone 帶平台前綴、上一版綁的是同名(沒前綴)→ rc0", rc == 0, out[-800:])」
- [S2] test:t_nodehome_diff_test_tag_only_edit_is_not_write_back:rc0=①、散文 rc1=②。已有格。
  引句:「check("①推送前:同一個提交改程式、B 只換綁定 → rc0", rc == 0, out[-800:])」
- [S3] 沒家舊檔+只換綁定只提醒:=⑩(斷言 rc0 且輸出含 ui/old.py)。已有格。(⚠ 輕微:沒有斷言輸出不含「每支改動檔都要有家」字樣,但 rc0 已排除擋下,不影響裁定。)
  引句:「check("⑩改到沒家舊檔+B 只換綁定 → rc0(只提醒)", rc == 0 and "ui/old.py" in out, out[-800:])」
- [S4] test:t_nodehome_test_tag_strip_edges
  - rc1:跨三行假標記=①;落單反引號=②;圍欄=③;別欄位值=④;沒收尾=⑩;只有空白值=⑦;超過 200 字=⑨;反引號中文=⑧;pytest 參數化=⑥;只改縮排=⑬;圍欄少空行=⑭;標記插兩字中間=⑫b;核取方塊未勾改勾=⑫c。
  - rc0:單獨成行綁定加刪=⑤;夾空行=⑪(尾格);行首/縮排後/全形空白=⑫;CRLF=⑮。全數有格。
  引句:「check("⑫c 核取方塊只剩綁定、從未勾改成勾 → rc1(勾選狀態算內容)", rc == 1 and "Systems/B" in out, out[-600:])」
- [S5] test:t_slot_parse_unchanged_after_scan_refactor:全 repo 逐行比對舊版抄本、strip 全部鍵後去空白等於 core 去空白,兩個斷言都在。
  引句:「check(f"全 repo 筆記 {len(lines)} 行的 slot_parse 輸出跟改之前一樣", not bad, repr(bad[:3]))」
- [S6] test:t_nodehome_tag_only_new_names_must_be_real_tests:合約行新寫英文 test=①、新寫 test-gone 英文=②、帶 @提交=③(皆 rc1 點名 B);真測試 rc0=④;已追蹤測試檔有未提交改動不豁免=④b;推送非簽出版本不豁免=⑤。全數有格。
  引句:「check("⑤推送的不是目前簽出的版本(測試索引對不上)→ 不豁免、rc1", rc == 1 and "Systems/B" in out, out[-600:])」

### 〈天花板〉
1–8 皆為文件宣告的已知限制,實作與之一致:中文說明與白名單外符號不拿掉(value_ok);新 test-gone 沒綁過就不豁免(`bare(nm) not in old_tests`);名稱只收單一識別字(NAME_RE,連字號與括號不過);推送非終點/未提交改動回 None;提交前 tip=None 只查工作目錄索引;本案不動筆記形狀。無縮水。
引句:「if bare(nm) not in old_tests:」

總結:縮水加未實作共 0 條
