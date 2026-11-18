# r6 收貨紀錄

第六輪代碼審(tier high,上限三輪跑滿後人裁第三次加開的一輪,cap-decision extra-round 與更新後的跑滿回顧在第五輪帳本提交):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r6-snapshot.patch`(範圍 `6857e3d60..8333987ac`,1881 行,資安席整份、不拆),另附修補鏡頭 `r6-repair.patch`(修前 c261a154 → 修後 8333987a)、`r6-repair-binding.json`、`r6-behavior-cases.md`。派工詞只放標記行加一句「先讀完 scratchpad 裡自己那份完整派工詞照做」,完整派工詞由 mk_b2_seats_r6.py 產生;七席都照完整派工詞的格式交回。

## 收貨

- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔。
- report-normalize:七份都已是正規化格式。quote-check:通才席唯一一句引句對 `r6-snapshot.patch` 與 `r6-repair-docs.patch` 錨定;其餘六席 clean、沒有引句。refcheck:通才席一處 missing 是它寫明沒核對的 `governance/residual-index.json`,只是提到檔名、不拿來當證據。seat-check:派工單材料欄沿用前幾輪格式,工具判 vacuous 豁免。
- 記帳材料:正確性、邊界兩席派工材料是 `r6-repair-code.patch` 加 `r6-repair-tests.patch`(177 行),記帳 `--snapshot` 填兩份原樣串接的 `r6-repair-codetests.patch`(材料腳本凍結時就產生)。通才席派工材料另含計劃筆記,它的引句引的是這次計劃改動那一句,記帳 `--snapshot` 填 `r6-repair-generalist.patch`(`r6-repair-codetests.patch` 後面原樣接 `r6-repair-docs.patch`,204 行,內容不增不減)。通才席是唯一有引句的一席,當載體。
- 圖譜鏡頭:鏡頭備份 `lens-r6.txt` 派工前同步產生完畢(83 秒,超過掛鉤 45 秒時限,派工詞尾端沒附上鏡頭)。通才、邊界、合約、正確性四席依修補沒碰 `scripts/lumos` 逐條判固定席不影響;資源、架構對齊、資安三席沒讀備份,依改動只有規則、樣本與測試判不影響。殘留段因鏡頭逾時算不出來,通才、邊界、合約三席照實寫未判定;`governance/residual-index.json` 在範圍內沒有改動(編排者 `git diff --stat 6857e3d60..8333987ac -- governance/residual-index.json` 空)。
- 席位臨時目錄:正確性、邊界、通才、資源、合約、架構對齊自己刪了;資安席留下空目錄,收貨後由編排者刪(刪前 lsof)。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| g1 | 探針 `g1.kt`(標註加字串、true、null、字元、數字、負數,`!true`、`-(1)`,不帶標註的 `"s"`、`true`),兩版 api.yml(c261a154、8333987a)各 `ast-grep scan -r` 一次 | 修前 C-36 命中第 3–10 行;修後命中第 3–6、8–10 行。標註加數字(第 7 行)修後不命中;標註加字串、true、null、字元(第 3–6 行)兩版都命中;`@Suppress("x") -1`、`!true`、`-(1)` 兩版都命中;不帶標註的字面值兩版都不命中 | HIT |

## 處置

| id | 去向 | 種類 | 理由 |
|---|---|---|---|
| g1 | 放行 | code | 標註加非數字常數(及 `@Suppress("x") -1`、`!true`、`-(1)`)當選擇點,後果只是多產一個必然等價的壞法(雜訊),守衛不失效、不漏報;在常數引數前加標註的寫法實務上幾乎不出現;兩版行為相同,不是修補造成;第三輪已用同樣理由放行同類的「括號包住的常數 key 照樣命中」。這輪七席沒有 major,依規放行 minor 附理由 |

## 先查世界

- g1:放行、不修,不需外部依據;判法沿用「只看語法樹節點種類」的既有形狀(第五輪〈先查世界〉的 Stryker、TCE 依據)。

修補因果:g1 兩版同結果,原有;本輪無回歸。
