### ext-f1 解析前的錨點失敗仍會永久吃掉 gap，S1 並未真正建立「失敗不丟件」保證

severity: blocker

引句:「orchestrator 輸出解析失敗(PARSE_FAIL/NO_JSON/空)時,中止前把選中的 gap 原分數放回 backlog」

佐證:file: `governance/autonomous-loop.sh:170`

說明：gap 在第 145 行已由 `select()` pop，之後才執行 anchor verify；若 anchor 缺失或驗證失敗，第 177 行直接退出，完全不 requeue。故修完指定三種解析錯誤後，仍存在可確定重現的丟件路徑；回填必須涵蓋 pop 後所有提前退出，或改成成功提交後才 ack。

### ext-f2 無成本信封的 PARSE_FAIL 不會產生帳目，因此「連續兩天管線死喊人」沒有可靠資料源

severity: blocker

引句:「連續 2 天 pipeline_fail → 復用既有 line_notify 喊人」

佐證:file: `governance/autonomous-loop.sh:228`

說明：成本解析遇到無法載入的 JSON 會直接退出、不寫 canary 帳；但這正是 `PARSE_FAIL` 的典型形狀。S3 又把 outcome 綁在「成本落帳那筆」，因此連續兩天都收到損壞或空信封時，帳上反而是零筆 pipeline failure，通知條件永遠無法成立。失敗事件必須獨立於成本是否可抽取而必寫。

### ext-f3 outcome 在成本帳寫入之後才判定，單一 note 無法如實記錄完整結局

severity: major

引句:「成本落帳那筆的 --note 帶上結局分類與美元」

佐證:file: `governance/autonomous-loop.sh:245`

說明：現行成本記錄發生在解析結果分支、收斂判定及 tier 守衛之前；真正的 `CONVERGED` 直到第 257 行才取出，後續守衛還可能否決自報收斂。依此控制流，寫帳當下尚不知道最終 outcome；spec 未裁定延後落帳、補記事件或如何避免重複，S3/S4 的統計基礎因此不成立。

### ext-f4 七天彙總要求的「放行 Z」無法從指定的 canary 帳推導

severity: major

引句:「資料源=canary 帳的 auto-* 迴圈」

佐證:file: `governance/autonomous-loop.sh:367`

說明：自主迴圈收斂後只把 spec 放進 `pending/`，等待人類另行放行；目前寫入 `auto-*` canary 行的則只是 orchestrator 成本。兩者沒有共同識別鍵或後續放行回寫，所以 canary 帳最多能算「產生待審 spec」，不能算實際放行件數；S4 所稱逐筆加總一致無法成立。

### ext-f5 每次進場都乘 0.95 並不等於每日衰減，重跑會在同一天任意加速淘汰

severity: major

引句:「每日進場呼叫既有 decay_and_prune」

佐證:file: `governance/autonomous_loop/backlog.py:32`

說明：既有函式沒有記錄或檢查上次衰減日期，每呼叫一次就再次乘上 rate。排程重跑、人工驗收或異常重啟均可讓同一天衰減多次，甚至提早歸檔大量 backlog；spec 必須定義以日期差計算，或保存 last-decayed date 並保證同日冪等。
