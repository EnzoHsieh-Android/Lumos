# 空發現記帳用法更正

首輪兩項minor確實折入，第二輪兩份原始報告確實clean零finding。第二輪載體參數由編排者錯傳 `--findings-set none --folded-set none`，CLI把none當一般ID；這不是工具不支援乾淨無引句報告。原canary列和報告不改、不撤、不重記同輪；第三輪全新席按現有編制重審，零發現時完全不帶處置選項。

證據：cmd_canary明文「這輪沒有任何發現的話，處置那幾個選項就別帶」；_loop_status_disposal在vacuous且carrier為None時省略引句錨定、不宣稱quote通過。另`--refuted-set none`與`--regression-set none`才有none保留值，不能把該慣例套到findings-set。

前次凍結命令仍執行了anchor approve，只有刻意改動並經兩輪審查的test檔指紋更新；code golden未凍成，不能宣稱整案已通過。已有design golden不重凍，保留原收斂時內容指紋，後續計劃文字清理由代碼審原始graph patch見證，非新設計裁定。
