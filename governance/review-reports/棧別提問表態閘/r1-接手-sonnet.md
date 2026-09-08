severity: blocker
# r1 接手席(sonnet)——棧別提問表態閘


## Findings

### H1 CI 讀不到剛寫入的表態,tier=high 通過本機審查的推送在 CI 會被誤擋
severity: blocker
blocking: 是——CI 後盾路徑必然觸發,直接讓已過審的推送假紅,不是邊界情境。
引句:「讀當前 sha 的 pass 記錄,逐問核對」
`governance/code-loop/` 整個目錄被 gitignore(file: `governance/.gitignore:10`,註解明講「本機守衛用,不版控、不跨機當權威」),CI 用 `actions/checkout@v4` 全新結帳絕對讀不到 marker 檔,`code-loop check` 這時走 `_codeloop_read_from_ledger`(file: `scripts/lumos:20135-20160`)重建記錄,但那支重建只回 `{status,head_sha,note,ts,_source}` 五個鍵、沒有 `dispositions`。CI 那一步正是 file: `.github/workflows/ci.yml:48` 跑的 `code-loop check --diff … --repo .`,是 pre-push 被 `--no-verify` 繞過後唯一的後盾。

### H2 `gov --stats` 的資料源頭已經在濾掉多餘欄位,S6 的按問題彙總拿不到 `dispositions`
severity: major
blocking: 是——不修這個 mapper,S6 承諾的統計功能完全不會出現,且不報錯、無人知道壞在哪。
引句:「按問題原文彙總歷來 `satisfied/na/todo` 次數」
`cmd_gov` 讀 `.governance-log.jsonl` 的 mapper(file: `scripts/lumos:4695-4697`)白名單只挑 `ts/commit/gate/kind/hard/nodes/detail` 六個鍵,任何額外欄位一律丟棄——同一支 `_gate_event`(file: `scripts/lumos:898` 的 `if extra: ev.update(extra)`)寫進去的 `tier` 欄位就是現成的先例,今天已經被這個 mapper 悄悄濾掉。

### H3 派工鏡頭要附的「表態」在派工當下根本還不存在
severity: major
blocking: 是——S5 描述的能力(對稱辯方機制)在主要工作流程下是死碼,不是邊界案例。
引句:「派工單附上實作者表態讓席位反駁」
file: `skills/lumos-code-loop/SKILL.md:19`(步驟 2·派審查員)在審查開始前發生,而 `dispositions` 只在 `code-loop pass --dispositions` 才寫入(file: `skills/lumos-code-loop/SKILL.md:29`,步驟 8·過了留痕之後),兩者順序相反。單輪審查流程裡,`cmd_dispatch_lens` 要讀的「pass 記錄裡的表態」在派工那一刻幾乎必然不存在。

### H4 S7 的「建議改成 check 會擋」會覆寫掉同一句裡本該保留的 tier=standard 分句
severity: major
blocking: 是——違反「不能誇大機制效力」鐵則,寫出的文件會誤導下一個讀者以為 standard 也被機械擋下。
引句:「code-loop skill 步驟 8 與 reference 棧別段改寫」
file: `skills/lumos-code-loop/reference.md:283` 唯一命中的「建議」字樣,同一句後半緊接著「tier=standard 走單 reviewer 時同義務落在終審紀錄/commit message」——這半句在新設計裡仍然只是提醒(S4:rc 不變),若照字面把「建議」整句換成「check 會擋」,會讓文件宣稱 standard 也被擋,牴觸 S4。

### H5 S7 漏列 `效能檢核目錄.md` 的三時機 KEY 行
severity: minor
blocking: 否——純屬文件一致性缺口。
引句:「code-loop skill 步驟 8 與 reference 棧別段改寫」
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:26` 現在仍寫「③code-loop pass 留痕須含檢核答案」(「須」),而 reference.md:283 已在 2026-08-21 降成「建議」;本案把 tier=high 重新變回機械強制後,這行本該同步更新,但 S7 沒把這個節點排進去。

### H6 `test:` 錨點驗證假設單一 test profile,跟既有多平台索引機制不對齊
severity: minor
blocking: 否——本 repo 不會觸發,只在下游多平台消費專案才會出現空缺,且有既有機制(`_platform_test_index`)可填。
引句:「用該 repo 的 test profile 跑 `discover_test_methods`」
file: `scripts/lumos:7893` 的 `_platform_test_index` 之所以存在,就是因為部分消費專案是多平台。

### H7 `todo` 錨點只驗檔案存在,不驗跟哪一問相關,是三種狀態裡最好敷衍的一種
severity: minor
blocking: 否——是已承認風險的加重版本。
引句:「只查檔案路徑存不存在、不載入圖譜」
`todo` 只要任一 `Issues/<名>.md` 存在即可,agent 可以把每一問全指向同一篇既存但無關的 Issue 就過關。

### H8 ⚠ 簿記豁免路徑下,被核對的 dispositions 可能對應的是舊 diff 範圍
severity: major
blocking: 是——若真的錯配,會出現「明明簿記豁免生效卻因為鍵對不上被判缺表態」的假擋,但需要實測才能定案。
引句:「留痕本來就綁 sha,改碼即失效」
file: `scripts/lumos:20649-20661` `_codeloop_guard_verdict` 有一條既有的簿記白名單豁免:祖先 sha 的 pass 記錄在其後只動簿記檔時仍算有效,但這時拿去核對表態的 `diff_range` 其實是新 sha 對應的範圍,不必然等於當初產生 dispositions 那次的命中棧集合。⚠ 待驗證。

### H9 `--dispositions <json>` 沒說是內容還是檔案路徑,跟既有 `--from-json <path>` 慣例不一致
severity: minor
blocking: 否——不管哪種實作都可行,只是需要補一句裁定。
引句:「`code-loop pass --dispositions <json>`」
file: `scripts/lumos:22233-22234` 同一個 `code-loop check` 底下已有 `--from-json`,明確吃「已經算好的結果」檔案路徑。

## 已讀,無 finding
- 統計拿什麼當鍵:spec 用 `question` 原文當彙總鍵,設計正確。
- `--dispositions-template` 與既有 `--json` 是否兩套 diff 掃描:`_pitfall_diff_collect`(file: `scripts/lumos:16404`)本來就一次算出 `stack_questions`,可重用同一次計算。
- `dispatch-lens-hook.py`:純轉發 `cmd_dispatch_lens` 回傳的 `text`(file: `scripts/hooks/claude/dispatch-lens-hook.py:14-16`),不需要另外改。
- ARCHITECTURE.md 第 4 節 pre-push 閘序圖:新增的表態失敗理由仍落在同一個 BLOCKED 出口,圖不需要改。
- convergence-evidence-gate / finding-refute:類比借用,沒被改動。

## 總結
最嚴重 severity 為 blocker,blocking 共 4 條(H1、H2、H3、H4;H8 為 ⚠ 未定案)。
