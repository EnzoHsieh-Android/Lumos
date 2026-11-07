severity: major

核對上一輪(第四輪正確性席)的三條:
- **F1(子目錄專案路徑基準)已修好。** 我用 monorepo 的 `mono/app` 當專案根跑 `_wt_changed_nofilter`,涵蓋乾淨的樹、大小不變內容改、改名、刪除、未追蹤、`paths` 過濾。結果跟在 repo 根跑一致,路徑從 repo 根算起,不再回 None。
- **F2(檔名結尾 CR)已修好。** 結尾 CR 的檔被當 `M`,其他檔照查。
- **F3(含換行檔名)已修好。** `_impact_wt_nofilter` 對 `src/nl\nx.kt` 退回只用路徑,其餘檔照算。
- 我另外帶 16 種怪檔名(空白、tab、前後空白、引號、反斜線、`@{1}`、`-` 開頭、`^`、`~` 等)跑 `_impact_wt_nofilter`,查詢文字全對。
- `-k r4wt` 這 26 項斷言我跑過,全過。

以下是新問題。

## F1 工作樹上缺檔但索引有的檔被一律報成刪除或改過,跟 `git status` 不同(sparse-checkout、skip-worktree)
- 輸入:
  - 例一:`git sparse-checkout set app`(`lib/L.kt` 在索引、被排除、磁碟上不存在)。
  - 例二:`git update-index --skip-worktree local.kt` 後改了 `local.kt`。
- 實際:
  - 例一:`_wt_changed_nofilter` 回 `[(' ', 'D', 'lib/L.kt', None)]`。
  - 例二:回 `[(' ', 'M', 'local.kt', None)]`。
- 預期:兩例的 `git status --porcelain` 都是空(我實跑確認)。docstring 寫「狀態碼同 git status --porcelain」。
- 影響:
  - sparse-checkout 的 monorepo 裡,圈外每支碼檔都被當「已刪除的程式碼」。
  - 收工點名鉤子的 `_entry_is_code` 對刪除檔只看副檔名,所以每個有寫檔的 session 會被擋一次,清單列出大量不存在的檔。
  - 影響分析的候選也跟著暴增,可能拖垮時間預算而靜默失效。
- 作者沒看到的原因:前幾輪的取捨只談過濾器與時間戳,沒談索引旗標。
- 修法:`ls-files -s -t -z`(或 `-v`)把 `S`(skip-worktree)與小寫(assume-unchanged)的條目整支略過。`-t` 我試過,輸出是 `S 100644 oid 0\tpath`。
- 這不是這輪新增的洞,是這個函式一開始就有的。但它正是鏡頭 3 問的「關掉過濾器後 status 結果有沒有變」,第四輪報告也沒涵蓋。
- 引句:「用了真過濾器的專案(LFS、autocrlf)會多報幾支(工作樹原樣跟索引裡轉過的不同),方向是多查不漏查。」
- file: `scripts/lumos:40095`(`_wt_changed_nofilter`)
- file: `scripts/hooks/claude/check-graph-sync.py:345`(逐字複本)
severity: major
- blocking: 是

## F2 影響分析宣稱 `--repo` 可以是子目錄,但入口一律拒收子目錄,補丁只在直接呼叫函式時才通
- 輸入:`lumos impact --diff HEAD --sync-check --worktree-nofilter --json --repo <monorepo>/mono/app`(收工點名鉤子實際用的呼叫形狀)。
- 實際:印「擋下:找不到 git 專案,用 --repo 指定」,rc 2。
- 原因:`cmd_impact_diff` 開頭的 `(repo_root / ".git").exists()` 檢查先把子目錄擋掉,到不了被修過的 `_impact_wt_nofilter`。
- 預期:跟函式註解和計劃說的一樣,子目錄也能算。
- 為什麼沒被測試抓到:`t_r4wt_monorepo_subdir` 直接呼叫 `m._impact_wt_nofilter(sub)`,沒走命令入口。
- 影響:子目錄當專案根時,收工的「相關筆記還沒動」點名整個靜默沒資料。這是舊行為沒退步,只是這輪的修補沒真的生效、文件與測試卻宣稱修好。
- 引句:「路徑從 repo 根算起,--repo 可以是子目錄」
- file: `scripts/lumos:67505`(`cmd_impact_diff` 的 `.git` 存在性檢查)
severity: minor
- blocking: 否

沒找到問題的部分:
- `_impact_line_delta`:行序不保留是設計取捨。`+++`/`---` 開頭的行被濾掉,跟原本 `git diff` 那條一樣。
- 被刪檔的 `#!` 判定:可正確取 HEAD 那一版,實測 `governance/code-loop/gone` 判成程式碼、`gone2` 判成非程式碼。
- 超過 1MB 的檔退回只用路徑。
- `_lens_git` 沒被這輪改到:不傳 `data` 的既有呼叫端行為不變,鏡頭 4 沒新問題。
- 五支鉤子的 `_trusted_lumos` 拒絕相對路徑:讀碼確認,主程式的 `_py_which` 本來就是同一規則。
- `_lint_wt_toplevel`:我在乾淨 monorepo 對 `--repo` 子目錄與 repo 根各跑一次 `lint-new --worktree --json`,判定一致。有宣告檔的端到端情境只靠作者的測試,我沒另跑。

總結:最嚴重是 F1(sparse-checkout 或 skip-worktree 下,找改動的結果跟 `git status` 不同,收工鉤子會誤擋且列出大量不存在的刪除檔),會擋 1 條。

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet/` 的實驗檔我已刪完,該目錄也已移除。我沒修改 repo。
