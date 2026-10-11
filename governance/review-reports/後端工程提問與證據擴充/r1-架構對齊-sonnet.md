severity: major

這份設計大體掛在既有機制上,方向對齊;但有兩處結構上的第二種做法或跨層落差,和三處命名與錯誤處理不一致。

### 問 1 分層與依賴方向

新指令的分層大致和既有指令同形:

- `evidence run` 由 Lumos 代跑指令並落帳。這和 `cmd_guard_kill`(file: `scripts/lumos:17298`)是同一型:CLI 子命令自己跑指令、自己寫帳,不經過 hook。
- `pitfalls --stage` 加在 `cmd_pitfalls(md, diff, ...)`(file: `scripts/lumos:42832`)的參數上,不新增指令,和既有做法一致。
- `decision-add` 加選填欄位,延續 `cmd_decision_add(env, rel, content, decided, context, why)` 的簽名風格(file: `scripts/lumos:20434`)。

我只找到一處落差。「規格閘讀〈待決問題〉」「交付前證據檢查帶階段進 `pitfalls`」都要求關卡去呼叫 `pitfalls`。目前 `pitfalls --diff` 是獨立指令,規格閘不呼叫它。這條新的呼叫方向設計稿沒寫清楚由誰實作、放哪一層。

severity: minor
blocking: 否
引句:「規格閘帶需求與架構;交付前證據檢查帶驗證、效能、交付」
file: `scripts/lumos:8168`(`cmd_spec_trace` 是獨立指令、不呼叫 `pitfalls`)
說明:先決定是規格閘直讀〈待決問題〉,還是閘去呼叫 `pitfalls --stage`,在設計稿寫明。⚠ 這是設計空白,不是已確定的違反,交編排者判。

### 問 2 命名與錯誤處理

三處和鄰居不一致。

**回傳碼沒有定義。** 設計稿只說「回非零」(S9、S10)。既有慣例是:

- rc1 代表「未滿足或有未標條款」(file: `scripts/lumos:8170`)。
- rc2 代表帳寫不進去或自驗失敗,優先於紅燈(file: `scripts/lumos:43684`,`_ci_record` 的 docstring)。

設計稿沒有說 BLOCKED、證據帳寫入失敗、FAIL 各對應 rc0/1/2 哪一個。證據帳寫失敗尤其該 rc2,不能像 `_gate_event_or_warn`(file: `scripts/lumos:1618`)那樣「不改判定」。證據擷取的前提就是帳要寫得進去。

severity: minor
blocking: 否
引句:「`lumos evidence check` 應回非零並印出交人提示」

**設定壞掉時的行為衝突。** 既有讀法是 `_ci_config`(file: `scripts/lumos:43435`)和 `_stack_questions_config`(file: `scripts/lumos:26987`):壞值只在 stderr 警告,然後退回預設。S11 要求「能力清單把正式環境標成 WRITE 時應報錯」。這是安全取向,可能是刻意的,但設計稿沒說明為什麼和既有「警告後退預設」不同。

severity: minor
blocking: 否
引句:「能力清單把正式環境標成 WRITE 時應報錯」

**帳檔名和欄位名沒定。** 既有帳檔名都是 `.ci-log.jsonl`、`.kill-log.jsonl` 這種 `.<名>-log.jsonl`(file: `scripts/lumos:43428`、`scripts/lumos:17529`)。設計稿只叫它「證據帳」。實作前要定名;名字定了之後,還要同步進 `_BOOKKEEPING_FILES`(file: `scripts/lumos:27097`)。

### 問 3 第二種做法

**證據帳該不該是治理帳的一種事件**:判定不必併入,另開一本符合既有做法。

- 既有先例是各工具自己的事實帳(`.ci-log`、`.kill-log`、`.signoff-log`),再由 `cmd_gov` 用 `load(檔名, mapper)` 撈進來(file: `scripts/lumos:8720`、`scripts/lumos:8725`)。
- 治理帳的 `_gate_event` 記的是「擋人、放行、被跳過」這種閘判定,欄位是 `gate`、`kind`、`hard`(file: `scripts/lumos:1492`)。
- 證據列有原始檔路徑、退出碼、環境、HEAD,語意不同,塞進治理帳會污染欄位。

缺的是設計稿沒說證據帳要不要加進 `cmd_gov` 的 `load` 清單。RETIRE-IF 的量法寫了「跑 `lumos gov --stats` 與證據帳計數,人工加總」,等於證據帳沒接進 `gov`。

severity: minor
blocking: 否
引句:「跑 `lumos gov --stats` 與證據帳計數,人工加總」
file: `scripts/lumos:8725`
說明:要嘛加一個 mapper 讓 `gov` 能撈,要嘛在設計稿註明刻意不接。

**帳檔名單有第三個消費者沒列入。** 設計稿講了 `_BOOKKEEPING_FILES` / `_BOOKKEEPING_DIRS` 要加,但同一組帳名還出現在 cochange 的預設排除清單(file: `scripts/lumos:41219`)。另外 `.gitignore` 注入的忽略清單(file: `scripts/lumos:23084`)也要確認「證據帳不被忽略」。設計稿只提了簿記名單,漏了這兩處。

severity: minor
blocking: 否
引句:「證據帳與原始檔目錄要加進這兩份名單」
file: `scripts/lumos:41219`

**題庫形狀混雜是第二種做法。** 設計稿把「觸發條件加要釐清什麼」塞進現有 `_PITFALL_QUESTIONS`(file: `scripts/lumos:26474`),而現有四類的值是固定題目字串。設計稿自己也承認這會改形狀。鄰居 `_STACK_QUESTION_SPECS`(file: `scripts/lumos:26516`)已經是結構化條目。同一張表出現兩種值形狀,讀者要分辨,是新引入的做法。比較一致的做法是新類用結構化條目,或另開一張同風格的表。

severity: major
blocking: 是
引句:「現有四類的值都是固定題目字串,新類的值是「觸發條件+要釐清什麼」,讀它的程式要能分辨兩種」

**能力清單放 `.lumos/config.json`** 符合該檔用途:該檔本來就放每個功能自己的區塊(`ci`、`stack_questions`、`lint_new`、`arch_targets`、`review_roles`),且有清單型區塊(`arch_targets` 用 `_arch_targets_config`,file: `scripts/lumos:41835`)。但設計稿沒指定要寫一支專用讀取函式照 `_ci_config` 慣例處理。若直接讀 dict,就是新的設定讀法。「`類` 允許專案在設定裡擴充」也是另一個未命名的設定區塊,同理。

severity: minor
blocking: 否
引句:「放在專案設定 `.lumos/config.json` 的 `capabilities` 區塊」

**版本有效性判法**照用 `_codeloop_record_valid`(file: `scripts/lumos:48870`),對齊,不是第二種做法。

### 問 4 落點

**lumos-guard 不該列入。** 該節點的 responsibility 是「審查席隔離外掛」,about_code 只有 `mods/claude/lumos-guard/` 底下的 TypeScript(file: `docs/lumos-toolchain-knowledge/Systems/lumos-guard.md:6`)。設計稿的 B 塊自己說「用 Claude Code 原生 permissions,不自建」,由 Python 的 `lumos capabilities` 印建議條目,不改外掛。把它列進 `lands_in` 不符合範圍。

severity: major
blocking: 是
引句:「lands_in:」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-guard.md:6`
說明:`lands_in` 列了 `Systems/lumos-guard`,但設計內容完全不動這個外掛。要嘛移除,要嘛說明為什麼要動外掛的工具呼叫過濾。

**效能檢核目錄(52KB)** 的 responsibility 是「各棧檢核題的內容源,`scripts/lumos` 的題目表 `_STACK_QUESTION_SPECS` 照這份寫」(file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:7`)。設計稿要把「後端資料與交易」風險面放這裡,但那是計劃稿題庫 `_PITFALL_QUESTIONS`,不是棧別題庫 `_STACK_QUESTION_SPECS`。我在這篇和 `pitfalls-code-loop` 都沒找到 `_PITFALL_QUESTIONS` 的出現,所以不確定哪篇是它的家。⚠ 交編排者確認,必要時為計劃稿題庫另開或指定家。

**pitfalls-code-loop(42KB)** 已經很大。`--stage` 的對照表和排序規則併進去會再變大;它的 frontmatter 我沒找到 responsibility 欄位,範圍靠正文判斷。⚠ 交編排者看要不要為「分階段出題」另開節點。

**lumos-cli-write(29KB)** 負責 `decision-add`、`set` 這類寫入指令,放決策三欄和 `set` 的 pass 限制合理。**規格閘(20KB)** 有明確 responsibility 涵蓋條款句式與綁定,放 `[evidence:]` 條款與阻塞題檢查合理。**證據擷取**新開合理:沒有既有節點負責「代跑指令加落帳」。

### 摘要

不對齊共 7 條,其中 major 2 條。

- 較重的兩條:
  - `_PITFALL_QUESTIONS` 值形狀混雜。
  - `lands_in` 列了 `lumos-guard`,但範圍不符。
- 較輕的幾條:
  - 規格閘與 `pitfalls --stage` 的呼叫方向沒定。
  - rc 碼沒定義。
  - S11 報錯與設定讀法衝突。
  - 帳檔名單漏了兩處消費者。
  - `capabilities` 與擴充類別缺專用 config 讀取函式。
  - 證據帳沒說要不要接進 `cmd_gov`。

另有兩個 ⚠ 交編排者:`_PITFALL_QUESTIONS` 的家是哪篇,以及 `pitfalls-code-loop` 要不要另開節點。
