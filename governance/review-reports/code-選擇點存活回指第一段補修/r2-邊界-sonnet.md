severity: minor

我只做了靜態審讀,補修差異裡沒有 blocker 或 major。另外實測了一個我擔心的點:基準檔 JSON 深層巢狀不會丟 RecursionError,此點不成立。

severity: minor
blocking: 否
`scripts/lumos`(補修後 `_CHOICE_COV_SRC_SKIP` 一行):共用跳過清單 `CODE_SKIP_DIRS` 是給 C# 和 Node 掃描用的,內含 bin、obj、dist、publish、vendor。補修把它整份併進主程式套件走訪,這些資料夾在任何深度都會被跳過,而舊版沒有跳。
失敗場景:主程式有 `com/acme/publish/Publisher.kt`、`com/acme/dist/…` 或 `com/acme/bin/…` 這類套件資料夾,它們的 package 不會被收進套件集合。只碰這些套件的測試,專案類別有紀錄數會算成 0。若前 3 支 Robolectric 測試都這樣,斷路器會誤判成「覆蓋設定沒生效」而整組關覆蓋。這是少見的巧合,所以降到 minor。
測試只蓋根層 `vendor/v` 和 `app/build`,沒蓋主程式套件深處的 bin、dist、publish。建議把清單縮成 Gradle 專用,例如 build、.gradle、.git、.idea、node_modules,或只在根層或 src 以外套用。
引句:「_CHOICE_COV_SRC_SKIP = frozenset(CODE_SKIP_DIRS | {".gradle"})」

severity: minor
blocking: 否
`scripts/lumos`(`_choice_cov_test_srcset`):判斷「上一層叫 src」靠 `os.path.basename(parent) == "src"`,有兩個界線漏洞。
- 平台根本身叫 `src` 時,例如傳統 Java 版面 `proj/src/org/...`,根底下頂層的 `testing`、`tests`、`testapp` 這類頂層套件資料夾會被當測試原始碼資料夾跳過。
- 根字串帶尾斜線時,例如 `app/src/`,走訪第一層的 `d` 是 `app/src/`,`basename` 為空字串,`app/src/test` 不會被跳過,測試類別反而算成專案類別。我沒追到 `pentry["root"]` 是否會帶尾斜線,所以這點是推測。
這兩種只有在根不是標準 Gradle 版面時才會碰到,影響方向是多跑,不是少跑。
引句:「return os.path.basename(parent) == "src" and (name.startswith(("test", "androidTest")) or name.endswith("Test"))」

severity: minor
blocking: 否
`scripts/lumos`(`_choice_cov_src_pkgs` 的 package 正規式):只讀每支檔的前 8KB,且必須在行首。
- 授權標頭超過 8KB 時找不到 package。
- 同一行的 `/* … */ package a.b;` 也找不到。
這兩種情況都會把空字串 `""` 當預設套件加進集合,是舊版就有的行為,補修沒處理。
測試沒有蓋「超長標頭」和「宣告前有同行區塊註解」這兩個極端輸入。
引句:「_CHOICE_COV_PKG_RE = re.compile(r"^[ \t\ufeff]*package[ \t]+([\w.`]+)", re.M)」

上輪列的角落我都看過,其餘沒有問題:
- 基準檔 `el` 為 0、1e308、True、10 的 400 次方、NaN、負數,`rc` 為 0.0 或 True,以及超過 64KB 的檔,都正確回 None。
- 基準檔寫失敗時,覆蓋資料照用。
- `entries` 和 `seen` 的上限比較是剛好超過才停,第一個檔就超過也行。
- 一個平台根只掃一次,符號連結與具名管道不開。

總結:最高等級是 minor
