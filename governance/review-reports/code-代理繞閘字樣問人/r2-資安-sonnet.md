severity: major

審查結果(資安席,第 2 輪):找到 5 條可被利用的洞,其中 4 條是 major,1 條 minor。第 4 條是這輪修補自己引入的回歸。第 1、3 條跟修前行為相同,是原有漏查,但都不在〈範圍〉的「攔不到」清單裡。

**重現方式**:`SourceFileLoader` 載入修後 `4e87b682` 與修前 `b5be3aad` 的 `bypass-ask-hook.py`(臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/資安-sonnet/`,腳本 `p.py`,新舊版分別在 `n/`、`o/`),對同一批輸入呼叫 `bypass_reasons(指令, repo根)`。回傳 `[]` 代表放行。下面的 `R` 是真 repo 路徑 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass`。

1. `mktemp` 只看詞首,後面接什麼參數、跟什麼指令都當成新暫存目錄
   - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
   - 位置:`_replace_cmdsubs`,`_expand` 對 `subs[word]` 回 `_MKTEMP`,`_not_real_repo(_MKTEMP)` 直接回 True。
   - 攻擊路徑:
     - 誰:被提示注入、想順手繞閘的代理。
     - 從哪:一條普通 Bash 指令。
     - 送什麼:`cd $(mktemp -d -p R); git commit --no-verify -m x`,或 `d=$(mktemp -d -p R); cd $d; git commit -n -m x`,或 `cd $(mktemp -d >/dev/null; echo R); git commit --no-verify -m x`。
     - 拿到什麼:`mktemp -p` 把目錄建在真 repo 底下,後面的提交跑在真 repo,掛鉤卻放行不問。第三種用 `echo` 直接換掉 `cd` 的目標,同樣放行。
   - 重現:三條都回 `[]`。對照組:`git commit --no-verify -m x` 回 `['no-verify']`。
   - 歸因:有證據的原有漏查。修前版本同樣回 `[]`,不是修補造成。
   - 應該是:只在 mktemp 後面沒有 `-p`、`--tmpdir=`,也沒有其他指令,而且參數都是已知安全旗標時才算新暫存目錄。其他一律判不出,照問。

severity: major

blocking: 是

2. `export GIT_DIR` / `GIT_WORK_TREE` 沒被追蹤
   - 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
   - 位置:`_GITDIR_ASSIGN` 只檢查同一段 `git` 詞之前的賦值,`_mark_exported` 完全不認這三個名字。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`export GIT_DIR=R/.git GIT_WORK_TREE=R; cd $(mktemp -d); git commit --no-verify -m x`。
     - 拿到什麼:生效目錄被判成暫存目錄,實際上 git 動的是真 repo,掛鉤放行。
   - 重現:回 `[]`。內嵌寫法 `GIT_DIR=… git commit --no-verify` 已被 r1 修補擋住,所以只有 export 這條路漏。
   - 歸因:有證據的原有漏查(修前同樣回 `[]`)。
   - 應該是:`export`、`declare -x`,或先賦值再 `export` 這三個名字後,生效目錄一律判不出。

severity: major

blocking: 是

3. 「同指令建過的目錄」的豁免,擋不住 `ln -s` 指回真 repo
   - 引句:「return _within(eff, created)     # 不存在又不是這條指令建的:cd 會失敗,git 跑在原目錄」
   - 位置:`_not_real_repo`,目錄在掛鉤判斷時還不存在,`created` 靠字串前綴比對,不管路徑之後被什麼換掉。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`mkdir /tmp/zz9 && ln -s R /tmp/zz9/r && cd /tmp/zz9/r && git commit --no-verify -m x`。
     - 拿到什麼:`/tmp/zz9/r` 落在 `created` 底下,被當成拋棄式。實際上它是指回真 repo 的符號連結,掛鉤放行。換成 `rm -rf` 後再建連結、或 `git init /tmp/x; rm -rf /tmp/x; ln -s …` 也一樣。
   - 重現:回 `[]`。
   - 歸因:有證據的原有漏查(修前同樣回 `[]`)。
   - 應該是:同一條指令裡出現 `ln`、`mv`、`rm`、`cp` 等會動到路徑的指令(其他指令的寫法也一併想過),就取消「同指令建過」的豁免。

severity: major

blocking: 是

4. 修補回歸:同指令的 `git remote set-url` 被當成「推送位址就是這個」
   - 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
   - 位置:`_remote_set`(在 `_git` 裡呼叫),以及 `_push_target_temp` 的 `if added and remote in added:`。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:
       - `git remote set-url --add --push origin /tmp/zz && git push --no-verify origin`
       - `git remote set-url origin /tmp/zz && git push --no-verify origin`
     - 拿到什麼:
       - `--add --push` 是追加一個推送位址,原本的真遠端仍然在;推送會同時送到真遠端。
       - 沒帶 `--push` 的 `set-url` 只改抓取位址;若原本另有 `pushurl`,推送仍然去真遠端。
       - 掛鉤兩種都判成「推送到暫存目錄」而放行。
   - 重現:修後兩條都回 `[]`;修前同兩條都回 `['no-verify']`(照問)。
   - 歸因:有證據的修復回歸。「同指令 `set-url` 一律記下」是 r1 之後為了放寬誤問才加的。
   - 應該是:只有 `git remote add` 的位址才採信(新增的遠端不會有舊的真位址)。`set-url` 帶 `--add`、`--delete`、不帶 `--push`,或這個名稱已存在,就不採信。

severity: major

blocking: 是

5. 預篩被引號拆字繞過(實際進入點上的洞)
   - 引句:「return "git" in low and re.search(r"\bcommit\b", low) is not None and _PRE_SHORT_N.search(low) is not None」
   - 位置:`prefilter` 只做子字串比對,不解引號;`entry` 在 `_guard` 之外先呼叫它。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`git push --no-ver''ify origin`,或 `git commit -"n" -m x`。
     - 拿到什麼:`bypass_reasons` 對這兩條會回 `no-verify` / `commit-n`(實測),但實際從 stdin 走 `entry`,`prefilter` 回 `False`,整支掛鉤不會被叫到。
   - 重現:`prefilter(json)` 對 `--no-ver''ify` 回 `False`,修前修後都是。
   - 歸因:有證據的原有漏查。
   - 說明:計劃〈範圍〉只說「有心改寫攔不到」,沒明列引號拆字。我判這條屬於未明列。
   - 理由:這是單人、問人層的設計,且需要有心改寫,標 minor;但這輪新加的拋棄式規則都可以用正常寫法繞過(第 1 到 3 條),相比之下這條是原有的設計缺口。

severity: minor

blocking: 否

**逐類確認:**
- 類 1,不可信輸入流到危險操作:
  - 已看,無可利用的路徑。
  - `git -C <目錄> rev-parse --git-common-dir` 與 `remote get-url --push <名稱>` 不會觸發 `core.fsmonitor`(只有 `status` / `diff` 這類動到 index 的指令才會),也不會執行設定檔裡的程式。
  - 名稱以 `-` 開頭時,`_push_remote_arg` 把它當選項跳過;含換行時被 shlex 切開。
  - 副作用:目錄不是 repo,或 git 因 `safe.directory` 拒絕時回 rc 非 0,`_not_real_repo` 會判成「不在任何 repo 裡」而放行。這要求目錄先在暫存根下,屬「暫存目錄就當拋棄式」的設計取捨,不單獨報。
- 類 2,輸出:已看,無。理由只用固定代碼對應的文字;存活事件的 note 是 `type(e).__name__ + ":" + str(e)[:120]`,不含指令原文。
- 類 3,`_hookevent` 的 mkstemp 新增寫入面:已看,無新的利用。暫存檔隨機命名、在同一目錄、`os.replace` 原子換入。`hook-events.jsonl` 若是符號連結,`open(f, "a")` 會追加到連結目標,那是原有行為,不是 mkstemp 新增的。
- 類 4,繞過面:見第 1 到 3 條(新加的拋棄式規則)與第 4 條。
  - 另外 `git push` 的 `file:` 位址、`_remote_url_temp` 對沒有 `@` 的 `host:path` 位址(例如 `github.com:org/repo`)會被當成本機相對路徑。若生效目錄在暫存根下就判拋棄式。要求先在暫存目錄裡操作,我沒有寫出完整攻擊路徑,標推論 minor,不列為 finding。

**三問(用於核對 r1 修補):**
- ①原問題的修復效果:本席只驗證了第 4 條的反面。同指令 `remote set-url` 在修前是照問,修後變成放行,不是修好,是放寬。其他 r1 修補(內嵌 `GIT_DIR=`、`--git-dir`、`mktemp ..`)我沒有逐條重驗。
- ②修補處的相鄰路徑:第 1、2、3 條在修前修後都不成立(都放行),所以這幾條不是修補造成,但都落在拋棄式判定的相鄰路徑上。
- ③新發現的同一案例在修前修後:見上面各條的「歸因」。只有第 4 條是修補造成的回歸(修前 `['no-verify']`,修後 `[]`)。

**固定席節點:**
- `Issues/code-loop守衛main-direct盲區`、`lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger` 等:不影響本席的資安判斷。它們的 INVARIANT 都是 search 排除、re-inject、處置閘、guard kill 等,與這支掛鉤的拋棄式判定無關;本席沒有從這幾篇找到可利用的點。
- `_hookevent.py` 屬 lumos-cli-read / lifecycle 的牽連檔;本席只檢查了 mkstemp 與 record 的寫入面,見類 3。

最嚴重等級 major,blocking 共 4 條(第 1、2、3、4 條),另 1 條 minor。
