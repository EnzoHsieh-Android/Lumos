# code-否決提案收齊查重 r3 收貨紀錄

- 凍結材料:r3-snapshot.patch(範圍 6467401a7012bb39acb3d5be064bb88758f45818..25ee639ccdca91ec47f305913fc0596c6a2706e3,排除帳本 jsonl 與 governance/ 卷證);修補差異 r3-repair.patch(09ffec28 → 25ee639c),來源 r3-repair-binding.json(r2 fix-check 通過的輸出存為 r2-fix-check.txt)。
- 席位:正確性r3-sonnet(找問題席)、架構對齊r3-sonnet(不算人數),全新代理,派工詞明寫不讀 r1、r2 卷證。
- 兩席收齊後才一次寫進卷證(從逐字稿取最後一則回答);`git status` 只多卷證檔與兩本帳;`git reflog -1` 最新仍是 25ee639c。
- 收貨:正確性席 quote-check 2/2 全錨、refcheck 5 ok;架構對齊席 0 條不對齊(clean),報告沒有引句,quote-check 印「抽不到引句」——它沒有發現可錨,不採用為載體席;refcheck 4 ok。架構對齊席交的 ⚠(作廢 WHY 行裡的不選要不要列):照列,跟被翻案的決策整段列出同一個口徑,屬歷史否決紀錄,讀的人自己判;不算發現。
- finding ID:正確性席 F1–F2 記為 r3c1–r3c2。本輪最高 minor。

## 重現表

| id | 編排者重現 | 結果 | 採信 |
|---|---|---|---|
| r3c1 | 臨時庫決策 `翻案:原本不做X,現在改做`:25ee639c 列出 `Projects/p.md#d3`;09ffec28 版不列 | HIT | 採信;歸因修復回歸(r2 改成逐子句,冒號是切點);放行 |
| r3c2 | 臨時庫決策 `content: |` 兩行、第二行才有「不做」:三個版本都只印 `Projects/p.md#d4: 第一行普通說明` | HIT | 採信;歸因原有漏查;放行 |

## 放行理由(末輪、本輪最高 minor)

- r3c1:方向是多收不是漏收,落在標明「關鍵字判,可能誤收」的那一段,讀的人看得到整句;真圖譜修前修後輸出逐字相同、這種寫法 0 筆。要修得改子句切點,修完要再派新席驗,超過 standard 三輪上限;回頭條件寫進計劃筆記 REVISIT。
- r3c2:原有行為,所有種類的內容都只印第一行(同 decisions 的 first_line 慣例);真圖譜「第一行沒有關鍵字、第二行之後才有」的有效決策 0 筆;同一行 REVISIT 一起看。
