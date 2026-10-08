# R2 收貨與修復驗收

兩席收齊後才動來源；原報告未改。normalize／quote／ref／seat 兩席全rc0。

| ID | 重現 | 處置 | 證據 |
| --- | --- | --- | --- |
| COR-1 | HIT | folded | 真執行 .md/.json/.jsonl 前置成立，影響來源、家與角色清單五條紅；與 r2-boundary-red.json／green.json 對照 |
| COR-2 | HIT | folded | 真無副檔名歷史卷證入種子及誤觸事故四條紅；同上紅綠及 r2-targeted-rerun.json 工作目錄首行污染控制 |
| ARCH-1 | HIT | folded | 同 COR-1 的跨層例外缺漏，共用原簿記例外／raw解析／首行函式与 cap，不加副檔名或目錄表 |

兩個實際根因，三個報告ID；沒有把架構重複項冒稱第三個新缺陷。COR-1 在 main 舊版就漏可執行文件副檔名，並非此次首次引入；COR-2 是上次修補把 shebang? 當確定程式造成，regression-set只記 COR-2。同根因兩席一致且真入口已機械重現，免辯方，不降 severity。

父代理另發現驗收時間問題：兩內容功能案例受真 Git／三秒環境前提影響。可控時間3.1秒使原斷言紅、充足測試上下文則原斷言綠；原三次失敗／baseline／單案／controlled-clock均保留。三個正面功能段顯式測試 budget30，正式預設3秒与原零預算時間斷言保留。後者實際揭露 budget0 先讀 Git 的真入口缺陷，另探針0過2敗後修到角色16案例61全綠。此父代理補充不是冒稱審查員已報，也沒有灌進報告findings數；R3新席須檢查這些新增差異。

前段56/0的 source SHA 早於零預算修復，逐份卷證按其本來版本讀；最後修正關卡須在提交後重驗與綁版本。不宣稱正預算全鏈截止期、原 Python major 或完整 rename 舊路徑缺口已解。
