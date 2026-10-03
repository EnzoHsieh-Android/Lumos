severity: minor

# 第 3 輪(末輪)合約圖譜席報告

範圍:`/tmp/code-tail-r3.patch`(r2 修正段,對應 `git diff 35de50ac 6dc9ec04 -- scripts/lumos` 共 144 行,已核對一致)。repo 用 `rw` 唯讀;所有改碼實驗都在 `scratchpad/mut/` 的複本做。

做過的實驗(結果都在各條 finding 內):
- 在 rw 跑 `-k ns_append`(88 過)、`-k ns_nfc_clash`、`-k note_audit_dispute`、`-k note_audit`(345 過)、`-k gate_event_fit`、`-k drift_m1`(248 過),全綠。
- 對 r2 新增的每一處修法各做「改回去」變異:名字鍵扣減、申訴不分範圍、NFC 撞名檢查關閉、讀帳去重關閉、位元組總量上限關閉、capped 帳關閉、提醒印出關閉。除下面 G1 說的一處外,全都翻紅。

## Findings

**G1 放寬帳 capped 的「從真實配對到寫帳」那一段沒有測試守**
severity: minor
blocking: 否 — 條款 [S43] 的四個動作裡有三個翻紅有守,第四個(推送時真的記 capped)的接線拿掉測試照綠;影響只在遙測,且目前接線是對的
引句:「relaxed["capped"] = pairs.capped」
1. 重現:在 `_ns_relaxed_settle` 把 `relaxed["capped"] = pairs.capped` 改成 `pass`,跑 `python3.14 scripts/test_lumos.py -k ns_append` → `88 passed, 0 failed`(變異 M7)。
2. 原因:`t_ns_append_caps` ③ 是手餵 `m._ns_relaxed_record(root, head, "tipsha", {"capped": True, "by_line": {}})`,沒有走「真的超過上限 → `_NotelinesPairs.capped` → `_ns_relaxed_settle` → 記帳」這條線。
3. 對照(證明目前接線是對的):`m._NS_APPEND_MAX_PAIRS = 0` 再跑 `cmd_note_shape(root, diff_range=...)`,帳裡出現 `('capped', '這次推送:舊行尾補括號的候選超過總量上限,全部照整行查')`。所以現在行為正確,只是拿掉接線沒有人會紅;[S43] 寫的「推送時 應 記一筆 state capped」只被單元餵值守住一半。
4. 缺的:一條端到端測試(造超過上限的配對、跑 `--diff`、斷言帳裡有 capped)。

**G2 沒有放寬時,每次推送也讀整份治理帳尾(最多 24 MiB)**
severity: minor
blocking: 否 — 只是每次推送多約 0.2 秒,不影響判定
引句:「seen = _ns_relaxed_recorded(root, os.environ.get("LUMOS_PUSH_ATTEMPT", "").strip())」
1. 重現:在 rw 對一個普通改動(沒補括號、沒有放寬)設 `LUMOS_PUSH_ATTEMPT=att-plain` 跑 `cmd_note_shape(root, diff_range=...)`,對 `_ns_relaxed_recorded` 計數 → 呼叫 1 次、relaxed 事件 0 筆(`repro_read.py`)。
2. 原因:`_ns_relaxed_record` 在 `relaxed` 是非空字典(推送模式 `_ns_relaxed_settle` 一定填鍵)時,無條件先 `_ns_relaxed_recorded`,再才看 `fin` 空不空。r1 的舊寫法只有 `count` 為真才碰記號檔。
3. 量測:本 repo 治理帳 16.7 MB,`_ns_relaxed_recorded(".", "att-x")` 一次 0.21 秒;帳檔尾上限 24 MiB(`_GOV_TAIL_CAP`)時約 0.3 秒,而且是每條分支各一次。
4. 修法方向:先算 `fin`(`relaxed["by_line"]` 非空)才讀帳。這也跟 [[Systems/reversibility-governance-ledger]] d3「doctor 純 append(不必每 push 讀全檔)」的精神有張力(見固定席段)。

**G3 同一次推送的兩條分支補在同一(路徑, 行號),第二條的放寬帳被去重吃掉**
severity: minor
blocking: 否 — 只少記遙測,判定不受影響;但註解與計劃都宣稱「只多記、不少記」,這個說法不成立
引句:「fin = {k: r for k, r in (relaxed.get("by_line") or {}).items() if k not in seen}」
1. 重現(`repro_dedupe.py`):同一個起點 base,分支 A 與分支 B 各自把同一行(`A.md:14`)補不同的括號,tip 不同;設 `LUMOS_PUSH_ATTEMPT=one-push`,先後跑 `--diff base..tipA`、`--diff base..tipB`,兩次 rc 都 0。
2. 輸出:`relaxed events: [('1be82f5', [['docs/kg-knowledge/Systems/A.md', 14]])]`,只有 tipA 的一筆;tipB(`c946530`)的放寬沒有帳。
3. 原因:去重鍵只有 `(路徑, 行號)`,沒有 tip 也沒有行內容;r1 版鍵含起點、終點與配對,r2 為了「範圍重疊也去重」把鍵縮小,同時把「不同分支同位置」也當成已記過。
4. 影響:計劃 RETIRE-IF ② 要靠 `relaxed` 帳筆數分辨「沒機會用」與「壞了」,多分支推送會少算。計劃做法 5 與 [S48] 只寫了「範圍重疊」的情境,沒寫這個反例。

**G4 r2 的「只扣照片段比的」順手讓「回頭條件格式不合」「條件寫錯」也不再扣,計劃與死表沒同步**
severity: minor
blocking: 否 — 影響的是舊的、本來就寫錯的 REVISIT 行補括號這個窄情境;但是 r1 到 r2 的行為改變,計劃做法 2 還寫著舊行為,而且沒有任何測試守任何一邊
引句:「if v[2] not in _NS_FRAG_KEY_RULES:」
1. 重現(`repro_revisit.py`):起點版本正文有舊行 `REVISIT:下個版本再看這個項目`(第一個位置不是日期也不是條件標記,本來就違規),只在句尾補 `(更正:2026-10-02 已完成 [來源:人工])` 後暫存跑提交前那份。
   - 前一版(35de50ac 的 `scripts/lumos`):rc 0(舊行本來就有的違規被扣掉)。
   - 現在(6dc9ec04):rc 1,擋「回頭條件格式不合」。舊行是 `REVISIT:[when-file:src/a.py] 等它出現再回頭看看`(沒帶 `[by:]`)補括號時同樣:前一版 rc 0、現在 rc 1「條件寫錯」。
2. 原因:`_ns_append_subtract` 現在對 `v[2] not in _NS_FRAG_KEY_RULES`(只有「程式行號引用」「釘版本不合法」)一律保留。「回頭條件格式不合」只看行首,舊行與新行必同,補括號不可能改變它;它不是「括號借舊行的債」的那一族。
3. 內部不一致:
   - 計劃做法 2 的這一行沒改,仍是「`_ns_revisit_violations` 對 N 與 O 各算(兩邊都在圍欄外),鍵(規則, 改法);改法只有「條件寫錯」帶錯誤細節,補一個寫錯的條件會照報」,描述的是會扣。同一節上一條(新寫的)卻說整行層級的規則(含「或固定改法」)一律不扣。兩條互相矛盾。
   - `_NS_REVISIT_RULES` 與 `_ns_viol_key` 的回頭條件分支現在算出來的鍵永遠不會被拿去扣(`base` 計數器還是會算),等於死碼;`t_note_audit_append_scope_more` ③ 還在驗「`_NS_REVISIT_RULES` 每個名字出現在產生它的函式裡」,守的是一張沒人用的表。
4. 沒有測試守:把保留條件改成 `v[2] not in _NS_FRAG_KEY_RULES + ('回頭條件格式不合', '條件寫錯')` 跑 `-k ns_append` → 88 過,表示 r2 的取捨(扣或不扣)兩邊都沒有測試。
5. 判不準的部分 ⚠:是否有意讓舊的壞 REVISIT 行補括號也要整行修好(天花板 1 寫「想只補更正就得順手把整行修好」),計劃沒說這兩個規則也在內。要擋就把計劃做法 2 那行改掉並補一條 [SN] 測試;要放就把這兩條規則加回扣減範圍(只在改法相同時扣)。

**G5 r2 補的「讀被刪摘要行帶切法旗標」沒有測試釘**
severity: minor
blocking: 否 — 旗標本身是對的(下面第 2 點證明),只是拿掉沒人紅
引句:「"--inter-hunk-context=0", "--diff-algorithm=myers", "--src-prefix=a/", "--dst-prefix=b/", *args)」
1. 重現:在複本的 `_ns_deleted_summary_lines` 拿掉兩個旗標,跑 `-k deleted`(11 過)、`-k notelines`(10 過)、`-k ns_append_r1`(3 過)、`-k slots_`(196 過)、`-k move`(43 過)、`-k note_shape`(263 過;1 個失敗是複本缺 `.github/workflows/ci.yml` 造成的,跟變異無關)→ 沒有一支翻紅。
2. 旗標確實有差(模糊測試 `fz.py`):本機設 `diff.algorithm=histogram`,把含重複行的摘要前綴行打亂順序後暫存,同一個函式在有旗標與沒旗標時回的被刪行清單不同(有旗標 2 條 `['RULE:丁…','DEP:乙…']`,沒旗標 5 條),代表本機設定會改變「舊條目搬家」判斷。
3. 對照:`_ns_diff` 有 `t_notelines_parse_git_config`(設 `diff.interHunkContext`、`diff.algorithm` 驗輸出一致)守同一件事;這支讀被刪行的呼叫是 r2 才補,沒有對應的那種測試,`t_lumos_content_diffs_all_disable_external_drivers` 只管 `--no-ext-diff`。

**G6 [S47] 的測試沒有前置斷言證明配對真的走到**
severity: minor
blocking: 否 — 改回修法時它會紅(變異 M1 兩條都翻紅),但缺 [[Systems/測試假綠形態]] INVARIANT 要的現場成立斷言
引句:「check("①舊 SEE 行夾句子、補括號:SEE 只放連結照報", rc == 1 and "SEE 只放連結" in out, out[-500:])」
1. 重現:把 `_ns_append_same_context` 開頭加 `return {}`(整個配對關掉)跑 `-k ns_append_line_rules` → `2 passed, 0 failed`。
2. 原因:SEE 與「不評估的條件標記」這兩條沒有任何無害括號可當對照(補括號後仍照報,所以沒法寫「改成什麼就放行」的對照),測試只斷言 rc==1。配對有沒有發生,測試不知道;它翻紅完全靠「配對剛好在運作、修法一拿掉就變 rc 0」。
3. 缺的:一條在同一個專案、同一個起點下證明「配對有發生」的斷言,例如在同一測試裡對同一份起點補一行帶行號引用的舊行,斷言舊引用被扣(rc 0);或直接呼叫 `_notelines_append_pairs` 斷言這兩行在表裡。這正是 r2 合約圖譜席第一條抓的那一型。

**G7 兩篇系統筆記的 WHY 行寫了程式碼讀得出來的細節**
severity: minor
blocking: 否 — 不影響行為;是筆記內容審自己要擋的那一類
引句:「prepare、record、check、skip 能略過哪些都比範圍(只判尾巴的判定只涵蓋配到同一句舊句的項目;」
1. `Systems/筆記內容審.md` 這行 WHY 逐一列出哪幾個入口比範圍、哪幾個不比(prepare、record、check、skip、doctor、skip 的「同編號判過 CODE/MIXED」那步),這是 `_note_audit_class_for` 與 `_note_audit_fold` 各自被誰呼叫就看得到的事。真正程式碼推不出來的是原因(編號要穩定、doctor 起點不同所以比範圍會誤報),那部分已寫在 [因:] 裡。
2. `Systems/筆記內容閘.md` 新增句「候選超過總量上限(篇、對、位元組)時全不配、印提醒、推送記 capped」同樣是 `_notelines_append_pairs` / `_NotelinesPairs.table` / `_ns_relaxed_record` 讀得出的現況;值得留的是「為什麼印提醒」(r2 通才席:清舊筆記的人照提示做仍被擋、看不出原因)。
3. 建議的整理方向(不是新行為):入口對照表留在計劃,筆記只留 WHY 與否決過的方案。

**G8 計劃寫了一個範本改字不升版的例外,但 Systems/筆記內容審 的 RULE 仍寫「改任何一個字要升版號」**
severity: minor
blocking: 否 — 兩邊都不是機械擋的規則,只是讀的人會看到互相矛盾的指示
引句:「第 2 版範本在這次重跑前改過用字、版本號沒再升」
1. `Projects/筆記內容審_計劃.md` 新增這句,並說明理由(改字發生在第 2 版第一次推送之前,沒有用它發出的舊清單,所以不算改版;推送之後改一個字就要升版)。
2. `Systems/筆記內容審.md` 的 `RULE:派工詞範本改任何一個字要升版號,並重跑 68 句小實驗…` 沒變,沒有帶這個例外;兩者並列時三個月後的接手者無從判斷。該 RULE 只有 `[since:]`、`[retire:]`、`[applies:]`,沒有 `[confirmed:]`,按 CLAUDE.md 只是線索,不能壓過計劃。
3. 建議:RULE 補一句「第一次推送前的改動不算」,或計劃改成不提例外。

## 固定席節點(`/tmp/codetail3/lens.txt`)

- `Systems/reversibility-governance-ledger.md`(RISK)。這份 diff 新增一個讀治理帳的 `_ns_relaxed_recorded` 與一種新寫入事件 state `capped`,沒有動它的合約:放寬帳 `kind=relaxed` 仍是第三個「沒違規不寫帳」例外,與該筆記 WHY 行(「推送時舊行尾補括號減掉違規另記 relaxed」)一致;`_gate_event_fit`(r1 已改成共用二分)這輪沒動。決策 d3(`valid: true`)的「doctor 純 append(不必每 push 讀全檔)」講的是 doctor 的寫入端,不被這份 diff 破壞,但新讀者每次推送都讀帳尾,見 G2。
- `Systems/lumos-cli-read.md`(INVARIANT:search 預設排除 superseded 不排除 stale)。diff 完全沒碰 search 的篩選位置與旗標,不影響。
- `Systems/bound-tests-gate.md`(INVARIANT:impact 固定席上合約綁的測試逐支真跑)。diff 沒動這道閘的程式;新增與改寫的測試名稱都存在於測試索引(`t_ns_append_line_rules`、`t_ns_append_ledger_dedupe`、`t_ns_nfc_clash_errs`、`t_note_audit_dispute_scope`),不會造成懸空。這道閘只看「存在加 rc」,抓不到 G1、G6 這類「存在但守不住」,不影響它宣稱的行為。
- `Systems/guard-kill.md`(INVARIANT:rc 優先序與 `--json` 純度)。diff 不碰 `guard kill` 路徑,不影響。
- `Systems/授權與歸屬.md`(INVARIANT:授權檔不進 `_VENDORED_TOOLKIT`;`scripts/lumos` 檔頭要有 SPDX 兩行與 MIT)。diff 沒有改檔頭、沒有新增被複製的檔案,不影響。
- `Systems/測試假綠形態.md`(INVARIANT:還原翻紅釘要配前置斷言)。r2 改的七支配對測試這輪已補前置斷言(例如 `t_ns_append_old_line` ①a、`t_ns_append_bypass` ①、`t_ns_append_context` ①a/③),跟這條一致;新增的 `t_ns_append_line_rules` 沒有,見 G6;`t_ns_append_caps` ③ 手餵值,見 G1。
- `Systems/pitfalls-code-loop.md`(RISK)。diff 不碰 pitfalls 計算與代碼審流程,不影響。
- `Systems/design-loop.md`(INVARIANT:處置閘第五步,計劃有 [SN] 時每條要綁測試)。計劃新增的 [S47]–[S50] 都帶 `[test:…]` 且測試存在;[S43]–[S46] 改寫後仍綁既有測試。不影響。
- 「超出上限,只列名」的 12 篇以上(`lumos-cli-lifecycle`、`loop-convergence-recording`、`節點範圍與索引守衛`、`lumos-deinit`、`check-t-sentinel`、`cochange-guard`、`check-r-guard`、`doctor-irreversible-hint`、`lumos-refcheck`、`canary-audit`、`slim-*`、`core-invariant-baseline`、`judge-severity-gate`,以及 `規格落成可驗收條件_計劃`、`雙向門放行_計劃`、`逃逸自動記_計劃`):沒有完整內容可讀,只憑節點名與這份 diff 只動 `note-shape`/`note-audit` 兩組函式、測試與四篇筆記判斷,看不出牽連;其中 `節點範圍與索引守衛` 與 NFC 撞名的新檢查名稱相近,diff 沒改它管的檔,不影響(⚠ 沒讀全文,判斷以 diff 範圍為依據)。

## 沒問題的項目

- NFC/NFD 撞名新檢查(`_ns_nfc_clash_errs`):有「前提:暫存區真的有兩種寫法」「端到端 rc 1」「內容審同一支」三層斷言,關掉檢查會翻紅(變異 M3);`lst[1]` 在 `_note_shape_eval` 開頭就有定義,`_nodehome_list` 對 index 已排除合併中的衝突階段,不會把未解決的衝突誤算成並存。
- 申訴範圍(`_note_audit_dispute_for`):整行申訴換掉每種範圍、句尾申訴只換同一個句尾、兩種都有取最重,改回「任一範圍」翻紅(變異 M2 三條斷言紅);沒有別的呼叫端還在用舊的 `{(檔名, 編號): 類別}` 形狀(全檔只有 `_note_audit_fold_scoped` 呼叫)。
- 放寬帳讀帳去重:不同推送編號照記、沒有推送編號不去重,關掉去重翻紅(變異 M4);帳檔不存在時 `OSError` 被吞,回空集合。
- 總量上限:位元組總和、篇數、對數三種超過都回 `"cap"` 且 `failed` 為假、提醒只印一次;關掉位元組上限或提醒翻紅(變異 M5、M8、M9)。`_nodehome_cat_sizes` 對不存在的物件回 None,加總時排除,不會把「起點沒有這篇」當成錯誤。
- 整行層級規則不扣:SEE 夾句子與表格列不評估條件標記補括號仍照報,改回名字鍵翻紅(變異 M1);「現況描述沒寫來源」「程式行號引用」「釘版本不合法」的行為與計劃做法 2 一致。
- 牆上時鐘門檻:`t_gate_event_fit_bisect` 改成數 `_gate_event_build` 呼叫次數(上限 40),`t_ns_append_r1_minor_folds` 改成取三次最快的相對倍數;改回平方版會遠超門檻。
- 配對測試假綠:r2 抓到的「沒帶來源的括號當探針」全部改成「舊行就有的行號引用 + 帶來源的括號」並附前置斷言,`t_ns_append_old_line` ①a、`t_ns_append_eol` ①、`t_ns_append_push_range` ① 都有「改一個字/換起點時照報」的對照。
- 新增的三篇筆記與計劃修改沒有殘留舊的記號檔(`lumos-relaxed-seen`、`_ns_relaxed_seen`)引用(全 repo grep 無);`否定現況句配回頭條件_計劃` 兩處「放寬帳幫不上」的改寫與程式一致(提交前 `relaxed=None`,不記帳)。
- 範圍內 `-k note_audit`(345)、`-k ns_append`(88)、`-k gate_event_fit`(3)、`-k drift_m1`(248)全綠。

最高 severity:minor
