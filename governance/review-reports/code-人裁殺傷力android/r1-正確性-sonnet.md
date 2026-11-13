severity: minor

我逐 hunk 讀完 diff 與測試差異,在 `/tmp/lumos-seat-work/code-人裁殺傷力android/正確性-sonnet/` 的複本裡實跑。檔頭區、任務清單、失敗摘錄、`also` 套用、`--diff` 入口驗這幾條主路徑都對得上規格:

- **CRLF**:`_kt_sit_read_many` 與 `cmd_guard_kill` 都會把 `\r\n` 轉成 `\n`,所以預檢和殺傷力兩邊看到同一份文字,CRLF 檔不會出錯。
- **fail-closed**:`also` 套不上時,預檢先擋,`cmd_guard_kill` 也會在寫檔前判 error。
- **新舊互讀**:舊 kill-log 沒有 `fail_excerpt`、舊治理帳沒有 `imports`,都不影響讀取。
- **測試**:`t_kill_log_fail_excerpt` 在複本上 14 條全過。
- **範圍**:我沒找到 major 以上的錯誤行為。下面五條都是規格措辭、擋太嚴或測試覆蓋面的問題。

## c1 規格條款 S1/S2 的字面跟〈範圍〉1 與預期值表矛盾
severity: minor
blocking: 否
引句:「當 --import 的名稱不是這次新寫法才有的觸發字、或形狀不合、或檔裡已有同一行,人裁指令 應 在跑殺傷力之前拒絕」
file: `docs/lumos-toolchain-knowledge/Projects/人裁殺傷力在真實Android專案跑得起來_計劃.md:99`
1. S2 條款字面是「名稱不是觸發字就拒絕」。
2. 〈範圍〉1 寫「名稱不必是觸發字(D-5 換成 `SharingStarted.Lazily` 要補 `SharingStarted`)」,預期值表 S1 第四列也收下這種輸入。實作與測試 `t_situation_rule_import_flag` ④ 都照後者做。
3. `[S1]` 條款(第 98 行)同樣只講「新寫法觸發字的 import」。
4. 後來讀條款的人照字面會以為 `SharingStarted` 應被拒,但實作收下。這是設計審 r1 收斂後沒改回條款句式留下的不一致。
5. 建議改條款字面,對齊「名稱要在 --new 以識別字出現、檔頭還沒 import」。

## c2 檔頭區判定:合法檔頭被拒,或插入點落進註解
severity: minor
blocking: 否
引句:「elif t and not t.startswith(("//", "@file:", "package ", "import ")) and t != "package":」
file: `scripts/lumos:76201`(`_situation_rule_header_rows`)
重現:`/tmp/lumos-seat-work/code-人裁殺傷力android/正確性-sonnet/t4.py`,用 `python3.14 t4.py` 跑。
1. **多行 `@file:` 註記**:
   - 輸入:`@file:OptIn(\n    ExperimentalCoroutinesApi::class,\n    FlowPreview::class,\n)\npackage a\nimport b.C\nclass X\n`。
   - 第二行 `ExperimentalCoroutinesApi::class,` 不是檔頭行,迴圈在第 1 行就 break,`package` 與 `import` 都沒進檔頭區。
   - 結果回「檔頭區既沒有 import 也沒有 package 那一行」,被拒,而檔頭其實都有。
   - 這個輸入正落在主要用途:`flatMapLatest` 本來就要 `@file:OptIn(ExperimentalCoroutinesApi::class)`,用 ktlint 折行後就會踩到。
   - 單行的 `@file:OptIn(...)` 正常。
2. **UTF-8 BOM**:輸入 `"\ufeffpackage a\nimport b.C\nclass X\n"`。第一行不以 `package ` 開頭,同樣被拒,而且訊息會誤導。
3. **區塊註解裡被註解掉的 import**:輸入 `package a\n\nimport b.C\n/*\nimport old.Thing\n*/\nclass X{}\n`。
   - `in_block` 的行也進了 `rows`,被當成最後一行 import。
   - 插入點變成 `import old.Thing\n`,也就是補的 import 被塞進註解裡,對編譯沒有效果。
   - 殺傷力會判 `killed_unattributed` 被拒,摘錄只看到 `Unresolved reference`,看不出原因。
   - `_situation_rule_has_import` 同理,會把註解裡的 import 當成「已有」。
4. 三種都是 fail-closed(被拒),不會放行錯的判定。

## c3 `app:test`(沒有開頭冒號)擋不住
severity: minor
blocking: 否
引句:「parts = t[1:].split(":")[:-1] if t.startswith(":") and t.endswith(":test") else []」
file: `scripts/lumos:76345`(`_gradle_blocked_tasks`)
重現:在複本裡建 `proj/app/build.gradle.kts`,內容 `plugins { id("com.android.application") }`,然後執行 `_gradle_blocked_tasks(_gradle_task_list("./gradlew app:test --tests '*{method}'"), proj)`。輸出 `[]`(已刪掉暫存專案)。對照 `:app:test` 輸出 `[':app:test']`。
1. Gradle 接受 `app:test` 這種相對根專案的寫法,效果跟 `:app:test` 一樣,對 Android 模組一樣不收 `--tests`。
2. 實作只認 `:` 開頭,run_cmd 寫成 `./gradlew app:test --tests '*{method}'` 時預檢放行。
3. 殺傷力會先冷建構基準(可能十幾分鐘),才因 `Unknown command-line option '--tests'` 判 abort。
4. 規格〈用詞〉字面只寫 `:<模組>:test`,所以不算違反規格。

## c4 測試抓不到「名稱要整字出現」被改成子字串
severity: minor
blocking: 否
引句:「if not re.search(rf"\b{re.escape(name)}\b", new):」
file: `scripts/test_lumos.py`(`t_situation_rule_import_flag_rejects`,測試差異第 160–208 行)
重現:在複本把這行改成 `if name not in new:`,然後執行 `python3.14 scripts/test_lumos.py -k t_situation_rule_import_flag`,結果 22 passed、0 failed。
1. 〈範圍〉1 明寫 `\b<名稱>\b`。
2. S2 ② 只測「名稱完全不在 `--new`」(`debounce`),沒有「名稱只是 `--new` 某個識別字的一部分」(例如 `--new` 含 `myflatMapConcatX`)。
3. 守衛被改壞測試仍全綠,是覆蓋缺口。

## c5 測試抓不到「工作樹先於家目錄」的遮罩順序
severity: minor
blocking: 否
引句:「for p, tag in ((wt, "<worktree>"), (home, "~")):」
file: `scripts/test_lumos.py`(`t_kill_log_fail_excerpt`,測試差異第 546–642 行)
重現:在複本把順序換成 `((home, "~"), (wt, "<worktree>"))`,然後執行 `python3.14 scripts/test_lumos.py -k t_kill_log_fail_excerpt`,結果 14 passed、0 failed。
1. 目前的實作順序是對的:輸入 `wt=/Users/enzo/tmp/lumos-kill-1`、`home=/Users/enzo` 時,輸出 `<worktree>/a.kt`。
2. 但測試的 `wt` 在 `/var/folders` 或 `tempfile` 底下,從來不在家目錄底下,這個順序沒有被測試保護。
3. 實際會踩到的情況是 `TMPDIR` 設在家目錄底下。順序一換,摘錄會變成 `~/…/lumos-kill-…`,不再是規格要的 `<worktree>`。

## 附:圖譜鏡頭
這次沒附固定席節點(LUMOS-LENS 註明未釘到節點),我不逐條答。`.warming` 鎖檔不存在,不需處理。

最嚴重 severity:minor;blocking 共 0 條。
