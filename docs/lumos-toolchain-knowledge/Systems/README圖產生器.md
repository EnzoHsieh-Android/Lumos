---
type: system
status: doing
created: 2026-09-30
updated: 2026-09-30
responsibility: 負責重產 README 中英兩版的示意圖 SVG 並檢查圖的語意與動畫限制;不負責 logo、錄影 GIF 與 docs 裡的高密度詳圖
aliases: []
about_code:
  - assets/readme-diagrams/generate.py
tags:
  - type/system
  - status/doing
  - scope/ux-docs-hygiene
summary: |-
  WHY:[2026-09-30 [[Projects/README面試官十分鐘_計劃]]]主圖站名改成跟 README 正文一致的白話(讀程式碼/分派審查/審查與處理/寫回筆記),箭頭標上交給下一步的東西——讀者扮面試官時一再扣「圖上的圖譜、派工、evals 看不懂」「四個方框看不出資料怎麼流」
  WHY:[2026-09-30 同上]新增案例時間線圖 case-review,把 README〈一個真實的例子〉那段四輪審查畫成一張;數字來自 governance/review-reports/code-工具自裝檔不算消費專案/ 的四份 intake(每輪 7/4/7/5 位、12/6/17/11 條)
  PITFALL:[2026-09-30 本輪發現]2026-09-21 那次「說明改成程式碼為主」直接手改了 map-zh/en.svg,沒改產生器,之後 `--check` 一直是紅的;這次重畫主圖時才順手對齊。重現:`python3 assets/readme-diagrams/generate.py --check`
  PITFALL:[2026-09-30 本輪發現]用 qlmanage 把這批 SVG 轉 PNG 會截到動畫第一格(知識圖節點全空)而且裁成正方形;目視檢查改用無頭 Chrome 加 `--virtual-time-budget` 等動畫跑完再截。重現:`qlmanage -t -s 1400 -o /tmp assets/graph-demo-zh.svg` 後打開那張 PNG,節點是空的
---
# README圖產生器

> 白話:README 裡那幾張深色示意圖都是這支產生器吐出來的,不要手改 SVG。改完跑 `--check`,再轉圖用眼睛看中英兩版有沒有字擠出框、線穿過字。

## 怎麼改、怎麼驗

- 改 `assets/readme-diagrams/generate.py` 裡對應的 scene 函式,跑一次產生,再跑 `--check`(驗 XML、可重現、動畫只動線不動字、知識圖的揭露順序與關聯)。
- `--check` 驗不了排版:英文字通常比中文長,框要各自配寬;這次就修掉了英文字擠出框、數字和單位黏在一起、虛線穿過標籤這三種。
- 目視用無頭 Chrome 截圖(見上面的坑),中英兩版都要看。

## 這次的取捨

- 主圖版型、配色、動畫全部沿用,只換字與加箭頭標籤;使用者要求「圖該改就改,但要保持可讀性和美觀、新增的圖樣式要一致」。
- 「第一次使用」那張示意圖 README 已不引用(改用實機終端輸出),產生器照舊產出,沒刪。
