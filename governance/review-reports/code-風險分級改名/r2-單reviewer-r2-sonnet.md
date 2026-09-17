severity: blocker

## F1 刪掉無副檔名的 shebang 程式檔(例如 scripts/hooks/pre-push 本身)會被判成「沒有程式檔」→ tier=light,漏派代碼審

severity: blocker
blocking: yes

引句:「+def _is_code_file(rr, path):」
引句:「+    kind = _nodehome_code_kind(path)」
引句:「+    if kind != "shebang?":」
引句:「+        return False」
引句:「+        with open(Path(rr) / path, "rb") as f:」
引句:「+        except OSError:」
引句:「+        return False」

觀察:`_is_code_file` 對「沒副檔名、要看首行 #!」的檔案,是拿 `rr`(repo 根,現行工作樹/HEAD 的檔案系統路徑)去 `open()` 讀首行。如果這支檔案在這次 diff 裡是被**整支刪除**,現在的工作樹上它已經不存在,`open()` 會丟 `OSError`,函式回 `False` = 不算程式檔。而 `_pitfall_diff_collect`(patch 第 22374/22438 行一帶)呼叫 `_pitfall_tier(claims, list(added) + list(changed_lines), repo_root, diff_range)`——`changed_lines` 這個 dict 對「整檔刪除」的處理是:遇到 `+++ /dev/null` 時 `cur_file = _old_file`(被刪那支檔的舊路徑),接著把它所有的 `-` 行內容記進 `changed_lines[cur_file]`,所以被刪檔案的路徑**確實在** `_pitfall_tier` 收到的 `files` 清單裡,只是 `_is_code_file` 對它讀不到檔而判 False。

重現(在 worktree /tmp/seat-rn-r2-reviewer,HEAD=f8077c03,即這批凍結 patch 的終點):
```
git rm --cached scripts/hooks/pre-push -q
rm -f scripts/hooks/pre-push
git add -A
git commit -q -m "test: delete pre-push hook"
python3 scripts/lumos pitfalls --diff HEAD~1..HEAD --repo /tmp/seat-rn-r2-reviewer --no-lint
```
實際輸出:
```
tier: light(改動裡沒有程式檔(只有文件/資料/圖譜))
```
而 `scripts/hooks/pre-push` 第一行是 `#!/usr/bin/env bash`(`git show HEAD~1:scripts/hooks/pre-push | head -1` 驗過),是貨真價實的無副檔名程式檔——它本身就是這次改動 patch 裡改到的那支檔(`scripts/hooks/pre-push` 開頭沒有副檔名)。

為什麼是 bug:這支工具的整套改動風險分級(`_pitfall_tier`)存在的目的就是決定「這批要不要派代碼審」;作者自己在函式 docstring 寫「改動裡沒有任何『需要有家的程式檔』→ light」,但「刪掉一支程式檔」明明是最該審的一種改動(刪除守衛/hook/邏輯),卻因為刪除後檔案在工作樹上讀不到而被歸類成「跟改動 README/圖一樣沒風險」。本 repo 大量核心檔就是這種無副檔名 shebang 檔(`scripts/hooks/pre-push`、`pre-commit`、`post-commit` 都沒副檔名),攻擊面不是邊角案例。`_sc_diffusion`(patch 第 5731/5758 行)用的是同一支 `_is_code_file`,同一個洞也會讓小改動閘漏算被整檔刪除的無副檔名程式檔(擴散檔數/落點檢查都少算它)。
測試面:`scripts/test_lumos.py` 裡 `t_pitfalls_tier_light_sources` 只測了新增/修改情境(README/圖/.gitignore/Makefile 判非程式碼、小改一行判 standard),完全沒測「整檔刪除無副檔名程式檔」這個路徑,所以現有測試套件過不了也擋不下這個洞。


## 複核(上一輪四件)

severity: clean

①pitfalls(宣告 vault-free)拿掉 Env 載整份圖譜:複核通過。`_pitfall_tier`/`_ledger_has_manual_only`(patch 第 22374/22503 行一帶)只用 `find_vault` 找路徑、直接 `read_text` 讀 `.canary-log.jsonl` 找子字串 `"manual_only": true`,沒有建 `Env`、沒有 parse 節點圖。
引句:「+def _ledger_has_manual_only(repo_root):」

②每支檔有家節點沒登記新消費者(文件):`_is_code_file` 是「每支檔有家同一套定義」的新消費者,patch 裡多處註解(如 `_sc_diffusion` 那行)寫「每支檔有家同一套」,但這輪凍結材料只給 `scripts/lumos` / `scripts/hooks/pre-push` 的 diff,沒有 `docs/` 底下的節點變更可核對——文件登記與否要看未凍結的圖譜筆記,超出這份審材範圍,不在這裡判定。

③「計劃風險低+全靠人驗+小改動閘過 → light」不重跑有綁測試候選的測試:**這件事本身沒有問題,但複核時發現實作路徑跟審查詞的說法不一致,已拆成 F2 另外提報告——見下方 F2。**

④`_nodehome_code_kind` 對無副檔名回 shebang? 被當程式檔:`_is_code_file` 補了首行 `#!` 檢查(patch 第 4907/22244 行一帶),對「新增/修改」的無副檔名檔判定正確(見 `t_small_change_gate_docs_files_need_no_home`、`t_pitfalls_tier_light_sources` 的 README/.gitignore/Makefile 案例都過);但對「刪除」的無副檔名程式檔有反向錯,已獨立報 F1。


## F2 `_spec_gate_push_report(manual_only=True)` 是死碼,從未被任何地方呼叫;圖譜 KEY 卻寫它是「light 分級」的機制——合約與圖譜不一致

severity: major
blocking: no

引句:「+def _spec_gate_push_report(env, rr, git_range, manual_only=False):」
引句:「+    manual_only=True 只查全靠人驗的留痕(不跑任何測試)。"""」

觀察:在整份 `scripts/lumos` 裡搜尋 `_spec_gate_push_report(`,只有第 5847 行那個 `def` 本身,沒有任何呼叫端(`grep -n "_spec_gate_push_report(" scripts/lumos` 只回一行)。實際印出「改動風險分級:light」的地方是 `_spec_gate_push_check`(patch 第 5878/5928 行一帶),它直接呼叫 `_spec_gate_push_scan(env, rr, plans, git_range)`(**沒有帶 `manual_only=True`、也沒有經過 `_spec_gate_push_report`**),然後在拿到 `oks` 之後才判斷是否全部 manual_only 再印 light:
引句:「+    if not bad and oks and all(mo for _p, mo in oks):   # 計劃風險低+全靠人驗+小改動閘過 → 改動風險分級 light(2026-09-18 Enzo 裁;pitfalls/code-loop 都是 vault-free,只有這裡有圖譜)」

但是 `docs/lumos-toolchain-knowledge/Systems/規格閘.md` 的 KEY(審材外查證):
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:31`
「KEY:[2026-09-18]spec-gate --push-check 全部候選都是全靠人驗且都過 → 印「改動風險分級:light」與 loop next --tier light(計劃風險低+小改動閘過=只派架構對齊席;pitfalls/code-loop 是 vault-free 所以放這裡);_spec_gate_push_report(manual_only=True) 給分級用時不跑任何測試、不記逃逸 [test:t_pitfalls_tier_light_sources]」

這句話明確斷言「light 分級用 `_spec_gate_push_report(manual_only=True)`、不跑任何測試」,但實測與 grep 都證明:真正跑的是 `_spec_gate_push_scan`(不帶 manual_only),它**會對留痕裡有綁測試的候選真的去跑測試**(見 `_spec_gate_push_one` 沒被 `manual_only` 短路);「不跑任何測試」只對死碼裡未被呼叫的那條路徑成立,不是實際發生的行為。`[test:t_pitfalls_tier_light_sources]` 這支測試(scripts/test_lumos.py:43932 一帶)驗的也是 `_spec_gate_push_check` 直接印 light,同樣沒有經過 `_spec_gate_push_report`——測試綠不代表 KEY 描述的機制存在,只代表「light 這個字串有印出來」,兩件事被混為一談。

為什麼是 bug(合約與圖譜一致這個面向):下一個讀這篇筆記的人(AI 或人)會照 KEY 的說法去 `scripts/lumos` 找 `_spec_gate_push_report` 想確認「分級真的不跑測試/不記逃逸」,結果會發現這支函式根本沒被接進主路徑,得到錯誤的心智模型(以為有一條「輕量、不跑測試」的分級專用路徑,實際上分級只是全套 `push-check` 掃描的副產物,會跑測試、也可能記逃逸)。另外,`_spec_gate_push_report` 這支死碼本身也帶一個潛在缺陷,若日後真的被接上:
引句:「+        if manual_only and (rec.get("tests") or []):」
引句:「+            oks.append((prel, False))   # 有綁測試的:不在這裡跑(spec-gate --push-check 會跑),只記「不是全靠人驗」」
它把「有綁測試、根本沒被驗過」的候選直接塞進 `oks`(=「過了」的清單),沒有標記「未驗證」;呼叫端如果只看 `oks` 非空就當作放行依據,會把「還沒驗過的測試」誤當「已經過」,是語意上的假綠風險——目前因為死碼沒被呼叫而沒有實際發生,但既然圖譜已經在描述它、遲早會有人依圖譜去接線,先記下來。

建議處置:要嘛刪掉 `_spec_gate_push_report`(連同它未使用的 `manual_only` 分支)並改圖譜 KEY 只描述真正在跑的 `_spec_gate_push_check`/`_spec_gate_push_scan` 路徑;要嘛真的把它接進去且修掉上面那個「未驗證也塞進 oks」的問題。兩者選一,不要留著一支沒人呼叫、圖譜卻宣稱是機制核心的函式。
