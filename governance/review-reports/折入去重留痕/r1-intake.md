preflight-4: ran

# r1 前掃留痕(折入去重留痕)
日期:2026-09-03。前掃席=haiku;四項+肯定斷言逐條實跑。編排者回原檔核後處置。
## 機械排乾
refcheck 1/1 對得上;prose-lint 0;pitfalls --check 有節;doctor 0。
## ④ 語意類(修改前→後)
- ★抄錯迴圈名(前掃報對)★:原寫「驗證層自證三件 r1 五席 32 條→15 id」;32 條與 15 id 其實是 `panel收斂判準改革` r1 的數字(早上通才席數的)。編排者重數:panel收斂判準改革 r1 五席、六份報告原始發現約 34 條→15 id、id 出現 0 次;驗證層自證三件 r1 五份約 39 條→18 id、1 命中。兩個迴圈都支持「合併判斷無留痕」,已改寫成正確歸屬。★同日第 N 次:抄別處數字沒重數。★
- 「key 任意字串,節點明寫」→ 節點原文是「跨 finder 正規化(casefold+strip)」,未寫「任意」;改為引程式碼 `_capture_counts_from_finders` 的 `str(k).strip().casefold()`(4431 起)——實質不限形式,由程式碼證。
- 「重用 _quote_rows」→ 它吃整份報告文字;本案不改它,把單句包成一行 `引句:「…」` 餵入。已寫進設計第 3 條。
- 「引句唯一強制且機器驗」→ 補出處:記帳側 --report 必附;處置閘 quote-check 零引句判失敗。
## ①
五個詞(quote-check/hay.find/finding_kinds/refute_verdicts/誠實邊界)就地定義。
## ②③
壞引用:「任意字串」精度已修;`_quote_rows` 引用補行號。矛盾 0。
## 不採信
無。
