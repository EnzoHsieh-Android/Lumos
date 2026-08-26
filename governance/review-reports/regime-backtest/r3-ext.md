### ext-f4
severity: clean
引句:「回放讀凍結檔(report/snapshot)前先 sha 對帳」
佐證:file: `governance/review-reports/regime-backtest/r3-snapshot.md:29`
說明:已解。回放先核對凍結檔雜湊；不符或佚失時改報資料完整性紅燈，停止該項合取，不會誤報邏輯漂移。verdict 另存各檔 git blob id，提供內容位址與版控回復依據。

### ext-f5
severity: clean
引句:「舊 verdict 改名 `verdict-<日期>-<時分秒>.json` 存檔不回改」
佐證:file: `governance/review-reports/regime-backtest/r3-snapshot.md:30`
說明:已解。歸檔名稱加入時分秒，且目的檔已存在時拒寫 fail-closed；即使時間仍碰撞，也不會覆寫既有歷史。順掃其餘 r2 折入項，未發現照字面實作會產生錯誤行為的 major 以上新洞。

結論:否決解除
