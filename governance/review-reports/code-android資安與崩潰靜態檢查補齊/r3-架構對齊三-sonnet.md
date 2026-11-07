severity: minor

**1. 分層與依賴方向**

規則到共用判斷的引用方向是對的,但共用判斷放的位置是專案裡第一次出現。

- 發現 1
severity: minor
  blocking: 否
  - 專案原本的共用寫法,是每條規則自己帶一段 `utils:`,內容直接複製、不另開目錄。例子有 `configs/ast-grep/kotlin-android/rules/compose.yml:5`、`:101`、`:202` 和 `configs/ast-grep/kotlin-android/rules-hints/api.yml:5`。`compose.yml:22` 的註解明說「六條規則共用同一份,改一份要全改」,等於專案接受複製。
  - 這份 diff 新開 `utils/` 目錄,四份 sgconfig 各加 `utilDirs`,規則改用 `not: matches:` 引用。同一個專案裡,共用子判斷現在有兩種做法,既有的 `compose.yml` 那幾組沒有搬,也沒有說為什麼不搬。
  - 理由其實有寫:規則包節點的 WHY 寫了 `[不選:每條規則各寫一份(兩支檔要手抄同步)]`。但它只拿「各寫一份」當對照,沒提 `compose.yml` 這個既有前例。
  - 因此我判為結構已有理由、沒有「沒寫理由」的第二種做法。這裡標 ⚠:如果審查者認定「共用機制本身出現第二種」就算第二種做法,這條要升級。
  - 引句:「+    matches: kt-in-debug-only-branch」
  - 引句:「+  - configs/ast-grep/kotlin-android/utils/debug-only.yml」

- 發現 3
severity: minor
  blocking: 否
  - 節點 `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 的目錄說明沒有跟上。
  - 第 67 到 70 行逐一說明每份 sgconfig 掛哪個規則目錄,新增的 `utils/` 和 `utilDirs` 一個都沒寫進去。`utils/` 只出現在 about_code(第 16 行)和一條 WHY(第 55 行)。
  - 讀目錄清單的人看不到有第五個目錄、而且四份設定都掛它。
  - `configs/ast-grep/kotlin-android/check.py:26` 的 `CONFIGS` 只列四個規則目錄,`utils/` 不在其中。這一點我只標 ⚠,不單獨算一條。
  - 引句:「+  - configs/ast-grep/kotlin-android/utils/debug-only.yml」

新規則、樣本、測試的位置跟鄰居一致:
- `kt-webview-file-url-access` 放 `rules/api.yml`,其他三條放 `rules-unwired/`,依 API 或 DATA 主題分檔。
- 新案例 C25 到 C35 接在既有的 `_KTSEC_CASES` 表裡。
- 樣本放在既有的 `samples/bad|good/<id>/`。

**2. 命名與錯誤處理**

- 發現 2
severity: minor
  blocking: 否
  - 共用判斷的 id 是 `kt-in-debug-only-branch`,帶了規則 id 才用的 `kt-` 前綴。
  - 既有的共用判斷名都是不帶前綴的短名:`in-composable`、`deferred-lambda`、`in-composition`(`rules/compose.yml:6`、`:23`、`:50`),以及 `body-string`(`rules-hints/api.yml:6`)。
  - 檔名 `debug-only.yml` 跟 id 也對不上,既有規則檔是檔名對應主題、id 都以 `kt-` 開頭。
  - 引句:「+id: kt-in-debug-only-branch」

其餘三項與鄰居一致:
- 規則訊息格式(`[型錄編號]` 開頭、`改用…`)沒變。
- 測試 docstring 沿用既有的「翻紅釘」寫法逐項續寫。
- `check.py` 的 `ignores` 解析只擴充同一個函式。

⚠ C32 到 C35 是驗 API-19 和 DATA-16 的案例,放在 `t_kotlin_rulepack_security_rules` 裡。這兩條不屬於資安四條,但表頭已經註明是共用判斷的案例,所以我不算作不一致。

**3. 第二種做法**

「只在除錯版才走到」這個判斷,修補後只剩一種做法。
- API-19、DATA-16、`kt-webview-file-url-access`、`kt-webview-debugging-enabled` 四處全部改成 `matches: kt-in-debug-only-branch`,舊的各抄一份已經刪掉。
- 我在 `rules*/` 裡 grep `BuildConfig` 和 `DEBUG`,沒有別的規則用另一種寫法判同一件事。

剩下的第二種做法就是發現 1 的共用機制:`utilDirs` 與規則內 `utils:` 並存。這已經附了理由,所以沒有「沒寫理由」的問題。

不對齊共 3 條,其中 major 0 條
