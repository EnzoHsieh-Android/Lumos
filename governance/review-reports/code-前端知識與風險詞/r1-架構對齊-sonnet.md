severity: minor

審查範圍是 `r1-code.patch`,對照 d2297c94 版的 `scripts/lumos`。我讀了 patch 全文與同層鄰居,沒有跑 `pitfalls --diff`。暫存只放在 `/tmp/lumos-seat-work/code-前端知識與風險詞/架構對齊-sonnet/new.py`,沒有刪,也沒有寫進 repo。

### 問 1:分層與依賴方向

**這題沒有 major,沒有跨層直呼。**

- **前端題列與提示函式**
  - 新常數表接在 `_REQUIREMENT_FACETS` 後面,見 `scripts/lumos:29934`。
  - `_req_frontend_hit`、`_req_frontend_facets`、`_req_frontend_hint` 緊貼這張表。
  - 這和 `_pitfalls_stage` 讀 `_REQUIREMENT_FACETS` 的方向一致,見 `scripts/lumos:47764`。
  - 呼叫方向是 `cmd_pitfalls` 呼叫 `_pitfalls_check_print`、`_pitfalls_frontend_json`、`_pitfalls_frontend_print`,再呼叫 `_req_frontend_*`,沒有反向依賴。
  - 抽出來的 helper 命名與 `_pitfalls_stage` 同族,見 `scripts/lumos:47749`。
- **infra 題組**
  - `_STACK_QUESTION_SPECS["infra"]` 在字面量之後用指派加入,做法與 `_STACK_QUESTION_SPECS[_stk].append(...)` 的 extcode 迴圈相同,見 `scripts/lumos:30232`。
  - 題組用 `when` 與 `when_raw` 兩欄,與既有 spec 形狀一致。
  - 題目表經 `_STACK_TRIGGERS` 編譯,見 `scripts/lumos:30241`。
  - `_stack_applicability` 以 zip 配對讀這張表,見 `scripts/lumos:30598`,所以新鍵不用改消費端。
- **分類入口**
  - 「infra」鍵由 `_stack_key_for_file` 給出,見 `scripts/lumos:30310`。
  - `_review_role_for` 建在 `_stack_key_for_file` 上,見 `scripts/lumos:30400`,沒有另造一套分類。
- **`skip=vend_skip` 傳進 `_arch_alignment_hints`**
  - `skip=frozenset()` 的預設值和簽名,都和 `_stack_changed_ok(cur_file, skip=frozenset())` 一致,見 `scripts/lumos:46735`。
  - 唯一的呼叫點在 `scripts/lumos:47395`。
  - 過濾直接寫在鄰居清單推導式裡,沒有改走 `_stack_changed_ok`。
  - `_arch_alignment_hints` 本來就有自己的 `_PITFALL_DIFF_TEST_PAT` 與 `(Tests?|Spec)` 過濾,所以結構上對齊。
- **掃產品型樣處多加 `_TEST_INFRA_PATH_RE`**
  - 這個條件只加在 `_pitfall_diff_collect` 的迴圈裡,見 `scripts/lumos:47352`。
  - `_PITFALL_DIFF_PATTERNS` 只有這一處消費者,見 `scripts/lumos:47355`,所以單點有理由。
  - patch 的注釋已說明為何不改 `_stack_changed_ok`。

### 問 2:命名與錯誤處理

- **新增函式與測試的命名**
  - `_req_*`、`_pitfalls_*` 沿用既有前綴。
  - 測試用 `t_*`,測試輔助函式用 `_fe_*`、`_infra_*`,與鄰居一致。
- **`_INFRA_B` / `_INFRA_E` / `_INFRA_CMD`**
  - 這組命名沿用 `_EXTCODE_*` 的做法,見 `scripts/lumos:30006`。
  - 它的詞界把底線也排除,和 `PITFALL_CLASSES` 的詞界不同。patch 的注釋有交代原因,所以我當作兩張表各有規則,不列為不一致。
- **提示訊息形狀**
  - `_pitfalls_check_print` 的 ✓/✗ 兩行形狀不變,前端提醒另起一行,有「提醒:」前綴。
  - 只有 rc 沒變:零命中且有前端字樣時 rc 仍是 0,命中類且無節時仍是 1。
  - 提醒句把指令 `lumos pitfalls <計劃>` 放在句中,沒有獨立成一行。鄰居 `--check` 的 ✗ 行也是單行內嵌指令,所以我不算它不一致。
  - 但「提醒:」鄰居走 stderr,見 `scripts/lumos:47383` 的 `print(f"提醒:{w}", file=sys.stderr)`,新提示走 stdout。⚠ 鄰居本身沒有統一,交編排者判斷。
- **`_PITFALL_SEND_RE` / `_PITFALL_PAYMENT_RE`**
  - 這兩個名稱以 `_RE` 結尾,值卻是未編譯字串,見下方 finding 1。
- **`_arch_alignment_hints` 的 docstring**
  - docstring 沒補 `skip` 這個參數,但有 inline 注釋說明。這屬於文件問題,不計入。

### 問 3:第二種做法

沒有新的解析器、設定讀法或安全函式,讀檔、消毒、引號相關也沒新寫。有兩處「重抄一份既有知識」:

- **`_INFRA_CODE_EXTS` 重抄副檔名集合**,見 finding 2。
- **前端框架名多一份表**,見 finding 3。

### Findings

severity: minor
blocking: 否
引句:「_PITFALL_SEND_RE = (r"送出(?=[^,.;!?。、\n]*[給至往])|(?<=請求|表單)送出(?=到)|送出(?=(?:請求|表單)到)"」
說明:`_RE` 結尾在本檔慣例是 `re.compile` 物件,共 163 筆,例如 `_NOGO_H2_RE`、`_EXCLUDED_RE`、`_TEST_INFRA_PATH_RE`。這裡的值卻是未編譯字串,因為 `PITFALL_CLASSES` 會再編譯。
這個題材已有 `_EXTCODE_WHEN`、`_REQ_FE_WHEN` 這類 `_WHEN` 字串的命名。字串型的 `_RE` 只有 `_QUOTE_LABEL_RE` 一個先例。
⚠ 先例很弱,交編排者判斷要不要改名。
file: `scripts/lumos:27440`(`_QUOTE_LABEL_RE`,唯一的字串型 `_RE`)
file: `scripts/lumos:30031`(`_EXTCODE_*` 字串常數的命名)

severity: minor
blocking: 否
引句:「_INFRA_CODE_EXTS = {"sh", "py"} | {"ts", "tsx", "js", "jsx", "mjs", "cjs", "mts", "cts"}」
說明:這個集合手抄了一份 `_NODE_EXTS`,而 `_NODE_EXTS` 就定義在 `_stack_key_for_file` 正上方。日後有人改了其一,兩份會分歧。照鄰居做法應寫成 `{"sh", "py"} | _NODE_EXTS`。
file: `scripts/lumos:30306`(`_NODE_EXTS`)

severity: minor
blocking: 否
引句:「框架名跟 _NODE_FRONTEND_MARKERS 對齊(多一個 vite);那份比 package.json 的套件名、這份比計劃散文,所以不共用同一個集合。」
說明:`_REQ_FE_WHEN` 是專案內第三套「是不是前端」的判法。前兩套是 `_NODE_FRONTEND_MARKERS`(`scripts/lumos:30244`)和 `_review_role_for` 的 `_ROLE_FRONT_EXTS`(`scripts/lumos:30400`)。
patch 的注釋已說明比對對象不同(套件名 vs 計劃散文),屬於有意為之。
但框架名清單現在有兩處要同步,而且已經有一處不同(多了 vite)。這裡沒有機械守衛,只靠注釋「對齊」。
⚠ 這個分歧是否可接受,交編排者判斷。

不對齊共 3 條,其中 major 0 條
