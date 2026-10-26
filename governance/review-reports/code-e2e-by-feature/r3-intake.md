# code-e2e-by-feature r3 收貨紀錄

七席全交回(2026-10-26),git reflog 核過席位沒動 repo(HEAD 仍在 4b056532)。引句七席對各自審材全數錨定。通才席最後一則訊息是背景等待結束的補充說明,報告取它前一則以 severity 開頭的完整報告。

編號:正確性 C1–C4、資源 R1–R2、邊界 B1、合約 K1–K3、通才 G1–G3、資安 S1、架構 A1–A2,共 16 條,blocking 2 條(C1、A1)。第三輪是高風險上限;使用者在對話中選「加開一輪」。

## 修補因果(regression)

上一輪修補造成、有兩版證據的:C2(LUMOS_E2E_COLLECT 標記在沒收記憶體時也擋紀錄,修前照寫)、K1(計劃終端範例是上一輪改寫時寫錯)、K2(README 沒跟上上一輪擴大的提醒範圍)、G3(上一輪新增的測試小工具把結束時間算成解析不了的字串)。
原有漏查:C3 C4 R1 R2 B1 K3 G2 S1 A1 A2;C1 是上一輪新增函式缺反向測試,修前沒有可比版本,歸因未判定。G1 是上一輪刻意的取捨(不收 $),記成文件類。

## 根因分組與重現

重現方式:新測試放進修補前的版本(4b056532 的乾淨副本,換上修後測試檔)跑 -k android_e2e:363 過、8 紅(paths 反斜線與萬用字元、app_dirs 同一套規則、run-id 佔總表、替身收集腳本沒用到時照寫、紀錄目錄寫不進去、擋下的按功能跑與被拒的那次記總表、效能方法逾時不往下等;paths 只寫 . 與跳出專案根兩條是訊息字樣變了);另對修後版本把 _e2e_keep_old 的 old.get("complete") 改成 True,t_android_e2e_feature_record_rules 紅 2 條。

| 組 | 編號 | 重現 | 去向 |
|---|---|---|---|
| 路徑規則兩套 | A1 G2 | HIT:app\src、app/*.kt 在功能 paths 照收、app//src 在 app_dirs 照收 | 折:_e2e_relpath_err 加正規寫法與萬用字元,功能 paths 改用它 |
| 保留規則缺反向測試 | C1 | HIT:席位改壞後 359 全綠 | 折:t_android_e2e_feature_record_rules 逐格斷言 _e2e_keep_old |
| 替身收集腳本誤擋 | C2 | HIT:修後 --no-memory 也不寫紀錄 | 折:只有這次真的收記憶體才記 collector_override |
| 紀錄寫不進去噴堆疊 | C3 | HIT:chmod 555 後 rc 1、traceback、總表少一列 | 折:_e2e_record_update 接 OSError 回錯誤訊息 |
| 擋下的按功能跑記錯或不記 | C4 | HIT:總表 mode 是 full;沒帶 --no-record 被拒不記 | 折:預設 partial;被拒那次也記 |
| 一個卡住要等滿每個上限 | R1 | HIT:讀碼,修後測試以 3 秒上限驗 | 折:效能方法或記憶體情境逾時就不跑剩下的(沒跑到的判沒判完) |
| run-id 佔總表名 | B1 | HIT:席位兩版實測 | 折:run-id 不准叫 history.jsonl |
| 整數判斷沒用既有小工具 | A2 | HIT:讀碼 | 折:改用 _secev_int |
| 測試小工具時間字串 | G3 | HIT:fromisoformat 丟錯 | 折:改成解析後加一分鐘 |
| 文件 | K1 K2 K3 R2 G1 | HIT:讀文件對照程式 | 折:計劃終端範例、README 提醒範圍、skill 的 --preflight 用法、計劃清理那句、筆記補「不收 $ 而不加引號」的決定 |
| 紀錄目錄是捷徑 | S1 | HIT:席位兩版實測;新測試在 40036673 紅(紀錄寫到專案外) | 折:_e2e_record_update 遇到 .lumos、.lumos/e2e-records 或紀錄檔是捷徑就不寫、回錯誤訊息 |

沒有機械重現不到的條目(refuted 為 none)。同輪有 major,minor 全折、沒有放行。
