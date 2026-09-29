severity: major

# 代碼審 r1 正確性席(opus)——存量漂移防線 乙

審材:r1-snapshot.patch(ac5c7ccf..e8f17913)。重現腳本都放在 scratchpad/cy1/exp/(h.py 載入 clone-ns 的 scripts/lumos 與測試輔助;每支腳本自己 mktemp 建 repo,不動任何既有 repo)。七支新測試在 clone-ns 上各自跑過,全綠。

## F1 帶路徑的 symbol/test 指到沒有副檔名的程式檔(或指到另一類檔)時,條件永遠不成立,scan 也不列
severity: major
blocking: 是 — 工具鏈自己的主程式 scripts/lumos 上的 symbol 條件全部是死條件,寫的人和 scan 都看不出來
引句:「paths = sorted(p for p in self.files if _nodehome_code_kind(p) == "ext"」
file: `scripts/lumos:25808`

1. `_ProbeTree.corpus` 只收 `_nodehome_code_kind(p) == "ext"` 的檔。`scripts/lumos` 沒有副檔名,`_nodehome_code_kind` 回 `shebang?`,所以不會進語料。`one()` 帶路徑時做的是 `corpus.get(path)`:語料裡沒有這支檔就拿到 None,跳過後回 False。
2. 在 clone-ns HEAD 上實跑 `python3 scratchpad/cy1/exp/e8.py`,輸出:
   - `('symbol', 'scripts/lumos::_revisit_split') False`
   - `('symbol', '_revisit_split') False`(這支函式明明存在)
   - `('file', 'scripts/lumos') True`
   - 程式語料只有 32 支,scripts/lumos 不在裡面。
3. 推送判定照樣漏:e2.py 的 E2a 建了一個 repo,起點寫 `REVISIT:[when-symbol:scripts/tool::cmd_new][by:2099-12-31]`(scripts/tool 是有 `#!` 的 Python 檔),推送裡加上 `def cmd_new():`。`drift check` 回 `(0, '')`。drift scan 的 findings 與 problems 兩邊都是空的。
4. 同一個缺口也出現在:`[when-symbol:tests/helpers.py::make_fixture]` 指到測試檔,e1.py 實測 False;`[when-test:<非測試檔>::名稱]` 反過來也一樣。文法檢查放行,scan 的問題清單只查「指到資料夾」,這幾種都不查。
5. ⚠ 計劃第 2 節把 symbol 的語料寫成「`_nodehome_code_kind` 認得的副檔名」,但同一段又說「帶路徑就只在那支檔找」。作者指到的是一支存在的程式檔,工具卻判「永遠不成立」,期限 [by:] 到之前都沒人發現。而本 diff 的計劃新增了 REVISIT:2026-10-26,要把工具鏈的散文回頭條件改寫成條件式,最自然的寫法正是 `scripts/lumos::<函式>`。

## F2 程式檔被 .gitattributes 標成 -diff 時,候選篩選看不到新增行,條件翻轉的推送被放過
severity: major
blocking: 是 — 候選篩選漏掉條件真的翻轉的推送,等於靜默放行,違反〈做法〉第 0 節候選規則②
引句:「added = "\n".join(t for p, rows in _notelines_parse_added(d).items() if _nodehome_code_kind(p) == "ext"」
file: `scripts/lumos:25882`

1. `_probe_changes` 用 `_ns_diff`(`git diff -U0 -M --no-textconv`)抓新增行,沒帶 `--text`。檔案帶 `-diff` 或 `binary` 屬性時,git 只印「Binary files differ」,這支檔在 added_text 裡一行都沒有;而這種改動的狀態是 M 不是 A/D/R/C,`code_shape` 也是 False。
2. 重現(e2.py 的 E2b):`.gitattributes` 寫 `src/gen.py -diff`,起點的筆記寫 `REVISIT:[when-symbol:Foo][by:2099-12-31] …`,推送在 src/gen.py 加上 `class Foo:`。
   - `drift check` 回 `(0, '')`
   - 同一個終點直接評估 `_ProbeTree.one("symbol","Foo")` 是 True
   - `_probe_changes` 回 touched={'src/gen.py'}、added_text=''、code_shape=False
3. 結果是條件從不成立變成立,但這一行不是候選,不評估、也不擋。判定本身讀的是 cat-file、看得到內容,只有篩選看不到,所以兩者不一致。

## F3 條件式的要處理發現後面,印的是 c1 的修法(改預告句)
severity: minor
blocking: 否 — 只有提示文字錯,判定與 rc 都對
引句:「must.append({"kind": "probe", "path": p, "line": no, "text": tx, "related": [], "why": verdict})」
file: `scripts/lumos:26189`

1. `_drift_report_must` 只要 must 不是空的,就印「每一筆:把預告句手改成歷史說法(例:「為什麼還不做:」…)」。這次 probe 發現也進了 must。
2. e3.py 實跑(推送新增 src/runner.py,觸發 `[when-file:src/runner.py]`):輸出的 `[probe 回頭條件成立了] …` 後面緊接著叫人改預告句。條件式要的是「做掉待辦並刪掉或改寫這行,或 drift ack --kind probe」,給的修法是錯的。

## F4 lumos set 第③項:值原本就成立的也說成「因這次收尾成立」
severity: minor
blocking: 否 — 只列出不擋,但訊息內容不實
引句:「and new_status in {x.strip() for x in v.partition("=")[2].split("|")}]」
file: `scripts/lumos:25516`

1. 這裡只比「值裡有沒有新狀態」,沒看舊狀態在不在值裡。
2. e6.py:計劃 P 的 status 是 doing,Issue 寫 `REVISIT:[when-status:Projects/P_計劃=doing|done][by:2099-01-01]`,跑 `lumos set Projects/P_計劃 status done`,印出「回頭條件 Issues/I(第 6 行的 status 條件因這次收尾成立)」。但這條件在 doing 時就已成立,不是因為這次收尾。rtb 考卷 B3 的改寫就是 `=doing|done`,正好是這個形狀。

## F5 不是 git 專案的圖譜:純 status 條件在 scan 被列成「判不了(git 讀不出程式檔)」
severity: minor
blocking: 否 — scan 不擋,但成立的條件被藏起來,原因也寫錯
引句:「probs.append((p, no, tx, "判不了(git 讀不出程式檔)"))」
file: `scripts/lumos:25818`

1. `_ProbeTree.one` 一開頭就是 `if not self.ok: return None`,排在 status 分支前面。status 只要讀筆記、不需要 git;可是列不出樹時,連 status 也判成「判不了」。
2. e6.py 用 mkvault(不是 git 專案,甲的 scan 支援這種)寫 `[when-status:Projects/P_計劃=doing|done]`,P 當時是 doing,條件成立。drift scan --json 的 findings 是空的,problems 列「判不了(git 讀不出程式檔)」。

## F6 「這行是不是 REVISIT 只有一支判定」不成立:E5 餵的輸入跟另外兩層剝法不同
severity: minor
blocking: 否 — 只在雙反引號範例這種少見寫法上分岔,但筆記宣稱的單一判定跟實作不符
引句:「全庫只有一支判定(doctor E5、筆記形狀擋、筆記內容審都用它),各處自己判的話同一行會在一處算條件式、另一處算壞損」
file: `scripts/lumos:2017`
file: `scripts/lumos:3387`

1. E5 餵給 `_revisit_split` 的是 `_search_visible_lines` 的 probe,只剝 `INLINE_CODE_RE`。`_probe_lines`、`_ns_revisit_violations`、`_note_audit_items` 餵的是 `_strip_inline_markup`,會先剝雙反引號,遇到沒閉合的反引號就截斷。
2. e9.py:對這行 ``` ``REVISIT:[when-file:x.py][by:2020-01-01] 範例寫法`` ```
   - E5 的輸入變成 `REVISIT:[when-file:…]…`,判成 cond,doctor 真的印出「[E5] … 2020-01-01 範例寫法(逾 2463 天)」
   - `_probe_lines` 的輸入是空字串,判成 None,這行當範例不算
   - 同一行在 E5 被唸到期,在第一層、scan、Z 段卻不存在。換成日期式壞行(``` ``REVISIT:下次再看`` ```)時,E5 算壞損、第一層不擋。

## F7 文法放行、但照寫法永遠不會成立的值:`./` 開頭的路徑、`Type::method` 形式的符號
severity: minor
blocking: 否 — 有期限 [by:] 兜底,但 scan 與第一層都不提示
引句:「return (not p) or p.startswith("/") or ".." in p.split("/")」
file: `scripts/lumos:25700`

1. `[when-file:./scripts/lumos]` 通過 `_probe_bad_path`,但 `one()` 直接比 `v in self.files`,沒做正規化。e8.py 實測 `('file', './scripts/lumos') False`,`('file', 'scripts/lumos') True`。這個 repo 已有共用的 `_posix_norm`(去掉 ./、反斜線轉斜線),這裡沒用。
2. ⚠ `[when-symbol:Config::load]`(C++/Rust/PHP 常見寫法)照規格從最後一個 `::` 切成「路徑 Config、名稱 load」,Config 不是檔,永遠不成立,也不報錯。規格本身這樣定,但 scan 不列「路徑那段在樹上不存在」,寫的人不會知道。

## F8 計劃的考試結果列宣稱乙 5 題照改寫檔考過,但改寫檔有 3 題違反本 diff 強制的 [by:]
severity: minor
blocking: 否 — 考卷資料與文法規則對不上,判定碼沒錯
引句:「| 乙(2026-09-29,同上,probe 題照改寫檔) | 5(A7、B1–B4) | — | 0 | 0 / 0 | — | 1 |」

1. governance/eval/drift-exam/rtb-2026-09-28-probes.json(不在本 diff,來自 07e5bc96)裡,A7、B3、B4 的 rewrite 都沒帶 `[by:]`。本 diff 的第一層會擋「條件式沒帶期限」,所以這三條改寫自己過不了新閘。
2. 計劃第 3 節說「原文帶日期的(B1、B2)照原日期寫進 [by:]」,但考卷原文 B3 是 `REVISIT:2027-01-31 …`、B4 是 `REVISIT:2026-12-31 …`,兩題都帶日期,改寫時卻丟掉了。計劃與改寫檔互相矛盾。
3. 判定碼本身沒問題:我在 rtb-exam 上重跑 `drift exam --probes`,合計和計劃一致(擋到 8、點到 3、漏 0、誤列 1)。再攔下 `_drift_check_core` 看原因,5 題全是「這次推送讓條件成立了」,不是「新寫而已成立」,可見起點替換有生效。

## 已看,無 finding 的部分
- `_revisit_split` 對比 E5 原本判法(F6 另計):`- `/`* ` 的處理和舊版等價。新認得 `+ `、`1. `、`1) `、`> `、`-\t`,是規格明訂的擴大。`REVISIT:` 後有空白才接日期、或日期後緊接標點(例如 `2026-10-05;`),新舊版都算壞損。表格行新舊都排除。
- `_probe_parse`:標記之間的空白、期限寫兩次、期限不合法、沒有條件標記、`[by:]` 寫在前面(依規格算壞損),都照文法處理。
- 四種鍵:Python 的 def、async def、class、方法,帶型別的模組層指定,`==` 不算指定;其他語言整字比對;status 任一值與連結解析(路徑找不到時退回檔名主幹,跟 [[連結]] 一致)。這些新測試的案例都過,我另外補的邊界也沒有發現新問題(F1、F7 除外)。
- 「同一條」與改名對回:e4.py 跑了四種情況——筆記改名且同一次推送讓條件成立(擋);筆記改名但起點就已成立(不擋);只改期限並加列表記號(不擋);條件值多了頭尾空白(視為同一條、不擋)。結果都對。
- 候選篩選(F2 另計):條件標記全是「存在」型,只有新增行或 A/D/R 能把不成立翻成成立,所以不看刪除行不會漏。
- 起點是空樹:e7.py 直接呼叫 `_drift_check_core(root, None, …)`。已成立的那條依「新寫」算要處理,沒成立的不列,沒有例外。
- 判不了的路徑:`_probe_changes`、`_probe_prepare` 在 git 失敗時回原因,`_ProbeTree` 不可用時回 None 並列成判不了,都照 [S2] 算要處理(非 git 那一種見 F5)。
- 筆記形狀擋的 `keep_other`:other 區塊的行只進 `_ns_revisit_violations`,不進 `_ns_check_line`;筆記內容審沒傳這個選項,行為不變。
- 筆記內容審排除條件式、日期式照審:測試與程式一致。
- exam probe 的換行與替換:`_swap` 靠 strip 比對,縮排保留;CRLF 的 `\r` 被 strip 吃掉,不影響比對;起點、終點各自替換。rtb 實考已確認替換有生效。

## 圖譜鏡頭(LUMOS-IMPACT ac5c7ccf..e8f17913)
派工詞沒有附上固定席筆記全文,我在 --shared clone 上自己跑了 `lumos impact --diff`,逐篇判如下:
- Projects/存量漂移防線_計劃:本次兌現的規格。F1、F2 違反第 0 節候選規則②和第 2 節「帶路徑就只在那支檔找」的本意;F8 是這篇筆記跟考卷之間的不一致。
- Systems/存量漂移守衛:新加的「只有一支判定」段落被 F6 反證;其餘宣稱(同一條只看條件標記、新寫而已成立也擋)都實測成立。
- Systems/筆記內容閘:新 WHY 行(新寫的 REVISIT 在第一層擋、共用判定、keep_other 只給這一層)跟程式一致;共用判定的前處理見 F6。
- Systems/筆記內容審:「條件式不送審、日期式照審」成立,不影響它既有的讀不到放行語意。
- Systems/lumos-cli-read(d1:讀指令不寫帳):scan 新增的 probe 部分沒有寫帳、也沒寫檔(我跑完 exam 與 scan 後查 git status,沒有新的變動),不影響。
- Systems/lumos-cli-write:set 的第③項只多印幾行、不改寫入,改狀態照舊成功;訊息的準確度見 F4。
- 其餘固定席(guard-kill、授權與歸屬、測試假綠形態、design-loop、pitfalls-code-loop、lumos-cli-lifecycle、loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛、check-r-guard、doctor-irreversible-hint、check-t-sentinel、lumos-deinit、cochange-guard、lumos-refcheck、bound-tests-gate、canary-audit、slim-get/install/uninstall、雙向門放行、規格落成可驗收條件、逃逸自動記、core-invariant-baseline、judge-severity-gate):這次的改動都落在存量漂移、E5、筆記形狀擋、筆記內容審那幾支函式,這些筆記宣稱的合約碰不到那幾支函式,判不影響。其中節點範圍與索引守衛的「重用既有抽取、不另寫一套」原則,F6 算是一個小反例(E5 與其他層各用一套行內剝法)。

最嚴重等級 major;blocking 共 2 條(F1、F2),另有 minor 6 條。
