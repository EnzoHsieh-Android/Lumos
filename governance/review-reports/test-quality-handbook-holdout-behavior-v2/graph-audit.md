# 乾淨圖譜自足性審計

審計席：/root/holdout_graph_audit；唯讀，未傳預期結論。

指定四篇圖譜及 rescored-results.json、native summary.json 可還原本次範圍、結果、儀器修訂、限制與後續。Severity：無 actionable finding。

還原結果：Python 兩題各兩臂兩次；首次及最終兩臂各 detected 12/12。原生路由相关題 1/3 對 2/3、無關題均 0/3。首批行為排除，重跑批補 dict.items/subTest 後一致重算。候選留分支、不採用、不推送，S5 doing。

逐字引句：
> 本紀錄的 pass 只表示本次固定試行及證據核對完成，不表示候選改善測試品質。
> 原始分數與原始模型驗證回饋保留，重算結果不能冒充生成時就得到的分數。
> 它不代表完整安裝 Lumos、多技能競合或 Codex 原生路由。

限制：此席只核對指定筆記與 JSON，未獨立重跑模型、驗 SHA 或查其他原始事件。SHA 核對由實作席完成，不歸因本審計。
