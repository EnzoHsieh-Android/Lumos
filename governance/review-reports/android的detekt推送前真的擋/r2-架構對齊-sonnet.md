severity: minor

r1 的三條已解決:
- 放行鍵改成 `sha256("detekt-probe" + 分隔字元 + 規則名)` 取前 16 碼,跟 `scripts/lumos:38988` 的雜湊指紋同形。
- 探針改成放在 `scripts/templates/detekt-probe/` 的檔,不再是字串常數。
- 初始化腳本放 `configs/detekt/` 的理由已寫出,也登記進 `Systems/linter精選目錄` 的 about_code。

`Systems/pitfalls-code-loop` 為什麼在 lands_in,範圍第 9 條已交代(新類別與放行鍵寫進去)。以下只報第 2 版新出現的。

**1. 分層與依賴方向:對齊**
- 擋或放仍由 `_lint_new_classify`(`scripts/lumos:38996`)的兩分法決定:`env` 放行,其餘擋。
- 替換仍只走 `_lint_cmd_with_files`(`scripts/lumos:38521`),命令執行目錄是選填參數,既有呼叫不變。
- 探針與型別參數檔檢查都落在 `_lint_new_*` 這道閘內,沒有新的跨層直呼。
- Gradle 仍由消費專案自己跑初始化腳本,lumos 只讀參數檔是否存在。
- 沒有跨層問題。

**2. 命名與錯誤處理:兩處不對齊,結構對**
- 既有類別只有 `budget`、`env`(`scripts/lumos:39127`、`scripts/lumos:39146`),都是單詞。新增的 `typeinfo-missing`、`typeinfo-broken`、`separator-path`、`probe-missing` 是連字號的描述式命名,單看不算問題。
- `timeout` 的問題:
  - 逾時現在歸在 `env` 裡,計劃卻為型別宣告命令另立 `timeout` 類別。
  - 同一種原因會因命令種類落在兩個名字。
  - `scripts/lumos:39146` 的 `env` 說明寫的是「工具沒裝/逾時/拉不到規則」。
  - 比較順的做法是仍用 `budget`(逾時本來就是預算耗盡),或在 `env` 之外加一個旗標欄位,不要多一個同名同義的類別。
- `separator-path` 的問題:
  - 它是「某支檔沒被檢查,可用鍵放行」,跟既有 `oversize` 是同一類。
  - `oversize` 有獨立的 `out["oversize"]` / `out["oversize_waived"]` 清單,不走 `undone`(`scripts/lumos:39114`)。
  - 計劃把它併進「沒跑到」的類別,結構上不同形。
- `probe-missing`:是判定結果,不是命令沒跑到,也併在同一組類別名裡,混了兩種語意。
- 放行鍵前綴 `detekt-probe`、`detekt-sep-path` 與 `oversize` 風格不一,不另列。

severity: minor
blocking: 否
引句:「`timeout`:逾時。一般命令逾時照舊算環境類;型別宣告命令逾時算擋。」
file: `scripts/lumos:39146`

severity: minor
blocking: 否
引句:「`separator-path`:要檢查的檔裡有路徑含逗號或分號」
file: `scripts/lumos:39114`

**3. 第二種做法:一處不一致,一處 ⚠**
- 「型別宣告命令失敗就擋、其他命令照舊放行」不算第二種失敗處理。
  - `_lint_new_classify` 的規則仍是 `env` 放行、其餘擋。
  - 計劃只是把這一種命令的失敗歸進「其餘」。
  - 它也沒走 `_gate_failopen`(`scripts/lumos:66900`)那條整閘放行的路。
  - 缺的是上面第 2 問講的命名收斂。
- 型別宣告命令不用 `kind` 分流,而是在 `_lint_run_and_parse` 之前先做參數檔檢查。這跟既有 `budget` 在跑之前檢查剩餘時間(`scripts/lumos:39121`)同形,對齊。
- 探針沒登記進 `_VENDORED_TREE_FILES`:
  - 計劃把探針放成 `scripts/templates/detekt-probe/` 底下的檔,卻沒提登記。
  - `scripts/lumos:31975` 起的表要「跟 repo 底下受版控的檔一模一樣」,有逐檔比對測試。
  - 少登記測試會翻紅,消費專案也收不到探針。
  - 屬「沿用既有慣例但漏了接線」,minor。
- ⚠ CI 下載釘版本工具、驗 sha256、放快取:
  - `.github/workflows/ci.yml` 目前唯一的外部工具先例是 `python -m pip install --quiet ruff==0.16.7`(第 73 行),只釘版本,沒有下載 jar、驗 sha256、`actions/cache` 的先例。
  - 這是 CI 裡第一種原生二進位下載法,方向(釘版本、只在 CI 當工具)一致,但手法新。
  - 我判 minor,交編排者決定要不要升級。計劃可以補一句為什麼 jar 不能走套件管理器,或把下載步驟寫成可重用的一步,往後再有外部工具就照這個做。

severity: minor
blocking: 否
引句:「新增 `scripts/templates/detekt-probe/`(新增;跟既有 `.sql`、`.sh` 範本一樣把別的語言的內容放成檔」
file: `scripts/lumos:31988`

severity: minor
⚠
blocking: 否
引句:「下載釘版本的 detekt-cli 1.23.8 與 kotlinx-coroutines-core-jvm jar(從官方發布處,比對寫死的 sha256」
file: `.github/workflows/ci.yml:73`

**4. 落點:對齊**
- lands_in 四篇都對得上,初始化腳本的家(`Systems/linter精選目錄`)已指明。
- 探針檔該由哪一篇管,計劃沒寫。它在 `scripts/templates/`,依鐵則 5 也要有家。最順的是併進 `Systems/pitfalls-code-loop`(新增告警閘本體)或 `Systems/linter精選目錄`。這條併入上面「沒登記」那條,不另列。
- 沒有該另開新篇的理由。

總結:不對齊共 4 條,其中 major 0 條
