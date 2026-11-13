severity: minor

## c1 run_cmd 行尾註解帶單引號時,整行被丟掉,擋下檢查失效
severity: minor
blocking: 否
引句:「`#` 開頭的詞起到行尾是 shell 註解,不算任務;那一段的 `-p`/`--project-dir` 的值是它的專案目錄(相對平台根)。」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40647`(`_detekt_split_segments`,shlex 遇到未配對引號丟 ValueError 就回 None)
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40715`(`_detekt_walk_segments` 對 None 直接 `continue`)

失敗場景:
1. 平台根是 Android 專案(`app/build.gradle.kts` 宣告 com.android.application),run_cmd 寫成 `./gradlew :app:test # don't run all`。
2. `_detekt_split_segments` 把整行當一串切詞,`don't` 的引號沒配對,回 None。`_detekt_walk_segments` 因此整行跳過,連 `#` 前面的 `./gradlew :app:test` 都不產出。
3. `_gradle_task_list` 回空清單,`_situation_rule_android_cmd_problem` 回 None,人裁不擋,往下跑殺傷力。
4. 同一條命令把註解換成沒有引號的 `# no quote`,就會被擋下(rc2)。
5. 規格〈用詞〉任務清單寫「`#` 之後不算任務」,已知限制只提 `"#x"`,沒提註解內含引號。這是 r2 b2 同族沒修乾淨的地方。
6. 影響:Android 專案的裸 `test` 沒被攔下,殺傷力會把整個模組的測試跑一遍。這時會落在 killed_unattributed、被拒收,是安全方向的失敗,所以只給 minor。

重現,在 `/Users/enzo/harness/lumos-srl-android` 的 `scripts/lumos` 上執行(我用 importlib 載入):
- `list(m._detekt_walk_segments("./gradlew :app:test # don't", comments=True))` 輸出 `[]`。
- `m._gradle_task_list(...)` 輸出 `[]`。
- 對含 `app/build.gradle.kts` 的假專案呼叫 `_situation_rule_android_cmd_problem`,`# don't run all` 與 `# it's fine` 都回 pass。
- 未寫成測試:`t_situation_rule_android_run_cmd_segments` 的註解對照組都不含引號。

## 附:圖譜鏡頭
這次沒附固定席筆記,`LUMOS-IMPACT` 範圍(`6302b71a..8f27a98c`)也沒有附上節點清單,所以沒有節點可逐條判。我只對照了規格檔〈用詞〉〈驗收條款〉S5–S7 與〈預期值表〉的 S5–S7 列。

- 檔頭區(用詞 檔頭區):改用 `_strip_c_comments(kotlin=True)` 後,以下輸入的 `also` 插入點都對,結果與規格一致:
  - 檔頭加 BOM、shebang、CRLF。
  - 多行 `@file:` 註記、行尾有開著的區塊註解。
  - 只有 package、檔尾沒換行。
  - 同一行用分號寫兩句 import、import 帶 `as` 別名。
  - `Name` 在 `--new` 裡只以子字串出現(`flatMapConcatX`)時,會拒絕。
- 行尾是否乾淨的判斷,我做了變異:把 `nxt.startswith(_SR_LINE_MARK)` 改成永遠為 True,`t_situation_rule_header_scan_strip` 和 `t_situation_rule_import_flag_inserts` 兩支翻紅,所以該守衛有行為測試抓。
- 4MB 輸入(整檔是字串、行註解、大括號、空行)跑完 1.5 秒內,最高記憶體約 320MB,沒有新的效能問題。
- 讀檔一致性:`_kt_sit_read_many` 與 guard kill 的 `open(encoding="utf-8")` 都把 CRLF 轉成 LF 且保留 BOM,所以 `old` 與 `_kill_also_apply` 的整行比對不會因換行或 BOM 對不上。
- `--diff`:`_lens_full_sha` 會加 `^{commit}`,所以 blob 或 tree 的 sha 不會被當成左端放行。`head` 改用 `_lens_full_sha(rr, "HEAD")` 後,與右端比對的格式一致。
- `run_cmd` 不是字串:`isinstance` 檢查的 `multiplatform` 鍵存在於 `load_platforms` 的兩種回傳,端到端測試通過。
- 已知限制:`cd android && ./gradlew :app:test` 不會被擋。規格已寫明「不加 cd」,屬已知範圍外。
- 兩支新測試(`t_situation_rule_header_scan_strip` 與 `t_situation_rule_android_run_cmd_segments`)在本機各自全過。

我建的暫存目錄 `/private/tmp/lumos-seat-work/code-人裁殺傷力android/正確性-sonnet` 已用字面絕對路徑刪除。派工詞指定的鎖檔 `.warming` 不存在,所以沒有刪鎖。

最嚴重 severity:minor,blocking 共 0 條。
