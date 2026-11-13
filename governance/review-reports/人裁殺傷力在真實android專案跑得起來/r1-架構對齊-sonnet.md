severity: major

## 1. 分層與依賴方向
對齊。新邏輯的位置跟鄰居一致,沒有跨層直呼。
- 人裁指令 `cmd_situation_rule` 負責算連帶 import 的 `also`,再透過 `recipes_override` 交給 `cmd_guard_kill`。這跟現有的 `_situation_rule_kill` 做法一樣。
- `also` 的格式檢查放在 guard kill 那一層,而且是人裁與驗證共用同一支檢查。這跟 `_kill_old_issue`、`_kill_new_issue` 由 `_kill_judge_file` 與 guard kill 共用的做法一樣。
- 人裁先查 run_cmd,放在 `cmd_situation_rule` 跑殺傷力之前,位置跟 `_situation_rule_platform` 檢查 run_cmd 是否存在同一處。
- init 要看專案內容,走 `_init_test_profile(tp, root)` 那種「帶 root 去看專案」的先例。
- 對照:`/Users/enzo/harness/lumos-srl-android/scripts/lumos:27790`、`/Users/enzo/harness/lumos-srl-android/scripts/lumos:75736`、`/Users/enzo/harness/lumos-srl-android/scripts/lumos:35108`。
引句:「連帶替換交給殺傷力驗證(臨時配方多一個 `also` 清單)」

## 2. 命名與錯誤處理
大致對齊,有兩處差異,見下面 a2 和 a3。
- `--diff` 沿用 `_codeloop_disp_range`,metavar 也是現有的 `A..B`。
- 拒絕時 rc 2,訊息走 `_situation_rule_say`,印輸出前經 `_kill_esc`,都跟鄰居一樣。
- `also` 不合時判 `error`,跟現有的 `verdict: error` 同一處。
- 對照:`/Users/enzo/harness/lumos-srl-android/scripts/lumos:75138`、`/Users/enzo/harness/lumos-srl-android/scripts/lumos:27933`、`/Users/enzo/harness/lumos-srl-android/scripts/lumos:78877`。
引句:「`lumos situation-rule --diff <A..B>` 跟 `code-loop check --diff` 同一套規則(`_codeloop_disp_range`)」

## 3. 第二種做法
不對齊。設計另立了一套讀 settings.gradle 與判斷 Android application 外掛的解析,見 a1。連帶 import 的產生與 `also` 欄位沿用 `recipes_override` 路徑,沒有另立第二套殺傷力函式,這部分對齊。
- 對照:`/Users/enzo/harness/lumos-srl-android/scripts/lumos:40618`。
引句:「Android application 模組偵測只認外掛 id 與 `alias(libs.plugins.<名>)` 這兩種寫法」

## 4. 落點合不合理
大致合理,有一處落點不對,見 a4。`also` 寫進 Systems/guard-kill,人裁的 `--diff` 與 run_cmd 檢查寫進 Systems/棧別提問表態閘,這兩處都對。
- 對照:`/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:36`。
引句:「[[Systems/test-profile-multiplatform]] 加一行 WHY 講 Android 骨架」

## a1 另寫一套讀 settings.gradle 與判斷 Android 外掛的解析 ⚠
這條我標 major 但不確定。現有的 `_android_build_texts` 已經讀 settings.gradle(.kts)、各模組建置檔和 libs.versions.toml,並做了剝註解、層數上限、不跟符號連結、檔案必須在 repo 內這些防護。設計沒提到沿用它,而是自己規定了一套解析:找 `include`、找外掛 id、轉換 `alias(libs.plugins.<名>)`。它現在只回傳剝註解後的文字、不帶路徑,所以直接沿用可能要擴充,這是我拿不準的地方。
severity: major
blocking: 是
引句:「Android application 模組偵測只認外掛 id 與 `alias(libs.plugins.<名>)` 這兩種寫法」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40618`

## a2 偵測的起點是 repo 根,不是平台設定的 root
設計寫死「`settings.gradle` 在 repo 根,否則不猜」。專案既有做法是以平台設定的 `root` 為準,`load_platforms` 與 `_situation_rule_platform` 都這樣處理。多平台設定下 `platforms.kotlin.root` 可以是 `android/`,這時人裁先查 run_cmd 的範圍 4 應該從平台根找 settings.gradle,不該只看 repo 根。結構是對的,只是錨點不同。
severity: minor
blocking: 否
引句:「或 `settings.gradle` 不在 repo 根(Gradle 根在子目錄)時不猜」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:75736`

## a3 帳本摘錄長度跟現有的 200 字不一致
現有的 `tail` 是切 `[-200:]`,設計新加的摘錄改成 400 字,沒說為什麼。同一個欄位出現兩種長度,讀的人會分不清。
severity: minor
blocking: 否
引句:「現況:survived 與 abort 存的是基準輸出最後 200 字」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:27995`

## a4 init 骨架的說明寫進 test-profile-multiplatform,不是 init 骨架的家
`_init_config_skeleton` 的既有說明在 Systems/lumos-cli-lifecycle,那篇已經有同函式的 KEY 行。Systems/test-profile-multiplatform 講的是多平台測試綁定。計劃的 lands_in 把 Android 骨架 WHY 放到後者,會讓同一支函式的說明分散在兩篇。
severity: minor
blocking: 否
引句:「[[Systems/test-profile-multiplatform]] 加一行 WHY 講 Android 骨架」
file: `/Users/enzo/harness/lumos-srl-android/docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:36`

不對齊共 4 條,其中 major 1 條
