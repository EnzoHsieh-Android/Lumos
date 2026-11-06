severity: minor

審了 r2 修補,三道修補都修好了,**沒有擋件的發現**,剩 5 條 minor。我實跑了 `_android_ci_has_lint_task` 28 組、`_android_plugin_missing` 與 `_detekt_plugin_values` 32 組、`_android_build_texts` 16 組、`batch4_expected_tags` 24 組,另對真 `lumos lint-check --json` 做了端對端一次。

## 修補三問

**A1 換成找字**
- ①修好了。上輪重現輸入 `./gradlew assembleDebug \` 接 `lintDebug`,續行、`:app:lint`、`check`、矩陣 `lint${{ matrix.v }}` 都判有接。整行註解、`lintKotlin`、`lintFix`、`lintVital`、`lintAnalyze`、`lintReport`、`make check`、`echo lint` 判沒接。
- `lintFixtureDebug` 依規定判有接;`-x lint` 依天花板判有接。
- ③「同一形狀」見 F4。
- ②帶進一個新洞,見 F1。

**A3 切命令與展開**
- ①修好了。`$HOME`、`${HOME}`、`~`、已設的環境變數、`sh -c`、`--plugins=`、`-p`、相對路徑(`cwd=/` 仍對 repo 根)、逗號第二支缺檔都判對。
- 變數沒設判不了不印;缺檔時一條命令只印一則。
- ②新洞見 F2。

**建置檔掃描**
- ①修好了。具名管道不卡;`Pods`、`vendor`、`governance`、`*-knowledge`、`build`、隱藏資料夾不進。
- 根目錄先讀、深度 3 之內、200 支上限都對。
- 60 支各 1 MB 約 1.4 秒,未封閉引號與 `/*` 洪水各小於 0.1 秒,沒有效能問題。
- ③見 F3。

**型錄口徑搬進 check.py**
- ①修好了。`Android Lint:` 前綴認得;預設關、`opt-in`、待查、相近都不標。
- 真型錄 `catalog_problems()` 回空清單。
- 用同一口徑重算:94 列單標 Lint、7 列單標 cr、19 列雙標,與型錄一致。

**常數樣式 `[A-Z][A-Za-z0-9_]*`**
- ①沒有重現 `MAX_ITEMS` 報錯的情況,但我沒有重跑 detekt。測試 `t_detekt_compose_rules_shared_config` 新增了 `MAX_ITEMS` 一列守著。

## 發現

### F1 A1 把路徑裡的 `build` 當成任務字,常見的 CI 寫法會讓提醒被吞
severity: minor
blocking: 否
- 位置:`scripts/lumos:39026` 與 `39029` 附近的 `_android_ci_has_lint_task`。
- 它用 `[A-Za-z][\w:-]*` 抽詞,`/` 不算詞內字元,所以 `app/build/outputs` 會抽出獨立的 `build`。舊版是以空白與標點切詞,不會切開路徑。這是修補自己帶進來的回歸。
- 最小重現:CI 只有 `run: ./gradlew assembleDebug && cp app/build/outputs/apk/debug/app-debug.apk .`,`_android_ci_has_lint_task` 回 True。我用 `lint-check --json` 端對端確認,A1 沒有印出來,而這份 CI 實際沒跑 lint。
- 同類:`./gradlew test; cat lint` 也判成有接。
- 影響只是少印提醒,不擋任何東西;但這條路徑寫法比 `-x lint` 常見得多,不在計劃天花板列的範圍內。
- 引句:「if re.search(r"gradlew|\bgradle\b|\barguments:", ln) and any(」

### F2 A3 對反引號命令替換不判成「判不了」,可能誤印
severity: minor
blocking: 否
- 位置:`_android_plugin_missing` 的判不了條件只看 `"$" in pth`。
- 重現:`detekt --plugins \`echo $HOME/x.jar\``,`_detekt_plugin_values` 回 `` ['`echo'] ``,`_android_plugin_missing` 回 True。`x.jar` 其實存在,卻印了 A3。`$(echo …)` 因為帶 `$` 判不了而被正確跳過,反引號寫法不同。
- 罕見,只是提醒。
- 引句:「展開後還有 `$`(變數沒設)的判不了、不算。」

### F3 建置檔剝註解只認 C 式註解,`gradle/libs.versions.toml` 的 `#` 註解沒剝
severity: minor
blocking: 否
- 位置:`_android_build_texts` 對所有檔(含 toml)都走 `_kt_strip_comments`。
- 重現:toml 檔內容 `# compose-lint-checks` 加 `[versions]`,函式回傳的文字仍含 `compose-lint-checks`,A2 會被這行註解吞掉。
- 這與函式註解「註解裡提到的不算宣告」不符。
- 引句:「剝掉註解後的文字(同 `_kt_build_verdict`:註解裡提到的不算宣告)」

### F4 同形狀沒改齊:T4 不剝註解,A1 的 CI 讀法也漏掉 Jenkinsfile 的 `//` 註解
severity: minor
blocking: 否
- 計劃與 `_android_ci_has_lint_task` 的 docstring 都說「跟 T4 找 `detekt<變體>` 同一個形狀」。但 A1 經 `_ci_workflow_texts` 剝了註解,T4 `_detekt_ci_has_typed_task` 仍走 `_ci_config_texts` 讀原文。
- 重現:workflow 只有 `# - run: ./gradlew detektDebug`,T4 回 True(判成已接),同一檔 A1 卻判沒接,兩個提醒對同一份檔的結論不一致。
- 另外 `_ci_workflow_texts` 只認 `#` 註解。Jenkinsfile 的 `// sh './gradlew lintDebug'` 被當成有接,實測 True。
- 引句:「for text in _ci_config_texts(repo_root, github_only=True):」

### F5 計劃範圍 4 的口徑句沒跟著程式與型錄更新,舊句仍寫「開頭」且漏 `Android Lint:`
severity: minor
blocking: 否
- 位置:`Projects/Android現成檢查接上CI與推送前_計劃.md` 範圍 4 的 diff 上下文(約第 144 行)。
- 計劃原句寫「以 `androidx`、`內建`、`slack` 開頭、帶一個大寫開頭的規則碼」。程式(`_B4_LINT`)與型錄已改成「含 `androidx:`、`androidx.<套件>:`、`內建:`、`slack:`、`Android Lint:` 接規則碼」,不要求開頭。
- 計劃不是唯一依據,但同一個口徑現在有三種說法;這一條補正計劃那一句即可。
- 引句:「某一段以 `androidx`、`內建`、`slack` 開頭、帶一個大寫開頭的規則碼」

## 測試獨立性

我讀了 `t_lint_android_ci_advice`、`t_kt_catalog_batch4_wiring`、`t_detekt_compose_rules_shared_config` 的新增部分。
- 判準夠獨立,沒有照抄實作。
- 我想得到的改壞多半會翻紅:拿掉 `expandvars` 或 `expanduser`、把相對路徑改成對 cwd(測試從 `cwd="/"` 跑)、拿掉具名管道防護、拿掉型錄口徑的預設關清單。
- 型錄自檢的兩個變異副本也驗過會報。
- 唯一抓不到的是 F1,因為測試的 A1 負例裡沒有帶 `build/` 路徑的 gradlew 行。F1 的重現可直接補成一條負例。

## 圖譜鏡頭

固定席範圍算不出,我依指示讀了三篇。
- `Systems/lint-declaration-health.md`:新 WHY 與程式一致。`--json` 仍共用同一個字串清單,A 條目以 `[CI]` 或 `[kt 第 N 條]` 開頭可分。沒有 `--json` 的其他消費者會解析舊格式。不影響 T1 到 T4 與 P1、P2 的合約,提醒不改退出碼這條成立。
- `Systems/linter精選目錄.md`:A1 與 A3 的說明與程式一致。下載命令是先存暫存檔、雜湊對了才改名,語法無誤。其中 curl 網址 HTTP 200。「跟 T4 一樣只看字面」的說法受 F4 影響,細節不同。
- `Systems/kotlin規則包.md`:WHY 指向 `batch4_expected_tags`,對得上。「官方預設關的六條」與 `B4_DEFAULT_OFF`(另含已移除的 ComposeRememberMissing)不衝突。

## 計劃〈依據來源〉

- 15 個出處網址我全部連過,HTTP 200,含外掛 jar 下載網址。
- 逐頁核對了三處:
  - Slack 規則頁:`ComposeUnstableReceiver` 與 `ComposeUnstableCollections` 寫 disabled by default,`ComposeM2Api` 寫 disabled default and opt-in。
  - Slack 發行說明:1.6.0 寫「requires AGP/lint 9.3+」,1.6.1 寫「Build against lint 32.4.1」,1.4.2 的 lint 31.7.1 只在版本表有列,我沒有逐頁核對。
  - Android lint 頁:standalone 對 Gradle 專案會報錯、`-Dlint.baselines.continue=true` 的寫法都在。
- 我沒有重做「6 個公開專案實跑」那一行,也沒有跑 OpenSSF 那條 PR 的內容核對。
- 其餘各行(含 A1、A3、`TopLevelPropertyNaming` 那幾行)都對得上程式與測試名。

## 角色卡

- be-api-compat:`--json` 的 `advisories` 條目格式有改,A3 從 `[CI] A3:` 改成 `[kt 第 N 條] A3:`。但 A3 是同一分支新增,全庫沒有解析這個前綴的程式,舊版 lumos 或舊 `lint.json` 也不吃這個欄位,不構成相容問題。不影響。
- be-authz:本次沒有任何端點或授權路徑改動。不影響。

總結:最嚴重是 minor,會擋 0 條。

審查席臨時目錄 `/tmp/lumos-seat-work/code-android現成檢查/正確性-sonnet/` 已用字面路徑刪除。
