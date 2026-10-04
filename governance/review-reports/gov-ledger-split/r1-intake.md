# r1 首輪機械掃描(派席前)

掃描者:便宜 agent(sonnet),固定清單 ①未定義的詞 ②壞引用 ③範圍自相矛盾 ④機械宣稱驗語意。①②③與存在類命中直接修真檔;語意類命中逐條留前後對照。

壞引用:無(5 個 [[連結]] 都在;`git rev-parse --git-common-dir`、`doctor --ci`、telemetry-write-failed 都存在)。

## 語意類命中(7 條,全部已修進計劃)

| # | 修改前 | 修改後 | 程式碼佐證 |
|---|---|---|---|
| m1 | 例行紀錄寫不進去「照 `_gate_event` 回 False,呼叫端講 telemetry-write-failed」,一句話涵蓋全部 | 兩條路各照現有行為:`_gate_event` 回 False 照舊明講;`_append_governance_log` 照舊靜默;[S4] 限定 `_gate_event` 那一路 | `scripts/lumos:1410-1431`(`_append_governance_log` 吞 OSError)、`scripts/lumos:1394-1403` |
| m2 | 「不是 git 專案時退回寫版控帳(跟現在一樣)」 | `_append_governance_log` 取不到 HEAD 本來就不寫、`_gate_event` 沒 docs/ 本來就不寫,都維持;只有「有 docs/ 但取不到 git 共用資料夾」才退回版控帳;[S5] 改寫 | `scripts/lumos:1417-1424`、`scripts/lumos:1323` |
| m3 | 寫帳是「四支底層寫入器加 `_loop_gov_mark`」,分流在寫入器決定路徑那一步 | 直接寫帳的就四支,`_loop_gov_mark` 等是包裝;`_append_governance_log` 一批混兩種,要逐筆分流 | `scripts/lumos:978`、`scripts/lumos:1426` |
| m4 | 判定類讀者沒列 `_escape_released_loops` | 盤點與〈做法〉4 補上 | `scripts/lumos:11141` |
| m5 | code-loop 的 skipped-env 放右欄(本機帳) | 改留左欄:它是繞過代碼審的痕跡,工具對使用者承諾「這一筆會留在治理帳上」 | `scripts/lumos:43966` |
| m6 | doctor 的帳本成長段列為「兩本一起讀」 | 成長段量的是版控帳這個檔,只讀版控帳;loop list 的關門事件(`_loop_close_stamps`)也從統計類移到判定類 | `scripts/lumos:2238-2290`、`scripts/lumos:10189` |
| m7 | 天花板說「跨機器例行統計目前沒有讀者需要」 | 承認 S18 度量式撤除條件會變成只算本機,並寫明影響(只是軟提醒、--ci 不跑) | `scripts/lumos:3973`、`scripts/lumos:2720` |

## 存在類與範圍類(直接修,不算 findings)

- 分流表把 note-reread 的種類誤寫在 note-audit 底下 → 拆成兩個閘各自列(`scripts/lumos:31575`)。
- drift-check 漏 range-unavailable → 補進右欄(`scripts/lumos:35713`)。
- 「各閘的 fail-open」「各段 check-*」是萬用字元,跟「不在表上就留版控帳」衝突 → fail-open 改留左欄(自動放行的痕跡),check-* 限定為 doctor --ci 寫的提醒段,其餘一律明列。
