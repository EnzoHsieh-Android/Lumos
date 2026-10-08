F1 驗收：已折好  
F1 blocking：否  
全案等級：未重算；本次不宣稱全案 clean。

原合約要求：

引句:「★同時放一條前置斷言，證明現場真的成立★」  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:278`

引句:「前置斷言失敗 ＝ 這條測試根本沒在測它宣稱要測的東西」  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:287`

三項窄驗收結果：

1. C1／控制字元：已折好

引句:「self.assertEqual(json.loads(p.read_text()), data)」  
file: `governance/eval/test_review_convergence.py:199`

引句:「self.assertIn(chr(0x9B), data["loop"])」  
file: `governance/eval/test_review_convergence.py:200`

這兩條在產品命令執行前確認真實磁碟 JSON 能讀回原資料，且目標 C1 字元確實存在。執行後另以 round-trip 相等證明資料走完輸出路徑，見 file: `governance/eval/test_review_convergence.py:211`。符合我 F1 所要求的獨立現場前置證據。

2. token 型別衝突：已折好

引句:「self.assertIs(type(a["tokens"]), int)」  
file: `governance/eval/test_review_convergence.py:218`

引句:「self.assertIs(type(b["tokens"]), bool)」  
file: `governance/eval/test_review_convergence.py:219`

兩條斷言位於 `build_cohort` 呼叫前，直接證明案例不是兩個同型別值；目標產品呼叫在 file: `governance/eval/test_review_convergence.py:221`。符合 F1。

3. 十萬零一筆：已折好

引句:「raw = b"{}\n" * 100001」  
file: `governance/eval/test_review_convergence.py:233`

引句:「self.assertEqual(p.read_bytes(), raw)」  
file: `governance/eval/test_review_convergence.py:236`

引句:「with self.assertRaisesRegex(ev.DataError, "^input-record-limit$")」  
file: `governance/eval/test_review_convergence.py:237`

`raw` 明確由 100001 筆組成；磁碟讀回與它 byte-equal，且先確認總量低於 16 MiB，見 file: `governance/eval/test_review_convergence.py:235`。因此後續失敗可鎖定為筆數限制，而非 byte limit 或寫檔失敗；錯誤原因也精確要求 `input-record-limit`。符合 F1。

現有日誌只作修後接線佐證：

引句:「Ran 25 tests in 0.430s」  
file: `governance/review-reports/code-review-convergence-eval/r3-fixes-after.log:3`

引句:「OK」  
file: `governance/review-reports/code-review-convergence-eval/r3-fixes-after.log:5`

這只證明目前 25 案在該次修後執行通過；不當作產品修前失敗證據，也不據此宣稱其他席 finding、其他測試家族或全案皆乾淨。

結論：我先前 F1 指出的 formal invariant 缺陷已完整折掉，可解除 F1 的 major／blocking。全案其餘結論與未驗範圍不在本次窄驗收範圍內。