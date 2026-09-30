# 設計審第 3 輪收貨紀錄(上限輪):守檔筆記對照改動

6 席全收齊後才動計劃。四道機械檢查:6 份都已是正規化格式;quote-check 全數錨定;refcheck 見下(只有本案新建的資料夾不存在);reflog 無異動。

finding 編號:c=正確性-opus、b=邊界-sonnet、h=接手-sonnet、k=併發-sonnet、r=回滾-sonnet、a=架構對齊-sonnet,後面接報告裡的 F 編號。

| 編號 | 席 F | 等級 | 處置 | 折在哪 |
|---|---|---|---|---|
| c1 | 正確性 F1 | major | 折 | 做法 2 拆成對照指紋與材料指紋;項目檔名、prepared 用材料指紋 |
| c2 | 正確性 F2 | minor | 折 | 〈誠實界線〉對照指紋盲區改寫 |
| c3 | 正確性 F3 | minor | 折 | 做法 2、3 `model-actual:` 自報行;〈誠實界線〉 |
| b1 | 邊界 F1 | minor | 折 | 做法 3 紀錄資料夾先建 |
| b2 | 邊界 F2 | minor | 折 | 做法 2 檔頭路徑 errors=replace |
| b3 | 邊界 F3 | minor | 折 | 做法 4 頂端已在主線、刪除分支記 none |
| h1 | 接手 F1 | major | 折 | 做法 6 升小版加 CHANGELOG、上線日=推上 main |
| h2 | 接手 F2 | minor | 折 | S10 範圍寫法與平均比法 |
| k1 | 併發 F1 | major | 折 | 同 c1 |
| k2 | 併發 F2 | minor | 折 | 做法 3 提交指令已帶路徑(`git add governance/reread-verdicts`);skill 小節照同一句,不用 `git add -A` |
| r1 | 回滾 F1 | minor | 折 | 做法 6 先後順序改寫 |
| r2 | 回滾 F2 | minor | 折 | 做法 4 同提交改 `t_prepush_gates_stop_on_signal` 期望值 |
| a1 | 架構 F1 | major | 折 | 做法 6 錨點 approve;〈回退〉 |
| a2 | 架構 F2 | minor | 折 | 做法 4 註解不說「唯一」 |

重現不到而沒折的:無(refuted-set none)。放行的:無。
