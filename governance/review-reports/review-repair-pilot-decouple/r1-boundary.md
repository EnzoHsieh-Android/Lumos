severity: major

finding F1  
severity: major  
blocking: 是  
引句:「合格指本試行唯一協調者接手的本 repo 新程式行為工作」  
具體失敗場景：第三方提交只新增回歸測試，用來釘住既有程式行為，沒有修改 production code。一位協調者會把 Python 測試視為「程式工作」而納入第2案；另一位會依 repo 現行分級把測試檔排除於「程式檔」，判成不合格。兩者都符合現文，前四個樣本因而不唯一。快照引用的 Google 指南甚至明列「獨立測試修改」可作單獨 CL，使「只改測試」不能靠外部先例自行推定排除或納入。[Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)  
file: `scripts/lumos:6522`  
file: `scripts/lumos:6527`

finding F2  
severity: major  
blocking: 是  
引句:「修補目的和驗收證據均不依賴未放行的探針／消融程式或輸出」  
具體失敗場景：新工作以非探針目的修改一個共享函式或常數，自己的驗收也不用探針輸出，但未放行的消融程式會透過 import 間接受影響。按目前「目的和證據」判準可納入；按「不把探針修補混入樣本」又應排除。repo 已有真實形狀：消融 runner 直接從探針模組匯入兩個判準作為單一來源。現文沒有裁定應按修改意圖、直接檔案、執行期依賴，還是所有反向消費端判資格。  
file: `governance/eval/ablation_lumos_first.py:55`  
file: `governance/eval/ablation_lumos_first.py:58`

finding F3  
severity: major  
blocking: 是  
引句:「只在目前髒工作樹切分支不算隔離，因測試仍會載入未提交的探針草稿」  
具體失敗場景：協調者從目前 HEAD 建立乾淨 worktree；該 worktree 的 porcelain 雖然乾淨，基準提交本身卻已含尚未放行的探針提交，而且所有 worktree 仍共用 Git common dir、設定、refs 與外部資源。候選差異看不到舊草稿，但測試實際運行在它之上，樣本仍受污染。計劃只要求「記基準提交」，沒有指定必須是 main、已放行提交或通過何種基準驗證；目前 repo 的探針正式審仍是 FAIL/pending，這不是假設情境。  
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-04_消融派工正式審查修正.md:38`  
file: `docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:58`  
file: `docs/lumos-toolchain-knowledge/Projects/guard殺傷力驗證_計劃.md:78`

finding F4  
severity: major  
blocking: 是  
引句:「未滿五次也回報樣本與成本，由使用者決定停止或延長」  
具體失敗場景：2026-11-03 當天尚未回顧時出現合格候選。一位協調者在當日先領第2案，另一位依「到期先回顧、未裁決不延長」拒絕領號。若有案在截止前已登記但尚未首次派工，現文也未裁定繼續、凍結或記中止。`REVISIT` 機制在日期當天只產生提醒，候選登記沒有截止狀態或精確時刻可檢查，因此到期樣本集合仍會因執行順序改變。  
file: `scripts/lumos:2240`  
file: `scripts/lumos:2244`  
file: `skills/lumos-code-loop/reference.md:124`

finding F5  
severity: major  
blocking: 是  
引句:「已領號後才改成探針相依或中止，仍保留該格並標範圍偏離／中止」  
具體失敗場景：候選在10:00被誤記為合格並領第2案，10:05才發現它在領號前就已屬既有 loop，只是名稱不同。這不是「領號後才改成相依」，也不是一般中止。計劃沒有裁定應更正排除並讓下一件取得第2格、保留第2格算一次，還是另開更正事件；也沒規定錯誤時間、loop id、基準提交或誤清鎖的恢復格式。直接改表會抹掉稽核軌跡，追加更正又缺少哪一列為有效值的判準，而既有代碼審帳本明定記錯不能撤銷、只能換編號，兩套恢復語意會衝突。  
file: `skills/lumos-code-loop/SKILL.md:47`

已讀無 finding：

- 開頭欄位、摘要、PRIOR-ART 與總 RETIRE-IF。
- 「2026-10-04 收斂性診斷與下次試行的最小調整」。
- 「落點」。
- 同一工作換編號：S1、改道資格與第1案紀錄一致要求沿用原序號／loop，不洗輪次。
- 合格領號後中止：一致保留名額，不事後挑掉難案。
- 純文件工作：一致排除。
- 「實務隱患」。
- 「回退」。
- 「審計修正紀錄」。
- 「第1案逐案紀錄」。
- 「第1案例外續修授權」。
- 11 個內部 Wiki 連結皆有對應檔案。
- 四個外部連結皆可開啟；Google、Fowler 與 Git 文件能支持快照所述的小型自足變更、行為保持測試及 Git 設定／路徑查詢用途。[Martin Fowler](https://martinfowler.com/articles/refactoring-external-service.html)、[git-config](https://git-scm.com/docs/git-config)、[git-rev-parse](https://git-scm.com/docs/git-rev-parse)

最高級: major；blocking 件數: 5