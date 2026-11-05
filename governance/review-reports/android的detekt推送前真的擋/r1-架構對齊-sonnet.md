severity: minor

**1. 分層與依賴方向:對齊**

- **lumos 本體沒有開始執行 Gradle。** 快照的「初始化腳本」一條寫明是消費專案自己跑 `./gradlew -I <腳本路徑> lumosDetektTypeinfo`。lumos 只做兩件事:換佔位符,以及(說實話那套提醒裡)只看 `@<路徑>` 那個檔存不存在。
- **跟既有決定一致。** 對照:
  - `docs/lumos-toolchain-knowledge/Projects/Macrobenchmark退步提醒_計劃.md:87`:「Lumos 只讀結果檔」,不選「由 Lumos 呼叫 gradlew 或 adb 跑基準」。
  - `docs/lumos-toolchain-knowledge/Projects/Android逐層診斷_計劃.md:18`:「Lumos 核心不呼叫 adb、不跑工具」。
- **lumos 跑 detekt 不算新。** 新增告警閘本來就在 `scripts/lumos:38382`(`injected_cmd` 注入 `{LINT_SARIF_OUT}` 的那段)用 shell 跑宣告的 linter。
- **替換與判斷的層次沒變。**
  - 單一替換函式 `_lint_cmd_with_files`(`scripts/lumos:38521`)與共用判斷 `_lint_gate_covers`(`scripts/lumos:38515`)都維持單一實作。
  - 計劃沿用它們,沒有另開第二支替換函式。
  - 「全程式只准一處替換」的守衛測試在 `scripts/test_lumos.py:17127`,計劃已列入要一起改。

**2. 命名與錯誤處理:大致對齊,一處不對齊**

- **佔位符 `{LINT_FILES_CSV}`:** 對齊 `{LINT_FILES}` 與 `{LINT_SARIF_OUT}` 的全大寫底線寫法(`scripts/lumos:38512`)。
- **新的沒跑到類別 `comma-path`、`probe-missing`:** 既有類別是 `budget`、`env`(`scripts/lumos:39127`、`scripts/lumos:39146`)。多一個連字號的詞,不算結構問題,不列。
- **錯誤處理路徑:** 擋下、環境類放行、`_lint_new_classify`(`scripts/lumos:38996`)的分流方式沒變,對齊。
- **放行鍵:不對齊。**
  - 既有放行指紋都是 sha256 取前 16 碼的雜湊。例如大檔的 `_hl.sha256(("oversize" + _LINT_NEW_SEP + f)...)[:16]`,在 `scripts/lumos:38988`。
  - `lumos lint-waive` 的訊息也叫它「指紋」(`scripts/lumos:38078`)。
  - 快照卻寫明文鍵 `detekt-probe:<規則名>`,同一份快照又稱它「放行指紋」。

severity: minor
blocking: 否
引句:「鍵是 `detekt-probe:<規則名>`」
file: `scripts/lumos:38988`
問題:鍵的形狀跟既有雜湊指紋不同。計劃要說明是刻意用明文鍵,還是改成同形的雜湊(例如 `sha256("detekt-probe" + SEP + 規則名)[:16]`),以免 `lint-waive --list` 與擋下訊息出現兩種指紋長相。

**3. 第二種做法:兩處**

- **佔位符替換:** 沒有第二種做法,仍是同一支函式(見第 1 問)。
- **放行:** 沿用 `lumos lint-waive` 與 `.lumos/lint-waivers.json`,沒有另一種放行。差別只在新增一處讀取點,屬合理擴充。
- **Groovy:** `find` 結果顯示 repo 內沒有任何 `.gradle`、`.groovy`、`.kts` 檔,這支會是第一支。計劃有說明為什麼不能用 Kotlin 腳本,技術理由成立。
- **探針原始碼寫成 lumos 本體的字串常數:找不到同類先例。**
  - 既有的 `_PY_PROBE`(`scripts/lumos:75`)是驗 Python 直譯器的自檢,不是拿他語言樣本去驗 linter。
  - 作廢的 `detekt協程規則真的在跑_計劃` 是想法來源,但它已作廢,沒有留下可對照的實作。
  - repo 現行做法是把外語言內容放成檔,放在 `scripts/templates/`(`.sql`、`.pbtxt`、`.sh`,清單在 `scripts/lumos:31988` 到 `scripts/lumos:31999`)。
  - `Android逐層診斷_計劃.md:24` 記錄過,腳本寫在 reference.md 程式碼區塊被架構席判為「專案沒有的第二種做法」。
  - 這裡雖是 Python 常數而非 markdown 區塊,但同樣是把外語言程式內嵌進文字載體。
  - 計劃沒有交代為什麼不放成檔。
  - 嚴重度判 minor 而非 major:結構上仍在同一道閘內,寫入的 `.lumos/lintbase-` 暫存目錄也是既有慣例。⚠ 交編排者決定是否升級。

severity: minor
blocking: 否
引句:「兩支故意寫錯的 Kotlin 原始碼,當字串常數寫在 lumos 本體裡」
file: `scripts/lumos:31988`

- **分發位置 `configs/` 還是 `scripts/templates/`:計劃沒有講理由。**
  - 對照 `configs/detekt/android.yml`:它是 detekt 讀的設定,消費專案靠 clone 路徑引用(`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:125` 的 `$HOME/harness/lumos-toolchain/configs/detekt/android.yml`)。初始化腳本同樣由 `-I` 用 clone 路徑引用,放 `configs/detekt/` 說得通。
  - 但它是可執行腳本。既有的可執行範本放 `scripts/templates/`,還列在工具組複製清單(`scripts/lumos:31971`、`scripts/lumos:31988` 起)。`configs/` 目前只有一支純設定檔。
  - 兩條都有先例,不算違規。計劃沒有選擇依據,也沒有說要不要登記進複製清單。

severity: minor
blocking: 否
引句:「本 repo 分發的 `configs/detekt/lumos-detekt-typeinfo.init.gradle`(新增),Groovy 寫」
file: `scripts/lumos:31971`

**4. 落點:合理,一處缺口**

- **lands_in 的四篇都對得上。**
  - `Systems/pitfalls-lint-adapter`:runner 與佔位符注入(該節點第 22 行有 runner 承重的說明)。
  - `Systems/lint-declaration-health`:說實話提醒 P1、P2 與冒煙。
  - `Systems/linter精選目錄`:標準接法樣板與 android.yml。
  - `Systems/pitfalls-code-loop`:新增告警閘的決策紀錄(它在該節點第 101 行翻掉 d4)。
  - 我沒有發現應該另開新篇的理由。
- **缺口:初始化腳本的家。** 專案鐵則要求每支程式檔有一篇管它的 Systems 節點。快照沒有說這支新檔登記在哪一篇的 `about_code`。`Systems/linter精選目錄` 的 `about_code` 已列 `configs/detekt/android.yml`,最順的是加進它。這個缺口併進上面「分發位置」那條 finding,不另列。
- **⚠ `Systems/pitfalls-code-loop` 要寫什麼?** 它只出現在 lands_in,快照正文沒有任何一處指出要在那篇寫什麼。我判不準是列多了,還是新增告警閘的行為說明本來就在那篇,交編排者確認。

不對齊共 3 條,其中 major 0 條
