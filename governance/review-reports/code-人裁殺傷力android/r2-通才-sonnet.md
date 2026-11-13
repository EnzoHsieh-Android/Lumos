severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/47ebf45980d0bdbe5649fdd88d49a06caa7c1a9c79bc3e574bbe39410d0647f9.json.warming` 不存在(`ls` 回找不到),不需要處理,也沒有刪任何東西。我跑的實驗放在 `/private/tmp/lumos-seat-work/code-人裁殺傷力android/通才-sonnet/`,沒有改 repo。

## t1 Gradle 任務清單只看第一個 gradle 段,規格寫的是每一段
severity: minor
blocking: 否
引句:「每一段第一個檔名是 `gradlew` 或 `gradle` 的詞之後、不以 `-` 開頭的詞」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:_gradle_task_list`(`for seg in _detekt_walk_segments(...)` 找到第一個 gradle 段就 `return`)

失敗場景:
1. 平台 `run_cmd` 寫成 `./gradlew clean && ./gradlew :app:test --tests '*{method}'`。`app/build.gradle.kts` 宣告 `com.android.application`。
2. `_gradle_task_list` 在第一段 `./gradlew clean` 就回傳 `['clean']`。第二段的 `:app:test` 沒有被看到。
3. `_gradle_blocked_tasks` 回 `[]`,`_situation_rule_android_cmd_problem` 回 None,人裁不擋。
4. 殺傷力照跑,Android 的 test 任務不收 `--tests`,基準非綠,判 abort。人要等到基準跑完(最長 600 秒以上)才看到失敗,而不是在入口收到 rc 2 和設定提示。這就是範圍 4 要避免的情況。

翻紅重現(我在 `/private/tmp/lumos-seat-work/code-人裁殺傷力android/通才-sonnet/t3.py` 跑過):

```
./gradlew :app:test --tests '*{method}'                    -> [':app:test']
./gradlew clean && ./gradlew :app:test --tests '*{method}' -> []
./gradlew assemble; ./gradlew test                         -> []
```

只有第一行有被擋,後兩行應該各擋下 `:app:test` 與 `test`。

這不是修補新造成的退步。舊的自寫切詞遇到 `&&` 一樣停下。問題是修補把 `_gradle_task_list` 說成「沿用 detekt 那組」,實作卻只取第一段,跟規格〈用詞〉寫的「每一段」不一致。測試也沒有多段案例抓這點。

## 其餘檢查結論(沒有問題,不另列 finding)
- `_kill_run_dir` 改在平台根跑 `run_cmd`:`_run_bound_tests` 與 filter probe 的 `_kill_run(key[1], key[0], …)` 用的是 `pentry["root"]`,殺傷力現在和它們同一處。`_kill_run` 只剩這四個呼叫端,其他呼叫端沒被弄壞。平台根就是 repo 最上層時,`rel == "."`,行為不變。
- `_kill_mask_paths` 的邊界判斷:我看過 `/var` 與 `/private/var`、`/Users/enzo2` 的情形,沒有找到會漏遮或誤遮的真實輸入。
- `_situation_rule_header_scan` 與 `_imports_problem`:我實際跑了 KDoc 開頭、`@file:` 括號裡有字串或字元、`;` 連寫、區塊註解沒收尾、CRLF、只有 package、反引號 package、別名同名、行尾註解共 11 組,結果都合理。
- `_gradle_args_tasks` 抽出來與 detekt 共用:它預設引數用的 `_GRADLE_VALUE_OPTS` 在第 40638 行定義,早於使用處,detekt 路徑行為不變。
- `_gradle_test_module` 與 `max_depth=0` 讀模組建置檔:`:test` 不誤擋,`testDebugUnitTest` 不擋,`app:test` 與 `:app:test` 同樣處理。
- 修補後 `_situation_rule_android_cmd_problem(pdata, src)` 只有 `scripts/lumos` 的一個呼叫端,沒有舊簽名殘留。

## 附:圖譜鏡頭
這次沒有附固定席節點,收到的是備援段,所以不逐條答。我只確認了規格檔的〈用詞〉與〈範圍〉2、4,以及 S11 條款,都和修補後的執行目錄行為一致(上面的 t1 除外)。

最嚴重 severity:minor,blocking 共 0 條。
