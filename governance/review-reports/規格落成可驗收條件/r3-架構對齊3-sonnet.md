severity: major

## 一、分層與依賴方向

**對齊。** 逐項核對凍結稿列的六個機制,層級與呼叫方向都跟既有做法同層,沒有找到跨層直呼。

- `_excluded_line(line)` 是判定(跳不跳)與證明(算不算四行之一)共用同一支解析——這正是本 repo 既有慣例(例如 `_visible_lines`/`_search_visible_lines` 全檔唯一、共用給多處呼叫,`scripts/lumos:160`「★一律改用 `_visible_lines`(全檔唯一的 fence 判定)★」),沒有另開第二套。
- 合約行掃描(`★IRREVERSIBLE★`/`★CHECKPOINT★`)明講「這條走的是合約行掃描那一支(`cmd_contracts`/`IRREVERSIBLE_RE`/`CHECKPOINT_RE`)」,查得到這三個名字都是既有符號:`cmd_contracts` 在 `scripts/lumos:4029`、`IRREVERSIBLE_RE`/`CHECKPOINT_RE` 在 `scripts/lumos:3859-3860`——沒有重寫一套合約掃描,呼叫方向是「新指令借用既有掃描」,跟 `cmd_pitfalls`/`cmd_spec_trace` 借 `_clause_bindings_for` 是同一種借法。
- 留痕走 `cmd_canary` 單一寫入口、擴充 `kind` 列舉:`scripts/lumos:27888` 現在是 `cr.add_argument("kind", choices=("caught", "missed", "none"))`,凍結稿講清楚要擴充這個封閉列舉、`_round_valid_m2`(`scripts/lumos:6356`)要同步認得——維持既有「單一寫入口」慣例,不是另開路徑。
- 推送閘範圍限定(只讀本次範圍碰到的計劃)沿用 `_plans_in_range`(`scripts/lumos:7468`,已被 `_ci_red_escape`、pre-push 兩處呼叫),不是新邏輯。
- **「規格閘裡呼叫 git log 是不是本 repo 第一個『vault 指令跑 git』?」——不是。** `scripts/lumos:1498` 的 doctor Section I 已經在跑 `git -c core.quotepath=false log --diff-filter=A --since=... --name-only`(掃 `governance/review-reports/` 算迴圈首見序),而且整支檔有五十處以上 `subprocess.run(["git", ...])`(`git show`、`git diff`、`git merge-base` 等遍布 `cmd_*` 各處)。`git log -S"def <測試名>" --diff-filter=A` 只是同一族「vault 指令 shell 出去問 git 歷史」用法的新旗標,不是第一次跨進 git 這一層。

引句:「判定(跳不跳)與證明(算不算四行之一)共用同一支解析 `_excluded_line(line)`」

severity: clean

## 二、命名與錯誤處理

**對齊。**

- `--finding-severity` 值域:`clean/minor/major/blocker`,跟 `_SEV_ORDER = {"clean": 0, "minor": 1, "major": 2, "blocker": 3}`(`scripts/lumos:5379`)、`_SEV_DECL_LINE_RE`(`scripts/lumos:5427`)、既有 `--finding-severity` 錯誤訊息(`scripts/lumos:5992-5996`,已落地)完全同值域,不是新開一套等級。

引句:「逐條嚴重度走新的 `--finding-severity`;沒給就退回「輪級 major 且任一條 code」並在逃逸帳標 `precision: round`」

- `precision` 欄位值 `finding`/`round`:對照實際落地程式,`scripts/lumos:6203`(`_precision = "finding"`)、`scripts/lumos:6208`(`_precision = "round"`)——這條規則不是紙上設計,是已經在跑的程式碼;寫法是透過 `_auto_escape` 的 `extra` 參數(`scripts/lumos:7522` 定義簽名含 `extra=None`,`scripts/lumos:7569-7570` `if extra: rec.update(extra)`)附掛到記錄上,跟既有 `attribution` 欄位值 `ledger`/`plan-file`(`scripts/lumos:7552-7554`,同樣是 `_auto_escape` 內建欄位)是同一種「主記錄體 + 附掛診斷欄位」的形狀,命名風格(小寫英文單詞)也一致。
- `door_rule` 版本欄:雖然沒有逐字同名的既有欄位,但「規則版本號釘進留痕、改版後從零重算視窗」這個形狀有直接先例——`_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE`(`scripts/lumos:4599`、`4599`/`15805`)就是「規則生效時間戳當版本切點,不回溯」;另外 `anchor-baseline.json` 本身也有 `"version": 1` 頂層版本欄(`governance/anchor-baseline.json:2`)。凍結稿新增的 `_SPEC_GATE_SINCE` 常數命名完全承襲既有 `_XXX_GATE_SINCE` 家族,是同款不是新款。
- `door` 值 `one-way`/`two-way`:已經是落地程式的字面值(`scripts/lumos:7559` `door != "two-way"`),跟既有 `tier` 欄位小寫英文值(`high`/`standard`/`light`)同一種形狀。
- 擋下訊息三段式白話:凍結稿沒有逐條示範新訊息文字,但既有 `_auto_escape`/`pre-push` 的擋下訊息(如「逃逸自動記:「{loop_id}」沒有雙向門留痕…不記」)已經照「發生什麼→為何在意→怎麼辦」寫,凍結稿沒有偏離這個腔調。

- **上一輪(r2)本席報告的 3 條 minor 已全部折入,查證屬實**:①`push-gate:unreviewed` 冒號複合值 → 凍結稿與已落地程式(`scripts/lumos:7559`、`scripts/hooks/pre-push:245`)一律已是連字號 `push-gate-unreviewed`;②git tag 回退錨與既有「錨」機制混淆 → 凍結稿第 277 行已改成「落地那次提交的 sha 落地時填進這裡」,不再提 git tag;③`lands_in` frontmatter 與正文重複兩處兩種格式 → 凍結稿第 233 行只剩「落點見開頭欄位 `lands_in`」一句指向,正文不再重複列格式。

引句:「記成 `push-gate-unreviewed`(連字號,本 repo 欄位值沒有冒號複合詞)」

file: `scripts/lumos:6203-6208`(`precision` 兩值已是落地程式)、`scripts/lumos:7522`(`_auto_escape` 的 `extra` 參數簽名)、`scripts/lumos:4599`(`_CLAUSE_GATE_SINCE` 命名家族先例)

severity: clean

## 三、第二種做法

**不對齊一條(major):`_excluded_line` 的「去清單前綴」規則跟本 repo 既有同用途函式用了不同的字元集,是第二套「去前綴」解析。**

凍結稿寫:

引句:「去掉行首空白、清單前綴(`-`/`*`/`數字.`)與引用符 `>` 再比;冒號半形全形都收」

但本 repo 已經有一支處理「判斷一行是不是清單項、要去哪些前綴才算進入內容」的既有正則,而且範圍明顯更寬:

file: `scripts/lumos:4589` ——`_CLAUSE_LEAD_RE = re.compile(r"^[\s>*#\-\d.、|+•—·)]*" + _CLAUSE_ENUM + r"(?:\[[ xX]\]\s*)?(?:\*\*)?\s*\[S(\d+)\]")`,用於「條款定義行」判定,去前綴的字元集含 `- * + • — · # | 、 )` 與勾選框等,涵蓋範圍遠大於 `_excluded_line` 只認的 `-`/`*`/數字.`/`>`。

這不是同一件事的兩種措辭差異,是同一份文件裡「判斷一行是清單項要跳過哪些開頭符號」這個子問題,被兩支獨立、字元集不重疊的正則各自實作一次——凍結稿的「已排除:」行若以 `_CLAUSE_LEAD_RE` 已支援的 `•`、`—`、`·`、`)` 開頭(例如「• 已排除:守衛面:理由」),`_excluded_line` 不會剝掉那個前綴,判定結果會跟 `_CLAUSE_LEAD_RE` 對同一行的「是不是清單項」判斷不一致(第 133 行自己也承認「縮排/引用塊/全形冒號的變體否則會讓自我否決復發」,說明作者也在擔心變體漏接,但沒有選擇借用既有更寬的字元集,而是又寫了一支窄的)。凍結稿的 PRIOR-ART 明講「不動筆記結構、不做自動生測試」「借用不自建」,但這處具體實作沒有借用已經存在、範圍更廣的同類解析,構成本題定義下的「第二種做法」。

severity: major

## 四、落點

**對齊。** `scripts/hooks/pre-push` 目前已經同時登記在兩篇既有節點的 `about_code`——`Systems/anchor-integrity.md`(`about_code: … scripts/hooks/pre-push`)與 `Systems/每支檔有家.md`(`about_code: … scripts/hooks/pre-push`),這是既有狀態,不是凍結稿造成的。凍結稿要新開 `Systems/規格閘` 再管 `cmd_spec_gate`、`_clause_check`、`_excluded_line` 與 pre-push 新增段落,等於讓 pre-push 多一個第三個家;`scripts/lumos` 本身也會同時被 `Systems/design-loop`(`about_code: scripts/lumos`)與新 `Systems/規格閘` 兩篇管。

這種「一支檔多個家」不是本題定義下的違規——`Systems/每支檔有家.md` 自己明文承認並定義了處置方式:

引句:「天花板:散文講另一支也有家的檔、家很多的檔(本工具鏈主程式有 31 篇,2026-09-12 機械數)寫進哪一個家,都驗不出來——落點靠規則五(計劃 lands_in、設計審看)」

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:29`(`scripts/lumos` 機械數已有 31 篇家,是本 repo 目前家數最多的檔);`docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md`(`about_code` 含 `scripts/hooks/pre-push`)對照 `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`(`about_code` 同樣含 `scripts/hooks/pre-push`)——這支檔本來就已經有兩個家,不是本案第一次出現多家情形。

凍結稿的處理方式(frontmatter `lands_in` 明寫兩個目標節點、正文只指回 frontmatter 不重複列)正是「落點靠規則五(計劃 `lands_in`)」這條既有機制指定的用法,`_ci_step_is_test`/`--finding-severity` 這些已落地改動該記進哪篇,凍結稿也回答了(記進 `lands_in` 列的那兩篇,依內容性質分——句式/門/綁定判定進 `Systems/規格閘`,處置閘第五步契約行改寫留在 `Systems/design-loop`),跟現況「`Systems/design-loop` 的處置閘 ★INVARIANT★ 已經記在該節點裡(`docs/lumos-toolchain-knowledge/Systems/design-loop.md:39`)」的做法一致,沒有另開第三種記法。

引句:「`Systems/規格閘` 管 `cmd_spec_gate`、`_clause_check`、`_excluded_line` 與 pre-push 新增的「條款測試全綠」段落」

severity: clean

不對齊共 1 條,其中 major 1 條。
