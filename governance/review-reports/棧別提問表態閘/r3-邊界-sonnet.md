severity: blocker
# r3 邊界席(sonnet)——棧別提問表態閘(末輪)

前輪 B1–B15 全數複核已解(B10 原範圍已解,CJK 範圍另見 B6;B14 以刻意不做承接)。

### B1 merge main 進分支後兩點式範圍把 main 帶入的檔算成本次要表態
severity: blocker
blocking: 是——日常 merge 變成擋推送、要對他人已審的碼表態;無既有例外。
引句:「閘條件：diff 有適用題就擋，不看 tier」
file: `scripts/hooks/pre-push:179`。

### B2 `git grep -F` 子字串比對,撞名方法可偽造「已提交」
severity: blocker
blocking: 是——樹裡只有 testFooBar,grep testFoo 仍 exit 0;推翻「未提交的測試自然過不了②」。
引句:「未追蹤、未提交的測試檔自然過不了②」

### B3 id 唯一沒列進機測
severity: blocker
blocking: 是——list 不是 dict,重複 id 讓另一題被靜默視為已表態。
引句:「模組載入時編譯；空 when 或壞 regex 測試翻紅」

### B4 20 秒預算半途超時,已掃出的 BLOCKED 是丟是留沒講
severity: major
blocking: 是——可能把已確認的違規改判放行。
引句:「超時走既有 fail-open 進治理帳」

### B5 at_sha 為空時 test: 第②道沒定義
severity: major
blocking: 是——本機直接叫 check 是必試邊界。
引句:「沒有 at_sha（本機直接叫 check）退回工作樹」

### B6 CJK 範圍含不含假名/諺文沒說(minor,⚠)
severity: minor
blocking: 否。
引句:「去掉空白與標點後，CJK 字元 ≥10 個」
file: `scripts/lumos:2345`、`scripts/lumos:2682`。

### B7 多平台 root 在 repo 外 git grep fatal(minor)
severity: minor
blocking: 否——失敗方向是拒絕。
file: `scripts/lumos:3394`。

### B8 recall-miss 打錯 id 沒驗證(minor)
severity: minor
blocking: 否。
引句:「lumos code-loop recall-miss <id> --note」

### B9 搬家計數不對稱(minor)
severity: minor
blocking: 否——兩種結果都偏安全。
file: `scripts/lumos:16717`。

### B10 id 沒有格式規則(minor)
severity: minor
blocking: 否。
引句:「大小寫不對的錯誤訊息明講」

最嚴重 blocker(B1/B2/B3);blocking 共 5 條;minor 5 條。
