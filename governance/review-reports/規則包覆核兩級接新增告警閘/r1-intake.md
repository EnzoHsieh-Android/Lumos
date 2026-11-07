# r1 收貨(2026-11-08)

preflight-4: ran

## 首輪前掃(編排者自己逐句開檔驗,沒另派代理)

①未定義的詞:無。②壞引用:`lumos refcheck` 見提交前輸出。③範圍自相矛盾:無。④機械宣稱驗語意:
- 「出處不全列掛著 8 條提示級規則」:用主線 `configs/ast-grep/kotlin-android/check.py` 的 `main_rows` 與 `load_rules` 實算,8 條全在 `rules-hints/`,覆核級 0 條 → 成立。
- 「自檢的出處不全檢查只看嚴重度」:`catalog_problems` 裡 `r["severity"] != "hint"` 那段 → 成立。
- 「好例檢查的已知誤報排除只對 `rules-review/`」:`review_ids` 只收 `rules-review` → 成立。
- 「新增告警閘不分等級、接了就擋」:[[Systems/linter精選目錄]] Kotlin 規則包那節原文 → 成立(程式裡也沒有依 SARIF level 過濾的分支)。
- 「自檢的掃描用 JSON、沒驗過 SARIF」:`scan()` 用 `--json=stream` → 成立。
- 「提示級在 SARIF 對應 note」:只查到 ast-grep 0.42.0 原始碼,0.51.1 沒驗 → 計劃做 3 列成實作第一步的實驗。

## 收貨

四席報告全數存檔、正規化、引句全錨定。全輪 23 條(major 5、minor 18)。id:tc 通才、co 正確性、ig 整合、ar 架構對齊,加報告裡的 F 序號。整合席在 /tmp/lumos-seat-work 裝 ast-grep 0.51.1 做了實驗,目錄已由編排者刪除。

## 先查世界

- PRIOR-ART: 新規則先試水溫再擋——Semgrep 規則有 Monitor(只記)模式,新規則先放 Monitor 量過再改 Block(https://semgrep.dev/docs/semgrep-code/policies );本 repo 規則包既有「新規則先放覆核級、量過誤報低於一成才升級」。採用:不接閘目錄 `rules-unwired/` 承接試水溫,跟出處不全共用。
- PRIOR-ART: 放行過的告警不算進風險——SonarQube 標成 False Positive / Accepted 的問題不算進品質閘(https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ )。採用:分級不數指紋已放行的 lint 命中。
- SARIF 有沒有輸出:不查文件,r1 整合席直接實測 0.51.1。

## 逐條去向(全部折入)

| id | 一句 | 去向 | 重現 |
|---|---|---|---|
| tc1 | 提示級進不進得了閘沒驗、退路跟自檢打架 | 折:整合席實測有輸出;做 3 拿掉「提到 info」退路、改成綁測試的自檢 | HIT:r1 整合席 0.51.1 實掃 148 筆 note |
| tc2 | 指紋綁整段命中範圍 | 折:實務隱患改寫 | HIT:讀碼 `_lint_new_key` 取起訖行片段 |
| tc3 | 漏列要同步的既有測試 | 折:做 2 用 `r.get("dir")`、補第四目錄;S1 預期值補缺鍵列 | HIT:讀碼 `t_kotlin_rulepack_messages_cite_catalog` 假規則無 dir |
| tc4 | 62 條與現況數字對不上、設定檔已存在 | 折:隱患改 54 條;做 4 寫明只改範本文字 | HIT:主線 load_rules 數 12+50 |
| tc5 | 守衛面沒分析、量測門檻與預算順序沒定義 | 折:守衛面寫風險;20 筆門檻;做 4 會擋的那份排第一 | HIT:讀碼 `_LINT_NEW_DEFAULTS` budget 300 |
| co1 | 放行過的命中仍推高分級 | 折:做 6 | HIT:讀碼 `_pitfall_tier` 有 claims 就 high,本會談型錄那批實際撞過 |
| co2 | 規則目錄全空測試在加第四目錄後判錯 | 折:做 2 補第四目錄訊息;實作時同步改那支測試 | HIT:讀碼測試只刪三個目錄 |
| co3 | 假規則沒有 dir 鍵 | 折:同 tc3 | HIT:同 tc3 |
| co4 | SARIF 自檢沒共用逾時旗標 | 折:做 3 寫明共用、讀不懂照跑不起來報 | HIT:讀碼 `_TIMED_OUT` |
| co5 | 沒有反向檢查 | 折:做 1 把 unwired 定成也收試水溫的新規則,有出處的放進去是合法的;不加反向檢查 | HIT:讀第一版做 2 |
| co6 | 收工檢查也會跑 | 折:做 5 | HIT:讀碼 `_lint_wt_allow` 只看路徑在 configs/ast-grep 底下 |
| co7 | 型錄格數與分號 | 折:做 7 改成 40 格改 32、保留前綴、不放分號 | HIT:主線 main_rows 數 40 |
| ig1 | 收工檢查每回合擋 | 折:同 co6 | HIT:同 co6 |
| ig2 | S2 的 CI 步驟不存在、會被測試濾掉 | 折:做 3 原因句含「樣本」、S2 綁 `t_kotlin_rulepack_samples` | HIT:讀碼測試的關鍵詞過濾 |
| ig3 | 規則包節點的 RULE、WHY、工作流程跟新接法矛盾 | 折:做 1 新目錄兼收試水溫;做 7 逐條改寫 | HIT:讀 `Systems/kotlin規則包` 第 20、24 行與工作流程 |
| ig4 | 前案反向引用列不齊、3 格錯標批一 | 折:做 7 列齊兩篇計劃與 check.py 兩處註解、3 格改 | HIT:主線 git grep |
| ig5 | 已另加提示級宣告的專案會重複 | 折:做 4 範本加一句刪舊宣告 | HIT:整合席臨時 repo 實測 total 4 |
| ig6 | 新檔要有家、搬是拆檔 | 折:做 1 寫拆檔、做 7 補 about_code | HIT:讀節點 about_code |
| ig7 | RETIRE-IF 分母記不到 | 折:改成在實驗專案用 `lint-waive --list` 量 | HIT:讀碼 `_LINT_NEW_COUNTED_KINDS` |
| ar1 | 換軸連動三處沒列全 | 折:同 co2 | HIT:讀碼兩句寫死三目錄 |
| ar2 | 錯誤句格式與 info 退路 | 折:做 2 寫錯誤句;退路拿掉 | HIT:讀碼既有二元組 |
| ar3 | 新檔沒登記到家、舊描述沒改 | 折:同 ig6 | HIT:同 ig6 |
| ar4 | 前案作廢標法 | 折:`status` 已用 `lumos set` 改 superseded | HIT:讀碼作廢判定看 status |

修補因果:首輪,無。
