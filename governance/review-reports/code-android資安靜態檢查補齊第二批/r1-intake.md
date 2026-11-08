# r1 收貨紀錄(code-android資安靜態檢查補齊第二批)

## 收貨

- 四席(審查甲、審查乙、架構對齊甲、架構對齊乙)全部交回後一次從逐字稿存檔;架構對齊甲第 30 行 severity 行前有縮排,report-normalize --write 只搬到行首(純格式)。
- quote-check 四份都全數錨定各自那一包;refcheck missing 0。
- 臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/ 收貨後刪。
- 拆包:整份 2248 行超過 1800,甲包(configs/,1379 行)、乙包(skills、scripts、docs,869 行)各派一位審查員與一席架構對齊。分級:pitfalls 判 light(改動沒有產品程式檔),編排者拉高到 standard(新增一條推送前會擋的規則,照第一批做法)。

## 編號與處置

編號:審查甲 sa1;審查乙 sb1–sb3;架構對齊甲 aa1;架構對齊乙 ab1–ab3(照報告順序)。全部 minor,這輪沒有 major。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| sa1 | 混合內容 setter 帶常數、getSettings()!!、apply 裡不帶接收者的常數沒有案例,拿掉 always-const 測試照綠 | HIT:改壞 always-allow 拿掉 always-const,補案例前 135 passed | 折:補 C72–C74;改壞後 149 passed 1 failed |
| sb1 | 型錄〈待查證〉〈統計〉開頭兩句仍寫由程式產生 | HIT:checks-catalog.md 兩句原文 | 折:改成手寫,並寫明由哪支測試核對 |
| sb2 | 統計核對只驗四個數 | HIT:_kt_stats_problems 只讀四處 | 折:加 _kt_stats_extra_problems(各級、規則包各等級、逐列查證、待查證三個數);六個數各改一個都翻紅 |
| sb3 | 該寫批四的列拿掉批四,自檢與新測試都不抓 | HIT:check.py 只判已含批四的列 | 折:第二批 S3 加七列通電批次必含批四;DATA-27 拿掉批四翻紅。check.py 一般化見計劃 REVISIT |
| aa1 | 弱套件那條用套件宣告排除函式庫複本,專案原本沒有 | HIT:rules*/ 對 package_header 零命中 | 放行:函式庫複本路徑不固定,ignores 的 glob 排不到;只此一條用,沒侵入共用判斷 |
| ab1 | 六條規則只驗放置、沒有實跑案例 | HIT:_KTSEC_CASES 沒有這六條 | 折:補 C75–C86 各一壞一好,形狀照 samples/;測試說明改寫 C48~C71 與 C72~C86 的分工 |
| ab2 | 新測試標 [S3][S4] 與既有測試的條款編號撞名 | HIT:t_kotlin_rulepack_security_rules 也用 S3、S4 | 折:改標 [第二批 S3]、[第二批 S4] |
| ab3 | 統計核對自己切節,check.py 也有同樣切法 | HIT:check.py catalog_problems 內的 text.find | 放行:check.py 的切法寫在 catalog_problems 內部,不是可借的函式;主表讀法照走 main_rows;鄰居 _kt_ui39_problems 同樣把判準留在測試檔 |

--refuted-set none(沒有重現不到的)。

## 先查世界

- PRIOR-ART:sa1、sb2、sb3、ab1(測試抓不到錯)——照 lumos-project-notes〈實作測試品質〉:每道判準各改壞一次要翻紅;沒有要另查的業界做法,做法沿用規則包既有 _KTSEC_CASES 逐例表與型錄自檢的重數。
- PRIOR-ART:sb1、ab2(文字誤導)——改字,沒有要查的。
- PRIOR-ART:aa1、ab3(架構)——ast-grep 規則語法有 inside source_file 的前例(rules/architecture.yml 等),不是新機制;不另抽 utils。
