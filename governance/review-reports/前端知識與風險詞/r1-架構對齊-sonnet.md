severity: minor

四問對照結果:沒有引入第二套解析器或設定讀法,也沒有跨層直呼,所以沒有 major。有 8 條 minor,其中有一條(第 1 條)會影響題目實際亮不亮。

## 1. 分層與依賴方向

新邏輯放的位置和既有同類一致。
- 需求風險面加列,放進 `_REQUIREMENT_FACETS`,由 `_pitfalls_stage` 比對文字。
- infra 題組進 `_STACK_QUESTION_SPECS`,由 `_stack_key_for_file` 分流,四個消費者自動跟上。
- 詞表例外直接改 `PITFALL_CLASSES` 的正規式。

有兩處排序不一致。

severity: minor
blocking: 否
引句:「這是刻意的:e2e 腳本不是產品畫面。」
file: `scripts/lumos:30326`

- 計劃把 infra 規則放在 `_stack_key_for_file` 最前面,並說 `e2e/` 底下原本被判成前端的檔不再附前端卡。
- 但 `_review_role_for` 在走到 `_stack_key_for_file` 之前,先用 `_ROLE_FRONT_EXTS`(30263)判副檔名。
- 所以 `e2e/` 或 `fixtures/` 底下的 `.tsx`、`.jsx`、`.html` 仍會判成前端並附前端卡。這個說法只對 `.ts` 和 `.js` 成立。
- 計劃要嘛明寫只限 `.ts` 和 `.js`,要嘛讓 infra 路徑樣式也排在副檔名判斷之前。

severity: minor
blocking: 否
引句:「不再拿 vue-reactive、sql-transaction 這類產品題」
file: `scripts/lumos:47272`

- 47272、47282、50086、46612 這幾個消費者,都先用 `_PITFALL_DIFF_TEST_PAT` 做 `continue`,才呼叫 `_stack_key_for_file`。
- 路徑像 `tests/e2e/x.sh` 會先被 `/tests?/` 擋掉,根本到不了 infra 規則。
- 這樣「四個消費者都經這一支」只對沒被測試樣式擋掉的路徑成立。計劃沒講這個順序。

## 2. 命名與錯誤處理

severity: minor
blocking: 否
引句:「六題,每題 when 只收那一題的寫法:」
file: `scripts/lumos:30503`

- `_stack_norm_line` 比對前會先剝掉字串字面,只有放進 `when_raw` 的 pattern 才看字串內容(例如 `_EXTCODE_WHEN_RAW`)。
- infra 的觸發詞 `/tmp/`、`localhost:數字`、`-p 數字:`、`--name`、`PORT=` 在 shell 裡多半出現在引號內,放進 `when` 會被剝掉,題目不亮。
- 計劃只寫 id、q、when 三個欄位,沒提 `when_raw`。S12 的測試行(`kill "$pid"` 加 `/tmp/`)也要避開這點。

severity: minor
blocking: 否
引句:「這份計劃是前端:設計審派工用 templates.md §7.7〈前端計劃改述〉」
file: `scripts/lumos:47751`

- `--check` 現在只輸出一行 `✓` 或 `✗`,加提醒也沒用 `提醒:` 前綴(其他警告走 stderr)。
- 計劃沒說前端面段在 `--json` 的 `pitfalls <計劃>` 分支要不要出現。既有分支會回 `hits`、`general`、`known_pitfalls`,S7 只釘人讀輸出。

severity: minor
blocking: 否
引句:「消費專案的 `scripts/e2e.sh` 不再拿 `graph-rename.sh` 當對照。」
file: `scripts/lumos:46644`

- 同一個概念(要跳過的自帶檔集合),`_stack_changed_ok` 用參數名 `skip`。`_arch_alignment_hints` 新增參數建議同名,不要另取名字。
- 新常數 `_FE_PLAN_WHEN` 沒帶家族前綴,不像 `_PITFALL_*`、`_ROLE_*`、`_STACK_*`。實作時順手改名即可。

## 3. 第二種做法

沒有引入新機制,但有兩處「同一個概念多一份定義」。

severity: minor
blocking: 否
引句:「框架名 React / Vue / Svelte / Angular / Next.js / Nuxt / Vite(前後不是英文字母)」
file: `scripts/lumos:30167`

- 「什麼算前端」目前已有兩份定義:`_NODE_FRONTEND_MARKERS`(30167)和 `_ROLE_FRONT_EXTS`(30263)。
- 計劃再加第三份寫在計劃文字上的詞表。輸入不同(文字,不是檔案或 package.json),但詞彙已經分岔:新表有 Vite,舊表有 solid-js 和 preact,新表沒有。
- 建議從既有兩個集合派生,或在註解寫明為什麼不能共用。

severity: minor
blocking: 否
引句:「新增一個路徑樣式常數(暫名 `_TEST_INFRA_PATH_RE`)」
file: `scripts/lumos:30608`

- 專案裡已有兩套「這是測試檔」的路徑判斷:`_PITFALL_DIFF_TEST_PAT`(30608)和 `_testmap_is_test`(47901)。
- 計劃再加第三套。每套語意不同,所以不算 major。
- 但新常數該放在 `_PITFALL_DIFF_TEST_PAT` 旁邊,並在註解寫明兩者的分工:前者整支排除,後者改歸 infra。

## 4. 落點

severity: minor
blocking: 否
引句:「加一節〈網頁前端(Vitest／Jest + Testing Library)的撰寫補充〉,至少三條:」
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:9`

- `commands/test-quality-standard.md` 沒有任何 Systems 節點的 about_code 列到它。
- lands_in 列了 `Systems/test-quality-cli`,但它只管 `scripts/test_quality.py` 一類的檔,負責範圍是「命令收證與 JUnit 一致性核對」,不含這份標準文件。要嘛擴那篇的範圍,要嘛另開一篇。
- 同樣的問題:`templates.md` 的家是 `Systems/每輪修補差異派工`,它的負責範圍(修補差異材料與副作用提問,第 6 行)裝不下 §7.7 前端改述和 §7.8 網頁前端資安類。
- 計劃只寫了 `規格閘`、`效能檢核目錄`、`情境出題` 各落什麼,沒寫 `design-loop`、`pitfalls-code-loop`、`每輪修補差異派工`、`test-quality-cli` 各寫什麼。
- 做法 7 改了 `_arch_alignment_hints` 的選鄰居邏輯,對應 `Systems/arch-alignment-lens`,但它不在 lands_in 裡。

severity: minor
blocking: 否
引句:「在 A 表之後加一個 ### 小節〈前端計劃改述〉(不改 A 表本身)」
file: `skills/lumos-design-loop/templates.md:421`

- §7.7 的小節是 A 和 C 字母編號(400 與 421 行),新小節插在中間會讓編號變成 A、前端改述、C。
- `scripts/lumos:29921` 的註解寫著「★三處同步:此處+templates.md:31+design-loop skill★」。計劃改 §1 第 5 點,卻沒提這個同步註解和 design-loop skill 第 2 步(SKILL.md:24)。
- 建議計劃寫明這些都要一起更新。

不對齊共 8 條,其中 major 0 條。

另外,`PITFALL_CLASSES` 的 payment 例外沿用 `(?-i:…)` 局部旗標寫法,有 `_STACK_QUESTION_SPECS` 的先例,沒問題。它用底線 lookaround 而不是 `(?<![A-Za-z0-9])`,和同表的 send、prod 寫法不同。計劃的 WHY 行已說明刻意只放寬 payment 一字,我沒列為發現。
