severity: major

F1（第二種做法）
severity: major
blocking: 是
引句:「掃描先辨識一般反引號／波浪號圍欄，其內示例忽略；未閉合一般圍欄也列解析錯誤，避免其後登記被隱藏。」
規格要求專用解析器辨識一般圍欄、巢狀示例與未閉合錯誤，卻未規定重構並共用既有唯一圍欄狀態機。現有 `_visible_lines` 明定為「全檔唯一」實作，而且只回傳可見行，不回傳未閉合診斷；照用無法滿足 S2，另寫掃描器則形成第二套圍欄語意。file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:48`；file: `scripts/lumos:364`；file: `scripts/lumos:4936`；file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:27`
最小重現：輸入 `before\n```text\nhidden\nafter`，實跑 `list(_visible_lines(text.split("\n")))` 得 `[(1, "before")]`，沒有可供盤點輸出 `malformed_block` 的未閉合狀態。修規格時應指定抽出共用 fence-state 原語，讓 `_visible_lines` 與安全區塊解析共同消費；並以四反引號包住 `lumos-security-v1`、未閉合圍欄、縮排圍欄三組對照翻紅，禁止另寫第二個 toggle/regex。

1 分層依賴：已讀，無 finding。`Env.from_texts`、`env_text`、`extract_contracts` 的規劃方向符合既有記憶體快照層，未見跨層直呼。file: `scripts/lumos:631`；file: `scripts/lumos:700`；file: `scripts/lumos:765`

2 命名與錯誤處理：已讀，無 finding。`reported_status`、`evidence_check`、`read_complete`、`registration_complete` 分工一致；rc2 與 stderr／JSON stdout 分離也對齊既有 CLI 慣例。file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:40`；file: `scripts/lumos:29553`

3 第二種做法：除 F1 外已讀，無 finding。正文 JSON 比現有僅支援純量、字串清單與 block scalar 的 frontmatter parser 更適合此巢狀 schema，未因「新功能新資料」本身判 major。file: `scripts/lumos:526`

4 lands_in 與模組責任：已讀，無 finding。留在 `Systems/lumos-cli-read` 與其既有 `scripts/lumos` 家相符；拆新檔時另建 System 家的條件也已寫明。file: `governance/review-reports/資安護欄唯讀盤點/r1-snapshot.md:32`；file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:111`

總結：最嚴重 severity major；不對齊 1；blocking 1。
