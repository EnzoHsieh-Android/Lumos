severity: minor

# 架構對齊審查 r3(Sonnet,末輪)

## 三問

1. 分層與依賴方向:沒有跨層直呼。`_probe_check_value` 仍在 `_probe_parse` 與 `_slot_retire_err` 之間共用(file: `scripts/lumos:3885`、`scripts/lumos:31975`);`_drift_specs` 把 `_drift_cat` 與 `_DriftProbeTree._read_raw` 原本各寫一份的「內容編號,查不到退回版本:路徑」收成一支(file: `scripts/lumos:32247`),方向正確(向內收斂,沒有新增反向依賴);方括號擋在 `_probe_bad_path` 一處,`_probe_value_err` 的 file/symbol/test/gone 四條路都經過它(file: `scripts/lumos:31994`、`scripts/lumos:31953`、`scripts/lumos:32007`)。
2. 命名與錯誤處理:新常數 `_PROBE_GONE_BACKTICK_MSG` 與鄰居 `_PROBE_KEYS`、`_REVISIT_MISPLACED_FIX` 的命名一致(file: `scripts/lumos:27981`);四處路徑錯誤訊息一起補「不能含方括號」,一致。差異只有下面 A1、A2。
3. 第二種做法:反引號檢查現在是兩個實作(回頭條件行用 `_probe_gone_backtick_err` 掃原文,RULE 撤除條件直接 `"`" in val`),共用同一句訊息。兩者輸入形狀不同(原文含剝除前的標記、撤除條件是已切好的值),這是 r2 架構對齊席要求的拆法,屬合理,不列。

## 發現

**A1 git 模式補問大小時重用已經耗掉一部分的 left,逾時預算被用兩次**
severity: minor
blocking: 否 — 只影響推送判定的總逾時上限,不影響判定結果,結構是對的
引句:「sizes = _nodehome_cat_sizes(self.root, [specs[i] for i in miss], timeout=left) if miss else []」
1. 輸入:git 模式、`self.deadline` 還剩 N 秒,`_read_raw` 走到批次讀(`left = ... self.deadline - self._t.monotonic()` 在函式前段算一次)。
2. 走到:`_nodehome_cat_blobs_capped(..., timeout=left)` 先跑(它內部已經是「問大小一次、讀內容一次」,各吃 `left`),再用同一個沒重算的 `left` 跑第二次 `_nodehome_cat_sizes`。
3. 壞在:鄰居的做法是一次預算算一次、一次呼叫用掉(file: `scripts/lumos:32339` 的 `_read` 路徑 `left = ... ; blobs = _drift_cat(..., left)`);這裡讓同一個 deadline 最壞被用超過一次。既有 `_nodehome_cat_blobs_capped` 內部兩次呼叫共用同一 timeout 也是這個形狀,所以這是沿襲而非新創,但新增的第三次呼叫是本 diff 加的。補問前重算 `left = max(1, self.deadline - monotonic())` 即與 `_read` 對齊。未能重現成逾時(要造 git 卡住),純結構比對,維持 minor。

**A2 為了分開講「太大」與「讀不出」,在批次讀函式外面重問一次大小 ⚠**
severity: minor
blocking: 否 — 結果正確,只是同一份大小資訊被問兩次,沒有第二套判定
引句:「# 帶上限的批次讀把「太大」與「讀不出」都回 None;只對這幾支再問一次大小,分開講(代碼審 r2 架構對齊席)」
1. 輸入:git 模式讀任何帶字串的 `when-gone` 條件,且至少一支回 None。
2. 走到:`_nodehome_cat_blobs_capped`(file: `scripts/lumos:26527`)內部已經呼叫過 `_nodehome_cat_sizes`,知道哪些是超過上限,卻把兩種原因都丟成 None;呼叫端為了區分,再起一個 `git cat-file --batch-check` 行程。
3. 壞在:資訊本來在鄰居那一層就有。更貼近既有分層的做法是讓 capped 那層回傳「太大」標記(其他呼叫者 `scripts/lumos:23838`、`scripts/lumos:42680` 目前不在意區別,所以不是 bug);現在做法功能上等價,只多一次行程,且只在 None 出現時才多。⚠ 判不準這算「第二種做法」還是可接受的局部補丁,先以 minor 記。

## 沒問題的項目

- 方括號擋法放在 `_probe_bad_path` 一處、四種鍵統一,沒有逐點補丁。
- `_probe_gone_err` 只剩 gone 專屬檢查(路徑規矩交給 `_probe_bad_path`),沒有複製一份。
- `_drift_gone_text` 的 `None` → 「讀不出」、`_DRIFT_RAW_TOO_BIG` → 「超過」分流與 `_DriftProbeTree.gone`、`unread_for` 的原因文案管線一致。
- 測試 `t_drift_when_gone_review_r2` 沿用 `_nh_repo`、`_nh_file`、`_na_head`、`check` 既有輔助(file: `scripts/test_lumos.py:44009`、`scripts/test_lumos.py:52096`),命名跟 `t_drift_when_gone_review_r1` 一致。
- 反引號奇偶判斷與 `_probe_parse` 前的行內程式碼剝除是同一個讀法,沒有出現新的分歧。

## 固定席節點

- lens.txt 列的固定席(bound-tests-gate、guard-kill、lumos-cli-read、lumos-cli-lifecycle、design-loop 等)本次 diff 沒有牴觸其 INVARIANT 的改動;`_reinject_all` 與範本注入區塊在本 diff 未動(計劃文件只記錄 r3 前已做的重注入)。

最高 severity:minor
