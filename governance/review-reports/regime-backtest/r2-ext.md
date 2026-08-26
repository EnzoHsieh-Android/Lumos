### ext-f2
severity: clean
引句:「重凍(制度合法演進後 golden 過期時)比照 anchor approve」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:30`
說明:已解。`engine_rev` 會把制度合法演進分流為不紅的 golden 過期，並提供理由必填、治理帳留痕、舊版存檔的重凍路徑。

### ext-f3
severity: clean
引句:「新凍結(從未回放過的)必跑+存量輪替抽樣每週 5 包」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:32`
說明:已解。週跑不再全量掃描；存量固定抽 5 包，另有 5 分鐘總預算、超時截斷、略過數通知及升級全量的 60 秒機械門檻，成本已有上界。

### ext-f4
severity: major
引句:「各席 report/snapshot path+sha、engine_rev」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:30`
佐證:file: `scripts/lumos:10249`
佐證:file: `scripts/lumos:10267`
說明:新洞。所稱完整輸入閉包只保存 report/snapshot 的路徑與雜湊，沒有保存檔案內容；但四合取會實際讀取兩者內容做留痕與 quote-check。檔案日後被修改、刪除或路徑失效時，verdict 無法提供原始輸入重算，照字面只能讀工作樹現檔並把失敗誤報成邏輯漂移。應把每份 report/snapshot 的原文或不可變內容位址納入閉包，並另行比較 live 檔案以判定資料被動。

### ext-f5
severity: major
引句:「舊 verdict 改名 verdict-<日期>.json 存檔不回改」
佐證:file: `governance/review-reports/regime-backtest/r2-snapshot.md:30`
說明:新洞。歷史檔名只有日期；同一天第二次重凍會撞上相同目的檔。照字面實作可能覆寫第一份歷史 verdict，直接違反重凍留痕與歷史不回改。檔名需加入時間、engine_rev 或不可重複序號，且目的檔存在時必須拒絕覆寫。

已掃過輸入閉包、verdict 分類、engine_rev 分流、`governance/replay/` 目錄隔離、重凍留痕、新舊制形狀分類、週跑抽樣與預算、通知及唯讀邊界；除 ext-f4、ext-f5 外，未見照 spec 字面實作必然造成 major 以上錯誤的新發現。

結論:否決維持(ext-f4 的閉包不足會使核心回放失真，ext-f5 會破壞重凍歷史)。
