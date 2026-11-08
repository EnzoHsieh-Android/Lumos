# r3 收貨紀錄(code-android形狀列補規則)

## 收貨

- 兩席(正確性三、架構對齊三)交回後從逐字稿原樣存檔;兩份都已是正規化格式,quote-check 全數錨定。收貨時 git status 沒有席位造成的 repo 改動;臨時目錄 /tmp/lumos-seat-work/code-android形狀列補規則/ 刪除。

## 編號與處置

編號照報告順序:正確性三 s1–s5、架構對齊三 a1。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| s1 | ARCH-59 的「同型別」($T)與同檔限定詞($Q)綁定拿掉照綠 | HIT:結構列舉 B 類解開綁定沒紅 | 折:補型別不同、同檔有 @Qualifier 但另一個註解不是限定詞兩例,列舉後全紅 |
| s2 | ARCH-62 的 $I 連結、元件名字邊界、stopBy 拿掉照綠 | HIT:結構列舉 B、C、D 類沒紅 | 折:補同檔兩個 entry point、名字含別的元件名、自訂元件、巢狀 entry point 各例 |
| s3 | ARCH-59 的 \w+Key 會把同檔宣告的 @ApiKey 限定詞當成多重綁定,漏報 | HIT:席位實跑、C188 修前會紅 | 折:改成只認 Dagger 內建 StringKey、IntKey、LongKey、ClassKey、LazyClassKey,補 C188 與 C218~C221 |
| s4 | 共用註冊判斷的 ^ $ 錨點拿掉照綠 | HIT:同上 | 折:補 unregisterReceiver、subscribeOn、setOnClick、addListenerCount 四例 |
| s5 | API-2 的 `ds?.map { it.await() }` 不報 | HIT:席位實跑 | 折:寫進計劃〈天花板〉(漏報,不擴大已量過誤報的形狀) |
| a1 | ARCH-59 放 rules/ 的 warning,卻寫成「只列出不擋」 | HIT:查新增告警閘程式,擋不擋看規則放哪個目錄,不看等級 | 折:更正錯誤前提,規格、規則註解、型錄、規則包節點都改成會擋;建議語氣的規則改成放 rules-hints/ |

--refuted-set none。

## 換形狀(同一類第三輪被打穿)

r1、r2、r3 都是「規則某個條件沒有例子守,改壞照綠」。r2 只列舉了 `- pattern:` 行與正規式 `|` 選項;這輪照第一點先上網查(ast-grep 官方規則測試寫法:每條規則寫該報與不該報的例子;變異測試的標準算子:PIT、Stryker 的拿掉條件、反轉條件),把列舉擴到四類共 102 項(`sweep2.py.txt`):A 拿掉 has/not/inside、B 解開變數綁定、C 拿掉正規式的 \b ^ $ \A \z、D 拿掉 stopBy: end。

- 第一次跑(`r3-sweep2-before.txt`):沒紅 23、標成無效 48。無效的判法有錯:ast-grep 掃到 error 等級告警時錯誤輸出一定印「Error: N error(s) found」,被當成載入失敗;改成只認「規則解析失敗」重判(`r3-sweep2-recheck.txt`):真的載入不了 8、其實有抓到 40。
- 沒紅的 23 項裡 7 項是等價改壞:都是拿掉註解比對開頭的 ^,註解文字本來就從 @ 開始,拿掉行為不變。其餘 16 項補 C202~C217。
- 補例後重跑沒紅的 23 項(`r3-sweep2-after.txt`):16 項全紅,只剩那 7 項等價改壞。
- 多重綁定清單改成五個 Key 後補 C218~C221,用 r2 的列舉程式只跑那一行:8 個選項拿掉全紅。
- 列舉範圍的天花板:只做刪除與放寬兩類算子,沒做反轉(例如把 not 換成 has)與換成相鄰值。

## 先查世界

- PRIOR-ART:ast-grep 官方規則測試 https://ast-grep.github.io/guide/test-rule.html (valid/invalid 例子);PIT 變異算子 https://pitest.org/quickstart/mutators (拿掉條件、反轉條件、邊界)。採用:用變異算子的思路逐項改壞規則條件;不採用整套工具:規則是 YAML,現成變異工具不認。
- PRIOR-ART:a1——讀 scripts/lumos 的新增告警閘解析,沒有依等級過濾;規則包節點寫明 rules/ 的 error 與 warning 都擋。

## 驗證

- kotlin_ 子集 847 項全過;規則包自測 0 問題。
