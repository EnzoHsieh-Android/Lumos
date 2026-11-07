severity: major

審查範圍是 `r1-snapshot.patch`,對照 `configs/ast-grep/kotlin-android/` 和 `scripts/test_lumos.py` 裡的鄰居。我沒有實跑 ast-grep 或測試,結論都來自讀 diff 和既有檔案。

## 1. 分層與依賴方向:基本對齊

- **規則放置:對齊。**
  - 自寫規則放進既有的 `rules/api.yml`(新增 `kt-webview-file-url-access`)。
  - 沒量過誤報的三條放進 `rules-unwired/`,其中 `rules-unwired/data.yml` 是新檔,但目錄本來就有 `rules-unwired/api.yml`、`rules-unwired/state.yml` 等同層檔案。
  - 同一檔用 `---` 分隔多份規則,跟 `rules/api.yml:23` 之後的寫法一致。
  - 規則註解開頭用 `# [[Projects/…_計劃]] 範圍 4:` 交代來歷,跟鄰居一樣。
- **樣本放置:對齊。** 路徑是 `samples/bad|good/<規則id>/src/main/kotlin/<規則id>.kt`,行尾用 `// BAD`、`// GOOD`,跟 `samples/bad/kt-okhttp-client-per-call/src/main/kotlin/kt-okhttp-client-per-call.kt:3` 同形。
- **依賴方向:對齊。**
  - `check.py` 只擴充 `_B4_LINT` 前綴,沒有新增跨層呼叫。
  - 新測試用 `_ktpack()`、`_ktpack_sg()`、`m.CONFIGS`、`m.scan`、`m.load_rules`,跟 `scripts/test_lumos.py:126635` 一帶的鄰居相同。
- **路徑排除:八項清單對齊。** 「七項加 `**/src/debug*/**`」這個清單,鄰居 `configs/ast-grep/kotlin-android/rules/api.yml:270` 已經用過,不算新寫法。

## 2. 命名與錯誤處理

- 規則 id 都以 `kt-` 開頭。訊息格式都是 `[型錄編號]現象;改用/改成…`,跟 `rules/api.yml:23` 同形。
- 測試命名 `t_kotlin_rulepack_*`、`t_kt_catalog_*` 和 docstring 的「判準來源 / 翻紅釘」寫法都跟鄰居一致。
- 本機沒有 ast-grep 時,新測試先跑靜態那半再印提示,跟 `scripts/test_lumos.py:126328` 的 `_ktpack_sg` 慣例一致。
- 暫存目錄用 `gctl-ktsec-` 前綴加 `rmtree`,跟 `gctl-ktpack-`、`gctl-ktsg-` 同形。
- 型錄欄位的 `資安包:<id>` 前綴和來源縮寫 `LINTREF`、`ASL`、`MASTG` 是照既有縮寫表加列,跟 `LINT`、`CR` 同形。

## 3. 第二種做法

**F1**
severity: major
blocking: 是
引句:「doc = next((x for x in re.split(r"^---\s*$", (m.HERE / d / fname).read_text(encoding="utf-8"), flags=re.MULTILINE)」
- `t_kotlin_rulepack_security_rules` 自己重切 yml 的 `---` 文件,再用正則 `^ignores:\s*\[(.*)\]\s*$` 抓路徑排除。
- 既有做法是由 `load_rules()`(`configs/ast-grep/kotlin-android/check.py:65`)統一切文件、解析欄位,`test_only` 也是在那裡算好的。
- 測試裡另寫一套 yml 解析,是第二種解析路徑。
- 鄰居的做法是在 `check.py` 的 `load_rules` 補一個 `ignores` 欄位,測試只讀 `r["ignores"]`。

**F2**
severity: minor
blocking: 否
引句:「check(f"S4 {rid} 訊息以 [{cat}] 開頭、不超過 120 字", msg.startswith(f"[{cat}]") and len(msg) <= 120」
- 訊息長度上限 120 在測試裡寫死,`check.py:30` 已有 `MSG_MAX`,`check.py:659` 的 `message_problems` 也已經在檢查,而且既有測試 `t_kotlin_rulepack_messages_cite_catalog` 會跑它。
- 「開頭是指定編號」是新增的判準,不算重複。只有「不超過 120 字」是重複,應改讀 `m.MSG_MAX`。

**F3**
severity: minor
blocking: 否
引句:「doc = (Path(GRAPHCTL).resolve().parents[1] / "docs" / "lumos-toolchain-knowledge" / "Systems" / "linter精選目錄.md").read_text(」
- 同一份 linter 目錄筆記,鄰居用 `base = Path(__file__).resolve().parent.parent`(`scripts/test_lumos.py:128622` 一帶)定位。
- 新測試改用 `GRAPHCTL` 往上兩層,結構沒有錯。
- ⚠ 檔內有 20 處 `Path(GRAPHCTL).resolve().parents[1]`,鄰居本身就兩種並存,交編排者裁。

**F4(⚠ 交編排者,不計入不對齊)**
- `t_kt_catalog_security_lint_ids` 把「還沒逐列查證 2 列」寫死成 `["API-14", "TEST-31"]`。
- 鄰居 `t_kt_catalog_unverified_rows`(`scripts/test_lumos.py:128696`)是用 `len(m.catalog_unverified())` 比對,不寫死列表。
- 這是新增斷言不是重寫,而且 docstring 說明數字來自型錄逐列查證計劃的收尾值。是否算第二種做法,請編排者裁。

不對齊共 3 條,其中 major 1 條。
