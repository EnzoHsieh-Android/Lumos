severity: major

### F1 Gradle/`src` 測試資料夾分支不比對副檔名、也不要求緊接在 src 下一層,任何語言的業務檔都可能被永久判成測試而不用家
severity: major
blocking: 是 — 直接違反這支函式自己文件宣稱的「過嚴、不漏」保證,是會讓程式檔悄悄逃過「每支檔有家」閘的假陰性,跟 r1 判 major 的 C1(頂層 Tests 只看名稱)同一類但影響面更廣(不限棧別、不限深度)。
- 規則①(頂層 suffix)有 `ext in exts` 卡副檔名,規則②(`src` 分支)完全沒有比對副檔名,也沒有要求 `test`/`androidTest` 緊接在 `src` 正下方——只要路徑裡任何位置出現字面叫 `test` 或 `androidTest` 的資料夾、而且它前面的任何位置曾出現過 `src`,不管中間隔幾層、不管是什麼語言,就會被判成測試。
- 已在乾淨 /tmp 副本(未改 repo 任何檔)重現,端到端跑 `_nodehome_required`:對一支 Go 業務檔 `backend/src/internal/test/handler.go`(跟 Kotlin/Gradle 毫無關係),`_testmap_is_test` 單獨判是 False(.go 不在測試地圖清單裡),但整條 `_nodehome_is_test` 判 True,`_nodehome_required` 回傳的需要家集合裡沒有它——即這支檔可以新增進 repo,提交前閘永遠不會要求它有家。同樣手法對 `.rs`/`.sh`/`.ps1` 業務檔也重現成立。
- 既有的漂移守衛(`scripts/test_lumos.py:36769-36772`)只用 `mod/src/{d}/x{該棧自己的副檔名}` 探測——`d` 永遠緊貼在 `src` 正下方、副檔名永遠是該棧自己的——完全沒測到「隔好幾層」與「別種語言副檔名」這兩種組合,所以這個洞沒被接住。
引句:「return any(seg in under_src and "src" in parts[:i] for i, seg in enumerate(parts[:-1]))」
file: `scripts/lumos:17821` 規則②的實際比對邏輯——`seg in under_src` 沒有任何副檔名檢查,`"src" in parts[:i]` 只要求 src 出現在更早的任意位置,不要求緊鄰
file: `scripts/lumos:17808` 函式自己的文件寫「Gradle 保留的名字,不分 JVM 語言」,但實測顯示連非 JVM 語言(Go/Rust/Shell/PowerShell)也會被放行,超出文件自陳的範圍
file: `scripts/lumos:18009` `_nodehome_required` 呼叫端把 `top_dirs` 傳進去,但規則②從不使用這個引數(只有規則①用),沒有等效的「旁邊要有同名資料夾」錨定
file: `scripts/test_lumos.py:36720` `t_nodehome_stack_test_dirs_not_required` 現有斷言沒有涵蓋「非緊鄰 src」與「外語言副檔名」的組合,是這個洞沒被抓到的原因

## 逐項判定

- 風險掃描點名的 `_NODEHOME_STACK_TEST_DIRS` 模組層級快取沒鎖:誤報,維持 r1 F1 的判斷——全檔搜尋 `threading|multiprocessing|ThreadPoolExecutor` 只命中 pitfalls 規則字串本身,repo 是單行程 CLI;另外查證這次改動後 `scripts/test_lumos.py` 裡所有讀 `TEST_PROFILES` 的測試都用 `dict(...)` 拷貝、沒有任何測試就地修改全域 `TEST_PROFILES`,所以就算在同一個 in-process 測試行程裡快取也不會因跨測試污染而算錯。
- 邊界:資料夾名剛好等於 `Tests`/`src`/`androidTest`(不帶前綴)——實測 `Tests/Foo.swift`(base 會算成空字串)、`src/Foo.swift`、`androidTest/Foo.kt`(前面沒有 `src`)三種都正確落回「要家」,不是漏洞方向。
- 邊界:大小寫變體(`apptests`、`androidtest`、`SRC`)——比對全程 `str.endswith`/集合成員比對皆大小寫敏感,變體一律判不到、退回要家,是保守方向,不是漏洞。
- 邊界:Unicode 與空白(含 NBSP)、點開頭資料夾——純字串切片與 `rstrip(".")`,無正規化需求,實測皆行為一致、無例外或誤判方向的問題;唯一的不對稱是 `base = top[:-len(suf)].rstrip(".")` 只剝點號分隔(對應 `.NET` 的 `Foo.Tests`),不剝空白或底線分隔的變體名——這會讓少見命名法「Foo_Tests」多要一次家,方向仍是保守(過嚴),沒有具體會壞的檔案能指出,不成立為缺陷。
- 邊界:路徑以裸檔名 `src`/`androidTest` 結尾(即該名字其實是檔名不是資料夾)——`parts[:-1]` 天生排除掉最後一段(檔名),實測確認不會被誤當成資料夾,不影響。
- 邊界:多個 `src` 出現在同一路徑——`"src" in parts[:i]` 只要任一個更早的 `src`存在即可,實測行為與設計一致,無新問題(這也是 F1 描述的同一種寬鬆邏輯的另一面,已併入 F1)。
- 漂移守衛對「新 dir_mode」與「空字串資料夾名」的假綠/假紅:跟 r1 F4 判斷一致——production 用 `if d` 濾掉空字串、測試裡漂移守衛沒濾,但兩邊分岔時測試會判紅(check⑤ 出 miss),不是假綠;新 dir_mode 若不落在 `suffix`/`rglob_under=="src"` 兩支,production 與守衛用同一組 `if/elif`,不會出現「production 認、守衛沒測到」的假綠,只是守衛完全不會被觸發、production 端維持保守。
- 圖譜鏡頭 8 個帶 INVARIANT 內容的固定席(bound-tests-gate、canary-audit、guard-kill、slim-get/install/uninstall 三篇、授權與歸屬、測試假綠形態):逐篇核對合約敘述都在講 code-loop 綁定測試執行機制、canary 落盤、guard kill rc 優先序、`.ps1`/CLAUDE.md 注入冪等與備份、vendored 白名單、還原翻紅釘方法論——這次 diff 只加了兩支私有函式與一支綁定測試,沒有動任何 `cmd_*`、canary 記錄、guard kill、slim 安裝/解除安裝或 `_VENDORED_TOOLKIT` 的程式碼,判全部不影響;F1 本身是「測試沒把這個場景寫進去」的覆蓋率缺口,不構成「測試假綠形態」節點所管的那種「翻紅釘沒接住」型缺陷(那篇管的是 slim-uninstall/deinit 系列既有測試,這次沒碰)。
- 其餘 16 篇超出上限只列名的節點:與 r1 F3 同結論——名稱上都是與 `_nodehome_*` 無函式呼叫或資料交集的其他子系統,無內容可逐條核對,不影響。

總結:最高 severity major,blocking 共 1 條
