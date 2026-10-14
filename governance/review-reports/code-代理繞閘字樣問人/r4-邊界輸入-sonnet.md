severity: major

## 範圍與方法

我用 `SourceFileLoader` 載入修後版 `bypass-ask-hook.py`(`465736e9`,檔案內容與工作目錄 `9981c0e5` 相同,後者只多一個派工材料提交),跑了約 350 條邊界輸入。修前版取自 `9b8ce146`,同時載入對照。每條都同時看 `prefilter`、新版 `bypass_reasons`、舊版 `bypass_reasons`。cwd 分兩組:真 repo,以及我在 `/tmp/lumos-seat-work/…/邊界輸入-sonnet/w/exp` 開的拋棄式 repo。

歸因統一用「有證據的修復回歸」或「有證據的原有漏查」,查證命令是同一批腳本(`h.py`、`t1.py` 到 `t7.py`)在兩版各跑一次。

## Findings

### 1. `$'\c'` 的結尾單引號被吞,引號狀態錯位,整條指令後半段都不再被分類

severity: major
blocking: 是

引句:「`if ch == "c" and k + 1 < len(cmd):`」

`_ansi_escape` 對 `\c` 無條件吃掉下一個字元。bash 5.3 實測 `printf '[%s]\n' a$'\c' -n` 印出 `[a\c]` 和 `[-n]`:`$'\c'` 在結尾單引號就收,`\c` 後面沒有可轉的字元,按字面留下,`-n` 是獨立的第二個詞。

掛鉤把結尾的 `'` 當成 `\c` 的運算元吞掉,ANSI 字串一路開到指令尾,後面的 `-n`、`;`、換行全被遮罩成字串內容。

以下四種寫法,修後都回 `[]`(放行),修前全是命中:
- `git commit $'\c' -n`:修前 `['commit-n']`,修後 `[]`
- `git push $'\c' --no-verify`:修前 `['no-verify']`,修後 `[]`
- `echo $'\c'; git push --no-verify`:修前 `['no-verify']`,修後 `[]`
- `echo $'\c'` 換行 `git push --no-verify`:修前 `['no-verify']`,修後 `[]`

連 `git commit -m $'x\c' -n` 也漏。

`echo $'\c'` 重複 1500 次(15000 字),修後回 `['literal']`,這是 shlex 報「沒有結尾引號」的間接證據。

應該是:`\c` 後面是 `'`(或已到字串尾)時不消耗它,`\c` 按字面留下。
歸因:有證據的修復回歸。`\cX` 是這輪新加的解碼。
附帶:`\c` 現在是「吞掉結尾引號就讓後面全被遮罩」的最小觸發器,修補時順便讓 `_ansi_decode` 不要跨過未配對的 `'` 而吃掉整條指令。

### 2. 程序替換 `<(` 和 `>(` 被當成導向,裡面的 git 指令被跳過

severity: minor
blocking: 否

引句:「`k = min(t.index(c) for c in "<>" if c in t)   # `)>`、`;>`:前面是分隔、後面是導向`」

「黏著標點」的新分支遇到只含標點的詞(例如 `<(`),就在第一個 `<` 或 `>` 切開,後半變成 `_Redir`。`_strip_redirects` 接著把 `<(` 後面的下一個詞(`git`)當導向目標丟掉,掛鉤就找不到 git 指令了。

- `cat <(git commit -n)`:修前 `['commit-n']`,修後 `[]`
- `tee >(git push --no-verify)`:修前 `['no-verify']`,修後 `[]`
- `diff <(echo) <(git commit -n)`:修前 `['commit-n']`,修後 `[]`

應該是:`<(` 和 `>(` 當成開子殼層的分隔,不是導向。
歸因:有證據的修復回歸。

另有一個原有漏查,不是這輪造成的:`git push <(echo x) --no-verify` 修前修後都是 `[]`。原因是 `)` 把段切斷,`--no-verify` 落在沒有 git 的新段。〈範圍〉沒有列程序替換。

### 3. 「if 或 for 本體裡的 cd」一律當作會執行,條件為假或迴圈零次時誤給拋棄式豁免

severity: minor
blocking: 否

引句:「`self.seg_conditional = any(w in ("if", "elif", "while", "until", "!") for w in seg[:i])`」

只有條件那一行的 cd 被當成條件式。`then` 或 `do` 本體裡的 cd 被當成必定執行。在真 repo 的 cwd 下:

- `if false; then cd E; fi; git commit -n`:修後 `[]`,修前 `[]`。真實是 cd 沒跑,提交落在真 repo。
- `for i in 1; do cd E; done; git commit -n` 和 `case x in x) cd E;; esac; …` 同樣放行。這兩條 cd 確實會跑,所以放行本身不算錯。零次迭代的 `for` 或不匹配的 `case` 才是錯。

E 是判斷當下存在的暫存 repo。常見的 `if [ -d E ]; then cd E; fi; git commit -n`,條件為假時會漏。方向上符合 d2「寧可漏問」,所以只列 minor。
應該是:`then`、`else`、`do` 本體裡的 cd 也標成條件式,和 `&&`、`||` 的處理一致。
歸因:有證據的原有漏查(修前修後同為 `[]`)。

### 4. 拋棄式 repo 裡,字串或參數中的 `GIT_DIR=` 字樣誤把豁免取消

severity: minor
blocking: 否

引句:「`if any(_GITDIR_ASSIGN.match(w) for w in seg):`」

`_note_markers` 掃整段所有詞,包含 `echo`、`grep`、`-m` 的引數。cwd 是拋棄式 repo 時,以下都回 `['commit-n']`,預期放行:

- `echo "GIT_DIR=x"; git commit -n`
- `grep -rn GIT_DIR=x .; git commit -n`
- `git commit -m "GIT_DIR=x" -n`
- `echo $'GIT_DIR=x'; …`
- `echo $x GIT_WORK_TREE=x; …`

heredoc 內文和註解裡的字樣沒問題,前處理已剝掉。因為只在拋棄式 repo 才多問,算 minor。
應該是:只認段首的前綴賦值,以及 `env` 或 `export` 後面的賦值。
歸因:有證據的原有漏查(修前修後同為 `['commit-n']`)。

## 三個必答問題

**① 原問題的修復效果有何行為證據。** 以下各案例修前修後的結果相反,都是修好的證據:

| 輸入 | 修前 | 修後 |
|---|---|---|
| `git commit -m 1 >x -n`(`-m` 的值是 1,後面是獨立 `-n`) | `[]` | `['commit-n']` |
| `git config {fd}>x --unset core.hooksPath` | `[]` | `['config-hookspath']` |
| `git commit -$'\156'` | `[]` | `['commit-n']` |
| `git commit -$'\u006e'` | `[]` | `['commit-n']` |
| `git commit -$'\U0000006e'` | `[]` | `['commit-n']` |
| `git commit $"-n"` | `[]` | `['commit-n']` |
| `git push $'\55\55no-verify'` | `[]` | `['no-verify']` |
| `git commit -$'\cn'n`(此例解出控制字元,見下) | `[]` | `['commit-n']` |
| `git commit -$'\1560'`(此例 git 實際會報錯,見下) | `[]` | `['commit-n']` |
| `if cd E; then git commit -n; fi`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `! cd E; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `{ cd E; } \| cat; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |
| `(cd E)>x; git commit -n`(cwd 為真 repo) | `[]` | `['commit-n']` |

倒數第 7、6 兩行(`\cn`、`\1560`)和 `\0n`、`\777n` 屬於解碼過度,見下一節「預篩與分類器」。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立。** 大致成立,但有 finding 1 和 2 的兩個回歸。

下面這些都過關:
- 檔案代號 `2>`、`10>`、`{fd}>`、`{fd}<&-`、`2>&1`、`3<>`、`03>`、`>|`、`&>>`、`>&-`。
- 導向放最前面、夾在 `git -C`、`git -c` 之間、夾在 `-C R` 之後。
- 引號、`$'…'`、`\>` 裡的 `2>`(不會被當成導向)。
- `cd` 後接導向。
- `cd E && cd R`、`||`、換行、`;` 混合鏈。
- `(…)` 子殼層,包含 `)>`、`)2>`、`;>`、`|&`、`}>` 黏著。
- `{ …; } | cat` 和 `{ …; } &`。
- `-m 1>x -n`、`-F 2>x -n`、`-C 5>x -n`:這幾條 `-n` 是 `-m` 的值,放行是對的。我一開始的預期寫反了。
- GIT_DIR 一族出現在 `export`、`declare -x`、`typeset -x`、前綴賦值、`--git-dir`、`--work-tree` 時,豁免都取消。
- heredoc 內文的 `GIT_DIR=`,不影響豁免。
- `env -u GIT_DIR`:修後視為不取消豁免,方向合理。
- 前綴 `LUMOS_SKIP_*` 夾在 `2>x`、`{fd}>x` 前後。
- `GIT_CONFIG_KEY_n` 前綴。
- `-c core.hooksPath` 夾在 `2>x`、`-C .` 周圍。
- `git config` 讀值加導向(`core.hooksPath 2>&1`)放行,寫值加導向命中。

**③ 新發現的同一案例在修前、修後各是什麼結果。** 見 finding 1 和 2 的清單。finding 3 和 4 兩版相同。

## 預篩與分類器是否一致

預篩放行時分類器根本不會被叫,所以先看有沒有「預篩放行、分類器卻會命中」的實際繞過。

我找到的預篩放行但分類器命中的案例:
- `git commit -$'\0n'`
- `git commit -$'\777n'`
- `git commit -$'\cn'n`
- `git commit -$'\1560'`
- `git commit -$'a<換行>b'n`
- `git commit $"-$'n'"`
- `git commit -$'$"n"'`

這些在 bash 裡都不會變成真的 `-n`:
- `\0` 讓 bash 在 NUL 處截斷字串。
- `\777` 在 bash 是 0xFF 位元組。
- `\cn` 是控制字元。
- `\1560` 變成 `-n0`,git 會報錯。
- 換行字串、雙引號裡的 `$'` 都是字面字元。

所以這些是分類器解碼過度,預篩剛好擋下,對結果沒影響。我沒有找到「預篩放行而 bash 真會執行 `-n`」的案例。

## 效能

2 萬字內的最壞形狀(`2>x ` 重複、`{fd}>x ` 重複、`()>`、`;>`、`a&>b`、未閉合 `$'` 九千次、`$"` 九千次)全在 40ms 內,預篩在 12ms 內。

## 固定席節點逐條判

- **Issues/code-loop守衛main-direct盲區、Systems/lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態、guard-kill、pitfalls-code-loop、reversibility-governance-ledger**:不影響。它們牽連的檔(`scripts/lumos`、`merge-claude-settings.py`、`test_lumos.py`)和那幾條 INVARIANT(search 預設排除、re-inject byte-equal、處置閘第五步、還原翻紅釘、guard kill rc 與 JSON)是 CLI 別的路徑,跟本席測的 `bypass-ask-hook.py` 的輸入處理無關。我沒有跑那幾條的綁定測試,結論只是從主題與牽連檔推出,不是實測。
- **超出上限、只列名的節點**:未逐篇讀,也不影響。
- 與本席有關的是 `_hookevent.py` 的修剪邏輯(存活事件)。我沒有測它,屬未驗範圍。

## 未驗範圍

- `_hookevent.py`:修剪與殘檔清理。
- `scripts/lumos` 和 `merge-claude-settings.py` 的註冊與安裝。
- `test_lumos.py` 的新測試是否真能翻紅。
- 真正的 git 子程序逾時與 `MAX_GIT_CALLS` 路徑。

## 最後一行

總結:最嚴重等級為 major,blocking 共 1 條(finding 1);另有 3 條 minor(finding 2、3、4),非 blocking。

臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/` 留給編排者刪,裡面有我複製的 `old.py`、`new.py`、`_hookevent.py` 和一個測試用的 `w/exp`。我一度把三個檔誤複製到主工作目錄 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search`,已刪掉,`git status` 現在只剩原有的 `docs/.governance-log.jsonl`。repo 本體(`-bypass`)沒有被我改動。
