severity: minor

三問都已對照既有規則檔、樣本和 `check.py` 看過。甲包 16 條規則和 32 個樣本跟現有做法大致對齊,只有 1 條 minor。

**問 1 分層與依賴方向**

沒有不對齊。
- 放置位置:15 條放 `rules-unwired/`,只有 `kt-webview-mixed-content-always` 放 `rules/`。這跟 `check.py` 的分層一致:`rules/` 收 error 與 warning,`rules-unwired/` 收還沒量過誤報的新規則。對照:`configs/ast-grep/kotlin-android/check.py:25`、`configs/ast-grep/kotlin-android/check.py:29`。
- 規則檔分配:API 系三條進 `api.yml`,ARCH 系兩條進 `architecture.yml`,DATA 系進 `data.yml`,跟既有規則一致。
- 除錯版判斷:16 條都用 `not: matches: in-debug-only-branch` 引用 `utils/debug-only.yml`,沒有任何一條自帶除錯判斷。對照:`configs/ast-grep/kotlin-android/rules/api.yml:271`、`configs/ast-grep/kotlin-android/rules-unwired/api.yml:257`。
- 規則檔內的 `utils:`:新規則自帶的 utils 只放這條規則專用的字串或形狀(例如 `intent-src`、`weak-name`)。既有規則也這樣做,例如 `rules/compose.yml:5`、`rules/data.yml:185`、`rules-unwired/api.yml:5`。
- 樣本結構:`samples/{bad,good}/<規則id>/src/main/kotlin/<規則id>.kt`,跟 `samples/bad/kt-webview-file-url-access/src/main/kotlin/kt-webview-file-url-access.kt` 相同。

**問 2 命名與錯誤處理**

沒有不對齊。
- 規則 id:全部是 `kt-` 加 kebab-case。
- 檔頭註解:`# [[Projects/…_計劃]] 範圍 4:不接閘(…)` 加一句形狀說明,跟 `rules-unwired/api.yml:25` 和 `rules/api.yml:246` 的寫法同形。
- 訊息格式:`'[CATEGORY-N]症狀;改成…'`,跟鄰居相同。
- `ignores`:16 條都帶同一份測試與除錯目錄清單,跟 `rules/api.yml:253` 逐字相同。
- 程式碼:`constraints:` 都放在 `rule:` 之後,跟 `rules/data.yml:389`、`rules/state.yml:73`、`rules-unwired/api.yml:97` 一樣。
- 訊息編號:`DATA-95` 在甲包沒出現,既有檔也沒有 95。這是編號延續的問題,不是寫法不一致,我不列為發現,交編排者確認是否留給乙包。

**問 3 第二種做法**

有 1 條 minor 發現,沒有 major。

1. 排除函式庫自己的原始碼複本,用的是「看套件宣告」的新寫法,專案原本沒有。

severity: minor
   blocking: 否

   引句:「            regex: '^package\s+(okhttp3|org\.eclipse\.paho)\b'」

   - 新做法:`kt-weak-cipher-suite` 用 `inside source_file has package_header regex` 排除 okhttp3、paho 的原始碼複本。
   - 既有做法:鄰居排除不想掃的檔案,一律用 `ignores:` 的路徑 glob。整個 `rules/` 和 `rules-unwired/` 對 `package_header` 零命中,`utils/` 也沒有。
   - 為何歸 minor 而不是 major:函式庫複本的路徑不固定,glob 排不到,而且這是規則專用的一次性形狀,結構沒有跨層。它也沒有侵入共用判斷。
   - 要編排者定奪:鄰居沒有「按套件排除」的前例,所以沒有哪一邊是標準。我標 minor,不標 major,請決定是否接受,或抽成 `utils/` 共用。

其他我逐項看過、沒有發現第二種做法:
- `constraints:` 位置都在 `rule:` 後面。
- 除錯判斷沒有自帶版本。
- 樣本沒有新結構。
- 所有 `ignores:` 清單相同。
- 所有 `inside source_file` 的用法在既有檔裡有前例,見 `rules/architecture.yml:488`、`rules/coroutines.yml:250`、`rules/testing.yml:354`。

不對齊共 1 條,其中 major 0 條
