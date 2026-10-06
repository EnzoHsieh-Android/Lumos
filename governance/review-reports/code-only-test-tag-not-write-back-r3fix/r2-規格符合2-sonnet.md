severity: clean

# 規格符合審查(r2-snapshot.patch 對 只換測試綁定不算寫說明_計劃)

實跑結果(python3.14 scripts/test_lumos.py -k ...):test_tag_only_edit 25 passed 0 failed(含 S1/S3 與 S2 兩支);test_tag_strip_edges 22 passed 0 failed;new_names_must_be_real 6 passed 0 failed;diff_test_tag_only 2 passed 0 failed;slot_parse_unchanged 2 passed 0 failed。

## 已實作

### 〈範圍〉
- 做①(新名稱核對、test-gone 整串一致、@ 提交編號、拿掉不核對、自己核對)已實作。blocking: 否,無偏離。
  引句:「新的 [test-gone:] 名稱要跟上一版的某個 [test:] 整串一致」 與程式 `old_tests = {nm for k, nm in b["tag_names"] if k == "test"}`、`if not _NODEHOME_TAG_NAME_RE.fullmatch(nm):`
  引句:「if j is None or j(nm)[0] != "yes":」
  spec:「新的 `[test:]` 名稱要是單一識別字(可帶平台前綴;帶點號、::、#、空白的不豁免,代碼審 r3)而且指得到真測試」
  @ 規則:引句:「_NODEHOME_COMMIT_RE = re.compile(r"[0-9a-f]{7,40}")」,一般綁定也套(值判準函式對所有含 @ 的段都檢查)。
- 做②(逐行、沿用 slot_parse 判法、行內程式碼/不成對反引號/沒收尾/別的欄位值/圍欄照留)已實作。
  引句:「vis = {no for no, _ln in _visible_lines(lines)}」(圍欄外才處理)與 `_slot_scan` 內「j = rest.find("`", i + 1)」「if j == -1:」「break」。
  別的欄位值裡的:`_slot_scan` 遇非 test 鍵欄位整段當一個欄位吐出,`_slot_strip_keys` 只拿 keys 內的鍵,內層標記不被掃到。
- 做③(值像測試名)已實作。
  引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」「_NODEHOME_TEST_TAG_VALUE_MAX = 200」,反引號包裹分支 `v[0] == v[-1] == "`" and v.count("`") == 2`。
- 做④(空白規則)已實作。
  引句:「if b >= len(line) or not line[b].isalnum():」(後接字則留前面空白,標點/空白/行尾連前面空白拿掉);「eat = True」(前面只有縮排改拿後面空白);「_NOTELINES_BARE_LIST_RE.match(line) and "[" not in line」(核取方塊不算);「if dropped and not line and out and not out[-1]:」(多出來的空行);每行 `line.rstrip()`。
- 不做①②③④(更正括號、測試檔當家、confirmed 日期、筆記形狀擋放行):diff 無對應程式,確認未多做。

### 〈做法〉
- 1 `_slot_strip_keys(line, keys, keep)` 與 `_slot_scan` 產生器:已實作。引句:「掃描規則只有這一份,slot_parse 與 _slot_strip_keys 共用」,`slot_parse` 改為「for kind, a, b, key, val, err in _slot_scan(rest):」。
- 2 `_nodehome_test_tag_value_ok`、`_nodehome_strip_test_tags`:已實作。引句:「line, rm = _slot_strip_keys(line, ("test", "test-gone"), keep=lambda v: not _nodehome_test_tag_value_ok(v))」,名稱用 `_test_names_of` 切法。
- 3 sig_t、tag_names、`_nodehome_tag_only_change`、`_nodehome_tag_judge`、_ns_tr_guard 回 None、用到才建、提交前與推送前共用:已實作。
  引句:「"sig_t": (st_s.strip(), dec, st_b.strip()),」(決策欄不動);「if tip and _ns_tr_guard(repo_root, tip, pidx[0]):」「return None」;`_tj = []` 加 `def tag_judge():`;`_nodehome_evaluate(..., tag_judge=tag_judge)`、`_nodehome_mark_note_content(..., tag_judge=tag_judge)`。
- 4 寫回圖譜:已實作。Systems/每支檔有家 加 WHY 並改兩行現況(簿記那句、唯一合法寫法那句);Systems/筆記內容閘 加 WHY;Projects/每支檔有家_計劃 的「內容有變」定義、[S12]、唯一解法那句都補例外。
  引句:「只換測試綁定也不算內容有變,條件見 [S12]」「只換測試綁定本來就不算寫說明,不經這條,見 [S12]」
- 5 上線後通知 rtb、關交棒單回頭條件:⚠ 屬流程動作,不在程式 diff 內,無從在此對答案(非縮水,是 diff 外)。

### 驗收條款(逐情境對測試格)
- S1 [test_tag_only_edit]:rc0 情境——換新名 ①、多加(逗號清單、大寫鍵、全形冒號)與刪一個 ②、test→test-gone@提交 ③、測試改名 ⑨;rc1 情境——散文字 ⑥、英文句子/不存在名稱/反引號英文句子 ④、新 test-gone 非上一版綁過 ⑤、非單一識別字(一句說明.真測試名、不存在類別.真測試名、Cls::、Cls#)⑤b、test-gone 前綴不一致(連字號英文前綴、python:)⑤d、@ 非小寫十六進位(含一般綁定帶 @)⑤c ⑤e、值是中文 ⑦、空 [test:] ⑧、行內程式碼舉例被改 ⑪。全部有格。
  引句:「check("⑨同一個提交測試改名、B 換成新名 → rc0", rc == 0, out[-800:])」
- S2 [diff_test_tag_only]:①rc0 散文 ②rc1,有格。
  引句:「check("①推送前:同一個提交改程式、B 只換綁定 → rc0", rc == 0, out[-800:])」
- S3:⑩有格(改沒家舊檔+只換綁定 → rc0 且提醒 ui/old.py)。
  引句:「check("⑩改到沒家舊檔+B 只換綁定 → rc0(只提醒)", rc == 0 and "ui/old.py" in out, out[-800:])」
- S4 [test_tag_strip_edges]:rc1 情境——跨三行 ①、落單反引號+行內舉例 ②、圍欄 ③、別的欄位值 ④、沒收尾 ⑩、空白值 ⑦、超 200 字 ⑨、反引號中文 ⑧、pytest 參數化 ⑥、只改縮排 ⑬、圍欄少空行 ⑭、兩字中間 ⑫b、核取方塊未勾改勾 ⑫c;rc0 情境——單獨成行加/刪 ⑤、夾空行 ⑪(檔內第二個編號⑪)、行首/縮排後/全形空白/tab ⑫、後接句號與全形逗號 ⑫、CRLF ⑮。全部有格。
  引句:「check("⑫c 核取方塊只剩綁定、從未勾改成勾 → rc1(勾選狀態算內容)", rc == 1 and "Systems/B" in out, out[-600:])」
- S5 [slot_parse_unchanged]:有格,舊實作抄本比對全 repo 行,並比對 `_slot_strip_keys` 拿掉全部鍵後與核心一句。
  引句:「check("_slot_strip_keys 拿掉全部鍵後去掉空白 = slot_parse 的核心一句去掉空白(兩支走同一套掃描,邊界判法一致)」
- S6 [new_names_must_be_real]:合約行新寫英文 [test:] ①、無 @ 的英文 test-gone ②、帶 @abc1234 的英文 test-gone ③ 皆 rc1;真測試 ④ rc0;已追蹤測試檔有未提交改動 ④b rc1;推送的不是簽出版本 ⑤ rc1。全部有格。
  引句:「check("④b 推送時已追蹤的測試檔有沒提交的改動(測試索引對不上被推的版本)→ 不豁免、rc1", rc == 1 and "Systems/B" in out, out[-600:])」

### 〈天花板〉1–10
天花板為文件宣告的已知限制,逐條對照實作行為,皆與程式一致,無需額外程式:
- 1 說明剛好是真測試名:判定只核對存在與單一識別字形狀,符合。引句:「if not _NODEHOME_TAG_NAME_RE.fullmatch(nm):」
- 2 更正括號/現況句仍算說明:無任何豁免程式,符合。
- 3 中文值/白名單外符號/pytest 方括號不拿:由值判準正則與 S4 ⑥⑧ 釘住。
- 4 筆記形狀擋不碰:diff 未動筆記形狀程式,符合。
- 5 簽出非終點或有未提交改動不豁免:`_ns_tr_guard` 回非空即 return None,S6 ④b ⑤ 釘住。
- 6 test-gone 只接受上一版同名:`if nm not in old_tests: return False`,S1 ⑤ 釘住。
- 7 只收單一識別字、無 test_profile 掃不到不豁免:`_NODEHOME_TAG_NAME_RE`、judge 為 None 時 return False。
- 8 提交前只查工作目錄索引:`_nodehome_tag_judge(root, None if staged else tip_where)`。
- 9、10 推送時到終點版本整字搜尋、整段共用終點測試清單:沿用 `_ns_tr_judge` 既有行為,diff 未改變,與天花板描述一致。

## 縮水
(無)

## 未實作
(無)

## 多做
(無)。⚠ 三處微小、無 spec 條文直接對應但屬附帶:
- `_nodehome_tag_judge` 建立失敗時印一句提醒到 stderr。blocking: 否,判準:不改變放行結果(仍不豁免),實作紀錄 r3 已記載。
  引句:「提醒:每支檔有家這次沒核對測試名({e.__class__.__name__}),只換測試綁定的筆記照舊算寫了說明」
- `_nodehome_parse_note` 內把迴圈變數 `l` 改名 `ln`(純改寫,輸出不變)。blocking: 否。
  引句:「"sig": ("\n".join(ln.rstrip() for ln in summ.splitlines()).strip(), dec,」
- Systems/每支檔有家 的 TEST 計數行改成「61 支」。blocking: 否,屬筆記同步,實作紀錄已記。

總結:縮水加未實作共 0 條
