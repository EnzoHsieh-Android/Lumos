結論：repo 已有「兩層防線」，足以支援保守的人工判讀；但跑滿回顧的 `family` 只能當事後歸類，不能當因果證明。若要機械保證「同族漏掃／修補引入／未知」分得正確，目前仍不足。

## 既有方案

第一層是逐 finding 的修補因果判讀，規則已相當完整：

- `fix-check` 的同類提醒、category、finding ID 或位置相同，都不證明同根因或修補因果；證據不足必須寫「未判定」。前次問題殘留也不自動等於修補造成回歸。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:181>)
- 必須固定實際修前、修後版本，保留完整差異；祖先關係、空 diff、執行順序都不等於因果。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:193>)
- 每個 finding 要用同一案例比較兩版：相同輸入、預期、測試來源、實際載入版本、環境與觀測。只見修後失敗、新 finding 出現，或兩版各自跑出結果，都不夠。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:200>)
- 可歸為：

  - 有證據的修復回歸；
  - 有證據的原有漏查；
  - 未判定。

  `--regression-set` 只能收第一類；未知不能灌成 `none`，也不能因未知而降低 severity 或丟掉 finding。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:209>)
- 修完仍要由全新席掃完整 delta；`fix-check` 只驗紀錄、測試與合約測試，不取代獨立回歸掃描。[SKILL.md](</tmp/lumos-future-repair-regression-research/skills/lumos-code-loop/SKILL.md:45>)

第二層才是跑滿回顧：

- 人裁到上限後，交給沒參與該迴圈的乾淨代理；只給席報告、intake 與快照，不給編排者的因果結論。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:423>)
- 回顧可歸成 `same-family-unswept`、`fix-induced` 等八類，並填輪次、報告路徑與說明。[templates.md](</tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:441>)
- 這套設計刻意沒有重建機械因果判斷；前案已拿掉「同類重複／修正引起比例」，原因正是粗略比對不準。[審查跑滿上限提示_計劃.md](</tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/審查跑滿上限提示_計劃.md:12>)

## 機械實際能驗什麼

`lumos loop retro --check` 能驗：

- family 是否在八類白名單；
- 輪次是否屬於最新人裁紀錄；
- `evidence` 是否是本迴圈帳上的既存席報告；
- 起草者不是原審查席，也不同於補完者；
- `why_cap`、`avoid`、`changes` 等欄位是否存在且達最低長度。

見 [scripts/lumos](</tmp/lumos-future-repair-regression-research/scripts/lumos:13137>) 與 [_cap_retro_check](</tmp/lumos-future-repair-regression-research/scripts/lumos:13391>)。

它不能驗：

- 報告內容真的支持該 family；
- 報告中的哪一條 finding 是證據；
- 兩個 finding 是否同根因；
- 後出 finding 是否由修補造成；
- 起草代理是否真的沒讀過編排者意見。

圖譜也明說：`evidence` 只保證路徑屬於本迴圈且檔案存在，不保證歸族正確；換一個代理可能得到不同分類。[審查跑滿回顧_計劃.md](</tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:183>)

因此：

> 「報告把它叫 fix-induced」或「這條 finding 在修補後才出現」都只是待驗主張，不是因果證據。

## 精確適用界線

逐 finding 的 §3.1 適用於：

- code-loop 的修訂輪；
- 上一輪確實有程式、測試或流程修補；
- 能固定修前／修後版本並核對同一案例。

首次審查不適用；版本、案例或環境不可比時，答案只能是「未判定」。

跑滿回顧適用於：

- 帶輪次的多席迴圈；
- 到上限後有人執行 `cap-decision`；
- 有本迴圈帳上席報告的卷證資料夾。

不涵蓋 light、循序單審、沒有卷證、到上限卻沒記人裁的迴圈。[審查跑滿回顧_計劃.md](</tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:88>) 此外，`accept-risk` 後直接結束、改用新迴圈編號等路徑也擋不到；凍結判定不包含回顧第八步。[loop-retro.md](</tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Systems/loop-retro.md:40>)

## 建議

若 family 只用來做跨迴圈趨勢與改善方向，維持現狀已足夠，但報告應明寫「這是回顧分類，不是因果裁定」。

若希望可靠區分三種原因，最小補強不必先改 CLI，只需收緊 §9 派工詞：

1. `fix-induced` 只接受 intake 已有 §3.1 同案例兩版證據，能證明修前正常、修後失敗，且混入變更的替代原因已處理。
2. `same-family-unswept` 要同時有：

   - 可核對的相同失效機制；
   - 後來案例在修補前已存在或已失敗的證據。

   「類別相同」「位置接近」「名稱相似」都不夠。
3. 缺任一因果要件時，不強迫二選一；暫用既有 `other`，note 固定寫 `attribution-undetermined: 缺少……`。這比新增 schema、CLI 與統計欄位更小。
4. 明訂 retro family 不得反向填充 `regression_set`，也不得用來調整 finding severity 或處置結果。

具體應判未知的場景：r2 修補同時混入重構與設定變更，r3 才發現空輸入錯誤，但修前版本無法載入同一測試。這時只能說「修前到修後區間出現問題」，不能寫 `fix-induced`；即使兩輪報告都把它歸為輸入驗證，也不能直接寫 `same-family-unswept`。

本次依限制未讀任何席報告，因此不能判斷真實回顧目前的分類一致率或既有回顧是否正確；只能確認規則、圖譜與實作邊界。本輪未寫檔、未做 Git 變動。
