severity: minor

**① 分層與依賴方向**

check.py 讀範本檔的做法跟既有慣例對得上。`TEMPLATES = HERE.parents[2] / "skills" / "kotlin-idioms" / "test-templates.md"` 跟 `CATALOG` 用同一個定位法,放在同一處常數區(`configs/ast-grep/kotlin-android/check.py:20-21`)。檢查也是掛在 `catalog_problems` 尾端(`problems += template_problems()`),所以 `--catalog-only` 和 CI 走的是同一條路(`check.py:398` 的 `catalog_problems(load_rules())`)。

家的歸屬也對得上。範本檔 `test-templates.md` 列在 Systems/kotlin規則包 的 `about_code`,而同節點本來就收著 Markdown 的 `skills/kotlin-idioms/checks-catalog.md`,所以不是新慣例。`test-quality-standard.md` 列進 Systems/test-quality-cli 的 `about_code` 也合既有做法。理由是該節點的 `responsibility` 本來就寫著「另含 lumos-project-notes 的測試品質接入標準文件」,而且它的「摘要」行(`Systems/test-quality-cli.md:80,84,88`)早就在記這份檔。這次只是把 frontmatter 補齊。

測試端的 `_ktpack(copy=True)` 把範本檔一併複製,再把 `m.TEMPLATES` 指向複本。這跟既有對 `m.HERE`、`m.CATALOG` 的做法一樣(`scripts/test_lumos.py:125439` 起的 `_ktpack`)。

沒有跨層直呼。

**② 命名與錯誤處理**

- 回傳形狀對齊:`template_problems` 回 `(id, 原因)` 的 tuple 串列,跟 `catalog_problems` 一樣(`check.py:131-216`)。
- 整體性問題的 id 用 `<templates>`,跟 `<catalog>`、`<決策表>` 的角括號寫法一致。
- 錯誤訊息是中文短句,風格同「對應檢查 X 不在型錄主表」。
- 新測試名 `t_kotlin_test_templates_sections`、`t_kotlin_catalog_c_rows_batch_resolved`、`t_kotlin_test_templates_linked` 都是 `t_kotlin_*` 前綴。
- 測試內的「★改壞★」「★對照★」標記沿用 `t_kotlin_catalog_rows_wired`(`scripts/test_lumos.py:125648`)的寫法。

不一致有一處:

F1
severity: minor
blocking: 否
引句:「    text = CATALOG.read_text(encoding="utf-8")」
`template_problems` 另外重讀一次型錄,自己再切一次「情境決策表」之前的主表,再重做 `_MAIN_ROW_RE` 比對、`_cells` 切格、欄位數檢查。同一個動作在 `catalog_problems` 裡已經做過,而且做完就有 `main`、`rows`(`check.py:131-171`)。結構上沒有跨層,但形成兩條讀同一張主表的路徑,日後主表格式改動要同步兩處。

**③ 第二種做法**

check.py 這邊沒有重做既有解析,因為既有程式本來就沒有解析「通電批次」值的函式(對 `批`、`通電` 搜過)。通電批次格子的解析是新增的。有兩個小偏差:

F2
severity: minor
blocking: 否
引句:「    mm = _re.search(r"行為測試或正向約束=([^;]*)", batch_cell)」
同一個格子有兩套解析。check.py 的 `_TEMPLATE_REF_RE`(`範本 (T\d+)`)直接掃整個 `c[9]`。測試端的 `_kt_behavior_value` 則先抓「行為測試或正向約束=」那一段再比對。兩邊口徑不同:若「告警帶寫法=」那一段也出現「範本 T<n>」,check.py 會驗、測試端的列號對照卻不算。型錄〈輸入與口徑〉把「範本 T<n>」定義成「行為測試或正向約束=」那段的值,所以 check.py 比測試端寬鬆。

範本節標題比對本身,`^## (T\d+) ` 加 `re.M`,是新需求,沒有既有的標題比對可借用。型錄那邊不算第二種做法:`checks-catalog.md` 的〈輸入與口徑〉只多補了值的說明,沒有新增欄位或語法,符合「沿用既有欄位」。

不對齊共 2 條,其中會擋的 0 條。
