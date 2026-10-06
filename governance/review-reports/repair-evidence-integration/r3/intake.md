# R3 findings 收貨及處置

只認真實原報告。閱讀超額/未能證上限均不算受控行數成功；不改原報告等級。

| ID | 重現 | 折入 |
|---|---|---|
| design3-logic-F1 | HIT | 固定樹重算變更；16/0 |
| design3-logic-F2 | HIT | 起終各讀自身設定；18/0 |
| design3-boundary-F1 | HIT | 交付自足錨及R2來源，空庫離線還原成功 |
| design3-integration-F1 | HIT | 同上離線冷還原 |
| design3-integration-F2 | HIT | 計劃明定閱讀帳入口与最低欄位；超額仍未判定 |
| design3-integration-F3 | HIT | 明定三份權威技能路徑及章節 |
| design3-resources-F1 | HIT | 交付自足錨及離線還原 |
| design3-resources-F2 | HIT | 256KiB/8MiB/5秒共享截止；32/0 |
| design3-resources-F3 | HIT | 權威技能清單 |
| design3-rollback-F1 | HIT | 各版各驗配置18/0 |
| design3-rollback-F2 | HIT | 補助逆向patch與載入CLI/test指紋；既有控制綠/已知缺口紅 |
| design3-rollback-F3 | HIT | 自足錨離線驗收 |
| design3-architecture-F1 | HIT | 固定樹變更集合16/0 |

原問題及保留控制見code-convergence-input-guards/r3-fixed-source-boundaries/lumos-route-final-native-subset.json（424/0/0），不同版本結果不得替代最後交付全套。回退控制receipt.json以實際退出碼為準；自足來源見r3-self-contained-source/delivered-offline-cold.json。
