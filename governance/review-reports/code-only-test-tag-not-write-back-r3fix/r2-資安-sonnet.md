severity: minor

# 資安驗收:test-gone 整串一致、空白規則改為「後面不是英數或中文就吞前面空白」

驗收範圍:r2-delta.patch 的 scripts/lumos 兩處修正(`_slot_strip_keys` 的空白判斷、`_nodehome_tag_only_change` 的 test-gone 比對),另對照 `_nodehome_strip_test_tags` 與 `_nodehome_test_tag_value_ok`。

## 1. 不可信輸入流到危險操作
已看,無。筆記內容只進字串比對與正規表達式 fullmatch,沒有 shell、eval、檔案路徑拼接。`_NODEHOME_TAG_NAME_RE` 是線性模式,沒有巢狀量詞。
引句:「if not _NODEHOME_TAG_NAME_RE.fullmatch(nm):」
file: `scripts/lumos:26950`(`_nodehome_tag_only_change` 內,行號以工作目錄現況為準)

## 2. 守衛繞過(貢獻者能否讓只換綁定的判定放過一段說明)
已看,無。
- test-gone 改成整串一致後,舊的繞法(用「連字號英文串:舊名」前綴夾帶說明)被堵:前綴不再被剝掉,名稱必須逐字等於上一版某個 `[test:]` 名稱。名稱經 `_test_names_of` 已去掉 `@提交`,提交編號只認 7 到 40 碼小寫十六進位,沒有地方塞自由文字。
- 空白規則改成 `not line[b].isalnum()`:攻擊者只能多加或少加標記旁的空白,拿掉標記後兩版比對的是「沒有標記時的同一行」。要藏說明就得讓說明字元出現在比對文字裡,而那會讓 sig 不同、判成寫說明。標記後面接英數或中文時前面的空白照留,所以不能靠吞空白把兩個字接成一個字去掩蓋改字。
- 殘餘觀察(推論,縱深防禦):上一版若已經存在一個值像測試名的英文句子型 `[test:...]`(例如先前某次順手寫了真正內容改動時帶進去的),之後可以只把它改標成 `[test-gone:同一句]` 而過關。但那句文字在上一版就已經存在並被接受,這次沒有新增任何資訊,不構成新的夾帶通道。
引句:「old_tests = {nm for k, nm in b["tag_names"] if k == "test"}」

severity: minor
推論:誰=有提交權的貢獻者;從哪裡=節點摘要或正文;送什麼進來=把上一版已存在的句子型 `[test:一句話]` 改標成 `[test-gone:同一句話]`;拿到什麼=不需要寫說明就改變該行標記種類,但句子內容在舊版就已存在,沒有新增說明內容,實際收益近乎零。
blocking: 否。判準:推論、無新增資訊洩出或新說明可夾帶,僅屬縱深防禦。

## 3. 密鑰與個資
已看,無。diff 不讀環境變數、不寫 log、不碰憑證。

## 4. 加密與傳輸
已看,無。沒有網路或加解密呼叫。

## 5. 執行邊界
已看,無。沒有 subprocess、eval、pickle 或反序列化新增(R18 不適用);邊界驗證(R15)由值正規表達式、200 字上限、提交編號正規表達式負責,未被本次修正削弱。
引句:「_NODEHOME_COMMIT_RE = re.compile(r"[0-9a-f]{7,40}")」

## 6. 行動端
已看,無。本改動不涉及行動端。

## 新依賴
已看,無。只用標準庫,刪掉 `_NODEHOME_TAG_PREFIX_RE` 縮小了攻擊面。

總結:全份最高等級 minor
