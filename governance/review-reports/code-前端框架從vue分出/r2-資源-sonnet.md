severity: major

範圍:資源鏡頭,第 2 輪修補(修前 600d7b02、修後 b9ff5494)。我用 `git show` 取出兩版 `scripts/lumos`,放在 `/tmp/lumos-seat-work/code-前端框架從vue分出/資源-sonnet/` 下的 `lumos_before` 與 `lumos_after` 跑實驗。沒有在 repo 內執行任何 git 寫入指令。

## 上一輪兩個 major 的驗證

**1. 空行二次方:建置檔那一半已修好,同一類問題在 `.kt` 檔頭和 `_ROLE_UI_IMPORT` 還在(見下方 F1)。**
- 實測:`_kt_flavor_at` 讀一份 65536 個空行的 `build.gradle.kts`,修前 7.65 秒,修後 0.0 秒。
- 其他大建置檔輸入在修後都是 0.01 到 0.02 秒:512KB 的 `/*/*/*`、`a/*` 無結尾、`a://`、`//`、全空白、全換行、`android \t` 重複。
- 新的 jest 樣式 `Tests\b[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed` 在 512KB 的「`Tests ` 加全數字」、`Tests` 重複、`1 ` 重複、尾端全空白都不超過 0.3 秒。

**2. 每支重掃:已修好。**
- 300 支 `.kt` 共用同一份 40KB 建置檔,修前 0.21 秒,修後 0.0 秒。
- `_kt_build_verdict` 的 `lru_cache(64)` 以文字為鍵,最壞約 32MB。角色路徑的 `blobs` 和工作樹路徑的快取都回傳同一個 str 物件,所以雜湊只算一次。
- 沒驗到:建置檔超過 64 份、目錄交錯排列時記憶會被擠掉。分類迴圈照路徑排序,實際不會。

**3. 預算與子程序,其餘各項成立。**
- 分類迴圈改看預算後,逾時會把 `blobs` 清空,後面的檔判不出。`.kt` 因 `content` 是 None 直接回 None;`.ts` 因 `package.json` 讀不到回 None。方向安全,沒有誤放行。
- 子程序:`_nodehome_cat_blobs` 用 `subprocess.run(timeout=)`,逾時或 Ctrl-C 都會被收掉。這次沒有新增子程序。

## Finding

**F1 `.kt` 檔頭匯入判定仍是二次方,預算管不住。**

severity: major
blocking: 是
歸因:有證據的原有漏查(修前、修後結果相同,不是這次修補造成)。
- 位置:`_ROLE_ANDROID_IMPORT = re.compile(r"^\s*import\s+(?:android|androidx)\.", re.M)`。`_kt_flavor_at` 對 `content[:64K]` 呼叫它。`_ROLE_UI_IMPORT[ext].search(content)` 用同一種 `^\s*`,吃的是最多 512KB 的全文。
- 問題:修補只把建置檔那條正規式改成 `[ \t]*`,同一份 diff 的註解自己寫明「`\s*` 會吞換行,搭多行旗標二次方」。檔頭匯入判定的正規式沒有跟著改。
- 輸入一:`A.kt` 內容為 65536 個 `\n`,旁邊放一份 spring-boot 建置檔,呼叫 `_kt_flavor("A.kt", repo)`。修前 7.63 秒,修後 7.56 秒。
- 輸入二:`_review_roles(root, "HEAD~1", "HEAD", budget=3.0)`,新增 `V.dart` 內容為 131072 個 `\n`。修前 31.24 秒,修後 31.32 秒,回傳 `timed_out=False`。預算 3 秒,實際用了 31 秒,還報告沒逾時,因為預算只在檔與檔之間檢查,單次 regex 打斷不了。512KB 全空行的 `.dart`、`.swift`、`.kt` 依平方外推約 8 分鐘。
- 放大:pitfalls 的 `_stack_platform_excluded` 對最多 300 支 `.kt` 逐支呼叫 `_kt_flavor`,沒有時間預算。每支 7.5 秒,最壞 300 支約 37 分鐘。改檔前推播的 hook 對單一檔也一樣。
- 修法方向:這幾條行首空白一律改 `[ \t]*`,或先 `.lstrip()` 再逐行比對。
- 引句:「行首空白只收空格與 tab:\s* 會吞換行,搭多行旗標在一大段空行上二次方回溯(r1 資源席:6.5 萬空行 7.5 秒)」

**F2 超過大小上限的 Android 建置檔,在角色路徑被當成「不存在」,往上找到伺服端建置檔,判成 backend。**

severity: major
blocking: 是
歸因:有證據的原有漏查(修前、修後輸出都是 backend)。
- 位置:`_nodehome_cat_blobs_capped(..., max_total_bytes=_ROLE_MAX_TOTAL_BYTES)`,連同被截斷的建置檔候選。
- 問題:`_nodehome_cat_blobs_capped` 把「超過 `max_bytes` 或總量上限」的檔回成 None。`_kt_flavor_at` 對 None 的解讀是「沒有這個檔,往上找」,而工作樹路徑的 `_worktree_text(max_bytes=)` 對同樣情況回 `""`(停、判不出)。兩條路徑不一致。
- 輸入:根目錄 `build.gradle.kts` 含 `org.springframework.boot`。`app/build.gradle.kts` 含 `com.android.application`,另加 80000 行註解墊到約 640KB。`app/src/Main.kt` 沒有匯入。
- 預期:判不出(None)。
- 實際:`_review_roles` 回 `{'app/src/Main.kt': 'backend'}`。建置檔縮成小檔時回 None,正確。
- 總量上限路徑同理:`total + n > max_total_bytes` 時較近的大檔被跳過,較遠的小檔仍會被收進來。
- 後果:Android 檔被判成後端,違反計劃 B10 自己寫的「判錯的方向只准是判不出,不准把 Android 判成伺服端」。
- 發生條件不常見(要超過 512KB 的建置檔,或整批超過 16MB)。
- 引句:「快取一筆最多一份檔(大小受 max_bytes/head 管);呼叫端各自有檔數上限,所以總量有界。」

## 三問的回答

1. 原問題的修復效果:建置檔空行二次方與每支重掃,有修前修後的行為證據,已修好。分類迴圈看預算的邏輯路徑成立。我沒有用 `_ROLE_CLOCK` 注入跑測試。
2. 修補處的相鄰路徑:F1 和 F2 都是「同一條機制的另一個入口沒收」,修前就在,不是修補造成。
3. 新發現在兩版的結果:見 F1 與 F2 的修前、修後數字。

## 未驗與備註

- `_worktree_text` 讀 `package.json` 沒有 `max_bytes`。`_linter_config_hits` 與 `_uses_vitest` 都會整份讀入。`_uses_vitest` 修前也是整份 `read_text`,不是新增的風險,也沒造大檔實測。
- 同一個函式 `_kt_strip_comments` 先剝區塊再剝行註解。`// 說明 /*` 後面若還有 `*/`,中間的 `com.android` 宣告會被吃掉,可能把 Android 專案判成 server。這屬正確性鏡頭,我沒有實測。
- 表態記錄裡「py-hotpath na」不成立:正規式在角色路徑和 pitfalls 路徑上對每支檔跑,且吃使用者提供的檔案內容。
- 不確定是否同時被其他席報的點:F1 的 `_ROLE_UI_IMPORT` 部分(`.dart`、`.swift` 的 512KB 全文)。

最嚴重 severity:major。blocking 共 2 條(F1、F2)。

涉及檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos`(b9ff5494 版,`_ROLE_ANDROID_IMPORT` 約第 30499 行、`_nodehome_cat_blobs_capped` 約第 33460 行)。實驗檔都在 `/tmp/lumos-seat-work/code-前端框架從vue分出/資源-sonnet/`,收貨後由編排者刪除。
