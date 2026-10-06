通過：指定圖譜能還原範圍、驗證天花板與接手方式；S1／S2／S3 與三份技能來源一致，未發現阻礙。**目前通過的是來源文字與受控判讀核對，尚非提交、安裝或實際成效驗收。**

- **S1 通過：完整分段、新席完整範圍、比較與因果分開。**
  [templates §3.1 第0步](/private/tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:183)逐字要求：「先保存僅修補與必要測試的完整可執行固定版本，驗repair及preserve，再保存重構版驗受影響的相同preserve。」另明寫：「順序不是因果證明」及「新席從完整改動核對作者分類，不以分類排除檔案。」

- **S2 通過：必要重構先行，拆不開不造半成品。**
  同段逐字寫：「必要重構先行時先驗重構前後保留行為，再驗修補；拆不開則記原因與合看路徑，不拼混合版本，不以不能載入的半成品當回歸。」第6步再要求不可比或未執行者「寫未判定與原因」。

- **S3 通過：整理提交後重新固定與留痕，可一起 PR。**
  [templates](/private/tmp/lumos-future-repair-regression-research/skills/lumos-design-loop/templates.md:184)逐字寫：「推前仍按一功能一提交整理，最後可一起PR，不因此增加輪數。」以及「壓提交或換基底後按原規則重新固定派工版本與留痕，歷史中間結果不可挪成新版本通過。」
  [code-loop 第5步](/private/tmp/lumos-future-repair-regression-research/skills/lumos-code-loop/SKILL.md:45)與[commands/06 末尾](/private/tmp/lumos-future-repair-regression-research/skills/lumos-project-notes/commands/06-代碼審與推送.md:104)均指向此單一來源，沒有另立不同規則。

原始結果已唯讀重算：四份來源 SHA-256 與 Git 樹碼一致；保留的 probe 在記憶體重算 **24／24 筆觀測、預期值與退出碼均吻合**。

| 版本 | 六案例退出碼 |
|---|---|
| 修前 | 1、0、0、0、0、0 |
| 僅修補 | 0、0、0、0、0、0 |
| 安全重構 | 0、0、0、0、0、0 |
| 故意退化重構 | 0、0、0、1、1、0 |

[README](/private/tmp/lumos-future-repair-regression-research/governance/research/review-repair-regressions/repair-refactor-stages/README.md:3)明寫「歷史SHA是當次指紋，重放應從原文重建」；本次未重建歷史提交或寫檔。其「不稱24項正式測試通過」也與結果一致。

接手資訊足夠：[計劃](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/修復與重構分段驗證_計劃.md:53)明寫「來源完成後維持doing等待試行」及「本次無全域安裝，受控例子只驗證判讀方法，不證實收斂成效」。連結的觀察入口列出安裝、實際載入文字、治理帳與派工原始紀錄，並要求 2026-10-20 回看；不足十輪補下一個日期。

目前相關改動仍未提交，計劃、驗證與實驗資料仍未追蹤，因此**一功能一提交是已核對成立的交付規則，尚未完成實際提交驗收**。全程未寫檔、未派代理、未全圖巡檢。
