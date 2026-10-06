severity: major

## F1 提交前提醒對每篇有改的筆記各叫兩次 git,沒有預先篩選,大量暫存時提交被拖慢 20 倍
severity: major
blocking: 是 — 效能回歸:拿 400 篇只改 status 的筆記暫存,note-shape --staged 從 3.9 秒變 78 秒;更常見的 `updated-sync` 這類大量改 updated 的提交也一樣吃這個成本
引文:
引句:「        old = _lens_git(root, "show", f"{base_where}:{path}", binary=True)」
引句:「    r = _lens_git(root, "diff", "--cached", "--name-only", "-z", "--diff-filter=M", "--", vault_rel, binary=True)」
走法:`_ns_close_summary_hits` 把圖譜下所有暫存且為 M 的 .md 列出,不管狀態有沒有動,逐篇 `git show <HEAD>:path` 與 `git show :path` 各一次(sys 時間大,每次約 90ms)。也沒有篇數上限;單次 timeout 20 秒,最壞情形更糟。
最小重現(臨時目錄,我已跑過):建 400 篇 `type: issue / status: open / summary: |-\n  KEY:a`,commit,再用 sed 把每篇 open 改 resolved,`git add -A`,然後 `time python3.14 scripts/lumos note-shape --staged`。舊版(e80705c4)real 3.9s,新版(2f807142)real 78s。若改成只改 `updated:` 的 400 篇,同樣要跑 800 次 git show 才發現狀態沒變。
建議:先用 `git diff --cached --name-only -z --diff-filter=M -G'^status:' -- <vault>` 把狀態行有動的才留下(少一個量級),或改用 `git cat-file --batch`,並加篇數上限。
file: `scripts/lumos:32358`(呼叫點 `_ns_close_summary_hints(root, staged, base_where, vault_rel)`)

## F2 提示對「狀態有引號」與「改名同時改狀態」會漏報,跟 drift scan 的 c7 不一致
severity: minor
blocking: 否 — 只提醒、不擋;漏報而已,存量掃描還是會抓到
引句:「    st = next((ln.split(":", 1)[1].strip() for ln in lines[1:e] if ln.startswith("status:")), None)」
引句:「    r = _lens_git(root, "diff", "--cached", "--name-only", "-z", "--diff-filter=M", "--", vault_rel, binary=True)」
走法一:`status: "resolved"`(帶引號)在這裡取到字串 `"resolved"`(含引號),不在 `_DRIFT_SETTLED`,所以不提醒;但同一篇提交後 `drift scan` 把它判成已收尾並列出 c7。我在臨時 repo 實測:暫存把 quoted.md 從 open 改成 `"resolved"`,提醒清單沒有它,提交後 scan 出 `Issues/quoted.md:5 DECISION:尚未裁定`(c7)。兩處判狀態不是同一支(提醒手拆 `split(":")`,scan 走 `_drift_str`/frontmatter 解析)。
走法二:`--diff-filter=M` 排除了 R。git 預設偵測改名,「改名且同時改成收尾值」(`ren.md`→`ren2.md`,內容相似 79%)顯示為 R079,不在清單內,實測沒提醒。
建議:狀態值用跟 c7 同一支解析(去引號);篩選改 `--diff-filter=MR` 並對 R 用舊路徑讀 base。

## F3 `drift fix --kind c7` 的錯誤訊息沒指向修法
severity: minor
blocking: 否 — 只是引導不足,掃描表與 doctor 都已印 summary-line 修法
引句:「    if kind == "c7":」
走法:c7 刻意沒有 fix 路徑(`_DRIFT_FIX_KINDS` 沒加)。我實測 `lumos drift fix X 1 --kind c7` 回「擋下:--kind 只能是 c1/c2/c3/c4/c5/c6/count」,沒說 c7 要手改、改用 `lumos summary-line`;c6 以外的 probe 種類在 `_drift_fix_args_err` 有專屬訊息,c7 沒有。`drift ack --kind c7` 可用:`_DRIFT_KINDS` 含 c7、`_drift_ack_line_err` 對非 retire/probe 只驗行非空,已實測不壞(非綁定種類,不記 related)。
file: `scripts/lumos:37060`

## F4 c7 在本 repo 自掃就有誤報:待定詞出現在「說明詞語」或歷史句而非現況
severity: minor
blocking: 否 — 只列不擋,且推送時只對這次碰到的筆記列出
引句:「            for no, ln, reg in _drift_pending_lines(text) if reg == "summary" and _drift_pending_clauses(ln)]」
走法:我在乾淨 clone(2f807142)跑 `lumos drift scan`,c7 共 4 筆:`Projects/c6不看連結標題裡的待定詞_計劃.md:15` 是 WHY 行描述「這句在說還沒做」(用詞被提及而不是在待定,只有全形引號才被遮);`Systems/autonomous-iteration-loop.md:24` 的「未處置」是名詞描述歷史修理;`Systems/verification-rot-eval.md` 是已 superseded 的設計筆記。4 筆中至少 2 筆不是「結案時忘了改摘要」。c6 對已收尾正文不看正是怕這種歷史句,c7 對摘要不分前綴(WHY/PITFALL 本來就寫歷史)全收。建議在 `RETIRE-IF` 裡明列誤報比例門檻,或只看 KEY/DECISION/FACT 這類現況前綴。
file: `docs/lumos-toolchain-knowledge/Projects/c6不看連結標題裡的待定詞_計劃.md:15`

## 其他逐項已讀、無 finding
- 沒有 summary 欄:`_ns_status_summary` 的 summary 清單為空,`and nsum` 擋掉,不提醒;實測 nosum.md 不提醒。引句:「        if nst in _DRIFT_SETTLED and ost not in _DRIFT_SETTLED and osum == nsum and nsum:」
- 單行 summary 值:`_drift_pending_lines` 有收單行值,提醒會連 `summary:` 前綴一起印(外觀瑕疵,不影響判定)。
- 中文與含空白路徑:`-z` 加 `os.fsdecode`,實測 `Issues/中文`、`Issues/sp ace` 都能列。
- 尾端空白 `status: resolved   `:有 `.strip()`,實測有列。
- 首次提交沒有 HEAD:`base_where` 為 None,`if not base_where: return []`,不提醒。合併中:以 HEAD(第一父)為底,行為同一般。
- `_lens_git` 回 None / returncode 非 0:在 hits 內 `continue` 或 return [],不丟例外;`_drift_fm_end` 回 0 → `(None, None)`,`nst in _DRIFT_SETTLED` 為 False。外層另有 `try/except` 只印一句,rc 不動。
- 種類表:Grep 全檔,`_DRIFT_KINDS` / `_DRIFT_KIND_NAMES` / `_DRIFT_SCAN_KINDS`(自動帶 c7)/ doctor Z 迴圈 / scan 統計 / `_drift_print_findings` 都已含 c7;推送檢查 `must` 只收 c1,c7 落在 `listed`(只列不擋)。`_DRIFT_FIX_KINDS`、`_DRIFT_BOUND_KINDS` 刻意不含 c7,未知種類路徑無壞。
- 同一篇多行待定:`_drift_c7` 一行一筆,各行各自可 ack;決策欄位(decisions)不看,屬設計範圍。
- 與否定現況句、標籤提醒的先後:兩者只看這次「新寫」的行,而 c7 提醒要求摘要逐字沒變,所以同一行不會被兩則提醒各列一次;同一篇可能因為正文新寫句被否定提醒、又因摘要沒動被這則列,是不同的行,不算重複。
- 時間:只在 F1 所述的量;不可逆:無寫入、無帳,純 stderr。
- 圖譜鏡頭:本次沒附固定席筆記(鏡頭超時),依派工詞不逐條答;角色卡未附。

總結:除了大量暫存時的 git 呼叫量(F1)需修之外,邏輯本身在各邊界輸入上穩,其餘僅是漏報與誤報的小瑕疵。
