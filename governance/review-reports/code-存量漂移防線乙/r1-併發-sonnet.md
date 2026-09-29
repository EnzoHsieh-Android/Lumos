severity: major

## F1 乙的推送判定新增至少 5 次未受 60 秒預算節流、且互相重複的 git 呼叫(同一棵樹的檔案清單被列 2–3 遍)

severity: major
blocking: 是 — `_drift_check_core` 的 docstring 明講「每一步開始前、每篇候選之前都看一次預算」,但乙新增的
`_ProbeTree.__init__`、`_probe_prepare` 三處呼叫都沒看 deadline,且對同一顆樹重複列清單,直接違反這個機制自己
宣稱要守住的預算保證,而這個保證正是計劃裡「預設改 block」三門檻之一(RULE:[since:2026-09-28] 那條)的前提。
引句:「lst = _nodehome_list(root, "index" if where == "disk" else where)」

1. `scripts/lumos:25787`(`_ProbeTree.__init__`)在建每一版的 `_ProbeTree` 時,不論 deadline 剩多少都無條件呼叫
   `_nodehome_list(root, where)`(對提交等於 `git ls-tree -r -z --full-tree <sha>`,是全庫檔案清單,不是只列圖譜),
   呼叫前沒有任何 `deadline`/`_left()` 檢查。
2. `_drift_probe_check`(`scripts/lumos:25918-25919`)緊接著又各建一個 `_ProbeTree`:
   `tip_ctx = _ProbeTree(root, tip, tenv, deadline)`、`base_ctx = _ProbeTree(root, base, benv, deadline) if base else None`。
   但 `tip` 那棵樹在 `_drift_check_core` 一開頭(`scripts/lumos:25620`)已經透過 `_drift_tree_env(root, tip, ...)`
   列過一次(同樣呼叫 `_nodehome_list`);這裡等於重列第二次。`base` 那棵樹的情況更糟,見下一點。
3. `_probe_prepare`(`scripts/lumos:25940`)裡,`base` 樹的檔案清單在同一個函式內被列了兩次:
   `_drift_vault_rel(root, base)`(內部呼叫 `_nodehome_list(root, base)`)和緊接著的
   `_drift_tree_env(root, base, ..., deadline=deadline)`(內部又呼叫一次 `_nodehome_list(root, base)`)——
   引句:「benv = _drift_tree_env(root, base, _drift_vault_rel(root, base) or vault_rel, override_base, deadline=deadline)」
   ——加上第 2 點裡 `_drift_probe_check` 又建一次 `base_ctx`,`base` 樹的檔案清單在一次 drift check 裡總共被列 3 遍。
4. `_probe_prepare` 結尾還有一個全新、完全沒被既有預算檢查涵蓋的 git 呼叫:
   引句:「rn = _ns_git(root, "diff", "--name-status", "-z", "-M", base, tip, "--", vault_rel)」
   (`scripts/lumos:25950`)——它排在 `benv` 建好之後才打,前面沒有任何 `_left()` 判斷,若前面幾次呼叫已經把預算耗盡,
   這一次不會被攔下,只會繼續往下跑。
5. **最小重現**(在自己 mktemp 的 clone 裡對 `_drift_check_core` 直接掛 `subprocess.run` 計數器,範圍只有一個條件式
   REVISIT 行、兩個提交):
   ```
   total git calls: 18
     ...
     git -C . ls-tree -r -z --full-tree f7701f27fe5949f022f74fc2d46c7f966dd15300      ← tip,第 1 次(_drift_tree_env)
     ...
     git -C . ls-tree -r -z --full-tree 5e622d09d6901ff844fe1a790e6f280b5c6eef03      ← base,第 1 次(_drift_vault_rel)
     git -C . ls-tree -r -z --full-tree 5e622d09d6901ff844fe1a790e6f280b5c6eef03      ← base,第 2 次(_drift_tree_env)
     ...
     git -C . ls-tree -r -z --full-tree f7701f27fe5949f022f74fc2d46c7f966dd15300      ← tip,第 2 次(_ProbeTree)
     git -C . ls-tree -r -z --full-tree 5e622d09d6901ff844fe1a790e6f280b5c6eef03      ← base,第 3 次(_ProbeTree)
   ```
   全部 18 次 git 呼叫裡,只有 `_probe_changes` 自己的兩次前面有 `deadline` 檢查,其餘(包含上面列的 5 次全庫樹清單)
   一次都沒有。單次呼叫上限是 20 秒(`_lens_git` 的 `timeout=20`),60 秒預算只夠吃 3 次這種呼叫卡住就會整批算判不了
   ——這條重演的正是同一份 diff 自己 PITFALL 行講的「r2 只在每篇之前看、r3 查到一篇裡還有兩次呼叫不看」那個錯誤形狀,
   只是這次發生在 乙 全新、從沒被那三輪代碼審打磨過的程式碼裡,不是被那三輪修過的舊路徑。
6. 影響範圍:一旦計劃 REVISIT:2026-10-26 那條把 rtb 45 條散文回頭條件全部改寫成條件式(現在工具鏈與 rtb 都還是
   0 條,所以這條路目前完全沒被真實推送踩過),`_drift_probe_check` 的 `lines` 不再是空清單,乙的判定會變成
   **每一次推送都會跑到**的常態路徑,F1 這幾個重複、未受節流的呼叫就會變成穩定的額外開銷,而不是偶發。

## F2 `_ProbeTree.one()` 對任何 symbol/test 條件一律讀「整個庫」的程式檔或測試檔,即使條件已經釘死單一路徑

severity: major
blocking: 是 — 這正是這次鏡頭被要求特別看的「兩端各讀一次全部程式檔與測試檔」那個成本,而且釘死路徑不能倖免,
沒有任何設定能關掉這個全讀;在真實消費專案(程式檔遠比這個工具鏈 repo 多)上會被放大。
引句:「corpus = self.corpus(test)」

1. `_ProbeTree.one()`(`scripts/lumos:25816-25841`)處理 `symbol`/`test` 條件時,不論值是不是帶路徑(`path/to/x.py::Name`
   這種完全釘死單一檔案的寫法),都先呼叫 `corpus = self.corpus(test)`。`path` 只在「已經讀進記憶體的 corpus 字典裡
   查哪個 key」時才用得到(`items = [(path, corpus.get(path))] if path else list(corpus.items())`),完全沒有「path 給了
   就只批次讀那一支檔」的分支。
2. `corpus()`(`scripts/lumos:25805-25814`)批次讀的對象是「`self.files` 裡所有副檔名在白名單、不在 `docs/`/`governance/`
   底下、且測試/非測試分類等於 `test` 那個布林值的路徑」——即整個庫的非測試碼(或整個庫的測試碼),不是那一支被
   `path` 指到的檔。
3. **最小重現**(在自己的 mktemp clone 裡,對 `_nodehome_cat_blobs` 掛計數器,直接呼叫一個**完全釘死路徑與名稱**
   的條件 `when-test:scripts/test_lumos.py::t_drift_when_probes_evaluate_and_trigger`):
   ```
   anchored test condition result: True
   cat_blobs 呼叫批次大小(specs 數量): [2]
   ->即使條件釘死單一路徑,仍批次讀了 2 支檔(全庫非測試/測試檔數)
   ```
   這個工具鏈 repo 目前「非 docs/、非 governance/」下帶副檔名的測試檔只有 2 支,所以批次量看起來小;但批次大小是
   `_nodehome_is_test(...) == test` 篩出的**全庫**數量,跟條件釘不釘路徑無關——在一般消費專案(測試檔動輒幾十到
   幾百支)上,同一支 `when-test:` 或 `when-symbol:` 就算完全指名道姓,仍會觸發全庫測試檔(或全庫非測試檔)批次讀。
4. 跟 F1 疊加:當 `old` 為真(起點也有同一條)時,`_probe_judge`(`scripts/lumos:25956-25966`)會再對 `base_ctx`
   呼叫一次 `.line(conds)`,等於**兩端各再各自觸發一次同樣的全庫批次讀**——這正是派工詞裡明確點名要看的成本,
   而且沒有 `override`/設定能繞開(不像 `LUMOS_SKIP_DRIFT_CHECK` 那樣有逃生門)。
5. 修法方向(供作者參考,不是本審查的裁決):`path` 給定時应該直接 `_read_many([path])` 讀那一支,不經過
   `corpus()` 的全庫批次;`corpus()` 的全庫批次留給沒給路徑的條件用。

## 已看,無 finding 的部分

- **doctor 的 E5 與乙的 Z 段解析成本**:實測直接呼叫 `_drift_doctor_lines(env)`(573 篇筆記的工具鏈圖譜本身)
  5 次平均 0.138 秒/次,相對於整套 `lumos doctor` 12.8 秒的既有開銷可以忽略;E5 段對 `_revisit_split` 的改寫是
  逐行文字比對,沒有新增 git 呼叫或檔案批次讀,成本跟筆數線性,不到會拖慢 doctor 的量級。
- **筆記形狀擋(`_ns_revisit_violations` / `_notelines_new(..., keep_other=True)`)每次提交多做的事**:
  只多收「開頭欄位 other 區塊」裡這次新寫的幾行,範圍受限於這次 staged 的新增行,沒有新的 git 呼叫(沿用既有的
  `_notelines_new` 那一次 diff),量體隨這次提交改動的行數成正比,不是隨全庫大小成正比,沒看到會拖慢 pre-commit
  的路徑。
- **`diff -U0` 在大範圍(含起點是空樹)的輸出量**:`_probe_changes`(`scripts/lumos:25851-25884`)在 `base` 為空
  (新分支第一次推送)時明講「起點是空樹時 added_text 不算」並直接跳過 `_ns_diff` 那次呼叫,這點刻意避開了大範圍
  U0 diff 的輸出量問題,是好的設計;沒看到反例。空樹情境下反而改成「每一行都當候選」,但由於 `.corpus()` 有
  按 `_ProbeTree` 實例快取(`self._corpus`),同一個 `tip_ctx` 內多筆候選共用同一次批次讀,不會被候選數放大成
  N 次批次讀——這條路徑本身沒有额外的 git 呼叫放大問題,值得留意的成本已經在 F1/F2 涵蓋。
- **工作目錄模式(`where == "disk"`)讀磁碟的成本**:`_ProbeTree._read_many` 在 disk 模式下用逐檔
  `Path.read_bytes()`(`scripts/lumos:25792-25800`),沒有批次化、沒有逾時,但這條路只在 `lumos drift scan` 這種
  唯讀健檢指令上場(不受 60 秒推送預算約束,也不會擋推送),且成本一樣被同一個 `_ProbeTree` 實例的 `self._corpus`
  快取吃掉,不會隨候選行數重複讀。列成觀察但沒有具體失敗場景,不升級成 finding。

合計:severity 最高 major,blocking 共 2 條(F1、F2)。

---

## 圖譜鏡頭:派工尾端固定席節點逐條判(範圍 ac5c7ccf..e8f17913)

以下逐條判這份 diff 會不會破壞該節點宣稱的行為或合約;凡判「不影響」都附一句為什麼。

- **Systems/lumos-cli-read.md**(★家★ 直接,分數最高)——不影響,而且是明確遵守:diff 自己的 WHY 行寫「drift scan
  判不了的列出來但不寫治理帳:讀指令不寫帳是既有決定(見 [[Systems/lumos-cli-read]] 的 d1)」,`cmd_drift_scan` 對
  乙的發現(`_drift_probe_scan`)一樣走同一條不寫帳的路,沒有新開一條寫帳的讀指令。
- **Systems/guard-kill.md**(★家★ hop1)——不影響:這份 diff 沒有碰 settle 改寫預告句、guard plan/pass 那組函式,
  乙只是在既有的 `_drift_check_core` 尾端加一段回傳合併,沒有動 settle 共用的行首前綴比對邏輯。
- **Systems/授權與歸屬.md**(★家★ hop1)——不影響:FLOW 管的是 vendored 檔案的 SPDX 表頭與新增第三方碼登記,
  `scripts/lumos` 檔頭沒被這份 diff 動到,也沒有新增任何第三方程式碼。
- **Systems/測試假綠形態.md**(★家★ hop1)——不影響,且方向一致:diff 新增的每支測試(`t_drift_when_probes_...`
  等 5 支)docstring 都明寫「翻紅釘」列出會讓測試真的翻紅的突變點,符合這份節點家族要求的「測試要證明自己抓得到
  它宣稱要抓的失敗」,沒有發現新測試是「存在但沒在驗宣稱要驗的東西」那種假綠形態。
- **Systems/design-loop.md**(★家★ 直接)——不影響:這份 diff 走的是既有審查迴圈的產物,沒有修改 design-loop
  本身的程式(`_drift_*`/`_probe_*` 都在 drift 這條路徑上,不在 loop 派工/收斂那組函式裡)。
- **Systems/pitfalls-code-loop.md**(★家★ 直接)——不影響:diff 沒有動 lint-new / pitfalls 掃描器那組函式,
  `scripts/lumos` 裡跟 pitfalls-code-loop 相關的段落沒有出現在這份 diff 的 hunk 裡。
- **Systems/lumos-cli-lifecycle.md**(★家★ 直接)——不影響:管 init/update/bootstrap/deinit/teardown 的生命週期,
  這份 diff 只加了 `drift exam` 的 `--probes` 參數與內部函式,不涉及任何生命週期指令。
- **Systems/loop-convergence-recording.md**(★家★ 直接)——不影響:乙的 must 發現最終仍匯入既有
  `cmd_drift_check` → `_drift_report_must` 的既有記帳路徑(`drift-check` 閘名不變),沒有新開一條記帳路徑繞過
  `loop_kind`/`--sha`/`--defect-ref` 這組既有規則。
- **Systems/reversibility-governance-ledger.md**(★家★ 直接)——不影響:閘名單本來就已經在甲那次加了
  `drift-check`(這份 diff 的 WHY 行也提到「放行不寫帳(同筆記形狀擋),doctor Z 段也不寫」),乙沒有新增閘名、
  沒有改寫帳規則,只是讓同一個閘多一種發現來源。
- **Systems/節點範圍與索引守衛.md**(★家★ 直接)——不影響,且正向合規:這份 diff 把新函式寫回的家筆記
  (存量漂移守衛.md、筆記內容審.md、筆記內容閘.md)都有更新 `TEST:` 欄位列出新測試,符合「每支檔有家、改到的
  程式要寫進家筆記」的要求。
- **Systems/check-r-guard.md / Systems/check-t-sentinel.md**(★家★ 直接)——不影響:這兩個是特定字串哨兵/正則
  守衛,這份 diff 沒有新增會被這兩道守衛盯的模式(沒有新的裸 regex 字面量繞過既有白名單類型)。
- **Systems/doctor-irreversible-hint.md**(★家★ 直接)——不影響:管 doctor 對不可逆操作的提示,乙加的是
  Z 段一行摘要統計,不是不可逆操作提示。
- **Systems/lumos-deinit.md**(★家★ 直接,★RISK·不可逆★)——不影響:與 deinit/解除安裝無關,診斷路徑上
  的 `drift`/`probe` 相關函式跟 deinit 那組完全不相交。
- **Systems/cochange-guard.md**(★家★ 直接)——不影響甚至正向:這份 diff 的 commit 本身就是
  `scripts/lumos` + `scripts/test_lumos.py` + 對應家筆記一起改,符合共改配對守衛期待的模式,不會觸發「改了
  一邊沒改另一邊」的警告。
- **Systems/lumos-refcheck.md**(★家★ 直接)——不影響:管筆記連結完整性;這份 diff 新增/修改的 `related:`
  連結(如 `[[Systems/存量漂移守衛]]`)在同一份 diff 裡本來就存在對應節點,沒有斷鏈風險。
- **Systems/bound-tests-gate.md / Systems/canary-audit.md / Systems/slim-get-一行安裝.md /
  Systems/slim-install-安裝器.md / Systems/slim-uninstall-一行卸載.md**(hop1,因為同時改了
  `scripts/test_lumos.py` 而被牽連)——不影響:這份 diff 新增的測試函式名(`t_drift_when_probes_evaluate_and_trigger`
  等)都在函式體或 docstring 裡直接提到自己驗的模組/概念字樣,`-k`/關鍵字子集挑選抓得到;slim 那三個安裝腳本
  完全沒被這份 diff 動到(diff 裡不含 `slim/` 底下任何檔案)。
- **Projects/雙向門放行_計劃.md**——不影響:這份 diff 是程式+文件混合改動,推送前的閘本來就該落在
  「非純文件」那一支(keys 或 full 子集),不是 docs-only 子集,行為與這份計劃描述的分流邏輯一致,沒有讓一個
  該跑全套的改動誤判成純文件。
- **Projects/規格落成可驗收條件_計劃.md**——不影響:管 spec-gate 驗收流程,這份 diff 沒有新增/修改
  spec-gate 相關指令。
- **Projects/逃逸自動記_計劃.md**——不影響:`LUMOS_SKIP_DRIFT_CHECK` 這個既有逃生門的記帳邏輯
  (`_gate_event_or_warn`)沒有被這份 diff 改動,乙沒有新增第二個跳過旗標。
- **Systems/core-invariant-baseline.md**——不影響:管核心不變量基線登記,這份 diff 沒有新增/移除任何
  `★INVARIANT★` 標記行。
- **Systems/judge-severity-gate.md**——不影響:管代碼審嚴重度判定閘本身(也就是產生這份報告要過的那道閘),
  跟這份 diff 的功能無直接耦合。
- **Projects/存量漂移防線_計劃.md**(1.00,直接,這份 diff 本體之一)——已在 diff 內同步更新(考試結果表、
  REVISIT:2026-10-26 補的重放計畫),內容與程式行為一致,沒有發現筆記寫的和程式碼對不上的地方。
- **Systems/筆記內容閘.md / Systems/筆記內容審.md**(★家★ 直接,diff 本體之一)——已在 diff 內同步更新 WHY
  行(`[S10]`、`[S12]`),兩段新增的 `_ns_revisit_violations` 與「條件式不送審」邏輯跟筆記裡寫的描述一致。
- **Systems/lumos-cli-write.md**(★家★ 直接)——不影響:管寫入指令(`set`/`append`/`decision-add`)共用的
  YAML 引號/白名單邏輯;乙新增的 `_drift_status_probe_followups` 只在 `lumos set` 收尾計劃時「印出」連帶待辦
  文字,沒有新增任何寫欄位的路徑,不繞過既有的 `_yaml_quote`/`_fmt_decision_value` 共用寫入邏輯。
- **Projects/公開精簡版_實作計畫.md**——不影響本次程式碼正確性,但有一個既有的人工流程提醒(不是這份 diff
  造成的新問題):這份計畫管的是「生成 `dist/` 交付包」流程,`scripts/lumos` 改了 CLI 行為理論上要人工重新生成
  `dist/` 再推 Citrus_Lumos——這是既有流程本來就要求的人工步驟,不是這份 diff 能不能過審的判準,也不是併發/
  資源鏡頭該擋的問題,列出來給收貨端知會即可。
- **Projects/code側刪除傳播守衛_實作計畫.md**——不影響:這份 diff 沒有刪除任何既有匯出符號(舊的 REVISIT
  解析邏輯是被行內改寫,不是刪除獨立函式再讓別處孤兒引用它),delguard 不會有東西可抓。
- **Systems/存量漂移守衛.md**(★家★ hop1,diff 本體之一)——已在 diff 內同步更新(新增「條件式回頭條件(乙)」
  一節),內容與 F1/F2 指出的程式行為沒有衝突——筆記沒有宣稱過乙的資源成本上限,所以 F1/F2 不構成筆記與程式碼
  對不上,只是程式碼本身在資源鏡頭下的實作缺陷。
- **Projects/筆記內容審_計劃.md**——不影響:已涵蓋在 [S12] 的既有描述裡(條件式回頭條件不送審),這份 diff
  的 `_note_audit_items` 改動與筆記描述一致。
