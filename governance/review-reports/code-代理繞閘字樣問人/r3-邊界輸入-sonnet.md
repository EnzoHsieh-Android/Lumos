severity: major

我載入修後(9b8ce146)與修前(4e87b682)的 `bypass-ask-hook.py`,跑了約 300 條邊界輸入。能對照的都兩版並排,結果有兩層:
- `bypass_reasons`:直接比兩版的輸出。
- 掛鉤入口 `entry()`:餵 JSON 事件,看有沒有印出 `ask`。
- 實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/`(`t1.py` 到 `t11.py`)。

**發現**

1. 預篩擋在分類器前面,r3 補的解碼能力有一整批到不了。
引句:「low = re.sub(r"['\"\\]", "", _command_text(raw)).lower()」
severity: major
blocking: 是
- 預篩只拿掉引號和反斜線,不解 `$'…'`,也不接續行。分類器已經認得的寫法,在入口就被擋掉,整條放行。
- 重現(`entry()` 對照 `bypass_reasons`):

| 輸入 | `bypass_reasons` | `entry()` |
|---|---|---|
| `git commit -$'n'` | `['commit-n']` | 無輸出 |
| `git push --no-ve$'\x72'ify` | `['no-verify']` | 無輸出 |
| `git push $'\x2d\x2dno-verify'` | `['no-verify']` | 無輸出 |
| `git push --no-ver\<換行>ify` | `['no-verify']` | 無輸出 |
| `git commit -\<換行>n` | `['commit-n']` | 無輸出 |
| `git commit -a\<換行>n` | `['commit-n']` | 無輸出 |
| `git config core.hooks\<換行>Path x` | `['config-hookspath']` | 無輸出 |
| `LUMOS_SKIP\<換行>_X=1 git commit` | `['lumos-skip']` | 無輸出 |
| `git commit --no-$'verify'` | (未單獨查) | 無輸出 |

- 原因:反斜線被拿掉後換行還在,`--no-veri` 的字樣被換行切斷。
- 計劃 S1 明寫「續行切開長選項」「`$'…'` 之後或包住旗標」要問,而〈做法〉第 87 行舉的例子 `git commit -$'n'` 本身就是無聲放行。
- 同一批裡,`$'\055\055no-verify'`(八進位)、`\u002d`、`\c` 解碼器不認,`bypass_reasons` 本身就回 `[]`。
- 應該怎樣:預篩要用跟 `_Normalizer` 同一套前處理(至少接續行、解 `$'…'`)再比字樣。或者只要原文有 `$'`、反斜線加換行,就一律放進分類器。
- 歸因:有證據的原有漏查,修補不完整。
  - 修前 `bypass_reasons("git commit -$'n'")` 是 `[]`,修後分類器補上了,但入口擋住,效果為零。
  - 修前預篩連引號都沒剝。修後只補了引號和反斜線,沒補上面這兩類。
  - 兩版查證:`python3.14 t7.py`、`t8.py`、`t9.py`。

2. 大括號群組的 `cd` 不被當子殼層,誤給豁免。
引句:「elif changed and (p.endswith("&&") or p.endswith("||")):」
severity: minor
blocking: 否
- `{ cd /tmp/exist; } | cat; git commit -n`,cwd 在真 repo:兩版都回 `[]`。`{ cd X; } &` 同樣。
- 原因:`{` 只是關鍵字,沒有像 `(` 那樣推進 stack,管線判斷只看分隔符。
- 實際上管線或背景裡的群組跑在子殼層,`cd` 不會傳到後面,提交其實在真 repo,卻被豁免。
- 應該怎樣:`{ … }` 緊接管線或 `&` 時,把這段的 `cd` 還原。或者看到 `}` 後面接 `|` 或 `&` 就把目前目錄設為判不出。
- 歸因:有證據的原有漏查(兩版相同,非回歸)。

3. 條件式 `cd` 的第一個分支成功時,第二個 `cd` 根本不會執行,仍被當成已生效。
引句:「self.cond_pending = True     # 條件式 cd 之後緊接 &&:這條 && 鏈裡 cd 一定跑過」
severity: minor
blocking: 否
- `cd <真repo> || cd /tmp/x && git commit -n`:兩版都回 `[]`。`test -d R && cd R || cd /tmp/x && …` 同樣。
- 原因:`cd R` 成功時 `|| cd /tmp/x` 被跳過,提交跑在真 repo。程式把 `||` 後面、緊接 `&&` 的 `cd` 當作「一定跑過」。
- 反過來,`cd /tmp/x || cd <真repo> && …` 正確地問了。
- 應該怎樣:`||` 之後的 `cd` 一律設為判不出,或把前一個 `cd` 的目錄也納入,兩者都要是暫存才豁免。
- 歸因:有證據的原有漏查(`cond_pending` 是 r3 前就有的邏輯,兩版同結果)。

4. 括號後緊貼導向,括號被吃進詞裡,子殼層沒有還原。
引句:「if _is_sep(t):」
severity: minor
blocking: 否
- `(cd /tmp/x)>/dev/null; git commit -n`:兩版都回 `[]`。有空格 `) >/dev/null` 則正確回 `['commit-n']`。
- `(cd /tmp/x;git commit -n)>/dev/null; git commit -n` 也是 `[]`。
- 原因:shlex 把 `)>` 切成一個詞。`_is_sep` 不成立(含 `>`),`_is_redirect` 也不成立(含 `)`),於是成了普通詞,括號層沒被彈出。`)&>`、`;>` 同理。
- 應該怎樣:`_tokens` 切詞前先把括號、分號跟導向字元拆開,或在標點串裡逐字分類。
- 歸因:有證據的原有漏查(兩版都 `[]`)。

5. `{fd}>log` 形式的導向沒有被剝掉。
引句:「if w.isdigit() and k + 1 < len(words) and isinstance(words[k + 1], _Redir):」
severity: minor
blocking: 否
- `git {fd}>log commit -n` 回 `[]`。
- 原因:`{fd}` 被當成子指令名。
- 應該怎樣:在 `_strip_redirects` 一併剝掉 `^\{[A-Za-z_]\w*\}$` 且後面緊接導向的詞。
- 歸因:未判定,兩版都漏。

6. `GIT_DIR` 一族的判斷太寬,多問。
引句:「_GITDIR_NAME = re.compile(r"^(GIT_DIR|GIT_WORK_TREE|GIT_COMMON_DIR)(\+?=|$)")」
severity: minor
blocking: 否
- `cd <暫存repo> && echo "GIT_DIR=foo" && git commit -n`、`grep GIT_DIR f`、`git commit -n -m GIT_DIR` 都會多問。
- 修前這些是 `[]`,修後是 `['commit-n']`。
- 修前就有的 `GIT_DIR=/r git commit` 等本來就問。
- 這種誤問對照計劃「寧可多問」可以接受。heredoc 內的 `GIT_DIR` 被剝掉所以不影響,屬於範圍外。
- 應該怎樣:只在賦值形式 `NAME=`,或是前一個詞是 `export`/`declare`/`env`/`unset` 時才算,不用 `$` 比對單獨的詞。
- 歸因:有證據的修復造成的新多問,不是漏問,可接受。

**已驗、無問題**

重現檔都在 `t1.py` 到 `t11.py`。

- 導向寫法:`>|`、`<>`、`<<<`、`2>`、`&>>`、`>&-`、`>log git push --no-verify` 都問,兩版一致。
  - 夾在 git 全域選項之間:修前漏、修後問,如 `git >log push --no-verify`、`git -c a=b >log push …`。
  - 管線 `cd X 2>&1 | tee`、`cd X |& tee` 修後會問,是對的。
- 跳脫字元:`\\` 結尾、`\"` 在雙引號裡、單引號內的反斜線、`\$`、`\#` 結果都對。
  - 結尾孤立反斜線,修前走 `literal`,修後走結構判斷,也問。
- ANSI 在分類器層:
  - `\x` 後無十六進位數字、未閉合的 `$'`,都沒丟例外。
  - `$'a\nb'` 內含換行,結果對。
- 續行:單引號內不接、雙引號內接、註解內不誤接,都對。
  - heredoc 內,bash 實際會把 EOF 吃成續行,程式則多問,可接受。
- 條件式與管線 `cd`:
  - `if cd X; then …`、`while cd X`、`cd X && { …; }`、`cd X && ( … )`、`(cd X; true)|cat` 都對。
  - `cd X | cat && …` 修後問,對。
  - `cd >/dev/null X &&` 修後比修前更準確(導向被剝掉,`cd X` 才被認得)。
- `_local_url` 與推送目標:
  - `file:/x`(單斜線)、`~/x`、`$HOME/x`、`origin`、`host:/x` 全部走網路位址,都問,偏安全。
  - `file:///tmp/../Users`、`file://…/../../..`、指到真 repo 的符號連結都問。
  - `file://tmp/x` 回傳相對路徑,只有 cwd 剛好是 `/` 才可能誤豁免,不構成實際問題。
  - `git push /tmp`(目錄本身)豁免,但那不是 repo,推送本身會失敗,無害。
  - `file://localhost/tmp/x` 多問,可接受。
- 效能:各種 1 萬到 2 萬字的最壞輸入都在 0.04 秒內。

**三問**

- 原問題的修復效果:導向剝除、管線 `cd` 還原、`$'…'` 解碼、結尾反斜線、續行這幾項,在 `bypass_reasons` 層都有同一案例「修前 `[]`、修後命中」的證據(`t1.py`、`t2.py`、`t7.py`)。但發現 1 顯示其中解碼與續行兩項在入口層沒有生效。
- 修補處的相鄰路徑:正常與錯誤路徑成立。例外是發現 2、3、4,仍會誤給豁免。這三條在修前就如此,修補沒有惡化。
- 新發現的同案例修前修後:發現 2、3、4、5 兩版都是 `[]`。發現 1 的分類器層是修前 `[]`、修後命中,入口層兩版都靜默。發現 6 是修前不問、修後多問。

**固定席節點逐條判**

- `Issues/code-loop守衛main-direct盲區.md`:只牽連 `scripts/test_lumos.py`,與本席的掛鉤邊界輸入無關,不影響。
- `Systems/lumos-cli-read.md`:search 排除 superseded 的 INVARIANT 與本改動無關,不影響。
- `Systems/lumos-cli-lifecycle.md`:re-inject 保留 sentinel 之外內容的 INVARIANT 與本改動無關,不影響。我沒看到新掛鉤動 CLAUDE.md 注入。
- `Systems/design-loop.md`:處置閘第五步的 INVARIANT 與本改動無關,不影響。
- `Systems/測試假綠形態.md`:要求還原翻紅釘配前置斷言。發現 1 正好是同型風險,分類器層測試綠、入口層靜默;測試應從 `entry()` 層驗,但這屬於測試組的範圍。
- `Systems/guard-kill.md`:guard kill 的 rc 與 JSON 純度與本改動無關,不影響。
- `Systems/pitfalls-code-loop.md`、`Systems/reversibility-governance-ledger.md`:牽連 `scripts/lumos`,不在我的程式組範圍,未判,不影響本席結論。
- 其餘只列名的節點:不在我的程式組範圍,未判。

最嚴重等級為 major,blocking 共 1 條(發現 1),其餘 5 條為 minor。
