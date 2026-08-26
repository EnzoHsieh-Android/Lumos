# spec-conformance 對照(全文見 session 留痕;此檔存判定與缺口)

逐款:S1①③、S2①②③④、S3①②④、S4 = 兌現;S1②喊人分支/S2⑤/S3③⑤ = 部分兌現(缺口如下);「不做」六條全遵守。
真機佐證:2026-08-26 09:38 真跑一輪——decay ok、選中當日新 gap、anchor 拒跑、trap 放回(pf=1 分數不動)、落帳 outcome=pipeline_fail:anchor_fail、失敗日印出七天彙總行。

### conf-f1 load_covered 沒有逐行容錯,spec 明文兩支都要
severity: major
引句:「`load_backlog`/`load_covered` 逐行 try/except,壞行跳過並 log 計數」
佐證:file: `governance/autonomous_loop/gap_select.py:25`

### conf-f2 實作多出 spec 未列的細類 pipeline_fail:pending_write
severity: minor
引句:「pipeline_fail:api_error|truncated|parse_fail|anchor_fail」
佐證:file: `governance/autonomous-loop.sh:446`

### conf-f3 「連三輪管線死→喊人」的 LINE 分支零測試覆蓋
severity: major
引句:patch 中無對應內容(spec 行為斷言:連三輪管線死→進 covered 且觸發喊人(打樁))
佐證:file: `scripts/test_autonomous_loop.py:655`

### conf-f4 「已處置輪 trap 不重複放回」成功路徑無端到端驗證
severity: major
引句:patch 中無對應內容(spec 行為斷言:已 requeue/covered/收斂的輪 → trap 不重複放回)
佐證:file: `scripts/test_autonomous_loop.py:739`

### conf-f5 PARSE_FAIL 與 converged 的 trap 落帳端到端無沙箱測試
severity: major
引句:patch 中無對應內容(spec 行為斷言:PARSE_FAIL 輪帳上有 outcome 且無 usd;converged 輪 outcome 正確且含 usd)
佐證:file: `scripts/test_autonomous_loop.py:787`

### conf-f6 CONSEC_FAIL 分支真呼叫 send(build_alert) 的線路未測
severity: minor
引句:patch 中無對應內容(spec 行為斷言:連兩個有跑日全失敗觸發喊人,打樁驗訊息文字)
佐證:file: `governance/autonomous-loop.sh:61`
