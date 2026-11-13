severity: minor

## b1 --import 的插入點行在整支檔裡不唯一時,事前檢查放行,殺傷力才報錯
severity: minor
blocking: 否
引句:「    old = lines[at] + "\n"」
file: `scripts/lumos:26775`(`_kill_also_apply` 要求那一行整行相等「恰好一行」)
1. 輸入:HEAD 那支檔的檔頭是 `package a` 與 `import x.Y`,body 的 KDoc 裡另有一行頂格的 `import x.Y`。人裁給 `--import "import q.Foo"`,`--new` 含 `Foo`。
2. `_situation_rule_imports_problem` 只在檔頭區找插入點,回傳 `also=[{old:'import x.Y\n', new:'import x.Y\nimport q.Foo\n'}]`,沒有問題。
3. 人確認後,`_kill_also_apply` 逐行比對全檔,命中 2 行。重現輸出:`連帶替換的那一行在套完主替換的檔裡出現 2 次(要恰好一行整行相等)`。guard kill 判 error。
4. 壞在哪:事前檢查已放行,人確認、殺傷力起跑後才被擋。只要檔裡別處也有同一行就會發生,例如範例碼塊或三引號字串裡的 import,或與 package 行相同的行。計劃沒動,不會損壞資料。
5. 事前檢查要在 `_situation_rule_imports_problem` 對全檔數同一行,不是 1 次就當場拒絕,並講明原因。
6. 這是 r1 就有的路徑,不是 r2 修補帶進來的。

## b2 run_cmd 的 `cd` 換了專案目錄,Android 模組的 test 任務判成不擋
severity: minor
blocking: 否
引句:「("cd 之後那段的 gradle", "cd sub && ./gradlew app:test --tests x", ["app:test"])):」
file: `scripts/lumos:76440`(`_situation_rule_android_cmd_problem` 只用 `-p` 的值換專案目錄)
1. r2 把 `-p`/`--project-dir` 當專案目錄,卻沒處理 `cd <目錄> && ./gradlew …`。〈用詞〉任務清單只講 `-p`,所以這是漏掉的同一族,不是違反字面。
2. 輸入:平台根是 repo 根,run_cmd 為 `cd android && ./gradlew :mobile:test --tests '*{method}'`,`android/mobile` 是 Android 模組。
3. 實測 `_gradle_task_list` 回 `[('', [':mobile:test'])]`。`_gradle_blocked_tasks` 去平台根下找 `mobile/`,那裡沒有建置檔,所以不擋。
4. 殺傷力因此起跑。實際在 `android/` 跑 Android 模組的 `test`,不收 `--tests`,結果是 killed_unattributed 或失敗,後面才被拒。這正是缺口 ③ 要在跑前擋下的情境。
5. 錯誤只出現在跑完之後,不會寫錯計劃。

## 檢查過、沒有問題的項目(不報)
- 檔頭掃描改用 `_strip_c_comments` 的新邊界:對下列輸入的行號與「行尾乾淨」判斷都對。
  - 區塊註解內的 import、`*/ import …` 同行接續、行尾開著的區塊註解。
  - 三引號字串內的 import、`@file:Suppress("(")` 字串內括號、`;` 串多句、BOM、CRLF。
  - 反引號名稱形狀會被後面的 `_KILL_IMPORT_RE` 擋。
- `_detekt_walk_segments(comments=True)`:
  - 行尾 `# …` 與註解內 `&& ./gradlew test` 都不算任務,下一行照常產出。
  - `sh -c './gradlew test # x'` 的內層註解也剝掉。
  - `test#foo`、`'A#b'` 因 `#` 不在詞首,不當註解。
  - 引號包住的 `#` 開頭詞被當註解是已知限制,檔案內已寫明。
- `--diff` 改用 `_lens_full_sha` 後:
  - 它帶 `^{commit}`,`HEAD:路徑` 與 `HEAD^{tree}` 解不出來,回 None,仍被擋。
  - `HEAD~0`、`HEAD@{0}` 解出與 HEAD 相同的完整 sha,右端判定正確。
  - `_situation_rule_target` 改 `_lens_full_sha(rr, "HEAD")` 與右端比對用同一種完整 sha,一致。
- run_cmd 非字串檢查放在 `not pentry.get("run_cmd")` 之後:
  - 空清單、0 這類假值走「沒有宣告」那條訊息,不丟例外。
  - 非空的清單或數字走新的 rc 2,之後的 `"YOUR_MODULE" in cmd` 不會碰到非字串。
- ⚠ `-pandroid`(`-p` 值貼在同一個詞)這種寫法,`_gradle_args_tasks` 取不到專案目錄,實測回 `('', ['test'])`。我不確定 Gradle 是否接受這種寫法,查不到佐證,不列 finding。

## 附:圖譜鏡頭
這次沒有附固定席節點,也沒有備援段。改動只影響人裁殺傷力與 `_detekt_walk_segments`、`_gradle_args_tasks` 兩個共用函式。detekt 判定沿用 `comments=False`(預設)與 `values=None`,實測任務清單與原行為相同,不影響。

最嚴重 severity:minor;blocking 共 0 條。
