severity: minor

審查範圍:`r2-snapshot-甲.patch` 的 16 條規則與 30 個樣本檔,加上 `r2-repair.patch` 的測試與型錄修補。我沒有在 repo 動任何檔。

## 問 1 分層與依賴方向:對齊
- 放置位置照鄰居走:`kt-webview-mixed-content-always` 進 `rules/api.yml`(會擋),其餘 15 條進 `rules-unwired/` 的 api、architecture、data(不接閘)。鄰居 `rules/api.yml:239-262` 的 `kt-webview-file-url-access` 在 `rules/`,`rules-unwired/api.yml:25-42` 的既有不接閘規則在 `rules-unwired/`。
- 除錯版判斷全部引用共用的 `in-debug-only-branch`(`utils/debug-only.yml:6`),沒有任何一條自帶除錯判法。對照引句:
引句:「  not:    matches: in-debug-only-branch」
- 路徑排除的 `ignores` 八項與鄰居 `rules/api.yml:245` 逐字相同,沒有多帶建置腳本三項。
- 樣本路徑 `samples/{bad,good}/<id>/src/main/kotlin/<id>.kt`,跟既有的 `samples/bad/kt-webview-file-url-access/src/main/kotlin/kt-webview-file-url-access.kt` 一樣。
- 沒有新規則跨層直呼別層的東西。

## 問 2 命名與錯誤處理:大致對齊,2 條 minor
- 規則 id 都是 `kt-` 加 kebab-case。訊息都以 `[API-48]` 這類型錄編號開頭,後面接「現象;改成…」,跟 `rules/api.yml:241` 的 `[API-40]` 句式一致。
- 檔頭註解開頭都是 `# [[Projects/…_計劃]] 範圍 4:…`,跟鄰居一致。
- 新補的測試案例 C72~C86 沿用既有 `(路徑, 程式片段, 規則 id, 期望筆數)` 四元組。需要前置宣告的案例寫成 `\n    ` 兩行,跟 C68、C69 一樣。補的 15 筆成對壞好:5 條規則各一對,混合內容那條補三筆壞例。
- 型錄統計的新輔助函式 `_kt_stats_extra_problems` 接在 `_kt_stats_problems` 回傳,跟既有 `_kt_pending_problems` 的拆法同形。

1. 套件標頭排除是專案裡第一次出現的寫法。
severity: minor
blocking: 否
引句:「            regex: '^package\s+(okhttp3|org\.eclipse\.paho)\b'」
- 第二種排除法:鄰居要排除一批檔案,一律用檔頭 `ignores` 的路徑 glob。這條改成在規則內用 `inside source_file has package_header` 看檔案內容。
- 全 repo 的 `rules*/` 目錄裡,`package_header` 只在 `rules-unwired/api.yml:233` 這一處(新增的 `kt-weak-cipher-suite`)。
- 用意看得出來:是排除函式庫自己的原始碼複本,路徑 glob 不一定好寫。
- 判不準:鄰居沒有同類情境。屬 minor,交編排者決定要不要升格成共用寫法。

2. 測試函式的標籤前綴改成帶「第二批」字樣。
severity: minor
blocking: 否
引句:「    """[第二批 S3] 第二批型錄([[Projects/Android資安靜態檢查補齊第二批_計劃」
- 鄰居慣例:`scripts/test_lumos.py` 其餘測試的 docstring 都用 `[S1]`、`[S2]` 這種裸編號(例如 `:2488`、`:2506`)。
- repair 把 `t_kt_catalog_security_lint_batch2` 與 `t_kt_catalog_stats_consistent` 改成 `[第二批 S3]`、`[第二批 S4]`,全檔只有這兩處。
- 動機是區分同名 S 編號,但沒有套用到同批的 `t_kotlin_rulepack_security_rules`(仍是 `[S3][S4]`)。
- 同一批內標法不統一。

## 問 3 第二種做法:沒有 major,2 個 ⚠ 交編排者
- 每條規則的 `utils:` 都寫在自己檔內、`constraints:` 都放在規則末尾,跟鄰居一樣。
  - 鄰居:`rules/data.yml:185`、`rules/data.yml:397`,以及 `rules/data.yml:389` 的 `constraints`。
  - 新規則:`kt-command-exec-nonliteral` 末尾的 `constraints: RT`,`kt-xxe-documentbuilder` 末尾的 `constraints: F`。
  - 全 repo 的 `utils/` 目錄只有 `debug-only.yml` 一支,沒有鄰居把規則內的 utils 搬去共用。因此規則內自帶 utils 是現行做法,不是第二種做法。
- ⚠ 同一段判斷在兩條規則內各抄一份,沒抽成共用:
  - `kt-zip-slip` 與 `kt-provider-openfile-traversal` 的 `file-ctor` 完全相同。
  - 兩者的「同函式有 `canonicalPath|canonicalFile|…` 就不報」regex 也相同。
  - 引句:「          regex: 'canonicalPath|canonicalFile|getCanonical|normalize\(|toRealPath|"\.\."'」
  - 鄰居也沒有抽共用的先例(`rules/data.yml` 內各規則各自帶 utils),所以我不判成 major。
- ⚠ `kt-loadurl-external` 的 `intent-src` util(`:26`)已定義,但 `let/also/run` 那一支又把同一串 regex 內嵌了一次(`:93`)。
  - 這是規則內自己的重複,不是跨層。
  - 鄰居沒有這種既有 util 又內嵌副本的對照,交編排者判斷要不要合併。
- 樣本結構與 `_KTSEC_PLACE` 的登記(`"kt-webview-mixed-content-always": ("rules", "api.yml", "API-48")`)沿用既有表,沒有新結構。

不對齊共 2 條,其中 major 0 條(另有 2 個 ⚠ 交編排者,未計入條數)
