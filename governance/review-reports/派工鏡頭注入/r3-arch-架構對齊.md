# r3 架構對齊審查——派工鏡頭注入

被審材料(凍結審材):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/派工鏡頭注入-r3.md`
第 2→3 輪差異:`governance/review-reports/派工鏡頭注入/r3-delta.diff`
對照鄰居:`scripts/hooks/claude/impact-hook.py`、`scripts/lumos` 既有 git 呼叫慣例(`merge-base`/`rev-parse`/`ls-tree`/`core.quotePath`)、既有找圖譜根函式(`find_vault`/`_vault_in`)、既有合約行判定函式(`INVARIANT_RE`/`CHECKPOINT_RE`/`IRREVERSIBLE_RE`/`extract_contracts`)、`scripts/test_lumos.py`。

判定範圍只問「跟既有做法一不一樣」,不判 bug、不評風格;★只看第 2→3 版差異的 + 行★。

---

## 前輪 2 條驗收

r2 架構對齊席(`r2-arch-架構對齊.md`)判了 f5(`--repo` 只用 payload cwd,略過 `CLAUDE_PROJECT_DIR`,major)、f6(退役兩階段全記在同一個常數名下,minor)。逐條核對 r3 是否真改到:

- **f5(repo 解析)**:設計 §1 已改成「`--repo` 比照四支鄰居:先 `CLAUDE_PROJECT_DIR` 環境變數、再 hook payload 的 `cwd`」(審材 82 行)。跟鄰居 `impact-hook.py` 的實際寫法(`repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")`,file: `scripts/hooks/claude/impact-hook.py:436`)完全同構——不是文字改了但行為沒變,是真的把 `CLAUDE_PROJECT_DIR` 放回鏈裡當第一優先。✅ 真改到。
- **f6(退役常數)**:實務隱患的回滾段已改成「沿既有 hook 退役慣例兩階段:先進 `_RETIRED_STUB_CLAUDE_HOOKS`(留空殼),下一版才進 `_RETIRED_CLAUDE_HOOKS`(刪檔)——是兩個不同常數(r2 架構席:首版寫成一個,照字面會加錯)」(審材 129 行),對到 `scripts/lumos:11033-11034` 兩個確實分開的元組(`_RETIRED_STUB_CLAUDE_HOOKS = ("verification-rot-check.py",)`、`_RETIRED_CLAUDE_HOOKS = ("code-loop-guard.py",)`)。✅ 真改到,而且點名了自己上一版的錯誤,不是含糊帶過。

兩條都真改到,無一條是換句話說但骨子沒動。

## 問一:分層與依賴方向

新段落沒有動到呼叫鏈的層級本身:hook 仍是 `subprocess` 呼叫 `git`/`lumos`,沒有 `import scripts.lumos` 之類跨模組直呼,`--repo` 解析鏈(見〈前輪驗收〉f5)已對齊四支鄰居。這條本身沒有新的不對齊。

★但★ r3 新增的四段判定邏輯(base 存在性驗證、主線可達性、圖譜根路徑前綴、合約行擷取)把原本該由 `scripts/lumos` 承接的業務判斷,搬進 hook 腳本裡各自重新發明一套——這不是「該不該呼叫 git」的分層問題(呼叫 git 本身鄰居早就這樣做,見問三),而是「這件事 `scripts/lumos` 已經有標準答案,hook 卻不透過它、自己另算一次,而且算出來的規則還不一樣」。四個實例逐一列在問三(f7–f10),這裡先點出共同形狀:hook 層本該是薄封裝(組 CLI 參數、格式化輸出),现在扛了四段跟核心模組定義不一致的領域邏輯。

## 問二:命名與錯誤處理

- 快取檔名機制(審材 88 行:「兩個 sha 都必須通過 `^[0-9a-f]{40}$` 才能當檔名……檔名=三者串起來的 sha256」)跟 `scripts/lumos` 既有的「多識別碼字串相接、`hashlib.sha256(...).hexdigest()`」慣例同構(file: `scripts/lumos:4599-4600`,`h = int(hashlib.sha256(f"{loop_id}:{rid}:{toks}".encode("utf-8")).hexdigest(), 16)`)。這條命名/實作風格對齊,不算問題。
- 錯誤處理(算不出/超時/base 解析不到 → 一律放行、預設靜默)延續既有「技術性失敗純靜默」慣例(前兩輪已核過),r3 新增的 base 驗證失敗(rc≠0 或非 40 碼)、圖譜根有多個時的失敗路徑,都沿用同一種「→放行」收斂寫法,格式一致。
- 沒有找到新的命名/錯誤處理不一致——r3 這輪新增的四段判定邏輯,問題不在「命名法或錯誤處理跟鄰居不同款」,而在問三要談的「同一件事鄰居/`scripts/lumos` 已有算法,這裡另開一條」,故歸入問三計分,這裡不重複計。

## 問三:第二種做法

逐項核對審材點名要查的五種判定,`scripts/lumos` 是否已有同功能 helper:

- **base 驗證**(審材 83 行:「`git rev-parse --verify <base>^{commit}` rc≠0 或輸出不是 40 位十六進位→放行」):`scripts/lumos` 已有 `_git_commit_exists(repo_root, sha)`(file: `scripts/lumos:2971-2978`)做同一件事——`git cat-file -e sha^{commit}`,回傳 rc==0 與否。r3 沒有呼叫它,改用 `rev-parse --verify` 另開一套(外加一個既有函式沒做的「必須是 40 碼」檢查)。同一個問題(「這個 sha 是不是有效 commit」)在同一個 repo 裡現在會有兩套判法。見 f10,major。
- **主線判定**(審材 83 行:「主線 tip=`refs/remotes/origin/HEAD` 解析到的分支,沒有就本地 `main`/`master`」):`scripts/lumos` 唯一現成的「主線是哪個」判法在 `_codeloop_guard_verdict`(file: `scripts/lumos:16748-16760`),做法是直接依序試本地分支 `("main", "master")`(`for base_branch in ("main", "master"): git merge-base HEAD base_branch`),完全不查 `refs/remotes/origin/HEAD`。全庫 grep `origin/HEAD`、`_default_branch` 都是 0 命中——`refs/remotes/origin/HEAD` 優先這個判法在 `scripts/lumos` 裡沒有先例,是 r3 自己發明的第三種(不是鄰居兩種寫法擇一)。見 f7,major。
- **合約行判定**(審材 85 行:「base 那版節點的合約行(`git show` 出來的正文裡以 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 開頭的行)」):`scripts/lumos` 的 `INVARIANT_RE`/`CHECKPOINT_RE`/`IRREVERSIBLE_RE`(file: `scripts/lumos:2405`、`2776-2777`)與 `extract_contracts`(file: `scripts/lumos:2409-2419`)刻意只認 **KEY: 行前綴**,函式上方註解逐字寫著「錨定 KEY 行起始 → 排除「散文中提到標記」的誤報(如方法論文件講解標記用法)」(file: `scripts/lumos:2403-2404`)。r3 的「正文裡以 ★INVARIANT★ 開頭的行」是直接掃整段正文任何一行,這正是既有函式刻意設計來排除的誤報形態——一篇解釋這三個標記怎麼用的方法論筆記,正文裡示範句「★INVARIANT★ 範例文字」會被當成真合約行注入進派工詞。不是選了鄰居沒有的第三種寫法這麼單純,是重新踩進鄰居當年已經踩過、寫進註解警告過的坑。見 f8,major(四條裡風險最高的一條)。
- **圖譜根判定**(審材 84 行:「圖譜根沿 lumos 既有慣例找 `docs/*-knowledge/`(不只一個→放行)」):`scripts/lumos` 現成的 `_vault_in`/`find_vault`(file: `scripts/lumos:11375-11400`)在 `docs/` 下有多個 `*-knowledge` 目錄時,行為是 `sorted(docs.iterdir())` 後**靜默取第一個**(file: `scripts/lumos:11380-11382`),從來不會「不只一個就放行/失敗」。設計文字自稱「沿 lumos 既有慣例」,但那個「既有慣例」實際上不存在「多個就放行」這種分支——r3 描述的既有慣例是它自己想像出來的一種,跟 `find_vault` 實際行為不同。見 f9,major。
- **快取檔名**:如問二所述,`sha256(三個識別碼相接)` 這個組法跟 `scripts/lumos:4599-4600` 的既有形狀一致,沒有找到「已有 helper 卻另開一套」的情形,不算第二種做法。

四個判定裡,base 驗證、主線判定、合約行判定、圖譜根判定全部都在 `scripts/lumos` 有現成、且行為不同的既有做法,r3 一概沒有呼叫它們,四段全部自己重寫一遍規則。

---

### f7

主線判定改用「`refs/remotes/origin/HEAD` 優先、沒有才退回本地 `main`/`master`」,但 `scripts/lumos` 目前唯一的主線判定實作(`_codeloop_guard_verdict`)只試本地 `("main", "master")`,從不查 `origin/HEAD`;全庫也沒有 `_default_branch` 或 `origin/HEAD` 判斷邏輯的先例。這是自己發明的第三種主線判法,不是鄰居既有兩種寫法之一。

severity: major
blocking: 是
引句:「主線 tip=`refs/remotes/origin/HEAD` 解析到的分支,沒有就本地 `main`/`master`」
file: 審材 `派工鏡頭注入-r3.md:83`
file: `scripts/lumos:16748-16760`(既有主線判法:`for base_branch in ("main", "master")`)

### f8

合約行判定改成掃「正文裡以 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 開頭的行」,但 `scripts/lumos` 的 `INVARIANT_RE`/`CHECKPOINT_RE`/`IRREVERSIBLE_RE` 與 `extract_contracts` 刻意只認 `summary` 區塊裡 `KEY:` 行前綴的標記,函式上方註解明寫這是為了「排除散文中提到標記的誤報(如方法論文件講解標記用法)」。r3 的正文任意行掃法會重新踩進這個既有設計特意避開的誤報坑——一篇講解標記用法的方法論筆記,示範句就會被誤判成真合約行貼進派工詞。

severity: major
blocking: 是
引句:「base 那版節點的合約行(`git show` 出來的正文裡以 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 開頭的行)」
file: 審材 `派工鏡頭注入-r3.md:85`
file: `scripts/lumos:2403-2405`(註解「錨定 KEY 行起始 → 排除「散文中提到標記」的誤報」+ `INVARIANT_RE`)
file: `scripts/lumos:2409-2419`(`extract_contracts`,docstring「只認 KEY 行前綴……散文中提及不算」)
file: `scripts/lumos:2776-2777`(`CHECKPOINT_RE`/`IRREVERSIBLE_RE`,同一錨定形式)

### f9

圖譜根判定寫「沿 lumos 既有慣例找 `docs/*-knowledge/`(不只一個→放行)」,但 `scripts/lumos` 現成的 `_vault_in`/`find_vault` 在多個 `docs/*-knowledge` 目錄時是 `sorted()` 後靜默取第一個,沒有「多個就放行/失敗」這種行為。設計自稱在沿用既有慣例,但這個「既有慣例」跟真正的既有函式行為不一致,等於用一個不存在的既有慣例包裝了一個新規則。

severity: major
blocking: 是
引句:「圖譜根沿 lumos 既有慣例找 `docs/*-knowledge/`(不只一個→放行)」
file: 審材 `派工鏡頭注入-r3.md:84`
file: `scripts/lumos:11375-11400`(`_vault_in`/`find_vault`,多個時 `sorted(docs.iterdir())` 取第一個)

### f10

base 存在性驗證改用 `git rev-parse --verify <base>^{commit}`,但 `scripts/lumos` 已有 `_git_commit_exists(repo_root, sha)` 做同一件事(`git cat-file -e sha^{commit}`)。同一個「這個 sha 是不是有效 commit」的判斷,現在 repo 裡會有兩套實作互不參照。

severity: major
blocking: 是
引句:「`git rev-parse --verify <base>^{commit}` rc≠0 或輸出不是 40 位十六進位→放行」
file: 審材 `派工鏡頭注入-r3.md:83`
file: `scripts/lumos:2971-2978`(`_git_commit_exists`,同功能既有 helper)

---

## 結論

不對齊共 4 條,其中 major 4 條。
