severity: minor

## A1 新場景的常數與 data-kind 命名跟 android 場景不同一套
severity: minor
blocking: 否

兩個既有 android 場景用的是 `ANDROID_TITLES` 加 `android-*` 的 data-kind。新場景的場景名叫 `android-acceptance`,常數卻只叫 `ACCEPTANCE_TITLES`,data-kind 又用 `e2e-*` 而不是 `android-*`。這裡跟既有做法剛好反過來:既有的場景鍵是 `android-e2e`,data-kind 是 `android-*`。結構本身(`*_TITLES` 常數加獨立的 `validate_*` 函式,在 `validate()` 裡一行呼叫)完全照鄰居,所以只算 minor。

對照:``file: `assets/readme-diagrams/generate.py:489` ``(`ANDROID_TITLES`)、``file: `assets/readme-diagrams/generate.py:496` ``(`android-inputs`)、``file: `assets/readme-diagrams/generate.py:522` ``(`android-record`)
引句:「ACCEPTANCE_TITLES={"en":"Android: a full device check before push.","zh":"Android：推之前在實機上整套驗收一次"}   # validate 也用它認圖,改標題只改這裡」
引句:「b+='<g data-kind="e2e-record">'+rect(38,680,684,96,"#14243a","#344967",14)」

## A2 缺工具的錯誤訊息格式跟同函式內、收集腳本的寫法不同
severity: minor
blocking: 否

同一個 `preflight()` 裡的既有檢查,以及收集腳本,訊息都是 `找不到 {tool};用環境變數 …= 指定`。新的檢查另寫了一種格式:多帶了「(記憶體與穩定性要用,找的是 …)」,環境變數名稱也改由變數 `{var}` 帶入。

對照:``file: `scripts/templates/android-e2e-run.sh:253` ``、``file: `scripts/templates/android-stability-collect.sh:378` ``、``file: `scripts/templates/android-stability-collect.sh:381` ``
引句:「die(f"找不到 {name}(記憶體與穩定性要用,找的是 {tool});用環境變數 {var}= 指定")」

## A3 測試尾端多印一行 ✓,跟同族 e2e 測試不一樣
severity: minor
blocking: 否

`t_android_e2e_vendored` 和 `t_android_e2e_run_script` 都不在尾端印 `✓`。檔內別處(例如 `t_gov_split_*`)有這個慣例,但 e2e 這一族沒有。這是日誌層面的差異,結構沒變。

對照:``file: `scripts/test_lumos.py:19024` ``(`t_android_e2e_vendored`)
引句:「print("  ✓ t_android_e2e_preflight_stability_tools")」

## 三問

1. **分層與依賴方向**:跟鄰居一致。
   - 產生器:新場景放在 `generate.py` 的場景函式層,在 `SCENES` 登記,檢查走 `validate_android_acceptance`,由 `validate()` 呼叫。這是複製 `validate_android` 的掛法(``file: `generate.py:597-603` ``)。
   - 範本:檢查加在 `preflight()` 內,沒有新增跨層呼叫。
   - 測試:擴充既有的 `_e2e_script_env(td, **proj)` 把參數轉給 `_e2e_proj`,沒有另起一套輔助函式。
2. **命名與錯誤處理**:有兩處差異,見 A1 和 A2,另有 A3 的日誌差異。其餘都對得上:`die(...)`、`check(...)` 的訊息形式、環境變數 `TP`/`JAVA_HEAP_DUMP`、`say`/`die` 的使用。
3. **第二種做法**:沒有。
   - `test_data` 判斷在兩支獨立範本各存一份,是因為兩支都是照抄進消費專案的單檔腳本,無法共用。守衛用「抽出那一行比相等」,跟檔內 hook 複本逐字相同的守衛(``file: `scripts/test_lumos.py:23549` ``)是同一種做法,另附 `★前置★` 斷言確保各恰好一行。
   - 產生器沒有另起新的掛法,圖的元件(`rect`、`path`、`arrow`、`badge`、`text`)都用既有的,沒有重寫。
   - README 放圖用的是既有的 `<p align="center"><a><img>` 寫法。

不對齊共 3 條,其中 major 0 條
