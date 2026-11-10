severity: minor

這份 diff 的結構跟鄰居一致:規則排除寫法照 `kt-register-without-unregister`、逐例表接在 C226 後面、WHY 行格式照鄰居。沒有第二種做法,也沒有跨層直呼,但有 5 條格式與命名上的不一致。

## 1. 預期值表「代碼審補」三列的條款欄不符工具既有格式,另有一格來源太短
severity: minor
blocking: 否
引句:「| S1 代碼審補 | `LifecycleService` 子類別裡用 ProcessLifecycleOwner 收(C236) | 不報 | 範圍 1:外圍是 Service 時一律不報 |」
- 鄰居:`docs/lumos-toolchain-knowledge/Projects/Android形狀列補規則_計劃.md:123` 起的〈預期值表〉,條款欄只寫 `S2` 這類編號,「代碼審補」之類的說明寫在來源欄。
- 工具對這格有規定:`scripts/lumos:14592` 的 `_expected_row_probs` 要求條款欄寫成 S 加數字,來源格至少 4 個字。
- 重現:對 17 篇有〈預期值表〉的計劃共 329 列掃條款欄,只有這份的 3 列不符,命令是用 python 逐列比對 `S[1-9]\d*`。
- 再用 `python3.14` 載入 `scripts/lumos`,對這份計劃呼叫 `_expected_table(text, {"S1","S4"}, set(), {"S1","S4"})`,輸出:
  - `第 66 行:條款欄要寫成 S 加不以 0 開頭的數字(例 S3,不加方括號),現在是 'S1 代碼審補'`(第 67、68 行同)
  - `第 61 行:來源格至少 4 個字(這個預期從哪條需求來)`,對應 C229 那列,來源只寫「同上」2 個字。
- 這份計劃目前判風險低(四類已排除、沒有 `risk/` 標籤、沒有關鍵字命中),所以表不會被擋。日後改判高風險,這 4 處會讓推送前的預期值表檢查不過。

## 2. 〈審計修正紀錄〉放在〈回退〉與〈天花板〉前面
severity: minor
blocking: 否
引句:「r1(2026-11-09,4 席):45 條/blocking 13/整份從四件縮成兩件,另兩件移到新計劃。」
- 鄰居:`docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第三批_計劃.md:141,145,161` 的順序是回退、天花板、審計修正紀錄。`Android形狀列補規則_計劃.md:167,177,189` 同。
- 重現:掃 `Projects/*.md` 中同時有三節的 39 篇,38 篇審計修正紀錄在最後,只有這份把它放在回退與天花板之前。
- 這份新計劃的順序是驗收條款、預期值表、審計修正紀錄、回退、天花板。

## 3. 代碼審輪次標籤寫成「-std r1」,鄰居寫「std r1」
severity: minor
blocking: 否
引句:「代碼審 -std r1(2026-11-09,2 席):9 條/blocking 1/」
- 鄰居:`scripts/test_lumos.py:31274`「(代碼審 std r2:…」、`scripts/test_lumos.py:49662`「(代碼審 std r1)」、`docs/lumos-toolchain-knowledge/Projects/測試總檔預設切片_計劃.md:83`「代碼審 std r1」。
- 帶連字號的 `-std` 是迴圈 id 的後綴(例如 `改開 -std`),不是輪次標籤。
- 這份 diff 在三處都用了「-std r1」:計劃的審計修正紀錄、預期值表那列「代碼審 r1、-std r1 補的覆蓋」、`scripts/test_lumos.py:127247` 與 `:127337` 的註解。

## 4. 兩篇新 todo 計劃的席發現編號用字母簡寫,指向的檔案裡查不到
severity: minor
blocking: 否
引句:「合併主線、空樹起點、壞編碼訊息、壓提交都會讓標記失效或誤升(r1 c1、c2、b1、b2、b3、i13)」
- 鄰居:`docs/lumos-toolchain-knowledge/Projects/規則包語意覆核級命中走盲判_計劃.md:113` 寫「解 r2 整合 6、架構對齊 5」,也就是輪次加席名加編號,指到的席報告能直接對上。
- 新計劃的 `c1`、`b1`、`i13` 是收貨紀錄的流水號,對照表在 `governance/review-reports/簡報審查抓到的機制缺口/r2-intake.md:5`(「編號:正確性 c1–c11、邊界 b1–b9、…」)。
- 但計劃寫的是「原文在 … 的 r1、r2 席報告」。席報告本身是各席自己的編號,例如 `r2-正確性-sonnet.md:7` 是「**1. …」,找不到 `c1`。
- 這個寫法出現在 `人工指定高風險路徑_計劃.md` 與 `行內忽略註解要留紀錄_計劃.md` 的〈審查帶過來的問題〉節。

## 5. 壞例樣本帶圖譜連結,註解也沒用鄰居的 `case:` 形式
severity: minor
blocking: 否
引句:「例外只看類別自己的繼承清單;Activity 裡另有內部 Service 時 Activity 自己的收集照報([[Projects/簡報審查抓到的機制缺口_計劃]] 預期值表)」
- 重現:在 `configs/ast-grep/kotlin-android/samples` 底下搜 `\[\[`,只有 `bad/kt-lifecycle-collect-without-repeat/.../kt-lifecycle-collect-without-repeat.kt:29` 這一處。規則檔與 `check.py` 有這種連結,樣本檔沒有。
- 鄰居:`samples/bad/kt-livedata-setvalue-background/.../kt-livedata-setvalue-background.kt:3,5,7,9` 用 `// case: <slug>` 標每一段,後來補的例子寫「代碼審 rN(規則X Finding N):…」。這份新增的三段都沒帶 `case:` 標籤或審查輪次出處。
- 這則註解說「Activity 裡另有內部 Service」,但同一段 `MainActivity` 裡沒有內部 Service,註解描述的情形樣本沒有呈現(內部 Service 那一例只在 C233)。

## 三問

**1. 分層與依賴方向**
- 對齊,只有 finding 5 的註解連結。
- 規則設定:`rules/state.yml:176` 起的排除段,形狀同 `rules/architecture.yml:287-300`,都是 `not: inside: class_declaration` 加 `has: delegation_specifier`、`regex`、`stopBy: end`。
- 樣本:新例子附加在既有的壞例與好例檔裡,沒有新檔。
- 測試:C227~C239 接在 `scripts/test_lumos.py` 的 C226 後面,整檔本體加第五欄,格式同 C157、C224。
- 型錄:STATE-5 名稱欄加括號說明,鄰居有先例(CO-31「(目標含 JS 或 Wasm 時)」、FLOW-7)。
- 圖譜:WHY 行放在 `Systems/kotlin規則包.md` 的摘要區,欄位 `[出處:][因:][不選:][test:]` 齊全。
- 沒有跨層直呼。

**2. 命名與錯誤處理**
- 規則 id、測試名、樣本檔名、筆記檔名(`<主題>_計劃`)、摘要行前綴(`WHY:`、`FLAG:TECHNICAL`、`PITFALL:` 加三個必有鍵)都跟鄰居一致。
- 逐例表編號連號,表頭註解有分開標「預期值表逐列」與「代碼審補」,行號期望值我逐列對過程式碼,都對。
- 不一致處是 finding 1、2、3、4。
- 錯誤處理這次沒有新增。

**3. 第二種做法**
- 已讀,無 finding。
- ⚠ 超類別名比對:新規則錨定 `^` 且只收固定的名字,所以自寫的 `BaseLifecycleService(` 不放行(C235)。`architecture.yml:298` 的 `^(\w+\.)*\w*Application\(` 與 `perf.yml` 的 `ViewModel\(` 是寬鬆比對。`data.yml:88` 的 `^(okhttp3\.)?(Interceptor|Authenticator)$` 是精確比對。鄰居本身兩種都有,計劃〈天花板〉也寫明了,所以不列 finding,交編排者知悉。
- 表態記錄涉及的檔案與現況不符:它說這次改到「規則包自我檢查、主程式的設定讀法與訊息顯示」,但 `r2-pack.patch` 的 12 個檔裡沒有 `check.py` 或 `scripts/lumos`,Python 只動了 `scripts/test_lumos.py` 的資料列與 docstring。該記錄綁的是 cbafb2f9,不是目前版本。各題答「na」的結論不受影響。

不對齊共 5 條,其中 major 0 條

臨時檔我只在 session scratchpad 放過一支探針腳本,已用字面絕對路徑刪除。repo 沒有被我改動,`git status` 與開始時一致。
