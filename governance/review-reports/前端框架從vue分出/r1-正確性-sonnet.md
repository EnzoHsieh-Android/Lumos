severity: major

審的是 `22317c77` 凍結的〈前端框架從 vue 分出_計劃〉。各節已讀,對照了 `scripts/lumos` 現況。已核對:`_node_flavor_of` 與 `_stack_key_for_file` 兩處改法對得上程式;`_stack_applicability` 與 `_idiom_skill_for` 的現況也對得上。〈八格盤點〉、F2 的 react 題組、F7 範本、W7 的 doctor/init 段落,除下列各條外已讀,無 finding。

### 1. B10 判伺服端的訊號會把 Android App 判成伺服端
spec 段落:〈做法〉B10 判伺服端的訊號,以及決策 d2。

severity: major
blocking: 是
判準:照字面實作會讓真的 Android 專案少問三題,守衛被放寬。

問題:spec 說「寫了 org.springframework.boot 或 io.ktor → 伺服端」,但沒限定只比對 `plugins { }` 區塊。Android 判定又只認字面 `com.android.application` / `com.android.library`。現行 Android Studio 範本用版本目錄寫 `alias(libs.plugins.android.application)`,字面找不到這個字串。

具體例:
- 輸入:Android App 模組的 `build.gradle.kts`,內容是 `plugins { alias(libs.plugins.android.application) }`,依賴裡有 `implementation("io.ktor:ktor-client-android:...")`,改動是一支沒有 `import android.` 的 `.kt` 檔(例如 repository)。
- 預期:判不出,或判 Android,照舊問 kt-compose、kt-leaks、kt-startup。
- 照 spec:Android 字面沒命中、`io.ktor` 命中,於是判伺服端。這三題被拿掉,角色判後端。

KMP 共用模組、純 JVM 的 Android 子模組(沒套 Android 外掛、只用 ktor-client)同理。這與 spec 自己的守衛面宣稱「判不出一律照舊」互相矛盾,S24、S25 也沒有覆蓋這個輸入。

引句:「都沒有或找不到 → 判不出。只看檔案頭的匯入與建置檔的外掛宣告,不猜程式內容。」

佐證:file: `scripts/lumos:30263` 附近的 `_ROLE_UI_IMPORT` 本來就是刻意收窄,理由是寬名單會把資料層判成畫面。

### 2. B10 的角色判定沒有接上批次預取與版本讀取,正式路徑拿不到建置檔
spec 段落:〈做法〉B10 的「判伺服端的訊號」與「角色」兩條。

severity: major
blocking: 是
判準:照字面實作後,單元測試會綠,正式派工路徑卻永遠判不出伺服端,S26 形同假綠。

問題:`_review_role_for` 的 `reader` 在正式路徑是 `blobs.get(f"{ref}:{rel}")`(file: `scripts/lumos:30410`)。`blobs` 只含 `_review_role_wanted` 預取的路徑。該函式對 `.kt` 只預取檔案本身,對 `.ts/.js` 才預取 package.json 候選(file: `scripts/lumos:30429`)。spec 完全沒說要把 build.gradle(.kts) / pom.xml 的候選路徑加進預取清單。

具體例:派工時 `.kt` 檔的 `reader("app/build.gradle.kts")` 一律回 `None`。
- 在 `_node_flavor_at` 的形狀下,`None` 被當成「沒有這個檔」並繼續往上找,最後吃到根目錄的宣告,或判不出。
- 單元測試直接塞假 reader,所以照樣綠。

另一個相關缺口:spec 寫「結果快取」,但沒說快取鍵要含版本。package.json 的快取只在工作樹讀取那條路使用。若新函式以檔案路徑為鍵快取,版本讀取與工作樹讀取會互相污染。

引句:「判不出的情況(沒有建置檔、兩種都沒寫)照舊不附」

佐證:file: `scripts/lumos:30417` 的 `_review_role_wanted`,加上 `scripts/lumos:30395-30410` 的 `blobs` 組裝。

### 3. 「全部 .kt 檔判伺服端」的集合範圍沒定義
spec 段落:B10 的規則、S22、S24。

severity: minor
blocking: 否
判準:規則本身清楚,但集合的邊界不寫,實作者會各做各的,最壞是 Android 專案少問題。

問題:集合是否含下列三種檔,spec 沒說:
- 測試檔:`_by_stack` 已排除測試檔(file: `scripts/lumos:47284`),但 `androidTest/` 下的 `.kt` 是否算「Android」不明。
- 刪除的檔:增刪行都算,但檔已不存在時①的檔內匯入讀不到。
- 超過 `_ROLE_MAX_BYTES` 沒讀內容的檔:不明。

另外,pitfalls --diff 還有另一份舊語意的整組清單 `stack_qs`(file: `scripts/lumos:47276`)。spec 只寫「整組清單在輸出前濾掉同一批題」,沒指名這份也要濾。`_STACK_PERF_QUESTIONS` 只存題目原文、沒有題號,過濾要靠 `platform` 旗標反查,spec 也沒寫。

引句:「當改動的 .kt 檔全部判成伺服端、改動行撞到 kt-leaks 或 kt-startup 的觸發詞時,這兩題應不列。」

### 4. vitest 樣式的實作細節會踩兩個讀者
spec 段落:F1 的 `_RAN_EVIDENCE` 統一樣式。

severity: minor
blocking: 否
判準:實作者用 `^` 錨定行首但漏了多行旗標,會讓所有 vitest 證據都判成沒跑過,S4 才會抓到。

問題:`_RAN_EVIDENCE["re"]` 有兩個讀者,讀法不同。
- `_ran_evidence_check` 對整段文字、去掉 ANSI 色碼後 `re.search`(file: `scripts/lumos:54296` 附近)。
- `_kill_cap` 對每一行用 `re.search(keep_re, l)`,不去色碼(file: `scripts/lumos:19395`)。

spec 說「行首(前面可有空白)」,但樣式字串是兩邊共用的單一字串。要錨行首就必須內嵌 `(?m)`。在 `FORCE_COLOR` 下,逐行讀者看到的行首是色碼,錨定會失效。實際上「Test Files」本身就不含「Tests」,錨行首不必要,spec 可以不錨。

引句:「全部 skipped 的那行沒有 passed,照舊判沒跑過。」

### 5. `.eslintrc*` 命中時印出的範本在 eslint 9 跑不動
spec 段落:W7、S9。

severity: minor
blocking: 否
判準:使用者照印出的步驟走,冒煙會紅,屬引導不完整,不是壞系統。

問題:spec 自己在 PRIOR-ART 寫了「舊 `.eslintrc*` 要設 `ESLINT_USE_FLAT_CONFIG=false` 才讀」。但 W7 偵測到 `.eslintrc.json` 時,印的範本與 flat config 那份完全相同。

具體例:eslint 9 的專案只有 `.eslintrc.json`,範本 `npx eslint -f @microsoft/sarif ...` 會報找不到 `eslint.config.js`。使用者得到的指引在 `lint-check --smoke` 才紅。

引句:「[S9] 當 doctor 在根目錄只有 .eslintrc.json 的 repo 跑時,[F] 段應同樣認得它。」

### 6. S23 的「其他 kt 題整組列出」與現況不符
spec 段落:S23。

severity: minor
blocking: 否
判準:照字面寫測試,對現有行為會紅,寫的人得自己猜哪些題算「其他」。

問題:`shape_only` 題(Spring 兩題與 kt-extcode)本來就不因行數超門檻而亮,spec 自己在〈現況〉B10 也這麼寫。拿掉 Android 三題後,超門檻時整組亮的是協程、Dispatchers、Flow、集合四題。S23 的「其他 kt 題」字面包含 shape_only 的三題。

引句:「kt-compose、kt-leaks、kt-startup 應不列,其他 kt 題應照舊整組列出。」

severity: major
— blocking 共 2 條(第 1、2 條)
