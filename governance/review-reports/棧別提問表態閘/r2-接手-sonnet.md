severity: blocker
# r2 接手席(sonnet)——棧別提問表態閘(修訂稿驗收)

前輪驗收:H1 未解(見 H2 事件形狀)、H2 部分解(見 H1 分類表)、H3 已解、H4 已解、H5 部分解(表格行 142)、H6 已解、H7 已解、H8 已解(`_BOOKKEEPING_DIR` 整目錄前綴)、H9 已解。

### H1 新 kind 會讓「審查迴圈關門分類」機械守衛翻紅
severity: blocker
blocking: 是——`t_loop_close_kinds_classified` 掃真實治理帳,每組 (gate,kind) 都要在 LOOP_CLOSE_EVENTS/LOOP_NOT_CLOSE_EVENTS 歸類;本 repo 跑一次 `code-loop dispositions` 測試立刻紅。
引句:「cmd_gov load mapper 與 _render_gov_stats」
file: `scripts/lumos:6316-6335`、`scripts/test_lumos.py:32079-32112`。

### H2 治理帳事件範例缺 branch/head_sha
severity: major
blocking: 是——`_codeloop_read_from_ledger` 用 `ev.get("branch")==branch` 與 `head_sha` 配對。
引句:「並追加治理帳事件 `{"gate":"code-loop","kind":"dispositions","commit":<head_sha>,"dispositions":{…}}`」
file: `scripts/lumos:20408-20440`、`scripts/lumos:889-897`。

### H3 hook「目前檔案內容」對新檔永遠觸發不了;既有 `extract_delta_query` 沒接
severity: major
blocking: 是——Write 新檔在編輯前不存在;既有 delta 機制已接進 impact 的 query。
引句:「跑同一組 `when`，只注入命中的題；沒命中任何題就不注入棧段。」
file: `scripts/hooks/claude/impact-hook.py:412-447`、`scripts/lumos:19016-19021`。

### H4 `decision-supersede` 對指名節點不可執行
severity: major
blocking: 是——該節點沒有 `decisions:` 欄位,裁定寫在散文裡;要先 `decision-add`。
引句:「的裁定（當時前提是整棧全問，現在前提變了），記進 pitfalls棧別效能追問_計劃 的決策。」
file: `scripts/lumos:10881-10882`、`docs/lumos-toolchain-knowledge/Projects/pitfalls棧別效能追問_計劃.md`。

### H5 既有測試樣本要同時「全表觸發」與「逐題隔離」,互相拉扯
severity: major
blocking: 是——S2 字面寫不出來。
引句:「既有 `t_pitfalls_stack_questions` 的樣本改成會觸發全表的內容」
file: `scripts/test_lumos.py:19061-19093`。

### H6 question 原文當機械錨點兼統計鍵,措辭一改就擋在途分支、統計歸零
severity: major
blocking: 是——同一份題表有措辭演進先例;無機制無 REVISIT。
引句:「不等就當缺（r1 外家 F5：表換順序後舊答案不得套錯題）」
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:26`。

### H7 S10 之外至少四處文件會與新設計矛盾
severity: major
blocking: 是——commands/02 說 tier:high 才觸發、ARCHITECTURE 流程圖 (tier=high)、pitfalls-code-loop FLOW 三分支、效能檢核目錄第 142 行表格「注入該棧全表問」。
引句:「注入該棧全表問(現行 kt=7/cs=5/vue=5/sql=4,單源=_STACK_PERF_QUESTIONS)」
file: `skills/lumos-project-notes/commands/02-動手前算波及.md:6`、`ARCHITECTURE.md:176`、`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:30`、`docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:142`。

最嚴重 blocker(H1);blocking 共 7 條。
