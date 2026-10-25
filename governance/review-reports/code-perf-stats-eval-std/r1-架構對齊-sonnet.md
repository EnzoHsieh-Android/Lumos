severity: minor

審查範圍是 `1f07e112` 對 `b9e35042`,共 3 個檔案(新增 Verification 筆記、改寫 Projects 計劃、Systems 節點補一條 verified_by)。

**1. 結構與位置跟鄰居一樣嗎?**
基本一樣。
- 新 Verification 放在 `Verification/` 目錄,檔名格式是 `日期_主題`,frontmatter 的 type、status、date、valid_under、revalidate_when、tags、plan_refs 也都齊。這些跟 `Verification/2026-10-23_macrobench實機端到端.md:1-16` 相同,該檔的 valid_under 同樣是清單寫法。
- 研究資料放 `governance/research/macrobench/2026-10-24-perf-stats/`,對應既有的 `2026-10-23-lab-tablet/`,都是「日期加主題」的子目錄。這批檔案早已進版控,不在這份 diff 裡。
- `Systems/macrobenchmark-adapter.md` 的 verified_by 在尾端追加一條。它跟前面五條同形,這也是 `2026-10-24_Android記憶體與穩定性實驗室驗收` 的做法。
- 「## 怎麼量」「## 結果」「## 沒驗的」這種小節標題,在 `Verification/` 目錄裡很常見,例如 `2026-09-04_Codex完全支援S0安裝層驗收.md` 就有「## 沒驗的」。
- 只有一處位置不同,見 A1。

**2. 寫法跟鄰居一樣嗎?**
大致一樣。
- 開頭的「白話:」段、「沒驗的」小節,以及放在檔尾、前面不加破折號的 `REVISIT:日期 內容`,都跟 `2026-10-23_macrobench實機端到端.md` 的結尾一致。
- 計劃裡一篇有多行 `RETIRE-IF:` 有先例,`Projects/探針隔離與清理收斂_計劃.md:36,101,126` 就是。同一篇有多行 `REVISIT:` 也有先例,`Projects/Android記憶體與穩定性驗收_計劃.md:45-49` 就是。
- 待辦清單沿用原來的「數字. 內容」寫法,「另待驗」那行也還在。
- 日期格式、`[[Verification/…]]` 連結寫法跟鄰居相同。

**3. 有沒有引入第二種做法?**
沒有。
- 證據沒有另開位置,仍放進 governance/research 的既有目錄,也沒另建統計腳本目錄。實驗腳本留在 macrobench-lab,跟上一篇一樣。
- 驗證紀錄沒有另開新欄位來取代 plan_refs 加 verified_by 這對既有連結。
- 撤除條件和回頭條件仍是 `RETIRE-IF:` 和 `REVISIT:` 這兩個既有的行首格式,沒有換成別的寫法。

## A1 計劃裡新的 REVISIT 擺在待辦清單中間
severity: minor
blocking: 否
引句:「REVISIT:2027-03-31 第 1、2、3、5 條上線後,真實專案若出現同場 20 輪仍誤報」
對照:`Projects/Android效能判定統計化_計劃.md:38`。同一篇的 RETIRE-IF 和另一條 REVISIT 集中在檔頭(`:22-25`),修改前的版本也是這樣放。`Projects/Android記憶體與穩定性驗收_計劃.md:44-49` 同樣把 RETIRE-IF 和 REVISIT 聚在一起。這條夾在第 9 條和「- 另待驗」之間,把清單切成兩段。結構沒錯,只是跟同一篇的集中放法不一致。`Projects/Macrobenchmark退步提醒_計劃.md:92,104,149` 也有 REVISIT 散在內文的先例,所以只列 minor。

不對齊共 1 條,其中重大 0 條
