# Lumos 測試品質實驗專案

這裡是五個獨立消費專案，實際使用各自安裝的 `scripts/lumos test-quality`。用途是驗證測試是否真的會抓錯，以及收證工具會否把無效執行算成成功。

## 重跑

```sh
cd /Users/enzo/lumos-test-quality-lab-20261008
python3 run_experiment.py node
python3 run_experiment.py laravel
# 有本機 Semgrep 時加 --semgrep /absolute/path/to/semgrep
```

每次新建 artifacts/run-*，不覆寫歷史證據。runner 只改本案例的 Pricing 實作，finally 還原；請逐次執行，不要同一專案同時跑兩次。明示執行可信本機程式，沒有沙盒。Python runner 使用標準庫。

Node 使用 node:test（本次 Node v24.16.0），無 npm 依賴。Laravel 使用官方 Laravel12 skeleton、composer.lock 鎖住依賴（本次框架12.69.3、PHPUnit11.5.57、PHP8.5.10）；搬到其他機器請先 composer install 與 composer check-platform-reqs。Laravel12 是本次明確固定的驗證版本，非最新版宣告。

## 做了哪些驗證

| 情境 | Node | Laravel |
|---|---|---|
| 正常實作 | 3 個獨立需求案例通過 | 3 個 Unit + 2 個 Feature 通過 |
| 故意回傳0 | 2 個金額案例失敗 | 2 個金額 + 1 個 HTTP 案例失敗 |
| 還原原始實作 | 全綠且來源快照相同 | 全綠且來源快照相同 |
| 等價重構 | 案例全綠 | 案例全綠 |
| 篩選不存在的測試 | 收證拒絕，即使原生runner退出0 | 零案例收證拒絕 |
| 故意自己比自己 | 選配 Semgrep 列出候選 | 選配 Semgrep 列出候選 |

Laravel Feature 真正啟動框架、送 POST /quotes、驗 JSON、持久化並查詢記憶體 SQLite；另驗負數回422、沒有資料副作用。前置斷言確認 testing、sqlite、:memory:。不接正式資料庫、真郵件或外部服務。

## 證據與界線

本次結果：[Node](node/artifacts/run-yk2hztlm/check.json)、[Laravel](laravel/artifacts/run-5eb89al1/check.json)。各資料夾有原生 XML、stdout/stderr、來源／測試／設定快照、hash、receipt、零選中負例。

故障被抓到不等於測試有獨立答案。「重抄演算法」反例可能也會抓到這次故障，靜態掃描目前不會完整抓出跨語言同源算法。因此 check 明示 verdict=not_assessed，需求來源只記 declared；仍由審查者對照 REQUIREMENTS.md、預期值來源與公共介面。保持行為的重構只在本需求域（非負且100的整數倍）說明等價，本次案例全綠不證明所有輸入。

這個實驗接的是 test-quality capture/check；Node 的原生 runner 並未冒充 node-jest 的 bound-tests/guard profile。Pest、Jest、Vitest、Laravel13、Dusk、外部服務、正式DB與其他語言框架均不由本次實驗推論已驗。

設計參照：[Laravel12 Testing](https://laravel.com/docs/12.x/testing)。

## C#、Android、iOS 接入

同一入口支援三棧：

```sh
python3 run_experiment.py csharp
python3 run_experiment.py android
python3 run_experiment.py ios
```

每棧執行 baseline、fault、restored、refactor、zero-selected、compile-error 六階段，保留原始報告／退出碼。所有價格預期來自各自 REQUIREMENTS.md；重構域限定非負且100整數倍，整數結果相同。這仍是部分原生合成驗證，不授予整棧 synthetic-verified 或真專案品質。

- C#：SDK9.0.117／net9.0、xUnit、VSTest、JunitXml.TestLogger4.1.0；global.json與packages.lock.json鎖定本次範圍，沒有ASP.NET API、NUnit或MSTest资格。SDK入口可用 LUMOS_LAB_DOTNET 覆寫；實驗配置 runtime指令目前固定本機已裝SDK，換機先調run_platform_experiment.py的配置。
- Android：AGP8.13.2、Gradle8.13、Kotlin2.2.21、JUnit4.13.2，本機3個價格測試加API35獨立模擬器2個instrumentation案例，驗私有SharedPreferences儲存及拒絕理由。不是僅JVM試跑；不推論Compose、UI、生命週期、其他裝置/API版本。local.properties是本機SDK指路，換機須更新。
- iOS：Xcode26.6／iOS26.5模擬器、XCTest、XcodeGen2.46.0、xcbeautify3.2.1；3個價格加2個測試專用UserDefaults案例。原生.xcresult及xcodebuild退出碼保留；reporter僅轉JUnit。Xcode65在橋接中轉成共同非零1，編譯／零案例必須由報告與目標身份拒絕，不能單看退出碼。Swift Testing、真機、UI測試與其他Xcode組合另驗。

### 平台啟動與配置

本機獨立模擬器已建立；重跑前啟動本專案的裝置。勿同時在同一consumer跑兩輪，runner在finally還原來源，但生成目錄是單一工作槽。

```sh
# Android（另一個終端持續執行，或加 &；等待 adb getprop sys.boot_completed 為1）
/Users/enzo/Library/Android/sdk/emulator/emulator -avd Lumos_TestQuality_API35 -port 5580 -no-window -no-audio -no-snapshot-save -gpu swiftshader_indirect
# iOS（若已booted則略過boot命令）
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun simctl boot 8B63215A-8A85-43A0-A874-0092E1ECAE88
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun simctl bootstatus 8B63215A-8A85-43A0-A874-0092E1ECAE88 -b
```

換機需安裝Android SDK/API35 system image、JDK17及Xcode/iOS runtime，建立自己的獨立裝置，設定 LUMOS_LAB_ANDROID_SDK、LUMOS_LAB_ANDROID_SERIAL、LUMOS_LAB_XCODE、LUMOS_LAB_IOS_DESTINATION；iOS destination格式為platform=iOS Simulator,id=裝置UUID。Android local.properties同步指向該SDK。C#先固定相應SDK並 dotnet restore --locked-mode；Android與iOS的開發工具依賴不加入Lumos核心。

原生設計參照：[dotnet VSTest](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test-vstest)、[JUnit logger](https://github.com/spekt/junit.testlogger)、[Android命令列測試](https://developer.android.com/studio/test/command-line)、[xcbeautify](https://github.com/cpisciotta/xcbeautify)。

### 重構例子的溢位核對

本次review找到「先乘9再除10」中間乘法可能溢位；綠燈不足以證明全域等價。未覆寫舊refactor卷證，三棧額外收refactor-safe、check-safe.json；重跑入口已改成先除10再乘9。對限定整數100倍數域，n=10q，n-n/10=9q，中間結果不超過n。Node使用Math.floor(n/10)*9、PHP用intdiv(n,10)*9；跨語言型別範圍仍須另核對。此為真正取捨與修正，不由check自行判等價。

本次正式核對結果：[C#](csharp/artifacts/run-e20xop57/check-safe.json)、[Android](android/artifacts/run-f1kw9ly6/check-safe.json)、[iOS](ios/artifacts/run-bd7n9ned/check-safe.json)。runs.json 保存本次卷證的相對位置；歷史補跑腳本只以source.txt歸檔，日後從run_experiment.py建立全新的完整run。
