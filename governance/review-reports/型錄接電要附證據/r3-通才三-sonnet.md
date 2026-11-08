severity: major

我只讀了兩份收貨紀錄、快照和真碼,沒跑測試。r2 折入的八項大致都進了快照,也沒看到新的互相矛盾。但我用 python3.14 載入 `check.py` 實跑了一遍候選列,發現第 1 條:有一批列照字面寫不出合格的〔真跑〕出處。

1. 31 列(168 個候選列中的 12 列加 19 列)的壞寫法欄沒有可抄的程式例子,〔真跑〕的出處驗證不可能過
severity: major
blocking: 是
失敗場景:
- 輸入:實作者照範圍 2 替 UI-44 寫樣本。UI-44 的壞寫法欄是「只讀 CompositionLocal 的小函式沒標」,沒有反引號。
- 預期:UI-44 有合格的〔真跑〕判定。
- 實際:
  - 範圍 2 說例子那一行不准改,但這欄沒有例子可抄。
  - 範圍 3 要求樣本含壞寫法欄「至少一段反引號內的原文」,這欄沒有反引號,驗證一定報錯。
  - 退路〔查證〕只限「樣本編不過」。UI-44 的樣本其實編得過,實作者只能寫假理由,或改成原文整段不含這列的壞例。
- 範圍:我實跑 `main_rows`,168 個候選列裡 12 列完全沒有反引號:UI-44、UI-45、UI-46、UI-64、UI-84、UI-86、UI-88、UI-92、UI-95、ARCH-81、ARCH-84、DATA-50。UI-92 的反引號在標準寫法欄,壞寫法欄沒有。
- 另有 19 列的反引號段全是帶「…」的佔位。例如 API-1 的 `val a = x.f(…)` 照抄編不過,又不准改那一行,只能走〔查證〕。
- 後果:這 31 列(約 18%)的真跑樣本不是不可能,就是靠假的「樣本編不過」理由。這等於把計劃要擺脫的「讀頁判定」大量放回去,而且〈天花板〉的準確率承認寫的是「實作後補」。
- 計劃要補的地方:壞寫法欄沒有可抄原文的列,規定樣本怎麼來(例如改從標準寫法欄反推,或允許自擬並另標一種出處),自檢怎麼驗。
引句:「例子那一行本身不准改」
引句:「內容要含壞寫法欄裡至少一段反引號內的原文」
佐證:file: `skills/kotlin-idioms/checks-catalog.md:371`(UI-44);file: `skills/kotlin-idioms/checks-catalog.md:419`(UI-92);file: `skills/kotlin-idioms/checks-catalog.md:589`(DATA-50);file: `skills/kotlin-idioms/checks-catalog.md:153`(API-1 的「…」佔位)

2. 168 列與「現在宣稱批四」的 223 列對不上,55 列舊寫法「批四(現成規則)」沒有明說怎麼處理
severity: minor
blocking: 否
為什麼標 minor:新比對遲早會把這 55 列點出來,實作者被迫自己裁,不會悄悄漏掉;但計劃沒寫,會各做各的。
- 實測:型錄有 223 列含「批四(」,其中 168 列有候選。
- 另 55 列是「批四(現成規則)」,例如 API-3、FLOW-5,沒有任何候選。〈輸入與口徑〉定義這個值是「其餘照舊」,是合法的未接值。
- 範圍 3 寫新比對是「每列該寫的批四標籤 = 該列判定擋得到的標籤」。這 55 列沒有判定,該寫的標籤是空,實際寫「現成規則」。
- 計劃沒寫:新比對是否容許「現成規則」?還是要把這 55 列也改成「未接」?S3 的「原宣稱接電列」是否包含它們?
引句:「只動現在宣稱批四的列」
佐證:file: `configs/ast-grep/kotlin-android/check.py:344`(`_batch4_problems` 只比標籤,對「批四(現成規則)」不報);file: `skills/kotlin-idioms/checks-catalog.md:155`(API-3 的舊值)

3. 一個標籤對應多筆檢查時,「擋得到」怎麼彙總沒寫
severity: minor
blocking: 否
為什麼標 minor:合理的讀法(任一擋得到)只有一種,多數實作者會選對。
- 場景:一列的 Android Lint 段有兩個規則碼,一個擋得到、一個擋不到。
- 計劃只說「每列該寫的批四標籤 = 該列判定擋得到的標籤」,沒說是「任一擋得到」還是「全部」。
- 另外,compose-rules 的「檢查」欄要寫 kebab(`lambda-param-in-effect`)還是 Pascal(`LambdaParameterInRestartableEffect`)也沒定。`_B4_CR` 現在只抽 kebab,但 detekt 報告出來的是 Pascal。
引句:「每列該寫的批四標籤 = 該列判定擋得到的標籤」
佐證:file: `configs/ast-grep/kotlin-android/check.py:107`(`_B4_CR` 只抽 kebab);file: `configs/ast-grep/kotlin-android/check.py:124`(`batch4_expected_tags` 只回標籤、不回(標籤,規則碼),候選要自己重寫抽取)

4. 驗收條款沒覆蓋範圍 3 列的幾項自檢
severity: minor
blocking: 否
為什麼標 minor:這是測試覆蓋缺口,不是會做錯的行為。
- 範圍 3 要求「真跑環境:」那一行要在、格式對,判定的編號不在主表要報,〔查證〕的理由要以「樣本編不過」開頭。
- 預期值表和 S2 都沒有對應的改壞案例。
- 實作者可能漏寫這幾道檢查,而全部測試照綠。
引句:「型錄自檢 應 各報一個以〈接電證據〉開頭、指名那一列的問題」
佐證:file: `scripts/test_lumos.py:129128`(`t_kt_catalog_batch4_wiring` 的改壞模式是逐項改壞後要求報,新測試應照辦)

最高等級 major;blocking 1 條
