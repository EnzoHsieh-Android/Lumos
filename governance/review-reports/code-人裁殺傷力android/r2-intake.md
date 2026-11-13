# r2 收貨紀錄(code-人裁殺傷力android)

七席全到(sonnet),收齊後一次寫進卷證;引句除資安席(clean、無引句)外全數錨定 r2-snapshot.patch。

## 修補因果核對(上一輪修補造成的)

- a1(檔頭掃描自寫 Kotlin 剝註解)、z1(檔頭掃描每行建 dict 記憶體放大):r1 G3 修補新寫的 `_situation_rule_header_scan` 造成 → 回歸。
- a2(`--diff` 兩端自叫 git、沒用 `_lens_full_sha`):r1 修補沒動 `--diff`,是原實作就有 → 非回歸。
- c1/b1/t1/g1(只看第一個 gradle 段):r1 G1 換成 detekt 切段時保留了「第一段就回傳」,舊實作同樣限制 → 非回歸(修補沒修乾淨的同族)。
- b2(行尾 `#` 註解當任務):r1 G1 改用 detekt 拆段(commenters 設空)新帶進來 → 回歸。
- b3(run_cmd 非字串丟例外)、g2(WHY 行漏寫無冒號)、c1 附帶 `-p` 子目錄、b1 附帶 `:test`:原實作或文件漏寫 → 非回歸。

## 分組

| 組 | 根因 | 發現 | 最高 | 處置 |
|---|---|---|---|---|
| R1 | 任務清單只取第一個 gradle 段;`#` 註解、`-p` 子目錄、`:test` 根專案、run_cmd 非字串 | c1、b1、t1、g1、b2、b3 | major | 折:每個 gradle 段的任務合併;遇 `#` 開頭的詞停;`-p/--project-dir` 的值當模組路徑基準;`:test` 當根專案 test 照 (a) 判;run_cmd 不是字串 → rc 2 印設定錯 |
| R2 | 檔頭掃描另寫一套 Kotlin 剝註解;每行建 dict | a1、z1 | major | 折:整檔先過既有 `_strip_c_comments(kotlin=True, keep_newlines=True)` 再逐行判檔頭,只留 import/package 行的索引 |
| R3 | `--diff` 兩端自叫 git | a2 | major | 折:改用 `_lens_full_sha` |
| R4 | 筆記 WHY 行漏寫 `app:test` 無冒號也擋 | g2 | minor | 折 |

## 先查世界

- R1 PRIOR-ART:POSIX shell 語法 `#` 起頭的詞到行尾是註解(https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_03);Gradle `-p` 指定專案目錄、任務路徑相對它解析(https://docs.gradle.org/current/userguide/command_line_interface.html#environment_options);`:test` 是根專案的 test(同上 executing_tasks_in_multi_project_builds)。
- R2 PRIOR-ART:專案既有 `_strip_c_comments` 說明寫「全庫只有這一個入口……不留兩套掃描」,支援 Kotlin 巢狀註解、三引號字串、樣板;採用既有,不另寫。
  方向:對 — 第二輪「另寫一套」類又出現 major(r1 a1 Gradle 切詞、r2 a1 Kotlin 剝註解),業界與專案慣例都是「單一解析入口」:https://kotlinlang.org/spec/syntax-and-grammar.html#lexical-grammar 、https://docs.python.org/3/library/shlex.html ;派工詞寫明「每寫一個解析或掃描前先 grep 既有同功能函式,報告列搜了什麼」。
- R3 PRIOR-ART:專案既有 `_lens_full_sha`(走 `_lens_git`,有 timeout 與 OSError 處理)。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| c1、b1、t1、g1 | 四席各自實跑 `_gradle_task_list("./gradlew clean && ./gradlew test …")` → `['clean']` | HIT |
| b2 | 席報告實跑 `# test only` → 任務含 test | HIT |
| a1 | 讀 `_strip_c_comments` 說明與新 `_situation_rule_code_of_line` | HIT(讀碼) |
| a2 | 讀 `_situation_rule_diff_problem` 的 subprocess.run 與 `_lens_full_sha` | HIT(讀碼) |
| z1 | 席報告量 4MB 空行檔峰值約 1GB | HIT(席位量測) |
