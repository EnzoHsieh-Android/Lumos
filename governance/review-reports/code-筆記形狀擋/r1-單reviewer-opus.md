severity: blocker

# 代碼審 r1(單 reviewer,opus)——筆記形狀擋 `lumos note-shape`

範圍:整份 r1-code.patch(1227 行,12 支檔)逐 hunk 讀過。實驗一律在 scratchpad 底下另開的臨時 repo 跑(nsexp1–4、nsimp 是 `git clone --shared` 出來的拋棄式複本),沒有改 clone-ns 裡的任何檔。

## F1 中文檔名與含空白檔名的筆記完全不查(提交前、推送前、CI 三處都漏)

severity: blocker
blocking: 是 —— 本 repo 567 篇筆記裡有 498 篇是非 ASCII 檔名,在預設 git 設定下這道閘對它們等於沒裝

引句:「path = nfc(p[2:]) if p.startswith("b/") else None」

走一遍:`_ns_diff` 經 `_nodehome_git` 呼叫 `_lens_git(binary=True)`,沒有帶 `quote=True`(見 `scripts/lumos:27936`),所以 git 用預設的 `core.quotePath=true`。中文路徑的檔頭會印成 `+++ "b/docs/.../\344\270\255\346\226\207.md"`,開頭是 `"`、不是 `b/`,於是 path=None,那個檔新增的每一行都被跳過。含空白的檔名也一樣漏:git 會在 `+++ b/a b.md` 後面補一個 TAB,path 變成 `...a b.md\t`,提交前那條 `.endswith(".md")` 過濾就把它丟掉。
影響到三處:
- 提交前:`added` 是空的 → rc0。
- 推送前與 CI:`_ns_range_added` 收集 texts 時也走同一支解析,texts 是空的 → 沒有任何一行會命中。CI 在 ubuntu 上用的就是預設設定。
- 新程式檔喚醒那段的 `git grep` 輸出同樣會被引號包起來,`p.endswith(".md")` 不成立 → 也漏。

最小重現(臨時 repo,兩篇內容完全一樣,只差檔名):
```
$ python3 <clone>/scripts/lumos note-shape --staged --repo nsexp1
擋下:…
  docs/demo-knowledge/Systems/ascii.md:5  現況描述沒寫來源 FACT:門檻是 30…
  docs/demo-knowledge/Systems/ascii.md:8  程式行號引用 `src/app.py:12`…
rc=1          ← 中文.md 有同樣兩行,卻一行都沒列
$ git commit (只留 中文.md 的改動); lumos note-shape --diff HEAD~1..HEAD → rc=0
$ git config core.quotePath false; lumos note-shape --diff HEAD~1..HEAD → rc=1(中文.md:5、:8 都擋)
含空白檔名:"Systems/a b.md" 加 `src/app.py:1` → rc=0;改名成 ab.md → rc=1
```
測試全綠多半是因為測試筆記都用 ASCII 檔名。修法是 `_ns_diff` 和喚醒那段的 grep 都改帶 `-c core.quotePath=false`(`_lens_git(..., quote=True)`),並且去掉檔頭尾端的 TAB;或者直接用 `scripts/lumos:18410` 那支現成的解引號函式。要補一條中文檔名加空白檔名的測試。

## F2 「已在遠端追蹤分支上的提交不重查」讓 CI 這道後盾整個能被繞過

severity: major
blocking: 是 —— 把有違規的提交先用 --no-verify 推到任何一條別的分支,再推 main,CI 會是綠的

引句:「rl += ["--not", "--remotes"]」
引句:「git update-ref -d "refs/remotes/origin/$BRANCH" || true」

走一遍:CI 只在 push 到 main 時觸發(`.github/workflows/ci.yml:4-6`),而 note-shape 這一步只在 push 事件跑。也就是說,推到非 main 分支的提交,CI 從來沒查過。可是 `_ns_range_added` 把「在任何一條遠端分支上」的提交全部排除,背後假設是「推上去時已經查過」。這個假設對 `--no-verify` 推到別的分支的提交不成立——而這一步存在的理由正是接住 `--no-verify`。本機推送前的檢查也一樣:只要提交已經在某條遠端分支上,就不會重查。
最小重現(臨時 bare remote,工作目錄沒裝 hook,效果等同 --no-verify):
```
init(含 pre-commit 標記)→ push main;checkout -b tmp;筆記加 `src/app.py:12`;push origin tmp
main ff 到 tmp、push main;模擬 CI:clone → fetch 全部分支 → update-ref -d refs/remotes/origin/main
$ lumos note-shape --diff "$BEFORE..$SHA" --repo .      → CI rc=0
$ git update-ref -d refs/remotes/origin/tmp; 再跑一次     → control rc=1
```
GitHub 合併 PR 的流程也會碰到:PR 事件本來就跳過這一步;合併後 main 那次 CI 跑的時候,只要功能分支還沒刪,它的提交就被排除。建議 CI 只排除「main 已經有的」,也就是 `--not origin/main` 或 BEFORE,不排除全部遠端分支;或者要求這一步在 PR 事件也跑。

## F3 工具自己產生的骨架會被自己擋:`lumos new system` 產出的 FLOW:/DEP: 空行,提交時被判成沒寫來源

severity: major
blocking: 是 —— 每支檔有家要求新程式檔先開一篇家,而 `lumos new system` 產出的節點一提交就被這道擋下

引句:「_NOTE_SHAPE_PREFIX_RULES = {k: _CONTEXT_MARKER_RULES["FACT"] for k in ("FACT", "FLOW", "DEP")}」

走一遍:`lumos new system` 的樣板把 `summary: |-\n  FLOW:\n  KEY:\n  DEP:\n  TEST:` 寫進開頭欄位(`scripts/lumos:15771`)。這四行在提交前全是新增行,而且都落在 summary 區塊。`FLOW:`、`DEP:` 後面是空字串,`_CTX_SOURCE_RE.search("")` 不成立,於是擋下。另外,skill 的 `reference.md` 還留著「`DEP:` 依賴模組(用 wikilink)`[[Billing]][[Inventory]]`」「FLOW/DEP 只寫指針」這兩條舊指示(diff 只改了 FACT 那一列與 Systems 那一條,本身沒碰這兩處)。照 skill 寫的 wikilink DEP 行一樣會被擋。Verification 裡寫到「共用假筆記摘要原本寫 FLOW:x,改成 KEY:x」,那是把測試夾具改掉來繞開這件事,不是修好它。
最小重現(nsimp 拋棄式複本):
```
$ lumos new system probe-node --code scripts/lumos --responsibility "負責探針測試的筆記內容,不負責任何別的東西"
$ git add …/Systems/probe-node.md; lumos note-shape --staged --repo .
擋下:…
  docs/lumos-toolchain-knowledge/Systems/probe-node.md:14  現況描述沒寫來源 FLOW::…
  docs/lumos-toolchain-knowledge/Systems/probe-node.md:16  現況描述沒寫來源 DEP::…
rc=1
```
(中文節點名目前因為 F1 被漏過;F1 一修好,每一篇新節點都會中。)要嘛前綴後面沒有內容就不判,要嘛同一次改掉樣板和 skill 裡的 FLOW/DEP 指示。

## F4 共用抽取器預設就解析 `@`,檔名本身含 `@` 的合法引用在 refcheck 與 G1 閘被判成不存在

severity: major
blocking: 是 —— 這違反了 docstring 宣稱的「既有使用者行為不變」,而且落在設計審 G1 這道硬閘上

引句:「if "@" in token.rsplit("/", 1)[-1]:」

走一遍:只要路徑最後一段含 `@`,就一律切成「路徑+釘的提交」,不管 `@` 後面是不是提交編號。`_refcheck_scan` 把每個 pin 都拿去 `_pin_commit` 驗,`2x.png`、`v2.sh` 都不是 12 位以上的十六進位,結果回 `missing`,原本那條正常的引用也因為 `(token,line) in pinned` 被跳過。`loop status --gate` 與 settle 的 G1 對 missing 直接判失敗(`scripts/lumos:9405-9410`、`scripts/lumos:10205-10212`)。iOS、Flutter 專案的 `Icon-App-20x20@2x.png` 這類檔名是常態。每支檔有家(`scripts/lumos:22672`)也受影響:`lib/foo@2.dart` 會被截成 `lib/foo`,不再算寫了那支檔。
最小重現(同一段文字,分別用 base 122a85fc 與這份 patch 的 scripts/lumos 跑 `_refcheck_scan`):
```
text = "see `assets/icon@2x.png` and `scripts/run@v2.sh:2`"   (兩支檔都真的存在)
base : [{'token':'assets/icon@2x.png','status':'ok'}, {'token':'scripts/run@v2.sh','line':'2','status':'ok','excerpt':'b'}], 0, 0, 2
patch: [{'token':'assets/icon@2x.png','status':'missing'}, {'token':'scripts/run@v2.sh','line':'2','status':'missing'}], 2, 0, 0
```
建議 pin 只在 `@` 後面符合十六進位或像提交的形狀時才切開,不然整串照舊當路徑;或者先看「整串是不是一支存在的檔」再決定要不要切。

## F5 doctor 的事後繞過掃描沒有上限,推送前的 `doctor --ci` 會隨提交數線性變慢

severity: major
blocking: 是 —— 推送前的掛鉤每次都跑 doctor --ci,這段每過一天就更慢,而且沒有任何上限

引句:「res = _note_shape_eval(root, False, gl, tip, vault_rel, exclude_remote=False)」

走一遍:每跑一次 doctor,都會對「上線點..上游」的每一個提交各開一次 `git diff`(`_ns_range_added` 逐提交迴圈),而且 `exclude_remote=False`,等於整段重算。本 repo 近三個月有 2072 個提交(每天約 23 個)。推送前掛鉤的註解記的 doctor 耗時是 1.1 秒(`scripts/hooks/pre-push:167`),`doctor --ci` 在推送前和 CI 都會跑(`scripts/hooks/pre-push:179-181`、`ci.yml:96-97`)。
量測(clone-ns 真歷史,直接呼叫 `_note_shape_eval`):
```
100 commits: 2.1 s
500 commits: 9.4 s        (約每個提交 19 ms)
```
照這個速度,上線一個月後約 +13 秒,三個月後約 +40 秒,而且每一次 doctor 都要付。建議只掃上一次 doctor 之後的新提交(記一個游標),或者設提交數上限並在截斷時講一句;至少別在 `--ci` 路徑上跑。

## F6 單一檔名加任意 `@` 就不查,短提交編號或 HEAD 釘版本都能過

severity: minor
blocking: 否 —— 這是釘版本合法性檢查的一個漏口,只影響單一檔名那一種寫法

引句:「if len(cands) == 1 and s is None and _ns_is_code(cands[0], reader, files):」

`singles` 裡只要帶了 pin(s 不是 None),就直接不處理,也沒送去 `_pin_commit` 驗。路徑寫法會照 S2 擋,單一檔名寫法卻整個放過:
```
`app.py:12`                   rc=1
`app.py@HEAD:12`              rc=0
`src/app.py@HEAD:12`          rc=1
`app.py@deadbeefdeadbeef:12`  rc=0   (不存在的提交)
```
AI 習慣寫 7 位短提交編號,`lumos@87e7fee:22760` 這種寫法很自然就會放行。應該跟路徑那段一樣走 `_pin_commit` 與 `_validate_repo_ref`。

## F7 單次跳過 `LUMOS_SKIP_NOTE_SHAPE=1` 在 CI 無效;被跳過的誤擋會讓 main 的 CI 紅,之後每次 doctor 也會一直唸

severity: minor
blocking: 否 —— 屬於設計層的一致性問題,不是程式錯;但紀律範本對使用者承諾「誤擋用它單次跳過」

引句:「if os.environ.get("LUMOS_SKIP_NOTE_SHAPE"):」

CI 那一步沒有任何跳過管道(`ci.yml` 新增那段)。本機提交和推送都帶了 env 跳過之後,同一段範圍在 CI 仍然 rc1。doctor 的繞過掃描(`exclude_remote=False`)也分不出「刻意跳過的誤擋」和「--no-verify 繞過」,會每次都列。要逃掉只剩兩條路:改寫那一行,或整個專案設 warn。計劃承認誤擋率沒量過(Verification〈沒驗到的〉),所以這個缺口遲早會碰到。建議讓治理帳裡的 skipped-env 事件(帶提交 sha)能被 CI 與 doctor 認得,或者在範本裡把「CI 仍會擋」寫明。

## F8 跟重建筆記的 `[src:路徑:行號]` 出處標記衝突,擋下訊息建議的改法又會被 Check J-c 擋

severity: minor
blocking: 否 —— 退一步寫成 `[src:路徑]`(不帶行號)兩道都能過

引句:「raws += [m.group(0) for m in _NODE_BARE_REF_RE.finditer(rest)]」

`[src:src/app.py:12]` 裡的 `src/app.py:12` 前面是冒號,不在 lookbehind 那個字元類裡,裸寫比對會抓到並判成程式行號引用(實測:摘要 `KEY:共用面:被 X 使用 [src:src/app.py:12]` → rc1)。skill `reference.md` 的〈重生守衛〉與〈考古還原〉兩處都明文教人寫 `[src:路徑:行號]`,diff 沒有同步改。照擋下訊息改成 `[src:src/app.py@<sha>:12]` 的話,`SRC_REF_RE`(`scripts/lumos:4283`)會把 `src/app.py@<sha>` 當成路徑,J-c 判不存在,兩道閘互相卡住。建議在 `[src:` 裡面豁免,或同一次改掉 skill 的寫法並讓 SRC_REF_RE 認得釘版本。

## F9 帶 BOM 的 UTF-8 筆記:整篇被當成正文,summary 的 FACT/FLOW/DEP 不查

severity: minor
blocking: 否 —— 只有存成帶 BOM 的筆記會漏,而且方向是漏擋

引句:「if not lines or lines[0].strip() != "---":」

`_note_shape_eval` 用 `b.decode("utf-8")` 解碼,不是 utf-8-sig,所以第一行是 `﻿---`。`strip()` 不會去掉 `﻿`,結果整篇都算 body,summary 規則根本不跑;frontmatter 裡的行反而被當正文查行號。repo 其他讀取器都用 utf-8-sig(例如 `_nodehome_parse_note`)。實測:內容相同的 b.md(帶 BOM)和 c.md(不帶),只有 c.md:4 被擋。

## 已讀,無 finding

- 兩支 hook 的接法:只認 rc1 為擋,其他非零放行,跟每支檔有家同型;pre-push 放在 `_hrange` 非空那個區塊裡、在 home check 之後。
- CLI 參數:--staged 與 --diff 互斥、兩個都沒給 rc2,形狀照抄 home check。
- 例外路徑:第一個提交(沒有 HEAD)實測 rc0;`_ns_became_code` 在 base=None 時退回空樹;doctor 那段有 try/except 包住。
- `_merge_new_lines` 從 `_nodehome_merge_wrote_new_lines` 拆出來:None 對應原本的 True,集合非空對應原本的 any(),語意相同。
- `_nodehome_golive` 和 `_nodehome_clamp_base` 加的 mark 參數預設 None,落回原本的標記,每支檔有家的行為不變。
- `context_marker_warnings` 的 rules 預設 None 時走原路徑(RULE 生命週期檢查照跑)。FACT 規則換成來源判定後,lint 對既有 9 行 FACT 會多出警告,但 lint 只唸不擋;我查過,沒有任何擋人的閘在數 `lumos lint` 的警告。
- `_KNOWN_GATES` 登記了 note-shape;淺層 clone 偵測、跳過時寫帳、放行不寫帳,都跟條款一致。
- 合併提交的判法:第二個上一版帶進來的行在 olds 裡找得到,不算新寫;判不了就退回跟第一個上一版比,偏向多查。
- 文件類 hunk(CLAUDE.md、AGENTS.md、紀律範本、INDEX.md、reference.md 的 FACT 列、兩篇新筆記、每支檔有家的鄰居段落):三份紀律區塊逐字一致。reference.md 的遺漏已記進 F3 與 F8。

## 圖譜鏡頭:固定席逐條判定(`lumos impact --diff 122a85fc..HEAD`,固定 29 席)

- **Systems/lumos-refcheck**(RISK·守衛面)——**受影響**。它的 FLOW 寫的是「剝:suffix(純數字才當行號)→須含/且首段=頂層目錄→…exists」,這次在中間插了 `@` 切分,含 `@` 的真檔被判 missing,見 F4。
- **Systems/design-loop**(INVARIANT)——**受影響**。G1 共用 `_refcheck_scan`,F4 的誤判會變成 G1 失敗。處置閘第五步的其他合約沒被碰到。
- **Systems/每支檔有家**——共用函式的預設行為不變(已讀段)。唯一的例外是 `_nodehome_refs` 走預設的 `@` 切分,帶 `@` 的程式檔會被截掉(F4)。新增的鄰居段落和事實相符。
- **Issues/code-loop守衛main-direct盲區**——note-shape 沒動 code-loop 的範圍算法,不影響那條宣稱。不過它是同一類盲區(main 直推加 CI 只在 main 觸發),F2 就是這個形狀。
- **Systems/anchor-integrity**(RISK)——diff 改了 pre-commit 和 pre-push 兩支被錨定的 hook。拋棄式複本跑 `anchor verify` 列出兩支 hook(加上 test_lumos.py)跟基準線不一致,diff 裡也沒有 `anchor approve` 的基準線更新。這是 wip 提交,推之前要記得核可,不開 finding。
- **Systems/reversibility-governance-ledger**——新閘名已登記進 `_KNOWN_GATES`,寫帳走 `_gate_event_or_warn`,不影響「gov 唯讀彙整、寫者分流」的宣稱。
- **Systems/lumos-cli-read**(INVARIANT)——search 與 Check P 的抽取不走新選項。bare 集合(`scripts/lumos:26661`)用的是 spans,不受影響。
- **Systems/節點範圍與索引守衛**(INVARIANT)——doctor 新加的是開頭提醒行,不是 [S5]/[S6]/[S7] 這類段落,沒有插進 [E3]..[H] 之間,段落順序合約不受影響;閘名登記照做了。
- **Systems/bound-tests-gate**、**Projects/雙向門放行_計劃**——pre-push 的測試範圍判定(`_SUITE_*`)沒動,note-shape 插在那段之前、跟它獨立,不影響。
- **Systems/lumos-cli-lifecycle**、**slim-install-安裝器**、**slim-get-一行安裝**、**slim-uninstall-一行卸載**(都是 INVARIANT)——這些合約講的是 sentinel 之間注入的 byte-equal 與冪等。diff 只改了紀律範本 sentinel 之間的內容,三份逐字一致,不碰注入機制,不影響。
- **Systems/授權與歸屬**(INVARIANT)——沒動 `_VENDORED_TOOLKIT` 和檔頭 SPDX,不影響。
- **Systems/測試假綠形態**(INVARIANT)——Verification 記了逐條改壞、看測試翻紅。前置斷言這一項沒辦法從 diff 驗(test_lumos.py 不在 patch 裡)。F1 正好是「現場走不到被測分支」的第④型:測試全用 ASCII 檔名,中文檔名那條路從來沒被執行過。
- **Systems/guard-kill**、**canary-audit**、**judge-severity-gate**、**core-invariant-baseline**、**loop-convergence-recording**、**pitfalls-code-loop**、**Projects/規格落成可驗收條件_計劃**、**Projects/逃逸自動記_計劃**——diff 沒碰它們的 rc 語意、帳本落盤、處置閘、基準線或 pitfalls 分級程式,不影響。
- **Systems/check-r-guard**、**check-t-sentinel**、**doctor-irreversible-hint**——doctor 只在開頭多印幾行提醒,不算 issues,沒動 Check R、T、H 的判定,不影響。
- **Systems/cochange-guard**、**lumos-deinit**——pre-commit 只在中間多一段,cochange 那段沒動;deinit 白名單沒動,不影響。

總結:max severity = blocker;blocking 5 條(F1 blocker;F2、F3、F4、F5 major),minor 4 條(F6–F9)。
