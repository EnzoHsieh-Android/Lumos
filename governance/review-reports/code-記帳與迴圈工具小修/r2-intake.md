# code-記帳與迴圈工具小修 r2 收貨與修正

七席(正確性、邊界、資源、整合、通才、架構對齊、資安)全部交回後一次存檔;report-normalize 只做格式搬移。共 20 條(正1–4、邊1–4、資1–3、整1–3、通1–4、架1–2;資安 clean 0 條):major 3 條(正1、邊1、資1),其餘 minor。

正確性席自述中途在 web-ledger 工作樹跑過一次 `git checkout --detach f791d8ba` 又切回;`git -C web-ledger reflog -5` 核對:HEAD@{0..2} 是那兩次 checkout,分支仍指 69ee6d76、工作樹乾淨,沒有改檔。

## 錨不到的三句引句:機械重現

| 編號 | 指令 | 輸出 | 判 |
|---|---|---|---|
| 整合 引句#3 | `grep -rn -F 'folded-set\` 沒有 \`none\` 這個值' --exclude-dir=review-reports .` | `docs/lumos-toolchain-knowledge/Projects/代碼審修正關卡第0步_計劃.md:142:…(\`--folded-set\` 沒有 \`none\` 這個值,這裡要自己認;…` | HIT(diff 外的舊計劃) |
| 資源 引句#3 | `grep -n "_lscan = _canary_ledger_" scripts/lumos` | `11446:            _lscan = _canary_ledger_scan(env)`(上兩行 `if loop:`、`try:`) | HIT(席位把換行寫成 \n) |
| 正確性 引句#4 | 讀 `_nogo_full_review_shape` 原始碼 | 函式本體第一段是 `for i, r in enumerate(rows, 1):` 換行 `rid = r.get("round")` | HIT(diff 外,席位自己標明) |

## 編排者裁定(交作者照做)

- G1 結局帳過濾(正1、正2、正4、通1、通4、架構席 ⚠):統一成一條規則——讀審查列的共用入口(`_review_rows`/`_loop_round_format`)負責濾掉結局帳,呼叫端不再各自重濾;正4 點出的 `_nogo_full_review_shape`、`_disposal_round_groups` 的呼叫端也走這個入口。每個讀側入口(loop next、loop status --panel、處置閘、跑滿提示、回放)各補一支「結局帳之後」的正向行為測試,斷言實際輸出,不只斷言沒有某句話;拿掉過濾要會紅。
- G2 保留字 none(邊1、正3):`none` 是保留字,任何清單(--findings-set、--folded-set、--accepted-set、--refuted-set、--regression-set)出現叫 `none` 的發現 id 一律 rc2 擋、講原因;不要只修 regression-set 一欄。
- G3 讀帳次數(資1、資2、資3):每條記帳路徑(含預設路徑)整本帳只讀一次並共用;先驗參數、驗過才讀帳;用完不留第二份。補一支數讀帳次數的測試涵蓋預設路徑。
- G4 訊息裡的示意指令(邊2、通3、架1):所有印給人照抄的指令,編號照鄰居做法先 quote、不截斷(控制字元照 `_esc_clean` 清);同一函式不要有兩種上限。每個印指令的分支都補 ESC 編號的測試。
- G5 帳壞的出口(邊3、邊4、架2):整本非 UTF-8 時 --orchestrator 路徑也走同一個友善訊息(重用 `_loop_records_checked` 那句,不另寫);最後一列沒有換行時寫入前先補換行或擋,二選一照既有寫入原語的做法。
- G6 測試名稱與文件(通2、整1、整2、整3):S17 標籤與 docstring 改成實際行為;計劃不做節、做法、圖譜筆記、兩篇舊計劃的過時句照現行行為改(舊計劃已 done 的照「當時」寫法加註,不改歷史結論)。
- 駁回 0 條。
