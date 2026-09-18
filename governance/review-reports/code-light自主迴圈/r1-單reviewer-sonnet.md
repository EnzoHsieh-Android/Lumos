severity: major

## F1 light 抽不出 affected_keys 時,自主迴圈靜默只跑一條、沒有警語(該整支跑卻只跑一條)

severity: major
blocking: yes

`_al_hit` 的判定邏輯是「有命中才清空 `_AUTOLOOP_ARGS`、整支跑;沒命中(含 `_SUITE_KEYS` 本身是空字串)就維持 `-k real_claude_md`」。但 `_SUITE_KEYS` 在 light 且 `light_ok=true` 時**是可以合法地是空字串的**——我用真的 `lumos pitfalls --diff` 對一支 basename 只有兩個字的程式檔(`app/db.py`)、且改動沒動到任何 `def` 行,實測拿到 `"affected_keys": [], "light_ok": true`。原因在 `scripts/lumos` 的 `_KEY_OK_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{2,}")`(最短 3 字),像 `db.py`/`io.py`/`os.py`/`ui.py` 這種常見短檔名,基名去副檔名後只有 2 字,連檔名鍵都抽不到,函式名鍵又要求 diff 裡真的動到 `def` 行,兩邊都可能落空。

這種情況下,`_al_hit` 迴圈對空字串一輪都不會執行(`[[ -n "$_k" ]]` 直接為假),`_AUTOLOOP_ARGS` 維持 `(-k real_claude_md)`,自主迴圈 144 支裡只跑 1 支就放行推送。跟旁邊「keys 子集」的對應邏輯比:抽不出關鍵字時,keys 子集會印「這次改動抽不出函式或檔名當關鍵字,推送前只跑文件子集;CI 會跑全套當後盾」;但自主迴圈這條路完全沒有等價的警語或退回整支跑,使用者不會知道這次自主迴圈只驗了 1/144。這也違反同一支檔案(`scripts/lumos`)自己在別處講的設計原則「算不出範圍 → full(fail-safe 是多跑,不是少跑)」。

引句:「[[ -n "$_al_hit" ]] && _AUTOLOOP_ARGS=()   # 改到它在測的東西(例:$_al_hit)→ 整支跑」

file: `scripts/lumos:22367`(`_KEY_OK_RE` 最短 3 字,2 字檔名如 db/io/os/ui 被濾掉)
file: `scripts/lumos:22364`(`light_ok = len(code) == len(non_docs)`,只要 non_docs 全是程式檔就是 true,不要求 affected_keys 非空)
file: `scripts/lumos:22340`(同檔案自己的既有設計原則:「算不出範圍 → full(fail-safe 是多跑,不是少跑)」)

機械驗證:在乾淨 worktree(`git -C /Users/enzo/harness/lumos-toolchain worktree add --detach /tmp/seat-單reviewer-sonnet HEAD`)裡用 `_sc_setup` 建好風險低計劃的假環境,把 `app/db.py` 收進 Home 落點、只改函式體一行(不動 def 行),直接呼叫 `python3 scripts/lumos pitfalls --diff <base>..<head> --no-lint --json --repo <d>`,回傳 `"affected_keys": [], "light_ok": true`,已核對。

## F2 grep -qw 沒跳脫正規表示式特殊字元,key 含字面 `.` 時把 `.` 當任意字元比對

severity: minor
blocking: no

`_affected_test_keys` 的檔名鍵是「basename 去掉最後一個副檔名」,像 `settings.dev.py`(`rsplit(".", 1)`)會產生 `settings.dev` 這種**中間還帶字面 `.` 的鍵**。`grep -qw -- "$_k"` 沒有先用 `grep -F`/跳脫就直接把 `$_k` 當正規表示式餵進去,`.` 在正規表示式裡是「任意字元」,不是字面句點。我實測 `grep -qw -- "a.b"` 對只含 `aXb`(沒有句點)的文字一樣會命中(`-w` 只檢查整個 pattern 頭尾外側是不是非單字字元,不會逐字比對內部的 `.`)。

方向上這只會造成「多跑」(誤判成有命中、整支跑自主迴圈),不會漏掉真正該跑的紅、也不會誤擋合法推送,所以沒有壓過 major 的門檻,但這是新增程式碼裡沒處理的跳脫問題,遇到含字面句點的鍵時會侵蝕這次改動想省下的 67 秒。

引句:「[[ -n "$_k" ]] && grep -qw -- "$_k" "$REPO_ROOT/scripts/test_autonomous_loop.py" 2>/dev/null && { echo "$_k"; break; }」

機械驗證(在 `/tmp` 建的臨時檔案,不動 repo):
```
printf 'this file mentions aXb somewhere\n' > t1.txt
grep -qw -- "a.b" t1.txt && echo MATCHED   # → MATCHED(無句點的文字也命中)
```

## 驗過的路徑(沒發現)

- **背景子殼的離開碼傳遞**:`( run_group s … ) & _gpid=$!` / `( run_group k … ) & _kpid=$!` 是 command substitution 外的純子殼,`run_group` 的 `return 0/1/3` 會原樣變成子殼的離開碼,`wait "$_gpid"`/`wait "$_kpid"` 能正確收到。用獨立腳本模擬 `S_RC`×`K_RC` 的 0/1/3 全組合(含「一組 3 一組 1」),`_grc`/`_krc`/最終 `_rc` 都算對:`_grc=3`(docs 選中 0 支)搭配 `_krc=1` 時,`[[ "$_grc" -ne 0 ]]` 仍會把 `_rc` 設成 1,不會被吞掉。
- **`_kpid` 未定義的路**:`_kpid` 只在 `if [[ ${#_keys_args[@]} -gt 0 ]]` 這個區塊內被賦值與使用,`_keys_args` 為空(keys 那組沒起)時完全不會碰到 `$_kpid`,`set -u` 不會炸。
- **兩組真的平行跑**:`_gpid`/`_kpid` 都是在任何 `wait` 呼叫之前就已經 `&` 起背景,`wait "$_kpid"` 只會擋住主殼等 k 組,不影響 s 組已經在背景平行執行,符合作者「兩組真的同時跑」的宣稱。
- **`printf '%s\n' … | tr ',' '\n' | while read` 的換行修法**:實測 `printf '%s'`(無換行)版本會在 `while read` 掉最後一個關鍵字(`foo,bar,baz` 只收到 `foo`/`bar`),換成 `printf '%s\n'` 後三個關鍵字都收到,修法確實對症。
- **假自主迴圈測試檔改內容再推那個情境**:新測試把 `af.write_text(...)` 改動留在**未 commit 的工作樹**上就呼叫 `push()`,沒有呼叫 `_sg_commit`,所以 `git diff base..head` 不會把這次修改算進推送範圍,不會重演「假執行器記錄檔被 git add -A 帶進提交」那種同型 bug;`alog`(記自主迴圈假測試參數的檔)本身也刻意放在 `d.parent`(repo 外),跟 `argl` 同一個做法。
- **多 ref 推送(一個 light 一個 docs)**:`_SUITE_LIGHT`/`_SUITE_KEYS` 是跨 ref 迴圈累積的全域旗標,docs ref 不會把已經被 light ref 設成 1 的 `_SUITE_LIGHT` 洗回去,`_suite_mode` 計算時 light 會蓋過純 docs(`[[ "$_SUITE_LIGHT" -eq 1 ]] && _suite_mode="light"`),結果是文件子集 + keys 子集都跑,涵蓋範圍不會比單獨判斷任一 ref 窄。
- **關鍵字很多時的效能**:`_al_hit` 迴圈對單一檔案(`test_autonomous_loop.py`)做逐鍵 `grep -qw`、命中就 `break`,鍵數頂多幾十個、檔案大小有限,不構成實質效能問題。
- 讀過 `scripts/hooks/pre-push` 全檔(504 行)與 `scripts/test_lumos.py` 裡 `_sc_setup`/`_sg_commit`/`t_prepush_docs_and_light_run_subset`/`t_prepush_and_ci_wired_for_docs_suite` 的完整既有內容與本次新增部分,沒有讀 governance/review-reports 底下任何席報告或 intake。
