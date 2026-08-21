# r3 對抗審計 — S2 seat: S3 v3 push-point enforcement(marker range/HEAD 綁定)

Lens: `code-loop check` 於 pre-push 實際執行點的判定式 vs `code-loop pass` 寫入的留痕——range 是否真同源、escape hatch(skip/waiver)是否真被 check 接受、branch key 是否真對得上。

---

## Finding 1 — blocker

引句：「①算 range=`_codeloop_range()`(新共用函式:有 upstream → `@{u}..HEAD`;無 → `merge-base(預設分支)..HEAD`)」

**What's wrong**:`_codeloop_range()` 的公式(upstream-tracking 或 merge-base)跟 `check` 真正拿到的 range 是兩套不同來源。`check` 的 range 由 pre-push hook 從 push 協商的 stdin 算出:一般情形 `scripts/hooks/pre-push:94` `_range="$_rsha..$_lsha"`;新分支首推(code/high 的正常路徑——新分支第一次跑 `pass` 時通常還沒設 upstream)或遠端 sha 本地沒抓到,是 `scripts/hooks/pre-push:88`/`91` `_range="$_EMPTY_TREE..$_lsha"`。`_codeloop_range()` 的「無 upstream」分支是 `merge-base(預設分支)..HEAD`——左端點是一個真實 commit sha,跟 git 固定的 empty-tree hash(`4b825dc6...`)在字串上永遠不相等。而 `check`(第 76 行)定義「有效留痕」要求 `marker.range == check 的 range` 逐字相等,兩公式在**最常見的 tier=high 推送形狀(新分支第一次推)**上必然不同 → 每次新分支首推都會被擋,而且照文件自己開的藥方「重跑 pass」(第 76 行、測試 18)沒用:`_codeloop_range()` 是確定性函式,重跑只會算出同一個錯 range,陷入無法自行解除的迴圈。文件「未決」段(第 115 行)已半承認 range「仍可能不同」,但只舉了 force-push/rebase 當例子,漏了「新分支首推」是**保證會撞**(不是「可能」),以及本地 `@{u}` 落後於 push 當下遠端真實狀態(隊友先推過、本地未 fetch)也會撞。

file:line:`scripts/hooks/pre-push:88,91,94,110`(check 實際吃到的 range 來源);`scripts/lumos:14010-14016`(`_codeloop_write` 現有留痕 schema,尚無 `range` 欄,證實這段是全新、未在文件裡把「兩邊必須真的同源」的機制講清楚)。

**correct rule**:`_codeloop_range()` 必須算出跟 push 真正會被檢查的 range **同一個**——例如直接查詢真實遠端 ref 狀態(`git ls-remote` 該目的地)或乾脆把 range 判定完全交給 `check`(用 hook 已算好的 `$_rsha..$_lsha`/empty-tree 邏輯),而不是憑本地追蹤中繼資料(`@{u}`)或跟 push 目的地無必然關係的本地 merge-base。或者退一步:留痕有效性改成語意比對(這次推送的 diff 內容是否等於曾被審過的 diff),而不是兩個各自獨立算出的 range 字串做逐字相等。

---

## Finding 2 — blocker

引句：「有效留痕=`status=passed ∧ head_sha 符 ∧ marker.range == check 的 range ∧ external_ok`」

**What's wrong**:文件對 `check` 怎麼判定有效留痕只給了這一條 AND 判定式,而文件自己開的兩道逃生門都過不了它。(a)`--waive-external`(第 77 行)明講寫 `external_ok: false` 且「check 接受之」——但判定式裡的 `∧ external_ok` 這一項會讓 `external_ok: false` 的留痕直接判無效,跟緊接著那句正面矛盾。(b)`skip`(「破窗制」那條)寫 `status: skipped`(沿用現有慣例,`scripts/lumos:14107` 現行判定式是 `status in ("passed", "skipped")`)——但新判定式第一項寫死 `status=passed`,全文找不到任何 `status=skipped` 的替代分支。照字面實作,一次合法跑過 `--waive-external` 或 `skip --class emergency` 的 tier=high 推送,會被 `check` 判得跟「完全沒留痕」一樣——把文件自己強調「逃生門要留著、只是變貴、被計數」(第 79 行:「skip 仍是合法逃生門...這就是本案對「更便宜的門」的回應,不是消滅它」)的設計意圖悄悄吃掉,而且是對現有正確行為(`scripts/lumos:14107` 現在正確地把 passed/skipped 都當有效)的倒退。

file:line:`scripts/lumos:14107`(現行 passed/skipped 皆有效的正確判定,新規則要保留而非取代);`scripts/lumos:14047` `_codeloop_guard_verdict`(要被擴充成含 range/external_ok 的函式——文件這一行式子讀起來像是「取代」整個判定,而非「疊加」在既有 status 分支判定之上,這個沒說清楚就是 bug 的根)。

**correct rule**:判定式要按留痕種類分開寫,而非單一 AND,例如:`status=passed → (range 符 ∧ external_ok=true)`;`status=skipped → (class ∈ {false-positive, emergency})`;`status=passed ∧ external_ok=false → waiver 非空`(waived 路徑)。單一扁平 AND 沒辦法表達「pass/skip/waiver 三選一皆合法」。

---

## Finding 3 — major

引句：「閘必須在 **pre-push 實際執行的 `code-loop check`** 裁決,`pass` 只負責把證據寫進留痕」

**What's wrong**:`pass`/`skip` 寫留痕檔用的 key 純粹是**當下 checkout 的分支名**(`scripts/lumos` `cmd_code_loop`:`branch = _codeloop_git_branch(repo_root)`,pass/skip 無條件套用,不看任何 `--branch`/推送目的地參數);而 `check` 查留痕檔用的 key 是**推送目的地**分支名,由 hook 傳入 `--branch "$_rbranch"`(`scripts/hooks/pre-push:109-110`:`_rbranch="${_rref#refs/heads/}"`)。文件默默假設這兩個永遠一樣。當本地分支名跟實際推送目的地不同(例如 `git push origin HEAD:feature-x` 但本地在 `wip` 分支跑的 `pass`,或任何「推送時改名」的工作流)就會分岔:`pass` 寫進 `governance/code-loop/wip.json`,`check` 去找 `governance/code-loop/feature-x.json`,永遠找不到,永遠回報「無留痕」——跟 range 對不對完全無關。v3 在這條查找路徑上疊加了更嚴的 range/HEAD/external_ok 判定,卻從未驗證「讀到的檔案是不是 pass 真的為這個推送目的地寫的那份」。

file:line:`scripts/lumos:14139-14160`(cmd_code_loop——branch 只從 checkout 解出一次,pass/skip 共用,不管實際推送目的地);`scripts/hooks/pre-push:109-110`(`_rbranch` 由目的地 ref 推出,只傳給 check,不曾回頭核對 pass 那邊用的是哪個 branch)。

**correct rule**:要嘛(a)`pass`/`skip` 也接受一個對應「即將推送到哪」的顯式 `--branch`/目的地參數,要嘛(b)`check` 在目的地分支的留痕檔缺席時,退而嘗試 checkout 分支的留痕檔(並印出提示),避免「推送時改名」這種常見情形悄悄變成「看起來像完全沒跑過 pass」。

---

3 findings(2 blocker / 1 major)
