severity: major

# code r3 正確性席3(sonnet)

做法:用 test_lumos.py 的夾具(`_nh_tag_repo`、`_nh_node`、`_nh_check`)在臨時目錄實跑 `lumos home check --staged`,逐題走派工詞列的輸入。

## 逐題結果(無問題的題目)
- 同名綁定出現兩次、摘要搬到正文(不新增名稱):tag_names 是集合,名稱沒變 → rc0,行為合理(只動位置不算寫說明)。實跑 `[test:test_drop][test:test_drop][test:test_old]`、摘要的綁定整批搬進正文都 rc0。
- 新增名稱後面接說明字:`[test:test_new every order needs approval]`、`[test:test_new (every order ...)]`、全形逗號切出的第二項,judge 判 no → rc1,擋得住。
- 連續標記、標記在行尾、標記後接標點:`_slot_strip_keys` 逐段走 `eat` 旗標,結果跟沒寫過那個標記的同一行相同(讀碼走過 `a [t] [t] b`、`[t] [t] b`、`text [t]。`)。
- tag_judge 閉包:`_tj` 清單快取(包含 None),mark_note_content 與 evaluate 共用同一個閉包,索引只建一次;`_nodehome_tag_judge` 建立時丟例外被 try 接住回 None。
- b 是 None(新開):`_nodehome_tag_only_change` 第一行回 False。

## finding 1:`[test-gone:]` 的 `@` 後面可藏任意英文說明,整句被當成「只換測試綁定」
severity: major
blocking: 是——放行了一次真正的說明改動(寫了說明卻不算寫說明),本案要擋的方向的反面;補洞檢查(test-gone 名稱要是上一版綁過的 test)只看 `@` 前面。
file: `scripts/lumos:26893`(`_nodehome_strip_test_tags`)、`scripts/lumos:29712`(`_test_names_of`,test-gone 走 split("@") 取第一段,`@` 之後全丟掉)
引句:「names |= {(key, nm) for nm in _test_names_of({"fields": [(key, val, None)]}, key)[0]}」
失敗場景:`_nodehome_test_tag_value_ok` 的字元集允許空白與英數,所以 `test_drop@1a2b3c4 now every order needs manager approval` 整段算「像測試名」被整個標記拿掉;名稱只剩 `test_drop`(在上一版 [test:] 裡)→ 判成站得住。`@` 後面的一句英文不留痕、不進 sig_t,也不被任何檢查核對(提交時 test_refs 只提醒,不核對 test-gone 的 `@` 後文)。
最小重現(臨時 repo,B 上一版 `- [S2] 另一條 [test:test_drop]`,本次同一個提交改了 src/a.py):

```
body 新版 S2 行: - [S2] 另一條 [test-gone:test_drop@1a2b3c4 now every order needs manager approval]
對照組(同一句寫成散文): - [S2] 另一條 [test:test_drop] now every order needs manager approval
```
實跑(`lumos home check --staged`):
```
control sentence as prose        rc= 1   (擋下,正確)
A2 test-gone @ hidden sentence   rc= 0   (放行,錯)
G  [test-gone:test_drop@ every order needs approval]  rc= 0
```
修法方向:test-gone 的 `@` 後文要驗成提交雜湊字樣(`[0-9a-f]{7,40}` 或空),不是就不算「像測試名」、整個標記留在文字裡。

## finding 2:前綴不一致的 test → test-gone 照舊誤擋(低,保守方向)
severity: minor
blocking: 否——只是多擋,有 `python:test_drop` 的正確寫法可走,不放過任何內容。
file: `scripts/lumos:26946`(`_nodehome_tag_only_change`)
引句:「if nm not in old_tests:」
失敗場景:上一版 `[test:test_drop]`,新版寫 `[test-gone:python:test_drop@abc]`,名稱 `python:test_drop` 不等於 `test_drop`,實跑 rc1。依「改成已刪」語意這是同一支測試。

## 其他未見問題
- judge 回 skip/undecidable/no 一律 `j(nm)[0] != "yes"` → 不豁免,方向保守。
- 推送前合併提交(olds 兩個):`any(...)` 逐個上一版各自比,只會比單一父版本多放過「跟某一邊只差綁定」的情形,與註解「合併時照搬某一邊也算」一致。
- 未能走到:judge 的 `__call__` 本身丟例外(`_classify_test_refs` 異常)時 `_nodehome_tag_only_change` 沒有 try,例外往外冒;沒找到能觸發的輸入,不標。

總結:全份最高等級 major
