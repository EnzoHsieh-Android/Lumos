severity: major

# 第三輪修正驗收(通才席)

實跑環境:`_nh_tag_repo` 夾具(python 測試棧),另把 `note_shape.test_refs` 設成 block;每個案例同時跑 `home check --staged`(與 `--diff`)和 `note-shape --diff HEAD~1..HEAD`。腳本在 scratchpad 的 h.py、h2.py。

## 已驗證被擋(rc=1)的路,不再報
- 逗號清單混說明 `[test:test_new, now every order needs approval]`、`test_new (說明)`、`test_new[說明]`、`test_new@1a2b3c4`
- 非 test 的鍵(`[tests:…]`、`[TEST:…]` 之外的 `[test_gone:…]`)夾說明:不拿掉,算內容,home 擋
- 新 `[test:]` 帶連字號假前綴 `Every-order:test_new`:home 擋,note-shape 也擋(bad-name)
- 對照組 `[test-gone:every order needs approval]`:home 擋

## Finding 1:test-gone 的平台前綴能走私連字號散文,兩道檢查都過

severity: major
blocking: 是——一句話(連字號串成)寫進不是家的筆記,home check 與 note-shape 都放行,正是本輪要堵的類別;前三輪同類(英文句子包成 test-gone)判 blocker/major。
file: `scripts/lumos:26938`(`bare()` 用 `_NODEHOME_TAG_PREFIX_RE` 把任何 `[A-Za-z0-9_-]+:` 前綴剝掉,再拿剩下的名稱比 `old_tests`,前綴本身從不核對)
引句:「        return _NODEHOME_TAG_PREFIX_RE.sub("", x)」
引句:「_NODEHOME_TAG_PREFIX_RE = re.compile(r"^[A-Za-z0-9_-]+:(?!:)")」
失敗場景:上一版有 `[test:test_drop]`,同一個提交改了 src/a.py,B 的那行改成
`- [S2] 另一條 [test-gone:Every-order-now-needs-manager-approval-and-retry-count-is-three:test_drop@1a2b3c4]`。
- 值只含白名單字元,被當綁定拿掉;名稱去前綴後是 `test_drop`,在上一版綁過,test-gone 分支直接放行(沒呼叫判定,前綴不用是真平台)。
- 實跑:`home check --staged` rc=0、`--diff base..HEAD` rc=0、`note-shape --diff` rc=0(test_refs=block 也一樣)。測試檔裡 test_drop 還在、或在同一提交改名刪掉,結果相同。
- 同一行、同一個 `[test-gone:]` 的逗號清單、或多個標記,都能用不同前綴重複同一個舊名稱(`[test-gone:Every-order:test_drop@1a2b3c4, needs-manager:test_drop@1a2b3c4]` 實跑兩道皆 rc=0),每個值 200 字內,所以能帶的散文沒有上限,只受「要有一個上一版綁過的名稱」限制。
最小重現(臨時 repo):夾具 `_nh_tag_repo()`,B 兩版只差上面那一行,再 `home check --staged`;對照把前綴拿掉的英文句子版本 rc=1。
對照新 `[test:]` 同形(`Every-order:test_new`)被擋,是因為判定要認得平台;test-gone 分支少了這道。修法方向:test-gone 的前綴要是設定裡的真平台,或比對時要求前綴與上一版綁定的前綴一致。

## 其餘找過但沒找到新路
- 刪舊綁定換新綁定夾帶散文:散文可見字照比,sig_t 不同,擋。
- `@提交` 只收 7 到 40 位十六進位;能走私的資訊量可忽略。
- 把說明拆成一串各自是真測試的單一識別字名稱:只有測試檔在同一提交改成句子式測試名才行,屬〈天花板〉1,不另報。
- 前言欄位(responsibility、aliases 等)不在 sig 內:本輪之前就如此,不是這輪引入。

總結:全份最高等級 major
