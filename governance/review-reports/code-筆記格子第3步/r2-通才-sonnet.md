severity: minor

我沒有找到 blocker 或 major。我在 repo 自己的圖譜和自造的小消費 vault 上,拿改前版本 2f9cb94f 和改後版本 384f4574 各跑 doctor、doctor --verbose、doctor --ci、drift scan、drift check,只找到一條 minor。

**R2U1 S16 接回續行後,摘要寫成單行純量的 RULE 不再被 S16 列出(只多不少的前提不成立)**

severity: minor
blocking: 否 — 只影響軟提醒,不計入問題數,不擋推送。

1. 改前 `_doctor_stale_rules` 逐行讀「解析後的摘要字串」,改後改用 `_ns_summary_logical` 對重組的前言區文字找前綴行。這支只認 `summary: |-` 這類縮排區塊,不認同一行的值。
2. 重現:vault 內放兩篇筆記,摘要分別寫成 `summary: "RULE:引號單行 [since:2025-01-01] [retire:人裁]"` 和 `summary: RULE:純量單行 [since:2025-01-01] [retire:人裁]`,跑 `lumos doctor --verbose`。改前版本在 S16 列出這兩條「沒寫 [confirmed:]」,改後版本一條都不列。同一個 vault 裡 `summary: >-` 折疊、`|` 字面、跨空行三種寫法兩邊輸出一致。
3. 影響:使用者的 doctor 輸出在這個寫法下會少一批 S16 提醒,不是多。這個寫法在本 repo 的圖譜上沒有出現,所以 repo 自己的改前改後 diff 看不到。
4. 判斷 ⚠:S17 到 S19 和提交時檢查本來就走 `_ns_summary_logical`,所以 S16 變成與它們一致,可能是刻意的。但改後的註解只說「續行接回」,沒交代單行純量被丟掉。改法是在說明裡寫明,或對單行值補一條路徑。

引句:「        for t in _ns_summary_logical("---\n" + "\n".join(n.fm_lines) + "\n---\n").values():」

**通才鏡頭:我實測過、確認沒問題的部分**
- **repo 自己的圖譜**:doctor --verbose 改前改後只差兩處。S17 的一條既有誤報消失(`Systems/lumos-cli-read.md:14` 是說明句,不是作廢行),總提醒數 257 降為 256,沒有新增的提醒。S16 在本 repo 沒有變化。
- **S16 續行**:欄位寫在續行的 RULE 不再被誤判成「沒寫 [confirmed:]」。我造的 vault 裡,同一條 RULE 改前列「沒寫 confirmed」,改後正確列「超過 180 天沒確認」。
- **doctor 崩潰**:改前版本在 `[retire:度量 … 近99999999999週]` 時 `OverflowError` 整個 doctor 崩潰,改後這條列成「度量寫法不合,不判(週數只收 1 到 8)」,拼錯閘名也同樣列出。
- **S18 取得設定**:壞掉的 `.lumos/config.json` 和欄位型別錯誤的設定,S18 都照常輸出。設定寫 `[1,2]` 時 doctor 在更早的 S3 崩潰,但改前版本也一樣(`load_symbol_profile` 對 list 呼叫 `.get`),與這份 diff 無關。
- **閘判斷**:六個閘(含沒有設定檔時)都不崩,lint_new 關掉時 `lint-new` 度量被正確略過。
- **S17**:`[[X#段落]]`、`X.md#d1`、`[[X.md]]`、`X#d1` 四種寫法都能解析,沒有誤報。
- **drift scan**:retire 兜底列出的成立條目含續行形式,改法提示與改前一致;`drift check` 在無參數時給出的用法提示也正常。
- **S19**:預設只列 3 條並提示用 `--verbose` 看全部,訊息看得懂。
- **測試**:`-k slots` 183 項全過。`-k doctor_metric` 選中 0 個,是測試名子字串用錯,不是失敗。
- **回滾**:S17 到 S19 不寫帳,還原提交後沒有留下持久狀態。推送那支的帳是只增不改,舊帳留著無害。

**圖譜鏡頭**
- 派工尾端沒有附固定席筆記,也沒有「圖譜沒有釘到節點」備援段,所以沒有逐條要答的節點。
- 我只用 diff 內附的筆記變更判斷,結論是不影響:
  - `Systems/存量漂移守衛` 的 WHY 說「doctor 不評估 when-*」,程式仍是如此。度量式另走 S18,這份 diff 已在筆記裡寫明。
  - `Systems/lumos-cli-read` 說 S17 到 S19 不寫治理帳,程式確實沒寫。
  - `Issues/撤除條件檢查末輪遺留四項` 由 done 改回 doing,與「推上主線後結案」的做法一致。

最高嚴重度 minor,blocking 0 條
