severity: major

# 代碼審 r2(通才2-opus):筆記形狀擋 r1 修正差異

範圍:r2-delta.patch 逐 hunk 讀完;需要上下文時對照 r2-snapshot.patch 與 clone 裡的 scripts/lumos。所有重現都在 scratchpad/r2g2 底下、用測試檔自己的輔助函式 `_ns_repo` 在臨時 repo 跑;對照組是同一段重現改跑 87e7feee(修正前)的 lumos。

## F1 `[src:…]` 豁免套到所有筆記,任何筆記都能用它夾帶程式行號,而且沒有別的守衛在驗
severity: major
blocking: 是 —— 這道閘的第一條規則(新寫的程式行號引用要擋)用一種現成、還被鼓勵的寫法就能完全繞過,修正前會擋,是這批修正新開的洞
引句:「scan = _NS_SRC_MARK_RE.sub(" ", text)」

- 豁免的理由寫的是「歸重建守衛(Check J)驗」,可是 Check J 只看帶 `regen` 欄位的筆記、而且只看 summary(`scripts/lumos:4581` 那一段:沒有 regen 就直接 return)。刪 `[src:]` 這件事卻對每一篇筆記、每一個區塊都做,正文也算。
- 會自然發生:`_CTX_SRC_RE` 把 `[src:` 算成 WHY 行的出處(`scripts/lumos:2891`),所以寫 WHY 的人(或 AI)本來就被引導去寫 `[src:路徑:行號]`;被這道閘擋了之後,換成 `[src:]` 就過。
- 重現(scratchpad/r2g2/repro1.py、repro2.py):一般筆記(沒有 regen)正文寫 `見 [src:src/a.py:5]` → rc0;summary 寫 `WHY:門檻這樣定是因為 [src:src/a.py:5]` → rc0;修正前兩者都是 rc1。再把行號寫成超出檔長的 `[src:src/a.py:999]` 提交進去,`lumos lint Systems/A` 回「0 問題」——沒有任何一道在驗它。
- 改法:只有筆記帶 `regen` 欄位(而且在 summary 裡)時才把 `[src:]` 拿掉;其他筆記照一般行號引用判。

## F2 `@` 後面只要有「.」就不當釘版本:`@v1.2.3` 這類標籤、甚至 `@x.` 都讓行號引用直接過
severity: major
blocking: 是 —— [S2] 寫明「標籤…應照樣擋」,這批修正讓最常見的標籤寫法(帶點的版本號)從擋下變成放行,而且不會報「釘版本不合法」
引句:「if "@" in last and "." not in last.rsplit("@", 1)[1]:」

- 走一遍:`src/a.py@v1.2.3:5` 的最後一段是 `a.py@v1.2.3`,`@` 後面有點,所以不切開。token 變成 `src/a.py@v1.2.3`,這個路徑不在檔案清單裡 → `_ns_is_code` 回假 → 程式行號引用這條規則不成立。它也沒進 pins,所以「釘版本不合法」這條也不會觸發。
- 重現(repro1.py,同一個臨時 repo 打了 `v1.2.3` 和 `v1` 兩個標籤):
  - `` `src/a.py@v1.2.3:5` `` 修正後 rc0,修正前 rc1
  - 裸寫 `src/a.py@v1.2.3:5` 修正後 rc0,修正前 rc1
  - `` `src/a.py@x.:5` `` 修正後 rc0,修正前 rc1
  - `` `src/a.py@v1:5` `` 兩邊都是 rc1,這組是對照
- 同一類、而且修正前就有的:`` `src/a.py@origin/main:5` `` 兩邊都是 rc0。`@` 後面帶斜線,最後一段看不到 `@`,token 變成不存在的路徑,結果就被放過。這正是 S2 要擋的會移動的參照。
- 改法:不要用「有沒有點」來猜。`@` 左邊那段路徑在被檢查的版本裡存在,就當成釘版本(`icon@2x.png` 本身存在,所以不會切錯)。要是整段 token 本身就是一支存在的檔,才照檔名處理。測試補 `@v1.2.3` 和 `@origin/main` 兩個案例。

## F3 doctor 事後掃描的 200 上限沿第一個上一版往回數,在合併式歷史裡會退到上線點之前,把舊帳當成「繞過推上去的」列出來
severity: major
blocking: 是 —— 新加的上限在常見的 PR 合併工作流裡必然觸發,每次 doctor 都會把上線前的舊內容誤報成 --no-verify 繞過,訊息還宣稱「只看最近 200 個」
引句:「b2 = _lens_full_sha(root, f"{tip}~{_NS_DOCTOR_SCAN_CAP}")」

- `rev-list --count gl..tip` 數的是所有提交,包括合併進來的分支。`tip~200` 卻只沿第一個上一版往回走。PR 合併的歷史裡,前者超過 200 時,主線上距離上線點可能才十幾步,所以 `tip~200` 會落在上線點之前。`_note_shape_eval` 本身不會截到上線點(截斷只在 `cmd_note_shape` 裡做),所以上線點之前新增的行全部進了掃描。
- 重現(scratchpad/r2g2/repro_cap.py):
  1. 上線點之前有 205 個空提交,再加一個提交寫下舊帳 `src/a.py:5`,接著提交上線點。
  2. 開一個分支做 205 個提交,用 --no-ff 合回主線,推上遠端。
  3. 跑 `lumos doctor`,印出「已推上遠端(origin/main)卻違反筆記形狀擋的新增行 1 處(多半是 --no-verify 繞過):docs/kg-knowledge/Systems/A.md:18 程式行號引用 `src/a.py:5`」。
  4. 對照:`note-shape --diff <空樹>..HEAD` 截到上線點之後是 rc0,證明那一行確實是上線前的舊帳。
- 改法:`b2` 要是上線點的後代(`merge-base --is-ancestor gl b2`)才用它,不然就維持 gl。或者改用 `rev-list --max-count=200 gl..tip` 拿到的邊界當起點。

## F4 只有連結的指路行豁免:別名裡可以夾帶現況;全形逗號反而會誤擋
severity: minor
blocking: 否 —— 要刻意把現況寫進 wikilink 別名才繞得過;誤擋那半有 LUMOS_SKIP 可以逃
引句:「_NS_POINTER_ONLY_RE = re.compile(r"^(?:\s*(?:\[\[[^\]]+\]\]|見|→|,|,|、|\||｜)\s*)*$")」

- `[^\]]+` 會把 `[[目標|別名]]` 的別名整段吃進去,別名裡寫什麼都行。`DEP:[[Systems/Billing|扣款門檻 180 秒、重試 3 次]]` 修正後 rc0、修正前 rc1;`FACT:[[A|目前只支援三種付款方式]]` 也是 rc0。而且豁免同時套到了 FACT,不只設計紀錄說的骨架 FLOW/DEP。
- 正則裡寫了兩個半形逗號(逐字元看是 0x2c、0x2c),漏了全形「,」(U+FF0C)。`DEP:[[A]]` 後面接全形逗號再接 `[[Billing]]` 的寫法會被擋(rc1),同樣內容用半形逗號或空白隔開則是 rc0。中文筆記習慣用全形逗號。
- 改法:連結內容裡不准有 `|`,或者要求別名等於目標的最後一段;把重複的那個逗號換成全形逗號。

## F5 單一檔名的同名判定改成先讀每一支沒有副檔名的檔,終點不是 HEAD 時一支開一個 git 行程
severity: minor
blocking: 否 —— 只是變慢,判定結果不受影響;在這個 repo(14 支沒有副檔名的檔)感覺不到
引句:「if _nodehome_code_kind(p) is not None and _ns_is_code(p, reader, files):」

- `by_name` 在 `_note_shape_eval` 一開頭就對每一支沒有副檔名的檔(LICENSE、Makefile、.gitignore、fixtures…)呼叫 `_ns_is_code`,不管這次有沒有 `檔名:行號` 的候選、甚至有沒有改到筆記都一樣。reader 只有在終點等於 HEAD、而且檔案跟磁碟一致時才讀磁碟,其他情況每一支都跑一次 `git show`。會走到這條路的情況:doctor 的事後掃描(本機有還沒推的提交時,終點是上游而不是 HEAD,這正是「收工跑 doctor」的常態)、推送目前沒切出來的分支。
- 量測(scratchpad/r2g2/repro_perf.py,500 支沒有副檔名的檔,終點不是 HEAD):修正後 11.7 秒,修正前 0.8 秒。
- 改法:有單一檔名候選時才建 by_name(延後算);讀內容改用已經有的 `_nodehome_cat_blobs` 一次批次讀完。

## F6 CI 那一步的註解和計劃的做法段還寫著「排除其他遠端分支」,但 CI 只在推 main 時跑,現在那兩行等於沒作用
severity: minor
blocking: 否 —— 行為上沒有漏查(沒排除任何東西只會查得更多),問題是維護的人會照註解誤判範圍
引句:「git update-ref -d "refs/remotes/origin/$BRANCH" || true」

- `.github/workflows/ci.yml:3` 的觸發條件只有 push 到 main,所以 BRANCH 一定是 main。這一行刪掉 origin/main 之後,`_ns_mainline_refs` 找不到任何主線參照,等於不排除任何提交;前面那個「抓所有遠端分支」的 fetch 也沒有用了。可是 `.github/workflows/ci.yml:123` 的註解還寫「note-shape 只查『不在任何其他遠端分支上』的提交」;計劃〈做法〉的 CI 那一條(`docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:34`)也還是舊說法,只有新加的〈代碼審修正紀錄〉講了新規則。
- 改法:改註解,並在計劃〈做法〉那一條加註「代碼審 r1 後改成只排除主線」。消費專案的 CI 可能也對 PR 分支觸發,所以這兩行要不要留,在計劃裡寫清楚理由。

## F7 doctor 在 --ci 不跑事後掃描、以及 200 上限,兩者都沒有測試
severity: minor
blocking: 否 —— 這兩段是效能保護,現在的行為是對的,只是被改壞時沒有東西會翻紅
引句:「for _ln in _note_shape_doctor_lines(_vault_repo_root(env), env.vault, ci=ci):」

- 突變實測:把 `if ci:` 改成 `if False:` 之後,`t_doctor_note_shape_ci_and_bypass_scan` 仍然全綠(2 passed)。上限那段也沒有任何測試會走到(F3 的問題就是這樣沒被發現的)。
- 改法:加一條 `doctor --ci` 不列事後掃描的斷言;再加一條合併式歷史超過上限的案例,正好也把 F3 釘住。

## 測試鏡頭(新加的回歸測試與加強的兩支)

在臨時複本(scratchpad/r2g2/mut)逐一把修正改回原樣,清掉 __pycache__ 再跑。**以下全部會翻紅,是真的在守**:

| 改回原樣的地方 | 翻紅的斷言 |
|---|---|
| 呼叫 git 時不關路徑引號 | ①② 中文檔名 |
| 範圍改回排除所有遠端分支 | ③ |
| 不去掉檔頭尾端的 TAB | ① 含空白的檔名 |
| 同名判定不看 #! | ⑨ |
| BOM 改回用 utf-8 解碼 | ⑧ |
| 不刪 `[src:]` | ⑩ |
| 拿掉指路行豁免 | ④ |
| 拿掉 warned 那筆帳 | ⑪ |
| 單一檔名的釘版本不驗 | ⑥ |
| 不存在的路徑也驗釘版本 | ⑥ |
| `@` 改回一律切開 | ⑤ |
| 拿掉主線排除 | 合併測試 ③ |
| refcheck 不帶 at_sha | 加強的釘版本測試 ② |
| diff 改成 --no-renames | 加強的改名測試 ② |

另外,把「釘版本只進 pins、不進 full」改回原樣,會由釘版本測試的「合法釘版本放行」和 refcheck 那兩條斷言翻紅。

沒守到的地方:
- decisions 結構鍵的豁免,拔掉後全綠。這是修正前就有的缺口,不列為 finding。
- F7 講的 doctor 那兩段。

小瑕疵:回歸測試 ⑤ 有一行 `note = kb.parent.parent.parent / "x.md"`,下一行馬上被覆寫,是死碼。

## 圖譜鏡頭(固定席,分組判)
- **Issues/code-loop守衛main-direct盲區**:事故是用 merge-base..HEAD 算範圍時,直接在 main 上提交會漏查。note-shape 推送前用的是「遠端版本..本機版本」,不走 merge-base,不會重演。CI 在 main 首推、或舊版本抓不到時退回上線點,也不會漏查。已讀,無 finding。
- **Systems/lumos-refcheck、Systems/design-loop(G1 錨)**:共用的抽取器有兩處改動:釘版本不再進 full、`@` 的切法改了。refcheck 對合法釘版本和 `icon@2x.png` 都有突變實測守住;帶點的標籤在 refcheck 會判成不存在的檔,跟修正前結果一樣。問題在 note-shape 那一側,見 F2。lumos-refcheck 摘要的 FLOW 行沒寫釘版本解析這一步。它只是線索、不算合約,不另外開 finding。
- **Systems/每支檔有家、節點範圍與索引守衛**:`_nodehome_*` 本身沒改。每支檔有家拿到的仍是兩欄,帶 `@` 的檔名現在不會被切錯,是改善。已讀,無 finding。
- **Systems/測試假綠形態(★INVARIANT★:還原翻紅要有「現場真的成立」的前置斷言)**:新加的豁免類斷言(⑩④⑥)都用突變證明過,拿掉豁免就會擋,現場成立。見上方測試鏡頭。
- **Systems/reversibility-governance-ledger、Issues/治理帳多個寫入者都沒上鎖**:warn 模式多了 warned 寫帳。同一條違規在提交前記一筆、推送前又記一筆,帳本會重複。這是量的雜訊,沒有正確性問題,不列 finding。
- **Systems/lumos-cli-lifecycle、anchor-integrity、bound-tests-gate、canary-audit、guard-kill、授權與歸屬、slim-* 三篇、check-r / check-t、cochange-guard、lumos-deinit、doctor-irreversible-hint、pitfalls-code-loop、loop-convergence-recording、core-invariant-baseline、judge-severity-gate,以及雙向門放行、規格落成可驗收條件、逃逸自動記三份計劃**:這批差異沒碰到它們管的程式段。doctor 開頭多一個 ci 參數,只影響筆記形狀擋那一段。已讀,無 finding。

## 其餘 hunk
- CI 錯誤標註:在 `a || { rc=$?; … }` 裡,`rc=$?` 拿到的確實是左邊那個指令的結束碼。已讀,無 finding。
- `_ns_regions` 改用 split_frontmatter:`end = len(fm) + 1` 正好對到收尾那行;開頭欄位沒關時回傳全部 other,行為跟以前相同。已讀,無 finding。
- BOM 改用 utf-8-sig:已讀,無 finding。
- 設定資料夾是捷徑的防護:已讀,無 finding。
- 文件同步(AGENTS / CLAUDE / 範本 / skill 三檔 / ARCHITECTURE 的命令數):已讀,無 finding。

總結:修正大多正確,而且有突變證明測試守得住;但有三條 blocking。`[src:]` 豁免(F1)和 `@` 後面帶點就不當釘版本(F2),是這批修正自己開出的放行洞;doctor 的 200 上限(F3)在合併式歷史會把上線前的舊帳誤報成繞過。
