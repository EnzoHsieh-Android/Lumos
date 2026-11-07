severity: major

我把表格與出處的怪輸入逐個餵給 `_plan_source_cell_ok`、`_plan_sources_problems`、`_plan_first_days_batch` 與 `lumos spec-gate`(在 `--shared` 臨時 clone 上跑,已刪)。下面只列有失敗場景的發現。

### F1 出處「反引號路徑」只看工作目錄檔案,不看大小寫、不看有沒有進版控
severity: major
blocking: 是
引句:「        if _validate_repo_ref(Path(rr), tok, None)[0] == "ok" and (Path(rr) / tok).is_file():」
file: `scripts/lumos:37635`(`_validate_repo_ref` 在不給 `at_sha` 時只用 `target.exists()` 判斷)

| 輸入 | 實際 | 預期 |
|---|---|---|
| `` `SCRIPTS/LUMOS` `` 與 `` `Scripts/lumos` `` | 在 macOS(APFS 不分大小寫)回 True | 大小寫不符不該算存在。Linux 的 CI 會回 False,同一份計劃本機過、CI 擋 |
| `` `.git/HEAD` `` 與 `` `.git/config` `` | True | 讀者在 repo 裡查不到,不該算 |
| 反引號寫一個本機有、但未追蹤或被 gitignore 的檔 | 可預期為 True(我沒另外造檔實測,依 `.is_file()` 只看工作目錄推論) | 讀者 clone 後查不到,不該算 |
| `` `scripts/lumos/` `` 尾端斜線(指向檔案) | True | 可接受,僅記錄 |
| `` `scripts/lumos:99999` `` | True,`:行號` 剝掉後不驗行號 | 設計明寫「去掉 :行號」,不算 bug,僅記錄 |

用本機檔案系統判存在,結果會隨平台與工作目錄狀態而變,「出處讀者查得到」這條沒守住。

### F2 被 HTML 註解包住的整張表也算「有依據來源節」
severity: minor
blocking: 否
引句:「    sec = _h2_section_lines(text, _PLAN_SOURCES_H2_RE, heads=heads)」

- 輸入:`<!--\n## 依據來源\n\n| 機制 | 依據 | 出處 |\n|---|---|---|\n| a | b | https://example.com/x |\n-->`
- 實際:`_plan_sources_problems` 回 `(1, [], [])`,視為合格。
- 預期:渲染後看不到的表不算。
- 場景:AI 把舊表註解掉再改寫,或貼樣板時留著註解,新計劃就放行。`_visible_lines` 只處理圍欄,不處理 HTML 註解。

### F3 健檢 S22 的批次首次日期,對「從 Projects 外面搬進來」的檔跟單篇版不一致
severity: minor
blocking: 否
引句:「規則同 _plan_first_day:取提交日期、改名跟得過去(-M,依時間順序把舊路徑的日期接給新路徑)、複製不跟;淺複製或讀不到回 None(呼叫端只看 created)。」
引句:「                            "--name-status", "--format=%x01%cs", "--", f"{vrel}/Projects" if vrel else "Projects"],」

- 重現:`v/Systems/x.md` 在 2026-10-01 加入,2026-11-20 `git mv` 成 `v/Projects/x_計劃.md`。
- 實際:`_plan_first_days_batch` 回 `2026-11-20`,`_plan_first_day` 回 `2026-10-01`。pathspec 限在 Projects 下,來源在範圍外,git 把這次改名當成 A。
- 預期:兩者一致。
- 影響:`created` 缺失或較舊時,健檢會列出一篇規格閘不擋的舊計劃,違反設計「舊計劃不列」。對本 repo 414 篇 Projects 筆記做批次對單篇的全量比對是 0 差異,所以只有跨目錄搬移會觸發。

### F4 frontmatter 壞掉或缺 `type` 的計劃會整個略過〈依據來源〉,沒有任何提示
severity: minor
blocking: 否
引句:「    return (n is not None and str(rel).startswith("Projects/") and str(rel).endswith("_計劃.md")」

- 輸入:開頭 `---` 沒有收尾、`type: project` 讀不到的 `壞fm_計劃.md`,新計劃日期、出處寫 `bad`。
- 實際:規格閘不印〈依據來源〉那一行,推送前重查與健檢也都略過,直接放行。
- 預期:至少印一行「型別讀不到,不查」。
- 備註:目前 345 篇 `_計劃.md` 全是 `type: project`,現況沒人觸發;壞掉的 frontmatter 要靠別的檢查擋。

### 已驗過、沒問題的項目
- **表格結構:**
  - 圍欄內的表、標題出現兩次、標題尾端空白或全形空白、表頭欄名有空白或粗體、只有表頭、`:---:` 分隔列、格內 `\|`、全形空白格、3 萬字超長格、4 格列、缺尾端管線、行首縮排 4 格,都得到合理結果,沒有崩潰。
  - 分隔列 `|--|--|--|` 與 `|-|-|-|` 被擋(GFM 其實合法),但訊息已講「像 --- 」,與預期值表一致,不另標。
- **出處格內容:**
  - 網址:`https://`、`https://localhost`、含空白網址、`https://a..b`、`http://[::1]`、`https://:80` 都擋。
  - 使用者原話:閏年 2028-02-29 過、2026-02-29 擋;2026-13-01、2026-11-00、0000-01-01 擋;全形與阿拉伯數字日期擋。
  - 節點連結:`[[節點|別名]]`、`[[節點#標題]]`、`[[ 節點 ]]` 都放行;`[[|x]]`、`[[#x]]`、不存在節點擋。
- **反引號路徑:** `..`、絕對路徑、NUL、3000 層路徑、反斜線、`.`、`docs` 目錄都擋;`./x` 與帶 `:行號` 放行。
- **計劃檔本身:**
  - 檔名含空白、Projects 子目錄、`type: note` 的 `_計劃.md`、`_調研.md` 的判定行為正確。
  - 非 UTF-8 計劃在規格閘印「讀不成文字」並擋。

總結:最嚴重是出處反引號路徑只靠工作目錄判存在,會因大小寫與未追蹤檔造成本機過、CI 或讀者查不到,會擋 1 條(F1);其餘 3 條為 minor。
