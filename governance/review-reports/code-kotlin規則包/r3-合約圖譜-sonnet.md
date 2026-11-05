severity: minor

審查席:合約圖譜(sonnet),第 3 輪(末輪驗收),範圍是 `r3-pack-docs.patch`。我沒有改 repo 工作樹裡的任何檔。

**程式實數核對(全部對得上)**
- 規則包 207 條:`rules/` 147(error 30、warning 117)、`rules-review/` 10(info)、`rules-hints/` 50(hint)。統計節寫的「207(error 30、warning 117、語意覆核級 info 10、hint 50)」全中。
- 型錄 473 列(473 個不同編號)。出處不全的列用程式數是 29,與統計節和母計劃實作紀錄寫的 29 一致。
- 「被會擋的規則守到的列數」我用「通電批次欄含告警帶寫法=批一、且不是只有提示級」的口徑數,得 130,與 diff 的 130 一致。
- 型錄、筆記裡所有 `kt-` 規則 id:
  - 對照規則包的 id 都存在。
  - 對不上的只有 `kt-register-pair-missing`、`kt-viewmodel-depends-on-api-dao`(型錄 ARCH-35、ARCH-49 的「已併入」說明)。
  - 還有 `kt-situation`、`kt-springdata` 等棧別題名。這些都不是規則包規則。

**r2 的 6 條修補檢查**
1. 計劃檔尾的工具呼叫殘渣:已刪。`規則包語意覆核級命中走盲判_計劃.md` 現在結尾乾淨,最後是正常的 `\n`。
2. 出處不全 28 改 29:統計節與母計劃都已更新,並註明以型錄統計節為準。
3. 母計劃與 `check.py` 的語意覆核級描述:兩處都改指新計劃,與第三批計劃的「不做」一致。
4. `Systems/kotlin規則包` 檔案清單漏了 `rules-review/`:已補。`check.py` 的「一條規則都沒讀到」訊息也已列三個目錄。
5. API-1 還寫 semgrep:已改成 ast-grep 規則 `kt-sequential-independent-await`。
6. 通電批次取值:〈輸入與口徑〉已定義「語意覆核級」。STATE-1、STATE-7、STATE-16、TEST-5 的實測欄都已標出覆核級。

**搬到語意覆核級的規則,仍有兩處沒標**
(這 10 條規則都在 `rules-review/` 且各有 `review-fp-` 好例。)

severity: minor
blocking: 否
引句:「規則 kt-statein-eagerly:樣本實測中壞例、好例不報(規則包沒有它專屬的好例,其他組好例都不報)」
型錄 STATE-4 列(diff 裡是未改動的上下文行)把 `kt-statein-eagerly` 和另外兩條會擋的規則並列。通電批次寫「告警帶寫法=批一」,實測欄沒說它已搬到語意覆核級。
- `kt-statein-eagerly` 在 `rules-review/state.yml`,是 info。
- 它的好例目錄有 `review-fp-reason-above-property.kt`,所以「規則包沒有它專屬的好例」與實況不符。
- 讀這列的人會以為用 Eagerly 會被擋,實際上同列另兩條才擋。
- 其他覆核級列(API-11、STATE-1、STATE-7、STATE-16、TEST-5)都有補註,這一列漏了。

severity: minor
blocking: 否
引句:「規則 kt-bg-dispatcher-touches-view:樣本實測中壞例、好例不報」
CO-44 與 DATA-36 這輪把通電批次改成「語意覆核級」,但實測欄沒有補「這列有規則在語意覆核級」那句。
- DATA-36 的 `kt-worker-retry-unbounded` 在 `rules-review/data.yml`。
- 好例目錄有 `review-fp-attempt-in-variable.kt`、`review-fp-main-dispatcher-variants.kt`,是故意會命中的。
- 兩列的實測欄寫「好例不報」,字面與實況相反。r2 對 STATE-1、STATE-7、STATE-16 提過同一類,這輪只補了那幾列。
- 影響只是措辭,通電批次欄已正確,不會讓人誤以為會擋。

總結:數字(207 條、守到 130、出處不全 29、473 列)全部與程式實數吻合,r2 的 6 條修補到位。剩下只有 STATE-4、CO-44、DATA-36 三列的覆核級標註還沒補齊,是措辭問題,不影響推送。
