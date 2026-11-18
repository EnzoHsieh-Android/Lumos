# r3 收貨紀錄

第三輪代碼審(tier high,上限最後一輪):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r3-snapshot.patch`(範圍 `6857e3d60..87093835a`),另附修補鏡頭 `r3-repair.patch`(修前 6cc9ad8c → 修後 87093835)、`r3-repair-binding.json`、`r3-behavior-cases.md`。派工詞照第二輪加了磁碟上限條款,這輪七席沒有寫滿磁碟(席位目錄收貨時 8.7GB)。

## 收貨

- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔。正確性席交回時通知說它還有自己的背景工作,核對逐字稿最後一則就是定稿報告。
- report-normalize:七份都已是正規化格式。refcheck:全對。
- quote-check:正確性、邊界、通才、合約全數錨定;資安與架構對齊是 clean 沒有引句;資源席 r1 的引句是規則檔註解,錨不到凍結快照,下面重現表機械重現。
- 圖譜鏡頭:派工鏡頭算 82 秒超過掛鉤時限,派工詞附了備份輸出位置;通才席逐條判了固定席,其餘六席照實寫沒讀備份、固定席未判定。
- 席位臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/` 收貨後已刪(刪前 lsof 確認沒有程序開著)。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| c1 g1 | 修後副本逐條拿掉 C-34 `value-used` 每個選項,各跑 `python3.14 scripts/test_lumos.py -k choice_samples_batch2`(掃描腳本在編排者 scratchpad 的 r3_mutsweep.py) | when 分支(頂層)、if/when 大括號區塊最後一個陳述、try、catch 五個選項拿掉都是 33 passed 0 failed | HIT |
| c2 | 同上,C-36、C-37 的 literal-arg 每個選項兩份一起拿掉,帶號運算元清單每種兩份一起拿掉 | boolean、null、integer、real、long、hex、bin、unsigned 八種字面值與帶號 long、hex、bin、unsigned 四種拿掉都是 33 passed 0 failed(席位只點到帶號四種) | HIT |
| b1 | `kp.choice_tables` 餵 `已撤列號:C-４０`、`C-040`、`C-４0`,表裡有 C-40 | 三種都回 `[]`(撤號守衛靜默漏擋) | HIT |
| c3 | `ast-grep scan` 修前 6cc9ad8c 與修後 87093835 的 api.yml 掃 `LaunchedEffect(-(1))`、`(-(-1))`、`((1))` | 兩版三行都命中 C-36 | HIT |
| r1 | 每層都帶尾隨 lambda 的 `remember(k, remember(k, …) { 1 }) { 1 }`,修前修後兩版 api.yml 各掃 | 300 層 3,760,378 位元組、1000 層 39,846,294 位元組,兩版逐位元組相同 | HIT |
| k1 | 讀 `skills/kotlin-idioms/checks-catalog.md` 的 C-34 列 | 判法欄寫「同 sbr.yml 的 value-pos」,實際 C-34 另排除分支位置 | HIT |
| k2 | 讀 `Verification/2026-11-17_選擇點第二批上線前實測` 開頭 | `valid_under` 釘 11-17 版規則、`revalidate_when` 只列加列撤列,11-18 修補改了判法 | HIT |

## 分組

1. **規則子句沒有樣本守住**(c1 major、c2 major、g1):C-34 值位置的五個選項與 C-36/C-37 字面值清單十二種,拿掉都不會讓樣本測試翻紅。c1(catch 區塊的 value-direct)與 c2(帶號運算元清單)是上一輪修補新寫的子句,修補時只補了誤命中那幾行的樣本;g1 與其餘字面值是第一版就沒有。C-34 這一組連三輪都出現(r1 c1、r2 g1、r3 c1)。
2. **撤號列號的數字寫法**(b1):`\d` 收全形數字、前導零跟表裡列號字串比不上,原有漏查。
3. **括號包住的常數 key**(c3):原有,修前修後同結果。
4. **引數巢狀輸出平方**(r1):原有,修前修後逐位元組相同。
5. **文件**(k1、k2):k1 原有(第一輪排除分支時就沒跟);k2 是上一輪修補改了判法、實測筆記的有效範圍沒跟。

## 先查世界

- 第 1 組:PRIOR-ART: 靜態分析規則的測試慣例是每個排除條件各寫一行「不該命中」、正面樣式寫「該命中」(Semgrep 規則測試的 `ok:` 與 `ruleid:` 標注,https://semgrep.dev/docs/writing-rules/testing-rules );變異分析把「注入的缺陷測試抓不到」當成測試不夠的判準(https://www.fuzzingbook.org/html/MutationAnalysis.html )。採用:規則每個子句與字面值清單每一項各有一行樣本,拿掉任何一項都要有一行翻紅;用逐條拿掉的掃描驗收,不新增測試機制。查詢詞:semgrep rule testing ruleid ok annotations;mutation testing static analysis rules test suite adequacy。
  方向:對 — 判法照舊只看語法(這一輪三席實跑的值位置與字面值行為都對),缺的是每條子句有沒有樣本守住;Semgrep 的規則測試與變異分析的充分性判準都是同一個形狀(來源同上兩個網址)。
- 第 2 組:PRIOR-ART: Python `re` 文件寫明 `\d` 在 str 樣式比對任何 Unicode 十進位數字(https://docs.python.org/3/library/re.html#regular-expression-syntax );改成 `C-[1-9][0-9]*`,其他寫法留下殘字、照既有路徑報看不懂。
- 第 3 組:同第一版與第二輪「不確定就不收」的反面:不遞迴拆括號(字面判法越補越多),等價存活靠放行承接;寫進計劃〈實務隱患〉。
- 第 4 組:計劃〈實務隱患〉已寫明平方成長靠 64MB 上限落成驗不了只提醒,這一筆數字補進同一段。
- 第 5 組:文件,不需外部依據。

## 處置

| id | 去向 | 種類 | 改了哪裡 |
|---|---|---|---|
| c1 c2 g1 | 折 | code | 樣本 choice-batch2.kt 補 C-34 五行 HIT(when 值、if 與 when 大括號區塊最後一個陳述、try、catch)與一行 MISS(if 底下 try 的 catch 區塊),C-36 補十二行 MISS(八種字面值、帶號 long/hex/bin/unsigned);逐條拿掉掃描 24 項全部翻紅、原樣 33 passed |
| b1 | 折 | code | check.py `_choice_retired` 列號改認 `C-[1-9][0-9]*`;`t_choice_table_batch2` 補全形數字、前導零、全形混半形三案例(修前紅 3 條、修後 16 passed) |
| k1 | 折 | spec | 型錄 C-34 判法欄改寫成「value-pos 再排除外層掛在分支底下的位置」 |
| k2 | 折 | spec | 實測筆記 `valid_under` 寫明修補改了判法、沒有重量;`revalidate_when` 改成規則判法改動也要重驗 |
| c3 | 放行 | code | 原有、修前修後同結果;括號包常數是罕見寫法,落成等價存活放行一次;寫進計劃〈實務隱患〉等價存活那一條 |
| r1 | 放行 | code | 原有、修前修後逐位元組相同;約 1300 層才超過上限,真實專案最大檔 1.1MB 碰不到;寫進計劃〈實務隱患〉掃描那一條 |

修補因果:c1、c2 是上一輪修補新寫的子句沒有樣本守住(行為正確、守衛缺),k2 是上一輪修補改了判法而筆記沒跟,記為回歸;其餘原有。
