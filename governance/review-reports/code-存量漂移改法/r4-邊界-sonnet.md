severity: major

範圍:c4 新形狀(`--new` 邊界輸入、`_drift_c4_item`、`_drift_c4_text_err`)、`_drift_git_cmd`、`Env.find` 剝 ./。實驗在 `git clone --shared` 臨時目錄,用 test_lumos.py 的 `_df_repo`、`_df_fix` 夾具,並用 PyYAML 6.0.3 當「標準 YAML」讀回。

已跑過、沒發現問題的輸入(不列 finding,列出供收貨端對照):
- `--new` 為 `"`、`'`、`''`、`a\b`、`x: y`、`- z`、`[a]`、`*a`、`a|b`、`~`、`true`、`2026-01-01`、`123`、`a #b`、`#c`、全形空白在中間、NBSP 在中間、emoji、組合字元、3000 字長字串:全部寫成 `_yaml_quote` 的引號形,PyYAML 讀回等於 --new。
- `--new` 為空字串:被 `--old、--new 不能是空字串` 擋下。含 Tab、頭尾空白、單雙引號並存:擋下且檔案不動。
- 原項目為 `""`、`-` 後多空白、下一行是另一個頂層鍵、`valid_under:` 後沒空白直接接值、檔案只有單行值:結果正確。原項目帶行尾註解、`&anchor` 開頭、下一行縮排註解:工具擋下要手改。
- `Env.find`:`./`、`././x`、`.//x`、`./x.md`、`.`、`./.` 都回 None(沒有筆記時),`./-x` 找到 `-x.md`,`./Done_計劃` 走檔名找到;沒有走偏或誤中別篇。
- `_drift_git_cmd`:路徑含空白、`'`、`*`、`[1]`、`?`、`$`、`"`、`:(top)`、全形空白、NFD、60 個中文字時,印出的指令貼到 shell 照跑,`git add` 只暫存那一篇加帳檔;`--literal-pathspecs` 放在 `add` 前面位置正確;含 Tab 的路徑印出降級提示、不印指令。

## F1 valid_under 行尾註解後接區塊清單時,c4 把一個標準 YAML 讀來根本沒有問題的檔改成無法解析
severity: major
blocking: 是
引句:「    prefix, err = _drift_c4_item(lines, fe, i)
    if err:
        return None, err
    try:
        quoted = _yaml_quote(new, "--new")          # 既有的安全寫法:本工具與標準 YAML 讀出來一樣」
file: `scripts/lumos:28012`(`_drift_fix_c4`,命中行是 `valid_under:` 那一行本身時走到這裡)
file: `scripts/lumos:27946`(`_drift_c4_item` 的結尾與 `nxt` 判斷)
敘述:
1. 輸入(`valid_under` 那行帶註解,清單在下面幾行,這是合法 YAML):
   ```
   valid_under: # 還沒提交
     - 乙
     - 丙
   ```
   PyYAML 讀出 `valid_under: ['乙','丙']`,標準讀法下這一欄沒有任何「還沒提交」。本工具的 `parse_frontmatter` 不認行尾註解,把值讀成純量 `"# 還沒提交"`,所以 c4 判成發現。
2. 跑 `lumos drift fix Verification/E 4 --kind c4 --old 還沒提交 --new "已提交 abc"`,結果 rc 0,檔案變成:
   ```
   valid_under: "已提交 abc"
     - 乙
     - 丙
   ```
   PyYAML 讀它丟 `YAML ERROR: while parsing a block mapping`,整份 frontmatter 對標準讀法失效。
3. 走到哪一行:`_drift_valid_under_hits` 命中 `valid_under:` 那一行(欄位名之後的部分);`_drift_c4_item` 的 `raw[0] in "[{|>&*!%@`"` 沒包含 `#`,`re.search(r"[ \t]#", raw)` 因 `#` 在最前面(前面的空白已被 `valid_under:[ \t]*` 吃掉)不命中;`nxt` 判斷只在「下一行縮排且不是 `- ` 開頭」才擋,下一行剛好是清單項就放行;`_drift_fix_c4` 的 before/after 比對用的還是本工具自己的讀法(兩邊都讀成純量、都 1 項、`after[0] == new`),驗不出。`_drift_fix_verify` 也用本工具讀法。
4. 同一個洞的另一種輸入:`valid_under: 甲(還沒提交)` 後面接一個空行再接縮排的續行(合法的多行純量);`nxt.strip()` 為空所以不擋,寫完變成 `valid_under: "…"` 加一行孤立縮排文字,PyYAML 同樣丟錯。
5. 這正是本輪重點宣稱的「語法全由工具決定、兩種讀法一致」被破壞的那一類:發現是本工具讀法的誤判、修法又只用本工具讀法驗收。重現指令(夾具 `_df_repo` + 上面那個檔內容 + `_df_fix(v, "Verification/E", "4", "--kind", "c4", "--old", "還沒提交", "--new", "已提交 abc")`)在 9c236f23 上實測 rc 0、寫出無效 YAML;把 `_drift_c4_item` 對 `#` 開頭與「`valid_under:` 行下一行是清單或空行後縮排」加擋後應為 rc 2。

## F2 乾淨檢查的 git diff 仍用一般 pathspec,檔名含 * ? [ 時別篇的未提交改動會害這篇被誤擋
severity: minor
blocking: 否
引句:「    gp = ps[0]
    r = _lens_git(root, "diff", "--quiet", "HEAD", "--", gp)」
file: `scripts/lumos:27760`(`_drift_fix_clean_err`)
敘述:
1. 這輪為了「檔名裡的 * ? [ 不被 git 當萬用字元」給印出的指令加了 `--literal-pathspecs`,但同一函式裡真正判乾不乾淨的 `git diff --quiet HEAD -- <gp>` 沒加。
2. 輸入:兩篇筆記 `Issues/a*b.md`(有 c2 發現)與 `Issues/axxb.md`(有人手改了一行、未提交)。跑 `lumos drift fix Issues/a*b 3 --kind c2 --close --status done --reason 已經修好了`,實測 rc 2,訊息「docs/kg-knowledge/Issues/a*b.md 有未提交的改動(不是 drift fix 自己留下的)」;實際那篇沒動。`git diff --quiet HEAD -- 'docs/kg-knowledge/Issues/a*b.md'` 回 1、加 `--literal-pathspecs` 回 0。
3. 方向只會誤擋、不會誤放(字面比對照樣包含在內);提交或還原別篇後可繼續。歸在同族一次掃完:同一個 pathspec 問題在同函式沒修。

## 圖譜鏡頭固定席逐條判定
- Systems/lumos-cli-read ★INVARIANT★(search 預設排除 superseded 但不排除 stale):本 diff 沒碰 search 的濾網與排序;`Env.find` 只在最前面剝一次 `./`,不影響 search 走的路徑。不影響。
- Systems/guard-kill:diff 沒動 guard kill 的 rc 優先序與 `--json` 輸出;`_sh_quote` 只是從檔中搬到檔頭。不影響。
- Systems/lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 之間):沒碰 CLAUDE.md 注入路徑。不影響。
- Systems/bound-tests-gate:合約綁的測試仍存在;diff 改了 `t_drift_fix_c4_evidence_then_replace` 等測試但沒改閘本身。不影響。
- Systems/授權與歸屬:SPDX 檔頭沒動;`_VENDORED_TOOLKIT` 沒動。不影響。
- Systems/測試假綠形態:本輪新增的「還原翻紅釘」在測試 docstring 寫了;我沒有逐條還原驗證,不下判定。
- Systems/design-loop:diff 不碰處置閘。不影響。
- Systems/pitfalls-code-loop(★RISK★):diff 沒碰 pitfalls 分級。`_codeloop_print_dirty_bookkeeping` 只因 `_sh_quote` 搬位置而不變。不影響。
- 其餘只列名的節點(loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛 等):沒有可指出的受影響行,不臆測。

最高等級:major
