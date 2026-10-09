# 第三輪收貨與停點

產品固定為03a46da，所有啟動的席及辯方均已完成後才寫入本輪卷證；原稿存 r3-originals，採用檔只允許 report-normalize 純格式處理。r3-delivery-manifest.json 分開保存超過1800行、未執行與部分覆蓋資格，不把material blocker當產品bug。

正式處置閘FAIL：尚無處置载體；資安材料的最後内容缺 historical_handbook_trial.py 與 test_quality_handbook.py 两檔。原r1/r2判定与原因不改。第三輪目前只記合資格分席，其他部分報告沒有偽裝成完整席。

| ID | 觀察及判準 | 去向 |
|---|---|---|
| NT1 | orphan failure測試只要求通用rc2；產品檢查已用同案例兩版驗出拒收差異 | 未折minor；加專屬原因與合法控制避免旁路假綠 |
| NT2 | 舊bytecode已建立，但拒收斷言未確認suite-count原因 | 未折minor；補確認來源與拒收分支 |
| NT3 | Git fixture無timeout及signing隔離 | 未折minor；補有界命令及隔離用戶簽章 |
| NT4 | 全域vault缺scanner案例未建立有效source | 未折minor；補現場輸入及deployment原因 |
| NT5 | HIT：launcher rc1後同群worker仍活；重現後已清除worker | 原major卷證保留；辯方concern指既有合約只明示取消／逾時／超量，尚無真模型launcher路徑；維持風險未定，不寫成已修或零回歸 |
| NT6 | 控制測試只證timeout，没有完整取消／一般錯誤路徑 | 未折minor，跟NT5合併判實際生命週期範圍 |
| NT7 | Semgrep同一來源每finding重新decode/split；同案例三筆decode三次，修前後相同 | 未折minor效能補強；不得說是R2引入 |
| NG1 | HIT：「5檔」歷史決策與當前8檔不同；兩端仍共用同一精確常數 | 原major報告保留；辯方有具體反證降為minor歷史澄清，核心共用白名單決策仍有效，不直接作廢或改原始決策 |
| NG2 | 新前綴行缺當前規範的結構化出處／根因欄 | 部分席觀察，原稿超限；原規範已核對，待補合資格核對與修正 |
| NG3 | 新部署計劃無驗證plan_refs回指，spec-trace三條未認領 | 已真跑重現，待補回指及qualification，不推翻原R2測試 |
| NP1 | 多次席位在1800行预算耗盡，Readonly不容建立實驗目錄 | process failure原樣留痕；未執行不等於產品紅，拆範圍時計入規則／鏡頭／補讀成本 |
| NP2 | HIT：通用installer被注入中途copyfile失敗，launcher留半檔；兩版helper相同 | 原部分席報告保留；獨立辯方evidence證明是既有可恢復installer問題，本配套設計明示不重建installer，轉後續hardening線索，不硬塞入本次修補因果 |

回歸歸因：多項在修前已存在，部分新測試只在修後出現；未知部分不填regression_set=none，不把同族與修後新發現說成修復引入。

尚未推送、尚未有第四輪人裁、未通過完整推送閘。等待人裁時只補原始卷證與資格；沒有修改03a產品。
