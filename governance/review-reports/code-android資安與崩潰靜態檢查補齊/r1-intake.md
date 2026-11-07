# r1 收貨紀錄(code-android資安與崩潰靜態檢查補齊)

兩席(審查、架構對齊)全數交回後才寫進卷證;報告從子代理逐字稿取最後一則原樣存檔。審查席初版總結句寫了比檔級宣告高的等級字樣(否定句),機械收貨擋下,退回該席改寫那一句、其餘不動,存的是重交版。兩份 quote-check 全數錨定。

編號:審查席 R1–R3(minor)、架構對齊 A1(major)、A2、A3(minor)。架構對齊 F4 自標「⚠ 交編排者,不計入不對齊」,不列 finding;編排者看過:那條斷言寫死的兩列是型錄逐列查證計劃的收尾值,留著(數字變了就該有人看)。

## 先查世界

- PRIOR-ART:A1 A2:規則讀法本 repo 已有單一來源(`configs/ast-grep/kotlin-android/check.py` 的 `load_rules`、`MSG_MAX`),鄰居測試都讀它;不查外部,直接收進既有讀法。R3:會擋那條的除錯判法沿用同一包裡 `kt-webview-debugging-enabled` 已過設計審的寫法(MobSF mobsfscan 與 MASTG-TEST-0227 的來源已記在計劃 PRIOR-ART ③),不另立判法。R1 R2:只補測試案例。

## 出處清單

- 讀 `ignores` 的位置:全 repo 只有這支新測試自己切檔讀(`grep -n "ignores:" scripts/test_lumos.py` 只有它);收進 `load_rules` 後測試改讀 `r["ignores"]`。
- 訊息長度上限 120:`check.py` 的 `MSG_MAX`、`message_problems`;新測試改讀 `m.MSG_MAX`。另一處 `t_lint_block_message_shows_fix` 的 120 是新增告警閘截斷長度,不是規則包常數,不動。
- 認 `BuildConfig.DEBUG` 的規則:`kt-webview-debugging-enabled`(已有)、`kt-webview-file-url-access`(這次補)、既有 `kt-http-logging-body-unguarded`(較寬的舊判法,計劃不做清單已寫不改)。

## 重現(修前紅、修後綠)

| id | 驗法 | 結果 |
|---|---|---|
| R1 | 新增 C21 `with(webView.settings) { setAllowUniversalAccessFromFileURLs(true) }`;拿掉不帶接收者的 pattern | HIT:C21 紅;還原綠 |
| R2 | 新增 C22 `socket.setEnabledProtocols(arrayOf("TLSv1", "TLSv1.2"))`;把規則裡的 setEnabledProtocols 改名 | HIT:C22 紅;還原綠 |
| R3 | 新增 C23(`if (BuildConfig.DEBUG)` 成立那一支,不報)、C24(否定,照報);拿掉會擋那條的除錯判斷 | HIT:修前 C23 被報;修後 C23 不報、C24 照報;拿掉判斷 C23 紅 |
| A1 | 讀碼:測試自己 `re.split(r"^---…")` 切 yml | HIT;修後讀 `load_rules` 的 `ignores` |
| A2 | 讀碼:測試寫死 120 | HIT;修後讀 `m.MSG_MAX` |
| A3 | 讀碼:`Path(GRAPHCTL).resolve().parents[1]` 檔內 20 處、`Path(__file__)…parent.parent` 也有 | HIT:鄰居兩種並存 |

修後:`check.py --sg` 規則 211 條、0 個問題;`-k kotlin_rulepack` 88 passed、`-k kt_catalog` 48 passed。
