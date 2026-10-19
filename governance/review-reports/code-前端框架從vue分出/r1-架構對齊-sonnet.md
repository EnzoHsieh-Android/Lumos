severity: major

## 1. 分層與依賴方向:對齊,沒有跨層直呼

- 新碼全放在 `scripts/lumos` 同一檔裡,位置跟鄰居一樣。
  - Kotlin 判別區塊(`_kt_*`)接在 `_node_flavor_at` / `_NODE_EXTS` 後面,跟 node 判別放同一帶。
  - 呼叫方向也一樣:`_review_role_for` 呼叫 `_kt_role`,`_kt_role` 呼叫 `_kt_flavor_at`。這跟 `_review_role_for` 呼叫 `_stack_key_for_file`、`_stack_key_for_file` 呼叫 `_node_flavor` 是同一條線。
- 批次讀取接得對。`_review_role_wanted` 在 `ext == "kt"` 時多加 `_kt_build_candidates`,跟 `.ts/.js` 加 `_package_json_candidates` 同一招,共用 `_ROLE_READ_CAP` 與預算,沒另開讀取路。
- `_kt_flavor_at` 的 reader 契約(None 代表沒有這個檔、往上找;空字串代表在但讀不了、停下判不出)跟 `_node_flavor_at` / `_node_pkg_text` 一致。
- `_ARCH_IDIOM_SKILL` 加 `node` / `react` 鍵,`_idiom_skill_for` 改查 `_stack_key_for_file` 的棧鍵。這是收斂回同一張表,沒有另立。
- `_RAN_EVIDENCE["node-vitest"] = _RAN_EVIDENCE["node-jest"]` 的別名寫法,跟 `TEST_PROFILES["node-vitest"] = TEST_PROFILES["node-jest"]`(`scripts/lumos:5886`)一模一樣。
- 分層上唯一要提的一點:`run_doctor`(`scripts/lumos:3785`)呼叫的 `_linter_config_hits`,定義在 init 區(`scripts/lumos:26150` 附近)。這是同檔模組層級函式,Python 允許,doctor 呼叫較後面的 helper 在本檔也常見。我不算跨層。

## 2. 命名與錯誤處理:大致對齊,有兩處小差異

- 命名跟鄰居成對。
  - `_kt_flavor` / `_kt_flavor_at` / `_kt_build_candidates` 對 `_node_flavor` / `_node_flavor_at` / `_package_json_candidates`。
  - `_pkg_dep_keys` 是從 `_node_flavor_of` 抽出來的,名字合理。
- 訊息形狀跟 `scripts/lumos:3795` 附近既有的「沒接 linter」`warn([], …)` 同形。
  - 都是 `warn([], 標題, 建議)`,空清單不計 issues。
  - `_init_lint_hint` 的指令 `lumos doctor` 獨立一行,符合「發生什麼→為何在意→指令獨立一行」。
  - `lumos lint-check --smoke` 在 doctor 建議文字裡是行內寫法,但既有那句也是行內寫法,所以一致。
- 回傳碼沒有變動。提醒都不計 issues,沒新增擋下路徑。
- 小差異 A(minor):`_stack_drop_excluded` 原地改傳入的 `app` / `meta` 又回傳它們。鄰居 `_stack_applicability`(`scripts/lumos:30739`)是組新結果回傳。呼叫點用 `*_stack_applicability(...)` 解包接進去,形狀跟鄰居不同。
- 小差異 B(minor):`_ESLINT_FLAT_CONFIGS` / `_ESLINT_LEGACY_CONFIGS` 跟 `_LINT_CONFIG_GLOBS`(`scripts/lumos:31764`)是兩份手動同步的 eslint 檔名清單。作者在註解寫「改一邊回頭看另一邊」,但我在 `scripts/test_lumos.py` 找不到釘兩邊一致的測試。專案慣例是散落同步要靠機械守衛,這裡只靠註解。

severity: minor
blocking: 否
引句:「跟 _LINT_CONFIG_GLOBS(新增告警閘搬設定檔進快照的名單)用途不同、不合併,但 eslint 那幾個檔名兩邊都要認得——改一邊回頭看另一邊」

## 3. 第二種做法:有三處,其中兩處要升 major

### 3a. `_kt_worktree_text` 加 `_KT_BUILD_CACHE`

- 專案裡本來就有「讀工作樹檔、處理 None 與空字串語意、進模組快取」的一套:`_node_pkg_text` 加 `_NODE_FLAVOR_CACHE`(`scripts/lumos:30285`)。作者另寫一支平行的 reader 和另一個快取字典。
- 差別只是多了 `limit` 與 `_ROLE_MAX_BYTES` 的大小守衛。這可以用參數併進既有 reader,或抽成共用 helper。
- 判定:這是「另一套讀檔、另一套快取」,算 major。
- ⚠ 理由有一半成立:`_node_pkg_text` 沒有大小上限,Kotlin 檔頭只讀 64KB 的需求確實不同。這點交編排者定奪。

severity: major
blocking: 是
引句:「_KT_BUILD_CACHE = {}                # 鍵 = (讀取來源, 路徑):工作樹與某個版本不互相污染」

### 3b. 「事後過濾兩支小函式、不動原函式簽名」(作者說法的判定)

我判這算第二種做法,原因有三。

1. 專案裡「某題在某些路徑不出」的既有做法是 spec 旗標加函式內消化。
   - `shape_only` 在 `_stack_applicability` 內部處理(`scripts/lumos:30754`)。
   - 在 `_STACK_PERF_QUESTIONS` 派生時濾掉(`scripts/lumos:30255`)。
   - 呼叫端完全不用知道。
   - `android_only` 的旗標位置跟 `shape_only` 一樣(spec dict),但消費方式不同:三個呼叫點各自算一個 exclude 集合、再各自呼叫 `_stack_drop_excluded` / `_stack_perf_questions` / `_tension_drop_excluded` 事後扣。
2. 「`not shape_only`」這條派生規則現在有兩份:`scripts/lumos:30255` 與 `_stack_perf_questions`(`scripts/lumos:30448`)。原本註解寫「單源=_STACK_PERF_QUESTIONS」,現在單源破了。
3. 作者的動機是避開新增告警閘,不是設計理由。
   - 動機只能說明為什麼沒走既有路,不能說明新路是對的。
   - 把 `exclude` 參數併進 `_stack_applicability`,或把 kt 題表依平台分組,都比三處事後過濾更貼近鄰居。
   - 同一個集合要在三個呼叫點各接一次,新增第四個消費者時漏接就會靜默不一致。

severity: major
blocking: 是
引句:「另立一支不改 _stack_applicability 本身,三個呼叫點(pitfalls、改檔前推播、張力候選)共用同一個集合」

severity: major
blocking: 是
引句:「return [sp["q"] for sp in _STACK_QUESTION_SPECS[stk] if not sp.get("shape_only") and sp["id"] not in exclude]」

這兩條是同一根因的兩個面向(第二條過濾通道,加上派生規則重複),建議合併處理。我分列是為了讓引句各錨一處。

### 3c. `_uses_vitest` 自己讀根 `package.json`

- 解析有共用(`_pkg_dep_keys`),這點做得對。
- 讀檔卻是內嵌的 `read_text`,繞過 `_node_pkg_text` 的快取和「在但讀不了回空字串」的語意。
- 這是 init 一次性路徑,風險小,所以只列 minor。

severity: minor
blocking: 否
引句:「txt = pj.read_text(encoding="utf-8", errors="replace") if pj.is_file() else None」

## 小結

不對齊共 5 條,其中 major 3 條(3a 一條、3b 兩條)。

- 這 5 條是:3a 一條 major、3b 兩條 major、3c 一條 minor、第 2 問的 eslint 檔名清單 minor。
- 第 2 問的小差異 A(原地改傳入物件)是純形狀差異,沒單獨立條。
- 3b 的兩條 major 是同一根因,合併成一件來修即可。實質上要處理的是「第二套讀檔與快取」和「第二條題目過濾通道」這兩件事。
- ⚠ 交編排者:3a 的 `limit` 與大小守衛需求是否足以豁免,由編排者裁決。
