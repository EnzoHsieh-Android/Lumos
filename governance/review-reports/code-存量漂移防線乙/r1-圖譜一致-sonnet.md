severity: minor

## F1 rename 對照另外起了一次 git,跟計劃第 0 節「只算一次」與 PRIOR-ART⑧「不另寫第二套」不符

severity: minor
blocking: 否 — 不影響正確性(git 呼叫本身有既有 20 秒單次逾時與整體 60 秒預算兜底),只是效能/維護面的實作跟筆記說法對不上
引句:「rn = _ns_git(root, "diff", "--name-status", "-z", "-M", base, tip, "--", vault_rel)」

1. 這行在 `_probe_prepare`(diff 內新函式)裡,在 `_probe_changes` 已經做過一次不限路徑的 `git diff --name-status -z -M` 與一次 `git diff -U0 -M`(用來算 `touched`/`code_shape`/`added_text`)之後,又對同一個 base..tip 範圍、限定 `vault_rel` 再起一次 `git diff --name-status -z -M`,只為了算筆記改名對照 `ren`。
2. `Projects/存量漂移防線_計劃.md`〈做法〉第 0 節明寫:「範圍的改動只算一次(一次 `git diff --name-status -M` 加一次 `git diff -U0`),兩端的全部路徑各列一次,讀檔有快取——不逐條件各起一次 git。」(file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:55`)——但 `_probe_prepare` 讓一次 `drift check`(只要有候選乙條件)實際跑 3 次 `git diff`,不是文字講的 1+1。
3. 同一段 PRIOR-ART⑧ 也明寫「筆記改名的對應借筆記形狀擋與筆記內容審共用那支(`_notelines_range_added`)裡的 `-M` 改名追蹤...要抽成可共用的一支,不另寫第二套」(file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:29`)。但 `_notelines_range_added` 內部的改名判定(`_renames` closure,`scripts/lumos:23905` 附近)仍是該函式的內部閉包,並未被抽成模組層級的共用函式;`_probe_prepare` 沒有呼叫它,而是自己重寫了一份幾乎一樣的 `git diff --name-status -M ... -- vault_rel` 呼叫。
4. 重現:在 `_probe_prepare` 呼叫前後各印一次呼叫次數(或直接讀 `scripts/lumos` 的 `_probe_changes`+`_probe_prepare` 兩支函式)即可看到 3 次 git diff。行為上沒有錯(改名對照算出來的結果是對的,乙的既有測試——含 `t_drift_when_probes_evaluate_and_trigger`——都綠),純粹是「筆記說一次,實際三次」與「說不另寫第二套,結果另寫了一套」兩處對不上。

## F2 PRIOR-ART⑥「借 `_strip_code_text`」跟乙實際用的函式對不上

severity: minor
blocking: 否 — 程式碼自己的說明(docstring)是準確的,只是計劃 PRIOR-ART 那句沒有跟著更新,不影響行為;既有 note_shape/revisit 測試全線通過
引句:「只認正文與摘要的可見行:圍欄(_visible_lines)、行內程式碼(_strip_inline_markup)、表格行裡的都不算」

1. `_probe_lines`(diff 新函式,`scripts/lumos` 內)的 docstring 明寫它用 `_visible_lines`(圍欄)配 `_strip_inline_markup`(行內反引號)兩支逐行處理;`_ns_revisit_violations` 也是呼叫 `_strip_inline_markup(ln)[0]`,`_note_audit_items` 新增的排除判定同樣呼叫 `_strip_inline_markup(ln)[0]`。三處全部繞開 `_strip_code_text`。
2. 但 `Projects/存量漂移防線_計劃.md`〈做法〉第 0 節前的 PRIOR-ART 清單第⑥項寫的是:「可見行判定借 `_strip_code_text`(圍欄與行內反引號一次剝,全檔唯一的剝碼函式,不另寫反引號正則)」(file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:29`)。`_strip_code_text` 是整段文字層級的函式(回傳拼接後的字串,見 `scripts/lumos:3277`),沒有行號,乙需要逐行判斷,實際上不可能直接拿它用——所以改用 `_visible_lines`+`_strip_inline_markup` 這對行級函式反而是合理選擇,程式本身沒問題;只是 PRIOR-ART 那句話跟最終落地的函式選擇不一致,屬於筆記沒跟著實作更新的內部矛盾。

## F3 [S2] 乙那一半「判不了」沒有新測試覆蓋,綁定測試的 docstring 自己承認欠帳

severity: minor
blocking: 否 — 我用 in-process monkeypatch 手動重現過,實際行為是對的(check 擋下印「判不了」、scan 在 --at 模式下列成 problems 且不寫治理帳),只是這條路徑目前完全沒有測試守著,回歸不會被抓到
引句:「t_drift_unknown_blocks_check_not_scan、t_drift_exam_scores」

1. 條款 [S2](計劃〈條款〉)寫「當 check 要評估的條件判不了...工具應把那些行算成要處理並印原因;scan 判不了時應列成判不了、不擋、不寫帳」,綁定測試是 `t_drift_unknown_blocks_check_not_scan`——這支名字在這次 diff 的 `Systems/存量漂移守衛.md` TEST 欄位裡繼續被列出(見引句,出自 diff 新寫的那一行 TEST 清單),沒有新增任何測試名字去覆蓋乙專屬的「判不了」路徑。
2. 但 `t_drift_unknown_blocks_check_not_scan`(`scripts/test_lumos.py:50426`)整支只用「monkeypatch `_drift_range_events` 回 None」模擬甲(c1–c5)那條路徑判不了,完全沒有觸發乙的 `_ProbeTree.corpus()`(走 `_nodehome_cat_blobs` 批次讀)失敗這條路。這支測試自己的 docstring 明寫:「scan 那一半的『判不了』屬於乙的條件評估,乙做完補在同一支測試」(file: `scripts/test_lumos.py:50429`)——這份 diff 就是乙,但這句承諾沒有兌現,那支測試本體(`scripts/test_lumos.py:50426`-`50445`)未被觸碰。
3. 我在 clone-ns 用 in-process 呼叫手動重現:monkeypatch `_nodehome_cat_blobs` 讓含 `runner.py` 的讀取回 `None`,對一個帶 `when-symbol:src/runner.py::start_up` 條件的候選行跑 `cmd_drift_check` → rc=1、印出「判不了:...的條件判不了(git 讀不出程式檔)」;對同一情境在 `--at <sha>` 模式跑 `cmd_drift_scan(..., as_json=True)` → rc=0、`problems` 裡出現同一筆、`findings` 不含它、且不寫治理帳。行為本身正確,但因為沒有機械測試釘住,之後任何人改動 `_ProbeTree`/`_probe_judge`/`_drift_probe_scan` 讓這條路徑悄悄回錯結果(例如誤判成「不成立」而不是「判不了」),現有 187+ 支 drift 測試不會變紅。

## F4 `_probe_changes` 的 `code_shape` 沒排除 `docs/`、`governance/`,跟 `_ProbeTree.corpus()` 的排除範圍不一致

severity: minor
blocking: 否 — 只會讓不帶路徑的 symbol/test 條件被過度標成候選(多評估,不會漏判也不會誤擋),方向安全,但跟計劃〈做法〉第 0 節「範圍裡有程式檔或測試檔被新增、刪除、改名」的候選定義本意有落差,也可能墊高〈做法〉第 4 節門檻③(單次噪音 ≤5)量測時的候選面
引句:「if code in ("A", "D", "R", "C") and any(_nodehome_code_kind(x) == "ext" for x in ps):」

1. `_probe_changes`(diff 新函式)算 `code_shape` 時,只要改動路徑 `_nodehome_code_kind(x) == "ext"`(判定是不是程式副檔名)就算,沒有排除 `docs/`、`governance/` 底下的檔案。
2. 但同一份 diff 裡 `_ProbeTree.corpus()` 明確排除這兩個資料夾(見引句「not p.startswith(("docs/", "governance/"))」,對應 diff 的 `paths = sorted(p for p in self.files if _nodehome_code_kind(p) == "ext" and not p.startswith(("docs/", "governance/"))...`),也就是乙真正用來解 symbol/test 條件的語料庫,從來不會看 `governance/` 或 `docs/` 底下的檔案內容。
3. 我在 clone-ns 用 `_dr_repo()` 建的測試庫重現:只新增一支 `governance/eval/unrelated_tool.py`(跟這個 repo 目前 `git status` 裡真的有的未追蹤檔 `governance/eval/maestro-matchpct.py` 同一種路徑形狀)並提交,`_probe_changes(...)["code_shape"]` 回 `True`;拿一個完全不相干名字的 bare `symbol` 條件丟進 `_probe_is_candidate([("symbol","totally_unrelated_name")], ch, vault_pre, tenv)` 回 `True`——即使 `_ProbeTree.corpus(False)` 對這個提交讀回來的語料庫是空的(governance/ 檔案本來就不在語料庫裡)。
4. 計劃〈做法〉第 0 節的候選定義②原文是「範圍裡有程式檔或測試檔被新增、刪除、改名(改名可能讓檔換了類別、名稱不在改動行裡)——這時所有不帶路徑的 symbol/test 行都當候選」(file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:55`),語境是「會影響 symbol/test 判定結果的程式檔變動」,governance/ 底下的工具腳本改動不會影響任何 symbol/test 判定結果(語料庫本來就不含它),卻仍被算進候選面。

## ① 條款兌現與測試綁定核對([S9][S10][S11][S12][S15] 與 [S2][S13][S14] 乙部分)

已看,無 finding(除上列 F1–F4)。逐條核對如下,均已讀程式碼並實跑對應測試(`python3 scripts/test_lumos.py -k drift`、`-k revisit`、`-k note_shape`、`-k note_audit`、`-k guard_settle`,共 521 支全線通過):
- **[S9]** 條件文法解析(`_probe_parse`/`_probe_value_err`)、四種鍵在指定提交樹上的判定(`_ProbeTree.one`)、check 以「行」為候選單位(`_probe_is_candidate`)、「同一條」只比條件標記 tuple(`_probe_judge`/`old` 比對)——都對得上條款文字。用 mutation 重現驗過測試不是假綠:把 `_probe_judge` 的 `if old:` 改成 `if False:`(即不看起點),`t_drift_when_probes_evaluate_and_trigger` 的 ⑦⑧兩個斷言立刻翻紅,證明「起點早就成立不列」「只改待辦文字仍是同一條」這兩條是真的被測試釘住,不是斷言太寬。
- **[S10]** `_ns_revisit_violations` 用共用 `_revisit_split`、`_notelines_new` 新增 `keep_other` 參數只給第一層用、既有規則用 `if reg != "other":` 繼續跳過 other 區——確認了新加的 `keep_other=True` 不會讓既有筆記形狀擋規則第一次看到 other 區的行(全部 113 支 note_shape 測試綠)。
- **[S11]** doctor E5 改用 `_revisit_split`,條件式不算壞損、`[by:]` 當日期判到期、沒到期沒壞行整段不印——`t_doctor_revisit_skips_probe_lines` 兩個斷言都綠,且既有 `t_doctor_revisit_reminder`(日期式舊行為)也綠,沒有回歸。
- **[S12]** `_note_audit_items` 新增排除:mutation 拿掉那三行排除邏輯後,`t_note_audit_skips_conditional_revisit` 的斷言①立刻翻紅(「條件式回頭條件不送審」),證明這支測試真的在守這條、不是擺著好看。
- **[S15]** `_drift_status_probe_followups` 只做文字比對、不跑 git(讀原始碼確認沒有任何 `_ns_git`/`_lens_git` 呼叫),三個斷言(成立列出、同行另有條件註明、值不含新狀態不列)都綠。
- **[S2] 乙部分** 見 F3——行為正確但缺專屬測試覆蓋,是本次核對裡唯一「條款寫的行為程式做到了、但綁定測試沒真正驗到」的案例。
- **[S13] 乙部分** `_drift_exam_probe`/`cmd_drift_exam` 的 `--probes` 路徑:`t_drift_exam_probe_mode` 用真的 subprocess 呼叫 CLI(不是 in-process 抄近路),且釘了「跟條件無關的提交要判成漏」(不是「有條件式就一定擋到」的寬鬆斷言),測試設計本身就在防自己假綠。
- **[S14] 乙部分** `_drift_doctor_lines` 新增的條件式計數段落只讀筆記(`_probe_lines`)、不呼叫 git,跟「不評估條件」的條款文字一致;全部是 0 時整段不印(`if _zl:` 才 `section(...)`)。

## ② 改到的筆記逐句核對(`Systems/存量漂移守衛`、`Systems/筆記內容閘`、`Systems/筆記內容審`、計劃〈考試結果〉)

已看,無 finding(除上列 F1–F4)。`Systems/存量漂移守衛.md` 新增的「條件式回頭條件(乙)」整段(「全庫只有一支判定」「同一條只看條件標記」等)跟程式行為對得上;`Systems/筆記內容閘.md`、`Systems/筆記內容審.md` 新增的 WHY 行(引用 [S10]/[S12])跟對應程式碼與測試一致(已用 mutation 驗證,見上)。計劃〈考試結果〉新增的乙那一列(擋到 5、漏 0、誤報 0/0、噪音 1)與總分列(8/3/0/0/4/1/1)是編排者自報的量測數字,考卷本身在唯讀複本 rtb-exam,依派工詞規定只能用 `git -C` 唯讀指令查那份 repo、不應該用會呼叫大量子行程的 `lumos drift exam` 去對它,所以我沒有重新對 rtb-exam 跑一次驗證這幾個數字;但 exam 機制本身(`_drift_exam_probe`、`cmd_drift_exam` 的 `--probes` 解析)在 clone-ns 的合成測試庫裡跑得通、行為跟敘述一致,數字本身屬於「無法用程式碼驗證、只能相信人工量測記錄」的那一類。

## ③ 做法第 0、2 節有沒有沒寫出來的偏離

已看,列在 F1、F4(git 呼叫次數與改名共用、candidate 排除範圍跟語料庫排除範圍不對稱)。除此之外沒有發現其他偏離:條件標記文法(`_PROBE_TOKEN_RE`/`_probe_value_err`)、期限必填(`_probe_parse` 的 `by` 處理)、`file`/`symbol`/`test`/`status` 四鍵定義、「只在正文與摘要可見行生效」的區域判定(`_probe_lines` 用 `_notelines_regions` 配 `_visible_lines`)都跟做法第 0 節文字逐條對得上;第 2 節的 E5 改法、check 判定、第一層排除、`lumos set` 第③項也都對得上。

## ④ 既有綁測試合約(筆記內容審、筆記形狀擋、doctor E5 回訪)有沒有被這次改動破壞

已看,無 finding。實跑結果:`-k note_audit` 175 support 全綠、`-k note_shape` 113 支全綠、`-k revisit` 18 支全綠(含既有 `t_doctor_revisit_reminder`)、`-k guard_settle` 28 支全綠(確認甲的 settle 行為沒被乙牽動)、`-k drift` 187 支全綠。`_notelines_new` 新增的 `keep_other` 參數只有 `_note_shape_eval` 這一個呼叫端傳 `True`,`_note_audit_items` 那個呼叫端(`scripts/lumos:24700` 附近)沒有改動、維持預設 `False`,兩層筆記閘互不牽連。

## 圖譜影響節點逐條判(LUMOS-IMPACT ac5c7ccf..e8f17913)

以下是 `lumos impact --diff ac5c7ccf5b206965135cd6aed19f14c734fd9a11..e8f17913f3da8ee42b4dfe914e266cc083ff58dd` 印出的 34 個節點,逐條判是否被這次 diff(乙:條件式回頭條件)影響其宣稱的行為或合約。多數是因為 about_code 涵蓋 `scripts/lumos`/`scripts/test_lumos.py` 整檔而被列為固定席,實際跟這次改動的內容(REVISIT 條件式、`_ProbeTree`、`_ns_revisit_violations`、`_note_audit_items` 排除、`lumos set` 第③項)無關;已對每篇的合約文字做關鍵字比對(revisit/drift/probe/when-file/when-status 等)排除同名異義。

- **Systems/lumos-cli-read.md**(家,直接,INVARIANT):不影響——這篇管的是讀指令的一般紀律(讀不寫帳、lint 開關等),乙新增的 `drift scan`/`drift exam` 全部遵守「讀指令不寫帳」(已讀程式碼確認 `cmd_drift_scan`/`cmd_drift_exam` 都不呼叫治理帳寫入函式),沒有違反。
- **Systems/guard-kill.md**(家,hop1,INVARIANT):不影響——乙沒有改動 `guard settle`/`guard plan`/`guard abandon` 本體或寫入鎖邏輯(那是甲已經做完的部分,這次 diff 沒有任何 hunk 碰 guard settle 的改寫或鎖);`-k guard_settle` 28 支測試全綠確認無回歸。
- **Systems/授權與歸屬.md**(家,hop1,INVARIANT):不影響——內容關於提交署名與授權,跟 REVISIT 條件式無關;檔內唯一命中詞是每篇筆記通用的 `REVISIT:` 前綴(自己的回頭條件),非同名衝突。
- **Systems/測試假綠形態.md**(家,hop1,INVARIANT):不影響(但主題相關)——這篇是關於「測試怎麼假綠」的通用清單,我在 F3 用的正是這篇教的方法論(找出綁定測試沒真的走到被測分支)去驗證 [S2] 乙那一半;這次 diff 本身沒有違反這篇列的具體假綠模式(已用 mutation 驗證 [S9][S12] 不是假綠)。
- **Systems/design-loop.md**(直接,INVARIANT):不影響——內容是多席設計審迴圈的收斂規則,跟這支程式碼變更本身無關;命中詞「probe」出自這篇講的「probe 輪退場」機制,跟乙的 probe 條件是同名不同義。
- **Systems/pitfalls-code-loop.md**(直接,RISK·守衛面):不影響——這篇是代碼審迴圈的既有隱患清單(UI 驗收慣例等),乙沒有新增或移除任何跟它列的隱患相關的機制;命中詞「Drift」出自這篇原有跟本次無關的一條。
- **Systems/lumos-cli-lifecycle.md**(直接,INVARIANT):不影響——內容管 vendor 白名單、install/uninstall,乙沒有新增檔案或改動 vendored 清單;命中詞「drift probe」分別出自這篇原有的「pre-commit 漂移守衛」與「Codex 三態 ok/probe/merge-failed/absent」,都是同名異義。
- **Systems/loop-convergence-recording.md**(直接,RISK·守衛面):不影響——內容跟本次無關,關鍵字掃描零命中(revisit/drift/probe 都沒有)。
- **Systems/reversibility-governance-ledger.md**(直接,RISK·守衛面):不影響——閘名 `drift-check` 與事件種類（blocked/warned/skipped-env/skipped/degraded/acked）已在甲那次登記過,乙沒有新增任何閘名或新事件種類(`_drift_probe_check` 的 must/listed/unknown 直接併進既有 `_drift_check_core` 的回傳,共用同一組事件寫法),不需要再改這篇。
- **Systems/節點範圍與索引守衛.md**(直接,INVARIANT):不影響——這篇的 ★INVARIANT★「新的閘名要同步登記進已知閘名單」對應測試 `t_gov_stats_gate_drift`,乙沒有新增閘名,該測試在 `-k drift` 全綠裡包含且通過。
- **Systems/check-r-guard.md**(直接,RISK·守衛面):不影響——命中詞「DRIFT」出自這篇一條跟 design-loop F-DRIFT 事故有關的 context,跟乙的 drift 命名同字不同事。
- **Systems/doctor-irreversible-hint.md**(直接,RISK·守衛面):不影響——內容跟 doctor 的不可逆提示有關,跟 Z 段的乙新增內容(`_drift_doctor_lines`)不重疊,關鍵字掃描零命中。
- **Systems/check-t-sentinel.md**(直接,RISK·守衛面):不影響——關鍵字掃描零命中,內容與本次無關。
- **Systems/lumos-deinit.md**(直接,RISK·不可逆):不影響——關鍵字掃描零命中,乙沒有新增/刪除任何 deinit 涉及的檔案清單項目。
- **Systems/cochange-guard.md**(直接,RISK·守衛面):不影響——關鍵字掃描零命中。
- **Systems/lumos-refcheck.md**(直接,RISK·守衛面):不影響——關鍵字掃描零命中;refcheck 管的是路徑/行號宣稱驗證,跟 REVISIT 條件式機制是兩套。
- **Systems/bound-tests-gate.md**(hop1,INVARIANT):不影響——這篇管「改動判 light/keys/全套」的測試子集門檻,乙新增的測試名字(`t_drift_when_probes_evaluate_and_trigger` 等)已經自然落在既有 `-k drift`/`-k` 子集規則裡,不需要改這篇的判定邏輯本身。
- **Systems/canary-audit.md**(hop1,INVARIANT):不影響——命中詞「probe」出自這篇原有的「canary probe」機制(跟設計審 probe 輪有關),跟乙的 REVISIT probe 條件同名異義。
- **Systems/slim-get-一行安裝.md / slim-install-安裝器.md / slim-uninstall-一行卸載.md**(hop1,INVARIANT,三篇):均不影響——這三篇管一行安裝/解除安裝腳本,跟乙的圖譜內容檢查完全無關,關鍵字掃描零命中。
- **Projects/雙向門放行_計劃.md**(直接,RISK·守衛面):不影響——管純文件推送子集放行門檻,乙這次的程式改動(`scripts/lumos`)本身不是純文件變更,不在這篇門檻的適用範圍內討論;內容關鍵字零命中。
- **Projects/規格落成可驗收條件_計劃.md**(直接,RISK·守衛面):不影響——管 `lumos spec-trace`/驗收條款機制,乙的條款([S9]等)本身是用這篇定義的條款格式寫的,但這篇本身的程式邏輯沒有被乙改動;關鍵字掃描零命中。
- **Projects/逃逸自動記_計劃.md**(直接,RISK·守衛面):不影響——跟終端逃逸序列記錄有關,跟本次無關,關鍵字掃描零命中。
- **Systems/core-invariant-baseline.md**(直接,RISK·守衛面):不影響——關鍵字掃描零命中。
- **Systems/judge-severity-gate.md**(直接,RISK·守衛面):不影響——關鍵字掃描零命中;這篇管代碼審判定者的嚴重度换算,乙沒有改動任何判定者邏輯。
- **Projects/存量漂移防線_計劃.md**(直接,1.00):直接相關,已在 F1/F2/F4 與「① ② ③」節詳細核對。
- **Systems/筆記內容閘.md**(家,直接):直接相關,已在「① ④」節核對([S10])。
- **Systems/筆記內容審.md**(家,直接):直接相關,已在「① ④」節核對([S12])。
- **Systems/lumos-cli-write.md**(家,直接):部分相關——這篇管 `set`/`append`/`decision`/`archive`/`new` 等寫入指令的回歸測試清單,乙在 `cmd_set`(`lumos set <計劃> status done|superseded`)裡新增了 `_drift_status_probe_followups` 呼叫(見 [S15]);已確認這個新增只在既有輸出後面多印一段文字,不改變 `lumos set` 本身的寫入行為或回傳碼,`t_set_plan_closed_lists_satisfied_status_probes` 與既有 `t_set_plan_closed_lists_followups` 都綠,沒有破壞這篇管的寫入合約。
- **Projects/公開精簡版_實作計畫.md**:不影響——關鍵字掃描零命中,內容跟精簡版發布流程有關。
- **Projects/code側刪除傳播守衛_實作計畫.md**:不影響——關鍵字掃描零命中,內容跟 delguard 機制有關,跟乙無關。
- **Projects/筆記內容審_計劃.md**(0.66):不影響其既有內容——這篇是筆記內容審的原始設計文件,本身沒有提到 REVISIT 條件式排除規則(那是這次 diff 才透過 [S12] 引入,寫進了 `Systems/筆記內容審.md` 而不是回頭改這篇原始計劃),兩者不衝突,只是這篇計劃文件目前對「條件式回頭條件不送審」這件事完全沒有著墨——這不算矛盾(它是舊計劃,S12 是新計劃的條款),只是提醒:之後若有人只讀這篇找筆記內容審的完整規則,會漏掉 S12 這條例外,需要靠 `Systems/筆記內容審.md` 的 WHY 行才看得到。

## 總結

三處內部不一致與一處測試覆蓋缺口,全部是 minor、全部不 blocking;沒有 major 或 blocker。
