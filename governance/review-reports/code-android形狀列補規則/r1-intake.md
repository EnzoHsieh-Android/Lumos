# r1 收貨紀錄(code-android形狀列補規則)

## 收貨

- standard 分級:一席正確性、一席架構對齊。第一位正確性席從 02:30 起兩小時沒有任何輸出(卡在沒設逾時的指令),停掉後重派同名席,派工詞加「每個指令設逾時、40 分鐘內交回」;卡住那位沒留下 repo 改動或殘留程序,臨時目錄刪掉。
- 兩席交回後從逐字稿原樣存檔。正確性席最後一行「severity: major(最高)」用 report-normalize --write 搬成獨立一行(只搬格式)。quote-check 兩份全數錨定,refcheck 全部對得上。
- 臨時目錄 /tmp/lumos-seat-work/code-android形狀列補規則/ 收貨後刪除。

## 編號與處置

編號照報告順序:正確性 s1–s5、架構對齊 c1–c6。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| s1 | ARCH-62 的 fromFragment、fromView 元件對應改壞,逐例表與樣本照綠 | HIT:複本把 FragmentComponent 改名、fromView 拿掉 ViewComponent,原版不報的兩處變成報,測試照綠 | 折:補 C153(fromFragment 配 FragmentComponent 不報)、C154(fromView 配 ViewComponent 不報)、C155(fromView 配 Singleton 報),三種改壞各自翻紅 |
| s2 | 多行 `@InstallIn(` 的正確寫法被誤報 | HIT:自造多行輸入被報 | 折:四支正規式的 `.*` 改成 `[\s\S]*`,補 C156;改回 `.*` 翻紅 |
| s3 | 搬到會擋的 map 那條會擋 Flow 的 map、Task;`.asFlow().map` 可直接排除 | HIT:量測時 2 處誤報就是 `.asFlow().map` | 折:加限制「接收者不以 .asFlow() 結尾」,補 C157;只會少報,不影響升級判斷。Flow 型別的變數與 Task 單檔看不出,照天花板 |
| s4 | 型錄 API-2 實測欄還寫已刪掉的 review-fp 樣本 | HIT:樣本目錄沒有那支檔 | 折:改寫 |
| s5 | 測試說明的編號範圍寫 C127~C148,實際到 C152 | HIT | 折:改成 C127~C157 並補新例的改壞對照 |
| c1 | 測試另寫一套型錄主表讀法,圖譜寫明只有 main_rows 一條 | HIT:新碼用 split("\|"),反引號裡的直線會錯位 | 折:改用 m.main_rows() 的第 5 欄 |
| c2 | 規則頂端註解日期在前、不接閘沒寫原因、規則本體夾過程紀錄 | HIT:對照 rules/api.yml 既有註解 | 折:照鄰居寫成「計劃連結 範圍:會擋/不接閘(數字)」,拿掉過程紀錄 |
| c3 | 逐例表編號沒照順序;S3 標籤從「報一次/不報」改成「報 n 次」 | HIT | 折:照編號重排;標籤保留「報 n 次」(C135 要報兩次,原標籤會寫錯),寫在這裡 |
| c4 | scan 依旗標回兩種長度的 tuple | HIT | 折:一律回三元組,check.py 兩個呼叫端跟著多解一個值 |
| c5 | 逐例表選填欄用 dict,_KTSEC_PLACE 用位置欄 | HIT | 折:改成位置欄,值是預期行號,有這欄就表示完整 kt 檔 |
| c6 | rules-unwired/api.yml 檔尾換行被拿掉 | HIT | 折:補回,檔案跟主線一樣 |

--refuted-set none。

## 出處清單(修前列齊同一問題的全部出處)

- s1、s2(ARCH-62 的對應與比對):規則四個分支(fromApplication、fromActivity、fromFragment、fromView)各自的元件正規式;逐例表 C140~C147、C152~C156;好例樣本;型錄 ARCH-62 情境欄;計劃預期值表。四支正規式一起改成跨行。
- s3(map 那條的誤報):rules/api.yml 規則;型錄 API-2 實測欄;計劃量測結果、天花板、REVISIT。
- c1(型錄讀法):全測試檔搜 `split("|")` 讀型錄主表的地方,只有這次新加的一處;其他都走 main_rows。
- c4(scan 回傳):check.py 內 scan 的呼叫端共兩處(樣本自測、祖先目錄叫 test 的樣本),測試一處;scripts/lumos 沒有呼叫。

## 先查世界

- PRIOR-ART:s2——ast-grep 的 regex 是 Rust regex,`.` 預設不匹配換行(Rust regex 文件);改用 `[\s\S]` 不靠旗標。
- PRIOR-ART:s3——量測判讀已確認 `.asFlow().map` 是誤報類;ast-grep 的 constraints 對單一 meta 變數加 not regex 是官方寫法(rule-config 文件),不另寫規則。
- PRIOR-ART:c1、c4——照專案既有單一讀法與單一回傳形狀,不另查。

## 驗證

- 修前:C156、C157 紅(多行 @InstallIn、asFlow 被報);C153~C155 原本就綠,是給改壞用的。
- 修後:kotlin_ 子集 719 項全過;規則包自測 0 問題;十九道改壞逐一翻紅後還原(含這輪新加的 fromFragment、fromView 各兩道、跨行、asFlow)。
