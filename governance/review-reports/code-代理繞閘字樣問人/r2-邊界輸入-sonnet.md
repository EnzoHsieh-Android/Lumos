severity: major

我載入修後(4e87b682)與修前(b5be3aad)兩版,跑了約 450 條邊界輸入。修前修後的輸出逐條對照,「歸因」就是這樣得出的。實驗目錄是我自己建的,收尾已刪。

## Findings

**1. `git push` 沒寫遠端、只用 `>` / `&>` / `<` 導向暫存檔時,導向的檔名被當成推送目標,整條被判成拋棄式而放行**
severity: major
blocking: 是
- 引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」
- 走到的地方:`_parse_git` 只丟掉 `>` 這個運算子,後面的檔名留在 args。`_push_target_temp` 取第一個位置參數當遠端,`/tmp/x.log` 是本機路徑且在暫存根底下,於是被當成拋棄式。
- 重現(cwd 是真 repo,輸出都是 `bypass_reasons` 的回傳):
  - `git push --no-verify > /tmp/x.log` 回 `[]`,應為 `['no-verify']`
  - `git push --no-verify >/tmp/x.log 2>&1` 回 `[]`
  - `git push --no-verify &> /tmp/x.log` 回 `[]`
  - `git push > /tmp/x.log --no-verify` 回 `[]`
  - `git push --no-verify < /tmp/in` 回 `[]`
- 對照組:有寫遠端的 `git push origin --no-verify > /tmp/x.log` 會問,`git push --no-verify 2>/tmp/err` 也會問(第一個位置參數是 `2`)。
- 應該怎樣:解析 git 參數時,把重導運算子連同它後面的目標一起丟掉。
- 歸因:有證據的原有漏查。修前與修後這 5 條輸出都一樣。
- 補充:新測試 `t_bypass_ask_throwaway_targets` 沒有任何一條帶重導的推送。代理把輸出導到 `/tmp/*.log` 是很常見的寫法,所以我給 major。

**2. 引號裡剛好是 `>` 或 `<` 的詞也被當重導丟掉,把 `-m` 的值位移,`-n` 被吃掉**
severity: minor
blocking: 否
- 引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」
- 原因:`_unmask` 先還原遮罩,`_is_redirect` 才判斷。引號裡的 `'>'` 還原後跟真的 `>` 沒有分別,被丟掉。`-m` 的值消失後,`-n` 反而被當成 `-m` 的值。
- 重現:
  - `git commit -m '>' -n` 回 `[]`(修前也是 `[]`)
  - `git commit -m ">>" -n` 回 `[]`
  - 這輪新加的遮罩帶來一條修前沒有的路:指令本身含私用區字元時,`git commit -m '<U+E006>' -n` 修前回 `['commit-n']`、修後回 `[]`。`<U+E005>` 與 `<U+E004><U+E006>` 同樣。
  - 私用區 U+E000 到 U+E00A 是 Nerd Font 的 Pomicons 區段,不算絕對不會出現。
  - 其他私用區字元(`<U+E003>`、`<U+E004>` 單獨出現)沒影響。
- 應該怎樣:`_is_redirect` 在切詞階段、用 `_Sep` 那種「切詞時認定」的標記判斷,不要看還原後的字串。
- 歸因:`'>'` 這條是有證據的原有漏查。私用區字元這條是有證據的修復回歸(遮罩機制的副作用),只此一條。

**3. 有撇號的註解會讓後面的反斜線續行不再接起來,`--no-verify` 被切成另一段而漏掉**
severity: minor
blocking: 否
- 引句:「out.append(" " if cmd.startswith("\\\n", i) else cmd[i:i + 2])」
- 走到的地方:`_join_continuations` 只追蹤引號,不認註解,也不認 `$'…'` 內的 `\'`。註解裡的 `don't` 讓它誤以為單引號打開了,之後的 `\<換行>` 不會被接起來。shlex 把換行當分隔符,`--no-verify` 變成獨立一段。
- 重現:
  - `"# don't do this\ngit push \\\n  --no-verify"` 回 `[]`,修前也是 `[]`
  - `"# don't do this\ngit commit -m x \\\n  -n"` 回 `[]`
  - `"echo \"don't\" # it's\ngit commit \\\n  --no-verify"` 回 `[]`
  - 修前不同的一條:`"echo $'a\\'b' ; git push \\\n --no-verify"` 修前回 `['literal']`,修後回 `[]`,因為修後把 `$'…'` 換成佔位詞,但 `_join_continuations` 仍不認 `$'`。
- 同一函式還有一個小問題:續行換成一個空白,而不是 bash 的「直接去掉」。所以 `git push --no-\<換行>verify` 回 `[]`(bash 會接成 `--no-verify`),`--no-veri\<換行>fy` 卻湊巧命中。
- 應該怎樣:`_join_continuations` 要認註解與 `$'`,或改成在 `_Normalizer` 裡處理續行。
- 歸因:前三條是有證據的原有漏查,`$'a\'b'` 那條是有證據的修復回歸。

**4. `git remote set-url --add` / `--delete` 被當成「把位址換成暫存路徑」,推送被誤判為拋棄式**
severity: minor
blocking: 否
- 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
- 重現:
  - `git remote set-url --add o /tmp/lsw/rem && git push --no-verify o` 修後回 `[]`、修前回 `['no-verify']`
  - `git remote set-url --add --push origin /tmp/lsw/rem && git push --no-verify origin` 修後 `[]`、修前 `['no-verify']`
  - `--delete` 同樣被放行。
- 原因:`--add` 是在原位址之外再多一個,原本的真遠端還在,推送會兩邊都推。`--delete` 是刪掉符合的位址,不是設定新位址。
- 應該怎樣:`--add`、`--delete` 不要記進 `added`。
- 歸因:有證據的修復回歸(修前問、修後放行)。

**5. `git -C 別處 remote add 名稱 暫存路徑` 設的遠端,被拿去判斷目前目錄那個 repo 的同名遠端**
severity: minor
blocking: 否
- 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
- 重現:cwd 是真 repo,`git -C /tmp/lsw/x remote add origin /tmp/lsw/rem && git push --no-verify origin` 回 `[]`。實際推的是真 repo 的 origin。
- 原因:`added` 是整條指令共用的一個字典,沒有按生效目錄分開。
- 應該怎樣:`added` 以生效目錄加遠端名稱為鍵。
- 歸因:有證據的原有漏查(修前也是 `[]`)。

**6. `export GIT_DIR=…`(或 `GIT_WORK_TREE`)不會讓生效目錄變成未知,拋棄式豁免繼續成立**
severity: minor
blocking: 否
- 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
- 重現:`cd $(mktemp -d); export GIT_DIR=/Users/enzo/x/.git; git commit --no-verify` 回 `[]`。
- 對照:同一條改成行內 `GIT_DIR=… git commit` 或 `env GIT_DIR=…` 會問。修前這兩種行內寫法都漏,修後補上了,但 `export` 形式沒補。
- 歸因:有證據的原有漏查。

**7. `export` 只認「export 名稱」,`declare -x 名稱` 與 `typeset -gx 名稱`(只給名稱、不帶 `=`)沒跟上**
severity: minor
blocking: 否
- 引句:「handler = {"cd": self._cd, "pushd": self._lose_dir, "popd": self._lose_dir, "export": self._export,」
- 重現:
  - `LUMOS_SKIP_X=1; export LUMOS_SKIP_X; git commit -m x` 修後回 `['lumos-skip']`、修前回 `[]`
  - `LUMOS_SKIP_X=1; declare -x LUMOS_SKIP_X; git commit -m x` 回 `[]`
  - `LUMOS_SKIP_X=1; typeset -gx LUMOS_SKIP_X; git commit -m x` 回 `[]`
  - 另有 `set -a; LUMOS_SKIP_X=1; git commit -m x` 回 `[]`,屬於承認範圍內的寫法。
- 應該怎樣:`_declare` 比照 `_export`,名稱已在 `variables` 裡就標記為匯出。
- 歸因:有證據的原有漏查。`export` 是這輪補的,`declare` 同族沒一起補。

**8. `cd` 放在管線裡、或放在 `||` 與條件後面,仍被當成真的換了目錄**
severity: minor
blocking: 否
- 引句:「handler = {"cd": self._cd, "pushd": self._lose_dir, "popd": self._lose_dir, "export": self._export,」
- 重現:
  - `cd /tmp | cat; git commit --no-verify` 回 `[]`,`cd /tmp 2>&1 | tail; …` 也是
  - `cd /tmp |& cat; …` 回 `[]`
  - `cd /real/nope || cd /tmp; …` 回 `[]`
  - `[ -d /nope ] && cd /tmp; …` 回 `[]`
- 原因:bash 裡管線的每一段在子殼層跑,`cd` 影響不到後面。這輪補了 `&` 背景的還原,管線沒補。後兩條是條件式 `cd`,分析把它當成無條件執行。
- 應該怎樣:`|`、`|&` 後的段還原目錄(跟 `&` 一樣);條件式 `cd` 保守起見讓生效目錄變 `_UNKNOWN`。
- 歸因:有證據的原有漏查。
- 補充:`&` 本身我驗過沒問題:`cd /tmp & git commit --no-verify`、`(cd /tmp & …)`、`cd /tmp &> /dev/null; …` 三種結果都符合 bash。

**9. 以下寫法會漏問或誤問,但屬於有心改寫或罕見,我只列出不要求處理**
severity: minor
blocking: 否
- `$(mktemp -d -p /真repo底下)`:只看指令的第一個詞是不是 `mktemp`,就判成暫存目錄,沒看 `-p` 或模板路徑。
  - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
  - 重現:`cd $(mktemp -d -p /Users/enzo/orca) && git commit --no-verify` 回 `[]`。
  - `mktemp -d /Users/enzo/orca/xXXXXXX` 與 `$(mktemp -d >/dev/null; echo /Users/enzo/orca)` 同樣回 `[]`。
  - 歸因:原有漏查。
- `git init -b main DIR`、`git init --template X DIR`、`git clone --depth 1 URL`、`git clone -b main URL` 這幾種寫法,值旗標沒被跳過,目標抓錯,於是多問(修前放行)。
  - 引句:「target = pos[0] if pos else "."」
  - 歸因:有證據的修復回歸,方向是多問,不危險。
- `git commit -$'n'` 修後回 `[]`、修前回 `['commit-n']`。
  - 引句:「self.out.append("__LUMOS_ANSI__")」
  - 原因:`$'…'` 被換成佔位詞,內容丟了。
  - 歸因:有證據的修復回歸,屬有心改寫。
  - `git push $'--no-verify'` 與 `git $'push' --no-verify` 修前修後都回 `[]`。
- `git config --remove-section core` 與 `--rename-section core x` 會拆掉 `core.hooksPath`,回 `[]`。`〈範圍〉`只承認 `--edit` 與直接改檔。
- 以下是設計上已承認或不危險,我確認過,不當 finding:
  - `echo git push --no-verify` 這類沒加引號的字面提到會問。
  - `$(…)`、反引號、`bash -c` 裡的指令不看。
  - `git -ccore.hooksPath=/x` 黏在一起的寫法 git 本身不收。

## 已驗為正常的路徑(輸入、預期、修前修後結果相同或更好)
- **引號與註解**
  - `$(` 在單引號、雙引號、反斜線之後,都正確:`echo '$('`、`echo \$(foo`、`"\$(…)"` 都正常。
  - `$'…'` 不閉合或內含 `\'` 時,未閉合與閉合兩種都沒有崩潰。
  - `#` 接在 `$`、`{`、`=` 之後不當註解:`echo $#`、`${#x}`、`x=#a`、`a#b` 修後都問、修前漏。
- **heredoc**
  - 在 `$(` 裡、在雙引號 `$(` 裡、結束字是 `)` 或 `A B` 都正確。
  - 找不到結束字時停止剝除,寧可多問。
  - 結束字帶尾端空白或 Tab 時不算結束字,跟 bash 一致。
  - `git commit -m "$(cat <<'EOF'…EOF)" --no-verify`(內文含 `don't`、括號、引號)修後回 `['no-verify']`、修前回 `['literal']`。
- **GIT_CONFIG_KEY_n 與 --config-env**
  - `GIT_CONFIG_KEY_0=core.hooksPath` 的值大小寫都命中(`CORE.HOOKSPATH` 也是),`export` 形式命中,沒 `export` 的單獨賦值不命中,符合 bash。
  - `--config-env=core.hooksPath=X` 與分開寫都命中(修前漏)。
- **export / declare**
  - `export -f`、`-p`、`-fn` 都命中。
  - `declare -gx`、`declare -x`、`typeset -x`、`declare -xn` 帶值時命中。
  - 沒 `-x` 的 `declare` 與 `declare -p` 不命中。
- **cwd 與目錄**
  - `cwd` 是 `/` 問、`/tmp` 與 `//tmp` 放行、`rel`、空字串、`None`、`/tmp/../Users` 問、不存在的 `/tmp/zzzz` 問。
  - `mkdir -p a b c`、`--parents`、`-m 755` 都正確;`git init --bare DIR` 正確。
  - `d=$(mktemp -d); cd $d/../..` 問(修前漏)。
  - `cd /tmp &> /dev/null` 與 `cd /tmp & git …` 的行為符合 bash。
- **commit -n 解析**
  - 組合旗標與帶值旗標的跳過都對:`-mn`(訊息 `n`)、`-Sn`、`-un`、`-m -n`、`-F -n`、`-- -n` 都不誤判。
  - `-vn`、`-anm`、`-nq`、`-S"key" -n` 命中。
- **pitfall:`LUMOS_SKIP_*`**
  - 一般無害指令 41 條都不誤問,包含 `grep LUMOS_SKIP_`、commit 訊息裡提到 `--no-verify`、heredoc 內文提到、`LUMOS_SKIP_X=1 pytest`。
- **事件入口**
  - `decide` 對 `None`、`[]`、`{}`、`tool_input` 為 `None`、`command` 為數字或空字串、`cwd` 為數字都放行,不丟例外。

**效能**:長度上限 20000 之下,最壞是未閉合的 `$(` 重複約 9990 次,耗時 3.06 秒;`$((` 重複 6600 次耗時 1.96 秒;反引號重複 19900 次耗時 0.89 秒(原因是 `_replace_cmdsubs` 對每個沒配對的 `$(` 都掃到結尾)。其餘輸入(巢狀已閉合的 `$(`、引號、heredoc、分號、export 等)都在 0.1 秒以內。註冊的逾時是 5 秒,逾時失敗也是放行,所以只是延遲,不算 finding;要處理的話,在 `$(` 沒配對時一次判斷就不要再重掃。

**三問的回答**
- 原問題的修復效果:路徑 A(引號、註解、heredoc、`export`、`--config-env`、`&` 背景 `cd`、`GIT_DIR` 行內)的案例,修前漏或誤、修後正確,上面列了逐條輸入與兩版結果。
- 修補處相鄰路徑是否仍成立:多數成立。回歸只有 finding 2 的私用區字元、finding 3 的 `$'a\'b'` 加續行、finding 4 的 `set-url --add/--delete`、finding 9 的 `git init`、`git clone` 值旗標與 `$'n'`。
- 同一案例修前修後:每條 finding 都標了兩版結果。

**未驗範圍**:merge-claude-settings.py 的註冊、`_hookevent.guard` 的存活事件寫入、test_lumos.py 各測試案例是否真能翻紅,我都沒讀。固定席節點的判斷如下。
- `Issues/code-loop守衛main-direct盲區`:只牽連 `scripts/test_lumos.py`,我沒有改測試相關行為的輸入,不影響。
- `lumos-cli-read` 的 search 排除 superseded INVARIANT、`lumos-cli-lifecycle` 的 re-inject 保留 sentinel 之外內容、`design-loop` 的處置閘第五步、`guard-kill` 的 rc 優先序與 json 純度:這些路徑都跟 Bash 掛鉤的指令分類無關,不影響。
- `測試假綠形態`的「還原翻紅釘需前置斷言」:我沒審這輪新增的測試。但這輪測試缺重導、`-m '>'`、`set-url --add` 這幾條,所以那幾種修補還原後測試不會翻紅。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):只牽連 `scripts/lumos`,我沒審。

最嚴重等級 major,blocking 共 1 條(finding 1)。

涉及的檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`。
