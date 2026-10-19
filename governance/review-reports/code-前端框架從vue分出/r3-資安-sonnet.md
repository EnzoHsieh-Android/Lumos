severity: minor

審查範圍:r3-snapshot.patch 全文,以及 r3-repair-lumos、r3-repair-tests、r3-repair-docs 三份修補差異。`/tmp/lumos_r3.py` 是我另外取出的修後 `scripts/lumos`,用來對照呼叫端。沒有 blocker 或 major。只有 3 條 minor,都不阻擋。

## 發現

**1. Kotlin 平台判定改成只看「工作樹裡還存在」的檔,diff 範圍的 head 不是已檢出版本時會少問 Android 題(類別③)**

severity: minor
blocking: 否
引句:「kts = [f for f in files if Path(f).suffix.lower() == ".kt" and not _PITFALL_DIFF_TEST_PAT.search(f)」
- 攻擊路徑:
  - 誰:照常操作的 AI 或使用者。
  - 從哪:`lumos pitfalls --diff <base>..<sha>`,而 `<sha>` 不是目前檢出的 HEAD。審查席派工用完整 sha 範圍,這種情形會出現。
  - 送什麼:範圍裡有新增的 Android `.kt`(檔案不在目前工作樹),加上一支工作樹有、且建置檔判成 Spring 的 `.kt`。
  - 拿到什麼:新加的 `(Path(repo_root) / f).exists()` 把「工作樹沒有」的檔直接丟出 `kts`。剩下的檔全判成伺服端,`_stack_platform_excluded` 就拿掉 `android_only` 的題。
- 原本讀不到的檔會判成「判不出」,Android 題照附;現在這個方向反了。這是 r2 針對「刪檔」所做的修補,同時把「diff 有、工作樹沒有」的檔也一併丟掉。
- 判定本來就讀工作樹而不是 diff 的 head 版。修補把這個落差從「判不出」放大成「少問題」。
- 呼叫端在 `scripts/lumos`(修後版)的 `_stack_platform_excluded(list(changed_lines), repo_root)` 一行,`changed_lines` 是 diff 來的。
- file: `scripts/lumos:30437`

**2. `_review_roles` 改成先問大小,但 `_nodehome_cat_sizes` 沒有擋路徑裡的換行(推論,範圍外邊界)**

severity: minor
blocking: 否
引句:「sizes = _nodehome_cat_sizes(root, want, timeout=left)」
- 攻擊路徑:寫不出完整四件,只能算推論。
  - 讀內容的 `_nodehome_cat_blobs` 遇到含 `\n` 的 spec 會整批回 None。
  - 新增的大小查詢走 `cat-file --batch-check`,輸入也是用換行拼接,卻沒有同樣的擋。
  - 帶換行的檔名會讓輸出行數多一行,後面所有 spec 的 `sizes[i]` 整體錯位一格。
  - 錯位只影響單檔上限和 `("" if n is not None else None)` 這個「在但讀不了」判斷。
  - 內容本身仍由逐筆對齊的 `--batch` 讀取,沒有跨檔串內容。
- 實際後果是上限判斷在這種罕見檔名下不準,沒有讀寫越界,所以只標縱深防禦。
- file: `scripts/lumos:33444`(`_nodehome_cat_sizes` 內沒有 `"\n" in s_` 的檢查)

**3. 「跑過證據」樣式的 `Tests:` 分支仍不錨行首(推論)**

severity: minor
blocking: 否
引句:「"re": r"(?:Tests:|(?:^|(?<=\n))[^\S\n]*(?:\x1b\[[0-9;]*m[^\S\n]*)*Tests\b)」
- 攻擊路徑:寫不出非刻意的情境,只能算推論。
  - r2 只把 `Tests\b` 這一支錨到行首。
  - 前面的 `Tests:` 分支仍可出現在行中任何位置。
  - 若被測程式在 `-t` 對不到測試的那次執行裡,於模組載入或 `beforeAll` 印出含「Tests: N passed」的字樣,「沒跑」會被判成「有跑過」。
- 要同時碰到「名字打錯讓 `-t` 對不到」和「程式自己印出同樣字樣」。第二個條件不是照平常操作會發生的,所以只標縱深防禦。
- file: `scripts/lumos:54521`

## 逐類檢查(已看,無)

### ① 提示注入
已看,無。
- 新增的 react-idioms skill、`_STACK_QUESTION_SPECS` 的 react 題組、`_init_lint_hint`、`_linter_config_hits` 印出的只有程式內建常數字串。
- 範本裡的 linter 命令是固定字面量,沒有拼進筆記、檔名或分支名等外來自由文字。

### ② 讀寫與執行越界
已看,無。
- `_worktree_text` 的快取鍵含 repo 絕對路徑,A repo 的判定不會被 B repo 沿用。
- `_KT_BUILD_VERDICT_CACHE` 以建置檔文字為鍵,是純函式,跨 repo 也安全。
- 角色路的 git 呼叫參數是 `ref:path` 形式,檔名不會被當成選項。
- `{method}` 經 `shlex.quote` 並先驗方法名;`ESLINT_USE_FLAT_CONFIG=false npx eslint` 只印給使用者貼進 `.lumos/lint.json`,不是 lumos 自己執行。
- 新增內容裡沒有密鑰、信箱或可被環境變數覆蓋的下載來源。
- 測試新增的 `_sp.run` 都是固定參數,在暫存目錄跑 git 或 `GRAPHCTL`。
- `_worktree_text` 會跟著符號連結讀檔,但內容只拿去比對正則,不外流。

### ③ 非刻意守衛繞過
- 測試檔判法收窄:`Test.tsx`、`test.py` 改回算正式檔,只會多問題,方向安全。
- `tests?/` 新增認 repo 根的 `tests/`,與舊行為一致。
- Spring 判法收窄(只認外掛宣告,不認依賴座標):方向是「判不出」→ 照附 Android 題,安全。
- 超限停住:`blobs` 對超限檔改為 `""`,停在該層判「判不出」,不再往上找父層而誤判成後端,是修對了。
- 此外無符合 `LUMOS_SKIP_*` 或殘留環境變數的新路徑。

最嚴重 severity:minor,blocking 共 0 條。
