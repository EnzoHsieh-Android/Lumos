severity: major

這是編排者根據九份原席報告編成的**處置彙總**，不是新增的獨立審查席。原席報告原樣保存在 `../probe-postreview-dispatch/r1-formal-*`；每一組下列出原席 finding，讓單輪只留一筆處置清單。凍結審材與當時的報告沒有因重新記帳而改寫。

finding G1：失敗嘗試與在途子程序沒有跨執行的可信失效記錄。
severity: major
blocking: 是
引句:「先以單次原子取代釘住事故，再歸檔舊資料；歸檔中斷不能讓下次重跑吃回成功外觀。」
file: `governance/eval/ablation_lumos_first.py:247`
來源：正確性 F1/F3、併發 F1、邊界 1/4/6、資料 D1、外家 finder F1、外家否決 F1。處置：未完成標記先於子程序建立，確認成功後才清；真進程父死子活與 ENOSPC 反例折 S11。

finding G2：單工作要求場數能越過窗口剩餘額度。
severity: major
blocking: 是
引句:「五小時窗口滿就留待下次補缺；本批只准單路派工，避免並行 TOCTOU 多開模型。」
file: `governance/eval/ablation_lumos_first.py:188`
來源：正確性 F2、併發 F3。處置：按剩餘額度縮小本次 runs；反例折 S12。

finding G3：互動式選題可把消融的一工作擴成多題。
severity: major
blocking: 是
引句:「"--only", qid, "--runs", str(n), "--arm", arm, "--out", str(out),」
file: `governance/eval/ablation_lumos_first.py:196`
來源：資安 F2。處置：題號入口拒空值、逗號與控制字元，探針新增精確單題旗標；dry-list 反例折 S12。

finding G4：組別與相對路徑可繞過單路輸出邊界。
severity: major
blocking: 是
引句:「for arm in a.arms.split(","):」
file: `governance/eval/ablation_lumos_first.py:364`
來源：邊界 3、資料 D4、資安 F1/F3/F4。處置：組別白名單及去重、輸出路徑絕對化、題號顯示轉義；反例折 S12。

finding G5：錯型或跨組結果可混入統計，或讓純合併崩潰。
severity: major
blocking: 是
引句:「s = merge(out_dir, ids, a.runs)」
file: `governance/eval/ablation_lumos_first.py:135`
來源：邊界 2、資料 D5。處置：同一份整檔失效判定驗證欄位與組別；反例折 S13。

finding G6：人看的摘要漏失效告示，純合併也會冒稱當前版本。
severity: major
blocking: 是
引句:「_atomic_write_text(out_dir / "summary.md", md)」
file: `governance/eval/ablation_lumos_first.py:408`
來源：資料 D2/D6、外家否決 F2。處置：Markdown 明示不可採信；純合併保留舊 meta 或標未知，明示 CLI 不等於逐場模型版本；反例折 S13–S14。

finding G7：歸檔中斷測試會由旁邊的 fatal 代打而假綠。
severity: major
blocking: 是
引句:「歸檔被中斷也須留下掃描得到的致命嘗試」
file: `scripts/test_lumos.py:37999`
來源：正確性 F4、邊界 5。處置：加入注入確實發生斷言；反例折 S13。

未列為本輪新增缺陷：併發 F2 的目錄改名反例超出當時 `valid_under` 的合作進程／目錄不被任意改名邊界；資料 D3 的跨三檔不同代在基線 `5ed04382` 已存在且無跨檔交易合約。兩項可重現現象及重啟入口都在原 intake 與計劃，這裡沒有宣稱已修。
