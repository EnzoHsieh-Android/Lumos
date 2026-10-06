# 首輪前掃與控制校正

preflight-4: ran

- 前掃 raw 與 execution 保留。未定義詞與語意各一命中，尚未更改生產碼或核心裁定。
- PF1 HIT：原句「中間與末尾的實際空白行不得消失」未有中間空白行案例；隔離行陣列突變保留舊七案例卻刪掉中間空行，preflight-semantic-control.json 可重現。原報告的「四組全綠」未實跑，不當作完整突變測試通過宣稱。把 S4 背書由僅空檔、單一空行、末尾空白行等七例，補為八例：a=1 / 空行 / b=2；兩條讀法皆驗第2行為空白、第3行正確、下一行超界。條款與裁定未變。
- PF2 HIT：原句「共用函式在該功能前後相同」未定義功能且卷證無版本；改為明列修正關卡便宜錯誤功能前 main 與功能提交，新增 attribution-pinned.json 的實際 git show + AST 雜湊比對。只補可核對的歸因，不以歷史判斷當新功能理由。
- 先前7項目錄基線預期錯誤改為各分支既有語義，95pass71fail；原紅燈與更正紅燈皆保留，見 test-control-refinement.md。不是七項產品修復。

- 前掃引句重播控制：第一次誤用已折入的新 r1-snapshot 對歷史前掃，第二條舊句因此未錨定；這是編排者選錯比對版本，非席報告幻覺。另從派審時未修改的 HEAD 還原 preflight-source-spec.md（明記事後還原來源），兩句皆錨定 rc0，原始報告未改。正式報告一律對派工前凍結的 r1-snapshot。前掃 raw 的混合等級標題未正規化，前掃不作正式 canary 載體。

## 正式六席收貨與處置

- 六份原始報告全部收齊，才改本計劃與測試。四席 clean，兩席各報 major 一條；不改等級。
- resources-F1 HIT：同一列採信重現 r1-resources-hook-repro.json，臨時全域配置 hooks 在來源 repo 外寫 marker；另有新 S5 fixture-red 0過1紅，受簽章設定阻擋。折入 fixture 過濾 GIT_*、官方全域／系統配置隔離、每次 Git 明示空 hooks 與停簽章、8秒上限；核心第2條明確正式入口與測試隔離的範圍，新增 S5，不改正式 Git 調用政策。
- integration-F1 MISS：同一列機械重現取真測試AST的八字元，compile/exec全部成功，兩個LF且執行值相符；r1-integration-compile-repro.json。不採信「SyntaxError」判斷，另派乾淨反向核對席從原問題驗證，結清後才記帳。原始報告不改，拒絕改三引號掩蓋誤判。

- integration-F1 MISS 已結清：乾淨反向核對席從原問題驗八字元 compile/exec 都成功，並以控制流程替身核對64次驗證呼叫。其真 TemporaryDirectory 試跑被唯讀沙箱擋住，不算真 pinned validator PASS；編排者真 Git 最小現場及真測試紅燈另有原始卷證。只排除 SyntaxError 誤判，不降原報告與帳面 major。
- 收貨 report-normalize/refcheck 均rc0；兩份 major 引句皆對派審前 r1-snapshot 全錨rc0。四份 clean 無引句rc2明記不適用，不宣稱quote PASS。seat-check全部rc0，其中 resources 把授權spec引句整句列為 out_of_scope，實際該句完全出自派審snapshot且quote-check已驗；視為字串抽取誤報，不改原報告或擴大派工範圍。
- fold-check提醒 body 的 attribution-pinned.json、scripts/test_lumos.py 沒出現在摘要；送鏡像核對只判真正前後矛盾，不複製程式現況填滿摘要。

- 折入鏡像核對 clean：摘要、裁定、S1–S5、風險與審計同步；71個來源座標反例仍紅，fixture的4綠不冒充產品修復。見 r1-mirror-raw.md 与 execution。
- 處置載體選 resources，該席全錨；唯一存活 resources-F1 折入，integration-F1 有反證列入 refuted。兩席 raw 與帳面均保留 major，integration存活數0，未用降等掩蓋誤判。
