severity: minor

派工詞點名的暖機鎖檔 `…ffdba22.json.warming` 在我檢查時不存在(`ls` 回 No such file),所以沒有鎖可處理,也沒刪任何鎖。

我逐 hunk 讀完整份 diff,追了 `cmd_guard_kill`、`_kill_also_*`、`cmd_situation_rule` 拆出的小函式、init 骨架和 `_kt_bj_segments` 這幾條呼叫路徑。幾個值得講的點先放前面:
- `cmd_situation_rule` 拆開後,原本每個守衛都還在,只是搬了位置。順序仍是段列、計劃、旗標、配方、工作目錄乾淨、平台、試插、殺傷力。
- 原本的 `return` 值語意沒變。
- `also` 在 CRLF 檔案上不會因換行對不上而失敗。HEAD 版的 `_kt_sit_read_many` 和工作樹的讀檔都已經把 `\r\n` 統一成 `\n`。
- 找不到可證明的 major。以下三條都是失敗的安全方向(多拒絕或晚擋),沒有壞資料的路徑。

## t1 缺前導冒號的 Android `app:test` 不會被擋
severity: minor
blocking: 否
引句:「parts = t[1:].split(":")[:-1] if t.startswith(":") and t.endswith(":test") else []」
file: `scripts/lumos:76343`
1. Gradle 接受不帶前導冒號的相對任務路徑,`./gradlew app:test --tests '*{method}'` 是合法寫法。init 骨架說明自己也教人填 `feature:search` 這種無冒號的模組名。
2. `_gradle_blocked_tasks` 只認 `t.startswith(":")`。我對真函式實跑,`app:test` 和 `:app:test` 都放進同一個 Android 的 `app/build.gradle.kts` 樣本:`:app:test` 回 `[':app:test']`,`app:test` 回 `[]`。
3. 結果是範圍 4 要在跑殺傷力之前擋下的情況放行了。殺傷力會先冷建構,基準才因 Android 的 test 任務不收 `--tests` 而 abort,等於晚擋。

## t2 `_gradle_task_list` 自己重寫切詞,漏掉既有解析器處理的 `sh -c` 包裝
severity: minor
blocking: 否
引句:「start = next((i for i, w in enumerate(words) if _is_gradle_head(w)), None)」
file: `scripts/lumos:76308`;既有的 `_detekt_walk_segments`、`_GRADLE_VALUE_OPTS` 在 `scripts/lumos:40609` 一帶
1. repo 已有一套 Gradle 命令解析:`_detekt_walk_segments` 處理續行、換行、環境變數與包裝詞、`sh -c` 展開;`_GRADLE_VALUE_OPTS` 是較完整的帶值選項表。新碼另寫一套,選項表只有五個。
2. 實跑 `sh -c "./gradlew test --tests '*{method}'"`:任務清單是 `[]`,頂層 test 沒被擋。
3. 另一個次要差異:`./gradlew --console plain test` 會把 `plain` 當成任務。這個無害,因為 test 仍被抓到。
4. 重用方式:改叫 `_detekt_walk_segments` 取段,再用 `_GRADLE_VALUE_OPTS | {"--tests"}`。

## t3 檔頭的 `@file:` 註記跨多行時,補 import 被拒,而且原因寫錯
severity: minor
blocking: 否
引句:「elif t and not t.startswith(("//", "@file:", "package ", "import ")) and t != "package":」
file: `scripts/lumos:76193`
1. 輸入:
   ```
   @file:OptIn(
     Foo::class
   )
   package a
   import x.Foo
   ```
   再帶 `--import "import k.flatMapConcat"`。
2. `_situation_rule_header_rows` 在第二行 `Foo::class` 就收尾,`package` 和 `import` 都沒進檔頭區。實跑回「檔頭區既沒有 import 也沒有 package 那一行…」,但這支檔明明兩者都有。
3. 這符合規格〈用詞〉的檔頭區定義,是失敗的安全方向,只是人會被誤導。ktlint 換行過的 `@file:OptIn(...)` 在真專案會遇到。
4. 要補的話,檔頭區要處理括號未閉合的續行,或訊息改講「檔頭區在第 N 行提前結束」。

## t4 `_gradle_build_android` 另寫一份讀建置檔的程式
severity: minor
blocking: 否
引句:「_SR_BUILD_NAMES = ("build.gradle.kts", "build.gradle")」
file: `scripts/lumos:76295`、`scripts/lumos:76320`;既有 `_KT_BUILD_FILES` 在 `scripts/lumos:39445`,`_android_build_texts` 在 `scripts/lumos:40757`
1. 讀前 1MB、剝註解、連結不出資料夾這套規則,`_android_build_texts` 已經有。新函式照抄,檔名清單也另寫一份。
2. 代價:將來有人改「什麼算建置檔」或讀取上限,只會改到其中一邊,Android 專案判定在兩處結果會不一致。
3. 重用方式:`any(_KT_BUILD_ANDROID.search(t) for t in _android_build_texts(folder, max_depth=0))`。

## 附:圖譜鏡頭
這次沒附固定席節點(`LUMOS-LENS` 說明沒有釘到節點),所以不逐條答。規格的 `lands_in` 有三篇:`Systems/guard-kill`、`Systems/棧別提問表態閘`、`Systems/lumos-cli-lifecycle`。我不評它們,因為這份 patch 沒含筆記改動。

規格〈範圍〉1 到 6 在程式裡各有對應實作,逐項核過沒有偏離:
- 「`also` 只有臨時配方認」由 `recipes_override is not None` 守住。
- 判 `error` 而不是 `drifted`,且在寫檔之前,符合規格。
- `fail_excerpt` 的欄位位置、200 字與 800 字的上限、遮路徑的先後順序,都和規格一致。

測試差異 9 支涵蓋 S1 到 S9,我沒找到抓不住必要行為的缺口。

我在 `/tmp/lumos-seat-work/code-人裁殺傷力android/通才-sonnet/` 做了唯讀實驗(只載入模組,沒改 repo),跑完已刪除。

最嚴重 severity: minor,blocking 共 0 條。
