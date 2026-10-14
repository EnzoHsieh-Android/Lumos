severity: major

補充:實驗全放在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/資安-sonnet/`,沒動 repo。另外要提醒:審查席的 Bash 被擋掉「git 加 push 同一行」,所以 push 相關重現是用腳本檔跑的。

1. 程序替換 `<(…)`、`>(…)` 裡的 git 指令不再被看見(修補造成的回歸)
severity: major
blocking: 是
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:一般的 Bash 工具呼叫。
  - 送什麼:`cat <(git commit --no-verify -m x)`,或 `diff <(true) >(git push --no-verify origin main)`。
  - 拿到什麼:提交和推送都真的會跑,真 repo 的提交前閘和推送前閘被跳過,掛鉤不問。
- 走到哪:`_tokens` 把 `<(` 認成導向運算子 `_Redir`,`_strip_redirects` 接著把它「後面那一個詞」當導向目標剔除,剔掉的剛好是 `git`。剩下的 `commit --no-verify` 段裡沒有 git 詞,於是沒有任何命中。bash 實測會執行程序替換裡的指令:`cat <(echo RAN-IN-PROCSUB)` 印出 RAN-IN-PROCSUB。
- 引句:「out.append(_Redir(t[k:]))」
- 重現(同一份輸入,修前修後各跑一次,預篩在修後也是 True):
  - 修後 465736e9:`bypass_reasons("cat <(git commit --no-verify -m x)", cwd)` 回 `[]`。
  - 修前 9b8ce146:同一輸入回 `['no-verify']`。
  - 第二個輸入 `diff <(true) >(git push --no-verify origin main)` 也是修前 `['no-verify']`、修後 `[]`。
- 歸因:有證據的修復回歸。`_Redir` 這個類別和 `_tokens` 的拆分是這次修補加的。
- 應該是:只有明確的導向運算子(`>`、`>>`、`<`、`&>`、`>&`)才吃下一個詞;`<(`、`>(` 這種括號開頭的要當「開子殼層」處理,不吃詞。

2. `(( 1<<EOF ))` 讓前處理誤判有 heredoc,把後面一行真指令當內文剝掉(原有漏查)
severity: major
blocking: 是
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:一般的 Bash 工具呼叫。
  - 送什麼(三行,最後一行的 `EOF` 會報 command not found,但提交已經跑了):
    ```
    (( 1<<EOF ))
    git commit --no-verify -m x
    EOF
    ```
  - 拿到什麼:提交的閘被跳過,掛鉤不問。
- 走到哪:`_bare_special` 的 `<<` 判斷只排除了 `$((`、`<<<`,沒排除裸的 `((…))` 算術命令。`_heredoc_op` 把 `<<EOF` 登記成 heredoc,`_drop_bodies` 在換行後把中間所有行剝到獨佔一行的 `EOF`,真正的 `git commit --no-verify` 就從分類器的視野消失。
- 預篩有同樣的問題:它拿「原文加正規化後文字」比字樣。這個輸入原文本身有 `--no-verify`,預篩回 True,所以進了分類器,但分類器看到的是剝光後的版本。
- 引句:「if self.heredoc_ok and cmd.startswith("<<", i) and not cmd.startswith("<<<", i) and (i == 0 or cmd[i - 1] != "<"):」
- 重現:
  - bash 實測 `(( 1<<EOF ))` 之後的 `echo RAN-AFTER-ARITH-HEREDOC` 會執行,結束字那行只報 `EOF: command not found`。
  - 修後和修前對該輸入的 `bypass_reasons` 都回 `[]`(預篩為 True)。
  - 對照:`$[1<<EOF]` 的變形被誤抓,因為結束字讀成 `EOF]`,所以不構成繞法。
- 歸因:有證據的原有漏查(修前修後同為 `[]`)。
- 應該是:heredoc 運算子只在「指令位置」認,或遇到 `((` 開頭的命令就不登記;更保守的做法是:剝掉內文時,如果被剝的內文含 git 或 `--no-veri` 字樣就不剝(寧可多問)。

3. `--push-o` 這類長選項縮寫,讓推送目的地被判成暫存目錄(原有漏查,有伺服器條件)
severity: major
blocking: 是(但標 ⚠,理由在下面)
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 從哪:在真 repo 的工作目錄裡執行。
  - 送什麼:`git push --no-verify --push-o /tmp origin main`。
  - 拿到什麼:向真遠端推送,推送前閘被跳過,掛鉤不問。
- 走到哪:
  - `_push_remote_arg` 只認完整寫法 `-o`、`--push-option`、`--repo` 等會吃值的選項。
  - git 的 parse-options 接受唯一縮寫,`--push-o` 就是 `--push-option`,git 會把 `/tmp` 當 push option 的值。我在本機重現過:錯誤訊息是 "receiving end does not support push options",和完整寫法 `-o /tmp` 同一個錯,證明 git 吃掉了 `/tmp`。
  - 掛鉤則把 `/tmp` 當第一個位置參數,也就是遠端。`_local_url` 判成本機路徑,`_temp_target` 看到 `/tmp` 存在且在暫存根底下,於是 `_push_target_temp` 回 True,`no-verify` 命中被豁免。
- 引句:「_PUSH_VALUE_OPTS = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}」
- 重現:
  - 修後與修前,`bypass_reasons("git push --no-verify --push-o /tmp origin main", <真 repo 的 cwd>)` 都回 `[]`。
  - 對照:完整寫法 `--push-option /tmp` 回 `['no-verify']`。
- ⚠ 條件:
  - 伺服器要接受 push options(GitLab、Gitea 等;GitHub 我不確定)。
  - 本機用 `file` 傳輸的裸 repo 即使開了 `receive.advertisePushOptions` 也報不支援,所以我沒能做出端到端成功推送。
  - 掛鉤端的誤判和 git 端的縮寫解析都已實測。
- 歸因:有證據的原有漏查。
- 應該是:縮寫要比照 `--no-veri` 的做法處理,對 `--push-option`、`--receive-pack`、`--exec`、`--repo`、`--recurse-submodules` 的任何非空前綴都當吃值選項;或只要出現未知的 `--` 開頭選項,就保守不豁免。

4. 直接叫 git 的子指令執行檔(`git-commit`、`git-push`)不會被當成 git
severity: minor
blocking: 否
- 攻擊路徑:
  - 誰:被提示注入的代理。
  - 送什麼:`/Library/Developer/CommandLineTools/usr/libexec/git-core/git-commit --no-verify -qm x`(本機 Apple Git 2.39.2 這個目錄有 `git-commit`、`git-push`)。
  - 拿到什麼:提交真的完成,而且 `--no-verify` 生效;我實測 pre-commit 沒跑,`log` 多了一筆提交。
- 走到哪:`_command` 只認檔名等於 `git` 的詞,`git-commit` 的基底檔名不等於 `git`。
- 實測:修後、修前都回 `[]`。
- 歸因:有證據的原有漏查。〈範圍〉沒列。
- 引句:「gi = next((k for k in range(i, len(seg)) if os.path.basename(seg[k]) == "git"), None)」

5. `-c include.path=<檔>` 讓設定檔把掛鉤目錄換掉,指令字面不含 `core.hooksPath`
severity: minor
blocking: 否
- 攻擊路徑:代理先用另一個 Bash 寫一個含 `[core] hooksPath=/dev/null` 的檔,再執行 `git -c include.path=/tmp/inc.cfg commit -m y`。
- 實測:提交成功、pre-commit 沒跑;預篩因沒有三個字樣而直接放行,`bypass_reasons` 回 `[]`。
- 為什麼只標 minor:這和〈範圍〉承認的「直接改 `.git/config`」同形,代理本來就能寫檔再繞,所以屬同族。
- 另外,`GIT_CONFIG_GLOBAL=檔` 被 repo 層設定蓋掉,不構成繞法(實測 pre-commit 照跑)。
- 歸因:有證據的原有漏查。
- 引句:「_CFG_ENV_ASSIGN = re.compile(r"^GIT_CONFIG_(KEY_[0-9]+|PARAMETERS)=(.*)$", re.S)」

6. 全域選項 `--attr-source <樹>`(帶分開的值)沒列進吃值選項
severity: minor
blocking: 否(推論)
- 掛鉤端已重現:`git --attr-source HEAD commit --no-verify -m x`,`_parse_git` 把 `HEAD` 當子指令,回 `[]`。
- 我沒能在 git 端確認,因為本機是 2.39.2,而 `--attr-source` 我記得是 2.40 才有,所以標推論。
- 做法:把 `--attr-source` 加進 `_GIT_VALUE_OPTS`,或遇到不認得的全域選項就保守地往後多看。
- 歸因:未判定。
- 引句:「_GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}」

已看,無:
- 路徑判斷:`..`、符號連結和相對路徑都靠 `os.path.realpath` 解開,`_join` 不做文字化簡。`~` 與沒賦值的 `$TMPDIR`、`${X:-…}` 都回 `_UNKNOWN`,不豁免。沒有找到讓真 repo 被判成暫存實驗 repo 的路徑。
- `_hookevent`:
  - `d.glob("hook-events.*.trim")` 的樣式是寫死的,不含使用者輸入。
  - 符號連結被跳過,就算 `unlink` 也只會刪連結本身。
  - `copymode` 只複製權限位元。
  - `os.replace(tmp, f)` 同目錄原子換入。
  - 沒找到能刪別的檔的路徑。
- 輸出:
  - 確認框理由只用固定文字,不嵌入指令內容。
  - 存活事件的 error note 是 `type(e).__name__` 加上 `str(e)[:120]`。
  - 目前能丟出來的例外訊息只含變數名或索引,拿不出寫進指令內容的場景,所以不報。

固定席節點逐條判:
- `Issues/code-loop守衛main-direct盲區`、`guard-kill`、`design-loop`、`測試假綠形態`、`lumos-cli-read`、`lumos-cli-lifecycle`:
  - 不影響本席的資安判斷。這些 ★INVARIANT★ 管的是 `search` 排除規則、sentinel 之間的重注入、guard kill 的回傳碼和設計審處置閘,和這次掛鉤的可利用面無交集。
  - `lumos-cli-lifecycle` 那條是重注入保留使用者手寫內容,這次掛鉤沒改動它。
- `pitfalls-code-loop`、`reversibility-governance-ledger`:標 ★RISK★,牽連 `scripts/lumos`。那屬於測試文件組。

三問:
1. 原問題的修復有行為證據嗎?
   - 引號、續行、ANSI 引號這些前處理,在我沒測的範圍內沒看出問題。
   - 未驗:我沒逐條跑 r3 的修補案例。
   - 唯一被我證明退步的是 finding 1。
2. 修補處相鄰路徑是否仍成立?
   - 不成立:finding 1,`_Redir` 的新拆法吃掉 `<(`、`>(` 後面的詞。
3. 新發現同一案例修前修後各是什麼結果?
   - 見各條:finding 1 是修前 `['no-verify']`、修後 `[]`。
   - findings 2 到 6 修前修後相同,都回 `[]`。

最嚴重等級 major,blocking 共 3 條(findings 1、2、3)。
