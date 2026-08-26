### d-f1 同帶抑制缺參數傳遞管線(disposal/settle 兩函式簽名都不知道 --roster)
severity: major
引句:「時尾端附加**自動抑制**(全史已含當輪,不重複)」
佐證:file: `scripts/lumos:4753`
佐證:file: `scripts/lumos:10074`

### d-f2 settle 無 rid 概念,與 disposal 不同構——「閘判定的 rid」在 settle 端未定義
severity: major
引句:「rid=**閘自己判定的 rid 唯一輸入**(不得由 roster 重算)」
佐證:file: `scripts/lumos:4645`
佐證:file: `scripts/lumos:10099`

### d-f3 settle 記錄恆 round-less→__seqN→被自己的跳過規則吃掉:「補掛」=功能空炮,比漏接更隱蔽
severity: blocker
引句:「__seqN 合成鍵跳過不印」
佐證:file: `scripts/lumos:10101`
佐證:file: `scripts/lumos:4645`

### d-f4 「單家族」提醒不屬四類異常任何一類,而它正是常用 tier 外家缺席唯一會印的訊號
severity: minor
引句:「對帳無異常(席數足、家族齊、無兼任、無 unknown)→ **零輸出**」
佐證:file: `scripts/lumos:5108`
佐證:file: `scripts/test_lumos.py:22513`

### d-f5 既有輸出過半是無條件常印(摘要/診斷/conditional/duals),anomalies_only 的涵蓋對照 spec 沒給
severity: major
引句:「健康輪零輸出、異常行轉述式含辯方條件 hedge」
佐證:file: `scripts/lumos:5093`
佐證:file: `scripts/lumos:5110`

### d-f6 hedge 條件「低共識」全庫無資料源——判準只活在編排者當場判斷,從未落欄
severity: major
引句:「若本輪有存活 major 低共識條目則屬缺席」
佐證:file: `skills/lumos-design-loop/reference.md:140`

### d-f7 兩季回頭條件的「零出現」無持久記錄可查([roster] 只印 stdout)
severity: minor
引句:「兩季(2026-11-26)仍零出現→連旗標一併重審退場(寫入本案 Verification revalidate_when)」
佐證:file: `scripts/lumos:475`

## 已查證清單
見席位報告全文(session 留痕);工作區並行 lint 改動已排查不影響引用行號。
