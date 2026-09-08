severity: blocker
# r2 邊界席(sonnet)——棧別提問表態閘(修訂稿驗收)

### B1 改檔前 hook 在編輯落地前執行,「目前檔案內容」抓不到即將寫入的觸發詞
severity: blocker
blocking: 是——Write 新檔磁碟上沒東西、Edit 的 new_string 還沒寫進去,最該攔的情境永遠抓不到;delta 早就算出來卻沒接。
引句:「沒命中任何題就不注入棧段。」
file: `scripts/hooks/claude/impact-hook.py:789`(`delta_q = extract_delta_query(payload)` 只餵 query 融合)、`scripts/lumos:19017-19021`(stack_questions 只看檔名)。

### B2 `test:` 證據要求 root 對 at_sha 乾淨,把 F3 換成更常見的假擋
severity: blocker
blocking: 是——同分支繼續開發是常態;無先例可佐證;逼人常態 --no-verify。
引句:「要求該平台 root 在 `git diff --quiet <at_sha> -- <root>` 下乾淨」
file: `scripts/hooks/pre-push:200-203`(每個 ref 都帶 --at-sha)。

### B3 表態 marker 檔要不要帶 head_sha 沒寫
severity: major
blocking: 是——本機 pre-push 讀 marker 不查治理帳,沒座標就判不出「對更早 commit 寫的」。
引句:「寫 `governance/code-loop/<branch>.dispositions.json`」
file: `scripts/lumos:20443-20452`(`_codeloop_write` 四欄含 head_sha)。

### B4 Vue 專案的 .ts/.js 主邏輯檔零覆蓋零稽核
severity: major
blocking: 是——`_stack_key_for_file` 對非 node 的 .ts 回 None,連 meta 未觸發紀錄都沒有;spec 沒裁定。
引句:「每題都必須有觸發；寫不出觸發的題本身就是設計問題。」
file: `scripts/lumos:15130-15136`。

### B5 「某棧 added 行 > 300」計算範圍未定(單檔還是該棧加總)
severity: major
blocking: 是——五檔各 61 行兩種讀法結果不同;S1 測試斷言寫法互不相容。
引句:「大改動全問：某棧 added 行 > 300」

### B6 `ask_all_over_lines` 合法值範圍未定(0/負數/字串)
severity: major
blocking: 是——跟 B5 對 config 錯誤「明講是設定檔問題」原則不一致。

### B7 `gate=off` 時樣板與寫側要不要逐題填沒定義
severity: major
blocking: 是——過渡閥沒跟著關,填一份沒強制力的 JSON,過渡意義落空。
引句:「可設 `all`（預設）／`high-only`／`off`，給消費專案過渡。」

### B8 pre-push if/elif 互斥怎麼重寫、standard 有適用題時訊息不該提代碼審
severity: major
blocking: 是——high+有適用題連既有 advisory 都不印;standard 缺表態≠缺審查,同一句話誤導。
引句:「tier standard 的既有 advisory 分支改成同一道閘。」
file: `scripts/hooks/pre-push:243` 附近。

### B9 CI 重建「取該 sha 最後一筆」沒講兩種 kind 各取最後一筆
severity: major
blocking: 是——不分 kind 取最後一筆會互相擠掉;既有讀側已示範必須按 kind 過濾。
引句:「同 sha 兩次 `dispositions` 寫入＝原子覆寫、治理帳兩筆，check 取該 sha 最後一筆事件（明文規則）。」
file: `scripts/lumos:20408-20431`。

### B10 理由門檻「含非 ASCII 就降到 10 字」一個中文句號就繞過
severity: major
blocking: 是——低成本繞過,削弱 B8 原意。
引句:「去掉空白後，含非 ASCII 字元的 ≥10 字、純 ASCII 的 ≥25 字。」

### B11 legacy 單平台下 `test:<平台>:<名>` 整段當方法名,訊息誤導
severity: major
blocking: 是——`resolve_test_refs` 只在 platforms 非空時切前綴;錯誤訊息是「找不到」不是「沒開多平台」。
引句:「裸名走 default_platform」
file: `scripts/lumos:3439-3456`。

### B12 BLOCKED 只列 10 問,沒講怎麼看全貌
severity: major
blocking: 是——另有 N 問看不到是什麼。
引句:「任一缺／原文不符／錨點壞 → BLOCKED」

### B13 「每題都必須有觸發」沒機械擋,空 when 的題永遠不觸發也不會進死題候選
severity: minor
blocking: 否。
引句:「每題都必須有觸發；寫不出觸發的題本身就是設計問題。」

### B14 分支名扁平化撞名/改名孤兒(既有風險原樣繼承)
severity: minor
blocking: 否。
引句:「寫 `governance/code-loop/<branch>.dispositions.json`」
file: `scripts/lumos:20388-20389`。

### B15 `when` 比對沒比照排除註解行與字串字面,虛增適用題污染統計
severity: major
blocking: 是——註解「// TODO remove GlobalScope」誤判適用;死題/觸發太窄統計失真。
引句:「做不分大小寫比對，任一命中＝適用」
file: `scripts/lumos:16719-16724`。

## 前輪驗收
B1 已解;B3 已解;B5 已解(覆蓋面不夠,見 B6/B7);B7 已解;B8 部分解(B10);B9 已解;B11 已解;B12 部分解(B12)。

最嚴重 blocker(B1/B2);blocking 共 13 條;minor 2。
